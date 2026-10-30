# Context maintenance

Read [repository guidance](../../AGENTS.md) first. This plugin ships context skills: authoring, routing diagnosis, mapping and workspace design. It is not a lifecycle runtime or execution engine.

| Skill | Use | Source (2026-10-25) |
|---|---|---|
| `progressive-context` | Entry points, capability contracts, evidence and reuse qualification | this repository |
| `context-fog-of-war` | Explain context-routing decisions from traces; audit guidance contracts | `~/.claude/skills/context-fog-of-war` |
| `context-routing-review` | Review and test repository context routes with fresh-agent trials | `/Volumes/kimba/.codex/skills/context-routing-review` |
| `generative-systems` | Generative systems grounded in authoritative kits, contracts and assets | `~/.claude/skills/generative-systems` |
| `system-atlas` | Whole-system workflow diagrams, machinery inventory and enforcement matrix | `~/.claude/skills/system-atlas` |
| `icm-architect` | ICM workspaces: folder structure as agent architecture | `~/.claude/skills/icm-architect` (upstream in its `SOURCE`) |

## progressive-context

- Keep `skills/progressive-context/SKILL.md` and the contract/evidence references domain-neutral. Load browser, A2UI, and SDLC guidance only through their optional routes.
- Preserve intent-only stubs, evidence-bound assessments, and qualification for a named reuse scope. Do not turn descriptive lifecycle views into mandatory stored states.
- Use existing project records; avoid duplicate tickets, plans, registries, or assessments. Keep examples explicitly illustrative and project decisions in repository design docs.
- Add a reference only when it has a distinct retrieval purpose. Link it from the skill with a clear loading condition.

## All skills

- Each skill keeps its own maintenance notes where it has them (`context-fog-of-war/AGENTS.md` and its `updates-log/`).
- A link to a skill in another plugin is written by name (`design:base-ui` and the file path), never as a relative link.
- Do not ship `.DS_Store`, `__pycache__`, `node_modules`, symlinks or dated evidence trees. `generative-systems/resources/reports/` stays in the user-level folder; links into it are code spans.
- Keep host manifests consistent. This plugin requires no model mapping, subagents, hooks, or SDLC dependency.

For any change, inspect changed links, run `python3 scripts/check-packaging.py` from the repository root (identity, skill sizes, relative links), validate the skill with the available skill validator, and run `git diff --check`. Run a skill's own tests when its scripts change: `python3 -B -m unittest discover -s tests` in `context-fog-of-war`, `python3 -B scripts/test_atlas_renderer.py` in `system-atlas`. The SDLC runner/hook suite is unnecessary unless that implementation also changes.
For substantive workflow changes, evaluate a realistic request against the revised guidance and report observed behavior separately from structural validation.
