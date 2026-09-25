<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - New helpers `norm_title`, `strip_prefix` and `parse_skip`.
  - `cmd_close` gains `dry_run` and `skip`, a `--reason` conflict refusal, a `--skip` range refusal, the duplicate check, dry-run output, and the extended real-close output.
  - `close` parser gains `--dry-run` and `--skip`, with updated help strings.
  - `main()` parses `--skip` and turns a bad token into a refusal.
  - Module docstring: extended Usage line and `close` paragraph.
  - New selftest cases (p) through (t).

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: `tickets selftest: PASS`, rc 0. Existing cases (a) through (o) are unchanged and still pass.
- Mutation checks. I replaced each condition with `if False:`, ran selftest, then restored the file; `cmp` confirmed the restore:
  - `if dry_run:` (dry run falls through to a real close): rc 1, (p) in stderr.
  - `if i in skipped:` (skip ignored): rc 1, (q) in stderr.
  - `if not 1 <= i <= len(items):` (out-of-range check dropped): rc 1, six (r) lines in stderr.
  - `if dup:` (duplicate check disabled): rc 1, (p) and (s) in stderr.
- Manual run in a `mktemp` root, set up as the handoff describes:
  - `close alpha --dry-run`: rc 0. Header plus 3 numbered lines; line 1 is `1. Fix #12 [fix-12] duplicate of T-0002 (beta)`. The file list is unchanged and alpha is still `status: proposed`.
  - `close alpha --skip 9`: rc 1 with `--skip 9 is out of range: Follow-ups has 3 item(s), so indices run 1 to 3; nothing written`. No new files.
  - `close alpha --skip x`: rc 1 with a one-line refusal and no traceback. No new files.
  - `close alpha --skip 3`: rc 0 with `T-0001 done; 1 follow-up ticket(s): add-retry; skipped duplicate(s): Fix #12 (duplicate of T-0002 (beta)); skipped by --skip: 3`. Exactly one new file, `add-retry/handoff.md`. `check` passes afterwards.
- `python3 plugins/sdlc-lite/scripts/tickets.py close --help`: lists `--dry-run` and `--skip N[,N...]`.
- `plugins/sdlc-lite/scripts/check.sh`: rc 0, every section passes.

## Notes
- **Fixed a shadowed variable:** the old planning loop reused `n` as its `-2` suffix counter. That overwrote the `re.subn` count, so the "no status: line" refusal could never fire once any follow-up existed. I renamed the loop counter to `k`, so that refusal now runs after planning as its docstring says.
- **Where the `--reason` conflict refusal sits:** it is the first check in `cmd_close`, before bad slug. It is an argument conflict and writes nothing. All other refusals keep their order.
- **Skip and duplicate on one bullet:** `--skip` wins. The bullet shows `skip (--skip)` and is not listed as a duplicate.
- **Slug shown for a skipped bullet:** skipped and duplicate bullets have no id, so the dry-run line shows the bare slug base in brackets, like `[fix-12]`. Filed bullets show their final folder name, with the `NNNN-` prefix in numbered mode.
- **Empty titles never match:** the title match only counts when the normalized title is non-empty. Otherwise a punctuation-only follow-up would match every untitled ticket (for example, `new feature alpha` with no title).
- **Extra test coverage:**
  - (p) runs with `numbered=True`, which also proves a dry run writes no config.
  - (q) also checks that the filed follow-ups take the consecutive ids T-0003 and T-0004.
  - (r) also covers `skip=[1]` with Follow-ups `None`, both dry-run orders, and `parse_skip` (bad token refuses, `'3, 1'` parses).
- `.sdlc/confirm-follow-ups/handoff.md` was already modified before this step. I did not touch it.
- The doc updates the task asks for are left for step 2: `skills/file`, `skills/ticket`, root `CLAUDE.md`, and the author agent.
