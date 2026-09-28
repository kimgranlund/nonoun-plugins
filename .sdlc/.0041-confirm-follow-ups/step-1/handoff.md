## Task goal
Follow-up tickets are proposed to the user, or checked against the task's artifacts, before close files them, so already-answered and duplicate follow-ups never land.

## Step 1: Add dry run, --skip, and duplicate auto-skip to tickets.py close, with selftest cases
level: L3
### Do
Only `plugins/sdlc-lite/scripts/tickets.py` changes.

- `cmd_close(root, slug, force=False, numbered=False, reason=None, dry_run=False, skip=None)`:
  - All current refusals stay, in their current order: bad slug, missing front matter, ticket problems, already done, missing filer, missing sections, open Warnings without `--force`, prose Follow-ups, and no `status:` line. They apply to `--dry-run` too.
  - `--dry-run` or `--skip` together with `--reason` refuses with a message and writes nothing.
  - Duplicate check:
    - Normalized title: `' '.join(re.findall(r'[a-z0-9]+', s.lower()))`.
    - A follow-up is a duplicate when its normalized title equals an existing ticket's normalized title, or its slug `base` equals an existing ticket's folder name. For that `base`, use the value before any `-2` suffix, with any `NNNN-` prefix stripped. Also strip the `NNNN-` prefix from the existing folder name before comparing.
    - Match against every ticket of any status that is loaded before this close (`ts`), using the first match in `ts` order.
    - Items in the same batch are NOT checked against each other. The existing case (i), with two identical "Add retry to fetch" bullets, must still file two tickets.
  - `skip`: a list of 1-based indices into the Follow-ups bullets.
    - Refuse if any index is < 1 or > len(items), naming the bad index and the count. The refusal writes nothing, and applies in dry-run too.
    - With Follow-ups `None`, any `--skip` is out of range.
  - Planning loop: skip each index named in `skip`, and skip each duplicate. Skipped items get no id, so later follow-ups take consecutive ids.
  - Dry run output. It writes nothing: no follow-up dirs, no parent status change, no roadmap, no config, even with `--numbered`.
    - A header line: `<pid> dry run: <n> proposed follow-up(s); nothing written`.
    - Then one line per bullet: `<i>. <title> [<slug it would get>]`, followed by ` duplicate of T-NNNN (<slug>)` when marked, or ` skip (--skip)` when named in `skip`.
    - With zero follow-ups, the header line alone.
  - Real close output keeps its current prefix `<pid> done; <k> follow-up ticket(s): <slugs or none>`. After it, append `; skipped duplicate(s): <title> (duplicate of T-NNNN (<slug>)), ...` when any duplicate was skipped, and `; skipped by --skip: <i>, ...` when `--skip` was used.
- `run()` passes these through unchanged, since it already forwards `**kw`.
- `main()`:
  - On the `close` parser, add `--dry-run` (store_true) and `--skip` (metavar `N[,N...]`). Parse `--skip` into a list of ints, and turn a non-integer token into a `Fail`-style refusal (exit 1, stderr, nothing written), not an argparse traceback.
  - Put `dry_run` and `skip` into `kw` for `close`.
  - Update the `close` help strings.
- Module docstring: extend the Usage line to `close <slug> [--force] [--reason TEXT] [--dry-run] [--skip N[,N...]] [--numbered]`. Describe dry-run, `--skip`, and duplicate auto-skip in the `close` paragraph.
- `selftest`: add close cases, each in its own `case(...)` copy, using the existing `filer`, `snap`, `fresh`, and `status` helpers.
  - (p) Dry run writes nothing:
    - A filer with Warnings None and 3 bullets, one of them `- Fix #12` (duplicate of beta by title).
    - Expect: `close --dry-run` gives rc 0, `snap(root) == before`, alpha status still `proposed`, and the output lists indices 1 to 3 with `duplicate of T-0002 (beta)` on the Fix #12 line.
    - Also: dry run with open Warnings and no `--force` refuses with rc 1, and `snap` is unchanged.
  - (q) `--skip` files the rest: 3 non-duplicate bullets with `skip=[2]` gives rc 0, exactly 2 new tickets, none of them from bullet 2, and alpha `done`.
  - (r) `--skip` out of range refuses: `skip=[4]` with 3 bullets, and `skip=[0]`, each give rc 1, the bad index named in stderr, and `snap(root) == before`.
  - (s) Duplicate auto-skip on a plain close:
    - Bullets `- Fix #12` (title match with beta), `- Beta` (slug-base match with beta), and one fresh bullet.
    - Expect: rc 0, exactly 1 new ticket, output containing `skipped duplicate(s)` and `T-0002 (beta)`, and `check` passing afterwards.
  - (t) `--reason` combined with `dry_run=True` or with `skip` refuses with rc 1 and writes nothing.
  - Existing cases (a) through (o) stay unchanged and passing.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS` and exits 0.
- Each new behavior is covered, and its case goes red when the behavior is removed. Temporarily make the dry-run branch fall through to a real close, then ignore `skip`, then drop the out-of-range check, then disable the duplicate check. Each change on its own makes selftest exit 1 with the matching (p), (q), (r), or (s) label in stderr. Revert after each.
- Manual run in a temp root:
  - Setup: `tickets.py --root $T new feature alpha`, then `new bug beta "Fix #12"`, then write `$T/alpha/filer-L1.md` with `## Warnings\nNone\n\n## Follow-ups\n- Fix #12\n- Add retry\n- Quote docs\n`.
  - `close alpha --dry-run` exits 0, prints 3 numbered lines with `duplicate of T-0002 (beta)` on line 1, and `git status`/`find $T` shows no new files, with alpha still `status: proposed`.
  - `close alpha --skip 9` exits 1 and writes nothing.
  - `close alpha --skip x` exits 1 with no Python traceback.
  - `close alpha --skip 3` exits 0, creates exactly one follow-up (`add-retry`), and reports the Fix #12 duplicate as skipped.
- `python3 plugins/sdlc-lite/scripts/tickets.py close --help` lists `--dry-run` and `--skip`.
- `plugins/sdlc-lite/scripts/check.sh` passes.
