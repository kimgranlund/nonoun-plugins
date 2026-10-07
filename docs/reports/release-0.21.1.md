---
date: 2026-10-07
---

# Release 0.21.1

Recorded: 2026-10-07. SDLC Lite 0.21.1, a patch to 0.21.0 (tag `v0.21.0`, commit 027da15a). Progressive Context is unchanged: `git diff v0.21.0 HEAD -- plugins/progressive-context` is empty, so its version is not bumped. Built from main commit 1235d8a8 (13 commits past `v0.21.0`; main has since gained b553fc8d, 3079ea30, b6eea866 and a88921f9, which file and close T-0337, see Known limitations) on the branch `release-0.21.1`. The release commit adds the version bump in the two `plugin.json` files, this record and its docs index entry. The release is not tagged, pushed or published by this commit.

This record states only what a committed file or a command run for it shows. Where a record does not say something, it says so.

## What changed for consumers

`git diff --stat v0.21.0 1235d8a8 -- plugins` shows 14 files. The consumer-visible change is the twelve launcher skills; the rest is a check guard and a script docstring and selftest.

| Change | Ticket |
|---|---|
| Twelve launcher skills (agent, architect, build, dig, file, fix, fleet-retro, plan, research, review-traces, scout, verify) spelled `dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> ...` without `--transcript`. They now include `--transcript <sub-agent transcript jsonl>`, so a conductor following them records transcript usage and the cost estimate is priced from usage fields rather than the undercounting notice tokens | T-0334 |
| `check.py` rejects a skill that spells a `dispatch.py record <dispatch_file> --` call without `--transcript`, with a positive and a negative control; it is item 41 in the `check.py` docstring, added in this release commit (maintenance, not shipped behavior) | T-0334 |
| `cost_estimate.py` docstring said transcript pricing "is not assumed" while `dispatch.py` implements it. It now names the basis label `usage fields x rates`. The label the code writes is unchanged, so stored rows and readers are unaffected; the selftest pins the docstring | T-0335 |
| The L3 fable verifier row of the live evidence prices at 0.570 of the host figure after the T-0332 refit. No refit was made; the row is recorded as an accepted outlier in `docs/reports/l3-verifier-row-outlier-2026-10-06.md`, and `cost_estimate.py selftest` pins the L3 row to a 0.5 to 0.65 range of host 2.4762 (the report says it pins the figure; the range is what the selftest checks) and now fails if that report file is missing, so the selftest needs the repository's `docs/` folder | T-0336 |

Repository maintenance, not shipped to consumers: the T-0333 verification records in `.sdlc/verify-subagent/` and the closed ticket folders, ticket and note commits, a repair of the `messages.py` paths in the `.sdlc/messages/**/AGENTS.md` files (commit 7f4607d8), and the new report above.

## Upgrade notes

None required. No script interface, agent definition, hook, levels or prices table changed. A conductor that already passes `--transcript` to `dispatch.py record` sees no difference; one that followed the old skill text and omitted it now gets the transcript-priced estimate.

## Verification

T-0333 ran an independent L3 verifier (fable, a different model family than the sonnet builders; transcript model fields read `claude-fable-5-1`) over the 12 sub-agent tickets that closed in 0.21.0 without a verifier verdict, through `dispatch.py prepare`, a spawn of `sdlc-lite:verifier-L3`, and `dispatch.py record --transcript`, in six batches. Verdicts are in `.sdlc/verify-subagent/` (`summary.md` and one file per ticket): 9 pass (T-0275, T-0279, T-0284, T-0286, T-0326, T-0327, T-0329, T-0330, T-0332) and 3 fail (T-0280, T-0328, T-0331). The three fails are exactly the three fixes in this release:

- T-0280 (label drift and stale docstring): resolved by T-0335, which fixed the docstring and kept the code's label `usage fields x rates` as the agreed one, so the criterion's literal `transcript usage x price` is not what the code writes.
- T-0331 criterion T0331-1 (launcher skills without `--transcript`): fixed by T-0334.
- T-0328 (T0328-1) and T-0331 (T0331-3), the L3 verifier row outside the 35 percent band: handled by T-0336 as an accepted outlier, not by a fix.

The L3 row stays outside the band. The T-0336 report states why: a refit that lifts it to 0.65 would push the L2 row (0.93 to 1.09) and the G and F rows above the band, because the fitted factors (input x225, output x1.27) already sit at the limit the other rows allow. The band holds for the L2 opus verifier row and the G, F and R1 fable rows (0.745, 0.830, 0.847). The cause of the L3 miss is not established; the guess that its cache read and write counts differ in kind is untested and its surviving transcript cannot confirm it.

Each fix ticket's closed folder (`.sdlc/.0334-*`, `.0335-*`, `.0336-*`) holds its handoff and one solo sonnet run line in `runs.jsonl`; none holds a verifier verdict. The checks run for this release (the full `check.sh` run, `check-packaging.py` and `codex_roles.py generate --check` on a `git archive` copy under `/tmp` with no `claude` in the path, and the detached fact-checks) are stated in the hand-off report; no committed file records them and their logs are not committed.

Still UNVERIFIED:

- T-0334, T-0335 and T-0336 closed on the solo lane with no independent verifier verdict.

Carried over from 0.21.0, not exercised by this patch:

- An account switch spanning a run.
- The resume ladder (`dispatch.py resume`).
- Interactive background sub-agents (`run_in_background: true`) and the completion-notification path.
- Behavior at a session limit, a parent exit with sub-agents running, nested lane conductors, and a lane whose spawn fails on a missing model.
- Codex: no live Codex run of the sub-agent mode.

The T-0334 skill text edits and the new `check.py` guard were not exercised in a new live sub-agent run for this patch.

## Known limitations

- T-0337 (P2 bug) was filed and fixed on main after the build commit (filed b553fc8d, fix 3079ea30, merged b6eea866, closed a88921f9). The fix is not in 0.21.1. In 0.21.1, `dispatch.py prepare scout L1` prints the model `claude-haiku-4-5`, which the Agent tool rejects, and `block-role-spawn.sh` denies the alias `haiku`, so a scout spawn through the sub-agent path is denied; `SDLC_BACKEND=claude run.sh scout L1` is the documented fallback. Scout is one of the twelve patched launcher skills. A release that includes the fix needs a rebuild from a later main.
- T-0288 is open: `claude -p` stays as a fallback, and `run.sh`'s Claude branch, `solo_run.py --exec` and the headless fanout conductor are not retired.
- Estimated cost is approximate (`cost_estimated: true`). The L3 fable verifier row prices at 0.570 of host and is outside the 35 percent band. The input factor of `usage_calibration` is empirical and unexplained.
- Observations from T-0333 that no criterion failed on and no ticket was filed for are listed in `.sdlc/verify-subagent/summary.md` (for example `dispatch.py resume --root` with a path holding a `.worktrees` component finds nothing, and the verifier role text and the stray-worktree hook disagree about throwaway worktrees in this mode).
