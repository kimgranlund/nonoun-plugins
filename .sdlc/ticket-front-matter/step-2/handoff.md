## Task goal
Document optional YAML front matter for task handoff.md files so a handoff can double as a ticket, without breaking handoffs that omit it.

Task brief: .sdlc/ticket-front-matter/handoff.md (paths in this step are relative to the repo root).

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
