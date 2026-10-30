#!/usr/bin/env python3
"""Compile-check Fortran files with gfortran, without building anything.

Runs `gfortran -fsyntax-only` on each file, in module order, and prints one
line per diagnostic: `path:line:col: error|warning: message`.

Exit status: 0 no errors, 1 errors found, 2 the check could not run.
Reads `.fortlsrc`, `.fortls.json` or `.fortls` at the project root for
`pp_defs`, `include_dirs` and `excl_paths`. Module files go to a temporary
directory; nothing is written to the project. Uses no network.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXED = {".f", ".for", ".f77", ".fpp", ".ftn"}
FREE = {".f90", ".f95", ".f03", ".f08"}
SUFFIXES = FIXED | FREE
CONFIG_NAMES = (".fortlsrc", ".fortls.json", ".fortls")
ROOT_MARKERS = CONFIG_NAMES + ("fpm.toml", ".git")
INTRINSIC = {
    "iso_fortran_env", "iso_c_binding", "ieee_arithmetic", "ieee_exceptions",
    "ieee_features", "omp_lib", "omp_lib_kinds", "openacc",
}

MODULE_RE = re.compile(
    r"^\s*module\s+(?!(?:procedure|function|subroutine|pure|impure|elemental|recursive)\b)(\w+)\s*(?:!.*)?$",
    re.I,
)
SUBMODULE_RE = re.compile(r"^\s*submodule\s*\(\s*(\w+)\s*(?::\s*(\w+))?\s*\)\s*(\w+)", re.I)
USE_RE = re.compile(r"^\s*use\b\s*(,\s*(non_)?intrinsic\s*)?(::)?\s*(\w+)", re.I)
DIAG_RE = re.compile(r"^(.+?):(\d+):(?:(\d+):)?\s*(Fatal Error|Error|Warning):\s*(.*)$", re.M)
FATAL_RE = re.compile(r"^\S+: Fatal Error:\s*(.*)$", re.M)
MISSING_MOD_RE = re.compile(r"Cannot open module file '[^']+\.mod'|Module file '[^']+\.smod' has not been generated")


def is_fortran(path: Path) -> bool:
    return path.suffix.lower() in SUFFIXES


def find_root(start: Path) -> Path:
    for d in (start, *start.parents):
        if any((d / m).exists() for m in ROOT_MARKERS):
            return d
    return start


def load_config(root: Path) -> dict:
    for name in CONFIG_NAMES:
        p = root / name
        if p.is_file():
            text = p.read_text(encoding="utf-8", errors="replace")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                stripped = "\n".join(re.sub(r"^\s*//.*$", "", ln) for ln in text.splitlines())
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError as e:
                    print(f"note: {p} is not valid JSON ({e}); ignoring it", file=sys.stderr)
                    return {}
    return {}


def expand(root: Path, patterns) -> list[Path]:
    out: list[Path] = []
    for pat in patterns or []:
        hits = glob.glob(str(root / pat), recursive=True) or [str(root / pat)]
        out.extend(Path(h).resolve() for h in hits)
    return out


def walk(top: Path, excluded: list[Path]) -> list[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(top):
        d = Path(dirpath).resolve()
        dirnames[:] = [
            n for n in dirnames
            if not n.startswith(".") and (d / n).resolve() not in excluded
        ]
        files.extend(d / f for f in filenames if is_fortran(Path(f)))
    return sorted(files)


def scan(path: Path) -> tuple[set[str], set[str]]:
    """Modules a file defines, and modules it uses (lowercase)."""
    defines, uses = set(), set()
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return defines, uses
    fixed = path.suffix.lower() in FIXED
    logical: list[str] = []
    joining = False
    for line in lines:
        if fixed and line[:1] in ("c", "C", "*", "!"):
            continue
        part = line.split("!", 1)[0].rstrip()
        if joining and logical:
            logical[-1] += part.lstrip().lstrip("&")
        else:
            logical.append(part)
        joining = not fixed and logical[-1].endswith("&")
        if joining:
            logical[-1] = logical[-1][:-1]
    for line in logical:
        if m := MODULE_RE.match(line):
            defines.add(m.group(1).lower())
        elif m := SUBMODULE_RE.match(line):
            parent, ancestor, name = (g.lower() if g else g for g in m.groups())
            defines.add(f"{parent}@{name}")
            uses.add(f"{parent}@{ancestor}" if ancestor else parent)
        elif (m := USE_RE.match(line)) and not (m.group(1) and not m.group(2)):
            name = m.group(4).lower()
            if name not in INTRINSIC:
                uses.add(name)
    return defines, uses


def order(targets: list[Path], pool: list[Path]) -> tuple[list[Path], set[Path]]:
    """Files to check, providers first, and the files that use modules the targets define."""
    info = {p: scan(p) for p in set(pool) | set(targets)}
    provider: dict[str, Path] = {}
    for p in sorted(info):
        for mod in info[p][0]:
            provider.setdefault(mod, p)
    changed = set().union(*(info[t][0] for t in targets))
    users = {p for p in info if p not in targets and info[p][1] & changed}
    seen: set[Path] = set()
    result: list[Path] = []

    def visit(p: Path, stack: set[Path]) -> None:
        if p in seen or p in stack:
            return
        stack.add(p)
        for mod in sorted(info[p][1]):
            dep = provider.get(mod)
            if dep and dep != p:
                visit(dep, stack)
        stack.discard(p)
        seen.add(p)
        result.append(p)

    for t in [*targets, *sorted(users)]:
        visit(t, set())
    return result, users


def compile_one(fc: str, path: Path, base: list[str], moddir: str) -> tuple[int, str]:
    suffix = path.suffix
    cpp = suffix != suffix.lower() or suffix.lower() == ".fpp"
    form = "-ffixed-form" if suffix.lower() in FIXED else "-ffree-form"
    lang = "f95-cpp-input" if cpp else "f95"
    cmd = [fc, "-fsyntax-only", "-fno-diagnostics-show-caret", "-fmax-errors=20", form,
           f"-J{moddir}", f"-I{moddir}", f"-I{path.parent}", *base]
    if cpp:
        cmd.append("-cpp")
    cmd += ["-x", lang, str(path)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                           env={**os.environ, "LC_ALL": "C"})
    except subprocess.TimeoutExpired:
        return 1, f"{path}:1:1: Error: gfortran timed out after 300 s"
    return r.returncode, r.stderr


def parse(stderr: str, path: Path) -> list[tuple[str, int, int, str, str]]:
    diags = []
    for line in stderr.splitlines():
        if m := DIAG_RE.match(line):
            file, ln, col, kind, msg = m.groups()
            level = "warning" if kind == "Warning" else "error"
            diags.append((file, int(ln), int(col or 1), level, msg.strip()))
        elif m := FATAL_RE.match(line):
            diags.append((str(path), 1, 1, "error", m.group(1).strip()))
    return diags


def only_missing_modules(diags) -> bool:
    errs = [d for d in diags if d[3] == "error"]
    return bool(errs) and all(MISSING_MOD_RE.search(d[4]) for d in errs)


def rel(p: str) -> str:
    try:
        return os.path.relpath(p)
    except ValueError:
        return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_fortran.py",
        description="Compile-check Fortran files with gfortran -fsyntax-only (nothing is built or written).",
    )
    ap.add_argument("paths", nargs="+", help="Fortran files or directories to check")
    ap.add_argument("--root", help="project root (default: nearest folder with .fortls*, fpm.toml or .git)")
    ap.add_argument("--std", help="Fortran standard, e.g. f2018 or f2008 (default: gfortran's GNU dialect)")
    ap.add_argument("-I", dest="incs", action="append", default=[], help="extra include or module directory")
    ap.add_argument("-D", dest="defs", action="append", default=[], help="extra preprocessor definition")
    ap.add_argument("--flag", action="append", default=[], help="extra gfortran flag, e.g. --flag=-fopenmp")
    ap.add_argument("--fc", default="gfortran", help="gfortran executable (default: gfortran)")
    ap.add_argument("--no-warnings", action="store_true", help="do not pass -Wall")
    ap.add_argument("--no-users", dest="users", action="store_false",
                    help="do not also check the files that use modules defined in the given files")
    args = ap.parse_args(argv)

    fc = shutil.which(args.fc)
    if not fc:
        print(f"fortran-check: {args.fc} not found; install gfortran to run compile checks", file=sys.stderr)
        return 2

    given = [Path(p).resolve() for p in args.paths]
    missing = [str(p) for p in given if not p.exists()]
    if missing:
        print(f"fortran-check: no such file or directory: {', '.join(missing)}", file=sys.stderr)
        return 2

    root = Path(args.root).resolve() if args.root else find_root(given[0] if given[0].is_dir() else given[0].parent)
    cfg = load_config(root)
    excluded = expand(root, cfg.get("excl_paths"))

    targets: list[Path] = []
    for p in given:
        targets.extend(walk(p, excluded) if p.is_dir() else [p])
    targets = list(dict.fromkeys(targets))
    if not targets:
        print("fortran-check: no Fortran files found", file=sys.stderr)
        return 2

    base = [] if args.no_warnings else ["-Wall"]
    if args.std:
        base.append(f"-std={args.std}")
    for d in [*expand(root, cfg.get("include_dirs")), *(Path(i).resolve() for i in args.incs)]:
        base.append(f"-I{d}")
    defs = cfg.get("pp_defs") or {}
    if isinstance(defs, dict):
        base += [f"-D{k}={v}" if str(v) != "" else f"-D{k}" for k, v in defs.items()]
    base += [f"-D{d}" for d in args.defs] + args.flag

    pool = walk(root, excluded) if root.is_dir() else []
    queue, users = order(targets, pool)
    if not args.users:
        queue = [p for p in queue if p not in users]
        users = set()
    target_set = set(targets)
    results: dict[Path, tuple[int, list]] = {}

    with tempfile.TemporaryDirectory(prefix="fortran-check-") as moddir:
        pending = queue
        while pending:
            retry = []
            for p in pending:
                rc, err = compile_one(fc, p, base, moddir)
                diags = parse(err, p)
                if rc and not diags:
                    lines = [ln for ln in err.strip().splitlines() if ln != "compilation terminated."]
                    diags = [(str(p), 1, 1, "error", f"gfortran failed: {lines[0] if lines else 'no output'}")]
                results[p] = (rc, diags)
                if rc and only_missing_modules(diags):
                    retry.append(p)
            if len(retry) == len(pending):
                break
            pending = retry

    errors = warnings = 0
    for p in queue:
        _, diags = results[p]
        for file, ln, col, level, msg in diags:
            if p in target_set:
                note = ""
            elif level == "warning":
                continue
            elif p in users:
                note = " [this file uses a module you changed]"
            else:
                note = " [in a module this file needs]"
            print(f"{rel(file)}:{ln}:{col}: {level}: {msg}{note}")
            errors += level == "error"
            warnings += level == "warning"

    extra = f" (and {len(users)} file(s) using their modules)" if users else ""
    print(f"fortran-check: {len(targets)} file(s){extra}, {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
