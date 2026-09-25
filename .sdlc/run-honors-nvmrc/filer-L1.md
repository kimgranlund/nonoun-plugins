<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0074: run.sh uses the node version from .nvmrc when present

## PR body
### Summary
Headless builders were tripping the repo's Node version guard. The headless shell's PATH had an older node than the one pinned in `.nvmrc`. `scripts/run.sh` now reads the target repo's toplevel `.nvmrc` after the git preflight. When nvm has that version installed, run.sh puts its `bin` dir first on PATH for the role run. It never sources or runs nvm.

### Changes
- **`plugins/sdlc-lite/scripts/run.sh`**
  - The resolution runs after the git preflight and before the `SDLC_DRY_RUN` exit, so dry runs show it too.
  - It looks under `${NVM_DIR:-$HOME/.nvm}/versions/node`.
  - An exact version (`v20.11.0` or `20.11.0`) matches only its own dir.
  - A partial version (`20`, `v20.11`) matches whole components and picks the highest by numeric compare. So `20` ignores `v200.1.0`, and `v20.1` does not match `v20.11.0`.
  - Aliases (`lts/*`, `node`, `stable`) are not resolved.
  - Each outcome prints one stderr line: prepended, not found (PATH unchanged), or alias not resolved (PATH unchanged).
  - No `.nvmrc`, or one holding only whitespace, prints nothing.
  - The exit code never changes. The code is written for bash 3.2 and `set -euo pipefail`.
- **`plugins/sdlc-lite/scripts/run-selftest.sh`**
  - Adds `.nvmrc` cases against a fake `NVM_DIR`:
    - exact match, with and without the `v`
    - prefix picks the highest version
    - component boundaries
    - missing version
    - aliases
    - nvm dir that does not exist
    - no `.nvmrc`
    - whitespace is stripped
  - Adds one real run in which the stub `claude` records the head of PATH.
  - The existing cases are unchanged.
- **`CLAUDE.md`**: the `scripts/run.sh` Layout bullet now describes the behavior. `.claude/agents/sdlc-lite-author.md` does not describe run.sh's PATH handling, so it is unchanged.

### Verification
- **Step 1 (run.sh + selftest): verifier L2 pass.**
  - All four dry-run acceptance commands printed the expected line: prefix picks v20.11.0, whitespace-padded exact version, missing version, `lts/*` alias.
  - The prefix check returns rc=1 at HEAD, so it can fail.
  - The no-`.nvmrc` guard passed, `run selftest: PASS`, and `shellcheck --severity=warning` is clean.
  - Negative control: with the `export PATH=` line removed, the selftest printed `run selftest: FAIL` on the real-run PATH-head check and exited 1.
  - The builder also ran four more deliberate code breakages (lexical pick, missing minor-component check, string-prefix major, alias reported as not found). The selftest caught each one.
- **Step 2 (docs): verifier L1 pass.**
  - Both grep criteria are red at HEAD and green now.
  - The verifier checked each claim in the CLAUDE.md sentence against run.sh.
  - `scripts/check.sh` exits 0 with every selftest PASS, `ok: shellcheck`, and `ok: plugin validate`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `scripts/run.sh` now uses the Node version pinned in the target repo's `.nvmrc`: exact or highest numeric-prefix match under `$NVM_DIR` (else `~/.nvm`), prepended to PATH for the role run. Aliases and missing versions leave PATH unchanged with one stderr line. `SDLC_DRY_RUN=1` shows the resolution. (T-0074)

## Follow-ups
None
