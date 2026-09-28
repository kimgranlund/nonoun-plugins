<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- `tickets.py selftest` exits 0 and prints `tickets selftest: PASS`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` → `tickets selftest: PASS`, `rc=0`. Can go red: a temp copy with `for cyc in cycles(ts)` replaced by `for cyc in []` gave `tickets selftest: FAIL, these did not bite: cycle, self-cycle`, rc=1. At HEAD (throwaway worktree) the script does not exist (`ls: ... No such file or directory`).
- `new feature alpha "Alpha"` then `new bug beta "Beta"` create the two handoffs with correct id/title/created/type, and `roadmap.md` exists: pass. Evidence: both rc=0; alpha has `id: T-0001`, `title: "Alpha"`, `created: 2026-09-24` (matches `date +%F`); beta has `id: T-0002`, `type: bug`; `ls -la $R/roadmap.md` shows 534 bytes.
- alpha `depends: [T-0002]` → `check` exits 1 with `stale`; `roadmap` then `check` exits 0; T-0002 row before T-0001: pass. Evidence: `roadmap.md: stale or missing, run tickets.py --root ... roadmap`, `check rc=1`; `roadmap rc=0`; `ok: 2 tickets, roadmap current`, `check rc=0`; `grep -n '| T-000'` → line 8 T-0002, line 9 T-0001.
- `roadmap` twice leaves the file unchanged: pass. Evidence: `cp roadmap.md /tmp/rm1.md; roadmap; cmp` → `cmp rc=0`.
- Negative controls (each on a copy, `check` exit 1, stderr names the problem): pass. Evidence:
  - `type: epic` → rc=1, `alpha: type='epic' not in feature|bug|chore|spike|idea`
  - `status: wip` → rc=1, `alpha: status='wip' not in proposed|ready|blocked|done|dropped`
  - `size:` deleted → rc=1, `alpha: missing size`
  - `id: T-12` → rc=1, `alpha: id 'T-12' is not T-NNNN (T-0000 is the template placeholder)`
  - beta `id: T-0001` → rc=1, `beta: duplicate id T-0001, also used by alpha`
  - `depends: [T-0099]` → rc=1, `alpha: depends on T-0099, which no ticket has`
  - `from: T-0099` (confirmed inserted at line 10) → rc=1, `alpha: from T-0099, which no ticket has`
  - beta depends on T-0001 while alpha depends on T-0002 → rc=1, `alpha: dependency cycle T-0001 -> T-0002 -> T-0001`; grep for `Traceback` in stderr found nothing
  - line appended to `roadmap.md` → rc=1, `roadmap.md: stale or missing, ...`
- `plain/handoff.md` with no front matter keeps `check` at 0 after `roadmap`: pass. Evidence: `wrote .../roadmap.md`, `ok: 2 tickets, roadmap current`, `rc=0`.
- `new idea alpha` exits nonzero and leaves alpha unchanged; `new epic gamma` exits nonzero listing the five types: pass. Evidence: md5 `b57125fe...` before and after, `alpha: ... already exists; nothing written`, rc=1; `no template for type 'epic'; available types: bug, chore, feature, idea, spike`, rc=1; `ls $R` shows only alpha, beta, roadmap.md.
- `check.sh` exits 0 and output includes `tickets selftest: PASS`: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` → `ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `tickets selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`, `check.sh rc=0`. At HEAD the output has no `tickets selftest` line, so the wiring is what adds it.
- `board.py --root .sdlc` still exits 0: pass. Evidence: `board rc=0`.

## Out of scope changes
None. `git diff` touches only `plugins/sdlc-lite/scripts/check.sh` (header comment plus the one selftest line the step asked for). Untracked `plugins/sdlc-lite/scripts/tickets.py` is this step's deliverable; `plugins/sdlc-lite/skills/ticket/` (SKILL.md, five templates) is step 1's output, already verified there; `.sdlc/0002-ticket-intake-roadmap/` is task artifacts.

## For the next attempt
None.
