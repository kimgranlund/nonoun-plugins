<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/review-traces/SKILL.md`: replaced the `## 3. Verify` placeholder with the verify stage. It holds the fenced `finding-step` template (`## Task goal`, `## Step 1: Reproduce finding <id>`, `level: L1`, `### Do` stating there is nothing to build, and `### Acceptance criteria` with `<evidence command>`), the rules for rendering evidence into commands, the `steps.py lint` call, the `run.sh verifier L1` call, the fail/pass/no-verdict handling, and the rule that a finding whose evidence cannot be rendered is dropped before any run.

## Checks
- `grep -qF 'verifier L1' plugins/sdlc-lite/skills/review-traces/SKILL.md`: exit 0
- `grep -qF 'steps.py lint' plugins/sdlc-lite/skills/review-traces/SKILL.md`: exit 0
- `grep -qF 'drops the finding from the propose list' plugins/sdlc-lite/skills/review-traces/SKILL.md`: exit 0
- The awk/sed template extraction, the two greps, and `steps.py lint`: printed "steps lint: ok", exit 0
- (guard) scope check: exit 0
- `git diff --check`: exit 0

## Notes
Dropped findings are sent to the stage 5 report with their reason. That section is still a placeholder until step 21 fills it.
