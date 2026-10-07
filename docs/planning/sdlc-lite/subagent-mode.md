---
status: proposed
---
# Sub-agent execution mode (Claude host)

Version 0.1, 2026-10-06. Built in SDLC Lite 0.21.0 except T-0288 (retiring the Claude headless path), which is open, so `claude -p` and `run.sh`'s Claude branch remain as a fallback; sections below that say "becomes" or "is retired" describe the end state, not the shipped one ([release record](../../reports/2026-10-06-release-0-21-0.md)). Tickets T-0275 to T-0288. The user decided (binding): one execution mode for every multi-agent session on the Claude host, and it is in-session sub-agents, because execution must survive account switches (`/login`). `claude -p` children are retired from the pipeline. Codex keeps its native exchange.

## Evidence and the decision

- In-session sub-agents (Agent tool, background, named, resumable with `SendMessage`) survived repeated `/login` switches in this maintenance session.
- `run_lifecycle.py` marks an attempt `interrupted` when the owner lock is released with no terminal record (`recover_unlocked`, lines 39 to 52), and `run.sh` runs the role as a `claude -p` child of that owner (`run.sh:542`). A switch that kills the owner kills the role.
- A canary at `/tmp/canary` (detached and attached `claude -p`, heartbeats in `*.beat`) was still beating at 05:23:44 when this was written; it had not yet seen a switch. Its result is a footnote to the decision, not an input.

## Spawn contract

Status tags: CONFIRMED (host documentation), OBSERVED (this author session), UNVERIFIED (a probe ticket owns it).

```
Agent({description, prompt, subagent_type: "sdlc-lite:solo-L2", model: "sonnet"|"opus"|"haiku"|"fable",
       name: "<ticket>-solo", isolation: "worktree", run_in_background: true})
```

| Fact | Status |
|---|---|
| Those parameters exist; there is no `effort`, `tools`, `cwd`, or permission parameter, so effort and tools come only from the definition frontmatter | OBSERVED (schema) |
| `run_in_background` is an explicit parameter here; the research claim that background is the default does not match, so the conductor always sets it explicitly | OBSERVED |
| Definition frontmatter holds `model`, `effort` (low, medium, high, xhigh, max), `tools`, `disallowedTools`, `maxTurns`, `permissionMode`, `isolation`, `background`, `skills`, `hooks`, `memory`; whether a plugin-shipped agent may set `permissionMode` and `hooks` | CONFIRMED for the list; plugin limits UNVERIFIED (P1) |
| Model resolution: per-call `model`, then definition `model`, then env `CLAUDE_CODE_SUBAGENT_MODEL`, then the parent's. The conductor always passes `model`, so the env var cannot change a tier | CONFIRMED |
| `SendMessage({to: "<name or agentId>", message})` resumes a finished or stopped sub-agent from its transcript with context kept | OBSERVED repeatedly; cross-session UNVERIFIED (P4) |
| Limits: 20 concurrent (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), spawn depth 3 (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`); refusal text `Concurrent subagent limit reached`; whether the count is per session or global | limits CONFIRMED; scope UNVERIFIED (P7) |
| PreToolUse on `Agent` receives `tool_input.subagent_type`, `description`, `prompt`, `model`, `run_in_background`, `isolation` and can deny with exit 2; `permissions.deny/allow` accept `Agent(<type>)`; `SubagentStop` input carries `agent_id`, `agent_type`, `effort`; `SubagentStart` cannot block | CONFIRMED |
| A hook cannot rewrite tool input, so the gate can deny but not correct a `model` | UNVERIFIED (P2) |
| The completion notification gives `subagent_tokens`, `tool_uses`, `duration_ms`, and no cost | OBSERVED |
| `isolation: worktree` creates `.claude/worktrees/<name>` on branch `worktree-<name>`, removed if empty, kept if changed; the result gives path and branch; the parent merges | CONFIRMED; result fields OBSERVED |
| Account switch: docs are silent; sub-agents survived repeated `/login`, `claude -p` children were marked interrupted | OBSERVED |
| Behavior at a session limit; whether a parent restart loses background sub-agents | UNVERIFIED (P7, P4) |

Consequences. Solo levels L1, L2, L3 (Sonnet low, Sonnet xhigh, Opus xhigh) need three definitions, `solo-L1`, `solo-L2`, `solo-L3`, or one definition with a fixed effort and a per-call model; two levels share `xhigh`, so a per-effort pair (`low`, `xhigh`) would do for solo, but the design uses per-level definitions everywhere (section 1) so `check.py` compares rows one to one. Sub-agents inherit the parent's environment, so `SDLC_ROLE` and `SDLC_TMP_WORKTREES` stop being per-role facts, and the hooks resolve the role from `agent_type` (section 4).

## 1. Dispatch contract

The conductor spawns every role the same three-step way. The first and third steps are scripts, so the gates and records of `run.sh` survive as code.

1. `dispatch.py prepare <role> <level> <handoff>` runs the pre-launch half of `run.sh`: goal precheck, lane gate, specgate, budget gate, the family rules, result naming (`-k`), base sha, tmp prefix, and the attempt record. It prints a dispatch JSON and writes `<name>.dispatch.json` beside the handoff.
2. The conductor calls `Agent` with exactly that JSON: `subagent_type: sdlc-lite:<role>-L<n>`, `name: <role>-L<n>-<slug>[-<k>]`, `model`, `prompt`, background. The prompt is the `run.sh` prompt (Handoff path, Artifacts dir, result path, output-format sentence) plus the tree and tmp-prefix lines. The handoff file is the brief; nothing is forked.
3. When the agent reports, `dispatch.py record <name>.dispatch.json` validates and records (section 3).

Forks. A full-context fork needs a stated reason (`Fork reason:` first line of the prompt) and is never allowed for `verifier` or `plan-reviewer`, because a fork inherits the parent's context and model and cannot be independent. The hook enforces it (section 4).

Level to model and effort. `model` is a per-call override; `effort` is fixed by the definition. So the level table gets one generated definition per `role:level` row, `sdlc-lite:builder-L3` and so on (19 rows plus `solo-L1`, `solo-L2`, `solo-L3`), each the role body of `agents/<role>.md` verbatim plus frontmatter `model`, `effort`, `disallowedTools`, `skills`. Per-effort definitions would be 13 files instead of 22, but per-level maps one to one onto the `run.sh` and level-rubric rows, makes the level readable in the agent name and the record, and keeps the agreement check a plain row comparison. The verifier family remap changes only the `model` argument, never the definition, so it adds no definitions.

Table home. The `role:level` rows move from the `run.sh` `case` to `adapters/claude/levels.json`, mirroring `adapters/codex/models.json`; `scripts/claude_roles.py generate|--check` writes the definitions (the `codex_roles.py` pattern). Values do not change (user decision). `evals.py canonical_table` must keep producing the same text so `evals.py hash` and `table-lock.json` stay valid; the ticket's acceptance proves the hash is unchanged.

`check.py` changes, each with a negative control:

| Item | Today | Becomes |
|---|---|---|
| 1 level tables | `run.sh` regex vs level-rubric rows | `levels.json` vs `run.sh` vs level-rubric, three ways; any one source edited fails |
| 2 role files | every `agents/<role>.md` has a `run.sh` case | every role has `levels.json` rows; `run.sh` case required only until run.sh's Claude branch is retired |
| 15 evals lock | table read from `run.sh` | table read from `levels.json`, hash unchanged |
| 18, 24, 27 solo levels | `solo.md`, `fanout.SOLO_TIERS`, `solo_run.py` | also the generated `solo-L1`, `solo-L2`, `solo-L3` |
| new | none | `claude_roles.py generate --check`: a hand edit to a generated file, or a `levels.json` change without regeneration, fails |

Skills. Today `run.sh` appends each declared skill with `--append-system-prompt-file` because `claude --agent` does not preload them (`sdlc-internals.md`, token probe 2026-09-24). A sub-agent definition's `skills:` frontmatter is the documented route; unverified for plugin-shipped agents (probe P1).

## 2. Verifier independence

The rule is unchanged and moves into `prepare`: a verifier never runs on the build's model family (Fable or Sonnet build, Opus verifier at the same effort), and a plan-reviewer never on the planner's (Opus planner, Fable reviewer). `prepare` reads `model=` from the newest builder or planner result header by `order.py`, exactly as `run.sh:213-252` does, and writes the answer into the dispatch JSON. The conductor passes it as the Agent `model` parameter.

What now carries the guarantee, in order of strength:

- Dispatch record: `prepare` decides the model and the hook requires the spawn's `model` to equal the dispatch (section 4), so the conductor cannot downgrade a verifier.
- Header: `record` writes `<!-- role=.. level=.. model=.. effort=.. -->` from the dispatch, so later family rules and `steps.py` read it as today.
- Observed model: the sub-agent transcript carries a model per message, if probe P5 confirms it; `record` then cross-checks the dispatched model. Until P5, the evidence is the dispatch, which says what was requested, not what ran. Say so in reports.

Unverified: the `haiku`, `sonnet`, `opus`, and `fable` aliases resolve to the models the pinned table assumes (scout is pinned to `claude-haiku-4-5` today). The alias mapping is checked in P1.

## 3. Results and records

Who validates. `dispatch.py record` calls `results.py validate --role <role>` (the one schema) and exits 3 on a defect with the file kept, as `run.sh` does (`run.sh:590-595`). `steps.py` and `order.py` need no change because the result file, the header, and the `runs.jsonl` line keep their shape.

Where the text comes from. The Agent result reaches the parent's context, but copying a 20 KB planner plan through the conductor is costly and not verbatim. So a role writes its own result file with Write to the path in its brief; the hook allows a read-only role to Write only that path (section 4). `record` reads that file. If probe P2 fails, the fallback is `record --stdin` with the conductor piping the final message.

The record. `record` writes the result with its header, one `runs.jsonl` line with the same key set as `run.sh` plus `transport: subagent` and `agent_id`, completes `<name>.attempt.json`, reports a changed handoff sha256, reports strayed worktrees and branches, removes the tmp prefix, and on a 429 or session-limit text writes `<role>-<level>.limit` with the resume command. The directory lock of `run_lifecycle.py` is replaced by `prepare` refusing a second running attempt on a handoff dir.

Cost. The sub-agent usage block gives tokens (and, per probe P3, tool uses and duration), not `total_cost_usd`. Precisely lost: `cost_usd` as measured, the input/output/cache split, `num_turns`, and a per-model split inside a run. `budget.py` sums `cost_usd` and counts null as unmetered, so with no replacement every sub-agent run is unmetered and the 80 percent gate (`run.sh:322-330`, `solo_run.py budget_hold`) never fires. That is the worst silent loss.

Cheapest honest replacement: `cost_usd = tokens x blended USD per million tokens for the dispatched model`, from `adapters/claude/prices.json`, written with `cost_estimated: true` and `cost_basis`. The rate is calibrated on existing `runs.jsonl` lines, which hold both `usage` and a real `cost_usd`, and the selftest fails when the estimate is off by more than 35 percent in aggregate per model. If probe P5 shows per-message usage in the transcript, `record` prices the cache and output tokens separately and the basis changes to `transcript usage x price`. `budget.py` counts estimated cost and prints the estimated share, `board.py` prefixes `~`, and a missing usage block records null with a `cost_reason`, never zero. The 80 percent rule and tiers do not change; only the meter is approximate, and it says so.

## 4. Hooks

`block-role-spawn.sh` today denies a conductor Agent spawn of any `sdlc-lite:` agent, so it is the one thing that stops the flip. Two changes, in one ticket (T-0281), landing before the conductor text changes.

Spawn gate. For a conductor session the hook becomes an allow gate: it allows an Agent call only when `subagent_type` is `sdlc-lite:<role>-L<n>`, `name` matches `<role>-L<n>-<slug>[-<k>]`, a `<name>.dispatch.json` exists next to the handoff named in the prompt (so `prepare` and every gate ran), and `model` equals the dispatch model (so independence cannot be downgraded). It denies `fork` for `verifier-*` and `plan-reviewer-*` names, and any other fork without a `Fork reason:` line. Other plugins' builder, verifier, reviewer, planner, and checker agents stay denied; read-only helpers pass, as today.

Role resolution. The role hooks (`block-publish`, `block-pattern-kill`, `block-stray-worktree`, `block-repo-format`, `block-disk-scan`) read `SDLC_ROLE`, set per process by `run.sh`. A sub-agent inherits the parent's env, so every sub-agent would look like the conductor or like nobody. A shared `hooks/_role.sh` resolves the role from `SDLC_ROLE`, else from the hook input's `agent_type` (`block-role-spawn.sh` already reads `.agent_type`, so the field exists for that case). The stray-worktree hook's per-run prefix becomes the dispatch's `.worktrees/tmp/<name>`; the hook accepts any path under `.worktrees/tmp/` for a role agent, which is weaker (parallel agents share the parent dir) and accepted.

Read-only enforcement. `run.sh` disallows Edit, Write, and NotebookEdit for every role but the builder. Sub-agents get `disallowedTools` in the definition for Edit and NotebookEdit, and Write is allowed to the one result path by the hook. The verifier's no-git-state-change rule stays in its prompt, as today.

Permissions. Sub-agents run under the parent's mode unless a definition sets `permissionMode` (whether a plugin-shipped agent may is P1), so the per-role `--dangerously-skip-permissions` is gone. `permissions.deny` with `Agent(<type>)` rules is a second, static layer for the consumer's settings. The hooks above stay the guardrail. Headless conductors keep `block-background.sh` (`SDLC_HEADLESS=1`): their spawns are foreground.

Unverified and gating: that a plugin PreToolUse hook fires for sub-agent tool calls and carries `agent_type` (probe P2). If it does not, T-0281 stops and replans around `tools:` allowlists and the spawn gate alone.

## 5. Fanout lanes

Spawn depth defaults to 3, so a lane conductor sub-agent that dispatches roles is possible on paper, but whether the generated definitions get the Agent tool and whether nested background results reach the lane conductor is unverified (P8). The baseline is flat: the parent session is the only dispatcher, one level deep. Fanout keeps what is deterministic and moves process launching to the conductor:

- `fanout.py prep` does preflight, the overlap check, the lane choice (`steps.py lane`), and prints a dispatch table. `fanout.py land <branch>` does the locked merge, the gates, the vacuous-gate refusal, `close <id>`, and the report. `run --driver` stays for the selftest.
- A ticket of level L1 or L2 is one named background `solo-L1`/`solo-L2` sub-agent with `isolation: worktree`. The brief adds the lane commit instruction (`<id>: <title>`), because solo commits nothing unless asked. The worktree branch the host returns is merged by `land`; this is the existing external-lane path (`<lane>@<branch>`, `external_branch:`).
- A `full` or `lean` ticket is driven by the parent (a nested lane conductor is a later option if P8 passes): roles are sub-agents against the lane branch, each brief carrying a `Tree:` line and using `cd <tree> &&` per Bash call, since a sub-agent shares the parent's cwd and cwd resets between calls. The parent reads only `steps.py next` and the records, so its context cost is the status lines.
- Solo levels L2 and L3 still need one task-dir verifier; the parent dispatches it after the solo returns, which keeps independence in one place and does not depend on nesting.
- `--max-lanes` (default 4) stays, well under the 20-agent default ceiling (`Concurrent subagent limit reached` is a failed spawn, not a crash). Parallel sub-agents draw on one account limit. Lane names are `<ticket>-solo`, but the host names the branch `worktree-agent-<agent_id>` (observed live, T-0287), so the conductor reads it from the Agent result and `land` treats a host branch as a solo lane; `.claude/worktrees/` must be ignored by the repo and excluded from watchers, as `.worktrees/` is today.

Unverified: a resumed sub-agent keeps its worktree (P4), and nested lane conductors (P8).

## 6. Survival and resume

Detection. `prepare` records the owning `claude` pid (walking parent pids from the Bash call) in the attempt record. `dispatch.py status` shows an attempt as `orphaned` when it is `running`, has no result, and that pid is dead. A live parent with a failed Agent result is `failed`, not orphaned. Liveness uses the pid, not file mtimes.

Resume ladder, cheapest first, never replaying an old report:

1. `SendMessage` to the agent by `name` (then by agent id) with "continue and write the result". This is the path that worked across `/login` switches here.
2. After a new session, `SendMessage` by id if the host still resolves it (P4; may fail across sessions).
3. A new attempt (`-k`) whose brief starts with: inspect `git status` and the artifacts dir, transcript at `<path>`. This is the `run_lifecycle.py recover` rule, `dispatch.py recover` marks the old attempt `interrupted`, and `prepare` calls it for a dead-parent attempt.

`dispatch.py resume <name>` prints the ladder for an orphan. The supervisor (`supervisor.py`) wakes conductors for mail and starts its wakes as `claude -p`; that is a single session, not the multi-agent executor, so it is unchanged except that `status.json` lists orphaned dispatches (read-only; it still never claims or reads a message). The board shows `orphaned`. A wake that dispatches roles uses foreground sub-agents, and an interrupted wake leaves orphans the next wake reports.

## 7. Single points of failure

- The parent session. Closing the terminal or a crash may end the background sub-agents (P7) and leaves running attempts. Mitigation is durable state: `steps.py resume`, the dispatch and attempt records, and the resume ladder let a new parent continue. A compacted parent loses nothing because no state lives only in its context.
- Account limits. All sub-agents and the parent share one account's session limit, so parallel lanes spend it faster; a 429 inside a sub-agent returns as a failed result and `record` writes the `.limit` marker. A `/login` to another account can change model access (`fable` may be missing there): a spawn that fails on the model is reported, and the conductor never silently moves a verifier onto the builder's family to proceed.
- Cost visibility (section 3) and hook visibility (section 4) are the two silent ones, so each has a check.

## 8. What `run.sh` becomes, and the order

`run.sh` stays as the Codex runner (its exec and subagent transports, `run_lifecycle.py`, `codex_exchange.py`) and loses its Claude branch last. In between it is unchanged, so main stays usable at every commit. At the end `SDLC_BACKEND=claude run.sh` exits 2 with one line pointing to `dispatch.py prepare`, unless `SDLC_CLAUDE_EXEC=1` (legacy, for `bench.sh` and CI only, which are not multi-agent interactive sessions and cannot use sub-agents). `solo_run.py` and fanout's default headless conductor go the same way.

Codex parity. Codex already works this way: with `SDLC_CODEX_TRANSPORT=subagent`, `run.sh` writes a request, the parent invokes the named native agent with fresh context and submits the report through `codex_exchange.py`, and the runner validates and records it (`codex-role-execution.md` line 54). Both hosts therefore end in the same validate-and-record step and the same result and `runs.jsonl` shapes; they differ in who launches the agent (the parent's Agent call versus the parent's native subagent call) and in enforcement (Claude hooks do not apply to Codex). Models and efforts stay in their own tables: `levels.json` and `models.json`. T-0278's acceptance proves record-shape parity and leaves `codex-selftest.py` green.

Order (additive first; the flip is T-0282; removal is last):

| Order | Ticket | Size | Depends | Why here |
|---|---|---|---|---|
| 1 | T-0275 probes | S | none | Closes the unverified items that decide fallbacks |
| 2 | T-0276 levels table and generated agents | M | T-0275 | Definitions exist before anything spawns them |
| 3 | T-0277 `dispatch.py prepare` | M | T-0276 | Gates as code, parity with `run.sh` dry run |
| 4 | T-0278 `dispatch.py record` | M | T-0277 | Validation and record shape |
| 5a | T-0279 `status` and `resume` | S | T-0278 | Survival |
| 5b | T-0280 estimated cost | S | T-0278 | Keeps the budget gate live |
| 5c | T-0281 hooks and spawn gate | M | T-0275, T-0277 | Must land before the flip or spawns are denied |
| 6 | T-0282 conductor and chain text (the flip) | M | T-0276, T-0278, T-0279, T-0280, T-0281 | Sub-agents become the Claude mode |
| 7a | T-0283 launcher skills | M | T-0282 | Text |
| 7b | T-0284 solo as sub-agent | S | T-0282 | Default lane |
| 7c | T-0286 supervisor orphans | S | T-0279 | Visibility |
| 8 | T-0285 fanout as sub-agents | M | T-0284, T-0281 | Needs solo and isolation |
| 9 | T-0287 live evidence incl. account switch | M | T-0283, T-0284, T-0285, T-0286 | Release gate |
| 10 | T-0288 retire the Claude headless path | S | T-0287 | Only after a passing live run |

Rows 5a to 5c, and 7a to 7c, are independent of each other except where they share a file (`check.py`, `hooks.json`), where they run in sequence. T-0275 to T-0281 are additive: no consumer-visible behavior changes until T-0282.

## 9. Risks and what is unverified

Biggest risks:

1. Hooks may not see sub-agent role or may not fire (P2). That removes publish, kill, worktree, and Write-path enforcement for roles. Mitigation in T-0281 is stop-and-replan to `tools:` allowlists; until proven, roles are less sandboxed than under `run.sh`.
2. Cost becomes an estimate. A bad blended rate quietly mis-gates budgets either way. Mitigation is the calibration check against recorded history, the `estimated` flag everywhere, and P5 for better pricing.
3. The parent session is a single point of failure and the only dispatcher, with fanout lanes sharing one account limit and an unknown background concurrency ceiling. Mitigation is durable records plus the resume ladder, and `--max-lanes`.

Unverified (each is a probe row in T-0275, owned and closed there or in T-0287):

| Id | Assumption | If false |
|---|---|---|
| P1 | `effort`, `model`, `disallowedTools`, `skills` frontmatter of a plugin agent are honored; aliases map to the pinned models | One definition per effort and skills appended in the brief; pin check |
| P2 | Plugin hooks fire for sub-agent calls with `agent_type` and `agent_id` | Replan T-0281 around `tools:` allowlists; `record --stdin` |
| P3 | Notification usage fields beyond `subagent_tokens`, `tool_uses`, `duration_ms` (observed); behavior at a session limit | Cost basis stays tokens only; limit handled from the failed result text |
| P4 | `SendMessage` resumes a finished agent, in a new session too | Rung 3 (new attempt) is the only cross-session path |
| P5 | Transcript path, per-message model and usage are readable | Dispatch record stands as the independence evidence; blended cost |
| P6 | `SubagentStop` input (`agent_id`, `agent_type`, `effort` documented) also holds the transcript path and last message | `record` runs only from the conductor |
| P7 | The 20-agent limit is per session or global; a parent restart's effect on background agents | Lower `--max-lanes`; rely on the resume ladder |
| P8 | A sub-agent can dispatch sub-agents (depth 3) with the Agent tool and receive their results | Parent stays the only dispatcher (baseline) |

Also unverified: the `/tmp/canary` result for `claude -p`; that background sub-agents survive the parent closing (assumed not); that a hook cannot rewrite tool input. What is observed: sub-agents survived `/login` switches; the code facts cited above.
