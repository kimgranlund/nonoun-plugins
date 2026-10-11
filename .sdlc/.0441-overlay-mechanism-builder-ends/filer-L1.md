<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt 7814d8e5fd81416c80aa2e7b16a4fe9f, handoff sha256 6888c4b7a99c, 4 of 4 (red) criteria in step 2 had no pre-edit red control. These are the live-run file checks (`test -s` and `test -f` on the live-run files). The builder says `redck.py record` ran before any edit in step 2 but logged the controls as retrospective, because step 1's files already differed from base. The step 2 verifier passed, and a passing verdict does not clear this deviation. The verifier did run its own red checks: the AGENTS.md grep counts 0 at base, and the live-run files do not exist at base.
- Both steps passed: step 1 (verifier L2) and step 2 (verifier L1). Step 1 has no `process-deviations.md`.
- The handoff's Plan review records one plan defect: step 2's first handoff cited output paths that did not exist yet. The planner replanned step 2 only, and step 1 stayed unchanged.
- The step 2 live run proves less than the "Done when" line suggests. It shows that `claude -p --agent sdlc-lite:builder-L1` exited 0 and that its report has `## Status` and no `## At this level`. That the generated builder-L1 definition carries the overlay block rests on a grep of `agents/builder-L1.md`. Nothing in the artifacts shows the live agent acting on the overlay's content.

## PR title
T-0441: Per-level prompt overlays: generator mechanism plus builder L1 and L5 overlays

## PR body
### Summary
Role prompts can now differ by level at generation time. A new `plugins/sdlc-lite/overlays/<role>.md` file holds `## L<n>` sections. The generators insert the matching section before `## Output` as an `## At this level` block. `overlays/builder.md` carries only `## L1` and `## L5`, so only builder-L1, builder-L5 and their two Codex TOMLs change. Every other generated agent, including builder-L3, is byte-identical to base. No model or effort row changed.

### Changes
- `plugins/sdlc-lite/scripts/claude_roles.py`:
  - New `overlay(plugin, role)` and `insert_overlay(body, level, text)`; `definitions()` inserts the block.
  - The generator refuses, with `TableError` (exit 2): an overlay stem with no `levels.json` role, a level with no row, an H2 inside a section, a heading from the role's `results.SCHEMA` sections, a section over 20 lines, text before the first section, and a denylist word. The denylist match is whole-word, so `PR` or `push` inside another word passes.
  - 16 new `ok: overlay:` selftest cases.
- `plugins/sdlc-lite/scripts/codex_roles.py`: `instructions(role, level)` applies the overlay. `main()` now catches `TableError` and exits 2.
- `plugins/sdlc-lite/scripts/check.py`: new item 52, `overlay_placement_bad`, with three controls (a ghost stem, `agents/overlays/x.md`, and an allowed case). The item 39 temp plugin now copies `overlays/`.
- `plugins/sdlc-lite/overlays/builder.md` (new):
  - `## L1`: an ordered procedure and five gap defaults.
  - `## L5`: goal, KPI, budget and four judgment rules.
  - It names no model or effort.
- Regenerated: `agents/builder-L1.md`, `agents/builder-L5.md`, `adapters/codex/agents/sdlc-builder-l1.toml`, `adapters/codex/agents/sdlc-builder-l5.toml`.
- Docs: `plugins/sdlc-lite/AGENTS.md` (lines 17 and 18 name `overlays/<role>.md`) and `docs/references/sdlc-internals.md` (one sentence).

### How each was verified
Step 1 (verifier L2, pass; 12 criteria):
- The builder recorded 7 controls red before the first edit.
- `claude_roles.py selftest` printed 16 `ok: overlay:` lines and PASS.
- Both `generate --check` commands exited 0 (22 Claude files verified).
- `codex-selftest.py` and `check.py` exited 0.
- `git diff --quiet` on `agents/builder-L3.md` against base holds, and only the four builder L1/L5 generated files changed.
- The verifier ran two mutation controls in a throwaway copy:
  - With the insert line removed, 5 selftest cases failed.
  - With the denylist condition forced off, the "push" case failed.
- The verifier did not mutation-test `check.py` item 52. It read the three controls as correct.
- The builder checked the Codex refusal path by hand: an `## L9` section gave exit 2.

Step 2 (verifier L1, pass; 10 criteria):
- `bash plugins/sdlc-lite/scripts/check.sh` exited 0.
- `python3 scripts/check-packaging.py` printed PASS.
- `git diff --check` exited 0.
- The AGENTS.md grep counts 0 at base and matches now.
- A live dispatch of `claude -p --agent sdlc-lite:builder-L1` on a throwaway step exited 0. Its report has `## Status` and no `## At this level`. The generated `agents/builder-L1.md` carries exactly one `## At this level`.
- The scope guard passed, and builder-L3 is unchanged.

Process deviation (does not change the passing verdicts):
- Step 2's red controls were recorded retrospectively; see the first Warning above.

## Changelog entry
- Added per-level prompt overlays: `plugins/sdlc-lite/overlays/<role>.md` sections `## L<n>` are inserted into the generated Claude agents and Codex TOMLs as an `## At this level` block, and the generators refuse malformed overlays. The first overlays, for builder L1 and L5, change only those two agents. Other agents are byte-identical, and model and effort rows are unchanged. `check.py` item 52 guards overlay placement.

## Follow-ups
- note: T-0441's live run shows only that the builder-L1 dispatch ran, exited 0 and reported without the overlay heading. Whether the overlay changes builder behavior is left to the A/B in T-0442.
- note: Step 2's four (red) live-run criteria were recorded retrospectively, because step 1's changes already existed when `redck.py record` ran. A later multi-step task that edits files in step 1 and checks them in step 2 will hit the same deviation.
- note: `check.py` item 52 was not mutation-tested by the verifier. Its three controls were read, not broken, so the gate's bite rests on reading alone.
