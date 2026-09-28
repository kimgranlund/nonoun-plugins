<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add an sdlc-lite `open-questions` skill, ported from harness find-open-questions with no harness dependency, and run it as a close-out step at the end of /chain. It asks one batched AskUserQuestion round when a person is present and lists open items in the report when unattended. The conductor routes to it and CLAUDE.md lists it.

## Step 1: Add the open-questions skill
level: L2
### Do
Create `plugins/sdlc-lite/skills/open-questions/SKILL.md`. Port and trim it from `~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/find-open-questions/SKILL.md`. Match the shape of sibling skills such as `skills/clarify/SKILL.md`.

Frontmatter:
- `name: open-questions`
- A one-line `description:` with trigger phrases ("anything still open", "loose ends", "close this out") and NOT clauses that point only at sdlc-lite siblings (`/clarify` for pre-task ambiguity, `/ticket` for filing work).
- `argument-hint: [task dir]`
- `allowed-tools: Read, Grep, Glob, AskUserQuestion`

Body procedure:
1. Scan these sources for items still open:
   - `(gap: ...; default: ...)` lines in the task handoff's `## Intent` written by the /clarify flow.
   - `## Plan review` entries still unanswered.
   - Builder `## Notes`, verifier `## For the next attempt`, and filer output in the task dir that ask for a user decision.
   - Questions raised earlier in the session.
   Ground every item in something actually raised. Do not invent items.
2. If nothing qualifies, report one "nothing open" line and stop.
3. Otherwise make exactly ONE AskUserQuestion call with 1 to 4 questions of 2 to 4 options each. Put an option first as recommended only where a default or lean was actually stated. Otherwise leave the options unranked.
4. After the answers, resolve each item by name.

Failure branches:
- More than 4 items: ask the 4 most consequential and name the count of the rest in the question framing.
- A stale item is dropped. Stale means already asked in /file's own publishing round, or settled since.
- A decline is not re-asked in the session.
- Unattended (headless, `SDLC_HEADLESS=1`, `SDLC_ROLE` set, or no person present): never call AskUserQuestion. List the open items as plain lines in the final report, or say nothing is open.

Include one short good/bad example. The file must not contain the word `harness` or the names `write-handoff`, `find-intent`, `file-leftovers`, `close-session`, or `find-open-questions`, so leave out any provenance line. The provenance goes in CLAUDE.md in step 2. No em dashes.
### Acceptance criteria
- `test -f plugins/sdlc-lite/skills/open-questions/SKILL.md`
- `test "$(sed -n 1p plugins/sdlc-lite/skills/open-questions/SKILL.md)" = "---" && grep -qx 'name: open-questions' plugins/sdlc-lite/skills/open-questions/SKILL.md && grep -q '^description: ..' plugins/sdlc-lite/skills/open-questions/SKILL.md && grep -q '^allowed-tools:.*AskUserQuestion' plugins/sdlc-lite/skills/open-questions/SKILL.md`
- `test -f plugins/sdlc-lite/skills/open-questions/SKILL.md && ! grep -nE 'harness|write-handoff|find-intent|file-leftovers|close-session|find-open-questions' plugins/sdlc-lite/skills/open-questions/SKILL.md`
- `grep -qi 'nothing open' plugins/sdlc-lite/skills/open-questions/SKILL.md && grep -qi 'unattended' plugins/sdlc-lite/skills/open-questions/SKILL.md && grep -q 'Plan review' plugins/sdlc-lite/skills/open-questions/SKILL.md && grep -q 'gap:' plugins/sdlc-lite/skills/open-questions/SKILL.md`
- `test -f plugins/sdlc-lite/skills/open-questions/SKILL.md && ! grep -n '—' plugins/sdlc-lite/skills/open-questions/SKILL.md`
- Observable: the body describes one AskUserQuestion call with 1 to 4 questions of 2 to 4 options, recommended-first only where a default was stated, top 4 plus a count of the rest, stale items dropped, and a decline not re-asked.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0 (it runs `claude plugin validate`).

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

## Risks
- `claude plugin validate` may reject a frontmatter field in the new skill. The check.sh guard catches this.
- Placing the close-out after File could re-ask /file's publishing questions. The stale-item rule in both files covers this, but a verifier can only check it by reading the text.
- The "no harness reference" criterion also bans the word `harness` in the skill, so the provenance note has to live in CLAUDE.md.
