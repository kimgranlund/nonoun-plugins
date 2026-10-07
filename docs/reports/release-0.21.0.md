# Release 0.21.0

Recorded: 2026-10-06. SDLC Lite 0.21.0, the sub-agent execution mode for the Claude host. Previous release: SDLC Lite 0.20.12 (tag `v0.20.12`). Progressive Context is unchanged in content: `git diff v0.20.12 HEAD -- plugins/progressive-context` shows one changed line in `HARNESS-NOTES.md`, a link path updated by the docs migration on main, and nothing else, so its version is not bumped. Built from main commit d68320d7 plus a merge of the branch `subagent-w7` (head 1ea5b317; merge base e531d096) as commit 1b694d97 on the branch `release-0.21.0`. The release commit adds the version bump in the two `plugin.json` files, link repairs, this record and its docs index edits. The release is not tagged, pushed or published by this commit.

This record states only what a committed file or a command run for it shows. Where a record does not say something, it says so.

Headless `claude -p` is not retired. T-0288 (retire the Claude headless path) is open and is not part of this release, and T-0287 (live evidence, including an account switch) is still open although its fix 08bf3599 and evidence ship in this merge: `run.sh`'s Claude branch, `solo_run.py --exec` and fanout's headless conductor still work and remain the fallback.

## What changed for consumers

Sub-agent mode is now the Claude execution mode: a conductor session dispatches each role as an in-session sub-agent instead of a `claude -p` child, so a role no longer dies with a headless owner process. Codex keeps its native exchange and its `run.sh` runner.

| Change | Ticket |
|---|---|
| Probes of the sub-agent mechanics the design assumed, recorded in `docs/reports/subagent-probes-2026-10-06.md` | T-0275 |
| `adapters/claude/levels.json` is the Claude level table; `scripts/claude_roles.py generate` writes one definition per row (`agents/<role>-L<n>.md`, 19 pipeline rows, and `agents/solo-S.md`, `solo-M.md`, `solo-L.md`), 22 generated files, never hand-edited; `check.py` compares `levels.json`, the `run.sh` rows and the level rubric three ways | T-0276 |
| `scripts/dispatch.py prepare`: the pre-launch half of `run.sh` as code (row lookup, preflight, verifier and plan-reviewer family rules, goal precheck, lane gate, spec gate, budget gate, attempt lock) printing a dispatch JSON the conductor passes to the Agent tool | T-0277 |
| `dispatch.py record`: validates the result with `results.py`, writes the header and the `runs.jsonl` line (`transport: subagent`, `agent_id`), completes the attempt | T-0278 |
| `dispatch.py status`, `recover`, `resume`: an attempt whose owning parent pid is dead shows `orphaned`; `resume` prints the ladder (SendMessage by name, by id, then a new attempt) | T-0279 |
| `scripts/cost_estimate.py` and `adapters/claude/prices.json`: estimated cost for sub-agent runs from tokens (`cost_estimated: true`), so the budget gate has a meter | T-0280 |
| Hooks resolve the role from `agent_type` through `hooks/_role.sh` when `SDLC_ROLE` is unset; `block-role-spawn.sh` becomes a spawn gate that allows only `sdlc-lite:<role>-L<n>` (and, after T-0287's fix, `solo-S/M/L`) on a matching dispatch record and model | T-0281 |
| Conductor, chain and the launcher skills dispatch roles as sub-agents (prepare, Agent spawn, record); `run.sh` is named only for Codex in those texts (check.py guard 40) | T-0282, T-0283 |
| Solo and its verifier run as sub-agents (`solo_run.py` prints the dispatch JSON; `--exec` keeps the headless path; the dispatch record and `Handoff:` line came with the T-0287 fix 08bf3599) | T-0284 |
| Fanout: `fanout.py prep` prints a dispatch table, lanes are isolated background `solo-S/M/L` sub-agents, `fanout.py land` merges behind the gate | T-0285 |
| `supervisor.py` lists orphaned dispatches in `status.json` (read-only; it still never claims or reads a message) | T-0286 |
| Fixes from the live runs: `prep` lane spawns pass the gate (T-0326), `land` recognizes the host-named `worktree-agent-<id>` branch (T-0327), cost estimate repriced and solo rows priced (T-0328), verifier `Tree:` is the lane worktree (T-0329), the verifier report is on disk before `record` (T-0330), a transcript-priced cost with a fitted `usage_calibration` and fanout solo rows priced at `land` (T-0331), the last usage line per message id and the calibration refit to input 225 and output 1.27 (T-0332) | T-0326 to T-0332 |

Repository maintenance, not shipped to consumers: `check.py` guards 39 (generated Claude definitions) and 40 (dispatch core), the selftest lines in `check.sh`, `docs/planning/sdlc-lite/subagent-mode.md`, `docs/reports/subagent-probes-2026-10-06.md`, `docs/reports/subagent-mode-live-2026-10-07.md` and its record folder, and the ticket records.

## Upgrade notes

- On Claude, run roles through `dispatch.py prepare <role> <level> <handoff.md>`, an Agent call with exactly the printed JSON, then `dispatch.py record <stem>.dispatch.json --transcript <jsonl>` with the sub-agent's final message on stdin (conductor and chain texts say this). A spawn that does not match a dispatch record is denied by the hook.
- The plugin now ships 22 generated agent definitions under `agents/`; a consumer that pins agent names sees `sdlc-lite:<role>-L<n>` and `sdlc-lite:solo-S|M|L`. A level table change is made in `adapters/claude/levels.json` and `claude_roles.py generate`.
- Cost for sub-agent rows is an estimate (`cost_estimated: true`, `cost_basis`), not the measured `total_cost_usd`; `budget.py` counts it. See Known limitations for its accuracy.
- Headless fallback: `SDLC_BACKEND=claude run.sh <role> <level> <handoff.md>`, `solo_run.py run --exec`, and a headless fanout conductor still run as before. T-0288 will remove them; this release does not.
- `check.py` guard numbers: main already had guard 38 (reorganization apply), so the two sub-agent guards are renumbered 39 and 40.

## Merge notes

- `subagent-w7` merged into main d68320d7 with these conflicts. `.sdlc/AGENTS.md` (generated): ours, then `tickets.py roadmap` regenerated it and `.sdlc/roadmap.md`; the four `.sdlc/messages/**/AGENTS.md` files were rewritten with this worktree's path by that run and restored to ours. `.sdlc/0281-hooks-agent-role/handoff.md`: deleted on the branch (the ticket closed and moved to `.0281-hooks-agent-role/`), modified on main by the docs migration; the deletion was taken.
- `docs/references/claude-hooks.md`: kept both intents, the branch's `_role.sh` role resolution and sub-agent tmp prefix plus main's rule that a path with any other variable, `~` or a glob is denied (T-0267). `plugins/sdlc-lite/AGENTS.md`: kept the branch's `levels.json` and generated-definition lines with main's `docs/references/` paths. `agents/conductor.md`: kept the branch's dispatch wording for plan review and main's `--override-review` clause.
- `scripts/check.py`: both sides added guard 38; the reorganization guard keeps 38, the generated-definitions guard became 39 and the dispatch-core guard 40 (docstring entries and their `docstring item N` comments). `check.sh` auto-merged with both sides' selftest lines. The Codex agent TOMLs (conductor L1, planner L1 to L3) conflicted and were regenerated with `codex_roles.py generate`; `claude_roles.py generate` rewrote three Claude definitions.
- Defects fixed after the merge: three links (one in `claude-hooks.md`, two in `sdlc-internals.md`) to `../sdlc-lite/subagent-mode.md` pointed at the pre-migration path and now point at `../planning/sdlc-lite/subagent-mode.md`; the `check.py` broken-link guard flagged them in a local run after the merge. `docs/references/sdlc-internals.md` said `check.py` item 38 where the generated-definitions guard is now 39. The design doc's opening line said "nothing here is built" and now states what shipped and that T-0288 is open; the docs index entry was updated the same way. Neither marketplace file carries a version field, so no version was written there. The Claude marketplace description of SDLC Lite said "run headless" and now says sub-agents on Claude and natively on Codex.
- The release commit also edits two files not named above: `plugins/sdlc-lite/AGENTS.md` (the line "Claude uses headless role processes" now says roles are dispatched as sub-agents through `scripts/dispatch.py`, with `claude -p` kept as a fallback until T-0288) and the header comment of `plugins/sdlc-lite/hooks/block-role-spawn.sh` (it now allows `solo-S|M|L`).

## Verification

Independent L3 verifier verdicts found in the closed ticket folders (`.sdlc/.NNNN-*`), at their own build commits and not on this merged tree: T-0276, T-0277, T-0278, T-0281, T-0282, T-0283 and T-0285 each have a `verifier-L3.md` with verdict pass. T-0275, T-0279, T-0280, T-0284, T-0286 and T-0326 to T-0332 have no verifier verdict file in the tree. T-0326 to T-0332 were exercised by the live reruns instead (below).

Live evidence is `docs/reports/subagent-mode-live-2026-10-07.md` with raw records in `docs/reports/subagent-mode-live-2026-10-07/`. Host: Claude Code 2.1.292, headless conductor (`claude -p --agent sdlc-lite:conductor`, `SDLC_HEADLESS=1`), throwaway projects under `/tmp`, foreground sub-agents. It records:

- Observed working: conductor, `prepare`, the Agent spawn gate, a sub-agent and `record` end to end for planner, builder and verifier; solo S through the generated `solo-S` definition; two-lane fanout with isolated worktrees running side by side and a gate-checked merge; the verifier on a different model family than the build (sonnet to opus, sonnet to fable), confirmed from the transcript model fields; hooks firing for sub-agent calls with `agent_type`.
- Failures found and their fixes: the spawn gate refusing solo (T-0287 fix, commit 08bf3599), `prep` lane spawns (T-0326), `land` misreading host branches (T-0327), the cost estimate (T-0328, T-0331, T-0332), the verifier `Tree:` (T-0329) and the missing verifier report (T-0330). The final rerun (runs F and G) records T-0329, T-0330 and the `land` close as fixed on a size M lane with a verifier, nothing closed by hand; run G records the cost as fixed after T-0332 (verifier 0.74 of the host figure, solo rows 1.07 to 1.10, solo host shares derived, not host-reported). The solo gate and `prep` fixes were observed in the earlier runs (L1b, R1, R2). The live report's own summary line gives 0.75 for the G verifier where its table gives 0.74.

Not exercised, so UNVERIFIED:

- An account switch spanning a run. The coordinator's session switched accounts between two runs, and later runs worked on the new account, but no run was in flight at the switch.
- The resume ladder: no run needed `dispatch.py resume`, so no rung was observed live.
- Interactive background sub-agents (`run_in_background: true`) and the completion-notification path; the live runs were headless and foreground.
- Behavior at a session limit, a parent exit with sub-agents running, nested lane conductors, and a lane whose spawn fails on a missing model.
- Codex: no live Codex run of any of this. The Codex agents were regenerated with `codex_roles.py generate`.
- The estimate calibration rests on three fitted rows from one host build; one earlier verifier row stays outside the 35 percent band.

Checks run for the release (the full `check.sh` run, `check-packaging.py` and `codex_roles.py generate --check` on a `git archive` copy under `/tmp` with no `claude` in the path, and a detached fact-check) are stated in the hand-off report; no committed file records them and their logs are not committed.

## Known limitations

- T-0288 is open: `claude -p` stays as a fallback, and `run.sh`'s Claude branch, `solo_run.py --exec` and the headless fanout conductor are not retired. The design's `SDLC_CLAUDE_EXEC=1` gate is not implemented.
- Estimated cost is approximate. The notice's `subagent_tokens` undercounts, so the estimate uses transcript usage with a fitted `usage_calibration` (input x225, output x1.27), whose input factor is empirical and unexplained. A solo row exists only on the fanout path and the `solo_run.py` path; the live report lists the rows that stayed unpriced before T-0328.
- The spawn-gate and per-sub-agent tmp-prefix hook rule is weaker than the per-run prefix: parallel sub-agents share `.worktrees/tmp/` (`docs/references/claude-hooks.md`).
- The live report's earlier sections describe the state before each fix; its last section is the final rerun.
