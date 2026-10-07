---
id: T-0276
title: "Claude level table and per-level generated agents"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0275]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One table (`adapters/claude/levels.json`) holds the role, level, model, effort rows; a generator writes one agent definition per row so effort comes from the definition and model from the Agent call.

## Intent
- Do: Claude level table and per-level generated agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0, and exits 1 after one generated file is edited by hand or one `levels.json` effort is changed without regenerating (observed negative controls).
  - `python3 plugins/sdlc-lite/scripts/evals.py hash` prints the same sha256 before and after the change (values unchanged; only the table home moved), and `evals.py check` passes.
  - `python3 plugins/sdlc-lite/scripts/check.py` passes with item 1 comparing levels.json, run.sh, and the level-rubric three ways; changing one effort in any one of the three makes it fail (negative control per source).
  - Every generated definition has the role body of `agents/<role>.md` verbatim, frontmatter `name`, `description`, `model`, `effort`, `disallowedTools` (read-only roles), and `skills`; `check.py` item 2 holds that every `levels.json` row has a `run.sh` case until run.sh is retired.
  - Names are `<role>-L<n>` (solo: `solo-S`, `solo-M`, `solo-L`).

## Context
Design section 1 and 8. Verifier family remap changes only the Agent `model` parameter, never the definition, so no extra definitions exist for it. Depends on the P1 probe result for `effort` frontmatter; if P1 fails, fall back to one definition per effort and say so in the ticket.

## Acceptance criteria
Run the negative controls in a throwaway copy, never in the working tree: from the repository root, `T=$(mktemp -d) && rsync -a --exclude=.git ./ "$T"/`, then edit and run inside `$T`. The generated definitions are uncommitted, so a `git worktree` at HEAD does not hold them.
1. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0 and reports 22 files; in `$T`, appending a line to `plugins/sdlc-lite/agents/builder-L1.md` makes it exit 1, and (separately) changing one effort in `plugins/sdlc-lite/adapters/claude/levels.json` without regenerating makes it exit 1.
2. `python3 plugins/sdlc-lite/scripts/evals.py hash` prints `f4d26ef28e57559a85296cd885e261327cdf57863c3b1c73cc91ed50876048a3`, the value `HEAD` gives (`git show HEAD:plugins/sdlc-lite/scripts/run.sh` case rows plus `models.json` build the same text); `python3 plugins/sdlc-lite/scripts/evals.py check` and `python3 plugins/sdlc-lite/scripts/evals.py selftest` exit 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0; in `$T`, changing one effort in `adapters/claude/levels.json`, then (restored) in `scripts/run.sh`, then (restored) in `skills/level-rubric/SKILL.md` makes `check.py` exit 1 each time, and the failing lines name the changed source.
4. Each of the 22 generated files (`agents/<role>-L<n>.md` for the 19 pipeline rows, and `agents/solo-S.md`, `solo-M.md`, `solo-L.md`) has the text of `agents/<role>.md` after its frontmatter verbatim, and frontmatter keys `name` (equal to the file stem), `description`, `model` and `effort` (equal to its `levels.json` row), `skills` (equal to the role file's list, absent when it has none), and `disallowedTools: Edit, NotebookEdit` for every role except `builder` and `solo`.
5. No other `agents/*-L<n>.md` or `agents/solo-*.md` exists.
6. `git diff --stat HEAD -- plugins/sdlc-lite/adapters/codex` is empty and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0 (Codex files untouched). `git diff HEAD -- plugins/sdlc-lite/scripts/run.sh` changes only the comment above the `case "$role:$level"` rows: no model or effort value changes.
7. `bash plugins/sdlc-lite/scripts/check.sh` and `python3 scripts/check-packaging.py` exit 0.
8. P1 (`docs/reports/2026-10-06-subagent-probes.md`) found `effort`, `model`, `skills`, and `disallowedTools` honored for a plugin agent, so per-level definitions stand and no per-effort fallback is needed.

## Constraints
Model and effort values must not change (user decision). Codex files and `models.json` untouched. No em dashes. No push, tag, or publish.

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
