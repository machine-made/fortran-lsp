# fortran-lsp

Fortran Language Server ([fortls](https://github.com/fortran-lang/fortls)) marketplace plugin for Claude Code.

## Installation

1. **Install fortls:**
   ```bash
   uv tool install fortls
   ```

2. **Install the plugin:**
   ```
   /plugin install fortls-lsp --marketplace ricardofrantz/fortran-lsp
   ```
   On Claude Code versions before 2.1.275, add the marketplace first:
   ```
   /plugin marketplace add ricardofrantz/fortran-lsp
   /plugin install fortls-lsp@fortran-lsp
   ```

## Configuration

Large projects can tune indexing (excluded paths, extra suffixes, preprocessor
definitions) with a `.fortls` file at the project root — see
[plugins/fortls-lsp/README.md](plugins/fortls-lsp/README.md) and the
[fortls options reference](https://fortls.fortran-lang.org/options.html).

## License

MIT

## Disclaimer

This software is provided "as is", without warranty of any kind. To the extent
permitted by law, the authors and contributors are not liable for any damage, loss
or claim arising from its use or misuse. You are responsible for how you use it and
for following the laws and rules that apply to you. The full terms are in
[LICENSE](LICENSE).
