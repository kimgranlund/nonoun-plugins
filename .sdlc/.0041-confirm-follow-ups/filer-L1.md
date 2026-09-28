<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0041: close confirms follow-ups before filing them

## PR body
### Summary
Before this change, `tickets.py close` filed every follow-up bullet in the filer file. That included items the session had already answered and exact duplicates of existing tickets. Now `close` can list what it would file without writing anything, can leave out chosen items, and skips exact duplicates on its own. `/file` runs the dry run, drops follow-ups the task's artifacts already resolve, asks the user to confirm, and then closes.

### Changes
**Step 1: `plugins/sdlc-lite/scripts/tickets.py`** (builder L3, verifier L2: pass)
- `close --dry-run` lists each proposed follow-up with its 1-based index, title, slug, and any `duplicate of T-NNNN (<slug>)` or `skip (--skip)` mark. It writes nothing: no follow-up dirs, no status change, no roadmap, and no config, even with `--numbered`. The same refusals as a real close apply, including open Warnings without `--force`.
- `close --skip N[,N...]` files every follow-up except the named ones.
  - An index out of range refuses, names the bad index, and writes nothing.
  - A non-integer token refuses in one line, with no traceback.
- Duplicate auto-skip covers a follow-up whose normalized title or slug base exactly matches an existing ticket of any status. A real close skips it and names it in the output. Follow-ups in the same batch are not checked against each other, so existing case (i) still files two identical bullets.
- `--reason` together with `--dry-run` or `--skip` refuses.
- Neighboring fix: the planning loop reused `n` as its suffix counter, which overwrote the `re.subn` count. As a result, the "no status: line" refusal could never fire once a follow-up existed. The counter is renamed to `k`.
- New selftest cases (p) to (t). The docstring and argparse help are updated.

**Step 2: docs and the `/file` flow** (builder L2, verifier L1: pass)
- `skills/file/SKILL.md` step 3 now runs in this order:
  1. Dry run.
  2. Drop follow-ups the artifacts already answer, with a reason for each.
  3. AskUserQuestion (multiSelect, recommended set first).
  4. `close --skip`.
  5. When no one is present, a stated default: file the non-duplicates minus the artifact-answered items, and say so in the report.
  6. Report.
- `skills/ticket/SKILL.md`, the root `CLAUDE.md` tickets.py bullet, and `.claude/agents/sdlc-lite-author.md` (sync rule) describe the new flags and the duplicate skip.
- `agents/filer.md` and the `--reason` behavior are unchanged.

### Verification
- `tickets.py selftest`: PASS, rc 0. Existing cases (a) to (o) still pass.
- Mutation checks, run independently by the verifier in a throwaway worktree. Disabling each behavior on its own turns selftest red with the matching label:
  - dry-run branch → (p)
  - skip → (q)
  - range check → (r)
  - duplicate check → (p) and (s)
- Manual temp-root run:
  - `--dry-run` wrote no files and marked `Fix #12` as `duplicate of T-0002 (beta)`.
  - `--skip 9` and `--skip x` each refused and wrote nothing.
  - `--skip 3` filed only `add-retry` and reported the skipped duplicate. `check` passed afterwards.
- Negative control at HEAD: argparse rejected `--dry-run`, and plain close filed the duplicate.
- `close --help` lists both flags.
- `check.sh` passes: the step 1 verifier saw rc 0. The step 2 verifier read only the tail of the output, with no failures shown, and the step 2 builder reported exit 0.
- Step 2 doc criteria: the greps match in every required file, `filer.md` is unchanged, and no em dash was added. The order of `/file` step 3 was checked by reading the file, since it is prose with no runtime behavior.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py close` gains `--dry-run`, which lists the proposed follow-ups with indices and duplicate marks and writes nothing, and `--skip N[,N...]`. It now skips follow-ups that exactly duplicate an existing ticket (normalized title or slug). `/file` runs the dry run, drops follow-ups the artifacts already answer, and confirms with you before closing. Also fixed: the "no status: line" refusal in `close` now fires when follow-ups exist.

## Follow-ups
- Exercise the new /file step 3 flow (dry run, AskUserQuestion, then `close --skip`) end to end on a real ticketed task: it was verified only by reading SKILL.md.
- Guard `close --skip` against index drift: if the filer file changes between `--dry-run` and `--skip`, the indices shift and the wrong follow-ups get skipped (no lock or content check today).
