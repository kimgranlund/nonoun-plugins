<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0086: Close-out sweep at the end of /chain: batch unresolved items into one AskUserQuestion round

## PR body
### Summary
Every /chain run now ends with a close-out step. If a person is present, the step asks one batched AskUserQuestion round covering everything still unresolved. In an unattended run it lists the open items as plain lines in the final report, or says nothing is open. The logic lives in a new sdlc-lite skill, `open-questions`. It is ported from harness find-open-questions, so sdlc-lite no longer depends on the harness plugin for this.

### Changes
- `plugins/sdlc-lite/skills/open-questions/SKILL.md` (new)
  - Frontmatter: `name`, trigger-phrase `description`, `argument-hint: [task dir]`, `allowed-tools: Read, Grep, Glob, AskUserQuestion`.
  - Sources it scans: `(gap: ...; default: ...)` lines in the Intent, unanswered `## Plan review` entries, builder, verifier, and filer notes that ask for a decision, and questions raised earlier in the session.
  - When nothing is open, it reports one "nothing open" line.
  - Otherwise it makes exactly one AskUserQuestion call with 1 to 4 questions of 2 to 4 options. An option goes first as recommended only where a default was stated. With more than 4 items, it asks the top 4 and names how many are left.
  - Stale items are dropped, and a declined question is not asked again.
  - Unattended (`SDLC_HEADLESS`, `SDLC_ROLE`, or no person present): it never calls AskUserQuestion.
  - It includes a good/bad example and does not mention any harness skill.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: new `## 6. Close out` section between `## 5. File` and `## Report`, with the interactive and unattended branches. Items already asked in /file's publishing round are dropped as stale. `AskUserQuestion` is added to `allowed-tools`.
- `plugins/sdlc-lite/agents/conductor.md`: new route line that sends "anything still open", loose-ends, and close-out asks to `/sdlc-lite:open-questions`.
- `CLAUDE.md`: `/open-questions` added to the Understand skills list, noting that /chain runs it as its close-out. The provenance list now names harness find-open-questions.

### Verification
- Step 1 (new skill): builder L2, verifier L1 **pass**.
  - Checked by command: the file exists, frontmatter fields are present, no harness names, the required phrases are there, no em dashes.
  - The verifier read the body and confirmed the one-call and 1 to 4 limits, recommended-first only on a stated default, top 4 plus a count, stale items dropped, no re-asking, and the unattended branch.
  - `scripts/check.sh` exited 0, including shellcheck and `claude plugin validate`.
- Step 2 (wiring): builder L2, verifier L1 **pass**.
  - All three greps pass: the awk check on the chain close-out section, `allowed-tools`, and the conductor route. The chain and conductor greps also fail on HEAD, so they can catch a regression.
  - The `/open-questions` grep on CLAUDE.md passes, and no added lines contain an em dash.
  - The verifier read the interactive and unattended branch text.
  - `scripts/check.sh` exited 0.
- Not tested: an actual run of the skill during a live /chain close-out. The checks cover the file text only.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `/sdlc-lite:open-questions`, which collects unresolved items into one AskUserQuestion round (or lists them in the report when unattended). `/chain` now runs it as a close-out step after File, and the conductor routes "anything still open" asks to it. (T-0086)

## Follow-ups
- Run a real /chain close-out, both interactive and headless, to confirm open-questions asks one round, drops items /file already asked about, and never calls AskUserQuestion when unattended (so far only the text has been checked)
