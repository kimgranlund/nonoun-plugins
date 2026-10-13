<!-- role=solo level=L1 model=sonnet effort=high -->
## Output
🟢 The 1 error is not ours, so I changed no files.

- **The error:** `claude plugin list` and `claude --debug` print it. The exact text is: `figma~g2@synced: ✘ Not loaded — the claude.ai-synced copy in figma~g2/ declares the same plugin name "figma" as ab67d1d0-40de-460f-9d00-61fb989b8f43~g2/ (the first claude.ai copy of that name); only one synced copy per name is considered`. It comes from two claude.ai-synced copies of the Figma plugin.
- **Our plugins:** the installed `sdlc-lite@sdlc-lite` 0.22.6 and `progressive-context@sdlc-lite` 0.1.2 both show enabled. A `--debug` load of both plugin directories logged no error, warning or "not loaded" line that names either one. The `sdlc-lite` hooks loaded from `./adapters/claude/hooks.json`.
- **Validation:** the marketplace manifest passes. Each plugin passes with one warning: a root `CLAUDE.md` is not loaded as project context. I'm treating that as noise, not the error, because it is a warning and `/reload-plugins` counts errors.
- **Existing check:** `python3 scripts/check-packaging.py` exits 0 (PASS).
- **No new case:** the ticket asks for a `check-packaging.py` case and a negative control only if the cause is ours. It isn't, so I added none.

**Still open:** to clear the error, remove one of the duplicate synced Figma copies. That is machine-level plugin config, outside this repo. The ticket is ready to close on this evidence.

The ticket is level L1, so no verifier runs. I left the scratch debug log in `/tmp/t524`.
