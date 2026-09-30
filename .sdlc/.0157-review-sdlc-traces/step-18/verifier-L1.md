<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `head -1 ... | grep -qx -- '---'`: pass. Ran it on the built tree and it printed 1. The file starts with `---`.
- `grep -q '^name: review-traces$'`: pass. Printed 2. The `name:` line is in the frontmatter.
- `grep -qF '../sdlc-lite/SKILL.md'`: pass. Printed 3. The Codex host line names it.
- `archaeologist L1` and `scout L1`: pass. Printed 4. Both strings appear in section 2.
- `clusters --max`, `traces.py ingest`, `traces.py detect`: pass. Printed 5. All three appear in section 1.
- The awk over the `cluster-question` fence, then `grep -q '^## Question$'`: pass. Printed 6. The `## Question` heading sits inside the fence.
- The awk over the fence, then grep for `Read only the evidence paths listed above; nothing else.`: pass. Printed 7. The sentence is inside the fence.
- `grep -qF 'SDLC_ROUTING_REASON'`: pass. Printed 8. The line is present.
- (guard) scope: pass. Printed 9 with `SDLC_BASE_SHA` read from the step's `base-sha` file. `git diff --name-only` shows only `.gitignore` and `plugins/sdlc-lite/scripts/check.sh`. The new `SKILL.md` matches the allowed `review-traces/.*` pattern.
- Content beyond the greps: I read the whole file and compared it to `dig/SKILL.md`. The frontmatter has the `description`, `argument-hint`, and `allowed-tools` the Do asked for. The review-task-dir instruction is there. Sections 1 and 2 match the Do. Sections 3 to 5 are placeholders.
- Bite check: every check is a `grep` or `awk` on a fixed path. With the file missing, `grep` exits nonzero, so the check goes red. I did not run a separate negative control.

Steelman: I drafted "the builder edited `.gitignore` and `check.sh`, which are outside the step's files". The rebuttal holds. The guard's allowlist names both, and other steps in this task modified them. I dropped the finding.

## Out of scope changes
None from this step. `.gitignore` and `check.sh` show as modified, but both are on the guard's allowlist, and the guard passes.

## For the next attempt
None
