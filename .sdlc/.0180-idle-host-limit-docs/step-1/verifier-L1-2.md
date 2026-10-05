<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Five files contain `cannot wake an idle host`: pass. Evidence: the handoff's `grep -l ... | wc -l` check printed C1ok (count is 5). A file missing the sentence would drop the count, so the check can fail.
- `grep -q 'messages-idle-host-limit-2026-10-01.md' docs/README.md`: pass. Evidence: printed C2ok. The diff adds one README line linking the note, in the style of its neighbors.
- (guard) `codex_roles.py generate --check`: pass. Evidence: "Codex agent definitions verified", exit 0. The `sdlc-messenger-l1.toml` diff is one line, which matches regeneration.
- (guard) `messages.py selftest`: pass. Evidence: "messages selftest: PASS".
- (guard) scope guard on changed files: pass. Evidence: run with `SDLC_BASE_SHA=2ca8fe8b…` read from `step-1/base-sha`; printed C5ok. Only the allowed paths changed.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: two runs, both exit 0. Output includes the "messages", "run", "hook" and "hook live probe" selftests PASS and "ok: plugin validate". The only skip was "skip: shellcheck not installed".
- Previous-attempt fix: the note's citations hold. Evidence:
  - `docs/reports/messages-live-run.md` line 156 holds `spawn_agent`, `wait_agent` and `followup_task`.
  - The note no longer mentions `codex-messenger.txt`.
  - `run_in_background` appears in `messages-live-run.md`, and "spawn it again" is at lines 47 and 51.
  - `release-0.20.2.md` exists.
- No em dashes: pass. Evidence: grep for `—` over the added and removed lines of `docs` and `plugins` returned 0.

## Out of scope changes
None. The modified `.sdlc/.../step-1/handoff.md` and the untracked artifact files under `.sdlc` are excluded from the guard and are run bookkeeping.

## For the next attempt
None
