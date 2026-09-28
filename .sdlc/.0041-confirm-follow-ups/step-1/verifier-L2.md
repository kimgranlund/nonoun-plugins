<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- `selftest` prints `tickets selftest: PASS` and exits 0: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` → `tickets selftest: PASS`, `rc=0`. Existing (a) to (o) run in the same suite, including case (i) with two identical bullets.
- Each new behavior covered, case goes red when removed: pass. Evidence: in a throwaway worktree (`git worktree add <tmp> HEAD`, modified `tickets.py` copied in, unmutated selftest rc=0), each single-condition mutation to `if False:`, restored between runs (`cmp` confirmed):
  - `if dry_run:` → rc=1, stderr `(p) dry run lists 1 to 3 ... rc=0 out='T-0001 done; 2 f...'` (dry run fell through to a real close)
  - `if i in skipped:` → rc=1, stderr `(q) --skip 2 files bullets 1 and 3 only: ... 3 follow-up ticket(s)`
  - `if not 1 <= i <= len(items):` → rc=1, six `(r) --skip {4,0,1} (dry_run=True/False) ... refuses` lines
  - `if dup:` → rc=1, stderr `(p) ...` and `(s) duplicates of beta skipped on close: ... 3 follow-up ticket(s)`
  Biting variables named per case: (p) the early-return before the mkdir loop; (q) the `continue` on a skipped index; (r) the range refusal; (s)/(p) the `known` match.
- Manual run in a temp root: pass. Evidence (temp `.sdlc` with alpha, beta "Fix #12", filer as specified):
  - `close alpha --dry-run` → rc=0, output `T-0001 dry run: 3 proposed follow-up(s); nothing written` / `1. Fix #12 [fix-12] duplicate of T-0002 (beta)` / `2. Add retry [add-retry]` / `3. Quote docs [quote-docs]`; `find $T` diff against before: empty (`no new files`); alpha `status: proposed`.
  - `close alpha --skip 9` → rc=1, `alpha: --skip 9 is out of range: Follow-ups has 3 item(s), so indices run 1 to 3; nothing written`; no new files; alpha still proposed.
  - `close alpha --skip x` → rc=1, one line `--skip 'x': 'x' is not an integer; ...; nothing written`, no traceback; no new files.
  - `close alpha --skip 3` → rc=0, `T-0001 done; 1 follow-up ticket(s): add-retry; skipped duplicate(s): Fix #12 (duplicate of T-0002 (beta)); skipped by --skip: 3`; find diff shows exactly `add-retry/` and `add-retry/handoff.md` added; alpha `status: done`; `check` → `ok: 3 tickets, roadmap current`, rc=0.
  - Negative control at HEAD (throwaway worktree): `close alpha --dry-run` → argparse `unrecognized arguments: --dry-run`, rc=2; plain `close alpha` filed all 3 including `fix-12`, so the duplicate landed before this change.
- `close --help` lists `--dry-run` and `--skip`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py close --help` shows `--dry-run` and `--skip N[,N...]` with their help text, rc=0. At HEAD the same grep count is 0.
- `check.sh` passes: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` → all sections ok (`tickets selftest: PASS`, `steps selftest: PASS`, `run selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`), `check.sh rc=0`.

## Out of scope changes
- `.sdlc/0041-confirm-follow-ups/handoff.md` (Intent section filled by /clarify): modified before the builder ran (mtime 19:07 vs builder 19:11); not a builder change.
- Inside `tickets.py`, the builder renamed the `-2` suffix loop counter `n` → `k` so the pre-existing "no status: line" refusal can fire when follow-ups exist. Neighboring bug fix, consistent with "all refusals stay"; selftest and check.sh stay green.
- Cosmetic: `empty =pathlib.Path(...)` lost a space at tickets.py:1083.

## For the next attempt
None
