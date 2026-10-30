# Vendored TOML editor

`tomlkit/` is the complete Python source package from `tomlkit` 0.13.3
(`tomlkit-0.13.3-py3-none-any.whl` on PyPI, MIT license). Its license is at
`tomlkit/LICENSE`. Wheel SHA-256:
`c89c649d79ee40629a9fda55f8ace8c6a1b42deb912b2a8fd8d942ddadb606b0`.

The project-factory opt-in edits an existing `.codex/config.toml`. A
style-preserving parser is needed because that file may contain unrelated
settings, comments, tables, and existing developer instructions. The ordinary
agent generation and install path does not import this package.
