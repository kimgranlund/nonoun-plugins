## Task goal
Add an opt-in numbered-folder mode (`NNNN-<slug>`) to `scripts/tickets.py`'s `new`, `close`, and `check`, keeping plain-slug behavior byte-for-byte unchanged.

Task handoff (Intent, deltas, constraints): .sdlc/ticket-numbered-folders/handoff.md

## Step 1: Config parsing and numbered `new`
level: L3
### Do
In `plugins/sdlc-lite/scripts/tickets.py`:
- Add a small parser for `<root>/config` that recognizes a line `ticket_folders: numbered` (ignore blank/comment lines, no error if the file is absent or has other content).
- Add `--numbered` to the `new` subparser in `main()` and thread a `numbered` argument through `cmd_new`.
- In `cmd_new`, numbered mode is on when the config file says so OR `--numbered` is passed. When on: reject a `slug` that already matches `^\d{4}-` with a clear error naming the double-prefix problem; otherwise create the ticket folder as `{next-id:04d}-<slug>` instead of `<slug>` (front matter `id`, template stamping, and all other `stamp()` behavior stay the same — only the directory name changes). Keep the existing bare-slug `SLUG_RE` validation and pre-existence checks working against the final directory name.
- When numbered mode is off, folder naming is exactly today's behavior (bare `slug`).
- Add selftest cases in `selftest()`: `new` with `--numbered` (or config) produces `NNNN-<slug>`, where `NNNN` matches the stamped id's digits; `new` with an already-prefixed slug in numbered mode refuses and writes nothing; a negative control showing plain mode (`new` with no flag/config) still produces a bare-slug folder, unchanged from before this step.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes, and the new numbered-`new` and double-prefix and plain-mode-negative-control cases are present and pass (visible via added `expect(...)` labels in the failure list if broken).
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` (run from repo root) still passes, confirming this repo's plain-mode folders are unaffected.

## Risks (from the plan)
Compute each new id once and derive the folder name from it; check existence against the final (numbered) directory name. A missing `<root>/config` means plain mode with no error; cover that in selftest.
