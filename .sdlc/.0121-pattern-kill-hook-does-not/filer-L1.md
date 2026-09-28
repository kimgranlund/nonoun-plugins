<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps pass verification. Ready to draft the filer output.

## Warnings
None.

## PR title
T-0121: Catch a kill word assigned through a command substitution in block-pattern-kill.sh

## PR body
### Summary
`plugins/sdlc-lite/hooks/block-pattern-kill.sh` previously blocked `pkill`/`killall`/`kill` reaching a shell variable through a `$(...)` or backtick substitution only by accident, when the kill word happened to sit right after the `VAR=` prefix. Forms where the kill word appeared deeper in the substitution body (`p=$(echo find pkill); $p x`, `k=$(compgen -c | grep killall | head -1); ${k} node`, backtick equivalents, and `k=$(command -v kill); $k $(pgrep -f vite)`) passed through undetected inside a role run. This closes that gap while keeping `cmd=$(command -v ls); $cmd -la` and quoted mentions passing.

### Changes
- `plugins/sdlc-lite/hooks/block-pattern-kill.sh`: added a second `assign` alternative that matches `NAME=`, an optional `"`, then `$(` or a backtick, whose body up to the closing `)` or backtick holds `pkill`, `killall`, or `kill` as a whole word (using the existing `word`/`wend` boundaries, so `pattern-kill`, `killer`, `skill` still don't count). Matches feed the existing `held_kill` name extraction and `$NAME`/`${NAME}` command-position check. `strict`'s cheap exit and the raw `loose` path are unchanged.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: 6 new block fixtures and 3 new pass fixtures covering the substitution forms; header clause updated to mention substitution.
- `CLAUDE.md`: the `hooks/block-pattern-kill.sh` Layout entry now documents the `$(...)`/backtick substitution form with an example.
- `.claude/agents/sdlc-lite-author.md`: the kill-pattern hazard line now mentions the substitution form.

### How verified
- Step 1 (builder L3 opus/high, verifier L2 sonnet/high, pass): all 16 acceptance criteria run verbatim by the builder, all green; a negative control confirmed the new selftest fixtures fail against the pre-step hook (proving they bite); `shellcheck -S warning` clean on both scripts. The verifier independently reran each criterion in the built tree and against a throwaway worktree at the pre-build HEAD, confirming red-then-green on the new cases and unbroken green on the already-passing guard cases and docs checks.
- Step 2 "gates green" (builder L1 sonnet/low, verifier L1 opus/medium, pass): `bash plugins/sdlc-lite/scripts/check.sh` was already green after step 1, no fix needed. The verifier independently reran check.sh green on the built tree, and reproduced a red run by swapping the hook back to its HEAD version in a throwaway worktree, confirming the guard can actually fail and that the failure traces to the hook's substitution handling.
- No out-of-scope changes: both verifiers confirmed the diff touches only the five files listed above, plus normal task-tracking artifacts.
- Builder note: a nested substitution's kill word occurring after that inner substitution's first closing `)` (e.g. `k=$(basename $(x) kill)`) is not caught, since the body is scanned only up to the first `)`/backtick. Not part of this ticket's scope.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Fixed: `block-pattern-kill.sh` now catches a kill word (`pkill`/`killall`/`kill`) reached through a `$(...)` or backtick command substitution assigned to a variable and then run as a command, closing a gap where only the previous fix's two literal example forms were actually blocked.

## Follow-ups
- `block-pattern-kill.sh`'s new substitution matcher reads a substitution body only up to its first `)` or backtick, so a kill word placed after a nested inner substitution's closing paren (e.g. `k=$(basename $(x) kill)`) still passes undetected inside a role run; worth a dedicated ticket if that pattern is judged realistic.
