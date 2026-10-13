---
name: level-rubric
description: "Level tables and routing rubrics for every sdlc-lite role (model and effort per level, and how to pick a level). Reference for the launcher skills; not a command."
user-invocable: false
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

The tables below describe the Claude backend. For Codex, model and effort are defined in `adapters/codex/models.json`; the level scope and escalation rules below still apply. The Codex runner records its selected model. When the builder and verifier models match, the Codex verifier switches to the model that `verifier_alternates` in `adapters/codex/models.json` maps the builder's model to; the Codex plan-reviewer takes the model that map gives for the newest planner result's recorded model. With no alternate configured, the verifier keeps the builder's model and the runner records `shared_with_builder` in the result header and `runs.jsonl`.

The Claude model and effort per level live in `${CLAUDE_PLUGIN_ROOT}/adapters/claude/levels.json`, which `scripts/claude_roles.py` turns into one agent definition per row (`sdlc-lite:<role>-L<n>`); the definition fixes the effort. This file says how to pick a level. Keep the two in sync: `check.py` compares them.

On Claude, a role at a level is dispatched as a sub-agent: `dispatch.py prepare <role> <level> <handoff.md>` runs the gates and prints the dispatch JSON, the conductor passes its `subagent_type`, `name`, `model`, `prompt`, and `run_in_background` to the `Agent` tool unchanged, and `dispatch.py record` validates the result and writes its header. `model` is a per-call parameter and `prepare` chooses it, so a verifier or plan-reviewer stays off the producer's model family; `effort` comes from the definition, so the conductor never passes an `effort` argument. A Codex role runs through the Codex runner with the rows of `adapters/codex/models.json`.

## How to resolve a level

Use the first source that gives one:
1. A level in the user's arguments.
2. A `level: Lx` line in the handoff (set by the planner, per step).
3. The role's rule below. Pick the **lowest** level whose row fits every signal, then state the level and a one-line reason before running.

## One level scale

SDLC Lite has one level scale, L1 to L5, for every sized thing: a role run, a ticket (its front matter `size:`, the ticket level), and the solo agent. This table ties them together; the role sections below give each role's model per level.

| Level | Scale | Ticket level: default lane (`steps.py lane`) | Solo agent: Claude, Codex | Ticket budget (`budget.py set --tier`) |
|---|---|---|---|---|
| L1 | small | solo | `solo-L1`: Sonnet high, `sdlc-solo-l1` | $5 |
| L2 | medium | solo | `solo-L2`: Opus medium, `sdlc-solo-l2` | $30 |
| L3 | large | full chain | `solo-L3`: Opus high, `sdlc-solo-l3` | $60 |
| L4 | extra large | full chain | none | none, ask the user |
| L5 | reserved | full chain | none | none, ask the user |

The solo level is the ticket level, and a solo L3 runs when someone starts it for a large ticket, or when `steps.py lane` sends it there: under `profile: inner-loop` in `.sdlc/config`, a size L3 ticket with no merge in its title and no security word in its handoff takes the solo lane (T-0512). The Claude solo rows live in `adapters/claude/levels.json` (row `solo`), the Codex ones in `adapters/codex/models.json`. A ticket or a launcher written for an older plugin version may still use the one-letter names; the scripts read each as its level (`tickets.py migrate-size` rewrites ticket front matter).

## builder (L1 to L5)

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Opus low | Mechanical: rename, boilerplate, config, one file, spec fully given |
| L2 | Sonnet high | Small change in a known pattern, 1 to 3 files, tests exist |
| L3 | Opus medium | New feature inside the existing architecture |
| L4 | Opus high | Crosses modules, unclear edges, concurrency or state |
| L5 | Opus xhigh | Earlier attempt failed, root cause unknown, or high blast radius |

Bump one level for each earlier `builder-*.md` in the step dir with Status blocked, and after a verifier fail on the same step twice. A builder blocked tagged `plan defect:` goes to replan. A builder blocked tagged `stale lane:` (merged prerequisites missing from the lane) goes to `resplit`, not replan: rebase the lane, supersede the step dir, `steps.py split --only <n>`; it never bumps a level. A verifier fail tagged `plan defect:` goes to replan, or to a criterion swap and a rebuild at the same level when `steps.py swap` accepts the verifier's `swap old:`/`swap new:` proposal. Neither counts toward a bump. A builder block resolved by `steps.py widen` (a conductor scope decision, /chain 4.9) never counts toward a bump either. A recurring finding (a verifier fail or builder block that repeats an earlier attempt's finding on the same step: same criterion, same root cause, after a rebuild or replan addressed it) also goes to a planner L3 replan, like `plan defect:`; it never bumps a level and never counts toward a bump. Most fails are ordinary: the test fires only on a recurrence. L5 failed means stop and ask the user. There is no L6.

### Loose ends step

/chain 5's `Loose ends` step runs the builder at the lowest fitting level (L1 or L2 as a rule) and the verifier per the table below. A fail or block there is reported once and never rebuilt, bumped, or replanned.

The `/fix` fast lane runs builder L1 or L2 (never higher) and verifier L1. A fail gets one rebuild at the same level, with no bump; a second fail hands the item to /chain.

## verifier (L1 to L3)

Follows the newest build level in the step dir: builder L1 or L2 → L1, L3 → L2, L4 or L5 → L3. `dispatch.py prepare` (on Codex, the runner) never lets a verifier run on the build's model family: after a Fable or Sonnet build, a verifier on that family becomes Opus at the same effort; after an Opus build, an Opus verifier (the L1 row) becomes Sonnet at the same effort. The dispatch carries the changed `model`.

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Opus low | Criteria are commands to run |
| L2 | Sonnet high | Judgment on behavior and edge cases |
| L3 | Fable xhigh | Subtle correctness: concurrency, security, data |

A solo ticket's one batched verifier (agents/solo.md) is not chosen by build level: `steps.py verifier-level <task dir>` prints L2 for every ticket, L1 and L2 included, and L3 only for a ticket of size L4 or L5, a Merge ticket, a security ticket, or a ticket whose acceptance criteria pin an exact label or string (a `verifier: L3` line in the handoff says so when the words do not). Fanout's `solo_verifier` keeps L3 on the Codex host, because the replay measured Claude only. A chain step is still verified by the table above. Evidence: `docs/reports/2026-10-07-verifier-l2-replay.md` (L2 matched L3 on 41 of 43 criteria at about one sixth of the cost, and missed one literal label match).

## planner (L1 to L3)

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Sonnet high | 1 to 3 obvious steps |
| L2 | Opus medium | A normal feature |
| L3 | Opus high | Cross-cutting or risky, or any replan (a builder blocked other than `stale lane:`, or a verifier or `steps.py split` tagged `plan defect:`) |

## When a plan is reviewed

The plan-reviewer (L1, one level) reviews a plan before any builder starts. It is for L4 and L5 steps only: required for any plan with a step at builder L4 or L5. Planner level, a merge step, a replan, and a `## Plan review` line no longer trigger it; the planner's open readiness concerns become `## Notes` for the builder.

Other plans keep structural validation (`steps.py lint` and `steps.py split`) alone. `steps.py review <task dir>` prints the action (/chain 3).

The reviewer never runs on the planner's model family. Claude: the row is Fable high, so every plan by a Claude planner row (Sonnet L1, Opus L2 and L3) is reviewed on Fable high; a Fable planner result moves the review to Opus high. `dispatch.py prepare` applies this from the newest planner result's `model=` token. Codex: the `verifier_alternates` map in `adapters/codex/models.json`, keyed by the newest planner result's recorded model, so Astra high reviews Sol plans and `gpt-6.1-sol` high reviews Astra plans.

The verdict routes the plan:
- `pass`: `steps.py split`.
- `replan`: the findings are appended under `## Plan review` and a planner L3 replan runs. A second `replan` stops and asks the user.
- `blocked`: a design decision is missing. It always stops for the user.

## researcher (L1 to L3)

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Sonnet high | One known source, a single fact |
| L2 | Opus medium | Several sources, some conflicting |
| L3 | Opus high | New territory, and the synthesis drives a decision |

## ui-designer (L1)

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Opus high | Any DOM or CSS plan, review, or generate task |

The mode comes from the handoff's `mode:` line (`plan`, `review`, or `generate`); generate is the only mode that edits.

## Single-level roles

| Role | Level | Model / effort |
|---|---|---|
| architect | L1 | Opus xhigh |
| scout | L1 | Sonnet low |
| archaeologist | L1 | Sonnet medium |
| filer | L1 | Sonnet low |
| plan-reviewer | L1 | Fable high |

## Session agents (not pipeline roles)

The `conductor`, the `solo` operator, and the `messenger` are session agents. The messenger is not a pipeline role. Its Claude model `sonnet` at effort low is pinned in its own front matter, as is the conductor's `opus` at effort medium, and the messenger's Codex agent `sdlc-messenger-l1` comes from `adapters/codex/models.json`. `dispatch.py prepare` takes pipeline rows only, and the Codex runner has no messenger case. The messenger is never a prepared dispatch, so `record` does not queue it: when its parent is done with it, run `dispatch.py prune --add <name> --role messenger`, then `dispatch.py prune`.

## Agent-tool spawns (outside a dispatch)

This section applies to any in-session Agent-tool spawn that is not a prepared dispatch: `general-purpose`, `Explore`, `Plan`, or any spawn that names no agent file. Work that has a pipeline role goes through `dispatch.py prepare` and the `Agent` call it describes, never a bare spawn; a dispatch takes its `model` from the dispatch JSON, not from this section.

Every such spawn states `model` explicitly. An unset `model` inherits the session's top model. Pick the seat by class of work:

- Mechanical or gather-only work: `haiku`. The Agent tool takes an alias; the scout level row is `sonnet` low and no longer pins a Haiku id, so `haiku` is the seat for bare spawns only. On 2026-10-07 (Claude Code 2.1.293) the alias `haiku` resolved to Haiku 5.5; on an earlier login (Claude Code 2.1.285) it resolved to Sonnet 5.5, so only the transcript model field says what ran.
- Search, review, and routine coding: `sonnet`, the default.
- Judgment-heavy synthesis: `opus`.

A plain Agent spawn cannot set effort. A `context: fork` or `subagent_type: "fork"` spawn always prices at the parent model, so it is never a step-down.

Evidence: 62 inherited general-purpose builders cost $7.13 each, against $1.82 for an L3 pipeline builder.
