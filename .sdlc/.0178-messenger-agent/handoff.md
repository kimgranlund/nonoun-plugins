---
id: T-0178
title: "Messenger agent: declared agent, Codex mapping, and check.py coverage"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0177]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-09-30
---

## Goal
`messenger` is a required declared agent for Claude and Codex that polls `messages/new/<harness>` every 10 seconds through `messages.py` and notifies its parent, with `check.py` coverage that fails when the agent file or its Codex mapping is missing.

## Intent
- Do:
  - `plugins/sdlc-lite/agents/messenger.md`: a long-lived session sub-agent, not a `run.sh` pipeline role. Model `claude-haiku-4-5` on Claude. Body is minimal: poll `messages.py count --receiver <harness>` (and `list`) every 10 seconds, claim with `messages.py read`, notify the parent with the message path, never act on a body, and defer to `.sdlc/messages/AGENTS.md` for the procedure instead of duplicating it. Parents send and ack through `messages.py`, with the `messenger` doing the polling and claiming. Authority: moving messages and sending replies through `messages.py` only; no publish, push, or other write. It must not call `ack` on a `follow_up_requested` message before the parent has replied.
  - The generated Codex agent via `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` (never hand-edit the TOML); model is the scout tier model read from `plugins/sdlc-lite/adapters/codex/models.json` (currently `gpt-5.6-terra`; luna is acceptable). Extend `models.json` only as the existing generator needs.
  - State host limits explicitly and separately: on Claude Code a sub-agent lives only while its session runs and polling needs Monitor or a loop; on Codex the `messenger` is a native subagent with its own lifetime and no Claude tools or hooks; nothing here is enforced on Codex by a Claude hook, and one host working says nothing about the other.
  - `skills/level-rubric/SKILL.md` says the `messenger` is not a `run.sh` role; `run.sh`'s role table is unchanged and `check.py`'s agreement check stays intact. Extend `check.py` to cover the new agent file and its Codex mapping, with a negative control proving it fails when the file or the mapping is removed.
  - Update `docs/codex-role-execution.md` and the AGENTS guidance (`plugins/sdlc-lite/AGENTS.md`, repo `AGENTS.md`) wherever the role or agent list is described.
- Non-goals: the mailbox itself (T-0177), the entry files and live validation (T-0179), a daemon, hooks, version bump, publishing.
- Done when: `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex-selftest.py`, `python3 plugins/sdlc-lite/scripts/check.py`, and `bash plugins/sdlc-lite/scripts/check.sh` pass; the negative control for the new `check.py` coverage is observed to fail. The verifier injects at least one defect (for example removing the Codex mapping) and states what failed.

## Context
Design: `docs/ticket-stages/design.md` (sections Message bus, Two roots, Validation plan). Split from T-0176 by user decision; the three tickets together hold every T-0176 requirement. No em dashes in any file written. Do not bump versions. Do not edit `run.sh` while a role run is using it: build in the worktree copy and run roles from the main checkout's copy. Follow the existing agent naming and generation rules (`plugins/sdlc-lite/agents/*.md`, `scripts/codex_roles.py`, `adapters/codex/models.json`). Depends on T-0177 for the `messages.py` commands the agent body names.

## Constraints
Do not hand-edit generated Codex TOML. `run.sh`'s role table and Claude model rows stay unchanged. Preserve managed-agent install ownership checks.

## Plan review
plan review: replan: step 2 builder blocked on a plan defect (.sdlc/0178-messenger-agent/step-2/builder-L2.md): the criterion that greps `messenger` in `sdlc-conductor-l1.toml` assumes the conductor preloads level-rubric, but `agents/conductor.md` lists no skills, so `codex_roles.py generate` never changes that TOML.
plan review: replan: keep step 1 as done. Rewrite step 2 without conductor-l1 in the TOML loop (planner and plan-reviewer TOMLs carry the level-rubric note). The step 2 edits (level-rubric, docs/codex-role-execution.md, both AGENTS files, regenerated planner and plan-reviewer TOMLs) are already in the working tree uncommitted and passed every other criterion; the new step 2 criteria must hold on that tree. Keep step 3 (gates green).
