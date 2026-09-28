<!-- role=verifier level=L1 model=sonnet effort=medium -->
All three acceptance criteria verified directly against the diff. No test needed (docs-only, criteria are static grep-able facts). Check for out-of-scope changes: diff only touches the one file plus new untracked artifacts dir (expected). Also note there's a verifier-L1.running artifact leftover but that's my own run state.

## Verdict
pass

## Criteria
- SKILL.md contains a section documenting all of id, title, type, status, size, priority, depends, created, from with allowed values: pass. Evidence: `git diff plugins/sdlc-lite/skills/handoff-format/SKILL.md` shows new "## Ticket front matter (optional)" section with the YAML block listing `id: T-NNNN`, `title`, `type: feature|bug|chore|spike|idea`, `status: proposed|ready|blocked|done|dropped`, `size: S|M|L|XL`, `priority: P1|P2|P3`, `depends: [T-NNNN, ...]`, `created: YYYY-MM-DD`, `from: T-NNNN`.
- The section states front matter is optional and handoffs without it are unaffected: pass. Evidence: same diff, line "Front matter is purely additive: a handoff with no front matter keeps working unchanged, and neither `run.sh` nor `board.py` requires or parses it."
- The section states front matter `status` is not build progress and is distinct from `/board`'s derived status: pass. Evidence: same diff, "`status` here is a person's decision ... It never tracks how far a task got through the roles; that stays derived by `/board` from `.sdlc/` run state. The two are independent: a ticket can sit at `status: ready` while `/board` shows no runs yet, or `status: blocked` while a step has already built."

## Out of scope changes
None. `git status` shows only `plugins/sdlc-lite/skills/handoff-format/SKILL.md` modified (matches step scope) plus the untracked `.sdlc/0001-ticket-front-matter/` artifacts directory, which is expected run output, not a source change.

## For the next attempt
None.
