## Task goal
A cross-cutting or risky plan, or any replan, gets an independent semantic review before a builder starts, and a defective plan is rejected before it costs a build.

## Step 1: Planner contract: assumptions, settled interfaces, dependencies
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Edit `plugins/sdlc-lite/agents/planner.md` only. Depends on nothing.
- In the final-message format, add a `## Assumptions` section between the last step block and `## Risks`: one list item per load-bearing assumption, `- <assumption>: verified by <how>` (file:line or a command run), or `- unresolved: <decision>: <what settles it>` for a design decision the handoff, the artifacts, and the code do not settle. Say that `steps.py split` ignores the section (it copies only `## Step` blocks) and that `steps.py review` stops on an `unresolved:` item so the user decides.
- In the `### Do` line of the format ("What to change and where (paths)"), require the implementation targets (paths and symbols), the settled interface decisions the step relies on or creates (names, signatures, keys, paths, formats) with the evidence that settled them, the earlier steps it depends on (`Depends on: none` or `Depends on: step 2`), and the focused checks it runs. State the rule: a design decision is never left to the builder ("choose a convention", "as you see fit"); it is settled in the Do with evidence or listed as `unresolved:` under `## Assumptions`, because the plan-reviewer returns `blocked` for a step that depends on one.
- In rule 9 (replan), add: a `plan review:` entry in `## Plan review` quotes the plan-reviewer's findings, one `plan review: <verdict>: <finding>` line each; fix every step a finding names, and keep the numbers and text of steps it does not name.
Keep every phrase `scripts/check.py` requires in this file (`plan defect`, `Plan review`, `no new findings`, `gates green`, `one Bash call`, `can go red`, `SDLC_BASE_SHA`, `membership or structure`, `owns that budget`, `contract dependents`, `Read first`, the merge-step block) byte-identical.
### Acceptance criteria
- `grep -qx '## Assumptions' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'unresolved:' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'plan review:' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'Depends on:' plugins/sdlc-lite/agents/planner.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/agents/planner.md" | { ! grep -q .; }`
