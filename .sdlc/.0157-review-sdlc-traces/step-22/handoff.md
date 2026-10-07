## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 22: Integration: conductor route, Codex adapter, ignore guidance, internals doc
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
- `plugins/sdlc-lite/agents/conductor.md`: under `## Route every ask`, add the line: review a project's sdlc run traces for waste and bugs caused by sdlc-lite → `/sdlc-lite:review-traces`.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: add the table row `| Review sdlc run traces for sdlc-lite waste and bugs | review-traces |`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: add `.sdlc/runtime/` to the Layout block (traces analysis outputs and cursor written by `traces.py`, never committed) and to the ignore snippet for projects that commit the trail.
- `docs/references/sdlc-internals.md`: add a `## \`scripts/traces.py\`` entry (the four subcommands, the out dir and cursor under `.sdlc/runtime/traces/<repo-key>/`, the detector families and thresholds table, the model-free stages 1 and 2, the selftest and its corpus case, the `--rerun-criteria` opt-in and its worktree rule) and name `/review-traces` in the Launcher skills paragraph.
- The conductor is a generated Codex agent (`conductor` is a key of `adapters/codex/models.json`): run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` so `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml` carries the route and `generate --check` stays green.
### Acceptance criteria
- `grep -qF 'review-traces' plugins/sdlc-lite/agents/conductor.md`
- `grep -qF 'review-traces' plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `grep -qF 'review-traces' plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`
- `grep -qF 'sdlc/runtime' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'scripts/traces.py' docs/references/sdlc-internals.md && grep -qF 'review-traces' docs/references/sdlc-internals.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*|plugins/sdlc-lite/agents/conductor\.md|plugins/sdlc-lite/skills/sdlc-lite/SKILL\.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1\.toml|plugins/sdlc-lite/skills/handoff-format/SKILL\.md|docs/maintenance/sdlc-internals\.md)$')"`
