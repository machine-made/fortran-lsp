# fortls-lsp

Fortran language server ([fortls](https://github.com/fortran-lang/fortls)) for Claude Code, providing code intelligence and diagnostics.

With this plugin, Claude can go to definitions, find references, read hover information,
list the symbols of a file or a workspace, and see diagnostics right after each edit.

## Supported Extensions

Free-form: `.f90`, `.f95`, `.f03`, `.f08` — Fixed-form: `.f`, `.f77`, `.for` — Preprocessed: `.fpp` — plus the uppercase variants of each.
This is the same set that fortls indexes by default.

## Installation

1. Install fortls, the language server. The plugin does not install it for you.

   ### Via uv (recommended)
   ```bash
   uv tool install fortls
   ```

   ### Via pipx
   ```bash
   pipx install fortls
   ```

   ### Via pip
   ```bash
   pip install fortls
   ```

   Check that it is on your `PATH`:
   ```bash
   fortls --version
   ```

2. Install the plugin in Claude Code:
   ```
   /plugin install fortls-lsp --marketplace ricardofrantz/fortran-lsp
   ```
   On Claude Code versions before 2.1.275, add the marketplace first:
   ```
   /plugin marketplace add ricardofrantz/fortran-lsp
   /plugin install fortls-lsp@fortran-lsp
   ```

## Project Configuration

fortls reads an optional `.fortls` JSON file at the project root. Useful for large trees:

```json
{
  "excl_paths": ["build", "third_party"],
  "incl_suffixes": [".inc"],
  "pp_defs": {"MY_MACRO": "1"}
}
```

See the [fortls options reference](https://fortls.fortran-lang.org/options.html) for all settings. Note: when a `.fortls` file is present, its values replace any command-line arguments per key (`pp_defs` in particular resets unless restated in the file).

## Troubleshooting

- `Executable not found in $PATH` in the `/plugin` Errors tab: fortls is not installed, or its directory is not on `PATH`. Run `fortls --version` in the shell that starts Claude Code.
- Large source trees can take time to index. The plugin waits up to 120 s for the server to start. Exclude build and vendor directories with `excl_paths` in `.fortls`.

## Privacy

This plugin collects no data and sends nothing over the network. It only tells Claude Code to start the `fortls` program on your computer. fortls reads the Fortran files of your project locally. The plugin starts fortls with `--disable_autoupdate`, so fortls does not contact PyPI or update itself. Update fortls yourself with `uv tool upgrade fortls`.

## Support

Report problems with the plugin at <https://github.com/ricardofrantz/fortran-lsp/issues>. Report problems with the language server itself at <https://github.com/fortran-lang/fortls/issues>.

## More Information
- [fortls Documentation](https://fortls.fortran-lang.org/)
- [fortls on PyPI](https://pypi.org/project/fortls/)
- [GitHub Repository](https://github.com/fortran-lang/fortls)
