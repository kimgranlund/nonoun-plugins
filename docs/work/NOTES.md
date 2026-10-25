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

## T-0679: scripts warn once on stderr when a newer plugin version is installed (2026-10-20)

- note: scripts/check-packaging.py fails on plugins/sdlc-lite/skills/fanout/SKILL.md (18631 characters, limit 18,000) on both the tree and base 5032b547 with the identical message, so it is inherited and not a criterion here; main fixed it in T-0687.

## T-0690: dispatch.py status finds attempts in step folders and the records dir (2026-10-20)

- note: plugins/sdlc-lite/scripts/board.py:249 now also receives orphaned `step-*/` attempts from `dispatch.status(rd, True)`, though its guard at board.py:247 still returns early when the records dir itself holds no `*.attempt.json`; display-only, no criterion covers it.
- note: no builder-*.md report was in the artifacts dir; the handoff Outcome section served as the builder claim, and every claim was checked independently above.

## T-0693: briefs carry a Ports line from lanes.py port (2026-10-21)

- note: plugins/sdlc-lite/scripts/dispatch.py:384 `ports_line` returns '' when no port is found, so a brief for a tree without a lane port keeps the old prompt byte for byte. This was checked by reading the code (the `%s` slot gets ''), and the selftest negative controls also show no `Ports:` line.

## T-0684: settle a deferred: conductor held criterion so land reads it as pass (2026-10-21)

- decide: plugins/sdlc-lite/scripts/steps.py:2877 `owner_settled_hold`: a Criteria line that `results.criteria_states` cannot parse (for example `- #2 y FAILED no evidence`, no `: fail. Evidence:`) is ignored, so a result with such a line plus a settled `deferred:` hold reads as `pass` (probe returned True, and `results.py validate` accepts the file). The gap is the existing parser's, and a validated verifier result normally has no such line; decide: whether `settle-held` or `owner_settled_hold` should refuse a result with unparsed Criteria lines.
- decide: plugins/sdlc-lite/scripts/dispatch.py:1883: evidence with no `## Verdict` heading is accepted unchecked (only a review record's Verdict is judged); that matches the handoff but any existing repo-relative file settles a hold.
- decide: Cleanup: the throwaway worktree was removed with `git worktree remove`; `rm -rf` of the empty prefix dir `tmp:0684-verifier-L2` was denied by the permission system and may remain empty.

## T-0696: A settled hold must not pass a result with an unparsed criterion line (2026-10-21)

- note: plugins/sdlc-lite/scripts/steps.py:2886 the guard treats any bullet under ## Criteria that CRITERION_RE does not match as unparsed, so an indented sub-bullet under a criterion would also block a settled hold. That errs toward not settling, which is the safe direction.
- note: /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0696-verifier-L2 still holds the probe scratch files (rm was denied). The throwaway worktree has been removed.

## T-0698: Lane roles run heavy test suites through gate_lock run (2026-10-21)

- decide: plugins/sdlc-lite/agents/builder.md:14: the command path `${CLAUDE_PLUGIN_ROOT}` is now unquoted (needed for the literal match in criterion 1); a plugin root containing spaces would split the argument. note: accepted by the ticket Outcome.

## T-0697: gate_lock admits by load from a CPU-count default when policy sets no max_load (2026-10-21)

- fix-now: docs/specs/sdlc-lite/gate-lock-admission.md:208 still says "the cap is off unless the operator sets it", now stale: absent max_load is the CPU-count default.
- note: plugins/sdlc-lite/scripts/gate_lock.py:1466 the case_rr "over the load cap with a grant held" check is vacuous against cap removal: every entry needs 6 compute units and the held grant uses 1, so capacity alone refuses them (mutant D left case_rr GREEN). Likewise "then the cap holds" after b3 is held by capacity, not the cap. The real-process case_load_idle carries this proof instead.
- note: docs/specs/sdlc-lite/gate-lock-admission.md:213 the Reason bullet does not say `status --json` `over` is now true only while a grant or legacy holder is held (gate_lock.py:795).

## T-0701: settle --forward says when it skipped its gates (2026-10-21)

- note: plugins/sdlc-lite/scripts/fanout.py:2836 Conductor check on plain `settle fanout/x` (no `--forward`, no `--gate`), run by both the base a8680df4 script and the build script on identical probe repos. When the branch already contains main, both printed `lane still open: ... (not a plugin lane: ...)` and exited 1. When the branch had diverged, both printed `fanout: fanout/x is not a fast-forward of main: ...` and exited 2. Output, exit code and resulting main were the same.
- note: plugins/sdlc-lite/scripts/fanout.py:2819 `--forward` with no `--gate` does not fast-forward, at base or in the build. Both exit 2 with `settle --forward needs at least one --gate CMD ...; nothing merged`, and main stays where it was, for the ahead case and the diverged case alike. This refusal comes before the changed condition, so the build leaves it as it was.

## T-0703: A resumed sub-agent reports back to the conductor (2026-10-21)

- note: plugins/sdlc-lite/scripts/dispatch.py:971-974 answers the conductor's question about the two flags. The old `report-written-unrecorded` fires only for state running or orphaned with a non-empty report, whatever the mtime. The new `report-unrecorded` fires for any state except completed and failed, but only when the report is newer than the attempt record. Running or orphaned with a newer report prints both tokens. Running or orphaned with an older report (for example a report left by an earlier attempt or written before an attempt-record rewrite) prints only the old one. Only the new token covers interrupted and limit-stopped. That is the T-0703 case: `recover` rewrites the attempt to interrupted (dispatch.py:753), so the old flag goes quiet when a resumed agent later writes its report. A merge would need one rule for the older-report case, which the old flag reports and the new one skips by design.
- note: plugins/sdlc-lite/agents/conductor.md:43 names both the SendMessage-to-main resume message and `report-unrecorded` in the recovery paragraph.

## T-0702: Lane agents ran find / for hours despite block-disk-scan (2026-10-21)

- decide: plugins/sdlc-lite/hooks/_role.sh:57: `^solo-|-solo$` gives a user teammate named `solo-notes` or `my-solo` the solo role (and its blocks). Documented in the header comment and acceptable; any prefix or suffix `solo` part matches by design.
- decide: The claim that a teammate's hook payload `agent_type` equals meta.json `agentType` was not captured live by the builder and I did not capture it either; the Outcome labels it inferred.

## T-0700: fanout prep counts other lanes and the load before opening lanes (2026-10-21)

- decide: plugins/sdlc-lite/scripts/fanout.py (load_cap): the ledger-unreadable and `--force` branches have no selftest case beyond the busy, force and quiet cases; the unreadable-ledger path is unobserved. note: no criterion requires it.

## T-0705: dispatch.py status prints one unrecorded-report flag (2026-10-21)

- note: docs/references/sdlc-internals.md:29 the added clause "so a running attempt with a report prints it once)" closes a parenthesis that has no opening one in that sentence.

## T-0699: fanout prep warns when a gate runs a test runner with no worker cap (2026-10-21)

- note: plugins/sdlc-lite/skills/fanout/references/land.md:15 says the warning fires "for each `--gate`", but the code (fanout.py:2240) also checks `--light-gate`. The fanout.py docstring at line 43 names both.

## T-0706: Read-only roles may write in their brief's scratch dir (2026-10-21)

- note: plugins/sdlc-lite/hooks/block-role-write.sh:34-43: I ran adversarial probes directly against the built hook as a planner Write against the real scratch root sdlc-lite-0a5e021b. These were denied (rc=2): a `<root>x` prefix sibling, `<root>-sibling`, another repo's scratch dir (agent-ui-7439b17c), a `<sd>/../../agent-ui-7439b17c` escape, `<root>/..`, the root itself, `<root>/`, `<sd>/..`, a symlink dir pointing outside, a dangling symlink to an outside file, a relative symlink out, a symlink to /etc, a relative path, `./p.md`, `~/p.md`, an upper-case spelling of the root, a repo file, Edit and NotebookEdit inside, an embedded-newline path, and an empty path. These were allowed (rc=0): inside, nested `.txt`, `/private/var` spelling, `<sd>/./pd/../p.md`.
- note: plugins/sdlc-lite/hooks/block-role-write.sh:36: the hook fails closed. With python3 off PATH a scratch Write gave rc=2, and the same PATH plus python3 and git gave rc=0. A hooks dir next to an empty scripts dir (no wtroot.py) gave rc=2, a wtroot.py that raises gave rc=2, and a real wtroot.py copy gave rc=0. In each failure case it falls through to the `.md` result-path rule.
- note: plugins/sdlc-lite/hooks/block-role-write.sh:33: the root is keyed on the hook input's `cwd` (fallback $PWD). A session whose cwd is outside any repo gets a root `$TMPDIR/sdlc-lite/<dir>-<hash>`, which is still under `$TMPDIR/sdlc-lite`. With cwd `/` and no cwd field, a Write to this repo's scratch was denied (rc=2). It also relies on the hook process TMPDIR matching the dispatching Bash's TMPDIR. Here both are /var/folders/n0/.../T/.
- note: plugins/sdlc-lite/hooks/block-role-write.sh:41: a self-looping symlink inside the root is allowed (realpath returns it unresolved). The OS cannot resolve it either, so this is not an escape. A symlink swapped in after the check (TOCTOU) needs Bash, and a read-only role with Bash can already write files.
- note: cleanup of my probe files was refused by the permission system. These leftovers remain: tmp:0706-verifier-L2/out (an empty dir) and /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0706-verifier-L2 (stdout logs, probe.sh, symlinks, fake hooks copy). I removed the throwaway worktree.
- note: redck.py deviations printed no `process deviation:` lines for this artifacts dir.

## T-0708: Hooks treat an unset SDLC_TMP_WORKTREES as the fallback prefix (2026-10-21)

- note: conductor check (run.sh headless role): with SDLC_ROLE=verifier and SDLC_TMP_WORKTREES=<prefix> exported and no agent_type, the built hooks give `rm -rf "$SDLC_TMP_WORKTREES/scratch"` and `"${SDLC_TMP_WORKTREES}/scratch"` rc=0 with permissionDecision allow, and `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD` and `git worktree remove --force "$SDLC_TMP_WORKTREES/base"` rc=0, the same results as the base hooks. No previously working headless path is refused. `varset` comes from `${SDLC_TMP_WORKTREES:+1}` in the hook process (block-role-rm.sh:112, block-stray-worktree.sh:338), not from the fallback `$prefix`.
- note: plugins/sdlc-lite/adapters/claude/hooks.json:10,13 registers both hooks as direct commands with no env wrapper, so they inherit the Claude Code process environment, the same one the role's Bash tool starts from. This was established by reading the registration and observing the env in this sub-agent's Bash (SDLC_TMP_WORKTREES unset). No live host run of the new hooks was made, because the session loads the installed 0.28.1 cache.
- note: plugins/sdlc-lite/hooks/block-stray-worktree.sh still allows `git worktree remove --force "$SDLC_TMP_WORKTREES/base"` for a sub-agent with the variable unset (rc=0 before and after). The shell runs it as `git worktree remove --force /base`, which git rejects for an unregistered path, so it is harmless and out of this ticket's scope.
- decide: the verifier agent instructions (rule 3, `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`) still teach the variable form, which a dispatch.py prepare sub-agent now has refused. That brief text belongs to T-0707 (a Non-goal here).
- note: the throwaway prefix tmp:0708-verifier-L2 and the scratch dir still hold only their dispatch `.owner.json`. `rm -rf` of either directory was denied by permissions. The worktree and my scratch logs were removed.

## T-0710: Fix four verifier-flagged doc and test gaps (2026-10-21)

- note: redck.py deviations printed no process deviation lines for this artifacts dir; no criterion is marked (red).

## T-0707: Briefs say to write worktree and rm paths literally (2026-10-21)

- note: plugins/sdlc-lite/scripts/dispatch.py:1313 says the guard hooks "refuse the command". That holds for `$T` and `$S`, but the first verifier showed that block-stray-worktree.sh:237 and block-role-rm.sh:92 expand a literal `$SDLC_TMP_WORKTREES` and let it through. The hook side is T-0708.

## T-0709: Role definitions name the brief's literal throwaway prefix, not SDLC_TMP_WORKTREES (2026-10-21)

- note: plugins/sdlc-lite/scripts/dispatch.py:1310 dispatch briefs say `Throwaway worktrees only under <literal prefix>`. The new "the throwaway prefix your brief names" / `"<throwaway prefix>/base"` wording matches that line. T-0707 (3c47b09f, on main but not in this lane's base) changes the brief to "never through a shell variable such as $T, $S or $SDLC_TMP_WORKTREES". The definitions only say the variable may be set and never tell a role to use it, so the two agree. `git merge-tree --write-tree main 98ff10b9` merges cleanly.
- decide: plugins/sdlc-lite/scripts/run.sh:710 passes the prefix to a run.sh-launched role only as the `SDLC_TMP_WORKTREES` env var; the run.sh prompt has no throwaway-prefix line. A role launched that way with a brief that names no prefix has to infer from the parenthetical that the variable's value is its prefix.
- note: The throwaway worktrees were removed with `git worktree remove`. `rm -rf` was denied for the empty prefix dir tmp:0709-verifier-L2 and for the scratch dir /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0709-verifier-L2, which holds two selftest logs.

## T-0711: run.sh prompts name the literal throwaway prefix (2026-10-21)

- note: plugins/sdlc-lite/scripts/run.sh:43 the new header comment sentence was appended to an existing line, making it 257 characters where the surrounding header lines wrap near 115.
- note: redck.py deviations printed no process-deviation lines; the artifacts dir holds no builder-*.md (solo lane), so the builder claims were checked against the Outcome section of the handoff.

## T-0712: Briefs say record removes the throwaway prefix and scratch dir (2026-10-22)

- decide: plugins/sdlc-lite/agents/builder.md:20 says "`dispatch.py record` removes the prefix after the run". For a run.sh-launched role (the Codex sdlc-builder-l*.toml), nothing calls dispatch.py record. run.sh's own `cleanup_worktrees` (plugins/sdlc-lite/scripts/run.sh:581-591, called from on_exit at :679 on every exit) removes the prefix instead. The instruction "do not rm -rf it" is still correct, but the line names the wrong mechanism. A neutral wording would fix it, for example "the runner (`dispatch.py record` or `run.sh`) removes the prefix after the run".

## T-0715: Plan review lines in a tracked handoff use repo-relative paths (2026-10-22)

- note: plugins/sdlc-lite/scripts/steps.py:4398 the `amend` and `record_criterion_amends` (steps.py:3542) paths are wrapped in repo_relative but no selftest case drives them; only record_plan_review and record_review_override are exercised.
- note: plugins/sdlc-lite/scripts/steps.py:3279 an `invalid result: <path>` line from print_action is not passed through repo_relative; only the reason and read: lines are.

## T-0714: Review-fix resume refreshes the recorded end tree and keeps the report header (2026-10-22)

- decide: plugins/sdlc-lite/scripts/dispatch.py:1868: decide: `record --update` accepts any completed attempt of any role, not only a resumed builder or ui-designer, and checks only report format; a hand-edited verifier fail rewritten to pass would be accepted and get a fresh `result_sha256` in the attempt (runs.jsonl keeps the original sha, and nothing compares the sha to the file today, so this adds no new capability over editing the file). Consider restricting `--update` to builder and solo, or leaving the old sha in the attempt.
- decide: plugins/sdlc-lite/scripts/dispatch.py:2210: note: the new `stop: changes-required ...` relay text has no selftest assertion; a wording drift between `advance` and conductor.md would not be caught.

## T-0713: fanout.py land leaves lane-close bookkeeping uncommitted in the primary checkout (2026-10-22)

- note: plugins/sdlc-lite/scripts/lanes.py `commit_clear` into a non-main `into` with no integration tree commits on whatever branch the main checkout has checked out; same as ctx.main in every case this repo uses, so no action.

## T-0716: gate_lock run stops a gate whose process tree exceeds a memory cap (2026-10-22)

- fix-now: plugins/sdlc-lite/scripts/gate_lock.py:641-646 the SIGKILL loop reuses the pre-drain `pids` sample, which always includes `child.pid`; `drain_group` has already reaped the child via `child.poll()`. Observed probe: `os.kill(pid=74335, sig=9) is_child=True child.returncode_at_kill=-15`, so the watchdog signals a pid it already reaped, and any group member that died and was reaped by init during the up-to-10 s drain is signalled too; a pid recycled in that window would be an unrelated process. Re-sample `tree_rss` after the drain (or skip `child.pid` and pids no longer descended from the tree) before the SIGKILL loop.
- note: plugins/sdlc-lite/scripts/gate_lock.py:631-636 there is no sampler thread; `wait_watched` is a synchronous `child.wait(timeout=step)`. Under the default cap (32768 MB here) gates exited with their own code: `sleep 3; exit 7` rc 7 in 3.19 s, `exit 0` rc 0, `sleep 0.2; exit 5` rc 5, `kill -TERM $$` rc 143, and with the default 2 s step `sleep 0.1; exit 4` rc 4 in 0.29 s, `status` then `no holders`.
- note: plugins/sdlc-lite/scripts/gate_lock.py:608-628 `tree_rss` walks only ppid descendants of the child, so no process outside the tree at sample time is counted or targeted; the only stray-kill path is the stale pid list in the note above.

## T-0726: steps.py split sets SDLC_TMP_WORKTREES for guard and red spans (2026-10-22)

- note: plugins/sdlc-lite/scripts/steps.py:1042-1053 Conductor check: the temp dir is removed when a span fails or times out. Observed by running a probe of `split --only 1` outside git with TMPDIR pointed at scratch. In all four cases (red guard exit 3, guard timeout at 1s, a green (red) span refusal, a (red) span timeout) the span saw a `split-spans-*` dir, the dir was gone afterwards, and no `split-spans-*` was left behind. Inside git, `span_tmp(<tree>)` made `tmp:split-spans-*` and removed it both on a normal exit and after an exception was raised.
- note: plugins/sdlc-lite/scripts/steps.py:1031-1039 Conductor check: a caller's own SDLC_TMP_WORKTREES is overridden on purpose. With the caller's env set to `/caller/own/prefix`, every probed span saw the fresh `split-spans-*` dir instead. The dir sits under wtroot.tmp_root, the same prefix the role hooks allow.
- note: plugins/sdlc-lite/scripts/steps.py:4251,4397,4653,3697 and redck.py:209, specgate.py:164, traces/rerun.py:115 still call `run_guard`/`red_first` without `tmp`, so `swap`, `amend`, `widen`, `review-red`, `redck` and `specgate` spans keep the inherited SDLC_TMP_WORKTREES. The ticket's Non-goals and Outcome scope these out. If a span there uses the same pattern, the issue would come back, so a follow-up ticket may be wanted.
- note: plugins/sdlc-lite/scripts/steps.py:5367 The selftest runs from a task dir outside git, so it exercises only the fallback to the system temp dir. The in-git wtroot.tmp_root branch was checked only by the direct `span_tmp` probe above.

## T-0730: traces.py detect skips evidence logs, fanout lanes and declared preview worktrees (2026-10-22)

- note: plugins/sdlc-lite/scripts/traces/detectors/hygiene.py `_evidence_dirs` also skips docs/reports/ because it is a default `reports` home in docs_check.DEFAULT_HOMES; this matches the Outcome's "each docs/layout.md home of kind reports" and is not named by a criterion.

## T-0731: gate_lock status explains a load-cap stall (2026-10-22)

- note: plugins/sdlc-lite/scripts/fanout.py:2254 `load_cap` calls `gate_lock.status_data`, which now also runs `ps` (up to the 15 s timeout at plugins/sdlc-lite/scripts/gate_lock.py:483) when the load is over the cap and the queue is not empty. `stall` is an additive key that neither fanout.py nor report.py:1009 reads, and `outside_cpu` fails open, so neither breaks. The only cost is the possible delay.
- note: plugins/sdlc-lite/scripts/gate_lock.py:464 `outside_cpu` catches every `Exception`. That is broad, but the path is display-only and admission never calls it.

## T-0727: steps.py split reports missing dependencies as an environment error (2026-10-22)

- decide: plugins/sdlc-lite/scripts/steps.py:1096 treats a module-not-found line as an environment error whenever the tree root has no node_modules. A Node repo with no dependencies, or a guard whose missing module is a local file the step creates, is then reported as `environment error` with an `npm ci` hint that cannot fix it, and the split never reaches a plan defect. Also requiring a package.json would narrow this.
- note: the Goal names "guard or red span", but split --only runs only (guard) spans (steps.py:796 guard_spans), so only guards are classified.

## T-0728: Planner runs each new-behavior criterion red at base before returning (2026-10-22)

- fix-now: plugins/sdlc-lite/agents/planner.md:29 the new line writes the worktree path as a bare `<tmp>` placeholder. The conductor wanted the literal throwaway prefix from the brief, per T-0709. Rules 3, 8 and 11 (planner.md:31, :40, :43) still use the same `<tmp>` form, which T-0709 left as is, so the line matches its neighbors. No handoff criterion names this. A one-word follow-up across rules 1, 3, 8 and 11 would be `"<throwaway prefix>/base"`, as rule 13a (planner.md:47) already has it.
- note: plugins/sdlc-lite/agents/planner.md:29 the new line does not conflict with the read-only rule or the no-deletes rule. Rule 11 (planner.md:43) already allows a `git worktree add --detach` copy "within rule 1's read-only limits". The new line never asks the planner to remove the worktree, so rule 15 (planner.md:51) still holds.
- note: plugins/sdlc-lite/agents/planner.md:29 the new "last action" sentence comes before the existing "Before returning, dry-run each step's `(guard)` commands" sentence in the same rule, so it is unclear which runs last. This is harmless because both are base runs.
- note: docs/work/0728-planner-red-at-base-check/handoff.md Outcome quote paraphrases the parenthetical ("detached worktree copy of HEAD") and then states the exact in-file wording. It is not a verbatim quote.
- note: redck.py deviations printed no `process deviation:` lines. The ticket has no `(red)` criteria.

## T-0717: dispatch.py prepare uses the handoff base: line for Base sha (2026-10-22)

- decide: plugins/sdlc-lite/scripts/dispatch.py:3086-3094: the new ready-ref case writes a `base:` line into the handoff and restores it afterwards, which is fine; if a later selftest case ever reads that handoff while the line is present, it would break, so keep the restore adjacent.
- decide: Red-checkpoint deviation check printed no `process deviation:` line.

## T-0720: fanout.py land finds a verifier result recorded by prepare --tree (2026-10-22)

- decide: plugins/sdlc-lite/scripts/fanout.py:2550: decide: the new main-checkout fallback in branch_verdict is bound to the ticket slug but not to the current build (no sha or timestamp check). A pass left in main's records dir by an earlier attempt (for example a land that carried a pass into main and then failed its gate) is accepted when a fresh lane for the same ticket holds no verifier and none is committed on the branch. A newer lane-copy or branch result outranks it, a different ticket cannot collide, and the other fallbacks have the same property inside one lane, so it matches the criteria but is the stale-result window the conductor asked about.
- decide: plugins/sdlc-lite/scripts/fanout.py:2543: decide: the fallback weakens selftest coverage of `copy_lane_records`. Removing that call at 5587b51f leaves `fanout selftest: PASS`, because land_ticket's carry_records puts the same records in main and the new fallback reads them. The same removal at 83a3a4e6 fails `case 23 land records copy` and `case 23 land carry`. The records-copy negative control (`SDLC_SELFTEST_NO_RECORDS_COPY=1` now also skips the carry) still passes and still refuses, so it did not weaken; the positive case for the integration copy path did.

## T-0724: Lanes never stage .claude/settings.local.json (2026-10-22)

- note: plugins/sdlc-lite/scripts/lanes.py:1374 Conductor ask (idempotent, never rewrites): I ran a probe with the built lanes.Fixture. It wrote `# user comment\nmy-private.txt` (no trailing newline) to the common info/exclude, then opened 3 lanes. The result was `# user comment\nmy-private.txt\n.lane.json\n.claude/settings.local.json\n`: exactly one settings line, the original lines kept as a prefix, and the main checkout status stayed clean.
- note: plugins/sdlc-lite/scripts/lanes.py:1514 Conductor ask (a repo that tracks the file): `git check-ignore` reports a tracked path as not ignored, so the exclude line is still appended to the common info/exclude. The probe showed this has no effect on tracking: the file stays in `ls-files`, the lane checks out the tracked content, an edit in the lane is still staged by `git add -A`, and the main checkout status stays clean.
- decide: plugins/sdlc-lite/scripts/lanes.py:1514 The exclude is added only at `lanes.py open`. Lanes opened before this change, and checkouts where land or settle run without a prior open, get no line. The Goal's "land or settle tolerate it being untracked" is not covered by any criterion and was not tested.

## T-0729: Builders record a pre-edit red run for each (red) criterion (2026-10-22)

- decide: plugins/sdlc-lite/agents/builder.md:10 says to record "before any edit, a new test ... included" and that "a record taken after any edit is stored as retrospective", but plugins/sdlc-lite/skills/handoff-format/references/step-handoff-rules.md:15 and redck.py split_prelude (redck.py:142) let a handoff `tests:` line declare a regression test the build writes first, which records as pre-edit with a sha256 prelude. A builder following the new line records the (red) span before that test exists (red only because the file is missing) and skips the T-0395 prelude binding. Consider adding "except a test the handoff declares on a `tests:` line".
- note: redck.py deviations on the artifacts dir printed nothing (rc=0); this ticket has no `(red)` criterion.

## T-0736: split's environment error requires declared dependencies (2026-10-22)

- note: conductor probes were run directly against `steps.missing_deps` on fixture trees, comparing the built code with the reverted code. Scoped package `@scope/pkg` (ESM "Cannot find package") and `@scope/pkg/sub` (CJS) with declared deps both give `no node_modules` (env error). The same scoped package with no declared deps gives None (plan defect). An absolute path under `/node_modules/` gives env error. An absolute local path `/lane/src/x.mjs`, a `../lib/x` path, a malformed package.json, and a package.json holding a list all give None. With node_modules present the result is None.
- note: plugins/sdlc-lite/scripts/steps.py:1116 the `command not found` branch is unchanged by the diff. The probe gives `a command is not installed` on exit 127 and None on exit 1. The selftest case `(T-0727) a red guard that exits 127 with "command not found" is an environment error` passes.
- decide: plugins/sdlc-lite/scripts/steps.py:1090 `declares_deps` reads only the tree-root package.json. A monorepo whose root package.json holds only `workspaces`, with dependencies declared in `packages/app/package.json` and no node_modules, now classifies a missing `vitest` as a plan defect (None). The reverted T-0727 code classified it as an environment error, and a root `npm ci` would fix it. A root that holds `workspaces` plus any devDependency still classifies as an environment error. This matches the ticket Goal as written ("a package.json with dependencies or devDependencies"). Counting a non-empty `workspaces` key as declared dependencies would cover the workspaces-only root.
- note: plugins/sdlc-lite/scripts/steps.py:1086 the regex no longer matches a bare `ERR_MODULE_NOT_FOUND` line that has no `Cannot find module/package '<name>'` text. Node's ESM and CJS loaders print both, so this has no practical effect.

## T-0718: dispatch.py advance reverifies at the failing verifier level (2026-10-22)

- note: plugins/sdlc-lite/scripts/dispatch.py:2179 a newest verifier result whose verdict is `inherited red` (not `fail`) falls back to the ticket default level; no criterion covers that case.

## T-0725: lanes.py open takes the merge lock before committing to integration (2026-10-22)

- decide: Deadlock trace, no self-wait: the setup of `fanout.py prep` and `run` is the only in-repo `open_lane` call that passes `into=` (fanout.py:1268). It passes `root=` explicitly, so `explicit_root` is true and `rtop == top`, which takes no lock (lanes.py:1555, the `if rtop != top` guard). It also runs before any MergeLock is taken. `land`, `settle`, `cover`, `roll` and `queue` never call `open_lane` or `lanes.py open`. Only prep's printed `tree:` line and the user run `lanes.py open`. `solo_run.py:585` opens without `--into`, so also no lock. `fanout.py selftest` exits 0 (`fanout selftest: PASS`), covering the cases that call `lanes.py open` around land.
- decide: Lock ordering: `lanes.lock` is released (end of its `with` at lanes.py:1513 to 1529) before `merge.lock` is waited on, so open never holds `lanes.lock` while blocked behind a land. Land's close paths take `lanes.lock` but only after the merge lock is released, so there is no inversion.
- decide: Stale lock: flock is released by the kernel on process death. I held `merge.lock` in a child, wrote a `.holder` file naming its pid, SIGKILLed it, and `fanout.MergeLock` acquired in 0.00 s. fanout.py:6132 also has a selftest for a stale holder.
- decide: lanes.py:62-64 (module docstring): the added line runs past the surrounding wrap width, and the sentence is split mid-clause. Cosmetic only.
- decide: `integration_lock` waits without a timeout or a message, so an open behind a hung land blocks silently. This matches how land and queue treat the lock and the ticket asks for waiting, so no change is needed unless a progress line is wanted.

## T-0722: fanout.py land reads merge_gate from the integration tree (2026-10-22)

- note: plugins/sdlc-lite/scripts/fanout.py:1753 Security angle asked by the conductor: the lane being merged cannot set its own gate class. gate_class runs inside merge_gate_close under the merge lock, after the tracked-dirty refusal (fanout.py:1745-1749) and before `git merge` (its docstring: "Called before the merge, so HEAD is the pre-merge commit"), so it reads the integration tree's pre-merge `.sdlc/config`; the preflight light_refusal (fanout.py:2487-2488) likewise runs before any merge.
- note: plugins/sdlc-lite/scripts/fanout.py:1076 A lane that edits `.sdlc/config` brings a path outside the ticket root, so it lands under the full --gate unless light_scope already covers `.sdlc/config`. Once landed, a weakened `merge_gate`/`light_scope` does lower the class for later lands on that integration branch (that is the ticket's intent). Main stays protected by cover running the full --gate set at the integration tip and settle --require-covered refusing a fast-forward without a green ledger entry for that tip (fanout.py docstring, settle and cover sections); that holds only when settle is run with --require-covered.
- decide: plugins/sdlc-lite/scripts/fanout.py:1745 The dirty check uses `--untracked-files=no`, so an untracked `.sdlc/config` placed in the integration worktree (not committed) would be read by config_root/gate_class. Only fanout writes that worktree, so the risk is low; a repo that wants it closed could require the config file to be tracked at integration HEAD.
- note: plugins/sdlc-lite/scripts/fanout.py:2487 As the Outcome says, an integration branch with no worktree still reads main's config (config_root falls back to root when `where is None`).

## T-0721: fanout.py land closes a second lane ticket whose commits an earlier land merged (2026-10-22)

- decide: plugins/sdlc-lite/scripts/fanout.py:2551: decide: a solo L1 or full-lane ticket that committed nothing itself, sharing a lane with a landed sibling, now closes `commits carried by merge <sha>` with no verifier check (land cannot tell its commits from the sibling's). Same trust as a normal L1 or full land, but an empty sibling is closed on the sibling's work. Consider a follow-up ticket if that is not wanted (e.g. require the ticket's folder or commits to appear in the carried merge).
- decide: plugins/sdlc-lite/scripts/fanout.py:2551: note: `roll_ticket` keeps the same `no changes` short-circuit (builder's Open item, out of scope).

## T-0719: dispatch.py record --no-result closes a stalled solo as failed (2026-10-22)

- note: plugins/sdlc-lite/scripts/dispatch.py:2113 (conductor check): if a solo already wrote its report, `--no-result` does not discard it. The live probe gave rc=0, `solo report: <path>` / `solo recorded; live marker cleared`, and left the report content unchanged (`## Report\nreal\n`). The existing report wins.
- decide: plugins/sdlc-lite/scripts/dispatch.py:972 (conductor check): the closed solo attempt does not show `failed` in `dispatch.py status`. `status` lists only `*.attempt.json` files, and a solo dispatch has none (T-0350). So the live probe printed `no attempts in <dir>` before and after, on both the base and built trees. The solo's runs.jsonl row also still reads `exit_code: 0` and `cost_usd: null` after the `--no-result` close. The only record of "failed" is exit 1 plus the stdout and stderr text. The ticket's criteria do not require a durable failed state, so this is a follow-up, not a fail.

## T-0723: land drops a lane's stale open folder of a ticket closed on integration (2026-10-22)

- decide: plugins/sdlc-lite/scripts/fanout.py:1652 decide: data-loss probe. `drop_stale_open` removes an open folder whenever a closed folder with the same number sits in the index, whatever the open copy holds. In a scratch repo an open `0002-t2` with an extra file and different handoff text was dropped (`D .sdlc/0002-t2/extra.md`, `D .sdlc/0002-t2/handoff.md`). Edits to an open folder do not normally reach this path. A real merge of main's rename into a lane that edited the open handoff keeps the edits in `.0009-t/handoff.md` (checked in a scratch repo), and a rename with too little similarity stops at a modify/delete conflict before the drop. A deliberate re-add that differs from the closed copy is dropped. The content stays in the merge's second parent.
- decide: plugins/sdlc-lite/scripts/fanout.py:1652 decide: the drop is reported only in `merge_gate_close` (land). The other callers (fanout.py:3087 settle, :3314 sync, lanes.py:1116 lanes forward) pass no `dropped` list, so the drop is silent there, although the handoff Outcome says every caller gets it.
- decide: plugins/sdlc-lite/scripts/fanout.py:1660 fix-now: the glob `{trel}/*/handoff.md` matches across slashes and the code keys on `parent.name` only. A nested folder breaks it in two probes. A closed `.sdlc/archive/.0004-y` makes an unrelated top-level open `.sdlc/0004-z` get dropped (`dropped ['.sdlc/0002-t2', '.sdlc/0004-z']`). A nested open `.sdlc/archive/0003-x` beside a closed `.sdlc/.0003-c` makes `git rm -r .sdlc/0003-x` fail with `pathspec ... did not match` and raise Refuse. Ticket folders are direct children of the ticket dir, so this needs a nested NNNN-named folder, which is unlikely. Restricting to `{trel}/*/handoff.md` with a depth check, or comparing `parent.parent`, would close it.
- decide: The same-work-root requirement holds. `drop_stale_open` only looks under `tickets.ticket_dir(root)`, so in the probe a closed `docs/work/.0005-w` did not drop an open `.sdlc/0005-q`, and `docs/work/0005-w` was not touched.

## T-0737: A carried close needs a commit that names the ticket (2026-10-22)

- note: plugins/sdlc-lite/scripts/lanes.py:1246: `lanes.py ready` commits `{tid}: {title}`, so a normal lane commit satisfies the new subject check. A hand-made lane commit whose subject omits the id will now land as `no changes` and stay open, even when the merge carried it.

## T-0738: Stale open folder drop refuses when the open copy holds edits (2026-10-22)

- note: plugins/sdlc-lite/scripts/fanout.py:1825 the outcome string changed from `merge conflict` to `merge conflict: <detail>`. I found no reader that matches the old exact string: `git grep` over plugins/ and scripts/ found only substring checks (fanout.py selftest `'merge conflict' in ...`), `== 'merged'` tests (fanout.py:2095, 2741, 2767, 3436; report.py:1211; land_lanes fanout.py:2695/2708), the traces `_outcome_signal` (RED_RE `^red: ...`, DIRTY, WIP_CELL prefixes; hygiene.py:166) and prose. Other merge_generated callers (fanout.py:3150 settle, :3377 sync, lanes.py:1116 forward) already treat any non-None tuple as a conflict and abort, and none calls drop_stale_open directly, so its new tuple return type has no other caller.
- note: plugins/sdlc-lite/scripts/fanout.py:1683 a normal close (front matter rewrite plus an appended `## Outcome`, then the rename) is not flagged: case 23 (T-0723) runs a real land and close and still drops the copy. A probe over this repo's own history found 297 versions of open handoffs from first-parent main. For 287 of them, the body is a prefix of the closed body.
- decide: plugins/sdlc-lite/scripts/fanout.py:1683 the other 10 versions belong to 5 tickets (T-0641, T-0642, T-0676, T-0707, T-0716). Their handoff body was changed inside the lane, for example a replan in T-0716. A stale copy of such a ticket re-added from main would now refuse even though the closed copy supersedes it. This is what the Goal says, because the text differs. Comparing with the open folder's state at the merge base, which the Intent also allows, would avoid that refusal. The refusal is safe because the merge aborts and nothing is lost.

## T-0739: A stale open copy that matches a committed version is dropped (2026-10-22)

- note: plugins/sdlc-lite/scripts/fanout.py:1682 replay of the T-0738 finding. In a throwaway worktree at 6f4c760d (2990 commits), I staged each open handoff version from first-parent HEAD beside its closed folder and called the built `open_adds`. There are now 303 versions. The T-0738 body-prefix rule still refuses 10 of them, the same 5 tickets (T-0641, T-0642, T-0676, T-0707, T-0716, two versions each). With the history check, all 10 are dropped (`adds=[]`). This replay partly confirms itself, because those versions come from HEAD's history, but it shows that path-limited `git log` does not prune them.
- note: plugins/sdlc-lite/scripts/fanout.py:1683 the cost is bounded. Each stale open folder gets one `git log --raw` over the two folder pathspecs, not one per file per commit. Each flagged file gets one `rev-parse`. On this repo each `open_adds` call took about 0.10s.
- decide: plugins/sdlc-lite/scripts/fanout.py:1683 the log uses default history simplification (no `--full-history`). Suppose a merge is TREESAME to one parent for these paths. Then a version that only the other parent's commits held is pruned and would still refuse. That is the safe direction (the merge aborts and nothing is lost), and no observed version in this repo was affected.

## T-0744: dispatch.py advance and record accept the solo dispatch file prep writes (2026-10-22)

- decide: plugins/sdlc-lite/scripts/dispatch.py:2215 for an L2 or L3 prep solo, advance_solo prepares the ticket verifier against `handoff`, which `solo_record` sets to the main checkout's handoff (fanout.py:2180), not the sub-agent worktree; observed in the e2e run (verifier prompt `Handoff:` names the main-checkout path). The builder's Outcome already flags it as open; a new ticket.

## T-0741: fanout.py prep names every ticket it leaves out (2026-10-22)

- note: plugins/sdlc-lite/scripts/fanout.py:2359 Conductor question answered: the base version does print `prep: load 1000.0 over 3: opening 1 of 2 lanes` as the second stdout line in the issue's 2-lane scenario (observed run); the issue simply did not quote it, and it never named T-0002.
- note: plugins/sdlc-lite/scripts/fanout.py:2362 `load_cap` is the only place prep removes a lane after preflight (`git grep "ctx\['lanes'\] ="` has one hit). Preflight (fanout.py:840-870) refuses with exit 2 for done/dropped status, unknown ids, duplicates, and `--max-lanes` overflow; claimed tickets and `depends:` are not filtered; planned-scope overlap refuses via `refuse_overlap`. A budget hold prints `blocked: budget gate` under the ticket's own line. No other silent drop path found.
- decide: plugins/sdlc-lite/scripts/fanout.py:2295 the new `not planned: T-0002 (load cap ...)` line shares the words `not planned` with the existing `overlap (planned scope): not planned, checked at merge time: T-0001`, which means "no planned scope" rather than "no lane"; a reader scanning for dropped tickets may confuse the two.
- note: the selftest reproduces with 3 lanes rather than the issue's 2; the same mechanism, and the 2-lane shape was checked by hand above.

## T-0740: Solo lanes in host worktrees commit and report where land reads (2026-10-22)

- decide: plugins/sdlc-lite/scripts/fanout.py:2654: land's host-lane commit uses wip_commit (`git add -A` excluding only logs, locks and .running) inside lane_wt, the worktree where the host branch is checked out, gated on kind solo and branch `worktree-T-NNNN-solo` or `worktree-agent-*`. It cannot touch another tree. It does stage any untracked, non-ignored junk in that lane (`.claude/settings.local.json` is ignored in this repo's .gitignore, but not necessarily in a consumer repo). This is the same behavior as the existing wip commits at fanout.py:1507 and :1979. decide: whether a consumer repo needs an exclude.
- decide: plugins/sdlc-lite/scripts/dispatch.py:2108: host_report_copy cannot pick another ticket's report. The fallback searches the same relative path, which names the ticket id (`<id>-solo.md`). It returns None when more than one worktree holds a copy.
- decide: plugins/sdlc-lite/scripts/fanout.py:2272: merge overlap with T-0744 is real. T-0744 (already on main, 1566168e) added `artifacts_dir` through a helper at fanout.py:~2177. `git merge-tree main 59014ab9` reports `CONFLICT (content)` in fanout.py. dispatch.py auto-merges. The merge must keep one `artifacts_dir` entry in the solo dispatch file, not two.

## T-0742: The light gate set runs with dependencies installed (2026-10-22)

- decide: plugins/sdlc-lite/scripts/fanout.py:1210-1216 An install folded into a combined full gate (`--gate 'npm ci && npm test'`) is neither split nor run twice (light_installs returns [] for it, as the conductor asked), but the light set then still runs without node_modules and fails rc=127. deps_note (fanout.py:1204-1205) gives no warning either, because a gate does install. Probed with light_installs/deps_note on a package.json repo: `['npm ci && npm test'] + light ['npm run typecheck']` gives [] and no note.
- note: plugins/sdlc-lite/scripts/fanout.py:1884 A non-Node repo is untouched: the prepend runs only when the integration tree has package.json and no node_modules, and deps_note returns '' with no package.json at the start commit (probe on a plain repo: no note for any gate mix). An existing node_modules in a reused integration tree skips the install.
- note: plugins/sdlc-lite/scripts/fanout.py:1188 INSTALL_ONLY accepts flags only (`npm ci --prefer-offline`, `pnpm install`, bare `yarn`), so `npm install foo` is not treated as an install-only gate.

## T-0746: dispatch.py prune lists only agents that still exist (2026-10-22)

- decide: plugins/sdlc-lite/scripts/dispatch.py:1641 the comment "A queued solo is a background agent that has finished" and the note text "finished background agent" overclaim: a solo spawned as a named in-process teammate (as this repo's conductor does) is still live when queued by `--add`, and TaskStop succeeds on it. The line does not tell the conductor to skip TaskStop (it keeps `TaskStop task_id=` and only says a 'No task found' failure is safe to ignore, then `--done`), so behavior stays correct; consider wording such as "if it was a background agent, a 'No task found' failure ... is safe to ignore".

## T-0745: prepare prints no warning for the normal lane-start base of a ticket verifier (2026-10-22)

- note: I did not run a live `prepare` against a real `.claude/worktrees/<id>-solo` tree: the verifier hook refuses the worktree setup needed and a host record would write into the shared lanes root. The selftest uses the real `lanes.host_record` writer and the real `prepare` entry point in a temporary repo, and the negative control proves it bites.

## T-0748: A re-verify after a lane merges main keeps the ticket's build base (2026-10-22)

- decide: plugins/sdlc-lite/scripts/dispatch.py:3251: the changed T-0376 case is a correct new expectation, not a weakened one. It still asserts the builder gets the lane HEAD and now asserts the verifier gets the fork point (`dver['base_sha'] == fork`). The code change is gated on `role == 'verifier'`, so a builder prepare is unchanged. With the fix reverted this case fails.
- decide: plugins/sdlc-lite/scripts/dispatch.py:3396 and :3404: the two changed T-0745 cases are correct. They now expect `floor3` (the merge point), and `floor3 != start3` is asserted, so lane3 did merge main and the cases cannot pass vacuously. They still assert `'nothing recorded' not in err`, so a recorded start stays quiet. Both fail with the fix reverted.
- decide: T-0717: no named-`base:` case was touched, and all of them are green in the full selftest.

## T-0747: advance prepares a prep solo's verifier on the lane worktree (2026-10-22)

- note: plugins/sdlc-lite/scripts/dispatch.py:2307 the verifier brief's handoff is now the lane copy, whose records dir lacks the prep dispatch json, so base resolution prints `nothing recorded for this step: Base sha is the lane start ...` on stderr. The picked base is still the prep HEAD in both probes, so this is a misleading message, not a wrong base.

## T-0749: One owner-tree rule and helper for sdlc records (2026-10-24)

- decide: plugins/sdlc-lite/scripts/wtroot.py:_lane_rec: decide: the host-record root ignores `lanes_root:`, but `lanes.config` (lanes.py:373) honours it and `dispatch.lane_record_base` finds host records through `lanes.discover`, so it follows `lanes_root:`. With `lanes_root:` set the helper finds no host lane and falls back to primary. This is latent until T-0750 routes dispatch through the helper. Recommend fixing it as the first change in T-0750, together with collapsing the `lane_record_base` lookup, rather than reopening T-0749; there is no regression today because no caller uses the helper.
- decide: plugins/sdlc-lite/scripts/wtroot.py:309 and the config row of the table: note: the #58 note says `wtroot._config_root` reads the current tree. It reads `worktree_root:` from the main checkout (`main_top`) in a non-bare repo and has nothing to do with `merge_gate`, so the clause is inaccurate; it is harmless prose, but T-0751 should reword it.
- decide: API coverage for T-0750 to T-0752: the kinds those tickets name (records, base-sha, end-sha; config, lane-close; branch, worktree) all exist in `OWNERS`. The helper returns only a tree, so callers still join `order.records_dir` or `.sdlc/config` themselves; that is enough for the three tickets as written.
- decide: No `is_lane` or integration-tree-exists signal is exposed apart from `owner_trees`; T-0751 will need `owner_trees(...)['integration']` where `config_root` takes `integ_exists`, which is available.

## T-0752: lanes.py and steps.py read and write records through the owner-tree helper (2026-10-24)

- decide: Conductor check (existing selftests unchanged): the 257cf42c..28278a1d diff holds no hunk in the lanes.py selftest. The steps.py selftest diff is one added block and removes nothing. No existing assertion was edited.
- decide: Conductor check (plain solo flow): in a throwaway repo I ran the new `lanes.py open smoke --kind solo --ticket T-0001`. It recorded `branch:` and `worktree:` in main and committed `T-0001: record lane T-0001-smoke`. `close --discard` of the locked lane was refused (`locked: me T-0001`) identically by the base 257cf42c script and the built one. After `git worktree unlock`, `close` removed the tree and cleared both lines in main (`closed T-0001-smoke (ancestor)`), the same effect the T-0713 selftest cases pin. I did not run `finish` live; the lanes selftest `finish` cases pass unchanged.
- decide: plugins/sdlc-lite/scripts/lanes.py:1431: a host lane under a custom `lanes_root:` still resolves to primary until T-0750, as the Outcome states; not a defect for this ticket.

## T-0735: Audit for run.sh-era assumptions in prepare-launched roles (2026-10-24)

- decide: plugins/sdlc-lite/scripts/dispatch.py:1374: the SDLC_BASE_SHA fix is an instruction, not a mechanism. Observed: with the variable unset, `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- plugins 2>/dev/null)"` exits 0 (vacuous pass) while the bare `git diff` exits 128 `bad revision ''`. A role that ignores the line still passes such a criterion vacuously.
- decide: a `steps.py lint` rule could flag a criterion span that names `$SDLC_BASE_SHA` without a `${SDLC_BASE_SHA:?}` guard or an `export SDLC_BASE_SHA=` in the span, which would make the planner write the guard instead of relying on the brief; steps.py:6084 already has a lint case for this variable (that it is not flagged as a pinned sha), so the hook point exists. Not filed by the builder.
- note: criterion #2 (c), the block-role-rm.sh case, was verified by diff reading plus the shared base run, not an isolated red run.

## T-0751: fanout.py reads config and records through the owner-tree helper (2026-10-24)

- decide: plugins/sdlc-lite/scripts/wtroot.py:308-309: the OWNERS `config` row still names `config_root` and `fanout.py run light_refusal`, now stale. The Outcome flags it and T-0750 owns the file, so this is not a fail.
- decide: plugins/sdlc-lite/scripts/fanout.py:1060-1076: `owner_dirs` lets a lane record's tree win over a `lane=` argument, and `lane.dir`/`ctx['lane_wt']` only fills a None slot. If two worktrees list one ticket in their lane records, the record's tree is picked. Not reachable in the selftests; note: low risk.

## T-0750: dispatch.py reads and writes records through the owner-tree helper (2026-10-24)

- decide: dispatch.py:1033 and :1616: probe in a scratch repo (a lane record listing T-0900, `prepare builder L1` then `record` then `prepare verifier L1`, all from the main checkout, no --tree): Artifacts dir, Report file, dispatch file, base-sha, end-sha and runs.jsonl all land in the lane twin and agree, and the verifier's Diff range reads the builder's end-sha, so no role is misrouted; the brief's Tree line still names main, which only affects where the role works. But `dispatch.py status .sdlc/w` from main then prints `no attempts` while the lane twin shows the running verifier, so status and recover (and steps.py next / plan_done until T-0752) cannot see these attempts from the handoff dir the conductor passed. decide: route status and recover through owned_records, or tell the conductor to pass the lane twin, in T-0752 or a follow-up.
- decide: plugins/sdlc-lite/scripts/wtroot.py:386: owner_trees now takes the current linked tree as the lane for a ticket no lane record lists. Probe: with cwd an integration worktree or a role's throwaway worktree and an unlisted ticket, owner_tree('records') returns that worktree (with a live lane it returns the lane). In dispatch the tree argument is run_tree or the handoff's own checkout, never the bare cwd, so a prepare there already recorded in that tree before this change; only a main-checkout handoff with --tree <integration or throwaway> moves from primary to that tree, which is the table's intent. note: no misfire found in the build; the helper alone would misfire for a caller passing a bare cwd.
- decide: plugins/sdlc-lite/scripts/dispatch.py:3285-3290, 3457: the moved T-0381 and T-0748 fixtures keep their assertions and only move the recorded base-sha to the lane twin (lbase, l4base); the bypass control fails four of them, so they still bite the read side.
- note: runs recorded in primary before this change are not read for base-sha or end-sha when a lane lists the ticket (only ticket_minutes unions them), so an in-flight verifier right after upgrade falls back to the lane start.

## T-0753: Solo briefs give no exported SDLC_BASE_SHA for criteria that name it (2026-10-24)

- note: plugins/sdlc-lite/scripts/dispatch.py:1381 the prepare brief now composes its sentence through `base_export()`; the dispatch.py selftest literal at dispatch.py:3132 still asserts the T-0735 text (`ok: T-0735 the brief has the builder export SDLC_BASE_SHA ...`), and `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` printed `dispatch selftest: PASS`, rc=0.

## T-0754: steps.py lint flags a criterion that names SDLC_BASE_SHA without a guard (2026-10-24)

- note: plugins/sdlc-lite/scripts/steps.py:1517 the guard accepts `export SDLC_BASE_SHA=$OTHER &&` (any other variable), which is empty when `$OTHER` is unset; only a self-read value is refused.
- note: plugins/sdlc-lite/scripts/steps.py:544 with `:` in BUILTINS, prose spans that open with `: ` now count as command spans (e.g. `: <why>` in plugins/sdlc-lite/skills/handoff-format/references/step-handoff-rules.md:7, `: fail. Evidence:` in docs/work/NOTES.md:191); a criterion line holding such a prose span would now be linted with `bash -n` (`: <why>` does not parse). No open plan or handoff criterion holds one today.

## T-0755: steps.py next and plan_done read step records from the tree that owns them (2026-10-24)

- decide: plugins/sdlc-lite/scripts/steps.py:581: note: `records_of` is lane-wins-whole, so a task-level call (lane holds step-1 only) and a step-level call for a step recorded only in primary can see different trees; amend/widen write `step_handoff(d)`, which may resolve to the primary handoff through `tree_twins` when the lane twin has none. Both need records split across trees, which T-0750 no longer produces; no criterion covers it.

## T-0762: settle does not count a removed host lane as open (2026-10-24)

- decide: plugins/sdlc-lite/scripts/lanes.py:3378: note: the committed `host removed` case has no companion for a removed host tree whose branch is NOT an ancestor of the integration branch; I probed it by hand and it holds the tree open (correct), but a future edit dropping the ancestor test would pass the selftest. Consider adding that control.

## T-0756: A host-worktree solo brief asks for no git sync (2026-10-24)

- decide: plugins/sdlc-lite/scripts/fanout.py:2211: decide: the refusal message names only the push; a stale `origin/*` ref (remote ahead of the tracking ref) makes it fire when HEAD is already on the real remote, and the suggested push is rejected non-fast-forward when the remote is ahead. Adding "or `git fetch` if the remote already has it" would help.
- decide: plugins/sdlc-lite/scripts/fanout.py:2211: note: for a base on a non-main branch the message suggests `git push origin HEAD:main`, which pushes that branch to main; correct for what the host cuts from, but worth a human read before running.

## T-0760: dispatch.py advance does not route a blocked solo as done (2026-10-24)

- note: plugins/sdlc-lite/scripts/dispatch.py:2304 the match is case-insensitive and needs no colon, so a first line such as `Blocked on nothing; unblocked` also reads as blocked (probe returned that line); the contract shape is `blocked: <question>`, so anchoring on `blocked:` or the `solo blocked` pointer would be tighter.
- note: redck.py deviations printed no process deviation lines for this artifacts dir.

## T-0764: prep and record print no sweep lines for other repos (2026-10-24)

- decide: plugins/sdlc-lite/scripts/dispatch.py:1475 `record` still prints one `unmarked:` line per own-repo folder, with no summary line (observed: two lines for u-a and u-b). The Goal says "at most one summary line for this repo", and only `lanes.sweep` (the prep path) collapses them.
- decide: plugins/sdlc-lite/scripts/wtroot.py:250 (`sweep`, unchanged) removes a dead-owner folder past the limit in another repo's scratch dir, and both record and lanes sweep print `removed <other repo path>`. This happens at base too and is the documented design ("every repo's scratch dir"), so "never delete another repo's folder" holds only for unmarked folders.
- fix-now: docs/references/sdlc-internals.md:169 still says the sweep lists an unmarked folder, without saying that only this repo's own folders are named now (T-0764).

## T-0757: The verifier of a host lane diffs against the commit the host cut the worktree from (2026-10-24)

- note: Conductor probes run against a scratch repo with an origin bare remote and a host worktree under `.claude/worktrees/w1`, calling `dispatch.build_base(role='verifier')`. (a) origin moved ahead and was fetched, lane unmerged: base stays the cut point (6cf45a0c60ad), not origin's new head. (b) lane merged origin/main after the cut: base becomes the merge point (d6c1151f10e9 = origin/main), so the two rules agree and the diff holds only the lane's own commits. A handoff `base: <sha>` line still wins (returned the named sha, named flag True). `host_fork` returns '' for the non-host worktree, so a lanes.py lane under `../<repo>.worktrees` is unaffected; the existing lane cases (T-0546, T-0748) stay green in the full selftest.
- note: plugins/sdlc-lite/scripts/dispatch.py host_fork is placed before the recorded-base branch, so in a host worktree it also overrides a recorded `base-sha` for a verifier. This is the intended T-0757 behavior (the solo brief's Base sha line still names prep's base, the Open item in the handoff).

## T-0759: A host-lane solo brief names one report path (2026-10-24)

- note: conductor question 1 (can the solo Write a relative path): the Report file line says "write your report to exactly this path with the Write tool" with a relative path, but the same brief's write instruction (fanout.py:574-575, SOLO_SUBAGENT_PROMPT) says `write the report to <rel> under your worktree root (the directory you start in)`, so the brief does tell the solo what to resolve it against; the absolute path is still left for the solo to compose.
- note: conductor question 2 (solo-report check with a relative path): observed in a scratch tree mimicking the worktree layout, `results.py solo-report .sdlc/runtime/tasks/t1/T-0001-solo.md --handoff .sdlc/t1/handoff.md` run from that root gives rc=1 on a report missing the span's exit line and rc=0 on a full one; the brief's `--handoff` is also worktree-relative (fanout.py:2220), so both paths resolve from the solo's starting directory.
- note: conductor question 3 (block-role-write hook): plugins/sdlc-lite/hooks/block-role-write.sh exits 0 for any role not in SDLC_READONLY_ROLES (plugins/sdlc-lite/hooks/_role.sh:34 lists scout researcher architect archaeologist planner plan-reviewer verifier filer), so a solo's Write passes untouched.
- note: docs/work/0759-solo-report-path-one/handoff.md Outcome says case 30c was "the only miss" in its negative control; reverting only the fix line also fails case 22, so that control must have reverted case 22's update too. The criterion holds either way.

## T-0761: settle without --forward leaves main where it is (2026-10-24)

- note: plugins/sdlc-lite/scripts/fanout.py:125 says "--forward only adds the diverged case (merge main in, run the gates)", but with --forward a fast-forward branch is gated too (T-0701, settle_forward at fanout.py:3197-3221); skills/fanout/SKILL.md:31 likewise ties "gate it" to the diverged case only. The cmd_settle docstring and sdlc-internals.md:206 state the T-0701 case correctly.
- note: the new T-0761 case overlaps case 28's `fanout/ff` assertion (both fail under the same mutation); it adds only the `settled: ... is in main` output check.

## T-0763: dispatch status and steps next from main see a host lane's records (2026-10-24)

- note: the case 30b selftest assertion was not seen red with the guard removed through the full fanout selftest (about 9 minutes per run); the guard-removed behavior was observed directly with the probe above (base moves, false line prints), which is the same condition the assertion checks.

## T-0758: The land command prep prints names the branch the host actually made (2026-10-24)

- note: plugins/sdlc-lite/scripts/fanout.py:2615 prints `landing the host branch <b>` for `roll` too (observed in the R2 roll probe), where the action is a roll onto main, not a land.
- note: the probe's fanout/h holds two `T-0001: Ticket t1` commits. One is the host branch's own commit. The other is land committing the report the probe left uncommitted in the host tree (T-0740 behavior), so it is expected and not a T-0758 defect.

## T-0771: board.py renders a done ticket as closed and lets a later verifier pass win (2026-10-24)

- note: `steps.py next` keeps the inherited-red-before-verifier ordering (builder reports it as a deliberate follow-up, T-0766 editing that route); the board and `steps.py next` can now disagree for that case until the follow-up lands.
- note: no selftest case pins a done ticket with a `step-*/*.running` marker in board.py itself; the guard is covered only by the fleet_status selftest.

## T-0766: An inherited red from an earlier step of the same lane routes back into the task (2026-10-24)

- decide: plugins/sdlc-lite/scripts/steps.py:3342: note: the safety claim holds. Every new return None path (merge with a parent on `into`, no lane record, no base-sha, git error, base an ancestor of `into`) falls back to the pre-ticket `inherited`. A wrong `lane red` needs a base off `into` with no merge-from-`into` between the fork point and the base yet a main-born red; `lanes.py` and `fanout.py` contain no rebase, so lane trees take `into` only by merge, and the one residual (a lane commit made after a resync still reads `inherited`) errs the conservative way.
- decide: plugins/sdlc-lite/scripts/board.py:149: note: carried from verifier-L2.md, still true: the board renders a builder Status `inherited red` with the ask-the-user wording whatever `steps.py next` prints, so a `lane red` step shows the old wording.

## T-0769: land reads the ticket status where it closed it (2026-10-24)

- note: plugins/sdlc-lite/scripts/lanes.py:944 Conductor check, this repo's solo-into-main flow: for a lane with `into` main, `wtroot.owner_trees` finds no integration tree (it excludes primary), so `closer` is the main checkout and status is read there as before; the existing `claim still open` selftest case (lanes.py:2924-2942, solo lane into main) still passes with exact output `closed <leaf> (ancestor)` then `ticket still open: T-2`.
- note: plugins/sdlc-lite/scripts/lanes.py:996-1003 Fallback order is the owner tree resolved before the lane tree is removed, else the worktree whose branch is `into`, else main, and a ticket id absent from that tree is read in main. The lane tree itself (which keeps the open copy, #59) is never the read tree: it is removed before the read and owner_trees names it only as `lane`. A tree reads `done` only when a close commit or edit happened there, so a stale tree cannot read a really open ticket as done.
- decide: plugins/sdlc-lite/scripts/lanes.py:988 The reverse edge: a ticket closed by hand in main while the integration tree still reads it claimed now prints `ticket still open` (main is consulted only for ids the integration tree lacks). Before the change main's `done` won. No criterion covers it; an unlikely order, since land closes on the integration branch first.

## T-0774: dispatch.py record tries the transcript before stdin and never blocks (2026-10-24)

- decide: plugins/sdlc-lite/scripts/dispatch.py:2397 After the first bytes, each later chunk waits only `wait/5` (0.2s), so a producer that stalls more than 0.2s mid-stream gets cut off without any warning. Probe in scratch dir (`slow.py 0 0.3 | probe.py`) on a 324016-byte message: read_stdin returned 162008 bytes and the writer got BrokenPipe. If the cut lands inside a result's last section, that part could pass validation as a complete result. A writer whose first byte comes after 1s reads as empty, which is loud: exit 2 with no result, or the transcript is used. The conductor's documented forms are unaffected. Each was read whole with matching sha256: `< file` (324016 bytes), `printf '%s\n' "$msg" |` (40/40 trials, and 20/20 under 40 busy loops on 20 cores), `cat file |` (10/10 under load). `</dev/null` and closed stdin read empty. No current doc or skill pipes a slow producer into record (git grep over plugins and docs).
- note: plugins/sdlc-lite/scripts/dispatch.py:4317 The new selftest cases are bounded by `pr.wait(timeout=20)` plus a kill, so they cannot hang the suite. On a heavily loaded host, a record that takes longer than 20s would turn into a FAIL, not a hang. The cases passed inside gate_lock --nice here.

## T-0781: steps.py next lets a later verifier verdict win over an inherited-red build (2026-10-24)

- note: plugins/sdlc-lite/scripts/steps.py:3396 the build_status -> build_status_or_none swap cannot hide a real blocked build: b's status is non-None at that line (the None case returns at steps.py:3373), and build_status (steps.py:3177) returns the same value for done/blocked and only raised for inherited, which is the path this ticket now lets through. Confirmed by a 75-sequence matrix comparing steps.next_action with board.step_row over builder {done, blocked, inherited} x verifier {pass, fail, inherited red, no verdict} in orders B, B>V, done>V>B, B>V>V: 0 category mismatches at a0c4f56b (the one textual diff is `stop` vs `stop · no verdict x2`, same route) versus 11 inherited-builder mismatches at the base sha.
- note: contract dependents of next_action run green: fanout.py selftest PASS, board.py selftest PASS, `python3 -m traces.selftest` exit 0 (from plugins/sdlc-lite/scripts); dispatch.py:2282 consumes only action names, and no new action name was added.

## T-0775: land merges a lane runs.jsonl into the primary one instead of overwriting it (2026-10-24)

- note: fanout.py:1708 `move_closed_records` copytree(old, new, dirs_exist_ok=True) still overwrites files at the new records dir, runs.jsonl included, if that dir already exists on a numbered-mode rename; not reachable in the observed flow, left alone by the builder, candidate follow-up only if it is ever seen.
- note: fanout.py:1968 `shutil.copytree(src, folder, dirs_exist_ok=True)` for a legacy (folder-borne) records ticket could overwrite folder/runs.jsonl; guarded by the folder being untracked in the integration tree.

## T-0773: Lane commits never add a node_modules symlink; open warns when lane_setup is unset (2026-10-24)

- note: plugins/sdlc-lite/scripts/lanes.py:1427 add_exclude is idempotent. Five calls with NODE_MODULES left exactly one `/node_modules` line in info/exclude (probe.py in the scratch dir).
- note: plugins/sdlc-lite/scripts/lanes.py:257 `/node_modules` is anchored at the top. A probe showed a top-level symlink hidden from status and `git add -A`, while a nested `pkg/node_modules` symlink was still listed and staged. Nested packages are neither affected nor protected.
- decide: plugins/sdlc-lite/scripts/lanes.py:1584 the line goes into the shared common-dir info/exclude, so it applies to the main checkout and every worktree. Edits to tracked files in a tracked top-level node_modules still show as `M`. A new untracked file inside that tracked directory is now hidden, which only matters for a repo that tracks node_modules without a `.gitignore` entry for it.
- note: plugins/sdlc-lite/scripts/fanout.py:2819 builds a full `lanes.Ctx` on each host-lane land just to read `.common`. The cost is small, but the selftest does not measure it.

## T-0767: tickets.py close keeps no absolute path outside the repo (2026-10-24)

- note: plugins/sdlc-lite/scripts/tickets.py:3357 `path_bases` now returns three values. I checked every caller with `git grep`: fanout.py:3475 passes the tuple through `bases=` (it now also gets the outside-path rewrite), tickets.py:3803 falls back to a 2-tuple `([], [])` that `*rest` accepts, and steps.py:895 calls `relative_paths(text, top)`. `fanout.py selftest` and `steps.py selftest` both PASS with rc=0 on the built tree.
- note: plugins/sdlc-lite/scripts/tickets.py:3390 I ran `relative_paths` probes on the built tree. These stay absolute: /tmp, /var/folders, /opt, /private/tmp, `https://github.com/Users/...`, `file:///Users/...`, `~/...` and `/Users/kimgranlund2/...`. A sibling path becomes `../../../Projects/other/x.py`, and a /Users plugin-cache path becomes `../../../.claude/...`.
- decide: plugins/sdlc-lite/scripts/tickets.py:3397 `_outside_paths` also rewrites home paths inside backtick spans and ``` fences in a verifier note (probe: `` `<home>/Projects/other/tick.py` `` became `` `../../../Projects/other/tick.py` ``). This matches how `_inside_paths` already treats in-repo paths and the repo's absolute-path standard, but a fenced example that is meant to show an absolute path changes meaning.
- note: plugins/sdlc-lite/scripts/tickets.py:3392 the docstring says the home directory itself is left alone. A bare `<home>` is left alone, but `<home>/` with a trailing slash becomes `../../../`.

## T-0772: Ticket and lane commands leave no tracked file dirty in the integration tree (2026-10-24)

- decide: plugins/sdlc-lite/scripts/fanout.py:1883-1896: decide: notes.md is in the auto-commit set because `generated_files` returns it alongside the roadmap and router files. The commit is not destructive (the content stays in git history, and the old behaviour was to refuse). The tree it applies to is `<lanes-dir>/integration`, a plugin-managed worktree that `tickets.py close` appends to, not the primary checkout, so a half-edited hand-written notes.md is unlikely there. Keeping notes.md in the set is acceptable; drop it from the set only if a person is expected to edit notes.md inside the integration worktree.
- decide: docs/work/0772-integration-bookkeeping-clean/handoff.md: the Goal is met for what the title and the land refusal name (no tracked file left dirty in the integration tree). The undone `skips.md` move only leaves an untracked file on main when `steps.py lane` runs in the primary checkout; no tracked file is left dirty, and the Outcome gives a sound reason (about ten writers and readers, so moving only `record_lane` would split the file). Note: the suggested follow-up ticket, one skips.md location helper for every writer and reader, is not yet filed.
- decide: plugins/sdlc-lite/scripts/fanout.py:1886-1889: note: the `tickets.Fail` fallback (`gen = {}`) makes an unreadable layout fall back to the old refusal, which is the safe direction.

## T-0776: steps.py next works on a solo ticket task folder (2026-10-24)

- note: plugins/sdlc-lite/scripts/steps.py:3283 and :3317 call `dispatch.solo_dispatch` (dispatch.py:2154) and `dispatch.solo_blocked` (dispatch.py:2335) directly and do not copy their logic. `bool(j.get('verifier'))` mirrors how `advance_solo` (dispatch.py:2346) reads a null verifier as an L1 solo.
- note: `import dispatch` is local to `solo_report`/`solo_ticket_action` and creates no import cycle. dispatch imports steps only inside functions, and none of its module-level imports import steps. Importing dispatch does not put `steps` in sys.modules, and the solo path does not load steps a second time (`-X importtime` shows dispatch once and no `steps`). A step-dir `next` (scratch step-1 with `level: L2`) prints `build L2` and never imports dispatch. On the solo path dispatch costs about 14 to 38 ms.
- note: plugins/sdlc-lite/scripts/tickets.py:2396 also has a `solo_report(d)`, which finds the report from a runs.jsonl `role: solo` row. The live036b shape has no such row, so the steps.py helper of the same name reads the dispatch record instead. The two names collide only by name.

## T-0782: block-disk-scan does not refuse a heredoc body (2026-10-24)

- fix-now: docs/references/claude-hooks.md:31 still says the hook "fails closed, scanning the raw text, on a heredoc"; it now cuts terminated heredoc bodies first, so the reference is stale (AGENTS.md: the affected reference is updated in the same change).
- note: plugins/sdlc-lite/hooks/block-disk-scan.sh:49-85 evasion probe (base 8b232fc8 vs build, SDLC_ROLE=solo). Still blocked at build: `bash -s <<'EOF'` with the search in the body, `sh <<EOF`, `cat <<A <<B` (two heredocs on one line), a here-string `python3 - <<< "...find /..."`, and a search on the command line after the heredoc.
- decide: plugins/sdlc-lite/hooks/block-disk-scan.sh:53 now allows these shapes that base refused: an interpreter running its heredoc body (`python3 - <<'EOF'` with `os.system('find / -name x')` or `subprocess.run('find / ...', shell=True)`, `perl <<'EOF'` with `system(...)`, `node <<'EOF'` with `execSync(...)`, `cat <<EOF | python3`), `xargs find <<EOF` with `/` in the body, `$(cat <<EOF\nfind / -name x\nEOF\n)` and `echo $(cat <<EOF ...)` command substitution, and `source /dev/stdin <<EOF` or `. /dev/stdin <<EOF`. The interpreter cases follow from the ticket Goal, because python3 code and python3 data look the same to the hook. Base never covered a list-argument `subprocess.run(['find', '/', ...])` either, so scans run from inside an interpreter were already a gap. For a guard against accidental slow scans that is acceptable. The two shapes that run the body as shell with no shell word, `$(cat <<EOF ...)` and `source` or `.` of /dev/stdin, could be closed by treating `$(`, a backtick, `source` and `.` as evaluator words in the stripper's SHELL_WORD. Nobody writes those by accident, so this is low priority.

## T-0765: steps.py amend and swap can retag a red-at-base criterion to guard (2026-10-24)

- decide: plugins/sdlc-lite/scripts/steps.py:1106 (base_sha) with :4512 (red_green_at_base): decide: the base the proof runs at is still builder-writable. Observed: a step handoff `base:` line naming an older ancestor (or a rewritten `base-sha` file) is accepted by base_sha when it is an ancestor of HEAD, and no hook protects either file (warn-handoff-edit.sh only warns; block-role-write.sh exempts the builder). In a scratch repo where `flag.txt` exists at ancestor A, is deleted at the real base B and restored by the build, `test -f flag.txt` is red at B (an honest run refuses: "not green at base ... (exit 1)"), but with `base: A` added to the step handoff `steps.py amend` retagged it to `(guard)` and exited 0. What stops it: only that the retagged span must also be green now (a forged base with a span red now is refused as "(guard) red now"), so the forgery needs a span that is red at the real base, green at an older commit and green after the build, and the `base:` line already governs every span's SDLC_BASE_SHA at the same trust level. A cheap hardening, if wanted: take the retag base only from the dispatch-recorded base-sha, or require the named base to equal it.
- decide: plugins/sdlc-lite/scripts/steps.py:3517 and :4708 (amend_retag): note: `next` offers `amend` for a retag pair without running the proof (forged green line only: `next` prints `amend L2`, then `amend` refuses with a plan defect). With the replan spent the refusal goes to the user, which matches the docs route; the proof stays in `amend` alone by design.

## T-0770: settle --forward exits 0 after advancing main with lanes still open (2026-10-24)

- fix-now: plugins/sdlc-lite/skills/fanout/SKILL.md:75 still says settle prints `lane still open` with exit 1 when it cannot close, with no mention of the new exit-0 `settled: main advanced; integration kept (lanes open: ...)` line; references/main.md was updated but the skill body the conductor reads first was not.
- note: plugins/sdlc-lite/agents/conductor.md:57 and plugins/sdlc-lite/skills/run-plan/references/run-rules.md:37 describe settle as always removing the integration tree; with lanes open it now exits 0 and keeps the tree, so a later settle or sweep is needed to retire it (the old exit 1 also kept it, so no caller reads it wrong).
- note: plugins/sdlc-lite/scripts/lanes.py:1374-1379 `finish` now continues to its close step instead of stopping at `settle` when other lanes are open into the integration branch; the integration tree stays, so the `ldir` rmtree guard skips it, and lanes.py selftest stays green.

## T-0780: Give the fanout skill room under its size limit (2026-10-24)

- note: plugins/sdlc-lite/skills/fanout/references/lane-lifecycle.md:9 still says an integration tree with uncommitted tracked changes is refused as `integration dirty` and does not mention the T-0772 bookkeeping exception. SKILL.md:37 states it, but the moved paragraph was stale already at base.
- note: plugins/sdlc-lite/skills/fanout/SKILL.md:58 mentions a `stop: blocked` after a solo report inside the full-ticket item, but full tickets run /chain builders, not a solo, so the clause fits item 3 better.

## T-0768: fanout.py land names the gate log and failing line on red (2026-10-24)

- fix-now: plugins/sdlc-lite/scripts/fanout.py:82 the land docstring still says `red: <gate> rc=<n>`; line 331 and `references/land.md` give the new form.
- fix-now: docs/references/sdlc-internals.md:190 still says a red gate appends the npm hint to `red: <gate> rc=<n>`; the land line now carries ` (log <path>)` and an optional `: <line>` before the hint.
- fix-now: plugins/sdlc-lite/scripts/fanout.py:1976 `glog.read_text(...)` reads the whole gate log into memory before scanning it from the end; a bounded tail read would find the same last failing line with bounded memory.
- note: plugins/sdlc-lite/scripts/traces/sources/fanout.py:39 the tail group `\(log [^)]*\)` fails to match a log path that contains `)`; lanes paths do not today.
