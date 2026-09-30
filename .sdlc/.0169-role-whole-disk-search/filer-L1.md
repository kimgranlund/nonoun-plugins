<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0169: Refuse whole-disk and home-folder searches inside role runs

## PR body
### Summary
A planner run on T-0160 ran `find / -name quick_validate.py -path "*skill*" 2>/dev/null | head -3`. It stalled for more than 25 minutes with no output, because `| head` does not end a search that prints no match. This PR adds a Claude `PreToolUse(Bash)` hook, `block-disk-scan.sh`. Inside a role run, it refuses searches rooted at `/` or a home folder. The refusal names the role and points to a bounded path.

### Changes
- `plugins/sdlc-lite/hooks/block-disk-scan.sh` (new, executable), modeled on `block-pattern-kill.sh`.
  - It exits 0 at once when `SDLC_ROLE` is unset.
  - It masks quoted text, heredocs and comments with a python3 masker. `"$HOME"` and `"${HOME}"` are kept, so they still read as `$HOME`.
  - It fails closed to a raw scan when python3 is missing, a quote is unterminated, a heredoc is present, or a shell or evaluator word is a command word.
  - It blocks `find`, `bfs`, `fd`, `fdfind`, `rg`, `ag`, recursive `grep`/`egrep`, `du`, `ls -R` and `tree`. The path operand must be exactly `/`, `/*`, `~`, `$HOME`, `/Users`, `/home`, `/Volumes`, `/System`, `/Library`, `/private`, or a home folder itself. They may sit behind `sudo`, `command`, `env`, `nohup`, `timeout N`, `xargs` or a `VAR=value` assignment.
  - On a match it exits 2. Stderr names the role, says a whole-disk search can run for many minutes, and tells the role to search a bounded path (the repository, a named subfolder such as `~/.claude/plugins`, or `$CLAUDE_PLUGIN_ROOT`).
  - A root search is still blocked when it has `-maxdepth`. The handoff left this open, and the docs state the choice.
- `plugins/sdlc-lite/adapters/claude/hooks.json`: registered in the `Bash` matcher after `block-repo-format.sh`. No shared `hooks/hooks.json` was created.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: a new fixture block with 9 blocked cases (including the T-0160 repro and a `bash -c` wrapper) and 6 allowed cases (including no role). Search phrases are built with `printf`, so the file never holds a root search as a command. Every failure message starts with `block-disk-scan`.
- `plugins/sdlc-lite/scripts/check.sh`: hook list in the header comment updated.
- `docs/maintenance/claude-hooks.md`: new `## hooks/block-disk-scan.sh` section. It says the hook is Claude-only and that Codex roles are not covered.

### Verification
- Step 1 verifier (L2): pass. It ran every acceptance criterion as written.
  - Five blocked cases exit 2, and stderr names the role.
  - Allowed cases exit 0, including the quoted mention and a root find with no `SDLC_ROLE`.
  - Negative control: with the hook stubbed to `exit 0` in a temp copy, the selftest fails with `FAIL: block-disk-scan blocks the T-0160 repro: exit 0, want 2`. So the test failed without the fix and passes with it.
  - Scope guard: only the five expected files changed.
  - Extra hand checks agreed with the spec. Blocked: `du -sh ~`, `ls -R /`, `tree /`, `timeout 5 find / -name x`. Allowed: `ls /`, `find /Users/me/Projects/x`.
- Step 2 (gates) verifier (L1): pass. `hook-selftest.sh`, `hook-live-probe.sh --selftest`, `scripts/check-packaging.py`, `check.py`, `check.sh` and `git diff --check` all exit 0. The verifier's own negative controls:
  - The selftest goes red without the hook.
  - `check.sh` goes red when the hook script is deleted.
  - `git diff --check` catches a trailing-whitespace line added to `check.sh`.
- The builder also ran about 70 hand cases and a no-python3 fallback run, all as expected.

### Limits
- shellcheck is not installed on this host, so `check.sh` skipped it. The new hook has no lint here.
- No live role-session probe was run. The evidence is the offline selftest plus the existing `hook-live-probe.sh` shape check.
- The hook is Claude-only. Codex roles are not covered.
- A text hook cannot stop every scan. `cd / && find .`, a scan reached through a script, and a variable path such as `p=/; find "$p"` all bypass it.
- The hook only acts where the running plugin root carries it, normally the installed plugin cache and not this worktree.

## Changelog entry
- sdlc-lite: a new `block-disk-scan.sh` PreToolUse(Bash) hook refuses `find /`, `rg x ~` and similar whole-disk or home-folder searches inside Claude role runs, so a role can no longer stall on one. Codex roles are not covered.

## Follow-ups
- decide: Codex roles have no guard against whole-disk searches, because the hook is Claude-only; a line in the shared role contracts (needs `codex_roles.py generate`) was left out of this S-sized ticket.
- note: `scripts/check-packaging.py` still passes when a hook registered in `hooks.json` points at a missing script; only `check.sh` catches it (the step-2 verifier found this, and it predates this change).
- note: The hook bypasses are `cd / && find .`, a scan reached through a script, and a variable path such as `p=/; find "$p"`. There is no live role-session probe of the hook.
