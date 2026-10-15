#!/usr/bin/env python3
"""Consistency checks for the sdlc-lite plugin. Exit 1 on any mismatch.

1. Level tables agree three ways: adapters/claude/levels.json (the table home), scripts/run.sh (until its Claude branch is retired),
   and skills/level-rubric. Repository guidance links these sources instead of copying tables. Negative controls: one effort changed in
   each of the three sources must be flagged.
2. Every agents/<role>.md (the role files, not the generated per-level definitions) has levels.json rows, every levels.json pipeline
   role has an agent file, and every levels.json row has a run.sh case and every run.sh case a levels.json row until run.sh is retired.
3. Every skill an agent declares (frontmatter skills:) exists under skills/.
4. Long role runs: chain, bench, fanout, and conductor state the interactive vs headless rule.
5. Plan-defect route: the `plan defect` tag, the `Plan review` section, and the planner's
   "no new findings" rule appear in every doc and script that carries the route, and the
   `recurring finding` rule (a repeat fail or block takes a replan) appears in every doc that routes it,
   the parallel-lane rules ("sha fixed at plan time", linted by steps.py, "owns that budget", a guard that
   "can go red", and "membership or structure" checks) appear in the planner, the planner's "gates green" rule
   (whole-suite gate guards go on one final step, never on every step) appears in agents/planner.md, and the one-criterion swap (`swap old:` and `swap new:` lines on a plan-defect
   fail, applied by `steps.py swap`) appears in agents/verifier.md and scripts/steps.py, and the
   `steps.py swap` route appears in the conductor, the chain, handoff-format, and level-rubric skills,
   the builder's one-criterion amend (`amend old:` and `amend new:` lines under a blocked build's
   `plan defect:` note, applied by `steps.py amend`) appears in agents/builder.md and scripts/steps.py, and the
   `steps.py amend` route appears wherever `steps.py swap` does,
   and the build-start base `SDLC_BASE_SHA` appears in the planner, builder, verifier, run.sh, and steps.py.
6. Merge-step template: the fenced merge-step block in agents/planner.md and
   skills/handoff-format/SKILL.md is present and identical, passes `steps.py lint`,
   runs its conflict-marker guard (merge-introduced markers only) against a throwaway repo in seven
   cases (empty merge, merge-added marker, clean lane marker line, kept conflict markers,
   both-sides lane marker line, aligned kept marker, clean merge), and agents/builder.md
   names `git merge --no-ff`. The aligned-marker case pins a known miss: a kept marker textually
   identical to a parent line that aligns with it shows as `+ ` or ` +`, not `++`.
7. /file likely duplicates: skills/file/SKILL.md names the dry run's `open T-NNNN` lines and
   the `likely duplicate` marking of follow-ups that restate an open ticket.
8. Inherited-red route: the phrase `inherited red` (a gate already red at the pre-build HEAD) appears in
   agents/builder.md, agents/verifier.md, agents/conductor.md, skills/chain/SKILL.md, scripts/steps.py, scripts/board.py,
   scripts/run.sh, scripts/fanout.py, and skills/fanout/SKILL.md.
9. Finish-in-session: the follow-up tags `fix-now:` and `decide:` and the `notes.md` sink appear in
   agents/filer.md, scripts/tickets.py, skills/file/SKILL.md, and skills/ticket/SKILL.md; `fix-now:` also in
   skills/chain/SKILL.md and agents/conductor.md; `decide:` also there and in skills/open-questions/SKILL.md;
   `notes.md` also in skills/handoff-format/SKILL.md and agents/conductor.md; and `Loose ends` (/chain 5) in
   skills/chain/SKILL.md, agents/filer.md, skills/handoff-format/SKILL.md, skills/level-rubric/SKILL.md, and
   agents/conductor.md.
10. Read-first route: the phrase `Read first` (entry files a role reads before a step) appears in
   agents/planner.md, agents/builder.md, agents/verifier.md, skills/fix/SKILL.md, skills/chain/SKILL.md,
   skills/handoff-format/SKILL.md, and scripts/steps.py.
11. Plan-review route (in the plan-defect route dict): `plan-reviewer` appears in scripts/run.sh, the level-rubric,
   chain, plan, and handoff-format skills, agents/conductor.md, and scripts/steps.py; `steps.py review` in the chain,
   plan, level-rubric, and handoff-format skills, agents/conductor.md, and scripts/steps.py; `## Assumptions` and
   `unresolved:` in agents/planner.md, agents/plan-reviewer.md, and scripts/steps.py; `Missing decisions` in
   agents/plan-reviewer.md, skills/chain/SKILL.md, and agents/conductor.md; and `plan review:` in agents/planner.md,
   skills/chain/SKILL.md, skills/handoff-format/SKILL.md, and agents/conductor.md.
12. Messenger agent: agents/messenger.md exists, pins `model: sonnet` and `effort: low`, and names `messages.py` and
   `.sdlc/messages/AGENTS.md`; adapters/codex/models.json has a `messenger` entry; and the generated
   adapters/codex/agents/sdlc-messenger-l1.toml exists. It also carries the persistent-poller rules (T-0369): `SendMessage` delivery,
   the `Parent: <address>` startup ping, the same-turn loop, the yield line, the `inbox-<repo>-<receiver>` spawn name, the
   `find` and Monitor host pitfalls, and the claim/handled report format. Negative controls: empty text, no `messenger` key,
   no TOML, and the text with each of those words removed. It also carries the lifecycle procedure (T-0380): the
   `activate`, `beat` and `release` commands, the `supervisor.py` continuation route, that a message is never new
   authorization, and that a schedule or `activate` is no evidence of idle delivery; the generated mailbox text in
   scripts/messages.py carries the same procedure under `## Activate a worker`. Negative controls: each phrase removed.
13. Result schema: for each role in results.SCHEMA, agents/<role>.md has every declared section as a `## <Section>`
   line, first occurrences in declared order; scripts/run.sh and scripts/steps.py hold no copy of the schema table.
   Negative controls: builder body with `## Changes` and `## Checks` swapped; run.sh with an `allowed='x'` line.
14. Lean lane text: `## Lean chain` and `writes the Outcome` appear in skills/chain/SKILL.md;
   `independently verifiable outcome` appears in agents/planner.md; and `steps lint: warning:` appears in
   agents/planner.md and scripts/steps.py. Each pair has a negative control (the phrase removed must be flagged).
15. Evals lock: when `<plugin>/../../.sdlc` exists, `scripts/evals.py check` must pass for it: every eval is valid,
   and `evals/table-lock.json` holds the current model-table hash (read from adapters/claude/levels.json and the Codex models.json)
   and cites a valid eval dated later than its `previous_eval`. Each problem line prints as `FAIL evals: <line>`. With no such
   folder, the guard prints `skip: evals lock guard`. Negative control: levels.json with the builder:L1 model changed gives
   `model table changed`.
16. Spec gate: `guard timeout:` appears in agents/planner.md, skills/handoff-format/SKILL.md, scripts/steps.py,
   and scripts/specgate.py; `specgate.py check` appears in scripts/run.sh, skills/chain/SKILL.md, and
   agents/conductor.md; `specgate.py red` (the red-first control for a `(red)` criterion) appears in
   agents/solo.md, agents/planner.md, and scripts/steps.py; and the first `specgate.py check` line of run.sh comes before its
   `exec python3 "$plugin_root/scripts/run_lifecycle.py"` line. Negative controls: each phrase removed, and the
   two run.sh lines swapped, must be flagged.
17. Carry forward: `## Carry forward` appears in agents/scout.md, agents/researcher.md, agents/architect.md,
   agents/archaeologist.md, agents/ui-designer.md, agents/planner.md, and agents/builder.md; `at most 15 lines` in the five
   producing contracts (scout, researcher, architect, archaeologist, ui-designer); `search only what it does not answer` in
   agents/planner.md and agents/builder.md; and `cite the result path` in agents/planner.md. Each pair has a
   negative control (the phrase removed must be flagged). results.SCHEMA declares `Carry forward` last for the
   five producing roles, so item 13 also requires the `## Carry forward` heading line there.
18. Solo agent: agents/solo.md exists and names levels L1, L2, and L3 with `Sonnet high`, the row `| L2 | L2 | Opus medium |`, and
   `Opus high`; adapters/codex/models.json has the `solo` entry L1 gpt-6.1-sol medium, L2 gpt-6.1-sol high,
   L3 gpt-6.1-sol xhigh; the generated adapters/codex/agents/sdlc-solo-l1..l3.toml exist; and adapters/claude/levels.json has the
   `solo` levels L1 sonnet high, L2 opus medium, L3 opus high. Negative controls: each phrase removed, no `solo` key, a changed
   `solo` entry, one TOML missing, and a changed levels.json solo level must be flagged.
19. Conductor rules: agents/conductor.md names (1) the philosophy line and the objective line `cheapest path that
   still passes independent verification`, (2) lane-first routing (`Lane first: run` then `steps.py lane`) and the
   dispatch line `Lane: <lane> because <reason>`, (3) the stop rules `hard stop that comes to the user`, and (4) the
   thin-conductor rule `take back conclusions, not file contents or logs`. Each has a negative control (the phrase
   removed must be flagged).
20. Handoff freeze (warn mode): scripts/run_lifecycle.py names `SDLC_HANDOFF_SHA256` and `handoff_sha256`; scripts/run.sh
   names `SDLC_HANDOFF_SHA256`, `stale_input`, and `stale input:`; hooks/warn-handoff-edit.sh exists and is executable;
   adapters/claude/hooks.json registers it under an `Edit|Write|NotebookEdit` matcher; docs/references/claude-hooks.md names
   it. Each has a negative control (the phrase, file, or registration removed must be flagged).
21. Solo start path: agents/solo.md holds the start command `--agent sdlc-lite:solo`, and the routing texts send ticket
   levels L1 and L2 to `solo`: agents/conductor.md, skills/fix/SKILL.md, AGENTS.md, and (from the repository root)
   .claude/agents/sdlc-lite-author.md. Negative control: each phrase removed must be flagged. Claude headless retirement (T-0288):
   scripts/run.sh holds `SDLC_CLAUDE_EXEC` and `dispatch.py prepare` in its Claude refusal, and scripts/solo_run.py holds `SDLC_CLAUDE_EXEC` and fanout.py's default_driver body holds it
   so no `claude -p` runs by default (items 4, 20, 27 name the opt-in path only). Negative control: each phrase removed.
22. Ticket budget: `budget.py set` appears in skills/ticket/SKILL.md; `budget.py` and the `4 ticket budget` exit line
   in scripts/run.sh; and `budget.py` in scripts/board.py. Each pair has a negative control (the phrase removed
   must be flagged).
23. Guard numbers: the docstring's numbered guards run 1..N once each, and every `docstring item N` comment names an
   existing one. Negative controls: a duplicated number, and a comment citing a missing item, must be flagged.
24. Fanout solo first: scripts/fanout.py names `sdlc-lite:solo`, `solo_command(`, `SOLO_VERIFIER`, `--max-lanes`,
   `--stagger`, `--yes-many`, `--allow-overlap`, and the sub-agent lane entry points `def cmd_prep(`, `def cmd_land(`, and
   `SOLO_SUBAGENT_PROMPT`; its SOLO_TIERS agree with the levels in agents/solo.md (L1 `Sonnet
   low`, L2 `Sonnet high`, L3 `Opus xhigh`) and the Codex levels L1..L3; skills/fanout/SKILL.md names `Solo first`,
   `--max-lanes`, `--stagger`, `fanout.py prep`, `fanout.py land`, the `Tree: <path>` line of a full-chain brief, and `wtroot.py root`. Negative controls: a changed level, and each phrase removed, must be flagged.
25. Agent command: skills/agent/SKILL.md names every agents/*.md stem in backticks, its start table names only
   agents that exist and have a Codex entry in adapters/codex/models.json, and it names `block-role-spawn.sh`.
   Negative controls: a stem removed from the skill, a table row for a name with no agent file, and a table row
   with no Codex entry must each be flagged.
26. Solo lane skips: scripts/steps.py names `solo_skips_text`, `write_solo_skips`, and calls `write_solo_skips(task)` in
   `record_lane`; scripts/fanout.py calls `steps.write_solo_skips`; agents/conductor.md says a solo ticket closes with
   `tickets.py close --reason`. Negative controls: each phrase removed must be flagged.
27. Solo cost capture: scripts/solo_run.py names `sdlc-lite:solo`, `SDLC_ROLE`, `cost_usd`, `cost_reason`, and `total_cost_usd`;
   its TIERS agree with the levels in agents/solo.md and with fanout.py SOLO_TIERS; agents/solo.md names `solo_run.py` as the
   start path. Negative controls: a changed level, a phrase removed from solo_run.py, and solo.md without `solo_run.py`, must be flagged.
28. Solo budget gate: scripts/solo_run.py names `budget_hold`, `budget.py ack`, `--new-task`, and returns 4 when it holds;
   scripts/fanout.py names `budget gate: budget.py ack`; agents/solo.md, skills/agent/SKILL.md, and skills/fanout/SKILL.md name
   the gate and `--new-task` where they start solo. Negative controls: each phrase removed from each file must be flagged.
29. Ask skill: skills/ask/SKILL.md names `## 1. Sweep`, `## 2. Reason the options`, `## 3. Ask once`, `## 4. Take prose`, `Write it in chat`,
   `Nothing open.`, `AskUserQuestion`, the sweep searches (`tickets.py --root .sdlc blockers`, its `--scope`, and `## Verdict` results), and the plain-text fallback
   `If AskUserQuestion is unavailable`, and holds no `harness:` reference; skills/sdlc-lite/SKILL.md and agents/conductor.md route to
   `ask`. Negative controls: each phrase removed, a harness reference added, and a routing line removed must be flagged.
30. Document inventory: scripts/inventory.py names the flags `orphan`, `stale`, `duplicate`, `oversized`, `misplaced`, and `broken_links`, the options
   `--include-sdlc` and `--out`, and refuses to write inside the repository; scripts/check.sh runs `inventory.py selftest`;
   docs/planning/repo-onboarding/reorganization-plan-procedure.md names `inventory.py`. Negative controls: each phrase removed from each file must be flagged.
31. Plan skills: skills/plan and plan-loop each name `## 1. Gather`, `plan_check.py`, `AskUserQuestion`, `Why this plan`,
   `You must authorize`, `Unattended`, and `Codex host`, hold no `harness:` reference, and are routed from skills/sdlc-lite/SKILL.md (as `plan <kind>` and `plan-loop`);
   skills/plan also names each of the five kind tokens and `references/plan-rules.md` (T-0468).
   Negative controls: each phrase and each kind token removed, a harness reference added, and a routing line removed must be flagged.
   Compaction kind (T-0465): skills/plan/SKILL.md names `compaction` and `references/compaction.md`; that reference names `plan_check.py compaction`,
   `Run: /compact`, `lines: N of 60`, `## Compaction handoff`, `compaction_handoff.py`, `git check-ignore`, the verbs `KEEP`, `POINT`, `DROP` and `NEXT`,
   `[U]`, and `Codex`, and holds no `harness:` reference; skills/sdlc-lite/SKILL.md routes `plan compaction`. Negative controls: each phrase removed
   from its file, the reference reported empty, a harness reference added, and the entry row removed must be flagged.
32. Broken-link baseline: the broken relative Markdown links that rename_refs.py `links` reports (code fences and inline code excluded)
   equal the rows of docs/reports/broken-links-allowlist.md. Negative controls: an extra broken link and a stale allowlist row must be flagged.
33. Docs check: scripts/docs_check.py names rules `D-1` to `D-12`, `B-1a`, `B-2a`, `B-3a`, the options `--root` and `--only`, and `Legacy`; scripts/check.sh runs
   `docs_check.py" selftest` and `docs_check.py" --root` on this repository. Negative controls: each phrase removed from each file must be flagged.
34. Product name: live tracked files hold none of the retired spellings of SDLC Lite listed in NAME_BANNED, outside the NAME_ALLOW history paths
   (docs/reports, closed tickets, run workspaces under .sdlc, bench results). Negative control: a planted spelling must be flagged and an allowlisted path must not.
35. Gate lock: scripts/gate_lock.py names `SLOT-CAP`, `SDLC_GATE_WORKERS`, `SDLC_GATE_SLOTS`, `sdlc-gate-locks`, `SDLC_GATE_DIR`, and `SDLC_GATE_GRANT`; scripts/check.sh runs `gate_lock.py" selftest`;
   scripts/fanout.py names `gate_lock.py` and `--no-gate-lock`; agents/conductor.md names `gate_lock.py run`; and, where docs/references/sdlc-internals.md exists,
   it names `gate_lock.py`. Negative controls: each phrase removed from each file must be flagged.
36. Fleet retro: skills/fleet-retro/SKILL.md names `fleet_collect.py`, `fleet_detect.py`, `SendMessage`, `interview.md`, `rubric.md`, `AskUserQuestion`,
   `review-traces`, `Codex host`, `SDLC_HEADLESS`, and the stages `## 1. Collect` to `## 6. File`, and holds no `harness:` reference; skills/fleet-retro/rubric.md names
   gates `G1` to `G5`, criteria `C1` to `C5`, `7 of 10`, and `Outcome check`; skills/fleet-retro/fixtures.md names `F1`, `F2`, `F3`; skills/sdlc-lite/SKILL.md and
   agents/conductor.md route to `fleet-retro`; and, where docs/references/sdlc-internals.md exists, it names `fleet-retro`. Negative controls: each phrase removed
   from each file, a harness reference added, and a missing route must be flagged.
37. Fleet status: skills/fleet-status/SKILL.md names `fleet_status.py render`, `## 1. Render`, `## 2. Print it`, `## 3. Ask once`, `## 4. Relay, do not act`,
   `Render, never compose`, `AskUserQuestion`, `If AskUserQuestion is unavailable`, `--ping`, `sends nothing`, and `Codex host`, and holds no `harness:` reference;
   skills/sdlc-lite/SKILL.md routes to `fleet-status`; scripts/fleet_status.py names `RenderError`, `def render(`, `def schema_errors`, and `def selftest_render`;
   scripts/check.sh runs `fleet_status.py" selftest`; skills/fleet-status/SKILL.md links `resources/fleet-status.schema.json`, and that file exists, parses as
   JSON, declares draft 2020-12, and requires the `machine`, `repos`, `needs_you`, and `delta` keys. Negative controls: each phrase removed from each file, a
   harness reference added, the routing line removed, and a missing, unparsable, wrong-draft, or key-less schema file must be flagged.
38. Reorganization apply: scripts/reorg.py names `--dry-run`, `--approve`, `reorg.py: refused:`, and `final check failed`; scripts/check.sh runs
   `reorg.py" selftest`; docs/planning/repo-onboarding/reorganization-plan-procedure.md names `reorg.py` and `--approve`. Negative controls: each phrase removed
   from each file must be flagged.
39. Generated Claude definitions: `scripts/claude_roles.py generate --check` exits 0 (every levels.json row has its agents/<role>-L<n>.md or
   agents/solo-L<n>.md, byte for byte), and scripts/check.sh runs `claude_roles.py generate --check` and `claude_roles.py selftest`.
   Negative controls, on a temp copy: a hand-edited generated file, a levels.json effort changed without regenerating, and each
   check.sh phrase removed must be flagged.
40. Dispatch core: agents/conductor.md, skills/chain/SKILL.md, skills/fix/SKILL.md, skills/level-rubric/SKILL.md, and skills/handoff-format/SKILL.md
   each name `dispatch.py prepare`, `dispatch.py record`, and the `Agent` spawn with its `name`, `model`, and `run_in_background` parameters (the three
   launching texts, conductor, chain, and fix, also say the final message goes to `record` `on stdin`), and
   no line of them names `run.sh` without also naming Codex (run.sh is the Codex runner there; the Claude backend dispatches sub-agents).
   Negative controls: each phrase removed from each file, and a Claude-scoped `run.sh` line added to each file, must be flagged; a
   Codex-scoped `run.sh` line must not.
41. Record transcript flag (T-0334): no skills/*/SKILL.md spells a `dispatch.py record <dispatch_file> --` call with flags that omits `--transcript`.
   Negative control: a record call without it is flagged; one with it is not.
42. Self-contained skills (T-0325): in every skills/*/ folder of this plugin, and of the sibling progressive-context plugin when it sits next to this one, no
   markdown link in any .md file (fenced blocks aside) starts with `docs/`, `plugins/`, `../`, or `/`, or resolves outside its skill folder (URLs, `#anchors`, and
   links led by `${CLAUDE_PLUGIN_ROOT}/` pass); no SKILL.md or references/ file names a prose path starting with `plugins/`; and every
   `${CLAUDE_PLUGIN_ROOT}/<path>` a skill names exists in its plugin (a path with `<`, `*`, or `$` is a pattern and is skipped). Fixtures and rubrics quote evidence from
   other repos, so only their links are checked. Negative controls: a planted `../`, `../../`, `docs/`, `plugins/`, or absolute link, a `plugins/` prose path, and a
   dangling plugin-root path are each flagged; a link inside the folder, a URL, an anchor, and a plugin-root link are not.
43. One level system (T-0342): no skills/**/*.md, agents/*.md, commands/**/*.md, hooks/* file, adapters/codex/instructions.md,
   adapters/codex/agents/*.toml, or the alias owners scripts/tickets.py, scripts/solo_run.py, and scripts/claude_roles.py holds the
   retired S/M/L tier or size vocabulary (RETIRED_VOCAB: a tier, size, or level word before S, M, L, or XL, a solo-S|M|L agent
   name, the S|M|L, `S, M, L`, and S/M/L lists, and an `S $5, M $30` budget list); ticket levels and solo levels are L1 to L5. A line marked `ALIAS_OK` passes
   only in a file of ALIAS_FILES (the deprecated aliases kept for one release). Negative controls: a planted `tier S` line, a
   planted `solo-M` line, and an `ALIAS_OK` line outside ALIAS_FILES are each flagged; the same marked line in an alias file is not.
44. Generated-definition parity (T-0351): `codex_roles.py generate --check` and `claude_roles.py generate --check` pass inside check.py; negative control: a planted edit
   to a temp copy of agents/conductor.md without regenerating is flagged.
45. Red checkpoint (T-0378): `redck.py" record` appears in agents/builder.md; `redck.py` in scripts/run.sh and scripts/dispatch.py (the completion audit);
   `redck.py" deviations` in agents/verifier.md, agents/filer.md, and agents/builder.md, and `deviations <dir>` in scripts/redck.py (T-0543: the
   deviations live in red-checkpoint.jsonl audit rows; no process-deviations.md). Negative control: each phrase removed must be flagged.
46. Lean template (T-0385): agents/planner.md names `selected-test count`, `just to write the plan`, `validation scope`, `integration gate`, and `no record exists`;
   skills/handoff-format/SKILL.md names `validation scope`; agents/solo.md, scripts/fanout.py (both briefs) say `can affect` after a fix and never `rerun them all` or
   `rerun all checks`. Negative controls: each phrase removed, and a planted old phrase, must be flagged.
47. Version-free entry point (T-0401): no shipped skill, agent, command, hook, Codex adapter file, or the generated mailbox text in
   scripts/messages.py names a versioned plugin cache folder (`sdlc-lite/<digits>.<digits>`); the mailbox text runs the `{{launcher}}`
   (`messages-run.py`) and says `beat` never extends the window. Negative controls: a planted versioned path in each scanned kind of file, and each phrase removed.
   scripts/messages.py selftest runs the watch loop through a simulated version-folder rename.
48. Plan verification (T-0407): skills/plan-verification/SKILL.md names `references/outcome-block.md`, `Codex host`, and `Unattended` and holds no `harness:`
   reference; references/outcome-block.md names `Outcome`, `Measured by`, `Rubric`, `Negative control`, `outcome-block`, and `done-measured`; skills/plan/SKILL.md
   names `plan-verification`; skills/plan/references/goal.md names `outcome-block.md`; skills/sdlc-lite/SKILL.md routes to `plan-verification`.
   Item 31 stays for the plan skill and plan-loop. Negative controls: each phrase removed from each file, a harness reference added, and a routing line removed must be flagged.
49. Plan-doc parser and linter (T-0431): scripts/plan_doc.py exists and names `def parse`, `def table`, `def goal_line`, and `steps.STEP_RE`; scripts/plan_check.py names
   `GOOD_PLAN`, `def check_plan`, `plan_doc`, and every one of the 19 rule ids of docs/specs/sdlc-lite/plan-doc-executor.md section 3.3 (the list in `PLAN_RULES`) plus the
   warnings `l1-unverified`, `kpi-drift`, and `kpi-unresolved`; scripts/check.sh runs `plan_check.py" selftest` and `plan_doc.py" selftest`. Negative controls: each phrase and
   each rule id removed from its file must be flagged. The mutants themselves run in plan_check.py selftest (one case per rule, flagged as exactly that rule).
50. Plan-doc stop condition (T-0432): scripts/plan_done.py exists and names `plan done`, `plan defect:`, `ticket-absent`, `records ok; measures not read`,
   `replan cap reached: stopped`, `held_items`, `def assess`, `def selftest`, and `import dispatch, order, plan_check, plan_doc, results, steps, tickets`
   (it reuses the parser and the verifier family, order and held rules, and copies none); scripts/check.sh runs `plan_done.py" selftest`; docs/references/sdlc-internals.md has
   a `scripts/plan_done.py` section where that file exists. Negative controls: each phrase removed from each file must be flagged. The cases themselves run in plan_done.py selftest
   (one `plan_done: <row>` case per truth-table row and control of docs/specs/sdlc-lite/plan-doc-executor.md section 4.2).
51. Plan-doc skills (T-0433, retargeted in T-0468): skills/plan/SKILL.md names `## 1. Gather`, `plan_check.py plan`, `plan_done.py`, `Unattended`, and `Codex host`;
   skills/plan/references/plan-rules.md names `SDLC_ROLE`;
   skills/run-plan/SKILL.md names `Read`, `plan_check.py plan`, `plan_done.py`, `Unattended`, `Codex host`, and `SDLC_ROLE`; skills/plan/references/doc.md names `plan_check.py plan`
   and `Goal line`; references/run-rules.md names `plan_done.py`, `steps.py next`, `fanout.py prep`, `plan_done.py resume PD`, `recover --root . --open`, `fanout.py settle`, `status: ready`, and `Close a step only through `land``; neither skill references `harness:` or another plugin; skills/sdlc-lite/SKILL.md
   and agents/conductor.md route to `plan doc` and `run-plan`. Negative controls: each phrase removed from each file, a harness reference added, and a routing line removed must be flagged.
52. Level overlays (T-0441): every overlays/<role>.md stem has levels.json rows, and no .md file sits in a subdirectory of agents/ (an overlay placed in
   agents/overlays/ instead of the plugin's top-level overlays/). The overlay content rules run in claude_roles.py (generate exits 2; its selftest has the cases).
   Negative controls: a planted overlays/ghost.md stem and a planted agents/overlays/x.md path must each be flagged.
53. Prompt references (T-0447): scripts/prompt_lint.py reports no P-1 to P-3 error over agents/*.md, skills/*/SKILL.md, and overlays/*.md
   (a `rule N` cite names a numbered line of the role body, a script subcommand or `--flag` exists, a plugin path resolves), and scripts/check.sh
   runs `prompt_lint.py" selftest`. P-4 to P-6 are advisory and never fail here. Negative controls: an unresolved `rule 99` cite in an overlay,
   an unknown `--flag` on a real script, and a bare `scripts/coverage_check.py` in an agent file must each be flagged.
54. Report (T-0460): skills/report/SKILL.md names `report.py render`, `Render, never compose`, `Codex host`, `Exit 2 is a refusal`,
   `references/views.md`, and `references/record-schema.md`, and holds no `harness:` reference; scripts/report.py names `VERBS`, `CollectorError`,
   `session-status/1`, and `def selftest`; scripts/check.sh runs `report.py" selftest`; skills/sdlc-lite/SKILL.md routes to `report`.
   Negative controls: each phrase removed from each file, a harness reference added, and the routing row removed must each be flagged.
55. Solo dependents and verbatim criteria (T-0471): agents/solo.md carries the rule handles `Search-dependents` and `Run-verbatim`, names
   `git grep`, `plan defect: scope misses`, `plan defect: <criterion>`, and `results.py" solo-report`; scripts/results.py names `solo_report_error`
   and `criterion_spans`; the generated solo-L1, solo-L2, and solo-L3 carry both handles. Negative controls: each phrase removed from each file
   must be flagged, and a `verify: needed` report missing one criterion exit-code line must fail `solo_report_error`.
56. Merge ops (T-0492): agents/conductor.md, skills/fanout/SKILL.md, and skills/handoff-format/run-operations.md each name `fanout.py land <branch>`,
   `lanes.py sweep --apply`, `lanes.py list --stale`, `board.py --lanes`, and `--priority 1`, and carry the same settle command, the conductor's
   `fanout.py settle <integration> --forward`; the conductor and run-operations.md carry `Merge ops` and the conductor also `## Merge ops`. Negative
   controls: each phrase removed from each file, and the settle command changed in one file (the other two then disagree), must be flagged.
57. Plan kinds (T-0467): skills/plan/SKILL.md names each phrase of item 31 (`## 1. Gather`, `plan_check.py`, `AskUserQuestion`, `Why this plan`,
   `You must authorize`, `Unattended`, `Codex host`), the kind list `steps|doc|goal|campaign|fanout`, `Dry run (<kind>)`, `references/plan-rules.md`, and
   the reference file of each of the five kinds, and holds no `harness:` reference; references/plan-rules.md, references/steps.md, references/doc.md,
   references/goal.md, references/campaign.md, references/fanout.md, and evals/README.md exist in that folder; skills/sdlc-lite/SKILL.md routes to
   `plan <kind>`. Negative controls: each phrase removed, each kind reference removed, a harness reference added, the entry row removed, and each
   file reported missing must be flagged.
58. Plan redirect stubs (T-0468): each of skills/plan-goal, plan-campaign, plan-doc, and plan-fanout holds one SKILL.md of under 15 lines with the name of its folder, a
   description that starts `Redirect: run `/sdlc-lite:plan <kind>`` and ends `removed in the next minor.`, the path `${CLAUDE_PLUGIN_ROOT}/skills/plan/SKILL.md`, its kind token,
   and the Codex route path `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md`, no `## 1. Gather`, and no `references/` folder. Negative controls: a stub that regrows
   `## 1. Gather`, a stub without its kind token, a stub without the redirect description, a stub of 15 lines, a stub with a references folder, and a missing stub must be flagged.
   Ticket D deletes the stubs and this item.
59. Verifier parity line (T-0513): agents/verifier.md and its generated verifier-L1, L2 and L3 files each hold the `(parity)` rule line (`a `(parity)` criterion passes per named property`,
   `Read the real and the mockup image`). Negative control: each phrase removed from a file must be flagged.
60. Argument hints (T-0463): the standard is docs/specs/doc-standards/prompts.md `## Skill arguments and questions`. A skill reads arguments when its SKILL.md has a line
   that starts `Arguments: ` then the code span `$ARGUMENTS`. H-1: a reader has an `argument-hint` frontmatter line. H-2: the hint parses under the hint grammar. H-3: the
   hint is at most 100 characters (the text inside the YAML quotes). H-4: every `--flag` in the hint is in the skill text below the frontmatter and, for a skill in the
   script map (ticket, board, report, fleet-status, fanout, onboard, review-traces, fleet-retro), in that script's usage text. H-5: for a skill in the script map, every
   `--flag` in the script's usage text is in the hint, or in the first column of the skill's `## Arguments` table when the hint holds `[options]`, or in the allowlist.
   H-6: a reader has exactly one `## Arguments` heading whose next non-blank line is the row `| Argument | Meaning | Default | Example |`. H-7: a reference skill
   (checking-rules, checks-that-bite, handoff-format, level-rubric) has no `argument-hint`. The four plan redirect stubs of item 58 are exempt from H-2 to H-6. Usage text
   is a script's lines from the first `usage:` line to the next blank line; flags are prompt_lint.FLAG matches. Every rule runs on every skill it applies to. Negative
   controls, each a mutant that must add a finding for its rule: H-1 a reader without its hint line; H-2 braces, two dots, free text, a space inside angle brackets, an
   unbalanced bracket, and a double quote; H-3 a hint of 101 characters; H-4 a hint flag absent from the body, and a hint flag absent from the mapped script; H-5 a usage
   text with one extra flag; H-6 a reader without the heading, and one with two headings; H-7 a reference skill with a hint. Positive controls: the five must-parse
   hints, a clean reader, and a usage flag carried by the `## Arguments` table under `[options]` add no finding.
61. UI designer role (T-0520): agents/ui-designer.md names `mode: plan`, `mode: review`, `mode: generate`, `Inside out`, `Outside in`, and
   `only mode that edits`. The role is one role with a mode that holds the builder's write allowances, so `ui-designer` is in
   `claude_roles.WRITERS` and absent from the `SDLC_READONLY_ROLES` line of hooks/_role.sh; the two must agree, else one host layer
   lets the generate mode edit and the other denies it. No hook holds the rule that plan and review never edit: the role
   contract does, which is why the phrase is required here. Negative controls: each phrase removed, the role removed from
   WRITERS, the role added to the SDLC_READONLY_ROLES line, and a _role.sh with no such line must each be flagged.
"""
import os, re, sys, json, pathlib, subprocess, tempfile, shutil

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent.parent)
errors = []

def cap(m):
    """Alias -> "Sonnet"; pinned id claude-<family>-<major>-<minor> -> "Haiku 5.5"."""
    pin = re.fullmatch(r'claude-([a-z]+)-(\d+)-(\d+)', m)
    return f'{pin.group(1).capitalize()} {pin.group(2)}.{pin.group(3)}' if pin else m.capitalize()

# run.sh: "  builder:L1)  model=sonnet; effort=low ;;"
run = {}
for role, lvl, model, effort in re.findall(r'^\s*([\w-]+):(L\d)\)\s*model=([\w-]+);\s*effort=(\w+)', (root/'scripts/run.sh').read_text(), re.M):
    run[(role, lvl)] = f'{cap(model)} {effort}'
if not run: errors.append('run.sh: no role:level cases parsed')

# levels.json: {role: {level: [model, effort]}}; the L<n> rows of every role but solo are the pipeline roles, the solo row holds the solo levels L1 to L3.
levels, solo_levels = {}, {}
try:
    for role, by_level in json.loads((root/'adapters/claude/levels.json').read_text()).items():
        for lvl, (model, effort) in by_level.items():
            if role == 'solo': solo_levels[lvl] = [model, effort]
            else: levels[(role, lvl)] = f'{cap(model)} {effort}'
except (OSError, ValueError) as e:
    errors.append(f'adapters/claude/levels.json: cannot read: {e}')
if not levels: errors.append('adapters/claude/levels.json: no role:level rows parsed')

# level-rubric: per-role sections "## builder (...)" with rows "| L1 | Sonnet low | ...",
# plus the single-level table rows "| architect | L1 | Fable high |".
rubric = {}
role = None
for line in (root/'skills/level-rubric/SKILL.md').read_text().splitlines():
    h = re.match(r'^## ([\w-]+) \(L', line)
    if h: role = h.group(1); continue
    if line.startswith('## '): role = None
    m = re.match(r'^\| (L\d) \| (\w+(?: \d+\.\d+)? \w+) \|', line)
    if m and role: rubric[(role, m.group(1))] = m.group(2)
    m = re.match(r'^\| ([\w-]+) \| (L\d) \| (\w+(?: \d+\.\d+)? \w+) \|', line)
    if m: rubric[(m.group(1), m.group(2))] = m.group(3)

def table_diffs(levels, run, rubric):
    """Three-way agreement of the Claude level table. levels.json and run.sh also get their missing rows named by item 2."""
    out = []
    for la, a, lb, b, rows in (('levels.json', levels, 'run.sh', run, False), ('levels.json', levels, 'level-rubric', rubric, True),
                               ('run.sh', run, 'level-rubric', rubric, True)):
        for k in sorted(set(a) | set(b)):
            if k in a and k in b:
                if a[k] != b[k]: out.append(f'{lb}: {k[0]}:{k[1]} = {b[k]}, {la} = {a[k]}')
            elif rows and k not in b: out.append(f'{lb}: missing {k[0]}:{k[1]} ({la} has {a[k]})')
            elif rows: out.append(f'{lb}: has {k[0]}:{k[1]} = {b[k]}, {la} does not')
    return out
errors.extend(table_diffs(levels, run, rubric))
def change_effort(table):
    """A copy of the table with one effort changed, for a negative control."""
    k = sorted(table)[0]
    model, effort = table[k].rsplit(' ', 1)
    return {**table, k: f'{model} {"low" if effort == "xhigh" else "xhigh"}'}
for _label, _args in (('levels.json', (change_effort(levels), run, rubric)), ('run.sh', (levels, change_effort(run), rubric)),
                      ('level-rubric', (levels, run, change_effort(rubric)))):
    if not table_diffs(*_args): errors.append(f'check.py: level table negative control not flagged for a changed {_label} effort')
# Scout pin guard: run.sh scout row and rubric scout row agree, with a built-in negative control.
def scout_mismatch(run_text, rubric_text):
    m = re.search(r'^\s*scout:L1\)\s*model=([\w-]+);\s*effort=(\w+)', run_text, re.M)
    r = re.search(r'^\| scout \| L1 \| (\w+(?: \d+\.\d+)? \w+) \|', rubric_text, re.M)
    return not (m and r and f'{cap(m.group(1))} {m.group(2)}' == r.group(1))
_rs, _rb = (root/'scripts/run.sh').read_text(), (root/'skills/level-rubric/SKILL.md').read_text()
if scout_mismatch(_rs, _rb): errors.append('run.sh scout:L1 and level-rubric scout row disagree')
if cap('claude-haiku-5-5') != 'Haiku 5.5' or cap('sonnet') != 'Sonnet':
    errors.append('check.py: cap() pinned-id mapping broken')
if not scout_mismatch(re.sub(r'(scout:L1\)\s*model=)[\w-]+', r'\g<1>claude-haiku-9-9', _rs), _rb):
    errors.append('check.py: scout pin guard negative control not flagged')

# Role files (docstring item 2). The generated per-level definitions (agents/<role>-L<n>.md, agents/solo-<tier>.md) are not role files.
sys.path.insert(0, str(root/'scripts'))
import claude_roles
SESSION_AGENTS = {'conductor', 'messenger', 'solo'}  # all run as session agents (main session or its sub-agent), not through run.sh
try: GENERATED = claude_roles.generated_stems(root)
except claude_roles.TableError as e: GENERATED = set(); errors.append(f'claude_roles.py: {e}')
agents = {p.stem for p in (root/'agents').glob('*.md')} - SESSION_AGENTS - GENERATED
def role_table_diffs(agents, levels, run):
    roles, run_roles = {r for r, _ in levels}, {r for r, _ in run}
    return ([f'agents/{r}.md has no levels.json rows' for r in sorted(agents - roles)]
            + [f'levels.json role {r} has no agents/{r}.md' for r in sorted(roles - agents)]
            + [f'run.sh role {r} has no agents/{r}.md' for r in sorted(run_roles - agents)]
            + [f'levels.json row {r}:{l} has no run.sh case' for r, l in sorted(set(levels) - set(run))]
            + [f'run.sh case {r}:{l} has no levels.json row' for r, l in sorted(set(run) - set(levels))])
errors.extend(role_table_diffs(agents, levels, run))
_some = sorted(levels)[0] if levels else ('builder', 'L1')
for _label, _args in (('an agent file with no levels.json rows', (agents | {'ghost'}, levels, run)),
                      ('a levels.json role with no agent file', (agents - {_some[0]}, levels, run)),
                      ('a levels.json row with no run.sh case', (agents, levels, {k: v for k, v in run.items() if k != _some})),
                      ('a run.sh case with no levels.json row', (agents, {k: v for k, v in levels.items() if k != _some}, run))):
    if not role_table_diffs(*_args): errors.append(f'check.py: role file negative control not flagged for {_label}')

for p in sorted((root/'agents').glob('*.md')):
    fm = p.read_text().split('---')[1] if p.read_text().startswith('---') else ''
    for sk in re.findall(r'^  - (\S+)$', fm.split('skills:', 1)[1], re.M) if 'skills:' in fm else []:
        if not (root/'skills'/sk/'SKILL.md').exists():
            errors.append(f'agents/{p.name} declares missing skill: {sk}')

# Agent declarations parse as YAML (T-0503): a description with a colon-space or text after its closing quote is a silent frontmatter error.
try: import yaml
except ImportError: yaml = None; errors.append('agents/*.md: PyYAML is required to validate agent frontmatter (pip install pyyaml)')
def agent_yaml_problems(name, text):
    m = re.fullmatch(r'---\n(.*?)\n---\n.*', text, re.S)
    if not m: return [f'agents/{name}: no frontmatter block']
    try: data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e: return [f'agents/{name}: frontmatter is not valid YAML: {" ".join(str(e).split())}']
    if not isinstance(data, dict): return [f'agents/{name}: frontmatter is not a mapping']
    return [f'agents/{name}: frontmatter field {k} is missing or not text' for k in ('name', 'description') if not isinstance(data.get(k), str) or not data[k].strip()]
if yaml:
    for p in sorted((root/'agents').glob('*.md')): errors.extend(agent_yaml_problems(p.name, p.read_text()))
    _good = '---\nname: x\ndescription: "A role: with a colon. Level L1: sonnet low."\n---\nbody\n'
    _bad = '---\nname: x\ndescription: "A role." Level L1: sonnet low.\n---\nbody\n'  # the T-0503 defect: text after the closing quote
    _colon = '---\nname: x\ndescription: A role: with an unquoted colon.\n---\nbody\n'
    if agent_yaml_problems('good.md', _good): errors.append('check.py: agent YAML check rejects a valid quoted description')
    for _why, _t in (('text after a closing quote', _bad), ('an unquoted colon-space', _colon)):
        if not agent_yaml_problems('bad.md', _t): errors.append(f'check.py: agent YAML negative control not flagged for {_why}')

# Long role runs: interactive sessions background them; headless sessions keep them in the foreground.
for rel in ('skills/chain/SKILL.md', 'skills/bench/SKILL.md', 'skills/fanout/SKILL.md', 'agents/conductor.md',
            'skills/fix/SKILL.md'):
    f = root/rel
    if not f.is_file(): errors.append(f'{rel}: missing (long-run doc check)'); continue
    text = f.read_text()
    missing = [w for w in ('interactive', 'run_in_background', 'notification', 'sleep', 'SDLC_HEADLESS') if w not in text]
    if missing: errors.append(f'{rel}: long-run rule missing words: {", ".join(missing)}')
    if 'never `run_in_background`' in text or 'never run_in_background' in text:
        errors.append(f'{rel}: still says "never run_in_background" unqualified')
# Plan-defect route: a `plan defect` tag from the split lint, the builder, or the verifier goes to a replan.
PLAN_DEFECT_DOCS = {
    'plan defect': ('agents/planner.md', 'agents/builder.md', 'agents/verifier.md', 'agents/conductor.md',
                    'skills/chain/SKILL.md', 'skills/level-rubric/SKILL.md', 'skills/handoff-format/SKILL.md',
                    'scripts/steps.py'),
    'Plan review': ('agents/planner.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md'),
    'no new findings': ('agents/planner.md',),
    'clean porcelain status': ('agents/planner.md', 'scripts/steps.py'),
    'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py'),
    'nonzero `exit`': ('agents/planner.md', 'scripts/steps.py'),
    'red guard': ('skills/chain/SKILL.md', 'scripts/steps.py'),
    'changed the work tree': ('agents/planner.md', 'skills/chain/SKILL.md', 'scripts/steps.py'),
    'recurring finding': ('agents/planner.md', 'agents/conductor.md', 'skills/chain/SKILL.md',
                          'skills/level-rubric/SKILL.md', 'skills/handoff-format/SKILL.md'),
    'sha fixed at plan time': ('agents/planner.md', 'scripts/steps.py'),
    'owns that budget': ('agents/planner.md',),
    'contract dependents': ('agents/planner.md', 'agents/verifier.md'),
    'steps.py widen': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md',
                       'skills/level-rubric/SKILL.md', 'scripts/steps.py'),
    'gates green': ('agents/planner.md',),
    'one Bash call': ('agents/planner.md',),
    'can go red': ('agents/planner.md',),
    'SDLC_BASE_SHA': ('agents/planner.md', 'agents/builder.md', 'agents/verifier.md', 'scripts/run.sh',
                      'scripts/steps.py'),
    'membership or structure': ('agents/planner.md',),
    'swap old:': ('agents/verifier.md', 'scripts/steps.py'),
    'swap new:': ('agents/verifier.md', 'scripts/steps.py'),
    'steps.py swap': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md',
                      'skills/level-rubric/SKILL.md', 'scripts/steps.py'),
    'amend old:': ('agents/builder.md', 'scripts/steps.py'),
    'amend new:': ('agents/builder.md', 'scripts/steps.py'),
    'steps.py amend': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md',
                       'skills/level-rubric/SKILL.md', 'scripts/steps.py'),
    # Plan-review route (docstring item 11): a plan the rubric names is reviewed before any split.
    'plan-reviewer': ('scripts/run.sh', 'skills/level-rubric/SKILL.md', 'skills/chain/SKILL.md', 'agents/conductor.md',
                      'skills/plan/SKILL.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py'),
    'steps.py review': ('skills/chain/SKILL.md', 'agents/conductor.md', 'skills/plan/SKILL.md',
                        'skills/level-rubric/SKILL.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py'),
    '## Assumptions': ('agents/planner.md', 'agents/plan-reviewer.md', 'scripts/steps.py'),
    'unresolved:': ('agents/planner.md', 'agents/plan-reviewer.md', 'scripts/steps.py'),
    'Missing decisions': ('agents/plan-reviewer.md', 'skills/chain/SKILL.md', 'agents/conductor.md'),
    'plan review:': ('agents/planner.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md',
                     'agents/conductor.md'),
}
for word, rels in PLAN_DEFECT_DOCS.items():
    for rel in rels:
        f = root/rel
        if not f.is_file(): errors.append(f'{rel}: missing (plan-defect route check)'); continue
        if word not in f.read_text(): errors.append(f'{rel}: plan-defect route missing "{word}"')
# Inherited-red route: a builder Status `inherited red: <tests>` is routed, rendered, and accepted, never a fail.
INHERITED_RED_DOCS = ('agents/builder.md', 'agents/verifier.md', 'agents/conductor.md', 'skills/chain/SKILL.md',
                      'scripts/fanout.py', 'skills/fanout/SKILL.md',
                      'scripts/steps.py', 'scripts/board.py', 'scripts/run.sh')
for rel in INHERITED_RED_DOCS:
    f = root/rel
    if not f.is_file() or 'inherited red' not in f.read_text(): errors.append(f'{rel}: inherited-red route missing "inherited red"')
# Finish-in-session: follow-ups are tagged fix-now, decide, or note; only one decide item becomes a ticket.
FINISH_FILES = ('agents/filer.md', 'scripts/tickets.py', 'skills/file/SKILL.md', 'skills/ticket/SKILL.md')
CHAIN, CONDUCTOR, HANDOFF_FMT = 'skills/chain/SKILL.md', 'agents/conductor.md', 'skills/handoff-format/SKILL.md'
FINISH_DOCS = {'fix-now:': FINISH_FILES + (CHAIN, CONDUCTOR),
               'decide:': FINISH_FILES + (CHAIN, CONDUCTOR, 'skills/open-questions/SKILL.md'),
               'notes.md': FINISH_FILES + (HANDOFF_FMT, CONDUCTOR),
               'Loose ends': (CHAIN, 'agents/filer.md', HANDOFF_FMT, 'skills/level-rubric/SKILL.md', CONDUCTOR),
               'sdlc-lite:fix': (CONDUCTOR,),
               'fast lane': ('skills/fix/SKILL.md', CONDUCTOR, 'skills/level-rubric/SKILL.md')}
def finish_missing(text, word): return not re.search(re.escape(word) + r'(?![\w-])', text)
for word, rels in FINISH_DOCS.items():
    for rel in rels:
        f = root/rel
        if not f.is_file(): errors.append(f'{rel}: missing (finish-in-session check)'); continue
        text = f.read_text()
        if finish_missing(text, word): errors.append(f'{rel}: finish-in-session wording missing "{word}"')
        elif not finish_missing(text.replace(word, ''), word):
            errors.append(f'{rel}: finish-in-session negative control not flagged for "{word}"')
# Merge-step template: one block, kept identical in the planner and handoff-format, that lints clean.
def merge_block(rel):
    f = root/rel
    if not f.is_file(): return None
    out, inside = [], False
    for line in f.read_text().splitlines():
        if not inside and line == '```merge-step': inside = True; continue
        if inside and line == '```': return '\n'.join(out)
        if inside: out.append(line)
    return None
blocks = {rel: merge_block(rel) for rel in ('agents/planner.md', 'skills/handoff-format/SKILL.md')}
for rel, b in blocks.items():
    if not b or not b.strip(): errors.append(f'{rel}: merge-step block missing or empty')
pb, hb = blocks['agents/planner.md'], blocks['skills/handoff-format/SKILL.md']
if pb and hb and pb != hb: errors.append('merge-step block differs between agents/planner.md and skills/handoff-format/SKILL.md')
if pb and pb.strip():
    tmp = tempfile.mkdtemp()
    try:
        plan = pathlib.Path(tmp)/'planner-L2.md'
        plan.write_text(pb.replace('<n>', '1') + '\n')
        r = subprocess.run(['python3', str(root/'scripts/steps.py'), 'lint', str(plan)], capture_output=True, text=True)
        if r.returncode != 0: errors.append(f'merge-step block fails steps.py lint: {r.stderr.strip()}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
# Behavior probe: the conflict-marker guard fails only on markers the merge commit introduced.
# Seven cases: it passes an empty merge, fails on a marker the merge commit added (file name
# with a space), passes a lane line starting with >>>>>>> that merged cleanly, fails on kept git
# conflict markers, passes a lane line starting with >>>>>>> when both sides changed the file,
# passes an aligned kept marker, and passes a clean merge. The aligned-marker case pins a known
# miss: a kept marker textually identical to a parent line that aligns with it shows as `+ ` or
# ` +` in `git diff-tree --cc`, not `++`.
if pb and pb.strip():
    guard = next((l for l in pb.splitlines() if l.startswith('- (guard) ') and '<<<<<<<' in l), None)
    if guard is None or guard.count('`') < 2:
        errors.append('merge-step conflict-marker guard: criterion line missing')
    else:
        span = guard[guard.index('`') + 1:guard.rindex('`')]
        tmp = tempfile.mkdtemp()
        try:
            def g(*a):
                return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp,
                                      capture_output=True, text=True, check=True).stdout.strip()
            def span_rc():
                return subprocess.run(['bash', '-c', span], cwd=tmp, capture_output=True, text=True).returncode
            g('init', '-q', '-b', 'main')
            pathlib.Path(tmp, 'untouched.txt').write_text('<<<<<<< legit fixture\n')
            pathlib.Path(tmp, 'sp ace.txt').write_text('a\n')
            g('add', '-A'); g('commit', '-qm', 'base')
            g('checkout', '-qb', 'empty'); g('commit', '-q', '--allow-empty', '-m', 'empty')
            g('checkout', '-q', 'main'); g('merge', '-q', '--no-ff', '-m', 'merge empty', 'empty')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: empty merge flagged')
            pre = g('rev-parse', 'HEAD^1')
            def gr(*a):
                return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp,
                                      capture_output=True, text=True)
            def app(s):
                with open(pathlib.Path(tmp, 'sp ace.txt'), 'a') as fh: fh.write(s)
            g('checkout', '-qb', 'marker', pre)
            pathlib.Path(tmp, 'm.txt').write_text('m\n')
            g('add', '-A'); g('commit', '-qm', 'marker lane')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            g('merge', '-q', '--no-ff', '--no-commit', 'marker')
            app('>>>>>>> evil\n'); g('add', '-A'); g('commit', '-qm', 'merge marker')
            if span_rc() == 0: errors.append('merge-step conflict-marker guard: marker in touched file not flagged')
            g('reset', '-q', '--hard', pre)
            g('checkout', '-qb', 'legit', pre)
            app('>>>>>>> lane\n'); g('commit', '-qam', 'legit')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            g('merge', '-q', '--no-ff', '-m', 'merge legit', 'legit')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: legit lane line flagged')
            g('reset', '-q', '--hard', pre)
            g('checkout', '-qb', 'conflict', pre)
            pathlib.Path(tmp, 'sp ace.txt').write_text('lane\n'); g('commit', '-qam', 'lane side')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            pathlib.Path(tmp, 'sp ace.txt').write_text('main\n'); g('commit', '-qam', 'main side')
            gr('merge', '-q', '--no-ff', 'conflict')
            g('add', '-A'); g('commit', '-qm', 'merge conflict kept')
            if span_rc() == 0: errors.append('merge-step conflict-marker guard: kept conflict markers not flagged')
            g('reset', '-q', '--hard', pre)
            sp = pathlib.Path(tmp, 'sp ace.txt')
            g('checkout', '-qb', 'both', pre)
            sp.write_text('a\n>>>>>>> lane\n'); g('commit', '-qam', 'both lane')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            sp.write_text('top\na\n'); g('commit', '-qam', 'both main')
            g('merge', '-q', '--no-ff', '-m', 'merge both', 'both')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: both-sides legit lane line flagged')
            g('reset', '-q', '--hard', pre)
            sp.write_text('a\n>>>>>>> aligned\n'); g('commit', '-qam', 'aligned base')
            b2 = g('rev-parse', 'HEAD')
            g('checkout', '-qb', 'aligned', b2)
            sp.write_text('lane\n>>>>>>> aligned\n'); g('commit', '-qam', 'aligned lane')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', b2)
            sp.write_text('main\n>>>>>>> aligned\n'); g('commit', '-qam', 'aligned main')
            gr('merge', '-q', '--no-ff', 'aligned')
            sp.write_text(''.join(l for l in sp.read_text().splitlines(True) if not l.startswith(('<<<<<<<', '======='))))
            g('add', '-A'); g('commit', '-qm', 'merge aligned kept')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: aligned kept marker flagged; the documented limitation changed, update the merge-step docs')
            g('reset', '-q', '--hard', pre)
            g('checkout', '-qb', 'clean')
            pathlib.Path(tmp, 'ok file.txt').write_text('ok\n')
            g('add', '-A'); g('commit', '-qm', 'clean')
            g('checkout', '-q', 'main'); g('merge', '-q', '--no-ff', '-m', 'merge clean', 'clean')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: clean merge flagged')
        except subprocess.CalledProcessError as e:
            errors.append(f'merge-step conflict-marker guard: probe setup failed: {e.stderr.strip()}')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
b = root/'agents/builder.md'
if not b.is_file() or 'git merge --no-ff' not in b.read_text(): errors.append('agents/builder.md: missing "git merge --no-ff"')
f = root/'skills/file/SKILL.md'
ft = f.read_text() if f.is_file() else ''
for w in ('likely duplicate', 'open T-NNNN'):
    if w not in ft: errors.append(f'skills/file/SKILL.md: missing "{w}"')
# AskUserQuestion allows at most 4 options per question; the publish question must fit.
if 'at most 4 options' not in ft: errors.append('skills/file/SKILL.md: publish question missing "at most 4 options"')
# Step 3.3 follow-ups must batch within AskUserQuestion's 4-option limit.
def step33_bad(text):
    l33 = next((l for l in text.splitlines() if l.startswith('   3. When a person is present')), '')
    return 'at most 4 options per question' not in l33
if step33_bad(ft): errors.append('skills/file/SKILL.md: step 3.3 missing "at most 4 options per question"')
if not step33_bad(ft.replace('at most 4 options per question', '')): errors.append('check.py: step 3.3 guard negative control not flagged')
# Builder scope rules: formatters only on the files this step changed; kill only the PIDs you started.
SCOPE_PHRASES = ('files this step changed', 'PIDs you started')
def builder_scope_missing(text): return [s for s in SCOPE_PHRASES if s not in text]
bf = root/'agents/builder.md'
bt = bf.read_text() if bf.is_file() else ''
for s in builder_scope_missing(bt): errors.append(f'agents/builder.md: builder scope rule missing "{s}"')
for s in SCOPE_PHRASES:
    if s not in builder_scope_missing(bt.replace(s, '')): errors.append('check.py: builder scope guard negative control not flagged')
# Builder and verifier keep gates in the foreground: a headless run ends with the turn.
FG_PHRASE = 'never end the turn while background work runs'
for rel in ('agents/builder.md', 'agents/verifier.md'):
    fp = root/rel
    if not fp.is_file() or FG_PHRASE not in fp.read_text(): errors.append(f'{rel}: foreground rule missing "{FG_PHRASE}"')
step4 = next((l for l in ft.splitlines() if l.startswith('4. ')), '')
m = re.search(r'\(([^)]*)\)', step4)
if (m and 'issue' in m.group(1).lower()) or 'optional item' in step4: errors.append('skills/file/SKILL.md: step 4 lists GitHub issues among the publish options')
# /fix lints its handwritten step handoff, not the task folder (a folder lint needs a planner file /fix never writes).
def fix_lint_bad(text):
    targets = re.findall(r'steps\.py lint (\S+?)`', text)
    return not targets or any(not t.endswith('/step-1/handoff.md') for t in targets)
fx = root/'skills/fix/SKILL.md'
fxt = fx.read_text() if fx.is_file() else ''
if fix_lint_bad(fxt): errors.append('skills/fix/SKILL.md: steps.py lint target is not <ticket dir>/<slug>/step-1/handoff.md (.sdlc/<slug>/..., or .sdlc/tickets/<slug>/... with ticket_root: tickets)')
if not fix_lint_bad(fxt.replace('/step-1/handoff.md`', '`')): errors.append('check.py: /fix lint-target guard negative control not flagged')
# /fix step 5 stops at publish when unattended: no push, no pull request.
def fix_unattended_bad(text):
    m = re.search(r'^5\. .*$', text, re.M)
    return not m or 'Unattended' not in m.group(0) or 'never push' not in m.group(0)
if fix_unattended_bad(fxt): errors.append('skills/fix/SKILL.md: step 5 lacks the Unattended rule with "never push"')
if not fix_unattended_bad(fxt.replace('never push', 'push')): errors.append('check.py: /fix unattended-publish guard negative control not flagged')
# The conductor forbids substituting other plugins' agents for run.sh roles.
SUBST_PHRASE = "Other plugins' agents are not substitutes"
def subst_missing(text): return SUBST_PHRASE not in text
ct = (root/CONDUCTOR).read_text() if (root/CONDUCTOR).is_file() else ''
if subst_missing(ct): errors.append(f'{CONDUCTOR}: run.sh-only rule missing "{SUBST_PHRASE}"')
if not subst_missing(ct.replace(SUBST_PHRASE, '')): errors.append('check.py: substitute-agent guard negative control not flagged')
# Plan-reviewer role: run.sh holds its L1 row and validates every result through results.py, whose schema gives
# plan-reviewer the key section Verdict with the allowed values pass, replan, blocked.
sys.path.insert(0, str(root/'scripts'))
import results
PR_VALIDATE = 'results.py" validate'
def plan_reviewer_missing(runs, text, schema):
    out = []
    if ('plan-reviewer', 'L1') not in runs: out.append('no plan-reviewer:L1 row')
    spec = schema.get('plan-reviewer', {})
    if spec.get('key') != 'Verdict' or [a[0] for a in spec.get('allowed', ())] != ['pass', 'replan', 'blocked']:
        out.append('results.py SCHEMA plan-reviewer is not key Verdict with allowed pass, replan, blocked')
    if PR_VALIDATE not in text: out.append(f'no result check "{PR_VALIDATE}"')
    return out
rt = (root/'scripts/run.sh').read_text()
for e in plan_reviewer_missing(run, rt, results.SCHEMA): errors.append(f'scripts/run.sh: plan-reviewer role: {e}')
bad_schema = dict(results.SCHEMA)
bad_schema['plan-reviewer'] = dict(bad_schema['plan-reviewer'], allowed=(('pass', r'pass', 'pass'), ('fail', r'fail', 'fail')))
no_pr_row = {k: v for k, v in run.items() if k[0] != 'plan-reviewer'}
for name, args, want in (('L1 row', (no_pr_row, rt, results.SCHEMA), 'no plan-reviewer:L1 row'),
                         ('schema', (run, rt, bad_schema), 'results.py SCHEMA'),
                         ('validate call', (run, rt.replace(PR_VALIDATE, 'results.py" schema'), results.SCHEMA),
                          'no result check')):
    if not any(e.startswith(want) for e in plan_reviewer_missing(*args)):
        errors.append(f'check.py: plan-reviewer run.sh guard negative control ({name}) not flagged')
# Read-first route: every role and doc that carries step entry files names `Read first`.
READ_FIRST = 'Read first'
READ_FIRST_FILES = ('agents/planner.md', 'agents/builder.md', 'agents/verifier.md', 'skills/fix/SKILL.md',
                    'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py')
def read_first_missing(text): return READ_FIRST not in text
for rel in READ_FIRST_FILES:
    f = root/rel
    text = f.read_text() if f.is_file() else ''
    if read_first_missing(text): errors.append(f'{rel}: read-first route missing "{READ_FIRST}"')
    elif not read_first_missing(text.replace(READ_FIRST, '')):
        errors.append(f'{rel}: read-first negative control not flagged')
# Lean lane text (docstring item 14): the lean chain section and the coarse-step rule name their phrases.
LEAN_LANE = {'## Lean chain': ('skills/chain/SKILL.md',),
             'writes the Outcome': ('skills/chain/SKILL.md',),
             'independently verifiable outcome': ('agents/planner.md',),
             'steps lint: warning:': ('agents/planner.md', 'scripts/steps.py')}
def lean_missing(text, phrase): return phrase not in text
for phrase, rels in LEAN_LANE.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if lean_missing(text, phrase): errors.append(f'{rel}: lean lane text missing "{phrase}"')
        elif not lean_missing(text.replace(phrase, ''), phrase):
            errors.append(f'{rel}: lean-lane negative control not flagged')
# Spec gate text (docstring item 16): the guard timeout line and the run.sh gate are named where they route.
SPEC_GATE = {'guard timeout:': ('agents/planner.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py', 'scripts/specgate.py'),
             'specgate.py check': ('scripts/run.sh', 'skills/chain/SKILL.md', 'agents/conductor.md'),
             'specgate.py red': ('agents/solo.md', 'agents/planner.md', 'scripts/steps.py')}
def spec_gate_missing(text, phrase): return phrase not in text
for phrase, rels in SPEC_GATE.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if spec_gate_missing(text, phrase): errors.append(f'{rel}: spec gate text missing "{phrase}"')
        elif not spec_gate_missing(text.replace(phrase, ''), phrase):
            errors.append(f'check.py: spec gate text negative control not flagged for {rel}')
SPEC_GATE_EXEC = 'exec python3 "$plugin_root/scripts/run_lifecycle.py"'
def spec_gate_order_bad(lines):
    gate = next((i for i, l in enumerate(lines) if 'specgate.py check' in l), None)
    run = next((i for i, l in enumerate(lines) if SPEC_GATE_EXEC in l), None)
    return gate is None or run is None or gate > run
rs_lines = (root/'scripts/run.sh').read_text().split('\n') if (root/'scripts/run.sh').is_file() else []
if spec_gate_order_bad(rs_lines):
    errors.append('scripts/run.sh: specgate.py check does not come before exec run_lifecycle.py')
else:
    gi = next(i for i, l in enumerate(rs_lines) if 'specgate.py check' in l)
    ri = next(i for i, l in enumerate(rs_lines) if SPEC_GATE_EXEC in l)
    swapped = list(rs_lines); swapped[gi], swapped[ri] = swapped[ri], swapped[gi]
    if not spec_gate_order_bad(swapped): errors.append('check.py: spec gate order negative control not flagged')
# Red checkpoint (docstring item 45): the builder records before editing, completion audits, the verifier and filer read the deviations.
RED_CHECKPOINT = {'redck.py" record': ('agents/builder.md',),
                  'redck.py': ('scripts/run.sh', 'scripts/dispatch.py'),
                  'redck.py" deviations': ('agents/verifier.md', 'agents/filer.md', 'agents/builder.md'),
                  'deviations <dir>': ('scripts/redck.py',)}
def red_checkpoint_missing(text, phrase): return phrase not in text
for phrase, rels in RED_CHECKPOINT.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if red_checkpoint_missing(text, phrase): errors.append(f'{rel}: red checkpoint text missing "{phrase}"')
        elif not red_checkpoint_missing(text.replace(phrase, ''), phrase):
            errors.append(f'check.py: red checkpoint text negative control not flagged for {rel}')
# Lean template (docstring item 46): validation scope, the integration-gate exception, and affected-input reruns.
LEAN_TEMPLATE = {'selected-test count': ('agents/planner.md',), 'just to write the plan': ('agents/planner.md',),
                 'validation scope': ('agents/planner.md', 'skills/handoff-format/SKILL.md'),
                 'integration gate': ('agents/planner.md',), 'no record exists': ('agents/planner.md',)}
RERUN_ALL = ('rerun them all', 'rerun all checks')
def lean_template_bad(rel, text):
    out = [f'{rel}: lean template text missing "{w}"' for w, rels in LEAN_TEMPLATE.items() if rel in rels and w not in text]
    if rel in ('agents/solo.md', 'scripts/fanout.py'):
        need = 2 if rel == 'scripts/fanout.py' else 1
        if len(re.findall(r'rerun the checks (?:the fix|that fix) can affect', text)) < need: out.append(f'{rel}: affected-input rerun wording missing ({need} expected)')
        out += [f'{rel}: still says "{w}"' for w in RERUN_ALL if w in text]
    return out
for rel in sorted({r for rels in LEAN_TEMPLATE.values() for r in rels} | {'agents/solo.md', 'scripts/fanout.py'}):
    f = root/rel
    text = f.read_text() if f.is_file() else ''
    errors.extend(lean_template_bad(rel, text))
    if not lean_template_bad(rel, text):
        mutants = [text.replace(w, '') for w, rels in LEAN_TEMPLATE.items() if rel in rels]
        if rel in ('agents/solo.md', 'scripts/fanout.py'):
            mutants += [text.replace('can affect', 'can touch'), text + '\nrerun them all\n', text + '\nrerun all checks\n']
        if any(not lean_template_bad(rel, m) for m in mutants): errors.append(f'check.py: lean template negative control not flagged for {rel}')
# Carry forward (docstring item 17): producer contracts end with the section; planner and builder read it first.
CF_PRODUCERS = ('agents/scout.md', 'agents/researcher.md', 'agents/architect.md', 'agents/archaeologist.md', 'agents/ui-designer.md')
CARRY_FORWARD = {'## Carry forward': CF_PRODUCERS + ('agents/planner.md', 'agents/builder.md'),
                 'at most 15 lines': CF_PRODUCERS,
                 'search only what it does not answer': ('agents/planner.md', 'agents/builder.md'),
                 'cite the result path': ('agents/planner.md',)}
def carry_forward_missing(text, phrase): return phrase not in text
for phrase, rels in CARRY_FORWARD.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if carry_forward_missing(text, phrase): errors.append(f'{rel}: carry-forward text missing "{phrase}"')
        elif not carry_forward_missing(text.replace(phrase, ''), phrase):
            errors.append(f'{rel}: carry-forward negative control not flagged')
# UI designer role (docstring item 61, T-0520): the role file names its modes, passes, and edit rule; both write layers agree it writes.
UI_DESIGNER_PHRASES = ('mode: plan', 'mode: review', 'mode: generate', 'Inside out', 'Outside in', 'only mode that edits')
def ui_designer_bad(agent, writers, role_sh):
    bad = [f'agents/ui-designer.md missing "{p}"' for p in UI_DESIGNER_PHRASES if p not in agent]
    if 'ui-designer' not in writers: bad.append('ui-designer is not in claude_roles.WRITERS')
    ro = [l for l in role_sh.splitlines() if l.startswith('SDLC_READONLY_ROLES=')]
    if len(ro) != 1: bad.append('hooks/_role.sh does not hold exactly one SDLC_READONLY_ROLES line')
    elif ' ui-designer ' in ro[0]: bad.append('hooks/_role.sh SDLC_READONLY_ROLES lists ui-designer, which claude_roles.WRITERS lets write')
    return bad
_uf, _uh = root/'agents/ui-designer.md', root/'hooks/_role.sh'
_ua, _ur = (_uf.read_text() if _uf.is_file() else ''), (_uh.read_text() if _uh.is_file() else '')
errors.extend(f'check.py: ui-designer role: {m}' for m in ui_designer_bad(_ua, claude_roles.WRITERS, _ur))
if not ui_designer_bad(_ua, claude_roles.WRITERS, _ur):
    for _ph in UI_DESIGNER_PHRASES:
        if not ui_designer_bad(_ua.replace(_ph, ''), claude_roles.WRITERS, _ur): errors.append(f'check.py: ui-designer role negative control not flagged for "{_ph}"')
    if not ui_designer_bad(_ua, tuple(w for w in claude_roles.WRITERS if w != 'ui-designer'), _ur): errors.append('check.py: ui-designer role negative control not flagged for a role missing from WRITERS')
    if not ui_designer_bad(_ua, claude_roles.WRITERS, _ur.replace('SDLC_READONLY_ROLES=" ', 'SDLC_READONLY_ROLES=" ui-designer ', 1)): errors.append('check.py: ui-designer role negative control not flagged for a read-only ui-designer')
    if not ui_designer_bad(_ua, claude_roles.WRITERS, _ur.replace('SDLC_READONLY_ROLES=', 'SDLC_RO=')): errors.append('check.py: ui-designer role negative control not flagged for a missing SDLC_READONLY_ROLES line')
# Ticket budget (docstring item 22): filing sets it, run.sh gates on it (exit 4), board.py renders it.
TICKET_BUDGET = {'budget.py set': ('skills/ticket/SKILL.md',),
                 'budget.py': ('scripts/run.sh', 'scripts/board.py'),
                 '4 ticket budget': ('scripts/run.sh',)}
def ticket_budget_missing(text, phrase): return phrase not in text
for phrase, rels in TICKET_BUDGET.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if ticket_budget_missing(text, phrase): errors.append(f'{rel}: ticket-budget text missing "{phrase}"')
        elif not ticket_budget_missing(text.replace(phrase, ''), phrase):
            errors.append(f'{rel}: ticket-budget negative control not flagged')
# Messenger agent (docstring item 12): a session sub-agent with a Claude file, a Codex mapping, and a generated TOML.
MESSENGER_WORDS = ('model: sonnet', 'effort: low', 'messages.py', '.sdlc/messages/AGENTS.md',
                   'SendMessage', 'Parent: <address>', 'messenger up', 'same turn', 'yielding;', 'inbox-<repo>-<receiver>',
                   'use `find`', 'Monitor', 'handled: unknown',  # T-0369: delivery, startup ping, loop, yield, spawn name, host pitfalls, report format
                   'messages.py activate', 'messages.py beat', 'messages.py release', 'scripts/supervisor.py',
                   'only active-turn delivery is available', 'never counts as new authorization',
                   'never evidence that an idle parent received a message', 'Any completion event ends you')  # T-0380: lifecycle
MAILBOX_WORDS = ('## Activate a worker', 'only active-turn delivery is available', 'idle-host watcher `supervisor.py`',
                 '--authorized-by', 'never widens that scope', 'is not evidence that an idle parent received anything',
                 'one re-arm per stall', 'exits 3 unless it is listening', 'Retry and recovery are bounded',
                 'the exchange cannot loop', 'python3 "{{launcher}}" watch', 'it never extends the window')  # T-0380, T-0401
def mailbox_missing(script_text): return [f'mailbox: scripts/messages.py entry text missing "{w}"' for w in MAILBOX_WORDS if w not in script_text]
def messenger_missing(agent_text, codex_models, toml_present):
    out = []
    if not agent_text.strip(): out.append('messenger: agents/messenger.md missing or empty')
    else: out += [f'messenger: agents/messenger.md missing "{w}"' for w in MESSENGER_WORDS if w not in agent_text]
    if 'messenger' not in codex_models: out.append('messenger: adapters/codex/models.json has no messenger entry')
    if not toml_present: out.append('messenger: adapters/codex/agents/sdlc-messenger-l1.toml missing')
    return out
mf, mj = root/'agents/messenger.md', root/'adapters/codex/models.json'
mt = mf.read_text() if mf.is_file() else ''
mc = json.loads(mj.read_text()) if mj.is_file() else {}
mtoml = (root/'adapters/codex/agents/sdlc-messenger-l1.toml').is_file()
errors.extend(messenger_missing(mt, mc, mtoml))
if (not messenger_missing('', mc, mtoml) or not messenger_missing(mt, {k: v for k, v in mc.items() if k != 'messenger'}, mtoml)
        or not messenger_missing(mt, mc, False)
        or any(not messenger_missing(mt.replace(w, ''), mc, mtoml) for w in MESSENGER_WORDS)):
    errors.append('check.py: messenger guard negative control not flagged')
mscript = root/'scripts/messages.py'
mst = mscript.read_text().split('ENTRY_TEMPLATE = """', 1)[-1].split('STAGE_TEMPLATES', 1)[0] if mscript.is_file() else ''
errors.extend(mailbox_missing(mst))
if not mailbox_missing('') or any(not mailbox_missing(mst.replace(w, '')) for w in MAILBOX_WORDS):
    errors.append('check.py: mailbox lifecycle guard negative control not flagged')
# Solo agent (docstring item 18): a session agent with levels L1, L2, L3, a Codex mapping, and three generated TOMLs.
SOLO_WORDS = ('| L1 | L1 |', '| L2 | L2 |', '| L3 | L3 |', 'Sonnet high', '| L2 | L2 | Opus medium |', 'Opus high')
SOLO_CODEX = {'L1': ['gpt-6.1-sol', 'medium'], 'L2': ['gpt-6.1-sol', 'high'], 'L3': ['gpt-6.1-sol', 'xhigh']}
def solo_missing(agent_text, codex_models, tomls):
    out = []
    if not agent_text.strip(): out.append('solo: agents/solo.md missing or empty')
    else: out += [f'solo: agents/solo.md missing "{w}"' for w in SOLO_WORDS if w not in agent_text]
    if codex_models.get('solo') != SOLO_CODEX: out.append(f'solo: adapters/codex/models.json solo entry is not {SOLO_CODEX}')
    out += [f'solo: adapters/codex/agents/sdlc-solo-{l}.toml missing' for l in ('l1', 'l2', 'l3') if l not in tomls]
    return out
sf = root/'agents/solo.md'
st = sf.read_text() if sf.is_file() else ''
stomls = {l for l in ('l1', 'l2', 'l3') if (root/f'adapters/codex/agents/sdlc-solo-{l}.toml').is_file()}
errors.extend(solo_missing(st, mc, stomls))
if not solo_missing(st, mc, stomls) and (
        any(not solo_missing(st.replace(w, ''), mc, stomls) for w in SOLO_WORDS)
        or not solo_missing('', mc, stomls)
        or not solo_missing(st, {k: v for k, v in mc.items() if k != 'solo'}, stomls)
        or not solo_missing(st, dict(mc, solo=dict(SOLO_CODEX, L2=['gpt-6.1-sol', 'xhigh'])), stomls)
        or not solo_missing(st, mc, stomls - {'l3'})):
    errors.append('check.py: solo guard negative control not flagged')
SOLO_CLAUDE = {'L1': ['sonnet', 'high'], 'L2': ['opus', 'medium'], 'L3': ['opus', 'high']}
def solo_levels_bad(claude_solo): return [] if claude_solo == SOLO_CLAUDE else [f'solo: adapters/claude/levels.json solo levels are not {SOLO_CLAUDE}']
errors.extend(solo_levels_bad(solo_levels))
if not solo_levels_bad(dict(solo_levels, L2=['sonnet', 'high'])) or not solo_levels_bad({}):
    errors.append('check.py: solo levels negative control not flagged')
# Conductor rules (docstring item 19): philosophy and objective, lane first, stop rules, thin conductor.
CONDUCTOR_RULES = ('Done is better than perfect. Trust that modern, advanced models are very capable if given useful '
                   'context and instruction.',
                   'cheapest path that still passes independent verification',
                   'Lane first: run `steps.py lane',
                   'Lane: <lane> because <reason>',
                   'hard stop that comes to the user',
                   'take back conclusions, not file contents or logs')
def conductor_rule_missing(text, phrase): return phrase not in text
for phrase in CONDUCTOR_RULES:
    if conductor_rule_missing(ct, phrase): errors.append(f'{CONDUCTOR}: conductor rules missing "{phrase}"')
    elif not conductor_rule_missing(ct.replace(phrase, ''), phrase):
        errors.append(f'check.py: conductor rules negative control not flagged for "{phrase}"')
# Markdown-only design (T-0387): the architect skips decompose and the coverage check unless the handoff asks for a breakdown.
MD_DESIGN = 'Markdown-only design'
def md_design_missing(text): return MD_DESIGN not in text or 'coverage_check.py' not in text
for _rel in ('agents/architect.md', 'skills/architect/SKILL.md'):
    _t = (root/_rel).read_text() if (root/_rel).is_file() else ''
    if md_design_missing(_t): errors.append(f'{_rel}: missing the Markdown-only design rule')
    elif not md_design_missing(_t.replace(MD_DESIGN, '')): errors.append(f'check.py: Markdown-only design negative control not flagged for {_rel}')
# Sub-agent wait rule (T-0494): the architect reads sub-agent results in-turn; a background notice goes to the session that started it.
FG_RULE = 'Run each sub-agent in the foreground'
def fg_rule_missing(text): return FG_RULE not in text
_t = (root/'agents/architect.md').read_text() if (root/'agents/architect.md').is_file() else ''
if fg_rule_missing(_t): errors.append('agents/architect.md: missing the foreground sub-agent rule')
elif not fg_rule_missing(_t.replace(FG_RULE, '')): errors.append('check.py: foreground sub-agent rule negative control not flagged')
# Result schema (docstring item 13): agent bodies carry results.SCHEMA sections in order; no script copies the table.
def schema_section_errors(text, sections):
    lines = [l.rstrip() for l in text.splitlines()]
    out, pos = [], []
    for sec in sections:
        h = f'## {sec}'
        if h not in lines: out.append(f'missing {h}')
        else: pos.append((lines.index(h), sec))
    for (a, x), (b, y) in zip(pos, pos[1:]):
        if b < a: out.append(f'## {y} before ## {x}')
    return out
for role, spec in results.SCHEMA.items():
    af = root/f'agents/{role}.md'
    for e in schema_section_errors(af.read_text() if af.is_file() else '', spec['sections']):
        errors.append(f'agents/{role}.md: result schema: {e}')
_bt = (root/'agents/builder.md').read_text() if (root/'agents/builder.md').is_file() else ''
_swapped = _bt.replace('## Changes', '## TMPX').replace('## Checks', '## Changes').replace('## TMPX', '## Checks')
if not schema_section_errors(_swapped, results.SCHEMA['builder']['sections']):
    errors.append('check.py: result-schema agent guard negative control not flagged')
SCHEMA_COPY = {'scripts/run.sh': r"allowed='|sect=[A-Z]",
               'scripts/steps.py': r"REVIEW_VERDICTS|startswith\('inherited red:'\)|first_word\(path, '(Status|Verdict)'"}
for rel, rx in SCHEMA_COPY.items():
    f = root/rel
    if f.is_file() and re.search(rx, f.read_text()): errors.append(f'{rel}: holds a copy of the result schema')
if not re.search(SCHEMA_COPY['scripts/run.sh'], rt + "\nallowed='x'\n"):
    errors.append('check.py: result-schema copy guard negative control not flagged')
sdlc = root.resolve().parent.parent / '.sdlc'
if sdlc.is_dir():
    def _evals(plugin):
        return subprocess.run([sys.executable, str(root/'scripts/evals.py'), '--root', str(sdlc), '--plugin', str(plugin), 'check'],
                              capture_output=True, text=True)
    _r = _evals(root)
    if _r.returncode != 0:
        _lines = [l for l in (_r.stdout + '\n' + _r.stderr).splitlines() if l.strip() and not l.startswith('evals check:')]
        errors.extend(f'evals: {l}' for l in _lines) if _lines else errors.append(f'evals: evals.py check exited {_r.returncode}')
    else:
        with tempfile.TemporaryDirectory() as _td:
            _tp = pathlib.Path(_td)
            (_tp/'adapters/claude').mkdir(parents=True); (_tp/'adapters/codex').mkdir(parents=True)
            _lv = json.loads((root/'adapters/claude/levels.json').read_text()); _lv['builder']['L1'][0] = 'evals-negative-control'
            (_tp/'adapters/claude/levels.json').write_text(json.dumps(_lv))
            shutil.copy(root/'adapters/codex/models.json', _tp/'adapters/codex/models.json')
            _n = _evals(_tp)
            if 'model table changed' not in _n.stdout + _n.stderr:
                errors.append('check.py: evals lock guard negative control not flagged')
else:
    print(f'skip: evals lock guard (no {sdlc})')
# Handoff freeze (docstring item 20): runner, lifecycle, hook file, registration, and the hooks doc agree.
FREEZE_RUN = ('SDLC_HANDOFF_SHA256', 'stale_input', 'stale input:')
FREEZE_LIFE = ('SDLC_HANDOFF_SHA256', 'handoff_sha256')
def freeze_missing(run_text, life_text, hook_ok, hooks_json, docs_text):
    out = [f'handoff freeze: scripts/run.sh missing "{w}"' for w in FREEZE_RUN if w not in run_text]
    out += [f'handoff freeze: scripts/run_lifecycle.py missing "{w}"' for w in FREEZE_LIFE if w not in life_text]
    if not hook_ok: out.append('handoff freeze: hooks/warn-handoff-edit.sh missing or not executable')
    if not re.search(r'"matcher":\s*"Edit\|Write\|NotebookEdit"[^]]*warn-handoff-edit\.sh', hooks_json):
        out.append('handoff freeze: adapters/claude/hooks.json does not register warn-handoff-edit.sh under Edit|Write|NotebookEdit')
    if 'warn-handoff-edit.sh' not in docs_text: out.append('handoff freeze: docs/references/claude-hooks.md does not name warn-handoff-edit.sh')
    return out
def _rd(path): return path.read_text() if path.is_file() else ''
_hook = root/'hooks/warn-handoff-edit.sh'
_hook_ok = _hook.is_file() and os.access(_hook, os.X_OK)
_fr = (_rd(root/'scripts/run.sh'), _rd(root/'scripts/run_lifecycle.py'), _hook_ok, _rd(root/'adapters/claude/hooks.json'),
       _rd(root.resolve().parent.parent/'docs/references/claude-hooks.md'))
errors.extend(freeze_missing(*_fr))
for _i, _w in ((0, FREEZE_RUN[1]), (1, FREEZE_LIFE[1]), (4, 'warn-handoff-edit.sh'), (3, 'warn-handoff-edit.sh')):
    _args = list(_fr); _args[_i] = _args[_i].replace(_w, '')
    if not freeze_missing(*_args): errors.append(f'check.py: handoff freeze guard negative control not flagged for "{_w}"')
if not freeze_missing(_fr[0], _fr[1], False, _fr[3], _fr[4]): errors.append('check.py: handoff freeze guard negative control not flagged for the hook file')
# Solo start path (docstring item 21): solo.md holds the start command; every routing text sends ticket levels L1 and L2 to solo.
SOLO_ROUTE = (('agents/solo.md', '--agent sdlc-lite:solo'),
              (CONDUCTOR, 'Ticket levels L1 and L2 go to `solo` by default'),
              ('skills/fix/SKILL.md', 'ticket levels L1 and L2 go to `solo`'),
              ('AGENTS.md', 'Ticket level L1 and L2 plugin work goes to `solo` by default'),
              ('.claude/agents/sdlc-lite-author.md', '`solo` for ticket levels L1 and L2 by default'))
def solo_route_missing(text, phrase): return phrase not in text
for rel, phrase in SOLO_ROUTE:
    srt = _rd(root.resolve().parent.parent/rel) if rel.startswith('.claude/') else _rd(root/rel)
    if solo_route_missing(srt, phrase): errors.append(f'{rel}: solo start path missing "{phrase}"')
    elif not solo_route_missing(srt.replace(phrase, ''), phrase):
        errors.append(f'check.py: solo start path negative control not flagged for "{phrase}"')
# Claude headless retirement (docstring item 21, T-0288): the legacy opt-in and the sub-agent pointer stay in the runner and the fanout driver.
RETIRE_NEEDS = (('scripts/run.sh', 'SDLC_CLAUDE_EXEC'), ('scripts/run.sh', 'dispatch.py prepare'), ('scripts/solo_run.py', 'SDLC_CLAUDE_EXEC'))
def _fn_body(text, name):
    m = re.search(r'(?ms)^def %s\(.*?(?=^\S)' % name, text)
    return m.group(0) if m else ''
def retire_missing(text, phrase): return phrase not in text
for rel, phrase in RETIRE_NEEDS:
    rtx = _rd(root/rel)
    if retire_missing(rtx, phrase): errors.append(f'{rel}: claude headless retirement missing "{phrase}"')
    elif not retire_missing(rtx.replace(phrase, ''), phrase): errors.append(f'check.py: claude retirement negative control not flagged for "{phrase}" in {rel}')
ddb = _fn_body(_rd(root/'scripts/fanout.py'), 'default_driver')
if retire_missing(ddb, 'SDLC_CLAUDE_EXEC'): errors.append('scripts/fanout.py: default_driver body missing the SDLC_CLAUDE_EXEC gate')
elif not retire_missing(ddb.replace('SDLC_CLAUDE_EXEC', ''), 'SDLC_CLAUDE_EXEC'): errors.append('check.py: default_driver gate negative control not flagged')
# Guard numbers (docstring item 23): the docstring's numbered guards run 1..N once each, and every "docstring item N" comment names one.
def guard_numbers_bad(doc, src):
    nums = [int(n) for n in re.findall(r'(?m)^(\d+)\. ', doc)]
    bad = []
    if nums != list(range(1, len(nums) + 1)): bad.append(f'docstring guard numbers are not 1..{len(nums)} once each: {nums}')
    bad += [f'comment cites docstring item {n}, which does not exist' for n in sorted({int(n) for n in re.findall(r'docstring item (\d+)', src)} - set(nums))]
    return bad
_src = pathlib.Path(__file__).read_text()
for _b in guard_numbers_bad(__doc__, _src): errors.append(f'check.py: {_b}')
_dup = __doc__.replace('\n19. Conductor rules', '\n18. Conductor rules', 1)
if not guard_numbers_bad(_dup, _src): errors.append('check.py: guard numbers negative control not flagged for a duplicated number')
if not guard_numbers_bad(__doc__, _src + '\n# x (docstring ' + 'item 99)'): errors.append('check.py: guard numbers negative control not flagged for a missing item')
# Fanout solo first (docstring item 24): fanout.py picks the lane per ticket and starts solo at the solo.md levels.
SOLO_ROW_RE = r"'(L[1-3])': \('(\w+)', '(\w+)', '(L\d)'\)"
FANOUT_PHRASES = ('sdlc-lite:solo', 'solo_command(', 'SOLO_VERIFIER', '--max-lanes', '--stagger', '--yes-many', '--allow-overlap', 'def cmd_prep(', 'def cmd_land(', 'SOLO_SUBAGENT_PROMPT')
FANOUT_SKILL_PHRASES = ('Solo first', '--max-lanes', '--stagger', 'fanout.py prep', 'fanout.py land', '`Tree: <path>`', 'wtroot.py root')
def fanout_solo_bad(fan, solo, skill):
    bad = [f'fanout.py missing "{ph}"' for ph in FANOUT_PHRASES if ph not in fan]
    bad += [f'skills/fanout/SKILL.md missing "{ph}"' for ph in FANOUT_SKILL_PHRASES if ph not in skill]
    tiers = re.findall(SOLO_ROW_RE, fan)
    if sorted(t[0] for t in tiers) != ['L1', 'L2', 'L3']: bad.append('fanout.py SOLO_TIERS does not list L1, L2, and L3')
    for tier, model, effort, level in tiers:
        if not re.search(rf'^\| {tier} \| {tier} \| {model.capitalize()} {effort} \|', solo, re.M): bad.append(f'SOLO_TIERS {tier} {model} {effort} is not the level {tier} row of agents/solo.md')
        if level != tier: bad.append(f'SOLO_TIERS {tier} has Codex level {level}')
    return bad
_ff, _fs, _fk = _rd(root/'scripts/fanout.py'), _rd(root/'agents/solo.md'), _rd(root/'skills/fanout/SKILL.md')
errors.extend(fanout_solo_bad(_ff, _fs, _fk))
for _mut in (lambda t: t.replace("'L2': ('opus', 'medium', 'L2')", "'L2': ('opus', 'low', 'L2')"), lambda t: t.replace('--stagger', '--pause'), lambda t: t.replace('def cmd_land(', 'def cmd_x(')):
    if not fanout_solo_bad(_mut(_ff), _fs, _fk): errors.append('check.py: fanout solo first negative control not flagged for a changed fanout.py')
if not fanout_solo_bad(_ff, _fs, _fk.replace('Solo first', '')): errors.append('check.py: fanout solo first negative control not flagged for the skill')
for _ph in ('fanout.py prep', 'fanout.py land', '`Tree: <path>`', 'wtroot.py root'):
    if not fanout_solo_bad(_ff, _fs, _fk.replace(_ph, '')): errors.append(f'check.py: fanout sub-agent lane negative control not flagged for the skill without {_ph}')
# Agent command (docstring item 25): the /agent skill's names agree with agents/*.md and the Codex mapping.
def agent_cmd_bad(skill, stems, codex_keys):
    if not skill.strip(): return ['skills/agent/SKILL.md missing or empty']
    bad = [f'skills/agent/SKILL.md does not name `{n}`' for n in sorted(stems) if f'`{n}`' not in skill]
    rows = re.findall(r'(?m)^\| `([a-z][\w-]*)` \|', skill)
    bad += [f'skills/agent/SKILL.md table row `{n}` has no agents/{n}.md' for n in rows if n not in stems]
    bad += [f'skills/agent/SKILL.md table row `{n}` has no Codex entry in models.json' for n in rows if n in stems and n not in codex_keys]
    if 'block-role-spawn.sh' not in skill: bad.append('skills/agent/SKILL.md does not name block-role-spawn.sh')
    return bad
_ak = _rd(root/'skills/agent/SKILL.md')
_as = {p.stem for p in (root/'agents').glob('*.md')} - GENERATED
errors.extend(agent_cmd_bad(_ak, _as, set(mc)))
if not agent_cmd_bad(_ak.replace('`archaeologist`', 'archaeologist'), _as, set(mc)): errors.append('check.py: agent command negative control not flagged for a removed stem')
if not agent_cmd_bad(_ak + '\n| `ghost` | x | x |\n', _as, set(mc)): errors.append('check.py: agent command negative control not flagged for a row with no agent file')
if not agent_cmd_bad(_ak, _as, set(mc) - {'scout'}): errors.append('check.py: agent command negative control not flagged for a row with no Codex entry')
# Solo lane skips (docstring item 26): the lane script itself writes the skipped planner and filer for lane solo.
SOLO_SKIPS_PHRASES = (('scripts/steps.py', 'solo_skips_text'), ('scripts/steps.py', 'write_solo_skips(task)'),
                      ('scripts/fanout.py', 'steps.write_solo_skips'), ('agents/conductor.md', 'tickets.py close --reason'))
def solo_skips_missing(text, phrase): return phrase not in text
for rel, phrase in SOLO_SKIPS_PHRASES:
    sst = _rd(root/rel)
    if solo_skips_missing(sst, phrase): errors.append(f'{rel}: solo lane skips missing "{phrase}"')
    elif not solo_skips_missing(sst.replace(phrase, ''), phrase):
        errors.append(f'check.py: solo lane skips negative control not flagged for "{phrase}"')
# Solo cost capture (docstring item 27): solo_run.py records the solo session's cost; solo.md names it as the start path.
SOLO_RUN_PHRASES = ('sdlc-lite:solo', 'SDLC_ROLE', 'cost_usd', 'cost_reason', 'total_cost_usd')
def solo_cost_bad(run_py, solo, fan):
    bad = [f'solo_run.py missing "{ph}"' for ph in SOLO_RUN_PHRASES if ph not in run_py]
    if 'solo_run.py' not in solo: bad.append('agents/solo.md does not name solo_run.py as the start path')
    mine = re.findall(SOLO_ROW_RE, run_py)
    if sorted(t[0] for t in mine) != ['L1', 'L2', 'L3']: bad.append('solo_run.py TIERS does not list L1, L2, and L3')
    for tier, model, effort, level in mine:
        if not re.search(rf'^\| {tier} \| {tier} \| {model.capitalize()} {effort} \|', solo, re.M): bad.append(f'solo_run.py TIERS {tier} {model} {effort} is not the level {tier} row of agents/solo.md')
    if sorted(mine) != sorted(re.findall(SOLO_ROW_RE, fan)): bad.append('solo_run.py TIERS differ from fanout.py SOLO_TIERS')
    return bad
_sr = _rd(root/'scripts/solo_run.py')
errors.extend(solo_cost_bad(_sr, _fs, _ff))
for _mut in (lambda t: t.replace("'L2': ('opus', 'medium', 'L2')", "'L2': ('opus', 'low', 'L2')"), lambda t: t.replace('cost_reason', 'cost_why')):
    if not solo_cost_bad(_mut(_sr), _fs, _ff): errors.append('check.py: solo cost capture negative control not flagged for a changed solo_run.py')
if not solo_cost_bad(_sr, _fs.replace('solo_run.py', 'the wrapper'), _ff): errors.append('check.py: solo cost capture negative control not flagged for solo.md')
# Solo budget gate (docstring item 28): solo_run.py stops at 80 percent with no ack, fanout names the outcome, the docs say so.
_sa, _fk2 = _rd(root/'skills/agent/SKILL.md'), _fk
SOLO_GATE_NEEDS = (('solo_run.py', ('budget_hold', 'budget.py ack', '--new-task', 'return 4')), ('fanout.py', ('budget gate: budget.py ack',)),
                   ('solo.md', ('budget.py ack', '--new-task')), ('agent SKILL.md', ('--new-task', 'budget.py ack')), ('fanout SKILL.md', ('budget gate', 'budget.py ack')))
def solo_gate_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in SOLO_GATE_NEEDS for ph in phrases if ph not in texts[name]]
_gate_texts = {'solo_run.py': _sr, 'fanout.py': _ff, 'solo.md': _fs, 'agent SKILL.md': _sa, 'fanout SKILL.md': _fk2}
errors.extend(f'check.py: solo budget gate: {m}' for m in solo_gate_bad(_gate_texts))
for _name, _phrases in SOLO_GATE_NEEDS:
    for _ph in _phrases:
        if not solo_gate_bad(dict(_gate_texts, **{_name: _gate_texts[_name].replace(_ph, '')})): errors.append(f'check.py: solo budget gate negative control not flagged for {_name} without "{_ph}"')
# Ask skill (docstring item 29): self-contained sweep, reasoned options, one round, a prose path, routed from the entry skill and the conductor.
_ask, _entry, _cond = _rd(root/'skills/ask/SKILL.md'), _rd(root/'skills/sdlc-lite/SKILL.md'), _rd(root/'agents/conductor.md')
ASK_NEEDS = ('## 1. Sweep', '## 2. Reason the options', '## 3. Ask once', '## 4. Take prose', 'Write it in chat', 'Nothing open.', 'AskUserQuestion', 'tickets.py --root .sdlc blockers', '--scope', '## Verdict', 'If AskUserQuestion is unavailable')
def ask_bad(ask, entry, cond):
    out = [f'ask SKILL.md missing "{ph}"' for ph in ASK_NEEDS if ph not in ask]
    if re.search(r'harness:', ask): out.append('ask SKILL.md references harness:')
    if '/ ask |' not in entry: out.append('skills/sdlc-lite/SKILL.md does not route to ask')
    if '/sdlc-lite:ask' not in cond: out.append('agents/conductor.md does not route to /sdlc-lite:ask')
    return out
errors.extend(f'check.py: ask skill: {m}' for m in ask_bad(_ask, _entry, _cond))
for _ph in ASK_NEEDS:
    if not ask_bad(_ask.replace(_ph, ''), _entry, _cond): errors.append(f'check.py: ask skill negative control not flagged for "{_ph}"')
if not ask_bad(_ask + ' see harness:find-open-questions', _entry, _cond): errors.append('check.py: ask skill negative control not flagged for a harness reference')
if not ask_bad(_ask, _entry.replace('/ ask |', '|'), _cond): errors.append('check.py: ask skill negative control not flagged for a missing entry route')
if not ask_bad(_ask, _entry, _cond.replace('/sdlc-lite:ask', '')): errors.append('check.py: ask skill negative control not flagged for a missing conductor route')
# Document inventory (docstring item 30): the read-only inventory script, its selftest wiring, and the plan procedure.
INVENTORY_NEEDS = (('inventory.py', ('orphan', 'stale', 'duplicate', 'oversized', 'misplaced', 'broken_links', '--include-sdlc', '--out', 'refusing to write inside the repository')),
                   ('check.sh', ('inventory.py" selftest',)), ('procedure', ('inventory.py',)))
def inventory_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in INVENTORY_NEEDS for ph in phrases if ph not in texts[name]]
_inv_texts = {'inventory.py': _rd(root/'scripts/inventory.py'), 'check.sh': _rd(root/'scripts/check.sh'),
              'procedure': _rd(root/'../../docs/planning/repo-onboarding/reorganization-plan-procedure.md')}
errors.extend(f'check.py: document inventory: {m}' for m in inventory_bad(_inv_texts))
for _name, _phrases in INVENTORY_NEEDS:
    for _ph in _phrases:
        if not inventory_bad(dict(_inv_texts, **{_name: _inv_texts[_name].replace(_ph, '')})): errors.append(f'check.py: document inventory negative control not flagged for {_name} without {_ph}')
# Reorganization apply (docstring item 38): the apply script, its selftest wiring, and the plan procedure's apply step.
REORG_NEEDS = (('reorg.py', ('--dry-run', '--approve', 'reorg.py: refused:', 'final check failed')),
               ('check.sh', ('reorg.py" selftest',)), ('procedure', ('reorg.py', '--approve')))
def reorg_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in REORG_NEEDS for ph in phrases if ph not in texts[name]]
_reorg_texts = {'reorg.py': _rd(root/'scripts/reorg.py'), 'check.sh': _rd(root/'scripts/check.sh'),
                'procedure': _rd(root/'../../docs/planning/repo-onboarding/reorganization-plan-procedure.md')}
errors.extend(f'check.py: reorganization apply: {m}' for m in reorg_bad(_reorg_texts))
for _name, _phrases in REORG_NEEDS:
    for _ph in _phrases:
        if not reorg_bad(dict(_reorg_texts, **{_name: _reorg_texts[_name].replace(_ph, '')})): errors.append(f'check.py: reorganization apply negative control not flagged for {_name} without {_ph}')
# Plan skills (docstring item 31): the plan skill and plan-loop each return a validated paste-ready block, routed from the entry skill.
PLAN_NEEDS = ('## 1. Gather', 'plan_check.py', 'AskUserQuestion', 'Why this plan', 'You must authorize', 'Unattended', 'Codex host')
PLAN_KINDS = ('steps', 'doc', 'goal', 'campaign', 'fanout')
PLAN_ROUTES = {'plan': 'plan <kind>', 'loop': 'plan-loop'}
PLAN_EXTRA = {'plan': PLAN_KINDS + ('references/plan-rules.md',)}
def plan_bad(texts, entry):
    out = []
    for name, body in texts.items():
        out += [f'{name} SKILL.md missing "{ph}"' for ph in PLAN_NEEDS + PLAN_EXTRA.get(name, ()) if ph not in body]
        if re.search(r'harness:', body): out.append(f'{name} SKILL.md references harness:')
        if PLAN_ROUTES[name] not in entry: out.append(f'skills/sdlc-lite/SKILL.md does not route to {PLAN_ROUTES[name]}')
    return out
_plans = {n: _rd(root/('skills/plan/SKILL.md' if n == 'plan' else f'skills/plan-{n}/SKILL.md')) for n in PLAN_ROUTES}
errors.extend(f'check.py: plan skills: {m}' for m in plan_bad(_plans, _entry))
for _n in _plans:
    for _ph in PLAN_NEEDS + PLAN_EXTRA.get(_n, ()):
        if not plan_bad(dict(_plans, **{_n: _plans[_n].replace(_ph, '')}), _entry): errors.append(f'check.py: plan skills negative control not flagged for {_n} without "{_ph}"')
    if not plan_bad(dict(_plans, **{_n: _plans[_n] + ' harness:x'}), _entry): errors.append(f'check.py: plan skills negative control not flagged for a harness reference in {_n}')
    if not plan_bad(_plans, _entry.replace(PLAN_ROUTES[_n], 'x')): errors.append(f'check.py: plan skills negative control not flagged for a missing entry route to {_n}')
# Plan compaction (docstring item 31, T-0465): the compaction kind of the plan skill, its reference, and the entry route.
PLAN_COMPACTION_NEEDS = (('skill', ('compaction', 'references/compaction.md')),
                         ('reference', ('plan_check.py compaction', 'Run: /compact', 'lines: N of 60', '## Compaction handoff', 'compaction_handoff.py',
                                        'git check-ignore', 'KEEP', 'POINT', 'DROP', 'NEXT', '[U]', 'Codex')),
                         ('entry', ('plan compaction',)))
def plan_compaction_bad(texts):
    """Findings for {'skill': skills/plan/SKILL.md, 'reference': references/compaction.md or '' when it is missing, 'entry': the entry skill}."""
    out = [f'{name} missing "{ph}"' for name, phrases in PLAN_COMPACTION_NEEDS for ph in phrases if ph not in texts[name]]
    if not texts['reference']: out.append('skills/plan/references/compaction.md is missing or empty')
    if 'harness:' in texts['reference']: out.append('skills/plan/references/compaction.md references harness:')
    return out
_pc = {'skill': _plans['plan'], 'reference': _rd(root/'skills/plan/references/compaction.md'), 'entry': _entry}
errors.extend(f'check.py: plan compaction: {m}' for m in plan_compaction_bad(_pc))
for _name, _phrases in PLAN_COMPACTION_NEEDS:
    for _ph in _phrases:
        if not plan_compaction_bad(dict(_pc, **{_name: _pc[_name].replace(_ph, '')})): errors.append(f'check.py: plan compaction negative control not flagged for {_name} without "{_ph}"')
if plan_compaction_bad(dict(_pc, reference='')) == plan_compaction_bad(dict(_pc, reference='x')): errors.append('check.py: plan compaction negative control not flagged for an empty reference')
if not plan_compaction_bad(dict(_pc, reference=_pc['reference'] + ' harness:x')): errors.append('check.py: plan compaction negative control not flagged for a harness reference')
if not plan_compaction_bad(dict(_pc, entry='\n'.join(_l for _l in _pc['entry'].splitlines() if '| plan compaction |' not in _l))): errors.append('check.py: plan compaction negative control not flagged for a removed entry row')
# Plan verification (docstring item 48): the capture skill, its shared reference, and the plan skill's goal reference that reads it.
PV_NEEDS = (('skill', ('references/outcome-block.md', 'Codex host', 'Unattended')),
            ('reference', ('Outcome', 'Measured by', 'Rubric', 'Negative control', 'outcome-block', 'done-measured')),
            ('goal', ('plan-verification',)), ('rules', ('outcome-block.md',)), ('entry', ('plan-verification',)))
def pv_bad(texts):
    out = [f'{name} missing "{ph}"' for name, phrases in PV_NEEDS for ph in phrases if ph not in texts[name]]
    if 'harness:' in texts['skill']: out.append('plan-verification SKILL.md references harness:')
    return out
_pv = {'skill': _rd(root/'skills/plan-verification/SKILL.md'), 'reference': _rd(root/'skills/plan-verification/references/outcome-block.md'),
       'goal': _rd(root/'skills/plan/SKILL.md'), 'rules': _rd(root/'skills/plan/references/goal.md'), 'entry': _entry}
errors.extend(f'check.py: plan verification: {m}' for m in pv_bad(_pv))
for _name, _phrases in PV_NEEDS:
    for _ph in _phrases:
        if not pv_bad(dict(_pv, **{_name: _pv[_name].replace(_ph, '')})): errors.append(f'check.py: plan verification negative control not flagged for {_name} without "{_ph}"')
if not pv_bad(dict(_pv, skill=_pv['skill'] + ' harness:x')): errors.append('check.py: plan verification negative control not flagged for a harness reference')
# Plan-doc parser and linter (docstring item 49): the shared parser, the 19 rule ids of section 3.3 of the plan-doc design, and the selftest wiring.
PLAN_RULES = ('plan-front', 'no-approval', 'outcome-block', 'done-measured', 'measure-row', 'measure-safe', 'later-named', 'step-shape', 'depends-order', 'cap-sum',
              'executor-unknown', 'verifier-seat', 'review-missing', 'upsert-shape', 'upsert-sweep', 'authorization', 'stop-rules', 'goal-line', 'done-plan-done')
PLAN_DOC_NEEDS = (('plan_doc.py', ('def parse', 'def table', 'def goal_line', 'steps.STEP_RE')),
                  ('plan_check.py', ('GOOD_PLAN', 'def check_plan', 'plan_doc', 'l1-unverified', 'kpi-drift', 'kpi-unresolved') + PLAN_RULES),
                  ('check.sh', ('plan_check.py" selftest', 'plan_doc.py" selftest')))
def plan_doc_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in PLAN_DOC_NEEDS for ph in phrases if ph not in texts[name]]
_pd = {'plan_doc.py': _rd(root/'scripts/plan_doc.py'), 'plan_check.py': _rd(root/'scripts/plan_check.py'), 'check.sh': _rd(root/'scripts/check.sh')}
errors.extend(f'check.py: plan doc: {m}' for m in plan_doc_bad(_pd))
for _name, _phrases in PLAN_DOC_NEEDS:
    for _ph in _phrases:
        if not plan_doc_bad(dict(_pd, **{_name: _pd[_name].replace(_ph, '')})): errors.append(f'check.py: plan doc negative control not flagged for {_name} without "{_ph}"')
# Plan-doc stop condition (docstring item 50): plan_done.py, its selftest wiring, and the internals reference.
PLAN_DONE_NEEDS = (('plan_done.py', ('plan done', 'plan defect:', 'ticket-absent', 'records ok; measures not read', 'replan cap reached: stopped', 'held_items', 'def assess',
                                     'def selftest', 'import dispatch, order, plan_check, plan_doc, results, steps, tickets')),
                   ('check.sh', ('plan_done.py" selftest',)),
                   ) + ((('internals', ('scripts/plan_done.py',)),) if (root/'../../docs/references/sdlc-internals.md').is_file() else ())  # absent in a consumer install
def plan_done_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in PLAN_DONE_NEEDS for ph in phrases if ph not in texts[name]]
_pn = {'plan_done.py': _rd(root/'scripts/plan_done.py'), 'check.sh': _rd(root/'scripts/check.sh'), 'internals': _rd(root/'../../docs/references/sdlc-internals.md')}
errors.extend(f'check.py: plan done: {m}' for m in plan_done_bad(_pn))
for _name, _phrases in PLAN_DONE_NEEDS:
    for _ph in _phrases:
        if not plan_done_bad(dict(_pn, **{_name: _pn[_name].replace(_ph, '')})): errors.append(f'check.py: plan done negative control not flagged for {_name} without "{_ph}"')
# Plan-doc skills (docstring item 51): the writing skill, the running skill, their references, and the routes to them.
PDS_NEEDS = (('doc', ('## 1. Gather', 'plan_check.py plan', 'plan_done.py', 'Unattended', 'Codex host')), ('prules', ('SDLC_ROLE',)),
             ('run', ('Read', 'plan_check.py plan', 'plan_done.py', 'Unattended', 'Codex host', 'SDLC_ROLE')),
             ('format', ('plan_check.py plan', 'Goal line')), ('rules', ('plan_done.py', 'steps.py next', 'fanout.py prep', 'plan_done.py resume PD', 'recover --root . --open', 'fanout.py settle', 'status: ready', 'Close a step only through `land`')),
             ('entry', ('plan doc', 'run-plan')), ('cond', ('/sdlc-lite:plan doc', 'run-plan')))
def pds_bad(texts):
    out = [f'{name} missing "{ph}"' for name, phrases in PDS_NEEDS for ph in phrases if ph not in texts[name]]
    out += [f'{name} references harness:' for name in ('doc', 'prules', 'run', 'format', 'rules') if 'harness:' in texts[name]]
    return out
_pds = {'doc': _rd(root/'skills/plan/SKILL.md'), 'prules': _rd(root/'skills/plan/references/plan-rules.md'), 'run': _rd(root/'skills/run-plan/SKILL.md'), 'format': _rd(root/'skills/plan/references/doc.md'),
        'rules': _rd(root/'skills/run-plan/references/run-rules.md'), 'entry': _entry, 'cond': _cond}
errors.extend(f'check.py: plan-doc skills: {m}' for m in pds_bad(_pds))
for _name, _phrases in PDS_NEEDS:
    for _ph in _phrases:
        if not pds_bad(dict(_pds, **{_name: _pds[_name].replace(_ph, '')})): errors.append(f'check.py: plan-doc skills negative control not flagged for {_name} without "{_ph}"')
for _name in ('doc', 'prules', 'run', 'format', 'rules'):
    if not pds_bad(dict(_pds, **{_name: _pds[_name] + ' harness:x'})): errors.append(f'check.py: plan-doc skills negative control not flagged for a harness reference in {_name}')
# Broken-link baseline (docstring item 32): runs only where the repository root is a git work tree (not in a consumer install).
def links_bad(broken, allowed):
    got, want = set(broken), set(allowed)
    return [f'unlisted broken link {f} -> {t}' for f, t in sorted(got - want)] + [f'stale allowlist row {f} -> {t}' for f, t in sorted(want - got)]
_repo = (root/'../..').resolve()
if (_repo/'.git').exists() and (_repo/'docs/reports/broken-links-allowlist.md').is_file():
    sys.path.insert(0, str(root/'scripts'))
    import rename_refs as _R
    _broken = [tuple(b) for b in _R.link_report(str(_repo))[1]]
    _allowed = [tuple(c.strip('` ') for c in ln.split('|')[1:3]) for ln in (_repo/'docs/reports/broken-links-allowlist.md').read_text().splitlines() if ln.startswith('| `')]
    errors.extend(f'check.py: broken links: {m}' for m in links_bad(_broken, _allowed))
    if not links_bad(_broken + [('x.md', 'nope.md')], _allowed): errors.append('check.py: broken links negative control not flagged for an extra broken link')
    if not links_bad(_broken, _allowed + [('x.md', 'nope.md')]): errors.append('check.py: broken links negative control not flagged for a stale allowlist row')
# Docs check (docstring item 33): the docs schema checker, its rule ids, and its selftest wiring.
DOCS_CHECK_NEEDS = (('docs_check.py', tuple(f'D-{i}' for i in range(1, 13)) + ('B-1a', 'B-2a', 'B-3a', '--root', '--only', 'Legacy')),
                    ('check.sh', ('docs_check.py" selftest', 'docs_check.py" --root')))
def docs_check_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in DOCS_CHECK_NEEDS for ph in phrases if ph not in texts[name]]
_dc_texts = {'docs_check.py': _rd(root/'scripts/docs_check.py'), 'check.sh': _rd(root/'scripts/check.sh')}
errors.extend(f'check.py: docs check: {m}' for m in docs_check_bad(_dc_texts))
for _name, _phrases in DOCS_CHECK_NEEDS:
    for _ph in _phrases:
        if not docs_check_bad(dict(_dc_texts, **{_name: _dc_texts[_name].replace(_ph, '')})): errors.append(f'check.py: docs check negative control not flagged for {_name} without {_ph}')
# Product name guard (docstring item 34): runs only where the repository root is a git work tree.
NAME_BANNED = ('Lean ' + 'SDLC', 'lean ' + 'SDLC', 'SDLC' + '-Lite', 'sdlc ' + 'lite')
NAME_ALLOW = ('docs/reports/*', '.sdlc/.[0-9]*', '.sdlc/verify-*', '.sdlc/*0309*', 'plugins/sdlc-lite/bench/results/*')
def name_bad(texts):
    import fnmatch
    return [f'{rel}: retired spelling "{b}"' for rel, t in sorted(texts.items()) if not any(fnmatch.fnmatchcase(rel, g) for g in NAME_ALLOW) for b in NAME_BANNED if b in t]
if (_repo/'.git').exists():
    _names = {}
    for _rel in subprocess.run(['git', 'ls-files', '-z'], cwd=_repo, capture_output=True, text=True).stdout.split('\0'):
        if _rel and (_repo/_rel).is_file():
            try: _names[_rel] = (_repo/_rel).read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError): pass
    errors.extend(f'check.py: product name: {m}' for m in name_bad(_names))
    if not name_bad(dict(_names, **{'docs/x.md': 'a ' + NAME_BANNED[0] + ' b'})): errors.append('check.py: product name negative control not flagged for a planted spelling')
    if name_bad({'docs/reports/x.md': 'a ' + NAME_BANNED[1] + ' b'}): errors.append('check.py: product name allowlist did not suppress a docs/reports path')
# Gate lock (docstring item 35): the semaphore script, its selftest wiring, the fanout wrapper, and the conductor and internals mentions.
GATE_LOCK_NEEDS = (('gate_lock.py', ('SLOT-CAP', 'SDLC_GATE_WORKERS', 'SDLC_GATE_SLOTS', 'sdlc-gate-locks', 'SDLC_GATE_DIR', 'SDLC_GATE_GRANT')),
                   ('check.sh', ('gate_lock.py" selftest',)), ('fanout.py', ('gate_lock.py', '--no-gate-lock')),
                   ('conductor', ('gate_lock.py run',)), ('internals', ('gate_lock.py',)))
def gate_lock_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in GATE_LOCK_NEEDS for ph in phrases if name in texts and ph not in texts[name]]
_gl_texts = {'gate_lock.py': _rd(root/'scripts/gate_lock.py'), 'check.sh': _rd(root/'scripts/check.sh'), 'fanout.py': _rd(root/'scripts/fanout.py'),
             'conductor': _rd(root/'agents/conductor.md')}
if (root/'../../docs/references/sdlc-internals.md').is_file(): _gl_texts['internals'] = _rd(root/'../../docs/references/sdlc-internals.md')
errors.extend(f'check.py: gate lock: {m}' for m in gate_lock_bad(_gl_texts))
for _name, _phrases in GATE_LOCK_NEEDS:
    for _ph in _phrases:
        if _name in _gl_texts and not gate_lock_bad(dict(_gl_texts, **{_name: _gl_texts[_name].replace(_ph, '')})): errors.append(f'check.py: gate lock negative control not flagged for {_name} without {_ph}')
# Fleet retro (docstring item 36): the skill, its rubric and fixtures, and the routes to it.
FLEET_NEEDS = (('skill', ('fleet_collect.py', 'fleet_detect.py', 'SendMessage', 'interview.md', 'rubric.md', 'AskUserQuestion', 'review-traces', 'Codex host',
                          'SDLC_HEADLESS', '## 1. Collect', '## 2. Detect', '## 3. Interview', '## 4. Report', '## 5. Verify', '## 6. File')),
               ('rubric', tuple(f'G{i}' for i in range(1, 6)) + tuple(f'C{i}' for i in range(1, 6)) + ('7 of 10', 'Outcome check')),
               ('fixtures', ('F1', 'F2', 'F3')), ('entry', ('fleet-retro',)), ('conductor', ('fleet-retro',)), ('internals', ('fleet-retro',)))
def fleet_bad(texts):
    out = [f'{name} missing "{ph}"' for name, phrases in FLEET_NEEDS for ph in phrases if name in texts and ph not in texts[name]]
    if 'harness:' in texts['skill']: out.append('skill references harness:')
    return out
_fl_texts = {'skill': _rd(root/'skills/fleet-retro/SKILL.md'), 'rubric': _rd(root/'skills/fleet-retro/rubric.md'), 'fixtures': _rd(root/'skills/fleet-retro/fixtures.md'),
             'entry': _entry, 'conductor': _rd(root/'agents/conductor.md')}
if (root/'../../docs/references/sdlc-internals.md').is_file(): _fl_texts['internals'] = _rd(root/'../../docs/references/sdlc-internals.md')
errors.extend(f'check.py: fleet retro: {m}' for m in fleet_bad(_fl_texts))
for _name, _phrases in FLEET_NEEDS:
    for _ph in _phrases:
        if _name in _fl_texts and not fleet_bad(dict(_fl_texts, **{_name: _fl_texts[_name].replace(_ph, '')})): errors.append(f'check.py: fleet retro negative control not flagged for {_name} without {_ph}')
if not fleet_bad(dict(_fl_texts, skill=_fl_texts['skill'] + ' harness:x')): errors.append('check.py: fleet retro negative control not flagged for a harness reference')
# Fleet status (docstring item 37): the skill prints the renderer's output and asks once; the renderer refuses a row with no source.
FLEET_STATUS_NEEDS = (('skill', ('fleet_status.py render', '## 1. Render', '## 2. Print it', '## 3. Ask once', '## 4. Relay, do not act', 'Render, never compose',
                                 'AskUserQuestion', 'If AskUserQuestion is unavailable', '--ping', 'sends nothing', 'Codex host',
                                 'resources/fleet-status.schema.json')),
                      ('script', ('RenderError', 'def render(', 'def schema_errors', 'def selftest_render')), ('check.sh', ('fleet_status.py" selftest',)))
FLEET_SCHEMA_KEYS = ('machine', 'repos', 'needs_you', 'delta')
def fleet_schema_bad(text):
    if not text.strip(): return ['skills/fleet-status/resources/fleet-status.schema.json is missing or empty']
    try: doc = json.loads(text)
    except ValueError as e: return [f'fleet-status.schema.json does not parse as JSON: {e}']
    if not isinstance(doc, dict): return ['fleet-status.schema.json is not a JSON object']
    out = [] if doc.get('$schema') == 'https://json-schema.org/draft/2020-12/schema' else ['fleet-status.schema.json does not declare draft 2020-12']
    return out + [f'fleet-status.schema.json does not require "{k}"' for k in FLEET_SCHEMA_KEYS if k not in (doc.get('required') or [])]
def fleet_status_bad(texts, entry):
    out = [f'{name} missing "{ph}"' for name, phrases in FLEET_STATUS_NEEDS for ph in phrases if ph not in texts[name]]
    out += fleet_schema_bad(texts['schema'])
    if re.search(r'harness:', texts['skill']): out.append('fleet-status SKILL.md references harness:')
    if '| fleet-status |' not in entry: out.append('skills/sdlc-lite/SKILL.md does not route to fleet-status')
    return out
_fs_texts = {'skill': _rd(root/'skills/fleet-status/SKILL.md'), 'script': _rd(root/'scripts/fleet_status.py'), 'check.sh': _rd(root/'scripts/check.sh'),
             'schema': _rd(root/'skills/fleet-status/resources/fleet-status.schema.json')}
errors.extend(f'check.py: fleet status: {m}' for m in fleet_status_bad(_fs_texts, _entry))
for _name, _phrases in FLEET_STATUS_NEEDS:
    for _ph in _phrases:
        if not fleet_status_bad(dict(_fs_texts, **{_name: _fs_texts[_name].replace(_ph, '')}), _entry): errors.append(f'check.py: fleet status negative control not flagged for {_name} without "{_ph}"')
if not fleet_status_bad(dict(_fs_texts, skill=_fs_texts['skill'] + ' harness:x'), _entry): errors.append('check.py: fleet status negative control not flagged for a harness reference')
if not fleet_status_bad(_fs_texts, _entry.replace('| fleet-status |', '|')): errors.append('check.py: fleet status negative control not flagged for a missing entry route')
for _why, _bad in (('a missing schema file', ''), ('an unparsable schema file', _fs_texts['schema'][:-20]), ('a schema file that is not an object', '[]'),
                   ('a schema file with the wrong draft', _fs_texts['schema'].replace('2020-12', '2019-09')),
                   ('a schema file that does not require repos', _fs_texts['schema'].replace('"repos", ', '', 1))):
    if not fleet_status_bad(dict(_fs_texts, schema=_bad), _entry): errors.append(f'check.py: fleet status negative control not flagged for {_why}')
# Generated Claude definitions (docstring item 39): one agents/<role>-L<n>.md per levels.json row, never hand-edited.
def claude_roles_check(plugin):
    return subprocess.run([sys.executable, str(root/'scripts/claude_roles.py'), '--plugin', str(plugin), 'generate', '--check'], capture_output=True, text=True)
_cr = claude_roles_check(root)
if _cr.returncode != 0: errors.extend(f'generated definitions: {l.removeprefix("claude_roles.py: ")}' for l in (_cr.stderr or _cr.stdout).strip().splitlines())
elif GENERATED:
    with tempfile.TemporaryDirectory() as _td:
        _tp = pathlib.Path(_td)
        shutil.copytree(root/'agents', _tp/'agents'); (_tp/'adapters/claude').mkdir(parents=True)
        shutil.copy(root/'adapters/claude/levels.json', _tp/'adapters/claude/levels.json')
        if (root/'overlays').exists(): shutil.copytree(root/'overlays', _tp/'overlays')
        _gen = _tp/'agents'/(sorted(GENERATED)[0] + '.md')
        _gen.write_text(_gen.read_text() + 'hand edit\n')
        if claude_roles_check(_tp).returncode != 1: errors.append('check.py: generated definitions negative control not flagged for a hand edit')
        shutil.copy(root/('agents/' + _gen.name), _gen)
        _lv = json.loads((_tp/'adapters/claude/levels.json').read_text()); _lv['builder']['L1'][1] = 'xhigh'
        (_tp/'adapters/claude/levels.json').write_text(json.dumps(_lv))
        if claude_roles_check(_tp).returncode != 1: errors.append('check.py: generated definitions negative control not flagged for a levels.json effort changed without regenerating')
CLAUDE_ROLES_NEEDS = ('claude_roles.py" generate --check', 'claude_roles.py" selftest')
def claude_roles_wiring_bad(sh): return [f'scripts/check.sh missing "{ph}"' for ph in CLAUDE_ROLES_NEEDS if ph not in sh]
_cr_sh = _rd(root/'scripts/check.sh')
errors.extend(f'check.py: generated definitions: {m}' for m in claude_roles_wiring_bad(_cr_sh))
for _ph in CLAUDE_ROLES_NEEDS:
    if not claude_roles_wiring_bad(_cr_sh.replace(_ph, '')): errors.append(f'check.py: generated definitions negative control not flagged for check.sh without {_ph}')
# Dispatch core (docstring item 40): the five dispatch texts name prepare, the Agent spawn, and record, and run.sh only for Codex.
DISPATCH_FILES = ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/fix/SKILL.md', 'skills/level-rubric/SKILL.md', 'skills/handoff-format/SKILL.md')
DISPATCH_PHRASES = ('dispatch.py prepare', 'dispatch.py record', '`Agent`', '`name`', '`model`', '`run_in_background`')
DISPATCH_STDIN = ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/fix/SKILL.md')
def dispatch_missing(text, phrase): return phrase not in text
def claude_runsh_lines(text): return [l.strip() for l in text.splitlines() if 'run.sh' in l and 'Codex' not in l and 'codex' not in l]
_dc_texts = {rel: _rd(root/rel) for rel in DISPATCH_FILES}
for rel, text in _dc_texts.items():
    for ph in DISPATCH_PHRASES + (('on stdin',) if rel in DISPATCH_STDIN else ()):
        if dispatch_missing(text, ph): errors.append(f'{rel}: dispatch core missing "{ph}"')
        elif not dispatch_missing(text.replace(ph, ''), ph): errors.append(f'check.py: dispatch core negative control not flagged for {rel} without "{ph}"')
    errors.extend(f'{rel}: names run.sh outside a Codex line: {l[:80]}' for l in claude_runsh_lines(text))
    if not claude_runsh_lines(text + '\nRun `scripts/run.sh builder L1 x.md`.\n'): errors.append(f'check.py: dispatch core negative control not flagged for a Claude run.sh line in {rel}')
    if claude_runsh_lines(text + '\nOn Codex, run `SDLC_BACKEND=codex scripts/run.sh builder L1 x.md`.\n') != claude_runsh_lines(text): errors.append(f'check.py: dispatch core flagged a Codex run.sh line in {rel}')
# Record transcript flag (docstring item 41, T-0334): a skill that spells a `dispatch.py record` call with flags passes --transcript.
def record_flag_bad(text): return [l.strip()[:60] for l in text.splitlines() if 'dispatch.py record <dispatch_file> --' in l and '--transcript' not in l]
_rt_texts = {d.parent.name: _rd(d) for d in sorted((root/'skills').glob('*/SKILL.md'))}
for _n, _t in _rt_texts.items():
    errors.extend(f'skills/{_n}/SKILL.md: dispatch.py record spelled without --transcript: {m}' for m in record_flag_bad(_t))
if not record_flag_bad('Run `python3 x/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n>`.'): errors.append('check.py: record transcript negative control not flagged for a record call without --transcript')
if record_flag_bad('Run `python3 x/dispatch.py record <dispatch_file> --agent-id <id> --transcript <t>`.'): errors.append('check.py: record transcript flagged a call that passes --transcript')
# Self-contained skills (docstring item 42, T-0325): a skill reaches only its own folder and ${CLAUDE_PLUGIN_ROOT}; the other plugin's skills are checked when present.
PLUGIN_VAR = '${CLAUDE_PLUGIN_ROOT}'
def skill_ref_bad(text, md_dir, skill_dir, plugin_root, prose_rule=True):
    """Findings for one skill .md file: a link leaving the skill folder, a `plugins/` prose path, a dangling plugin-root path."""
    out = []
    for tg in re.findall(r'\]\(([^)\s]+)', re.sub(r'```.*?```', '', text, flags=re.S)):
        if '://' in tg or tg.startswith(('#', 'mailto:', PLUGIN_VAR + '/')): continue
        rel = tg.split('#')[0]
        if rel.startswith(('docs/', 'plugins/', '../', '/', '~')) or not (md_dir/rel).resolve().is_relative_to(skill_dir.resolve()):
            out.append(f'link leaves the skill folder: {tg}')
    if prose_rule:
        out.extend(f'prose path starts with plugins/: {m}' for m in re.findall(r'(?<![\w/.${}-])plugins/[\w./-]+', text))
    for m in re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`"\'<>()*$\[\]]+)', text):
        if not (plugin_root/m.rstrip('.,;:')).exists(): out.append(f'{PLUGIN_VAR}/{m} does not exist in the plugin')
    return out
_sc_roots = [root/'skills'] + ([root.parent/'progressive-context/skills'] if (root.parent/'progressive-context/skills').is_dir() and root.name == 'sdlc-lite' else [])
_sc_n = 0
for _sr in _sc_roots:
    for _sk in sorted(d for d in _sr.iterdir() if d.is_dir()):
        for _md in sorted(_sk.rglob('*.md')):
            _sc_n += 1
            _prose = _md.name == 'SKILL.md' and _md.parent == _sk or 'references' in _md.relative_to(_sk).parts
            errors.extend(f'{_md.relative_to(_sr.parent.parent)}: {m}' for m in skill_ref_bad(_md.read_text(), _md.parent, _sk, _sr.parent, _prose))
_sc_dir, _sc_pl = pathlib.Path('/x/pl/skills/demo'), pathlib.Path('/x/pl')
for _why, _bad in (('a ../ link', '[a](../sdlc-lite/SKILL.md)'), ('a ../../ link', '[a](../../agents/planner.md)'), ('a docs/ link', '[a](docs/x.md)'),
                   ('a plugins/ link', '[a](plugins/sdlc-lite/scripts/x.py)'), ('an absolute link', '[a](/etc/hosts)'),
                   ('an in-folder link that climbs out', '[a](references/../../other/x.md#h)'),
                   ('a plugins/ prose path', 'Run `python3 plugins/sdlc-lite/scripts/fanout.py run`.'),
                   ('a dangling plugin-root path', 'Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/no-such-script.py`.')):
    if not skill_ref_bad(_bad, _sc_dir, _sc_dir, _sc_pl): errors.append(f'check.py: self-contained skills negative control not flagged for {_why}')
for _ok in ('[a](references/x.md)', '[a](resources/y.json#k)', '[a](https://example.com/docs/x)', '[a](#top)', '[a](${CLAUDE_PLUGIN_ROOT}/agents/planner.md)',
            '```\n[a](../x.md)\n```', 'Read `${CLAUDE_PLUGIN_ROOT}/scripts/steps.py` and `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`.'):
    if skill_ref_bad(_ok, _sc_dir, _sc_dir, root): errors.append(f'check.py: self-contained skills flagged a clean reference: {_ok[:40]}')
if not _sc_n: errors.append('skills: no skill .md files found for the self-contained check')
# One level system (docstring item 43, T-0342): ticket and solo levels are L1 to L5; the retired S/M/L vocabulary stays out of
# the shipped texts. An `ALIAS_OK` line passes only in an ALIAS_FILES file (the deprecated aliases kept for one release).
RETIRED_VOCAB = (r'\b(?i:tiers?|sizes?|levels?) (?:S|M|L|XL)\b', r'\bsolo-(?:S|M|L)\b', r'\bS\|M\|L\b',
                 r'\bS, M,? (?:and |or )?L\b', r'\bS/M/L\b', r'\bS \$\d+, M \$')
ALIAS_FILES = ('hooks/block-role-spawn.sh', 'hooks/_role.sh', 'scripts/tickets.py', 'scripts/solo_run.py', 'scripts/claude_roles.py')
def retired_vocab_bad(rel, text):
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if 'ALIAS_OK' in line and rel in ALIAS_FILES: continue
        for rx in RETIRED_VOCAB:
            m = re.search(rx, line)
            if m: out.append(f'{rel}:{n}: retired S/M/L vocabulary "{m.group(0)}"; use the level L1 to L5'); break
    return out
_rv_files = [p for d in ('skills', 'agents', 'commands') if (root/d).is_dir() for p in sorted((root/d).rglob('*.md'))]
_rv_files += sorted(p for p in (root/'hooks').glob('*') if p.is_file()) + [root/'adapters/codex/instructions.md']
_rv_files += sorted((root/'adapters/codex/agents').glob('*.toml')) + [root/a for a in ALIAS_FILES if a.startswith('scripts/')]
for _p in _rv_files:
    if _p.is_file(): errors.extend(retired_vocab_bad(_p.relative_to(root).as_posix(), _p.read_text(encoding='utf-8', errors='replace')))
if len(_rv_files) < 30: errors.append(f'one level system: only {len(_rv_files)} files scanned; the scan roots moved')
for _why, _rel, _bad in (('a planted tier S line', 'agents/solo.md', 'Start at tier S.'), ('a planted solo-M name', 'skills/agent/SKILL.md', 'spawn sdlc-lite:solo-M'),
                         ('a planted size XL', 'adapters/codex/instructions.md', 'a size XL ticket'), ('a planted S/M/L list', 'agents/conductor.md', 'tiers are S/M/L'),
                         ('an ALIAS_OK line outside ALIAS_FILES', 'skills/fix/SKILL.md', 'solo-S still works  # ALIAS_OK'),
                         ('a planted budget list', 'skills/plan-fanout/SKILL.md', 'caps S $5, M $30, L $60')):
    if not retired_vocab_bad(_rel, 'clean line\n' + _bad + '\n'): errors.append(f'check.py: one level system negative control not flagged for {_why}')
if retired_vocab_bad('hooks/_role.sh', "re_solo='^(solo)-[SML]$'  # solo-S|M|L ALIAS_OK\n") or retired_vocab_bad('agents/solo.md', 'level L1, L2, L3; size L4; solo-L1\n'):
    errors.append('check.py: one level system flagged an allowed line')
# Generated-definition parity (T-0351): an agent source edited without regenerating fails here, not only in check.sh.
def regen_drift(plugin):
    out = []
    for script, name in (('codex_roles.py', 'Codex'), ('claude_roles.py', 'Claude')):
        r = subprocess.run([sys.executable, str(plugin/'scripts'/script), 'generate', '--check'], capture_output=True, text=True)
        if r.returncode: out.append(f'{name} generated agent definitions drift from their sources; run {script} generate: ' + (r.stdout + r.stderr).strip().splitlines()[-1:][0] if (r.stdout + r.stderr).strip() else f'{name} generated agent definitions drift; run {script} generate')
    return out
errors.extend(regen_drift(root))
_rg = pathlib.Path(tempfile.mkdtemp())
try:
    shutil.copytree(root, _rg/'p', ignore=shutil.ignore_patterns('.git', '__pycache__'))
    (_rg/'p'/'agents'/'conductor.md').write_text((_rg/'p'/'agents'/'conductor.md').read_text() + '\nplanted edit\n')
    if not regen_drift(_rg/'p'): errors.append('check.py: regenerate parity negative control not flagged for an edited agent source')
finally: shutil.rmtree(_rg, ignore_errors=True)
# Version-free entry point (docstring item 47, T-0401): a versioned cache path breaks a loop on the next plugin update.
VERSIONED_PATH = re.compile(r'sdlc-lite/[0-9]+\.[0-9]+')
def versioned_path_bad(rel, text): return [f'{rel}: names a versioned plugin cache folder "{m.group(0)}"; use a version-free entry point' for m in VERSIONED_PATH.finditer(text)][:1]
_vp_files = [p for d in ('skills', 'agents', 'commands', 'hooks') if (root/d).is_dir() for p in sorted((root/d).rglob('*')) if p.is_file()]
_vp_files += [root/'adapters/codex/instructions.md'] + sorted((root/'adapters/codex/agents').glob('*.toml'))
for _p in _vp_files:
    if _p.is_file(): errors.extend(versioned_path_bad(_p.relative_to(root).as_posix(), _p.read_text(encoding='utf-8', errors='replace')))
errors.extend(versioned_path_bad('scripts/messages.py entry text', mst))
if len(_vp_files) < 30: errors.append(f'version-free entry point: only {len(_vp_files)} files scanned; the scan roots moved')
for _why, _bad in (('a skill', 'run python3 ~/.claude/plugins/cache/x/sdlc-lite/0.22.0/scripts/messages.py'), ('an agent', 'path .../sdlc-lite/1.2.3/scripts/messages.py')):
    if not versioned_path_bad('skills/x/SKILL.md', 'clean\n' + _bad + '\n'): errors.append(f'check.py: version-free negative control not flagged for {_why}')
if versioned_path_bad('skills/x/SKILL.md', 'the folder sdlc-lite/<version>/scripts and ${CLAUDE_PLUGIN_ROOT}/scripts/messages.py\n'): errors.append('check.py: version-free guard flagged an allowed line')
# Level overlays (docstring item 52, T-0441): overlays/<role>.md only for a levels.json role, and nothing .md under an agents/ subdirectory.
def overlay_placement_bad(overlay_stems, roles, agent_paths):
    out = [f'overlays/{s}.md has no levels.json rows' for s in sorted(overlay_stems) if s not in roles]
    return out + [f'agents/{p}: an .md file in a subdirectory of agents/; overlays live in the top-level overlays/' for p in sorted(agent_paths) if '/' in p]
_ov_roles = {r for r, _ in levels} | ({'solo'} if solo_levels else set())
_ov_stems = {p.stem for p in (root/'overlays').glob('*.md')}
_ov_agents = {p.relative_to(root/'agents').as_posix() for p in (root/'agents').rglob('*.md')}
errors.extend(f'check.py: level overlays: {m}' for m in overlay_placement_bad(_ov_stems, _ov_roles, _ov_agents))
if not overlay_placement_bad(_ov_stems | {'ghost'}, _ov_roles, _ov_agents): errors.append('check.py: level overlays negative control not flagged for a planted overlays/ghost.md')
if not overlay_placement_bad(_ov_stems, _ov_roles, _ov_agents | {'overlays/x.md'}): errors.append('check.py: level overlays negative control not flagged for a planted agents/overlays/x.md')
if overlay_placement_bad({'builder'}, {'builder'}, {'builder.md'}): errors.append('check.py: level overlays guard flagged an allowed overlay')
# Prompt references (docstring item 53, T-0447): no P-1 to P-3 error in the prompt files; P-4 to P-6 are advisory.
import prompt_lint
PL_ERRORS = ('P-1', 'P-2', 'P-3')
def prompt_ref_bad(found): return [f.line() for f in found if f.level == 'error' and f.rule in PL_ERRORS]
_pl_ctx = prompt_lint.Ctx(root)
_pl_files = prompt_lint.default_files(root)
errors.extend(f'check.py: prompt references: {m}' for m in prompt_ref_bad(prompt_lint.lint_files(_pl_ctx, [(p, p.relative_to(root).as_posix()) for p in _pl_files])))
if len(_pl_files) < 30: errors.append(f'prompt references: only {len(_pl_files)} files scanned; the scan roots moved')
if 'prompt_lint.py" selftest' not in (root/'scripts/check.sh').read_text(): errors.append('scripts/check.sh: no prompt_lint.py selftest line')
for _why, _rel, _bad in (('an unresolved rule 99 cite in an overlay', 'overlays/builder.md', 'Follow rule 99.'),
                         ('an unknown --flag on a real script', 'skills/chain/SKILL.md', 'Run `steps.py next --no-such-flag`.'),
                         ('a bare scripts/coverage_check.py in an agent file', 'agents/architect.md', 'Run `scripts/coverage_check.py`.')):
    if not prompt_ref_bad(prompt_lint.lint_text(_pl_ctx, _rel, 'clean line\n' + _bad + '\n')): errors.append(f'check.py: prompt references negative control not flagged for {_why}')
# Report (docstring item 54, T-0460): the skill prints the renderer's output; the script owns the verbs and the record schema.
REPORT_NEEDS = (('skill', ('report.py render', 'Render, never compose', 'Codex host', 'Exit 2 is a refusal', 'references/views.md', 'references/record-schema.md')),
                ('script', ('VERBS', 'CollectorError', 'session-status/1', 'def selftest')), ('check.sh', ('report.py" selftest',)))
def report_bad(texts, entry):
    out = [f'{name} missing "{ph}"' for name, phrases in REPORT_NEEDS for ph in phrases if ph not in texts[name]]
    if re.search(r'harness:', texts['skill']): out.append('report SKILL.md references harness:')
    if '| report |' not in entry: out.append('skills/sdlc-lite/SKILL.md does not route to report')
    return out
_rp_texts = {'skill': _rd(root/'skills/report/SKILL.md'), 'script': _rd(root/'scripts/report.py'), 'check.sh': _rd(root/'scripts/check.sh')}
errors.extend(f'check.py: report: {m}' for m in report_bad(_rp_texts, _entry))
for _name, _phrases in REPORT_NEEDS:
    for _ph in _phrases:
        if not report_bad(dict(_rp_texts, **{_name: _rp_texts[_name].replace(_ph, '')}), _entry): errors.append(f'check.py: report negative control not flagged for {_name} without "{_ph}"')
if not report_bad(dict(_rp_texts, skill=_rp_texts['skill'] + ' harness:x'), _entry): errors.append('check.py: report negative control not flagged for a harness reference')
if not report_bad(_rp_texts, _entry.replace('| report |', '|')): errors.append('check.py: report negative control not flagged for a missing entry route')
# Planner probe-criteria handle (T-0498): agents/planner.md and its generated levels carry the handle and the rule line.
PLANNER_PROBE = ('Probe-criteria', 'can exit 0 on a correct tree')
for _rel in ('agents/planner.md', 'agents/planner-L1.md', 'agents/planner-L2.md', 'agents/planner-L3.md'):
    _f = root/_rel
    _text = _f.read_text() if _f.is_file() else ''
    errors.extend(f'check.py: planner probe: {_rel} missing "{ph}"' for ph in PLANNER_PROBE if ph not in _text)
    if all(ph in _text for ph in PLANNER_PROBE) and not [ph for ph in PLANNER_PROBE if ph not in _text.replace(PLANNER_PROBE[0], '')]:
        errors.append(f'check.py: planner probe negative control not flagged for {_rel}')
# Solo dependents and verbatim criteria (docstring item 55, T-0471): the two Loop rules and the report detect rule.
SOLO_RULES = (('agents/solo.md', ('Search-dependents', 'Run-verbatim', 'git grep', 'plan defect: scope misses', 'plan defect: <criterion>', 'results.py" solo-report', 'Regenerate:', 'Scan-diff:')),
              ('scripts/results.py', ('def solo_report_error', 'def criterion_spans')),
              ('agents/solo-L1.md', ('Search-dependents', 'Run-verbatim', 'Regenerate:', 'Scan-diff:')), ('agents/solo-L2.md', ('Search-dependents', 'Run-verbatim', 'Regenerate:', 'Scan-diff:')),
              ('agents/solo-L3.md', ('Search-dependents', 'Run-verbatim', 'Regenerate:', 'Scan-diff:')))
def solo_rules_bad(rel, text): return [f'{rel} missing "{ph}"' for r, phrases in SOLO_RULES if r == rel for ph in phrases if ph not in text]
for _rel, _phrases in SOLO_RULES:
    _f = root/_rel
    _text = _f.read_text() if _f.is_file() else ''
    errors.extend(f'check.py: solo rules: {m}' for m in solo_rules_bad(_rel, _text))
    if not solo_rules_bad(_rel, _text) and any(not solo_rules_bad(_rel, _text.replace(_ph, '')) for _ph in _phrases):
        errors.append(f'check.py: solo rules negative control not flagged for {_rel}')
_sp = ['python3 a.py check', 'python3 b.py selftest']
if results.solo_report_error('- `python3 a.py check` exit 0\n- `python3 b.py selftest` exit 0\nverify: needed\n', _sp) is not None: errors.append('check.py: solo report rule flags a complete report')
if results.solo_report_error('- `python3 a.py check` exit 0\nverify: needed\n', _sp) is None: errors.append('check.py: solo report negative control not flagged for a missing exit-code line')
# Verifier Notes handle (T-0511): agents/verifier.md and its generated levels carry the handle and the rule line.
VERIFIER_NOTES = ('Notes: a finding that no criterion names', '`## Notes`')
for _rel in ('agents/verifier.md', 'agents/verifier-L1.md', 'agents/verifier-L2.md', 'agents/verifier-L3.md'):
    _f = root/_rel
    _text = _f.read_text() if _f.is_file() else ''
    errors.extend(f'check.py: verifier notes: {_rel} missing "{ph}"' for ph in VERIFIER_NOTES if ph not in _text)
    if all(ph in _text for ph in VERIFIER_NOTES) and not [ph for ph in VERIFIER_NOTES if ph not in _text.replace(VERIFIER_NOTES[0], '')]:
        errors.append(f'check.py: verifier notes negative control not flagged for {_rel}')
# Verifier (parity) line (docstring item 59, T-0513): agents/verifier.md and its generated levels carry the per-property parity rule.
VERIFIER_PARITY = ('a `(parity)` criterion passes per named property', 'Read the real and the mockup image')
for _rel in ('agents/verifier.md', 'agents/verifier-L1.md', 'agents/verifier-L2.md', 'agents/verifier-L3.md'):
    _f = root/_rel
    _text = _f.read_text() if _f.is_file() else ''
    errors.extend(f'check.py: verifier parity: {_rel} missing "{ph}"' for ph in VERIFIER_PARITY if ph not in _text)
    if all(ph in _text for ph in VERIFIER_PARITY) and any(all(q in _text.replace(ph, '') for q in VERIFIER_PARITY) for ph in VERIFIER_PARITY):
        errors.append(f'check.py: verifier parity negative control not flagged for {_rel}')
# Merge ops (docstring item 56, T-0492): the conductor, the fanout skill and run-operations.md name the same merge commands and the same settle command.
MERGE_OPS_FILES = ('agents/conductor.md', 'skills/fanout/SKILL.md', 'skills/handoff-format/run-operations.md')
MERGE_OPS_PHRASES = ('fanout.py land <branch>', 'lanes.py sweep --apply', 'lanes.py list --stale', 'board.py --lanes', '--priority 1', 'Merge ops', 'merge-base --is-ancestor origin/main HEAD', 'gh pr checks <n> --watch --fail-fast')
SETTLE_RE = re.compile(r'fanout\.py settle <integration>(?: --forward)?')
def merge_ops_bad(texts):
    out = [f'{rel} missing "{ph}"' for rel, text in texts.items() for ph in MERGE_OPS_PHRASES if ph not in text and not (ph == 'Merge ops' and rel == 'skills/fanout/SKILL.md')]
    if '## Merge ops' not in texts.get('agents/conductor.md', ''): out.append('agents/conductor.md missing "## Merge ops"')
    m = SETTLE_RE.search(texts.get('agents/conductor.md', ''))
    canon = m.group(0) if m else ''
    if '--forward' not in canon: out.append('agents/conductor.md settle command lacks --forward')
    out.extend(f'{rel} settle command disagrees with the conductor ({canon or "none"})' for rel, text in texts.items() if canon not in text)
    return out
_mo_texts = {rel: _rd(root/rel) for rel in MERGE_OPS_FILES}
errors.extend(f'check.py: merge ops: {m}' for m in merge_ops_bad(_mo_texts))
for _rel in MERGE_OPS_FILES:
    for _ph in MERGE_OPS_PHRASES:
        if _ph in _mo_texts[_rel] and not (_ph == 'Merge ops' and _rel == 'skills/fanout/SKILL.md') and not merge_ops_bad(dict(_mo_texts, **{_rel: _mo_texts[_rel].replace(_ph, '')})): errors.append(f'check.py: merge ops negative control not flagged for {_rel} without {_ph}')
    if not merge_ops_bad(dict(_mo_texts, **{_rel: _mo_texts[_rel].replace('settle <integration> --forward', 'settle <integration>')})): errors.append(f'check.py: merge ops negative control not flagged for a settle command changed in {_rel}')
# Plan kinds (docstring item 57, T-0467): one plan skill routes five kinds to their references and prints a dry run before every block.
PLAN_KIND_REFS = tuple(f'references/{k}.md' for k in PLAN_KINDS)
PLAN_KIND_NEEDS = PLAN_NEEDS + ('|'.join(PLAN_KINDS), 'Dry run (<kind>)', 'references/plan-rules.md') + PLAN_KIND_REFS
PLAN_KIND_FILES = ('references/plan-rules.md',) + PLAN_KIND_REFS + ('evals/README.md',)
def plan_kinds_bad(texts):
    """Findings for {'skill': SKILL.md, 'entry': the entry skill, <file>: its text or '' when the file is missing}."""
    out = [f'skills/plan/SKILL.md missing "{ph}"' for ph in PLAN_KIND_NEEDS if ph not in texts['skill']]
    if re.search(r'harness:', texts['skill']): out.append('skills/plan/SKILL.md references harness:')
    out += [f'skills/plan/{f} is missing or empty' for f in PLAN_KIND_FILES if not texts.get(f)]
    if 'plan <kind>' not in texts['entry']: out.append('skills/sdlc-lite/SKILL.md does not route to plan <kind>')
    return out
_pk = dict({f: _rd(root/'skills/plan'/f) for f in PLAN_KIND_FILES}, skill=_rd(root/'skills/plan/SKILL.md'), entry=_entry)
errors.extend(f'check.py: plan kinds: {m}' for m in plan_kinds_bad(_pk))
for _ph in PLAN_KIND_NEEDS:
    if not plan_kinds_bad(dict(_pk, skill=_pk['skill'].replace(_ph, ''))): errors.append(f'check.py: plan kinds negative control not flagged for SKILL.md without "{_ph}"')
if not plan_kinds_bad(dict(_pk, skill=_pk['skill'] + ' harness:x')): errors.append('check.py: plan kinds negative control not flagged for a harness reference')
if not plan_kinds_bad(dict(_pk, entry=_pk['entry'].replace('plan <kind>', ''))): errors.append('check.py: plan kinds negative control not flagged for a missing entry route')
for _f in PLAN_KIND_FILES:
    if not plan_kinds_bad(dict(_pk, **{_f: ''})): errors.append(f'check.py: plan kinds negative control not flagged for a missing {_f}')
# Plan redirect stubs (docstring item 58, T-0468): the four retired plan names redirect to the plan skill for one release; ticket D deletes them and this item.
PLAN_STUB_KINDS = ('goal', 'campaign', 'doc', 'fanout')
def plan_stubs_bad(texts, refs=()):
    """Findings for {kind: its SKILL.md text or '' when missing}; refs names the stub folders that still hold a references/ folder."""
    out = []
    for k in PLAN_STUB_KINDS:
        t, f = texts.get(k, ''), f'skills/plan-{k}/SKILL.md'
        if not t: out.append(f'{f} is missing'); continue
        if len(t.splitlines()) >= 15: out.append(f'{f} has {len(t.splitlines())} lines, expected under 15')
        out += [f'{f} missing "{ph}"' for ph in (f'name: plan-{k}', f'plan {k}', '${CLAUDE_PLUGIN_ROOT}/skills/plan/SKILL.md', '${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md') if ph not in t]
        if not re.search(rf'^description: "Redirect: run `/sdlc-lite:plan {k}`; removed in the next minor\."$', t, re.M): out.append(f'{f} description is not the redirect line')
        if '## 1. Gather' in t: out.append(f'{f} regrew ## 1. Gather')
        if k in refs: out.append(f'skills/plan-{k}/references still exists')
    return out
_stubs = {k: _rd(root/f'skills/plan-{k}/SKILL.md') for k in PLAN_STUB_KINDS}
errors.extend(f'check.py: plan stubs: {m}' for m in plan_stubs_bad(_stubs, [k for k in PLAN_STUB_KINDS if (root/f'skills/plan-{k}/references').exists()]))
for _k in PLAN_STUB_KINDS:
    for _why, _mut in (('a regrown ## 1. Gather', _stubs[_k] + '\n## 1. Gather\n'), ('a missing kind token', _stubs[_k].replace(f'plan {_k}', 'plan x')),
                       ('a description without the redirect', _stubs[_k].replace('Redirect: run', 'Plan: run')), ('a missing plan path', _stubs[_k].replace('skills/plan/SKILL.md', 'skills/x.md')),
                       ('a missing Codex route', _stubs[_k].replace('skills/sdlc-lite/SKILL.md', 'skills/x.md')), ('15 lines', _stubs[_k] + '\n' * 15)):
        if not plan_stubs_bad(dict(_stubs, **{_k: _mut})): errors.append(f'check.py: plan stubs negative control not flagged for {_why} in plan-{_k}')
    if not plan_stubs_bad(dict(_stubs, **{_k: ''})): errors.append(f'check.py: plan stubs negative control not flagged for a missing plan-{_k} stub')
    if not plan_stubs_bad(_stubs, [_k]): errors.append(f'check.py: plan stubs negative control not flagged for a references folder in plan-{_k}')
# Argument hints (docstring item 60, T-0463): every argument-reading skill carries a hint in one grammar, an ## Arguments table, and flags that agree with its script.
HINT_SCRIPTS = {'ticket': 'scripts/tickets.py', 'board': 'scripts/board.py', 'report': 'scripts/report.py', 'fleet-status': 'scripts/fleet_status.py',
                'fanout': 'scripts/fanout.py', 'onboard': 'scripts/onboard.py', 'review-traces': 'scripts/traces.py', 'fleet-retro': 'scripts/fleet_collect.py'}
HINT_ALLOW = {
    # ticket: the skill passes --root itself; --light-gate and --untracked are prose in the tickets.py usage block, not tickets.py flags.
    'ticket': ('--root', '--light-gate', '--untracked'),
    # fanout: --main, --require-covered and --ticket belong to subcommands the skill does not route; the skill adds --dry-run itself for the preview run; the rest are internal to the driver and its gates.
    'fanout': ('--main', '--require-covered', '--ticket', '--dry-run', '--driver', '--no-gate-lock', '--gate-need', '--allow-empty-gate', '--allow-overlap', '--yes-many'),
    # board: the skill sets --waiting itself, passes --task from the <task> positional, and never passes --summary.
    'board': ('--waiting', '--task', '--summary'),
    # onboard: the skill runs `setup --dry-run` itself as the preview.
    'onboard': ('--dry-run',),
    # fleet-status: internal state, test and write switches the skill never passes for the user.
    'fleet-status': ('--fleet', '--state-dir', '--stop-line', '--active-minutes', '--no-gh', '--no-write'),
    # review-traces: flags that only the detect, clusters and context subcommands take, which the skill sets itself; the skill forwards only --lanes-dir and --max, never --out, --bench-dir, --load-series or --rerun-criteria.
    'review-traces': ('--repo', '--backend', '--codex-home', '--out', '--bench-dir', '--load-series', '--rerun-criteria'),
    # fleet-retro: the skill passes --gh itself and never passes --days or --du-timeout.
    'fleet-retro': ('--gh', '--days', '--du-timeout'),
}
HINT_REF_SKILLS = ('checking-rules', 'checks-that-bite', 'handoff-format', 'level-rubric')
HINT_STUBS = tuple(f'plan-{k}' for k in PLAN_STUB_KINDS)
HINT_MAX = 100
HINT_TABLE = '| Argument | Meaning | Default | Example |'
_H_LOWER = r'[a-z][a-z0-9-]*'
_H_NAME = r'<[a-z0-9.|-]+>'
_H_POS = re.compile(rf'{_H_NAME}(?:[=@]{_H_NAME})*(?:\.\.\.)?')
_H_FLAG = re.compile(rf'--{_H_LOWER}(?: [A-Za-z0-9][A-Za-z0-9_,.|=-]*(?=$|[ \]]))?')
_H_LEVEL = re.compile(r'L\d(?:\|L\d)*')
_H_WORD = re.compile(rf'{_H_LOWER}(?:\|{_H_LOWER})*(?:\.\.\.)?')
def hint_parses(s):
    """True when s is a hint of the grammar in docs/specs/doc-standards/prompts.md: forms split by ' | ', items by one space, a word only first in its form."""
    def item(i, first):
        if s.startswith('[options]', i): return i + 9
        if s.startswith('[', i):
            j = forms(i + 1)
            if j is None or not s.startswith(']', j): return None
            return j + 4 if s.startswith('...', j + 1) else j + 1
        for rx in (_H_POS, _H_FLAG, _H_LEVEL) + ((_H_WORD,) if first else ()):
            m = rx.match(s, i)
            if m: return m.end()
        return None
    def forms(i):
        while True:
            first = True
            while True:
                i = item(i, first)
                if i is None: return None
                first = False
                if i < len(s) and s[i] == ' ' and not s.startswith(' | ', i): i += 1; continue
                break
            if not s.startswith(' | ', i): return i
            i += 3
    return forms(0) == len(s)
def usage_block(src):
    """A script's usage text: its lines from the first `usage:` line up to, not including, the next blank line."""
    lines = src.split('\n')
    for n, l in enumerate(lines):
        if re.search(r'(?i)\busage:\s*($|\S+\.py)', l):
            end = next((k for k in range(n, len(lines)) if not lines[k].strip()), len(lines))
            return '\n'.join(lines[n:end])
    return ''
def hints_bad(skills, usage):
    """Findings for {skill name: SKILL.md text} and {script path: usage text}, each `skills/<name>/SKILL.md: H-<n> <text>`."""
    out = []
    for name in sorted(skills):
        t, f = skills[name], f'skills/{name}/SKILL.md'
        m = re.match(r'---\n(.*?)\n---\n', t, re.S)
        fm, body = (m.group(1), t[m.end():]) if m else ('', t)
        h = re.search(r'^argument-hint:[ \t]*(.*)$', fm, re.M)
        hint = h.group(1).strip() if h else None
        if hint and len(hint) > 1 and hint[0] == hint[-1] and hint[0] in '"\'': hint = hint[1:-1]
        if name in HINT_REF_SKILLS:
            if hint is not None: out.append(f'{f}: H-7 a reference skill carries an argument-hint')
            continue
        if not re.search(r'^Arguments: `\$ARGUMENTS`', t, re.M): continue
        if hint is None: out.append(f'{f}: H-1 reads $ARGUMENTS but has no argument-hint line')
        if name in HINT_STUBS: continue
        script = HINT_SCRIPTS.get(name)
        uflags = set(prompt_lint.FLAG.findall(usage.get(script, ''))) if script else set()
        hflags = set(prompt_lint.FLAG.findall(hint or ''))
        if hint is not None:
            if not hint_parses(hint): out.append(f'{f}: H-2 hint does not parse under the hint grammar: {hint}')
            if len(hint) > HINT_MAX: out.append(f'{f}: H-3 hint is {len(hint)} characters, at most {HINT_MAX}')
            bflags = set(prompt_lint.FLAG.findall(body))
            out += [f'{f}: H-4 hint flag {x} is not in the skill body' for x in sorted(hflags - bflags)]
            if script: out += [f'{f}: H-4 hint flag {x} is not in the usage text of {script}' for x in sorted(hflags - uflags)]
        heads = [n for n, l in enumerate(body.split('\n')) if l.rstrip() == '## Arguments']
        rows = []
        if heads:
            rest = [l for l in body.split('\n')[heads[0] + 1:]]
            while rest and not rest[0].strip(): rest.pop(0)
            for l in rest:
                if not l.startswith('|'): break
                rows.append(l.rstrip())
        if script:
            if not uflags: out.append(f'{f}: H-5 {script} has no usage text')
            tflags = set(prompt_lint.FLAG.findall('\n'.join(r.split('|')[1] for r in rows[1:]))) if '[options]' in (hint or '') else set()
            out += [f'{f}: H-5 usage flag {x} of {script} is not in the hint, the ## Arguments table under [options], or the allowlist'
                    for x in sorted(uflags - hflags - tflags - set(HINT_ALLOW.get(name, ())))]
        if len(heads) != 1: out.append(f'{f}: H-6 has {len(heads)} `## Arguments` headings, expected 1')
        elif not rows or rows[0] != HINT_TABLE: out.append(f'{f}: H-6 `## Arguments` is not followed by the row {HINT_TABLE}')
    return out
_hs = {p.parent.name: p.read_text() for p in sorted((root/'skills').glob('*/SKILL.md'))}
_hu = {s: usage_block(_rd(root/s)) for s in sorted(set(HINT_SCRIPTS.values()))}
_hb = hints_bad(_hs, _hu)
errors.extend(f'check.py: argument hints: {m}' for m in _hb)
def _hint_set(text, hint): return re.sub(r'(?m)^argument-hint:.*$', lambda _m: f'argument-hint: "{hint}"', text, count=1)
def _hint_new(skill, rule, text=None, usage=None):
    """One rule's findings on one skill of a mutant tree. The tree may be red, so a control never tests the whole result for empty: it mutates the clean reader below, or filters on a flag no real skill holds."""
    got = hints_bad(_hs if text is None else dict(_hs, **{skill: text}), _hu if usage is None else dict(_hu, **usage))
    return [m for m in got if m.startswith(f'skills/{skill}/SKILL.md: {rule} ')]
_HT = f'\n## Arguments\n\n{HINT_TABLE}\n|---|---|---|---|\n'
# A clean reader built from the real handoff skill: a parsing hint and one table. Each control below mutates it or the real report skill.
_hk = _hint_set(_hs['handoff'], '<goal>') + ('' if '## Arguments' in _hs['handoff'] else _HT + '| `<goal>` | The goal | none | `fix the login` |\n')
if [m for m in hints_bad(dict(_hs, handoff=_hk), _hu) if m.startswith('skills/handoff/SKILL.md: ')]: errors.append('check.py: argument hints positive control flagged: a clean reader')
for _ok in ('<agent> [--level L1|L2|L3] <instructions>', '[L1|L2|L3|L4|L5] <handoff.md>', '[view...] [--since T=last-report] [--last N=5] [--format text|md|json] [options]',
            '<lane>=<ids>... <lane>@<branch>=<ids>... [options]', '[setup [--force] | check]'):
    if not hint_parses(_ok) or [m for m in hints_bad(dict(_hs, handoff=_hint_set(_hk, _ok)), _hu) if m.startswith('skills/handoff/SKILL.md: H-2 ')]: errors.append(f'check.py: argument hints positive control flagged: {_ok}')
if not _hint_new('handoff', 'H-1', re.sub(r'(?m)^argument-hint:.*\n', '', _hk, count=1)): errors.append('check.py: argument hints negative control not flagged for H-1: a reader without its hint line')
for _why, _bad in (('braces', '{agent-name} [--level L1|L2|L3] {instructions}'), ('two dots', '[L1..L5] <handoff.md>'), ('free text', '[topic or task dir]'),
                   ('a space inside angle brackets', '<handoff.md | goal>'), ('an unbalanced bracket', '[task'), ('a double quote', 'new <slug> \\"title\\"')):
    if not _hint_new('handoff', 'H-2', _hint_set(_hk, _bad)): errors.append(f'check.py: argument hints negative control not flagged for H-2: {_why}')
if _hint_new('handoff', 'H-3', _hint_set(_hk, '<' + 'a' * (HINT_MAX - 2) + '>')): errors.append(f'check.py: argument hints positive control flagged: a hint of {HINT_MAX} characters')
if not _hint_new('handoff', 'H-3', _hint_set(_hk, '<' + 'a' * (HINT_MAX - 1) + '>')): errors.append('check.py: argument hints negative control not flagged for H-3: a hint of 101 characters')
if not [m for m in _hint_new('handoff', 'H-4', _hint_set(_hk, '<goal> [--zz-nope]')) if 'skill body' in m]: errors.append('check.py: argument hints negative control not flagged for H-4: a hint flag absent from the body')
if not [m for m in _hint_new('report', 'H-4', _hint_set(_hs['report'], '[view...] [--zz-nope]') + '\n`--zz-nope`\n') if 'usage text' in m]: errors.append('check.py: argument hints negative control not flagged for H-4: a hint flag absent from the mapped script')
_hx = {'scripts/report.py': _hu['scripts/report.py'] + ' [--zz-extra]'}
if not [m for m in _hint_new('report', 'H-5', usage=_hx) if '--zz-extra' in m]: errors.append('check.py: argument hints negative control not flagged for H-5: a usage text with one extra flag')
if [m for m in _hint_new('report', 'H-5', _hint_set(_hs['report'], '[view...] [options]').replace('## Arguments', '## Old') + _HT + '| `--zz-extra N` | An extra | none | `--zz-extra 1` |\n', _hx) if '--zz-extra' in m]:
    errors.append('check.py: argument hints positive control flagged: a usage flag carried by the ## Arguments table under [options]')
if not _hint_new('handoff', 'H-6', _hk.replace('## Arguments', '## Other')): errors.append('check.py: argument hints negative control not flagged for H-6: a reader without the heading')
if not _hint_new('handoff', 'H-6', _hk + _HT): errors.append('check.py: argument hints negative control not flagged for H-6: a reader with two headings')
if not _hint_new('handoff', 'H-6', _hk.replace(HINT_TABLE, '| Argument | Meaning |')): errors.append('check.py: argument hints negative control not flagged for H-6: a table with another header row')
if not _hint_new('checking-rules', 'H-7', _hs['checking-rules'].replace('---\n', '---\nargument-hint: "<x>"\n', 1)): errors.append('check.py: argument hints negative control not flagged for H-7: a reference skill with a hint')
for e in errors: print('FAIL', e)
print(f'{"FAIL" if errors else "ok"}: {len(run)} role levels, {len(agents)} agents, {len(GENERATED)} generated definitions checked')
sys.exit(1 if errors else 0)
