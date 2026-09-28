<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Add an opt-in numbered-folder mode (`NNNN-<slug>`) to `scripts/tickets.py`'s `new`, `close`, and `check`, keeping plain-slug behavior byte-for-byte unchanged.

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

## Step 2: Numbered `close` follow-ups
level: L2
### Do
In the same file, add `--numbered` to the `close` subparser and thread `numbered` through `cmd_close` (same on/off rule as Step 1: flag or `<root>/config`). When on, each follow-up ticket created from a `## Follow-ups` bullet gets a numbered folder `{its-own-new-id:04d}-<base-slug>` instead of a bare `<base-slug>`, using each follow-up's own freshly stamped id (not the parent's id being closed). Keep the "plan everything first" no-partial-write structure and the existing collision-avoidance behavior (append `-2`, `-3`, ... on a name clash), now checked against the final numbered directory name. `close`'s own folder argument continues to be read as-is from disk (a plain or already-numbered name); this step is only about follow-up tickets it creates. Plain mode (no flag, no config) must remain byte-for-byte identical to today.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes, including a new case that closes a ticket with `--numbered` (or config) on and multiple `## Follow-ups` bullets, and asserts each created follow-up folder matches `^\d{4}-` with digits equal to that follow-up's own stamped `id`.
- A selftest case confirms `close` without `--numbered`/config still creates bare-slug follow-up folders exactly as before (negative control / no regression on existing close cases (a)-(h)).

## Step 3: `check` enforces the NNNN-/id match
level: L2
### Do
In `problems(ts)` (or a helper it calls) in `plugins/sdlc-lite/scripts/tickets.py`, add: for every ticket whose folder name matches `^\d{4}-`, its front matter `id` must equal `T-<those same 4 digits>`; append an error line (naming the slug) when it doesn't. This check runs unconditionally (not gated by numbered mode or config) and does not touch folders that don't start with 4 digits and a dash. Wire this into `cmd_check`, `cmd_new`'s and `cmd_close`'s existing `problems()` calls (no special-casing needed since it's just another rule in `problems`).

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes, including a new mutation case (alongside the existing `mutations` list style) where a folder named `NNNN-<slug>` has a front-matter `id` with different digits, and `check` fails naming the mismatch.
- A selftest case shows a correctly matching `NNNN-<slug>`/`id` folder passes `check`, and a plain-slug folder (no `NNNN-` prefix) is not subject to this rule (still passes with no prefix-related error).

## Step 4: Docs and full verification
level: L1
### Do
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: update `argument-hint` to mention `--numbered` on `new` and `close`, and add a rule line noting the `<root>/config` `ticket_folders: numbered` key and the always-on prefix/id check.
- `plugins/sdlc-lite/CLAUDE.md` (repo root `CLAUDE.md`), the `scripts/tickets.py` bullet: add a clause describing numbered mode (config key, `--numbered` flag, `NNNN-<slug>` naming, and that `check` always enforces prefix/id agreement).
- `.claude/agents/sdlc-lite-author.md`: update only if it describes `tickets.py new`/`close` command shapes; otherwise leave untouched.
- Do not touch `board.py`, roadmap rendering, or `.sdlc/` folder names in this repo (non-goals).

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes (full run, all cases from Steps 1-3 together).
- `plugins/sdlc-lite/scripts/check.sh` passes.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` (repo root) passes.
- `grep -n "numbered" plugins/sdlc-lite/skills/ticket/SKILL.md plugins/sdlc-lite/CLAUDE.md` shows the new mentions.

## Risks
`stamp()` currently computes the next id internally from `ts`, and `cmd_close` computes follow-up ids sequentially as it appends to `after`; Step 1 and Step 2 both need the numbered folder name to depend on an id known only after (or via replicating) that internal computation — a builder rushing this could compute the id twice and let the two calculations drift, or could check directory existence against the wrong name (bare vs. numbered) and let a rare collision through. If `<root>/config` doesn't exist yet anywhere in this repo or its fixtures, the parser must treat that as plain mode with no error, not fail — worth an explicit selftest case if one isn't already implied above.
