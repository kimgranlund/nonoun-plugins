<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'planner L2' plugins/sdlc-lite/skills/review-traces/SKILL.md`: pass. Evidence: it exits 0. The section 4 text reads "Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh planner L2 <propose handoff.md>`".
- The awk extract of the `propose-handoff` fence, with greps for `^Repro:`, `^Expected:`, `^Actual:` and `^Red check:`: pass. Evidence: I ran each grep separately and all four printed ok. As a negative control, the same awk pointed at a nonexistent fence name made the `^Repro:` grep fail. That shows the extraction is what the check depends on.
- `grep -qF 'quoted verbatim' plugins/sdlc-lite/skills/review-traces/SKILL.md`: pass. Evidence: it exits 0. It matches the line "Actual: <quoted verbatim from the finding summary and evidence>" and the section's intro text.
- (guard) scope: pass. Evidence: I ran the command with `SDLC_BASE_SHA` read from the step's `base-sha` file. The list of files changed against that sha, excluding `.sdlc`, matched only the allowed patterns, so the command exited 0 and printed "guard".

I also read section 4 against the Do. It has Goal, Context (id, detector, summary, evidence, diagnose result path, verify result path) and the four required lines. Constraints say drafts only, no code, no filing, and one L1 `## Step` per ticket. The planner L2 run and the mapping of each Step to a ticket draft are described.

## Out of scope changes
None. `git diff --stat` shows `.gitignore`, `plugins/sdlc-lite/scripts/check.sh` and `.sdlc/.../handoff.md`. The first two are on the guard's allow-list, and the `.sdlc` files are excluded from scope.

## For the next attempt
None
