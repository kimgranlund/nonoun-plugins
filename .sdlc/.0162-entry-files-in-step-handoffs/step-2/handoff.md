## Task goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Step 2: Planner writes the subsection; builder and verifier read it
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

In `plugins/sdlc-lite/agents/planner.md`, add a short `## Entry files` section between the "Criteria that can pass" rules and `## Merge steps`. It states:
- For each file a step changes, find the nearest `AGENTS.md` in that file's folder or a folder above it.
- Leave out the root entry.
- List the rest under a `### Read first` subsection. The subsection sits after the step's `level:` line and before `### Do`.
- Each item is one line, ``- `<path>` ``, with the path relative to the repository root.
- A step whose only entry is the root has no subsection.
- Files the step only reads are not listed.
- `steps.py lint` refuses a listed path that does not exist.

In the planner's final-message template, show the optional subsection between `level: L<n>` and `### Do`, with a one-line note that it appears only when needed. Do not touch the fenced `merge-step` block. check.py requires it to stay identical in the planner and handoff-format.

In `plugins/sdlc-lite/agents/builder.md` and `plugins/sdlc-lite/agents/verifier.md`, add one sentence to the opening paragraph: before starting, read every file listed under the handoff's `### Read first` and follow it for the files it governs. Put it in the opening paragraph, not the numbered list, because `hooks/block-repo-format.sh` cites "builder rule 6" and renumbering would break that reference.

Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` so the Codex agent TOMLs under `plugins/sdlc-lite/adapters/codex/agents/` match.
### Acceptance criteria
- `grep -qF '### Read first' plugins/sdlc-lite/agents/planner.md`
- `grep -qE 'nearest .?AGENTS\.md' plugins/sdlc-lite/agents/planner.md`
- `grep -qF '### Read first' plugins/sdlc-lite/agents/builder.md`
- `grep -qF '### Read first' plugins/sdlc-lite/agents/verifier.md`
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l1.toml`
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml`
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-verifier-l1.toml`
