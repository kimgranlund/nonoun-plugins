## Task goal
Document optional YAML front matter for task handoff.md files so a handoff can double as a ticket, without breaking handoffs that omit it.

Task brief: .sdlc/ticket-front-matter/handoff.md (paths in this step are relative to the repo root).

## Step 1: Document ticket front matter in skills/handoff-format
level: L1
### Do
Edit `plugins/sdlc-lite/skills/handoff-format/SKILL.md`. Add a new section (e.g. "Ticket front matter (optional)") before or after the "Task handoff" section, documenting the optional YAML block at the top of `.sdlc/<task>/handoff.md`:
- Fields: `id` (T-NNNN), `title`, `type` (feature|bug|chore|spike|idea), `status` (proposed|ready|blocked|done|dropped), `size` (S|M|L|XL), `priority` (P1|P2|P3), `depends` ([ids]), `created` (YYYY-MM-DD), `from` (origin ticket id, optional).
- State explicitly that `status` here is a person's decision and never tracks build progress (that stays derived by `/board`), matching the Non-goals in `.sdlc/tickets/T-0001-ticket-front-matter.md`.
- State that a handoff with no front matter keeps working unchanged (front matter is purely additive; `run.sh` and `board.py` do not require or parse it).
- Reference `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/.sdlc/_templates/*.md` and `CONTEXT.md` as the origin of the convention, and this repo's `.sdlc/tickets/T-*.md` as the in-repo examples.
### Acceptance criteria
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md` contains a section documenting all of: `id`, `title`, `type`, `status`, `size`, `priority`, `depends`, `created`, `from`, with their allowed values as listed above.
- The section states that front matter is optional and handoffs without it are unaffected.
- The section states that front matter `status` is not build progress and is distinct from `/board`'s derived status.
