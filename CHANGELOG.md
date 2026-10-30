# Changelog

## 1.3.1

- Changed the `fortran` skill to stop and ask before installing gfortran when it is missing, with the command that works in Claude's code sandbox (`apt-get update` first)
- Changed the `fortran` skill so an answer about code that was not compile-checked starts with "Not compile-checked: gfortran is not available here." and never calls the code verified
- Changed the README to say the Claude apps sandbox starts without gfortran

## 1.3.0

- Added the `fortran` skill, which works in Claude Code, Cowork and Claude apps: Claude compile-checks every Fortran edit with gfortran, debugs runtime errors with gfortran's checking flags and follows modern Fortran conventions
- Added `check_fortran.py`, a standard-library Python script that runs `gfortran -fsyntax-only` in module order (submodules included), also checks the files that use a changed module, reads `pp_defs`, `include_dirs` and `excl_paths` from `.fortls`, and prints one line per problem without writing into the project
- Changed the listing name to "Fortran (fortls + gfortran)"; the plugin id stays `fortls-lsp`, so existing installs keep working
- Changed the homepage to this repository; the README now says where each part works, credits fortls and gfortran, and extends the privacy section to the skill
- Added tests and CI for the compile check
