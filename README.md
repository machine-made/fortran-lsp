# fortran-lsp

Fortran plugin for Claude, `fortls-lsp`:

- a `fortran` skill that compile-checks every Fortran edit with gfortran, debugs
  runtime errors and writes modern Fortran, in Claude Code, Cowork and Claude apps;
- the [fortls](https://github.com/fortran-lang/fortls) language server for code
  intelligence in Claude Code.

## Installation

1. **Install gfortran** for compile checks (`brew install gcc`, `sudo apt-get install gfortran`, …)
   **and fortls** for the language server in Claude Code:
   ```bash
   uv tool install fortls
   ```

2. **Install the plugin** (in Claude apps and Cowork: **Customize > Plugins**):
   ```
   /plugin install fortls-lsp --marketplace machine-made/fortran-lsp
   ```
   On Claude Code versions before 2.1.275, add the marketplace first:
   ```
   /plugin marketplace add machine-made/fortran-lsp
   /plugin install fortls-lsp@fortran-lsp
   ```

## Configuration

Large projects can tune indexing (excluded paths, extra suffixes, preprocessor
definitions) with a `.fortls` file at the project root — see
[plugins/fortls-lsp/README.md](plugins/fortls-lsp/README.md) and the
[fortls options reference](https://fortls.fortran-lang.org/options.html).

## Development

```bash
python3 -m unittest discover -s tests -v   # needs gfortran
```

Release notes are in [CHANGELOG.md](CHANGELOG.md).

## License

MIT

## Disclaimer

This software is provided "as is", without warranty of any kind. To the extent
permitted by law, the authors and contributors are not liable for any damage, loss
or claim arising from its use or misuse. You are responsible for how you use it and
for following the laws and rules that apply to you. The full terms are in
[LICENSE](LICENSE).
