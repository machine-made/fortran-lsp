# Changelog

## 1.3.0

- Added the `fortran` skill, which works in Claude Code, Cowork and Claude apps: Claude compile-checks every Fortran edit with gfortran, debugs runtime errors with gfortran's checking flags and follows modern Fortran conventions
- Added `check_fortran.py`, a standard-library Python script that runs `gfortran -fsyntax-only` in module order, reads `pp_defs`, `include_dirs` and `excl_paths` from `.fortls`, and prints one line per problem without writing into the project
- Changed the listing name to "Fortran (fortls + gfortran)"; the plugin id stays `fortls-lsp`, so existing installs keep working
- Changed the homepage to this repository, and the README to say where each part works and how the privacy policy covers the skill
- Added tests and CI for the compile check
