## Task goal
Make `/file` close a finished ticketed task: refuse to close while the filer's Warnings are open (unless forced), file each follow-up bullet as a `proposed` idea ticket with `from: <id>`, set the ticket to `done`, regenerate the roadmap, and put the ticket id in the PR title. Publishing still needs the user's approval.

## Step 1: `tickets.py close <slug> [--force]` with selftest coverage
level: L3
### Do
Only `plugins/sdlc-lite/scripts/tickets.py` changes. Port the behavior of `close()` from `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/scripts/tickets.py` into this repo's structure: the `Fail` exceptions, `run()` dispatch, the `--root` argument, and `problems()` validation. Do not copy its module-level `ROOT` or its `SystemExit` style.
- Add `section(text, heading)`, which returns the body of `## <heading>` up to the next `## ` heading or EOF, stripped. It returns None if the heading is absent.
- Refactor `cmd_new` so it takes optional `origin` and `context`, or split out a shared helper that `close` also uses.
  - `origin` adds a `from: <id>` line inside the front matter, right after the `created:` line.
  - `context` replaces the body of the template's `## Context` section.
  - Keep today's validation: `problems(after)` must be empty before anything is written.
- Add `cmd_close(root, slug, force=False)`. It refuses with `Fail` and writes nothing in each of these cases:
  - `<root>/<slug>/handoff.md` is missing or has no front matter.
  - `problems(load(root))` is not empty.
  - The ticket's `status` is already `done`. The message says it is already closed, so a second close cannot file duplicate follow-ups.
  - The task dir has no `filer-L*.md`. The message names `/file`.
  - The newest `filer-L*.md` (by mtime, name as tie-break) has no `## Warnings` or no `## Follow-ups` section.
  - Warnings, compared case-insensitively with a trailing `.` stripped, is not `none` and `force` is false. The message includes the warnings text and mentions `--force`.
  - Follow-ups is not `None` but contains no top-level bullet (`-`, `*`, or `N.`/`N)`). Prose follow-ups must never be dropped silently.
- `cmd_close` then does the following:
  - Each top-level bullet becomes one ticket. Indented continuation lines join that bullet's text.
  - Each ticket is created from the `idea` template: `status: proposed`, `from: <parent id>`.
  - Title: the bullet text with markdown punctuation stripped, cut to at most 70 chars.
  - Slug: the first 5 lowercase alphanumeric words joined with `-` (fallback `follow-up`), with a `-2`, `-3`… suffix on collision.
  - Context: `Follow-up from <id> (<slug>/<filer file>):` plus the bullet text.
- After creating the tickets, set the parent's `status:` line to `done` with a single regex substitution that leaves the rest of the file byte-identical. Then regenerate `roadmap.md`. Return one line: `<id> done; N follow-up ticket(s): <slugs>`.
- Wiring:
  - `run()`: add a `close` branch.
  - argparse: add a `close` subparser (`slug`, `--force`).
  - Module docstring: add a usage line for `close`.
- Extend `selftest()` with these cases, each in its own copied fixture root:
  - (a) Filer file with Warnings `None` and two follow-up bullets, one with a backtick and one longer than 70 chars. After close: two new `type: idea`, `status: proposed` tickets with `from:` equal to the parent id; the parent is `status: done`; `check` returns 0.
  - (b) Warnings present, no force: rc 1 and no file changed (compare the handoff bytes, the ticket count, and the roadmap bytes).
  - (c) Case (b) with force: closes.
  - (d) Follow-ups `None`: zero tickets created and the parent is done.
  - (e) No filer file: refuses.
  - (f) Prose follow-ups with no bullets: refuses and writes nothing.
  - (g) A second close on a done ticket: refuses and creates no tickets.
  - (h) Two filer files with the older mtime holding warnings: the newest is used.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS` and exits 0.
- Fixture run by hand:
  1. `R=$(mktemp -d)/.sdlc`
  2. `tickets.py --root $R new feature parent "Parent"`
  3. Write `$R/parent/filer-L1.md` with `## Warnings\nNone\n\n## PR title\nx\n\n## Follow-ups\n- Add retry to fetch\n- Document the flag\n`.
  4. `tickets.py --root $R close parent` exits 0 and prints `T-0001 done; 2 follow-up ticket(s):`.
  5. `grep -l '^from: T-0001' $R/*/handoff.md | wc -l` is 2.
  6. `grep '^status: done' $R/parent/handoff.md` matches.
  7. `tickets.py --root $R check` exits 0.
- Same fixture with Warnings `step-2 verifier fail`: `close parent` exits 1, stderr names `--force`, `$R/parent/handoff.md` still has `status: proposed`, and no new ticket dir exists. With `--force` it exits 0.
- Negative control: temporarily make the warnings guard always pass (for example, change the comparison to always true). `selftest` must then report FAIL. Revert afterwards.
- `git diff --stat` touches only `plugins/sdlc-lite/scripts/tickets.py`.

## Plan risks (for reference)
- Only a real LLM run shows whether the filer obeys the bullet format. The step 1 refusal on prose follow-ups makes a non-compliant filer fail loudly rather than drop items, but it can block closes until the filer prompt is followed.
- This repo's own `.sdlc/` has no `roadmap.md`, and it may hold ticket dirs that fail `problems()` (for example, extra `source:` keys are fine, but a bad `depends` is not). Running `close` on the live repo could refuse for reasons unrelated to this change. The acceptance criteria use temp fixtures for that reason.
- mtime ordering of `filer-L*.md` can tie on a fast filesystem. The name tie-break covers it, but selftest case (h) must set mtimes explicitly (`os.utime`).
- The `status:` line is rewritten with a regex. A handoff whose body also has a line starting `status:` is safe only if the substitution is limited to the front matter block.
