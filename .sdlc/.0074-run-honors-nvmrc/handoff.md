---
id: T-0074
title: "run.sh uses the node version from .nvmrc when present"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P3         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Headless builders run the Node version the repo pins in .nvmrc.

## Intent
Literal ask: when .nvmrc exists and nvm has that version, run.sh prepends its bin dir to PATH.
Deltas:
- Which .nvmrc: defaulted: the one at the git toplevel of the directory run.sh runs in (the target repo), read after the git preflight.
- Version syntax: defaulted: an exact version (`v20.11.0` or `20.11.0`) matches `$NVM_DIR/versions/node/v20.11.0`; a partial one (`20`, `v20.11`) picks the highest installed version with that prefix by numeric compare; aliases (`lts/*`, `node`, `stable`, anything non-numeric) are not resolved and PATH is left unchanged. Whitespace and a trailing newline are stripped.
- nvm location: defaulted: `$NVM_DIR`, else `$HOME/.nvm`; nvm itself is never sourced or executed (no shell functions, no network).
- Version not installed or no nvm: defaulted: PATH unchanged, one line on stderr naming the .nvmrc version and that it was not found; the run proceeds (not an error exit).
- Visibility: defaulted: when a bin dir is prepended, one stderr line names it; `SDLC_DRY_RUN=1` does the same resolution and prints it, so it is testable without a model call.
- Test: defaulted: `scripts/run-selftest.sh` gains cases with a fake `NVM_DIR` in a throwaway repo (exact match, prefix picks highest, alias skipped, missing version, no .nvmrc), run by `scripts/check.sh`.
- Docs: defaulted: the run.sh line in CLAUDE.md Layout (and `.claude/agents/sdlc-lite-author.md` if it describes run.sh behavior) states the new behavior in the same change.
Do: in `scripts/run.sh`, after the git preflight, resolve the .nvmrc version against the nvm install as above and prepend the matched `bin` dir to PATH for the role run; add selftest cases; update the docs that describe run.sh.
Non-goals: sourcing nvm, installing a missing version, resolving nvm aliases, `.node-version` or `package.json` engines, any change to fanout.py or bench.sh.
Done when: `SDLC_DRY_RUN=1 scripts/run.sh builder L1 <handoff>` in a repo whose .nvmrc names an installed fake-NVM_DIR version reports that version's bin dir first on PATH (and leaves PATH unchanged for a missing version, an alias, or no .nvmrc), those cases are in `scripts/run-selftest.sh`, and `scripts/check.sh` passes.

## Context
From peer setup-sdlc-lite-generative-ui: builders hit the repo's Node version guard because the headless shell's PATH has an older node than .nvmrc. Ask: when .nvmrc exists and nvm has that version, run.sh prepends its bin dir to PATH.

## Constraints
What must not change. "None" if none.
