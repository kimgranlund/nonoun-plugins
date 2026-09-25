<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add a recurring-finding rule to sdlc-lite's escalation doctrine. When the same finding comes back on a step after a rebuild that addressed it, the chain sends it to a planner L3 replan that questions the plan or rule. It does not bump the level, and the recurrence does not count toward a bump. The four named docs and their records stay consistent, and `check.py` guards the rule.

## Step 1: State the recurring-finding rule in the escalation docs
level: L2
### Do
Use the exact phrase `recurring finding` everywhere, so Step 2 can guard it. The definition: a verifier fail or a builder block that repeats the same class of finding as an earlier attempt on the same step (same criterion, same root cause), even though a rebuild or replan addressed it. Keep every level, model, and effort table and the `plan defect:` tag semantics unchanged.
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: extend the builder "Bump one level ..." paragraph, on that same line. A recurring finding goes to a planner L3 replan like `plan defect:`. It never bumps a level and never counts toward a bump. Most fails are ordinary, and the test fires only on a recurrence.
- `plugins/sdlc-lite/skills/chain/SKILL.md`, step 4 item 4 (the line starting `4. Verdict fail`):
  - Before "A second fail → bump", check whether the second fail is a recurring finding: same criterion and same root cause as the first fail's For the next attempt, after the rebuild addressed it.
  - If it is, append a `recurring finding:` entry quoting both notes to the task handoff's `## Plan review`, then take the 4.2 replan path: planner L3, supersede, split, continue. No bump, no `## Previous attempt`, and it does not count toward a bump.
  - Also add to item 2: a replanned step whose builder blocks again on the same finding is a recurring finding, recorded the same way.
- `plugins/sdlc-lite/agents/planner.md`: add rule 6 under "Criteria that can pass", as a numbered line containing `recurring finding`. When `## Plan review` holds a `recurring finding:` entry, first ask whether the criterion, the step, or a rule is wrong. The answer must be a concrete change: a rewritten criterion or step, or a reason the rule holds stated in the rewritten step's Do together with a changed Do. A replan that only adds commentary is not allowed. Do not touch the fenced `merge-step` block.
- `plugins/sdlc-lite/agents/conductor.md`: extend the `- Levels follow the level-rubric skill. Escalation follows /chain: ...` line. A recurring finding means a planner L3 replan that questions the plan or rule, never a level bump.
- Records to keep from going stale, in the same change:
  - `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, `## Plan review` description (near line 90): /chain also writes `recurring finding:` entries there.
  - Repo-root `CLAUDE.md`, the "A plan defect goes to a replan" decision bullet: one sentence on the recurring finding.
  - `.claude/agents/sdlc-lite-author.md`, the plan-defect route bullet: one clause on the recurring finding.
### Acceptance criteria
- `grep 'Bump one level' skills/level-rubric/SKILL.md | grep -q 'recurring finding'` (run from `plugins/sdlc-lite`)
- `grep -qE '^4\. .*recurring finding' skills/chain/SKILL.md` (run from `plugins/sdlc-lite`)
- `grep -qE '^[0-9]+\. .*recurring finding' agents/planner.md` (run from `plugins/sdlc-lite`)
- `grep '^- Levels follow' agents/conductor.md | grep -q 'recurring finding'` (run from `plugins/sdlc-lite`)
- `grep -q 'recurring finding' skills/handoff-format/SKILL.md` (run from `plugins/sdlc-lite`)
- `grep -q 'recurring finding' ../../CLAUDE.md` (run from `plugins/sdlc-lite`)
- Reading the four named files, they agree on these points:
  - A recurring finding goes to a planner L3 replan, not a bump, and never counts toward a bump.
  - The test fires only on a recurrence: same criterion and same root cause after an addressing rebuild.
  - The replan must land a changed criterion, step, or rule, never commentary only.
  - The `plan defect:` rules read as before.
- (guard) `git diff --quiet HEAD -- scripts/run.sh` (run from `plugins/sdlc-lite`)
- (guard) `! git diff HEAD -- skills/level-rubric/SKILL.md ../../CLAUDE.md | grep -qE '^[-+]\|'`: no table row changes (run from `plugins/sdlc-lite`)
- (guard) `scripts/check.sh` exits 0 (run from `plugins/sdlc-lite`)

## Step 2: Guard the rule's presence in check.py
level: L2
### Do
In `plugins/sdlc-lite/scripts/check.py`:
- Add a `'recurring finding'` key to `PLAN_DEFECT_DOCS`, covering `agents/planner.md`, `agents/conductor.md`, `skills/chain/SKILL.md`, `skills/level-rubric/SKILL.md`, and `skills/handoff-format/SKILL.md`.
- Extend docstring item 5 to name the recurring-finding rule.
- Update the `check.sh` line in the repo-root `CLAUDE.md` Commands section, and the author agent file, if they list what check.py guards.
### Acceptance criteria
- Negative control (run from `plugins/sdlc-lite`, writes only to a temp dir): `t=$(mktemp -d) && cp -R . "$t/p" && cp ../../CLAUDE.md "$t/p/" && sed -i '' 's/recurring finding/recurring-xx/g' "$t/p/agents/conductor.md" && ! python3 scripts/check.py "$t/p" >/dev/null; rc=$?; rm -rf "$t"; test $rc -eq 0`
- `grep -q "'recurring finding'" scripts/check.py` (run from `plugins/sdlc-lite`)
- (guard) `scripts/check.sh` exits 0 (run from `plugins/sdlc-lite`)
- (guard) `git diff --quiet HEAD -- scripts/run.sh` (run from `plugins/sdlc-lite`)

## Risks
- The Step 2 negative control is green on the current tree, not red: its compound `rc=$?; ...; test $rc -eq 0` form hides the failure. The inner `! python3 scripts/check.py` part is red now (exit 1 in the trial run), so the check does detect the missing guard. The verifier should read the whole command's exit code after the build.
- The criteria assume commands run from `plugins/sdlc-lite` and that the builder does not commit. If a lane commits before verification (fanout commits only after the driver), the `HEAD`-based guards compare against the wrong base.
- The criteria cannot mechanically check "same root cause"; that part rests on the verifier's reading.
- `planner.md` is also the planner's own prompt. An edit near the `merge-step` block could break check.py's identical-block guard, which the `check.sh` guard catches.
