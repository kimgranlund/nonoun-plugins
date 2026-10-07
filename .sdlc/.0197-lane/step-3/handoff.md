## Task goal
Add `steps.py lane`, extract `review_required()`, and write the lane and skip history to skips.md.

## Step 3: Lane guidance in the Codex host, chain, and handoff-format skills, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets are `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`, `plugins/sdlc-lite/skills/chain/SKILL.md`, and `plugins/sdlc-lite/skills/handoff-format/SKILL.md`. This is also the gates green step for the ticket. Depends on: step 2.

Settled decisions:
- **Codex host skill.** It has no `steps.py` mention today (design.md:171). Insert a new section headed `Lane per ticket` (a level-2 heading) after the `## Host translations` section and before the `## Native execution` section, with exactly this paragraph:

  Before work on a ticket, run `python3 "<plugin-root>/scripts/steps.py" lane <ticket dir>` and follow its first line: `fix` means the fix workflow, `lean` the lean chain in the chain workflow, and `full` the chain workflow. Run it again after the planner result and after every append to the ticket handoff's `## Plan review` section; a lean ticket that meets a mandatory condition prints `full` from then on. Each run appends its result to `<ticket dir>/skips.md`, and its `reason:` lines name the facts that decided it.

  Add no links, so check-packaging's link check is unaffected. The lane rules stay in steps.py, their one location.
- **Chain skill sentence.** `skills/chain/SKILL.md:27` reads "What the code computes today: no script computes the lane yet. ...". Step 2 makes that false, and the handoff's Done-when requires affected guidance to be updated. Replace that whole line with exactly:

  What the code computes: `steps.py lane <task dir>` prints `fix`, `lean`, or `full` from these conditions, one `reason:` line per deciding fact, and appends each result to the task's `skips.md`; `steps.py lint` warns on step and criterion counts.

  Leave the rest of the Lean chain section unchanged. T-0199 owns the conductor and chain run rules. T-0199 depends on T-0198, which depends on this ticket, so the two never edit the file at once.
- **Task-folder layout.** `skills/handoff-format/SKILL.md` lines 10-35 hold the `## Layout` fenced block that lists every file a task dir may hold, and it has no `skips.md` entry today. Step 2 makes `steps.py lane` write `<task>/skips.md` into a ticket folder, so the layout record must name it (the plan review's goal-coverage finding). Insert exactly this one line inside that fenced block, directly after the line that starts `  runs.jsonl` and before the line `  step-1/`. It is two spaces, `skips.md`, then 14 spaces, so its description starts at column 24 like `  runs.jsonl            one line per run: ...`:

```
  skips.md              lane history: one "- lane:" line per steps.py lane run, under ## Lane
```

  Change nothing else in the file. check.py reads handoff-format only for phrase routes and the separate `merge-step` fenced block (check.py:126-207), so this line affects neither. The record format itself stays in the steps.py docstring, its one location.
- **No regeneration expected.** None of the three skill bodies is embedded in a generated Codex agent: a grep of `adapters/codex/agents/*.toml` for their text finds none. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` only if `--check` reports drift.
- **Gates.** Run every gate below. Fix any red that steps 1 or 2 introduced, inside the allowed files. All gates were green at the build-start HEAD at plan time. `check.sh` took 234s in the latest probe.

Focused checks: the gate commands below.
### Acceptance criteria
- `grep -qF 'steps.py" lane' plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `grep -qF "skips.md" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `! grep -qF "no script computes the lane yet" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF "steps.py lane" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qE "^  skips\.md +lane history: .*steps\.py lane" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (guard) `! grep -qF "—" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/scripts/steps.py docs/references/sdlc-internals.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/skills/sdlc-lite/SKILL\.md|plugins/sdlc-lite/skills/chain/SKILL\.md|plugins/sdlc-lite/skills/handoff-format/SKILL\.md|plugins/sdlc-lite/scripts/steps\.py|docs/maintenance/sdlc-internals\.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml)$" | grep -q .`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
