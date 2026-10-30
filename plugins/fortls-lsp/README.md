# fortls-lsp

Fortran plugin for Claude. It has two parts:

- **The `fortran` skill.** Claude compile-checks every Fortran edit with gfortran,
  debugs runtime errors with gfortran's checking flags, and writes modern Fortran
  (`implicit none`, `iso_fortran_env` kinds, `intent` on every argument, modules).
- **The fortls language server.** In Claude Code, Claude can go to definitions, find
  references, read hover information, list the symbols of a file or a workspace, and
  see [fortls](https://github.com/fortran-lang/fortls) diagnostics right after each edit.

## Where it works

| Part | Claude Code | Cowork | Claude apps (web, desktop, mobile) |
| --- | --- | --- | --- |
| `fortran` skill | Yes | Yes | Yes |
| fortls language server | Yes | No | No |

The skill's compile checks need gfortran wherever Claude runs the code: on your
computer in Claude Code and Cowork, and in the code-execution sandbox in Claude apps.
The Claude apps sandbox has no gfortran at first; Claude asks you, then installs it
there with `apt-get`, which only changes that temporary sandbox. Without gfortran the
skill still applies its conventions and reviews the code by reading it, and its answer
starts with "Not compile-checked".

## Installation

1. Install the plugin. In Claude Code:
   ```
   /plugin install fortls-lsp --marketplace machine-made/fortran-lsp
   ```
   On Claude Code versions before 2.1.275, add the marketplace first:
   ```
   /plugin marketplace add machine-made/fortran-lsp
   /plugin install fortls-lsp@fortran-lsp
   ```
   In Claude apps and Cowork, add it from **Customize > Plugins**.

2. Install gfortran for compile checks. The plugin never installs it for you; when it
   is missing, Claude shows the command and asks before running it.
   ```bash
   brew install gcc                  # macOS
   sudo apt-get update && sudo apt-get install -y gfortran   # Debian, Ubuntu
   sudo dnf install gcc-gfortran     # Fedora
   ```

3. For the language server in Claude Code, install fortls:
   ```bash
   uv tool install fortls            # or: pipx install fortls, pip install fortls
   fortls --version                  # check that it is on your PATH
   ```

## The compile check

The skill runs `skills/fortran/scripts/check_fortran.py`, a single Python file that
uses only the standard library. It runs `gfortran -fsyntax-only -Wall` on the files
Claude changed, in module order, on the files that define the modules they use, and on
the files that use modules the changed files define.
It prints one line per problem (`path:line:col: error|warning: message`). Module files
go to a temporary folder that is deleted afterwards, so nothing is written into your
project. The check does not link; Claude finishes with your project's own build
(fpm, CMake, make) when there is one.

## Supported extensions

Free form: `.f90`, `.f95`, `.f03`, `.f08`. Fixed form: `.f`, `.f77`, `.for`, and `.fpp`,
which is also preprocessed. The uppercase variants of each (`.F90`, `.F`, …) go through
the C preprocessor too. The language server indexes the same set.

## Project configuration

The language server and the compile check both read an optional `.fortls` JSON file
at the project root (`.fortlsrc` and `.fortls.json` also work):

```json
{
  "excl_paths": ["build", "third_party"],
  "include_dirs": ["include"],
  "pp_defs": {"MY_MACRO": "1"}
}
```

See the [fortls options reference](https://fortls.fortran-lang.org/options.html) for
every setting. The compile check uses `excl_paths`, `include_dirs` and `pp_defs`. When
a `.fortls` file is present, fortls lets its values replace any command-line
arguments per key (`pp_defs` in particular resets unless restated in the file).

## Troubleshooting

- `Executable not found in $PATH` in the `/plugin` Errors tab: fortls is not installed,
  or its directory is not on `PATH`. Run `fortls --version` in the shell that starts
  Claude Code.
- Large source trees can take time to index. The plugin waits up to 120 s for the
  server to start. Exclude build and vendor directories with `excl_paths` in `.fortls`.
- `fortran-check: gfortran not found`: install gfortran (step 2), or pass another
  gfortran executable with `--fc gfortran-14`.
- A file that needs OpenMP or MPI modules: pass `--flag=-fopenmp`, or `-I` the folder
  that holds the MPI module files.

## Privacy

This plugin collects no data and sends nothing over the network. The only downloads
are the ones you approve: installing gfortran or fortls fetches them from your package
manager or PyPI.

- The skill runs gfortran and the check script on the code in your project, on the
  machine or sandbox where Claude is working. The script makes no network
  connections and writes only to a temporary folder that it deletes.
- The skill never installs software by itself. When gfortran is missing, Claude asks
  you before installing it from your system's package manager.
- In Claude Code the plugin starts the `fortls` program on your computer, which reads
  your Fortran files locally. It starts fortls with `--disable_autoupdate`, so fortls
  does not contact PyPI or update itself. Update fortls yourself with
  `uv tool upgrade fortls`.

## Support

Report problems with the plugin at <https://github.com/machine-made/fortran-lsp/issues>.
Report problems with the language server itself at
<https://github.com/fortran-lang/fortls/issues>, and with gfortran at
<https://gcc.gnu.org/bugzilla/>.

## Credits

fortls is developed by the [fortran-lang](https://fortran-lang.org/) community and
gfortran by the [GCC project](https://gcc.gnu.org/). This plugin uses them as
installed; it is not affiliated with either project.

## More information

- [fortls documentation](https://fortls.fortran-lang.org/)
- [gfortran documentation](https://gcc.gnu.org/onlinedocs/gfortran/)
- [fortls on GitHub](https://github.com/fortran-lang/fortls)
