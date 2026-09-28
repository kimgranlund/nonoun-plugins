## Task goal
Headless builders run the Node version the repo pins in .nvmrc.

## Step 1: Resolve .nvmrc in run.sh and add selftest cases
level: L3
### Do
In `plugins/sdlc-lite/scripts/run.sh`, add the resolution after the git preflight (the two `git rev-parse` lines) and before the `SDLC_DRY_RUN` exit, so dry runs resolve too.

1. Read `.nvmrc` from `$(git rev-parse --show-toplevel)` of the current directory. Strip whitespace and newlines.
2. Set nvm dir to `${NVM_DIR:-$HOME/.nvm}`. Never source or run nvm.
3. Resolve the version:
   - An exact version (`v20.11.0` or `20.11.0`, three numeric parts) matches `<nvm dir>/versions/node/v20.11.0` only.
   - A partial numeric version (`20`, `v20`, `v20.11`) matches installed `vX.Y.Z` dirs by whole components. `20` must not match `v200.1.0`, and `v20.1` must not match `v20.11.0`. Pick the highest by numeric compare, not lexical: `v20.11.0` beats `v20.9.0`.
   - Anything non-numeric (`lts/*`, `node`, `stable`, ...) is an alias and is not resolved.
4. Print exactly one stderr line per case, in these formats, which the criteria grep:
   - Matched: `run.sh: .nvmrc <raw>: prepended <nvm dir>/versions/node/<vX.Y.Z>/bin to PATH`. Then `export PATH="<bin>:$PATH"` so the `claude` role run inherits it.
   - Numeric version, no match or no nvm dir: `run.sh: .nvmrc <raw>: not found under <nvm dir>/versions/node, PATH unchanged`
   - Alias: `run.sh: .nvmrc <raw>: alias not resolved, PATH unchanged`
   - No `.nvmrc`: print nothing and change nothing.
5. None of these cases changes the exit code. The run proceeds.
6. Update the header comment of run.sh to describe the behavior.
7. Keep the code valid under `set -euo pipefail` (for example, a `grep` that finds nothing or an empty glob must not abort) and clean under shellcheck.

In `plugins/sdlc-lite/scripts/run-selftest.sh`, add cases that use a fake `NVM_DIR` under `$tmp` (dirs `versions/node/vX.Y.Z/bin`) and a throwaway repo with a commit and an `.nvmrc`:
- exact match
- a prefix that picks the highest of `v20.9.0`/`v20.11.0` and ignores `v200.1.0`
- `v20.1` not matching `v20.11.0`
- alias `lts/*` skipped
- missing version
- no `.nvmrc`, with no nvmrc line printed

Use `SDLC_DRY_RUN=1` and assert on stderr. Add one non-dry run in which the stub `claude` writes `${PATH%%:*}` to a file, and assert that it equals the matched bin dir.

Keep the existing cases and the `run selftest: PASS` line.
### Acceptance criteria
- `bash -c 'r="$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/run.sh"; t=$(mktemp -d); mkdir -p "$t/nvm/versions/node/v20.9.0/bin" "$t/nvm/versions/node/v20.11.0/bin" "$t/nvm/versions/node/v200.1.0/bin" "$t/repo"; cd "$t/repo" && git init -q && printf "20\n" >.nvmrc && echo x >h.md && git add -A && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && NVM_DIR="$t/nvm" SDLC_DRY_RUN=1 "$r" builder L1 h.md 2>&1 | grep -F "prepended $t/nvm/versions/node/v20.11.0/bin to PATH"'`
- `bash -c 'r="$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/run.sh"; t=$(mktemp -d); mkdir -p "$t/nvm/versions/node/v20.11.0/bin" "$t/repo"; cd "$t/repo" && git init -q && printf "  v20.11.0\n" >.nvmrc && echo x >h.md && git add -A && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && NVM_DIR="$t/nvm" SDLC_DRY_RUN=1 "$r" builder L1 h.md 2>&1 | grep -F "prepended $t/nvm/versions/node/v20.11.0/bin to PATH"'`
- `bash -c 'r="$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/run.sh"; t=$(mktemp -d); mkdir -p "$t/nvm/versions/node/v22.1.0/bin" "$t/repo"; cd "$t/repo" && git init -q && printf "v20.11.0\n" >.nvmrc && echo x >h.md && git add -A && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && out=$(NVM_DIR="$t/nvm" SDLC_DRY_RUN=1 "$r" builder L1 h.md 2>&1) && printf "%s\n" "$out" | grep -F "v20.11.0" | grep -F "not found" && ! printf "%s\n" "$out" | grep -F "prepended"'`
- `bash -c 'r="$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/run.sh"; t=$(mktemp -d); mkdir -p "$t/nvm/versions/node/v20.11.0/bin" "$t/repo"; cd "$t/repo" && git init -q && printf "lts/*\n" >.nvmrc && echo x >h.md && git add -A && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && out=$(NVM_DIR="$t/nvm" SDLC_DRY_RUN=1 "$r" builder L1 h.md 2>&1) && printf "%s\n" "$out" | grep -F "lts/*" | grep -F "not resolved" && ! printf "%s\n" "$out" | grep -F "prepended"'`
- (guard) `bash -c 'r="$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/run.sh"; t=$(mktemp -d); mkdir -p "$t/nvm/versions/node/v20.11.0/bin" "$t/repo"; cd "$t/repo" && git init -q && echo x >h.md && git add -A && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && out=$(NVM_DIR="$t/nvm" SDLC_DRY_RUN=1 "$r" builder L1 h.md 2>&1) && ! printf "%s\n" "$out" | grep -F ".nvmrc"'`
- `grep -q NVM_DIR plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- Negative control, observable: in a `git worktree add <tmp> HEAD` copy with the built run.sh and run-selftest.sh copied in, and the `export PATH=` prepend line removed from run.sh, `bash <tmp>/plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: FAIL` and exits non-zero.
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`
