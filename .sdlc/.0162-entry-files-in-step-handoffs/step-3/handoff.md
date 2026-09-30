## Task goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Step 3: Handwritten step handoffs and the step template carry the subsection
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

- `plugins/sdlc-lite/skills/fix/SKILL.md` step 2: when the file being fixed has a nearest `AGENTS.md` other than the root, the conductor adds a `### Read first` subsection. It follows the same rule as the planner and sits after `level:` and before `### Do`. Keep the existing lint target `.sdlc/<slug>/step-1/handoff.md` unchanged, because check.py pins it.
- `plugins/sdlc-lite/skills/chain/SKILL.md` section 5 step 3: the `Loose ends` step handoff adds the same subsection for the files its items change.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, step handoff template: add the heading line `### Read first` with an item line ``- `<path>` `` between `level: L<n>` and `### Do`. Add prose that calls the subsection optional, states the nearest-entry rule with the root left out, and notes that `steps.py lint` refuses a missing path. Leave the fenced `merge-step` block unchanged.
### Acceptance criteria
- `grep -qF '### Read first' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -qF '### Read first' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF '### Read first' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -A2 -x 'level: L.n.' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qxF '### Read first'`
- `grep -F 'Read first' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qi optional`
