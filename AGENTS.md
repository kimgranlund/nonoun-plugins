# Repository guidance

This repository maintains two peer plugins for Claude Code and Codex.
`CLAUDE.md` imports this file for Claude Code. Read the scoped guidance linked below before editing that plugin; do not assume the host loaded it automatically.
All paths and shell commands in this file are relative to the repository root.

## Purpose and ownership

- **Progressive Context** owns durable intent, capability contracts, context navigation, evidence, and qualification for reuse.
- **SDLC Lite** owns work execution: tickets, plans, roles, runs, verification, escalation, and closure.
- Integrate through links to authoritative records. Keep execution status and capability qualification distinct.
- Repository maintenance instructions are not automatically shipped as consumer skill context.

## Map and how work is done here

- `plugins/` holds the two plugins; `docs/` holds contracts, designs, and dated evidence ([docs entry](docs/AGENTS.md)); `scripts/` holds repo-level checks; `.sdlc/` holds tickets, plans, and run records ([router](.sdlc/AGENTS.md)).
- Do not read unless asked: closed `.NNNN-*` ticket folders, `docs/reports/` evidence, and `docs/other/`.
- Philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction." Give each role a clear brief and the files it needs; do not add steps or checks for doubt the evidence does not support.
- Pick the lane first with `steps.py lane <task dir>`: `solo` is the default for size S and M, `/fix` runs only when the user asks or the lane script prints `fix`, and the full chain needs a stated reason (an L4 or L5 step, a merge step, or cross-cutting scope). One independent verifier per ticket.
- A new idea becomes a new ticket, not a larger one. Freeze a handoff once a role reads it, replan at most once, then ask.

## Read for the task

| Task | Read next |
|---|---|
| Progressive Context skill or references | [Plugin guidance](plugins/progressive-context/AGENTS.md) |
| SDLC roles, skills, runner, or checks | [Plugin guidance](plugins/sdlc-lite/AGENTS.md) |
| Codex execution or generated agents | [Codex execution guide](docs/codex-role-execution.md) |
| Claude hook behavior | [Hook maintenance](docs/maintenance/claude-hooks.md) |
| Marketplace or host packaging | [Compatibility report](docs/plugin-compatibility.md) and `scripts/check-packaging.py` |
| Design rationale and runtime proposals | [Documentation index](docs/README.md) |

Read only the linked details needed for the change. Keep scope-specific instructions in their owning plugin; keep implementation explanations in references.

## Shared invariants

- Preserve user changes and concurrent work. Do not edit or move runtime scripts while a role or benchmark is using them.
- Use self-contained handoffs for delegated roles. A full-context fork needs a stated reason and does not establish independent review.
- Model and effort defaults are user decisions. Preserve them unless the user authorizes a change.
- Scope host-specific flags, tool behavior, and permission claims explicitly. Claude hook enforcement does not imply Codex enforcement.
- Keep one authoritative location for each fact. Update the affected contract and reference when behavior changes; avoid copying tables into this file.
- Distinguish intended, implemented, checked, and reusable behavior. Bind evidence to the material actually assessed.
- Stop only processes owned by the task. Scope formatting and fixes to relevant files; preserve unrelated worktrees, branches, and stashes.
- Publishing and external writes follow the user's authorization. Existing authorization remains valid; do not invent an additional approval step.

## Authoritative sources

| Concern | Source |
|---|---|
| Shared role and output contracts | `plugins/sdlc-lite/agents/*.md` (pipeline roles plus the `conductor` and `messenger` session agents) |
| Claude role models and efforts | `plugins/sdlc-lite/adapters/claude/levels.json`; `run.sh` and the level rubric are checked against it, and `scripts/claude_roles.py` generates one agent definition per row |
| Codex models and efforts | `plugins/sdlc-lite/adapters/codex/models.json` |
| Codex agent generation | `plugins/sdlc-lite/scripts/codex_roles.py`; generated TOML files are not edited directly |
| Skill behavior and conditional references | Each plugin's `skills/` directory |
| Host manifests | Each plugin's `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` |
| Marketplace membership | `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`; preserve parity |
| Current task ordering | `.sdlc/roadmap.md`, when present; regenerate through the ticket workflow |

## Validation proportional to the change

Run commands from the repository root. Select checks for the affected behavior; passing a structural validator alone does not establish runtime correctness.

| Change | Required validation |
|---|---|
| Documentation or reference-only edits | Inspect local links, run `git diff --check`; validate changed skills and run packaging checks when plugin files or routes change |
| Skill frontmatter or packaging | `python3 scripts/check-packaging.py`, available host/skill validators, and inspection of discovery routes |
| SDLC role or execution behavior | Relevant regression checks, generated-agent parity, and a focused live run in a throwaway project |
| Shared runner, cross-workflow behavior, or release | `bash plugins/sdlc-lite/scripts/check.sh` and packaging checks; live evidence for changed host behavior |
| New or changed check/gate | A positive case and an observed negative control proving the gate rejects the defect |

Scoped plugin guidance names the relevant checks. For a documentation-only change, do not run unrelated role and hook suites. Broaden testing when changes or failures justify it.
If a required check cannot run, report it as unverified and explain the limitation. Do not silently substitute offline fixtures for live host validation.

## Completion

Summarize the change, checks actually run, and remaining limitations. Update affected guidance, not every document that mentions the subsystem.
Commit completed maintenance work with `Co-Authored-By: Codex <noreply@openai.com>` when authored by Codex, or the current agent's appropriate attribution. Push only when the user has asked for it.
Record historical benchmark results and validation evidence in dated reports, not this entry point. Git history retains earlier operating decisions.
