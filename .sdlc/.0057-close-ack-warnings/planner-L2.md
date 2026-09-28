<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add `tickets.py close --ack-warnings TEXT`. It passes the open-warnings gate the way `--force` does, still files follow-ups like a normal close, and appends a `## Closed` section to the ticket handoff.md holding the date, the reason and the acknowledged Warnings quoted verbatim. Then sync the docs that describe close flags.

## Step 1: Implement `--ack-warnings` in tickets.py with selftest cases
level: L3
### Do
In `plugins/sdlc-lite/scripts/tickets.py`:
- `cmd_close(...)`: add a keyword parameter `ack_warnings=None`, and describe it in the docstring. Behavior:
  - Early refusals. Each writes nothing and runs before any file is read or written, next to the existing `--reason` combination check at the top:
    - `ack_warnings is not None and force` refuses with a message naming `--ack-warnings` and `--force`.
    - `ack_warnings is not None and reason is not None` refuses with a message naming `--ack-warnings` and `--reason`.
    - `ack_warnings is not None and not ack_warnings.strip()` refuses: "empty --ack-warnings; ...; nothing written".
    - End every message with `nothing written`.
  - Filer path, at the current warnings gate (around line 597):
    - If `ack_warnings is not None` and `is_none(warnings)`, refuse. Say there are no open warnings to acknowledge and tell the user to rerun without `--ack-warnings`. Write nothing. This holds for `--dry-run` too.
    - If warnings are open and neither `force` nor `ack_warnings` is set, refuse. The message now names `--ack-warnings "<why>"` first and `--force` second, e.g. `(rerun with --ack-warnings "<why>" to record why they no longer apply, or --force to override)`. It still includes the warnings text.
    - When warnings are open and `ack_warnings` is set, the gate passes. Everything after it is unchanged: follow-up planning, duplicates, `--skip`/`--expect`, the dry-run listing and digest, numbered archive rename.
  - Write phase. Only when not dry_run, after the `if dry_run: return` line. Build the handoff body the same way the `--reason` branch does:
    - Take the body `raw[fm.end():]` and add a trailing newline if it lacks one.
    - Append `\n## Closed\n\n<YYYY-MM-DD>: warnings acknowledged: <why>\n\n` followed by each line of the filer's Warnings section, prefixed with `> ` (a blockquote; use `>` alone for blank lines). The warnings text appears verbatim after the prefix.
    - Write `head + body` in place of the current `head + raw[fm.end():]`, still before the archive rename.
  - Output line: append `; warnings acknowledged: <why>` to the success message. Dry-run output may add a line such as `ack warnings: <why>`, but the last line must stay `expect <digest>`.
- `main()`: add `p.add_argument('--ack-warnings', metavar='TEXT', help=...)`, saying it closes while filer warnings are open, records TEXT and the quoted warnings in a `## Closed` section, files follow-ups as normal, and refuses with `--force`, with `--reason`, with empty TEXT, or when no warnings are open. Pass `kw['ack_warnings'] = a.ack_warnings` for `close`. Update the `close` subparser help if it lists modes.
- Module docstring: add `[--ack-warnings TEXT]` to the Usage line, and add a paragraph under `close` describing the behavior and refusals above.
- `selftest()`, close section, after case (o) or at the end of the close cases. Add new lettered cases (e.g. `(w1)`..`(w8)`), using the existing `case`, `filer`, `snap`, `status`, `fresh` helpers and the `warned` fixture (`'step-2 verifier fail'`, one follow-up):
  1. An ack close with open warnings: rc 0, status done, 1 new follow-up ticket, handoff ends with a `## Closed` section containing today's date, `warnings acknowledged: committed later`, and `> step-2 verifier fail`. `check` passes afterwards.
  2. A multi-line Warnings section (two bullet lines) is quoted line by line, verbatim after the `> `.
  3. `--ack-warnings` with `force=True` refuses and writes nothing (`snap` unchanged).
  4. `--ack-warnings` with `reason=` refuses and writes nothing.
  5. Empty `''` and whitespace `'   '` TEXT each refuse and write nothing.
  6. With filer Warnings `None`, `--ack-warnings` refuses, names rerunning without `--ack-warnings`, and writes nothing. Run it both plain and with `dry_run=True`.
  7. `dry_run=True` with `--ack-warnings` on open warnings: rc 0, last line starts `expect `, and `snap` unchanged.
  8. `--ack-warnings` with `--skip`/`--expect` from a dry run files only the unskipped follow-ups.
  9. Numbered mode (`--numbered` on a `NNNN-` folder, reusing the `numbered_x`-style fixture if practical): ack close renames to `.NNNN-<slug>`, and the moved handoff holds the `## Closed` section.
  10. Refusal wording: extend case (b) (keep its existing asserts) or add a new case asserting that `--ack-warnings` appears in err before `--force`.
- Leave all existing selftest cases unchanged, apart from adding asserts.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS` and exits 0.
- `grep -n "ack_warnings\|ack-warnings" plugins/sdlc-lite/scripts/tickets.py` shows the parameter in `cmd_close`, the argparse flag, the Usage line, and at least 8 selftest asserts.
- Negative control: temporarily turning the ack gate into a no-op (treating ack as not set) makes the selftest fail on the new cases. The verifier does this in a throwaway worktree (`git worktree add`), not in the build tree.
- Manual run in a temp dir. Copy a ticket `.sdlc` with a `filer-L1.md` whose Warnings is `nothing committed yet` and whose Follow-ups is `- Add retry`. Then `python3 plugins/sdlc-lite/scripts/tickets.py --root <tmp>/.sdlc close <slug> --ack-warnings "committed later"`:
  - exits 0
  - the ticket front matter is `status: done`
  - one new idea ticket exists
  - handoff.md ends with `## Closed`, `<today>: warnings acknowledged: committed later`, and `> nothing committed yet`
- In the same kind of temp setup:
  - `close <slug>` (no flags) exits 1, and stderr contains `--ack-warnings` before `--force`
  - `close <slug> --ack-warnings x --force` exits 1 and changes no files
  - `close <slug> --ack-warnings "  "` exits 1 and changes no files
- `python3 plugins/sdlc-lite/scripts/tickets.py close --help` lists `--ack-warnings TEXT`.

## Step 2: Sync docs for `--ack-warnings`
level: L1
### Do
- `plugins/sdlc-lite/skills/file/SKILL.md` step 3.1: replace the open-warnings sentence. On a refusal for open Warnings, show the warnings and ask with AskUserQuestion, with three options:
  - "Leave open" (recommended, first): stop.
  - "Acknowledge with a reason": the user supplies the why, then add `--ack-warnings "<why>"` to every later call (dry run and real close).
  - "Force close": add `--force` to every later call.

  Also state that an unattended run stops on open warnings and never acks or forces.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`:
  - `argument-hint`: add `[--ack-warnings "<why>"]`.
  - Item 4: add a sentence covering what `--ack-warnings "<why>"` does, what it refuses, and its dry-run behavior. It closes while warnings are open, files follow-ups normally, and appends a `## Closed` section with the date, the reason and the quoted warnings. It refuses with `--force` or `--reason`, with empty text, or when no warnings are open. With `--dry-run` it passes the gate and writes nothing.
- Repo `CLAUDE.md`, the `scripts/tickets.py` paragraph under Layout: add one clause for `close --ack-warnings "<why>"`, with the same facts and in the same style as the `--reason` clause.
- `.claude/agents/sdlc-lite-author.md` line 16: add a sentence keeping `--ack-warnings` in sync across tickets.py, the /ticket skill, the /file skill, and CLAUDE.md.
- No em dashes in any edited text.
### Acceptance criteria
- `grep -c -- "--ack-warnings" plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` reports at least 1 for every file.
- `grep -n "Acknowledge with a reason" plugins/sdlc-lite/skills/file/SKILL.md` matches, and on that step the options appear in this order: "Leave open", then "Acknowledge with a reason", then "Force close".
- `grep -n "never acks or forces\|never ack" plugins/sdlc-lite/skills/file/SKILL.md` matches, because the unattended rule is stated.
- `grep -nP "\x{2014}" <edited files>` finds no new em dashes on the changed lines (`git diff | grep -P "^\+.*\x{2014}"` is empty).
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The only warning allowed is the existing validate warning about CLAUDE.md.

## Risks
- The format of the quoted warnings (a `> ` blockquote) is my choice. The handoff says only "quoted verbatim". A later `## Closed` parser or /board could expect another shape.
- If the filer's Warnings section contains a `## ` heading-like line, the blockquote prefix keeps it inside the section, but raw copying without the prefix would break the section structure. The builder must use the prefix.
- `check.sh` may enforce doc wording elsewhere that I did not find. `check.py` greps showed no ticket-flag enforcement.
