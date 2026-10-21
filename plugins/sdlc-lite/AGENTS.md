# SDLC Lite maintenance

Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction. Improvements serve [the four pillars](../../docs/specs/sdlc-lite/pillars.md): performance, cost, quality, resilience.

Read [repository guidance](../../AGENTS.md) first. Paths below are relative to this plugin unless a command starts with `plugins/`; those commands run from the repository root.

## Contracts and routing

- Ticket level L1 and L2 plugin work goes to `solo` by default; `/fix` only when the user asks for it or the lane script prints `fix`, and the lean lane when the lane script says so. Run the full chain only with a stated reason (an L4 or L5 step, a merge step, cross-cutting scope, a security-sensitive change) and record that reason in the ticket. See [the SDLC Lite design](../../docs/specs/sdlc-lite/design.md).
- Shared roles live in `agents/`; workflows and output contracts live in `skills/`. Keep callers and producers consistent when changing handoffs or verdicts.
- A skill is self-contained: what it needs to run (schemas, templates, rubrics, fixtures) ships in its own folder, and it names no repo-relative path outside it. Scripts and any file shared with another skill (the Codex adapter, `handoff-format/run-operations.md`, an agent file) are reached through `${CLAUDE_PLUGIN_ROOT}/...`, never `../` or `plugins/...`, and the consumer's own files (`.sdlc/`) are found by the script, not assumed by the skill text. `scripts/check.py` item 42 enforces it: a link that leaves its skill folder, a `plugins/` prose path, or a dangling plugin-root path fails.
- A skill that reads `$ARGUMENTS` carries an `argument-hint` in the hint grammar and one `## Arguments` table (Argument, Meaning, Default, Example); a reference skill carries no hint. The standard is [Skill arguments and questions](../../docs/specs/doc-standards/prompts.md#skill-arguments-and-questions), which also holds the `AskUserQuestion` rules. `scripts/check.py` item 60 enforces the hint rules H-1 to H-7, including flag agreement between a hint and the script the skill passes flags to.
- `agents/` also holds three session agents that are not `run.sh` roles, the `conductor`, the `messenger`, and `solo`. `scripts/check.py` excludes all three from the run.sh agreement check and checks the messenger's and solo's files and Codex mappings.
- Pipeline role execution goes through `scripts/run.sh` so required output sections, result files, and `runs.jsonl` remain authoritative. Direct native delegation alone does not advance pipeline state.
- `scripts/results.py` owns each role's result schema (key section, allowed first values, header, declared section order). `run.sh` and `steps.py` call it, `scripts/check.py` checks agent bodies against it, and no other file copies it.
- Claude dispatches roles as sub-agents (`scripts/dispatch.py`; design in [sub-agent mode](../../docs/planning/sdlc-lite/subagent-mode.md)); sub-agent mode is the Claude mode, and `run.sh` is the Codex runner. Its Claude branch is legacy for bench and CI: it exits 2 pointing to `dispatch.py prepare` unless `SDLC_CLAUDE_EXEC=1`. Codex supports standalone exec and native subagent exchange; read [Codex execution](../../docs/references/codex-role-execution.md) before changing that adapter.
- Claude models and efforts live in `adapters/claude/levels.json` (the `scripts/run.sh` `case` rows mirror it for the legacy Claude branch), with the consumer explanation in `skills/level-rubric/SKILL.md`. `scripts/check.py` checks the three against each other. Codex defaults live in `adapters/codex/models.json`. A change to either table needs a new eval in the work root's `evals/` (`roots.py paths --root .sdlc` prints it) and `scripts/evals.py lock`, else `scripts/check.py` fails; read [the evals entry file](../../docs/work/evals/AGENTS.md) first.
- After changing shared role bodies, preloaded skill bodies, Codex mappings, `overlays/<role>.md`, or the Codex prelude, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Preserve managed-agent install ownership checks.
- `agents/<role>-L<n>.md` and `agents/solo-L1|L2|L3.md` are generated, one per `levels.json` row, from the role file and the table: never edit one. After changing a role file, its skills list, `levels.json`, or `overlays/<role>.md`, run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate`; `generate --check` and `check.py` fail on a stale, hand-edited, or orphaned file.
- For runner, ticket, board, step, or fanout internals, read only the relevant entry in [the implementation reference](../../docs/references/sdlc-internals.md).
- For Claude hook registration, permissions, and background execution rules, read [hook maintenance](../../docs/references/claude-hooks.md). Do not apply Claude flags or permission bypasses to Codex.

## Behavioral invariants

- `scripts/order.py` owns newest-result ordering; never use file modification time.
- `scripts/steps.py` owns next-action decisions. Missing verdicts, inherited failures, plan defects, and implementation failures are distinct outcomes. Preserve the one-criterion verifier swap rules, the builder amend route (`steps.py amend`: one criterion of an unbuilt step, one per step, recorded as the task's one replan), and the recurring-finding replan route.
- Keep the merge-step template consistent across planner and handoff-format and with the builder's commit boundary. `scripts/check.py` validates these contracts.
- Checks must be able to fail. Preserve independent verification and the recorded build baseline (`SDLC_BASE_SHA`); scope criteria must account for relevant untracked work.
- Ticket changes must preserve cross-worktree ID uniqueness, reference-safe closure, and explicit follow-up selection. Read the ticket/file skills and associated tests before editing these behaviors.
- Preserve in-scope loose-end handling and the one-ticket follow-up cap; a new task is for work that is out of scope, large, or needs user input.
- Runner-created temporary worktrees use `SDLC_TMP_WORKTREES`; preserve owned cleanup and stray-worktree reporting. Where worktrees live is the Lanes section below.
- `scripts/supervisor.py` never claims, moves, or reads a message body; a wake it starts follows unattended-run rules (`SDLC_HEADLESS=1`, never push or publish).

## Lanes

Interim directive until the plugin ships its own sweep.

- Where: every worktree lives in the sibling root `<main checkout parent>/<repo>.worktrees/`, outside the repo on both hosts (`scripts/wtroot.py root`; its docstring is the rule). Lanes are `<root>/<lane>`, fanout lanes `<root>/fanout/<lane>`, role temp trees `<root>/tmp/<agent name>` (`$SDLC_TMP_WORKTREES` for run.sh), role scratch files under `$TMPDIR/sdlc-lite/`. A `worktree_root:` line in `.sdlc/config` overrides the root; a bare clone defaults to `<bare parent>/lanes`. No watcher or test exclusion is needed for it.
- Legacy: `<main checkout>/.claude/worktrees/` (0.23) and `<main checkout>/.worktrees/` (before 0.23.0) are read for one release; `scripts/migrate-worktrees.sh` moves them.
- Host-owned: Codex's `~/.codex/worktrees/*` and Claude Code's own `.claude/worktrees/agent-*` (`wtroot.host_owned`). `lanes.py sweep` and `dispatch.py` stray reports never list them for removal.
- Codex: `lanes.py open`, the solo and verifier runs in a lane, land and close write `.git` or the lane tree outside the checkout, so run them with full access, not the `workspace-write` sandbox. Each run folder holds an `.owner.json`; `lanes.py sweep` removes only a dead owner's folder past `lane_min_age_hours` and lists an unmarked one.
- Open: `fanout.py run` or `prep` opens a lane; the ticket is claimed with `status: claimed` and `claimed_by:`. `lanes.py open` commits the ticket's `branch:` and `worktree:` record on main only when main tracks no upstream; when it tracks one (a PR repo) it records nothing on main, so main stays level with origin (T-0609, `docs/references/sdlc-internals.md`). With `--into` an integration branch and no `--root`, the record and its commit go to the integration tree, not main (T-0680).
- Hosts in one repo (Claude Code, Codex, Pi; this bullet is the one home of the rule): claims and ticket ids are atomic through `refs/sdlc/claims/<id>` and `refs/sdlc/ids/<id>` (T-0588), which every worktree and host shares. One conductor per repo writes main: it opens lanes, lands, merges, closes, and commits. A worker writes only its own locked lane (T-0589) and commits nothing (Codex `workspace-write` cannot write `.git`); when its ticket is done it runs `lanes.py ready`, which pins the review sha and tells the conductor (T-0590). The verifier runs on a different model family from the worker. Pi works as a mailbox-driven worker (`messages.py`) until it has a backend.
- Close: after `fanout.py land` and `tickets.py close`, remove the lane worktree and branch once their content is on the default branch (ancestor, a MERGED PR whose head sha equals the tip, or every changed file equal).
- Before removal keep the branch reachable as `refs/archive/<date>/<branch>` and archive its untracked records.
- Never delete unmerged work. A locked worktree (`git worktree lock`) is a running lane: skip it.
- Names for new work: `lane/<ticket>-<slug>`, `wave/<N>`, `release/<X.Y.Z>`, annotated tags `vX.Y.Z`. Existing branches keep their names.
- Until the sweep ships, the maintainer's tool `~/.claude/lane/sweep.py` does the removal; it is a dry run by default.

## Verification

Use the root validation matrix. Useful focused checks, run from the repository root:

- Role/skill contracts: `python3 plugins/sdlc-lite/scripts/check.py`.
- Generated agents: `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` (and `claude_roles.py selftest`).
- Sub-agent dispatch (`prepare`, the pre-launch half of `run.sh`, and `record`, the validate-and-record half): `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`; a gate or `runs.jsonl` change in `run.sh` needs the same change in `dispatch.py`, which the parity cases compare.
- Codex adapter: `python3 plugins/sdlc-lite/scripts/codex-selftest.py`.
- Tickets, board, steps, ordering, fanout: the affected `plugins/sdlc-lite/scripts/<name>.py selftest`.
- Evals and the model-table lock: `python3 plugins/sdlc-lite/scripts/evals.py check` (and `selftest`).
- Proposals mined from runs: `python3 plugins/sdlc-lite/scripts/proposals.py selftest`; read [the proposals entry file](../../docs/work/proposals/AGENTS.md) before scan, accept, reject, or promote.
- Prompt references in agents, skills, and overlays: `python3 plugins/sdlc-lite/scripts/prompt_lint.py` (and `selftest`).
- Thread report: `python3 plugins/sdlc-lite/scripts/report.py selftest`.
- Author reply rules scored over a session transcript: `python3 plugins/sdlc-lite/scripts/reply_lint.py score <transcript.jsonl>` (and `selftest`).
- Docs-only verifier skip and the tests-gate pilot: `python3 plugins/sdlc-lite/scripts/verify_scope.py selftest` (its `tests-gate ok:` and `tests-gate red:` cases, and the `(docs-only)` and `(tests-gate)` cases of `tickets.py selftest`).
- Runner: `bash plugins/sdlc-lite/scripts/run-selftest.sh`.
- Hooks: commands in the hook maintenance reference.
- Full regression suite: `bash plugins/sdlc-lite/scripts/check.sh` (jobs run in parallel; the land gate). Quick tier for builders and CI: `bash plugins/sdlc-lite/scripts/check.sh --fast`.

A role behavior change needs a focused live run on a throwaway project. Benchmark fixtures must expose all names and constraints pinned by hidden checks and demonstrate both failure and success. If a verifier passes while a hidden check fails, resolve the discrepancy before tuning models.
Raw transcripts and benchmark logs are ignored. A ticket's committed record is its `handoff.md` with the `## Outcome` close writes; role results and run records stay local in the records dir (`.sdlc/runtime/tasks/<folder>/`), so promote a result worth keeping to `docs/` before the close. Dated reports in `docs/reports/` are for releases and retros. Keep dated validation evidence separate from current instructions.

Readiness and run ownership live in `scripts/readiness.py` and `scripts/run_lifecycle.py`. Preserve failure evidence and handoff-directory exclusion for both backends. Run `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` after changes to routing records, cancellation, or recovery; it includes negative readiness and duplicate-launch controls. Runtime `completed` status means a valid report was delivered, not that a task or verification passed.
