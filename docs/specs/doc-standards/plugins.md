# Plugin surfaces for both hosts

A plugin surface (manifest, skill, agent, command, hook, MCP wiring, script) ships to Claude Code and Codex from one source. This card is for anyone who adds or changes a plugin in `plugins/`. [Core rules](core.md) apply to its prose.

## Method

The shipped skill `author-cross-harness-plugins` (dev-tools plugin) is the authority for the method. Read it; this card copies none of it.

- [SKILL.md](../../../plugins/dev-tools/skills/author-cross-harness-plugins/SKILL.md): the operating contract, shared core with thin host adapters.
- [surface-matrix.md](../../../plugins/dev-tools/skills/author-cross-harness-plugins/references/surface-matrix.md): how each surface maps between hosts.
- [behavioral-fidelity.md](../../../plugins/dev-tools/skills/author-cross-harness-plugins/references/behavioral-fidelity.md): when a surface counts as portable.
- [evidence-contract.md](../../../plugins/dev-tools/skills/author-cross-harness-plugins/references/evidence-contract.md): what a parity claim must cite.
- [claude-code.md](../../../plugins/dev-tools/skills/author-cross-harness-plugins/references/claude-code.md) and [codex.md](../../../plugins/dev-tools/skills/author-cross-harness-plugins/references/codex.md): host facts.

## This repository

1. Each plugin has `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` with the same `name`, `version`, `description`, and `author`.
2. Both catalogs, `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`, list the same plugins at `./plugins/<name>`. The schemas differ; never copy one over the other.
3. Skills are shared: the Codex manifest reads `./skills/`. An SDLC skill carries the Codex adapter line that points at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc/SKILL.md`.
4. Agents are generated per host: `plugins/sdlc/scripts/claude_roles.py generate` for Claude, `plugins/sdlc/scripts/codex_roles.py generate` for the TOML files in `plugins/sdlc/adapters/codex/agents/`. Edit the source, not the output.
5. Claude hooks live in `plugins/sdlc/adapters/claude/hooks.json`, named by the Claude manifest. A plugin has no `hooks/hooks.json`, because Codex discovers hooks there.
6. A host-only gap is recorded in the plugin's `HARNESS-NOTES.md` with the affected surface and the fallback.

## Checks

- `python3 scripts/check-packaging.py` (enforced, run by `check.sh`): catalog parity and source paths, manifest identity, entry skills, the SDLC Codex route line, hook separation, and skill links.
- `python3 plugins/dev-tools/skills/author-cross-harness-plugins/scripts/validate_cross_harness.py plugins/<name>` (advisory): the skill's own validator. It is clean on `context` and `dev-tools`. It flags `${CLAUDE_PLUGIN_ROOT}` in SDLC skills, which rule 3 accepts through the Codex adapter, and `$ARGUMENTS` in one design skill.

Discovery in a live host is evidence the checks do not give; record it in a dated section of [plugin-compatibility.md](../../references/plugin-compatibility.md).
