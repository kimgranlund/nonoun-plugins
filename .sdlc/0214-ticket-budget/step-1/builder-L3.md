<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/budget.py` (new, untracked): `status`, `set`, `ack` and `selftest` subcommands, plus `ticket_of`, `spend`, `ceiling`, `report` and `fmt` helpers. The header says Codex runs record no cost, so the meter covers Claude roles only.
- `plugins/sdlc-lite/scripts/run.sh`: budget gate inside the `{ ... }` group, just before the lifecycle `exec` block, guarded by `SDLC_LIFECYCLE_CHILD != 1` (so dry runs are gated too). On status exit 3 it prints `run.sh: budget <pct>%: ask the user; budget.py ack` and exits 4. The `Exit codes:` header gains `4 ticket budget at 80 percent or more with no ack`, plus a short "Budget gate" header paragraph.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: the three `budget gate:` cases, each run from a `step-1/handoff.md` with no front matter so the walk-up is exercised.
- `plugins/sdlc-lite/scripts/board.py`: imports `budget`, adds `budget_cell()` and the gated Budget column, two selftest cases (`budget column: absent…`, `budget column: present…`), and a docstring paragraph.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `allowed-tools` gains the budget.py path, and step 2 gets the filing instruction (tiers, `--usd N`, 80 percent stop answered by `budget.py ack`).
- `plugins/sdlc-lite/scripts/check.sh`: `python3 "$root/scripts/budget.py" selftest || fail=1` after the footprint line, and the header comment names "the budget.py selftest".
- `plugins/sdlc-lite/scripts/check.py`: docstring item 17 and the `TICKET_BUDGET` guard with negative controls.
- `docs/maintenance/sdlc-internals.md`: a `scripts/budget.py` entry.

## Checks
- Criterion 1 (budget selftest, last line plus all 10 labels): exit 0.
- Criterion 2 (`run-selftest.sh`, ending `run selftest: PASS`, plus the 3 labels): exit 0. The first attempt failed on a `pipefail` exit in the new `blines()` helper (`cat` of a missing file); after the fix it passed.
- Criterion 3 (board selftest plus 2 labels): exit 0.
- Criterion 4 (seeded 85 percent ticket): status exit 3, `percent: 85`, `state: warn`; the check passed.
- Criterion 5: the first run exited 1 because `grep -qF "budget.py selftest"` found nothing in check.sh. After the header comment fix it exited 0, and `check.py` printed `ok: 19 role levels, 9 agents checked`.
- Criterion 6 (`tickets.py selftest` and `steps.py selftest`): exit 0.
- Guard (diff limited to the 8 allowed paths): exit 0, run again after the last edit.
- Negative control for item 17: in a temp copy of the plugin I removed `budget.py set` from SKILL.md and `4 ticket budget` from run.sh. `check.py` printed `FAIL skills/ticket/SKILL.md: ticket-budget text missing "budget.py set"` and `FAIL scripts/run.sh: ticket-budget text missing "4 ticket budget"`. The temp copy was deleted; the real files were not changed.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Every selftest passed and `claude plugin validate` was ok; it printed `skip: shellcheck not installed`.
- `git diff --check`: clean.

## Notes
- check.sh line: the required line `python3 "$root/scripts/budget.py" selftest` has a quote between `budget.py` and `selftest`, so criterion 5's grep cannot match it. The literal `budget.py selftest` comes from the check.sh header comment instead.
- Unverified: shellcheck is not installed here, so the new bash in `run.sh` and `run-selftest.sh` has not been linted.
- Not done: the design's live run (seed a ticket at 85 percent and see one question on Claude) is not in this step's criteria, so I did not run it. The planner should route it.
- No separate negative control was run for the first gate case. Its exit-4 check catches a missing gate on its own, because without the gate run.sh would exit 0 and call the stub.
- Behaviour choices the criteria leave open:
  - An empty-string `attempt_id` counts as "no attempt_id", since run.sh writes `""` when `SDLC_ATTEMPT_ID` is unset.
  - `cost_usd: 0` counts as metered.
  - `ack` on a ticket with no budget exits 2.
  - `status` with no ticket prints `no ticket` to stderr and exits 2.
  - run.sh sends budget.py's stderr to `/dev/null`, so existing tests that expect empty or exact stderr are unaffected.
- `budget.py` is untracked, as expected for a non-merge step; nothing is staged or committed.
