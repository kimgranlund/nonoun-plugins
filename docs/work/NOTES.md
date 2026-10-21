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

## T-0648: prepare appends the repo skills for a step's file scope (2026-10-20)

- note: the handoff Outcome says `solo_run.py selftest` exits 0; I ran it and it printed `solo_run selftest: PASS`. The solo brief line itself (solo_run.py:201-204) has no dedicated selftest case, and criterion 1 does not require one.
- note: the dispatch.py selftest takes longer than 5 minutes under load; a loaded host may need a foreground timeout of 600000 ms.

## T-0667: record --agent-id reads the final message from the transcript (2026-10-20)

- decide: plugins/sdlc-lite/skills/build/SKILL.md and 12 other skills (fix, agent, architect, dig, file, scout, research, verify, bench, fleet-retro, review-traces, plan/references/steps.md) still say "with the sub-agent's final message on stdin", per the builder's Outcome; this needs a follow-up ticket to align them with conductor.md:41.
- note: the scratch dir /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0667-verifier-L2 still holds the mutation copies (plug, plug2, *.out); the permission system denied rm there.

## T-0655: prepare checks lane guidance against main and named guidance paths (2026-10-20)

- note: the `redck.py deviations` run printed no `process deviation:` lines, and criterion #1 is not marked `(red)`.
- note: the harness denied `rm -rf` of the scratch dirs `tmp:0655-verifier-L2` and `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0655-verifier-L2`; the throwaway worktree `neg` was removed with `git worktree remove`, only the plain scratch repos `r` and `r-lane` remain in the second path.

## T-0673: Skills say record reads the transcript, not the final message on stdin (2026-10-20)

- note: plugins/sdlc-lite/skills/agent/SKILL.md:36 tells the solo `record` call to add "`--transcript` when you have it". That is still optional and correct, but the guidance differs from the other skills; item 41 does not match it because it has no `<dispatch_file> --` form.
- decide: the handoff's Non-goals ("any script change") contradict criterion 2 as written, because item 41 had to change. Future tickets that reword a check-enforced phrase should name the check in Do.

## T-0670: close verdict reason matches the recorded lane (2026-10-20)

- note: plugins/sdlc-lite/scripts/tickets.py:3552 also refuses `delivered by the solo agent` when the recorded lane is `fix` (or any other value that maps to `full`), slightly wider than the Do's solo vs full/lean wording; no criterion covers it and no producer writes that combination today.

## T-0674: prepare refuses a guidance path that is missing everywhere, not only in the lane (2026-10-20)

- note: plugins/sdlc-lite/scripts/dispatch.py:77 the header paragraph now breaks after "An" with a short line, so it is ragged next to its neighbours. This is cosmetic only.

## T-0669: Dispatch and skip records go to the records dir, not the work root (2026-10-20)

- note: plugins/sdlc-lite/scripts/tickets.py:3846-3852 the post-rename `moved += move_records(d, every=True)` plus `d.rmdir()` is unreachable through close: `d.rename(dot)` removes `d`, so `move_records` returns [] on `not d.is_dir()`. I removed the call in the throwaway worktree and tickets.py selftest still passed. The undotted-leftover move is exercised only by a direct `move_records(left, every=True)` call in the selftest. Close's real effect is the pre-rename move of `*.dispatch.json` / `*.attempt.json`; leftovers created after a close are handled only by check's new warning.
- note: the criterion 2 close case puts the dispatch record in the ticket folder itself (pre-rename), not in a separate undotted sibling; it satisfies the criterion text and bites, but does not model a leftover sibling.

## T-0661: Verifier brief carries a base..end diff range per built step (2026-10-20)

- note: `plugins/sdlc-lite/scripts/dispatch.py` selftest case (b) asserts the stash stack in a fresh temporary repo whose stack is empty, so `before == after` would also hold for a stash-and-pop implementation; the real-repo stash count (1 before and after) and the code read cover it.
- note: `plugins/sdlc-lite/scripts/dispatch.py` around line 113, the module-docstring sentence on `end-sha` was inserted mid-paragraph before "Every brief carries a Report file line", leaving that line over-long; cosmetic only.

## T-0675: close drops follow-ups whose leading file path matches a filed ticket's slug (2026-10-20)

- note: plugins/sdlc-lite/skills/ticket/SKILL.md:51 says a follow-up is a duplicate on "normalized title or slug"; the slug comparison now skips leading path-like words, which that sentence does not mention.
- decide: plugins/sdlc-lite/scripts/tickets.py:3777 the path-skip regex also strips a leading word like `Node.js`, and the shorter key (e.g. `src/x.py: fix bug` -> `fix-bug`) can now match an unrelated ticket folder slugged `fix-bug`; narrow, but a new false-duplicate path.

## T-0676: repo_skill_routes reads markdown-link and nested AGENTS.md prose skill routes (2026-10-20)

- note: T-0676-t0676:plugins/sdlc-lite/scripts/steps.py:182 the lint help text line has grown to about 180 characters ("... else against the repo root. A step whose scope allow-list ..."), well over the neighboring lines' wrap width; cosmetic only.
- note: during verification I briefly copied a mutated steps.py into the repo scripts dir and removed it straight away; `git status --short` was empty afterward, so the tree is unchanged.

## T-0680: lanes.py open --into an integration branch writes the claim and lane record there, not on main (2026-10-20)

- decide: plugins/sdlc-lite/scripts/lanes.py:69: the docstring line "A path already dirty before the open ..." is now 187 characters, joined onto the added text instead of re-wrapped like the surrounding ~120-column lines.
- note: the builder's Open item stands. `lanes.py close` removes `branch:` lines only from the main checkout's root, so a record written in an integration tree is not removed by close (possible follow-up ticket).

## T-0678: record judges a result by the plugin version that prepared it (2026-10-20)

- decide: `/Users/kimgranlund/.claude/plugins/cache/sdlc-lite/sdlc-lite/0.28.1/scripts/redck.py deviations` printed no process deviations.
- decide: Selftest mutation runs take several minutes each (three sequential runs exceeded the 600 s foreground cap).

## T-0683: merge_union config: land union-merges listed paths behind one light gate (2026-10-20)

- decide: plugins/sdlc-lite/scripts/fanout.py:1719: the force-full-gate-class behavior on a union land (`gate: full (union-merged)`, gates chosen at line 1735) has no selftest case; no criterion names it, so it is unverified by a run.

## T-0688: dispatch.py advance handles ticket-level completions (2026-10-20)

- decide: plugins/sdlc-lite/scripts/dispatch.py:2013: the L1 solo close line, the ui-designer branches (`next: <verdict>` / `stop: changes-required`) and the "other role keeps `next: <hint>`" branch have no selftest case; read-only inspection only, `results.key_value` for ui-designer is keyed on `## Mode` (results.py:81, 307) so `verdict_word == 'review'` matches. note: not a criterion.
- decide: Scratch dir /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0688-verifier-L2 (a copy of the plugin plus selftest logs) could not be removed: the permission layer denied `rm -rf` on it. note: harmless, outside the repo; the detached worktree was already removed.

## T-0694: lanes.py ready warns once per session and runs --notify-cmd on pin (2026-10-20)

- note: plugins/sdlc-lite/scripts/lanes.py:1716 `if notify_cmd: pass` followed by `elif` reads awkwardly; `if not notify_cmd:` wrapping the two branches would say the same thing.
- note: plugins/sdlc-lite/scripts/lanes.py:191 the docstring line ending `(T-0694); any other refused send prints ...` runs well past the surrounding wrap width.

## T-0692: lane_setup config commands run by lanes.py open (2026-10-20)

- note: docs/specs/sdlc-lite/lane-lifecycle.md:220 still says a failed setup records `setup: failed rc=<n>`. The record now appends ` (<cmd>)`, and the spec does not mention repeated lines.
- note: the contract changed from `config()['lane_setup']` as a str or None to a list. `git grep lane_setup` and `git grep "'setup'"` across plugins/ and scripts/ find no consumer outside lanes.py, and fanout.py selftest passes.

## T-0682: solo_run.py briefs carry Report file and pointer lines, and record reads the solo report file (2026-10-20)

- note: the throwaway scratch dirs `tmp:0682-verifier-L2` and `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0682-verifier-L2` hold only leftover logs; the negative-control worktree itself was removed, but `rm` was denied in this session so the two dirs remain.
- note: no builder-*.md report existed in the artifacts dir, and `redck.py deviations` printed no `red-checkpoint` line.

## T-0691: accept --tickets T-1,T-2 on lanes.py open, fanout.py land and tickets.py claim (2026-10-20)

- note: /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0691-verifier-L2/ holds my scratch logs and a copied scripts dir (`mut/`); `rm -rf` there was denied by the permission layer, so it is left behind. The throwaway worktree was removed with `git worktree remove`.

## T-0685: record --agent-id ignores short heading-less stdin when the transcript holds a complete result (2026-10-20)

- note: tmp:0685-verifier-L2 may remain as an empty directory; the worktree was removed with `git worktree remove --force` but `rm -rf` of the prefix dir was denied by the permission hook.

## T-0681: merging main into an integration branch regenerates .sdlc/AGENTS.md and ROADMAP.md (2026-10-20)

- decide: `settle --forward` was refactored (`settle_forward` now calls `merge_into_integration`); its messages, commit subject and exit codes read as unchanged in the diff and the existing T-0489 selftest cases still pass in the green selftest run.

## T-0686: record prints a repo-relative Review record line; lint warns on absolute home paths in criteria (2026-10-20)

- decide: plugins/sdlc-lite/scripts/steps.py:1746: `ABS_HOME_RE` copies the `tickets.ABS_PATH_RE` pattern as a literal, not an import, so the two can drift. The handoff said to reuse the pattern, and this is acceptable.

## T-0687: document merge.lock land queueing and add fanout.py queue (2026-10-20)

- decide: plugins/sdlc-lite/scripts/fanout.py:1297 (MergeLock): the holder file is written after the flock is taken and removed before release, so a land killed with SIGKILL leaves a stale file; `queue` reports it as `stale holder`, as the Constraints require.

## T-0689: fanout.py prep --integration reuses an existing integration worktree (2026-10-20)

- note: plugins/sdlc-lite/scripts/fanout.py:2398 adds a main-checkout refusal to land_preflight, but no selftest case covers it. The reuse control only exercises the prep refusal.
- note: plugins/sdlc-lite/scripts/fanout.py:2402 has land_preflight reuse whichever non-main worktree holds the integration branch. Prep is gated by reuse_integ, while land has no flag of its own (the handoff asked for this).
