## Task goal
Add an opt-in numbered-folder mode (`NNNN-<slug>`) to `scripts/tickets.py`'s `new`, `close`, and `check`, keeping plain-slug behavior byte-for-byte unchanged.

Task handoff (Intent, deltas, constraints): .sdlc/0016-ticket-numbered-folders/handoff.md

## Step 3: `check` enforces the NNNN-/id match
level: L2
### Do
In `problems(ts)` (or a helper it calls) in `plugins/sdlc-lite/scripts/tickets.py`, add: for every ticket whose folder name matches `^\d{4}-`, its front matter `id` must equal `T-<those same 4 digits>`; append an error line (naming the slug) when it doesn't. This check runs unconditionally (not gated by numbered mode or config) and does not touch folders that don't start with 4 digits and a dash. Wire this into `cmd_check`, `cmd_new`'s and `cmd_close`'s existing `problems()` calls (no special-casing needed since it's just another rule in `problems`).

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes, including a new mutation case (alongside the existing `mutations` list style) where a folder named `NNNN-<slug>` has a front-matter `id` with different digits, and `check` fails naming the mismatch.
- A selftest case shows a correctly matching `NNNN-<slug>`/`id` folder passes `check`, and a plain-slug folder (no `NNNN-` prefix) is not subject to this rule (still passes with no prefix-related error).
