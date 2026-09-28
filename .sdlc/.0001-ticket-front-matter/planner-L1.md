<!-- role=planner level=L1 model=sonnet effort=medium -->
Now I have everything I need. This is a small, well-scoped documentation task (S size), no decompose/design artifacts exist. Two clear steps: document the format, then verify board.py already handles it (confirmed by reading board.py — it never parses handoff.md content beyond `## Step` headers, so front matter is inert to it already; the "optionally add columns" is explicitly optional and not required by "Done when").

## Goal
Document optional YAML front matter for task handoff.md files so a handoff can double as a ticket, without breaking handoffs that omit it.

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

## Step 2: Confirm board.py renders with and without front matter, and check.sh passes
level: L1
### Do
No code change expected. Verify `plugins/sdlc-lite/scripts/board.py` already tolerates YAML front matter in a task's `handoff.md`:
- It only checks `(d / 'handoff.md').exists()` and scans task text with `re.search(r'^## Step (\d+): (.+)$', ...)`; front matter lines (`---`, `key: value`) do not match that pattern and are otherwise unread by `board.py`, so no code change is needed to satisfy the "renders a task with and without front matter" criterion.
- If a manual smoke check surfaces an actual rendering break (e.g. from `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc` against this task's own `handoff.md`, which now has front matter), fix `board.py` minimally to tolerate it; otherwise make no edit.
- Do not add id/status columns to `board.py` unless step 1's reviewer/user asks for it later; the ticket lists that as optional and out of Done-when scope.
- Run `plugins/sdlc-lite/scripts/check.sh` and confirm it passes.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc` runs without error and lists the `ticket-front-matter` task row, given this task's own front-matter-carrying `handoff.md`.
- `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc` (or against a task dir whose `handoff.md` has no front matter) also runs without error, showing pre-existing behavior is unchanged.
- `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Risks
None: the reference format, in-repo examples, and board.py's parsing logic were all read directly, and board.py's regex-based parsing already ignores YAML front matter, so this is a documentation-only change with no code path expected to move.
