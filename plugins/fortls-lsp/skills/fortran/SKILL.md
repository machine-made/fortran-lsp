---
name: fortran
description: Write, review, port and debug Fortran code (.f90, .f, .F90 and other Fortran files, fpm, CMake or make projects) with compile checks from gfortran after every edit, runtime debugging flags, and modern Fortran conventions. Use whenever a task reads or changes Fortran source, even for a small fix.
---

# Fortran

Check every change with the compiler, not by eye. A Fortran edit is done when the
checker below reports no errors.

## 1. Tools

Run `gfortran --version`. The checker needs gfortran and Python 3.

If gfortran is missing, tell the user and give the install command for their system.
**Ask before installing anything, and never install without a yes:**

| System | Command |
| --- | --- |
| macOS (Homebrew) | `brew install gcc` |
| Debian, Ubuntu | `sudo apt-get install gfortran` |
| Fedora | `sudo dnf install gcc-gfortran` |
| conda | `conda install -c conda-forge gfortran` |
| Windows (MSYS2) | `pacman -S mingw-w64-ucrt-x86_64-gcc-fortran` |

If gfortran cannot be installed, carry on by reading the code closely, and say
plainly in your answer that no compile check ran.

## 2. Check after every edit

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/check_fortran.py <files or directories>
```

Where `${CLAUDE_SKILL_DIR}` is not replaced, the script is `scripts/check_fortran.py`
next to this file.

- It runs `gfortran -fsyntax-only -Wall` on each file, in module order, and also
  checks the files that define the modules those files use.
- It prints one line per problem, `path:line:col: error|warning: message`, then a
  summary. Exit status 0 means no errors, 1 means errors, 2 means the check could not
  run (gfortran missing, path wrong).
- It reads `pp_defs`, `include_dirs` and `excl_paths` from a `.fortls`, `.fortlsrc` or
  `.fortls.json` file at the project root. It writes nothing into the project.
- Options: `--std f2018` to hold the code to a standard, `-I dir`, `-D NAME=value`,
  `--flag=-fopenmp` for any other gfortran flag, `--root dir` for the project root.

Fix every error, then run the check again until it is clean. Fix the warnings your
change caused; leave warnings in code you did not touch unless asked.

The check covers syntax, types, interfaces and module use. It does not link, so a
call to a procedure that exists nowhere shows up only at link time. When the project
has a build (`fpm.toml`, `CMakeLists.txt`, a `Makefile`), finish with that build and
the project's tests. Never say code compiles unless a check or a build ran clean.

## 3. Runtime bugs

Rebuild with the checks on, run the failing case, and read the backtrace:

```bash
gfortran -O0 -g -fcheck=all -fbacktrace -ffpe-trap=invalid,zero,overflow \
  -finit-real=snan -Wall -o debug_run <sources in module order>
```

With fpm: `fpm run --profile debug --flag "-fcheck=all -fbacktrace -ffpe-trap=invalid,zero,overflow"`.
`-fcheck=all` catches out-of-bounds indices and bad argument shapes; `-finit-real=snan`
makes uninitialised reals fail loudly. Do not leave debug flags in the project's build.

## 4. Writing Fortran

Keep the style of a file you edit: fixed form stays fixed form, existing kinds and
naming stay. Do not reformat code you were not asked to change. In new code:

- `implicit none` in every program, module and external procedure.
- Kinds from `iso_fortran_env` (`real64`, `int32`) or the project's kind module, and
  kind suffixes on literals: `0.1_dp`, not `0.1` (single precision) or `0.1d0`.
- `intent` on every dummy argument; `pure` or `elemental` where it is true.
- Modules with `use m, only: ...` instead of COMMON, EQUIVALENCE, ENTRY and include
  files of declarations; explicit interfaces for every call.
- `allocatable` instead of `pointer` unless aliasing is needed;
  `character(len=:), allocatable` for strings of unknown length.
- A local variable initialised in its declaration (`integer :: count = 0`) is
  implicitly `save`d and keeps its value between calls. Assign it in the body instead.
- Arrays are column-major: the innermost loop runs over the first index.
- `1/2` is integer division and gives 0.
- `do concurrent` only when iterations are independent.

## 5. Code intelligence in Claude Code

In Claude Code, this plugin also starts fortls as a language server. Use
go-to-definition, find references, hover and symbol search to trace names instead
of grep. fortls reports only some errors; the checker is the authority. In Cowork and
in Claude apps the language server does not run: use the checker and search.
