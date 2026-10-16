# Notes

`tickets.py close` appends follow-ups that did not become tickets.

## Standing maintainer rulings

- 2026-10-09: maintainer decision (T-0419): conductors may refresh managed blocks of docs/**/AGENTS.md in their own repo under the narrow rule in `plugins/sdlc-lite/skills/onboard/SKILL.md` (Standing authorization). Anything else (root AGENTS.md, template change, new file, `--force`, other repos) is reported to the maintainer with the diff.
- 2026-10-10: maintainer decision: the L4 full-chain cost replay (docs/reports/2026-10-09-l4-full-chain-cost-replay.md, verdict: allow chunked solo for L3/L4 with at most 4 chunks) stays a report; no build ticket. Revisit when a solo run is priced (K-001) and n is above 2. The scope-vs-tests lint (T-0416) and the delta verifier (T-0417) were both decided "do not build".

## Lean work records (maintainer decisions 2026-10-13)

- 2026-10-13: maintainer: objective is to complete the task, update the ticket, and hand off a clean merge-ready worktree, with minimal documentation. A closed ticket keeps `handoff.md` plus an Outcome section (what changed, checks run, verdict). Attempt and dispatch JSON, `runs.jsonl`, `base-sha` and `skips.md` move to a gitignored runtime folder; cost reports read it locally.
- 2026-10-13: maintainer: stop by default: filer drafts (PR body, changelog), dated `docs/reports` files per ticket, side files in task folders (`process-deviations.md`, `refusals.jsonl`, `red-checkpoint.jsonl`, `hints.md`), and any file a role or skill writes at the top of `.sdlc/` or the project root (fleet-retro answers go in a message). `docs/reports` stays for releases and retros.
- 2026-10-13: maintainer: design first (architect), build in waves, ship as 0.23.0. Queued T-0529, T-0530, T-0534 wait for the design, which says whether each is kept, merged or dropped.

## Decisions (maintainer, 2026-10-14, /ask)
- Codex live named-agent exchange (T-0507, T-0316): deferred past 0.23.0, stays UNVERIFIED in release notes.
- ui-designer per-mode write gate: declined; the role contract and check.py guard are enough until a mis-edit is observed.
- `/compact` `--write-handoff` live check (T-0465): left off for now.

## Live caveats and open decisions

- T-0496 decide: `tickets.py close` writes the tests-gate skip line only for a solo ticket with a `step-<n>/` dir, so a real solo ticket with no step dir never gets the line, `gate_tests_only` never counts it, and the pilot barely reaches the tickets it targets; decide whether close should consult the gate on that path.
- T-0496 decide: the handoff asks `lanes.py` to print `gate: tests-only` or `gate: verifier`, but `lanes.py list` has no per-ticket surface; the unattended run left `lanes.py` untouched and put the field in `solo_stats.py` only (skips.md decision); name a surface (a lane column, the `/report` lanes view) or drop it.
- T-0496 decide: the 20-ticket readout needs K-005 for tests-gate tickets and rework after close (a reopen, or a follow-up citing a closed ticket within 7 days), and neither is built; `first_pass / verified` excludes tickets with no verifier round, so the revert rule cannot be evaluated yet.
- T-0467 decide: `plan_check.py fanout` refused with `FAIL overlap` for T-0498 and T-0499 because both cite the same evidence report, while `fanout.py run --dry-run` printed `overlap (planned scope): none` for the same pair; say which definition should win.
- T-0530 decide: plugins/sdlc-lite/scripts/lanes.py:719 and :1013: close and list resolve tickets under a hardcoded `Path(top) / '.sdlc'` (as the existing `local_tickets` at :681) while open uses `--root`; a non-default root would record on open and never clear on close.
- T-0519 note: the Pareto read behind the 2026-10-12 model decisions comes from third-party Artificial Analysis summaries, is unverified, and has no copy in `docs/reports/`; no replay ran.
- T-0520 note: The live run used the legacy `run.sh` Claude branch. The generated `ui-designer-L<n>` agents, the sub-agent dispatch path, and the Codex host have no live evidence.
- T-0550 note (2026-10-14, wave 74): `solo_run.py run --no-worktree` run from inside a lane omits the `Tree:` line, so a parent in another directory must add it by hand; always write it (the parent's cwd is unknown to the script). Fold into the next solo_run change.
- T-0562 note (2026-10-15, T-0561 verifier): a foreground Bash call past the 600 s cap is auto-moved to the background by Claude Code, and the role then idles waiting for it; T-0562's hook cannot see that path. Fix candidates for a follow-up: roles split long suites into one selftest per call, or the brief states "no single command over 9 minutes"; fleet-doctor's `stalled` rule catches it meanwhile.
