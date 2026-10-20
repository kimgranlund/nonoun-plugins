# Notes

`tickets.py close` appends follow-ups that did not become tickets.

## Standing maintainer rulings

- 2026-10-09: maintainer decision (T-0419): conductors may refresh managed blocks of docs/**/AGENTS.md in their own repo under the narrow rule in `plugins/sdlc-lite/skills/onboard/SKILL.md` (Standing authorization). Anything else (root AGENTS.md, template change, new file, `--force`, other repos) is reported to the maintainer with the diff.
- 2026-10-10: maintainer decision: the L4 full-chain cost replay (docs/reports/2026-10-09-l4-full-chain-cost-replay.md, verdict: allow chunked solo for L3/L4 with at most 4 chunks) stays a report; no build ticket. Revisit when a solo run is priced (K-001) and n is above 2. The scope-vs-tests lint (T-0416) and the delta verifier (T-0417) were both decided "do not build".
- 2026-10-17: maintainer decision: the tests-gate pilot (T-0496) ends; every ticket keeps one independent verifier, and `tests_gate: pilot` is removed from `.sdlc/config`. The T-0530 (`.sdlc` root in lanes.py) and T-0467 (overlap definitions) caveats are dropped as unused paths.

## Lean work records (maintainer decisions 2026-10-13)

- 2026-10-13: maintainer: objective is to complete the task, update the ticket, and hand off a clean merge-ready worktree, with minimal documentation. A closed ticket keeps `handoff.md` plus an Outcome section (what changed, checks run, verdict). Attempt and dispatch JSON, `runs.jsonl`, `base-sha` and `skips.md` move to a gitignored runtime folder; cost reports read it locally.
- 2026-10-13: maintainer: stop by default: filer drafts (PR body, changelog), dated `docs/reports` files per ticket, side files in task folders (`process-deviations.md`, `refusals.jsonl`, `red-checkpoint.jsonl`, `hints.md`), and any file a role or skill writes at the top of `.sdlc/` or the project root (fleet-retro answers go in a message). `docs/reports` stays for releases and retros.
- 2026-10-13: maintainer: design first (architect), build in waves, ship as 0.23.0. Queued T-0529, T-0530, T-0534 wait for the design, which says whether each is kept, merged or dropped.

## Decisions (maintainer, 2026-10-14, /ask)
- Codex live named-agent exchange (T-0507, T-0316): deferred past 0.23.0, stays UNVERIFIED in release notes.
- ui-designer per-mode write gate: declined; the role contract and check.py guard are enough until a mis-edit is observed.
- `/compact` `--write-handoff` live check (T-0465): left off for now.

## Live caveats and open decisions

- T-0519 note: the Pareto read behind the 2026-10-12 model decisions comes from third-party Artificial Analysis summaries, is unverified, and has no copy in `docs/reports/`; no replay ran.
- T-0520 note: The live run used the legacy `run.sh` Claude branch. The generated `ui-designer-L<n>` agents, the sub-agent dispatch path, and the Codex host have no live evidence.

## T-0636: work_root t13: migrate this repository to docs/work (2026-10-19)

- note: check.sh was not run by this verifier; the conductor's separate run is the evidence for that part of #1.
- note: `docs/reports/2026-10-12-ceremony-audit.md` has one `.sdlc/.0356-...` path turned into an absolute GitHub permalink; its sha was not checked.

## T-0657: steps.py review reports red criteria already green at base (2026-10-20)

- note: my throwaway worktree is removed and its scratch dirs cleaned (a combined rm command was denied by the permission system, so the rm of `/Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/tmp/0657-verifier-L2` and the scratch dir under /var/folders may remain; the worktree itself is gone from `git worktree list`).

## T-0652: Outcome gains an optional Lessons line (2026-10-20)

- note: plugins/sdlc-lite/scripts/tickets.py:3268 collapses runs of whitespace in each lesson (`" ".join(x.split())`), so a multi-line lesson becomes one line. The handoff does not state this behavior.
- note: the selftest covers only the `--reason` route. The default and `--filer` routes go through the same `outcome()` wrapper at tickets.py:3491-3494 and were not exercised live.

## T-0645: dispatch.py advance runs record, prune, next and prepare in one call (2026-10-20)

- note: plugins/sdlc-lite/scripts/dispatch.py advance(): a solo dispatch prints `next: a solo ticket...` and skips the prune and TaskStop step, though the Intent does not mention solo dispatches (fanout.py prep solo dispatches are a stated non-goal).

## T-0656: settle --forward refuses while a lane attempt is running (2026-10-20)

- note: plugins/sdlc-lite/scripts/fanout.py:5111 the existing comment `# negative control: a red gate keeps main where it is ...` now sits above the new T-0656 block, not above the `settle-fwd-red` case it describes.
- note: plugins/sdlc-lite/scripts/fanout.py:2701 no selftest covers the `lanes.discover` branch of running_roles (a marker in a lane worktree whose `into` is the integration branch). Only the integration-worktree marker is tested.
- note: plugins/sdlc-lite/scripts/fanout.py:2648 the running check only runs on the diverged path that calls settle_forward. A `--forward` settle that is already a fast-forward skips it. This fits the Goal, since that path does not move the integration branch.

## T-0653: Roadmap renders an Open follow-ups section from NOTES.md (2026-10-20)

- note: plugins/sdlc-lite/scripts/tickets.py:2518 `FOLLOW_RE` is a `fullmatch` on a `- ` prefixed line, so an indented or `*` bullet in NOTES.md is not counted; matches the `append_notes` writer format, so no action needed.

## T-0671: onboard entry text agrees with the docs table on where plans go (2026-10-20)

- note: redck.py deviations printed no process deviation lines. The artifacts dir has no builder-*.md, so I took the builder's claims from the handoff `## Outcome` and checked each one myself.
- note: /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/tmp/0671-verifier-L2/.owner.json is still there. The prefix's rm -rf was denied and the file belongs to the harness. Both throwaway worktrees were removed with `git worktree remove`.

## T-0646: Every role writes its result file and ends with a one-line pointer (2026-10-20)

- note: `plugins/sdlc-lite/scripts/hook-selftest.sh:471` and `:521` still use the old "Your final message is saved verbatim as y." in their fixture prompts. This is harmless because no hook parses that string, but the fixtures no longer match what `prepare` emits.

## T-0654: fanout.py sync brings a lane up to date with the integration branch (2026-10-20)

- note: `redck.py deviations` printed no `process deviation:` lines, and the criteria carry no `(red)` tag.
- note: `fanout.py:3017` and `:3022` (cmd_sync): when `--regen` runs, `git add -A -- <hash_bound specs>` stages every change under those globs, including untracked files the regen command creates. This matches "stages its output". The `sync` gate runs only after the commit, as specified.
