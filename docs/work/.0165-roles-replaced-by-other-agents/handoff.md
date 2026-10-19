---
id: T-0165
title: "Sessions replace SDLC Lite roles with other plugins' agents"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A session in a repository that uses SDLC Lite runs plan, build, and verify work through `run.sh`, and does not substitute another plugin's agent for an SDLC Lite role. A check that failed before the fix passes after it.

## Repro
Reported by the user on 2026-09-29 from a consumer repository on SDLC Lite 0.18.0. The session was asked "doesnt sdlc come with agents?" and answered:

> I've confirmed sdlc-lite already scales model/effort by builder level (L1-L5) via run.sh, and its verifier deliberately runs on a different model family than the builder. I've been bypassing this by dispatching the fixed Opus-xhigh teamwork builder for everything, so I'll switch to running roles through run.sh as instructed instead of my duplicate tiering.

A second report arrived the same day from that repository's conductor session (gen-ui-kit, bare-clone layout, SDLC Lite 0.18.0, conductor system prompt in force). Over about 12 hours the conductor dispatched roughly 40 builder, planner, and reviewer runs through the Agent tool using other plugins' agents (`teamwork:builder` at a fixed Opus xhigh, `teamwork:code-checker`, `teamwork:planner`, `docs:doc-checker`) instead of `run.sh` roles. Many were tasks the rubric puts at L1. It also wrote three custom builder agent files that duplicated the level table, then deleted them. Evidence named by that session, not read here: its charter log and transcript on the maintainer's machine.

Causes the reporting session named, not verified in this repository: enforcement is text only; a dirty primary worktree in a bare-clone layout gave no obvious clean place to run `run.sh`; an overnight unattended goal met the publish approval gate in `/fix` and `/chain`, which pushed it toward agents that open pull requests themselves; and the Agent tool lists other plugins' builder agents next to SDLC Lite's with nothing preferring SDLC Lite.

## Expected
Every plan, build, and verify runs through `run.sh`, which sets model and effort per level and keeps the verifier on a different model family.

## Actual
The session dispatched another plugin's builder agent (teamwork, fixed Opus xhigh) for every build, which skips level routing, the verifier family rule, attempt records, and `steps.py next`.

## Context
What the plugin says today, checked 2026-09-29:

- `agents/conductor.md` says every role runs through `run.sh`, but it does not forbid an Agent-tool spawn of another plugin's agent in a role's place. Its rule about Agent-tool spawns only asks that they state a model, which reads as permission.
- A session that is not the conductor gets no standing instruction at all. Routing depends on the user invoking an SDLC Lite skill.
- The role agents' descriptions say "Launched headless by scripts/run.sh", which does not tell a session what to do instead.
- Other installed plugins advertise build agents with "Use PROACTIVELY" descriptions.

Fix in two parts:

1. Conductor: add a rule that no Agent-tool spawn of any plugin's agent, including SDLC Lite's own role agents, replaces a planner, builder, or verifier run. Add a `check.py` contract check with a negative control.
2. Sessions that are not the conductor: the root managed block that T-0160 writes gains a line routing plan, build, and verify work to SDLC Lite and forbidding substitution. This part ships with T-0160.

The second report shows the conductor contract was in force, so part 1 addresses the reported case and part 2 covers sessions that are not the conductor. The reporting session's other suggestions are separate tickets: a hook on Agent spawns (T-0166), running a role from a temporary worktree (T-0167), and publishing during an unattended run (T-0168).

## Constraints
The failing check lands before or with the fix. Generated Codex agents are regenerated after the conductor body changes. Model and effort defaults are unchanged.

## Closed

2026-09-29: fixed in session: conductor rule plus check.py guard (3988fd9), root routing line shipped in onboard (T-0160); live probe did not reproduce the bypass in either version, see docs/reports/role-routing-probe.md; enforcement is T-0166
