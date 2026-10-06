# Progressive Context maintenance

Read [repository guidance](../../AGENTS.md) first. This plugin supplies an authoring skill, not a lifecycle runtime or execution engine.

- Keep `skills/progressive-context/SKILL.md` and the contract/evidence references domain-neutral. Load browser, A2UI, and SDLC Lite guidance only through their optional routes.
- Preserve intent-only stubs, evidence-bound assessments, and qualification for a named reuse scope. Do not turn descriptive lifecycle views into mandatory stored states.
- Use existing project records; avoid duplicate tickets, plans, registries, or assessments. Keep examples explicitly illustrative and project decisions in repository design docs.
- Add a reference only when it has a distinct retrieval purpose. Link it from the skill with a clear loading condition.
- Keep host manifests consistent. This plugin requires no model mapping, subagents, hooks, or SDLC Lite dependency.

For reference edits, inspect changed links, run `python3 scripts/check-packaging.py` from the repository root, validate the skill with the available skill validator, and run `git diff --check`. The SDLC Lite runner/hook suite is unnecessary unless that implementation also changes.
For substantive workflow changes, evaluate a realistic request against the revised guidance and report observed behavior separately from structural validation.
