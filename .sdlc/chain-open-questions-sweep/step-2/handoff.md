## Task goal
A /chain run ends with one batched AskUserQuestion round for everything left unresolved.

## Step 2: Wire the close-out into /chain, the conductor, and CLAUDE.md
level: L2
### Do
1. In `plugins/sdlc-lite/skills/chain/SKILL.md`, add a section `## 6. Close out` between `## 5. File` and `## Report`. It runs the /open-questions flow (`${CLAUDE_PLUGIN_ROOT}/skills/open-questions/SKILL.md`) on the task dir after File:
   - Interactive: one batched AskUserQuestion round for everything left unresolved.
   - Unattended (headless, no person present): never call AskUserQuestion. List the open items as plain lines in the final report, or say nothing is open.
   - Items already asked in /file's publishing round are stale and dropped.
   Add `AskUserQuestion` to the chain's `allowed-tools`. Keep every existing word that check.py requires (`interactive`, `run_in_background`, `notification`, `sleep`, `SDLC_HEADLESS`, `plan defect`, `Plan review`, `recurring finding`) intact.
2. In `plugins/sdlc-lite/agents/conductor.md` under `## Route every ask`, add one line routing "anything still open", loose-ends, or close-out asks to `/sdlc-lite:open-questions`.
3. In the repo-root `CLAUDE.md` Layout bullet that lists the skills (line 33), add `/open-questions` as a skill that runs in your session and batches unresolved items into one AskUserQuestion round, and that /chain runs it as its close-out. Extend the "Modernized from harness ..." provenance to name harness find-open-questions.
4. `.claude/agents/sdlc-lite-author.md` has no skill list, so leave it unchanged.

No em dashes in the added text.
### Acceptance criteria
- `awk '/^## 5\. File/{f=1} f&&/open-questions/{a=1} f&&/AskUserQuestion/{b=1} f&&/[Uu]nattended/{c=1} END{exit !(a&&b&&c)}' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q '^allowed-tools:.*AskUserQuestion' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q '/sdlc-lite:open-questions' plugins/sdlc-lite/agents/conductor.md`
- `grep -q '/open-questions' CLAUDE.md`
- `test -z "$(git diff -U0 -- plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/agents/conductor.md CLAUDE.md | grep '^+' | grep '—')"`
- Observable: in the chain's new close-out section, the interactive branch asks one AskUserQuestion round and the unattended branch lists the items in the final report without calling AskUserQuestion.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0.
