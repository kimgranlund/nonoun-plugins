# Release 0.20.7

Recorded: [[PENDING date, UTC and local]]. SDLC Lite 0.20.7. Progressive Context stays at 0.1.2 (no change since 0.19.0). Previous release: SDLC Lite 0.20.6 (54f1c75, tag `v0.20.6`). Built from main commit [[PENDING fixed commit]]; the release branch merges that commit and adds the version bump and this record, and the release commit is the one tagged `v0.20.7`.

## What changed for consumers

This release makes the default lane complete end to end: a ticket the conductor starts as `solo` can now be closed under the skips guard, the default lane's cost is written to the run records, and one command launches an SDLC Lite agent by name. It follows 0.20.6, whose notes listed the first two as open limits.

| Change | Detail | Ticket |
| --- | --- | --- |
| Conductor-started solo closes | `scripts/steps.py` gains `solo_skips_text` and `write_solo_skips`. `record_lane` calls `write_solo_skips` when it records lane `solo`, so `steps.py lane <task dir>` adds the planner and filer entries under `## Skipped` (`- skip: <role>; step: all; reason: solo lane: ...; decided: lane`, once each, only when the last `- lane:` line is `solo`, with every other line kept byte for byte). A conductor that ran `steps.py lane` can close the ticket with `tickets.py close --reason` and the T-0219 skips guard passes. `fanout.py` now calls `steps.write_solo_skips` instead of its own copy (T-0222's `write_solo_skips` in `fanout.py` is removed). The guard in `tickets.py` is unchanged. `agents/conductor.md` says a solo ticket closes with `tickets.py close --reason`. `check.py` guard [[PENDING item number]] covers the function names, the fanout call and the conductor line, with a negative control for each phrase | T-0224 |
| `/agent` launcher | New skill `skills/agent/SKILL.md`, invoked as `/sdlc-lite:agent {agent-name} [--tier S\|M\|L \| --level L1\|L2\|L3] {instructions}`. `solo` starts through the `## Start` section of `agents/solo.md` (headless Bash on Claude Code, `sdlc-solo-l1` to `l3` on Codex, tier M by default or the tier `steps.py lane` gives for a named ticket). `scout`, `researcher`, `architect` and `archaeologist` start through `scripts/run.sh` with a handoff the skill writes from the instructions under `## Question`. `planner`, `builder`, `verifier`, `plan-reviewer`, `filer` and `messenger` answer with a one-line pointer to their own skill or path, `conductor` is refused, and an unknown name lists the valid names. It prints a `Lane:` line first and never spawns an `sdlc-lite:` agent with the Agent tool from a conductor. `check.py` guard [[PENDING item number]] keeps the skill's names in step with `agents/*.md` and the Codex mapping, with three negative controls. The skill index in `skills/sdlc-lite/SKILL.md` lists it | T-0223 |
| Solo cost capture | [[PENDING: the ticket is not filed yet as of this draft. Fill from the merged change: where the solo session's cost and usage are written (expected `runs.jsonl`, same shape as a `run.sh` role), how `budget.py` and the board count it, the selftest and negative control, the live run and its numbers.]] | [[PENDING ticket id]] |
| Live-run records | `docs/validation/solo-close-live-run.md` (T-0224) and `docs/validation/agent-command-live-run.md` (T-0223), each with committed raw evidence under a folder of the same name. They are evidence and change no behavior. See Known limits for what they do and do not show | T-0224, T-0223 |

T-0224 was built as a handwritten step on branch `solo-skips` and T-0223 as a handwritten step on branch `agent-cmd`; [[PENDING solo cost capture branch and builder]]. Each branch's independent L3 verifier: T-0224 [[PENDING result path and verdict, `.sdlc/verify-0224`]], T-0223 [[PENDING result path and verdict, `.sdlc/verify-0223/step-1`]], cost capture [[PENDING]]. [[PENDING: state any failed first pass, narrow re-verify, or missing verifier, plainly, as the 0.20.6 record did for T-0221.]]

## Upgrade notes

- New command `/sdlc-lite:agent` (see the table). Reload plugins to see it. It needs no settings change; `solo` and the read-only roles start as the skill describes.
- A conductor-started solo ticket now closes by reason with no extra step, provided `steps.py lane` ran for the task (it writes the lane line and, for `solo`, the Skipped entries). A solo ticket whose task folder never had `steps.py lane` run has no lane record and is unaffected by the guard, as before.
- `check.py` guard numbers: 0.20.6 left guards 1 to 24. This release adds [[PENDING: items 25 and 26, in merge order; T-0224 and T-0223 both wrote item 25 on their branches, so the second merge renumbers]]. Anything outside this repository that cites a guard by number needs the new number.
- Codex: [[PENDING: confirm `git diff v0.20.6..<fixed commit> -- plugins/sdlc-lite/adapters` is empty and `codex_roles.py generate --check` passes; if no generated Codex agent changed, `codex_roles.py install` is not needed, as in 0.20.6]]. The `/agent` skill is a shared skill, not a generated Codex agent.
- [[PENDING upgrade note for solo cost capture: the new record fields, whether `budget.py` totals change for repositories that already have solo run records, and any new command.]]
- No migration is needed and `tickets.py roadmap` is unchanged.

## Known limits

- How far the evidence supports "solo is the default and its cost is metered": the default lane is solo for size S and M (0.20.5, `steps.py lane`), a conductor-started solo ticket delivers and closes with the guard live in one run (T-0224: one tiny size M ticket, hidden check 9 of 9, 5 minutes 34 seconds, conductor $0.20 and verifier $3.09, the solo session's own cost not captured in that run), and the 0.20.6 fanout runs delivered four tickets through solo lanes. [[PENDING: state the metering claim only as far as the cost capture ticket's live run shows it, including whether the solo session cost is now in `runs.jsonl` for a conductor-started session, a fanout lane, and an `/agent solo` launch.]]
- T-0224's live run: one run, one machine, one tiny size M ticket, Claude Code only, with the plugin from the `solo-skips` worktree (0.20.6 manifests plus the T-0224 change). The conductor started the solo from Bash itself with the tier M flags it read in `agents/solo.md`, not through a script. The selftest negative control (steps selftest, `(lane solo close)`) is what shows the guard still refuses without the entries.
- T-0223's live run: one run per arm on a tiny fixture, headless and in the foreground. Only `solo` and `scout` were launched; `researcher`, `architect` and `archaeologist` share the scout path but were not run. The outer sessions were plain sessions, not conductor sessions, so the rule that a conductor starts agents from Bash was not exercised and `block-role-spawn.sh` was not triggered. The solo session's own cost was not captured in that run either. Codex was not run: the `scout` and `solo` paths on Codex and the Codex-host adapter of the skill are unverified.
- No Codex lane was run under fanout and no Codex conductor start of solo was run (carried over from 0.20.6 and 0.20.5).
- T-0221 still has no passing whole-branch verifier of its own; the T-0222 verifier passed (carried over from 0.20.6). The overlap refusal reads `step-<n>/handoff.md` only, so it cannot fire for a default-lane solo ticket (carried over).
- The `.0222-fanout-solo-skipped` ticket handoff is still the unfilled bug template, and [[PENDING: check whether `.sdlc/0224-solo-lane-skipped/handoff.md` is also still the template on the fixed commit and say so]].
- The 0.20.6 benchmark caveats stand: n=3, one run per cell, not blind to the author, solo had no independent verifier, the lean arm used a minimal chain driver, no size S or L task, no Codex arm, and the solo arm was plain `claude -p --model opus --effort high` and not `sdlc-lite:solo` at the tier models.
- Still true from earlier records: `shellcheck` is not installed, so `run.sh` and `run-selftest.sh` are not shellchecked; the budget stop at 80 percent is exercised only by selftests with a stub `claude` [[PENDING: reword if the cost capture ticket added a live run]]; and [[PENDING: spend counts Claude `run.sh` roles only, unless the cost capture ticket changed that]].
- The parked tickets are not in this release: replan by delta (T-0200, T-0201, T-0213), the spec gate's second half (T-0211), the folder-layout migration (T-0205 to T-0208) and the board overview (T-0187).

## Checks run for the release

Run from the release worktree on branch `release-0.20.7` ([[PENDING fixed commit]] merged in, plus the version bump and this record), [[PENDING date]], all exit 0:

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` ([[PENDING count]] tickets, roadmap current)
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`, `results.py selftest`, `evals.py selftest`, `proposals.py selftest`, `supervisor.py selftest`, `specgate.py selftest`, `footprint.py selftest`, `budget.py selftest`, `board.py selftest`, `fanout.py selftest`, `steps.py selftest`, `tickets.py selftest`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `git diff --check`
- Version parity: both SDLC Lite manifests read 0.20.7; both Progressive Context manifests read 0.1.2.

[[PENDING: one paragraph on the independent Opus fact-check passes: how many ran, what each found, that all findings are fixed, and whether a further pass was run. The review text is not committed.]]
