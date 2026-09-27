<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - New `TAG_RE`, `follow_tag` (untagged counts as `decide`) and `append_notes` (writes `<root>/notes.md`).
  - `cmd_close`: new `ticket=` parameter enforcing the one-ticket cap and its refusals; tag-aware title, slug, duplicate check and context; notes.md written in the write phase; new dry-run line marks (`ticket`, `note`); new success line: `follow-up ticket: <name>|none; <k> follow-up(s) appended to notes.md`.
  - `--reason` now also refuses with `--ticket`.
  - `main`: `close --ticket N` (`type=int`) added and passed through; close help, `--reason`, `--dry-run` and `--expect` help updated.
  - Module docstring `close` entry and usage line rewritten.
  - Selftest: cases (a), (c), (i), (p), (q), (s), (s2), (t), (v2), (u), (w1), (w8) and the worktree close/dry-run cases rewritten to the cap.
  - Selftest: new `close_one`/`notes` helpers and 18 `(cap)` expects.
  - Selftest: two fixture reads hardened (`long_title`, and the `(cap)` context read) so a mutation turns cases red instead of crashing the run.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: argument-hint gains `[--ticket N]`. Step 4 now states the tags, the cap, `--ticket`, notes.md, the dry-run marks and the new `--skip` meaning. The numbered-mode rule now says close numbers its one follow-up ticket.
- `CLAUDE.md` (repo root): the `scripts/tickets.py` bullet now covers the tags (untagged = decide), the cap, `--ticket N`, the notes.md format, the dry-run marks and the `--skip` meaning.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: one sentence in section 4 saying fanout's close is the plain form, so a lane files no follow-up ticket and every item lands in `notes.md` on the integration branch.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py close --help | grep -q -- '--ticket'`: rc 0
- Criterion 2 (two decide items and a note, `--ticket 1 --expect`): rc 0
- Criterion 3 (plain close with decide, fix-now and untagged items: zero folders, all in notes.md, status done): rc 0
- Criterion 4 (`--ticket 2` on a note item refuses, no notes.md, status proposed): rc 0
- Criterion 5 (`--dry-run --ticket 2` gives `1. ... note`, `2. ... ticket`, and `expect` as the last line): rc 0
- Criterion 6 (numbered: `0002-untagged-legacy-item`, `.0001-alpha`, `note: keep` in notes.md, check passes): rc 0
- Criterion 7 (`--ticket 1` without `--expect` refuses naming `--expect`, no notes.md): rc 0
- `grep -q '(cap)' plugins/sdlc-lite/scripts/tickets.py`: rc 0
- `grep -q -- '--ticket' plugins/sdlc-lite/skills/ticket/SKILL.md`: rc 0
- `grep -q 'notes.md' plugins/sdlc-lite/skills/ticket/SKILL.md`: rc 0
- `grep -q -- '--ticket' CLAUDE.md`: rc 0
- `grep -q 'notes.md' CLAUDE.md`: rc 0
- `grep -q 'notes.md' plugins/sdlc-lite/skills/fanout/SKILL.md`: rc 0
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: `tickets selftest: PASS`, rc 0
- Negative controls: I mutated `tickets.py` one rule at a time and confirmed each new `(cap)` expect goes red. I ran the mutations in place from a backup and checked with `cmp` that the file was restored afterwards.
  - M1 notes never written, M2 tag gate off, M3 no tag parsing, M4b plain close files item 1, M5 `--ticket` needs no `--expect`, M6 `--ticket` allowed inside `--skip`, M7 duplicate allowed as ticket.
  - M8 dry run writes notes, M9 `--reason` accepts `--ticket`, M10 untagged not treated as decide, M11 context keeps the tag, M12 digest over text only, M13 numbered name ignored, M15 digest ignores tags.
  - Each of these produced at least one named `(cap)` miss.
  - M14 (no range check) crashed the selftest with IndexError, which also exits red.
- `plugins/sdlc-lite/scripts/check.sh` (a wider check than the criteria ask for): rc 0. Tickets, steps, order, fanout, run and hook selftests pass, and so do the hook live-probe selftest, shellcheck and plugin validate.

## Notes
- **Refusal wording.** The tag refusal reads `--ticket N is a <tag>: item; only a decide: item can become a ticket; nothing written`. It names only the item's own tag, so a fix-now refusal does not contain the word "note". Other `--ticket` refusals use the phrases `is out of range`, `is also in --skip`, `already tracked by T-NNNN (<slug>)` and `--ticket needs --expect`. The `--reason` refusal starts `--reason files no follow-ups`.
- **Dry-run line formats.** Skip and duplicate lines keep `[<base>]`, as today: `<i>. <tag>: <title> [<base>] skip (--skip)`. Note lines carry no slug (`<i>. <tag>: <title> note`).
- **The notes.md heading uses the ticket id and title only, never a slug.** Item text is written as the filer gave it, so notes.md contains a path only if a follow-up's own text mentions one.
- **Duplicates.** A duplicate item is still skipped whatever its tag, including `note:` and `fix-now:`, and is named in the output but written nowhere, as the handoff specifies.
- **Out of scope.** `plugins/sdlc-lite/skills/handoff-format/SKILL.md` still says close stamps `from:` on "each follow-up idea ticket it creates". That is still true with at most one, so I left it. `skills/file/SKILL.md` is step 2's job. `fanout.py` is unchanged.
- **Pre-existing change.** `.sdlc/finish-in-session/handoff.md` was already modified before this build; I did not touch it. No commits were made.
