<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/review-traces/SKILL.md: replaced the `## 4. Propose` placeholder. The section now has the `propose-handoff` template: Goal, a Context entry per finding (id, detector, summary, evidence, diagnose result, verify result), and per ticket the lines Repro, Expected, Actual and Red check. Its Constraints say drafts only, no code, no filing, and one L1 `## Step` per ticket. The section then runs `run.sh planner L2` once and says how each `## Step` of the result becomes a ticket draft.

## Checks
- `grep -qF 'planner L2' …SKILL.md`: pass
- The awk block extract with greps for `^Repro:`, `^Expected:`, `^Actual:` and `^Red check:`: pass
- `grep -qF 'quoted verbatim' …SKILL.md`: pass
- (guard) scope check against `$SDLC_BASE_SHA`: pass
- `git diff --check`: pass

## Notes
None
