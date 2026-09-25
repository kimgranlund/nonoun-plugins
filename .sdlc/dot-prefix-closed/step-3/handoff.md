## Task goal
In numbered mode, closing a ticket renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/` so Finder and `ls` hide finished work, and every tool still treats it as a closed ticket.

## Step 3: board.py and steps.py handle dot ticket folders, with selftests to prove it
level: L2
### Do
`plugins/sdlc-lite/scripts/board.py` already lists every dir with a `handoff.md` (`root.iterdir()` at the `summary()` and `main()` candidate lists) and has no dot filter. `plugins/sdlc-lite/scripts/steps.py` takes an explicit path. So no code change is expected in either script. Change code only if a new selftest fails, and keep any change minimal.
- Add board.py selftest cases in a temp root:
  - `.0003-closed-work`, done, with a `planner-L1.md`, renders with ID `T-0003`
  - `.0004-closed-bare`, done, with no step work, is hidden
  - `.0005-gone`, dropped, is hidden
  - a `_templates/feature.md` dir and a `.board-state.json` file produce no row
  - `--task .0003-closed-work` renders that one task
  - under the default id sort, the dot folder sorts by its id among the other tickets
- Add a steps.py selftest case: `split` on a task dir named `.0003-x` (holding a planner file and a handoff with front matter) writes `.0003-x/step-1/handoff.md`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
- Run this in a temp root:
  - Tickets: `.0001-a` (done, with `planner-L1.md`), `.0002-b` (done, no step work) and `0003-c` (ready).
  - Non-tickets: a `_templates/feature.md` and a `.board-state.json`.

  `python3 plugins/sdlc-lite/scripts/board.py --root <root>` output contains `.0001-a` and `0003-c`, and no table row contains `.0002-b`, `_templates` or `board-state` (the documented legacy `.board-state.json` hint line below the table is expected).
- `git diff --stat plugins/sdlc-lite/scripts/board.py plugins/sdlc-lite/scripts/steps.py` shows selftest-only changes, or a stated minimal fix.


## Previous attempt
verifier-L1.md failed only on criterion wording: the output's documented legacy-cache hint names `.board-state.json`. Conductor reworded the criterion to table rows; no code change was requested.
