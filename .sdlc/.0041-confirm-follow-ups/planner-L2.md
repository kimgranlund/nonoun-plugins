<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
`tickets.py close` gains `--dry-run`, `--skip N[,N...]`, and automatic skipping of exact-duplicate follow-ups, and `/file` step 3 runs the dry run, drops follow-ups the artifacts already answer, confirms with the user, then closes with `--skip`.

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

## Step 2: Wire the confirm flow into /file and sync the docs
level: L2
### Do
- `plugins/sdlc-lite/skills/file/SKILL.md`: rewrite step 3 as numbered substeps. Keep the "only if ticket front matter" guard.
  1. Run `tickets.py --root .sdlc close <slug> --dry-run`. On an open-Warnings refusal, keep today's AskUserQuestion force-close flow and add `--force` to every later call only if the user approves. On any other refusal, report stderr and stop.
  2. Read the task's artifacts (plan, builder, and verifier files). Mark for dropping any follow-up they already resolve, with a one-line reason each. Items marked `duplicate of` are skipped by close automatically.
  3. When a person is present, ask with AskUserQuestion (multiSelect) which follow-ups to file. Put the recommended set first, which is the non-duplicate items minus the artifact-answered ones.
  4. Run `close <slug> --skip <unselected indices>`, or plain `close` if nothing is skipped.
  5. Unattended (no one to answer): file the non-duplicate follow-ups minus the artifact-answered ones, and state that choice and the reasons in the report.
  6. Report the tickets created, the duplicates skipped, and the items dropped, with reasons.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add `[--dry-run] [--skip N[,N...]]` to the `argument-hint` `close` form. In item 4, say what dry-run and `--skip` do, that exact duplicates of existing tickets (normalized title or slug) are skipped automatically, and that `--reason` does not combine with either.
- Repo root `CLAUDE.md`, the `scripts/tickets.py` bullet: add `--dry-run` (lists the proposed follow-ups with indices and duplicate marks, writes nothing), `--skip N[,N...]`, and duplicate auto-skip to the `close` description. Mention that `/file` runs the dry run and confirms first.
- `.claude/agents/sdlc-lite-author.md` line 16: extend the sync rule so `--dry-run`/`--skip` and duplicate skipping stay in sync across tickets.py, the /ticket skill, the /file skill, and CLAUDE.md.
- Do not change `agents/filer.md` or the `--reason` behavior.
### Acceptance criteria
- `grep -n -- '--dry-run' plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` matches in all four files.
- `grep -n -- '--skip' plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md` matches in all three files.
- `/file` step 3, read in order, has the dry run first, then dropping artifact-answered items with reasons, then AskUserQuestion with multiSelect and the recommendation first, then close with `--skip`, plus an unattended default that is stated in the report.
- `git diff --stat` shows no change to `plugins/sdlc-lite/agents/filer.md`.
- The new text contains no em dash: `git diff -U0 | grep '^+' | grep -c '—'` prints 0.
- `plugins/sdlc-lite/scripts/check.sh` passes.

## Risks
- Duplicate detection runs against tickets that exist before the close, not within the batch. If a builder also dedupes within the batch, existing selftest case (i) (two identical bullets) breaks. The plan keeps case (i) as-is.
- Slug-base matching can flag false duplicates on short generic bases, such as a follow-up whose first five words match an old ticket's slug. That is accepted per the handoff: exact match only, no fuzzy matching.
- The dry-run indices must match what a later `--skip` sees. If the filer file changes between the two calls (a /file rerun), the indices shift. /file runs them back to back, and the plan does not add a lock.
- `check.sh` may fail for reasons unrelated to this work, such as shellcheck or plugin validate on the worktree. The verifier should compare against a baseline run on the unmodified tree.
