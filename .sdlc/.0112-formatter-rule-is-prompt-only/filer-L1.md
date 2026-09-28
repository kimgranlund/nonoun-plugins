<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps built and verified with pass verdicts. Writing the filer report now.

## Warnings
None.

## PR title
T-0112: Block repo-wide formatters and format scripts in builder runs

## PR body
### Summary
Builder rule 6 ("run formatters only on the files this step changed") was prompt-only: `check.py` only proved the phrase existed in `builder.md`, so a builder could still run a repo-wide formatter through a project script such as `npm run format`. This adds a code gate that stops that before it runs.

### Changes
- `plugins/sdlc-lite/hooks/block-repo-format.sh` (new, executable): a PreToolUse(Bash) hook active only when `SDLC_ROLE=builder`. It blocks (exit 2) a project format/fix script run with no explicit file paths (`npm run format`, `pnpm run format`, `yarn run lint:fix`, `make fmt`, etc.) and known formatters/fixers run in write or fix mode against a directory, `.`, or a glob (`prettier --write .`, `eslint --fix src`, `cargo fmt`, `go fmt ./...`, and others). Explicit file-path arguments pass (`prettier --write a.ts`, `npm run format -- a.ts`). It masks quoted text so mentions pass, fails closed (raw-text scan) on heredocs, shell/evaluator words, unterminated quotes, or missing `python3`, and is a no-op for every other role and for interactive sessions. The stderr message names the role, cites "builder rule 6", and tells the caller to pass the changed paths explicitly.
- `plugins/sdlc-lite/hooks/hooks.json`: registers the hook as a fifth entry under the existing `Bash` matcher; the other four are untouched.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: new fixtures covering 11 blocked forms (exit 2, stderr names `builder` and `rule 6`), 6 allowed forms with builder, and the blocked forms passing with no role and with `SDLC_ROLE=verifier`/`conductor`.
- `plugins/sdlc-lite/agents/builder.md`: rule 6 now names the hook; the existing phrase "files this step changed" (guarded by `check.py`) is kept.
- `plugins/sdlc-lite/scripts/check.sh`: header comment's hook-selftest list now names the new hook.
- Root `CLAUDE.md`: `Check everything` line and a new Layout bullet describe the hook's scope, blocked forms, and fail-closed rules.
- `.claude/agents/sdlc-lite-author.md`: hook-selftest list and a new Hazards line updated to match.

### How each was verified
- Step 1 (hook, registration, selftest fixtures), builder L3, verifier L2: pass. Every acceptance criterion ran verbatim and passed, including a bite check (the verifier reproduced red at pre-build HEAD in a throwaway worktree for the registration and blocked/allowed loops) and a mutation check (replacing the hook body with `exit 0` makes `hook-selftest.sh` fail). `shellcheck --severity=warning` clean; guard `hook-selftest.sh` and a diff-quiet guard on the other four hooks both passed. Builder's own manual probes covered roughly 60 additional command forms (all correctly blocked or allowed) and confirmed the no-`python3` fallback still blocks the required 10 forms.
- Step 2 (records sync, full gate), builder L2, verifier L1: pass. All 8 non-guard grep criteria passed and were confirmed red at pre-build HEAD; the em-dash guard on the new hook passed; the full `scripts/check.sh` guard passed (all selftests, shellcheck, `claude plugin validate` green).
- Both verifiers reviewed the out-of-scope-looking files (task handoff, planner output, `runs.jsonl`) and attributed them correctly to the planning phase and to step 1's own prior output, not to scope creep.

## Changelog entry
Added `hooks/block-repo-format.sh`: a PreToolUse(Bash) hook that stops a builder from running a repo-wide formatter, `--fix` linter, or format script (directly or through a project script like `npm run format`) unless explicit file paths are given, closing the gap where builder rule 6 was enforced only by prompt text.

## Follow-ups
None.
