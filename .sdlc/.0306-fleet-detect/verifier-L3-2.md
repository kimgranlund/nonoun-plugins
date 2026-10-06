<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
No `builder-*.md` exists in the artifacts dir (solo lane, per `skips.md`), so there was no builder claim to review. This is a resume of `verifier-L3.md`, which failed only on the `ticket_root: tickets` layout. I re-ran all 14 criteria rather than only the failed item, because `fleet_detect.py` (mtime 13:39:35) and `fleet_collect.py` (13:40:38) both changed after that verdict (13:38:50). All evidence below is from my own runs on the current tree.

- C1 `fleet_detect.py selftest` prints `fleet_detect selftest: ok`: pass. Evidence: exit 0. Red on a scratch copy with mutant A (stall rule reads `3` instead of the table), exit 1.
- C2 observed positive and negative per rule, all 8 rules: pass. Evidence: exit 0. Red on mutant B (`n >= limit` in the planner rule): exit 1, with `FAIL: negative: planner_results_per_ticket yields no finding`.
- C3 negative control `raising stall_attempts in the table silences stall_attempts`: pass. Evidence: exit 0. On mutant A that exact line turns `FAIL:` and the criterion exits 1.
- C4 known findings in the selftest: pass. Evidence: exit 0. Red on both mutants below, exit 1 each.
  - Mutant C (Chromium count threshold unreachable) fails the maison and gen-ui-kit lines.
  - Mutant D (share rule dead) fails the agent-ui line.
- C5 live agent-ui collect at the cutoff piped to detect gives `plan_review_share` over 0.40: pass. Evidence: exit 0; collector summary `runs: 193 deduped, $786.95`. Red on mutant D, exit 1.
- C6 no-data fingerprint prints nothing on stdout: pass. Evidence: exit 0. Red on the input `{"repo":"/x","processes":{"chromium":{"count":31}}}`, exit 1.
- C7 `THRESHOLDS` sits before the first `def rule_` and has 9 rows: pass. Evidence: exit 0; table at lines 49 to 59 with a comment per row, first rule at line 136. Red on mutant E (a tenth row), exit 1.
- C8 (gate) `fleet_collect.py selftest`: pass. Evidence: exit 0. It was also green at the pre-build commit b5186e46 in a throwaway worktree, so there is no inherited-red question. Red on all three collector mutants listed under C9.
- C9 (new) selftest lines for `ticket_root: tickets` and the flat control: pass. Evidence: exit 0. Red at pre-build b5186e46 (exit 1) and red on three mutants of the built collector copied into the throwaway worktree. The unmutated copy there was green.
  - Mutant A (`ticket_of` ignores `nested`): `FAIL: ticket_root: tickets keys each ticket folder, not the tickets dir, in a config-less lane too`.
  - Mutant B (`tickets_info` ignores `nested`): `FAIL: tickets: the nested layout is read too, and the flat one`.
  - Mutant C (layout read per checkout, not per repo): the same line as mutant A fails, so the config-less lane conjunct bites.
- C10 (new) live maison collect has no bare `tickets` key, has `tickets/` keys, and `tickets.count` over 20: pass. Evidence: exit 0. Red at pre-build (exit 1) and on mutants A, B and C (exit 1 each).
  - Unsuppressed run: 177 `by_ticket` keys, 168 under `tickets/`, no bare `tickets` key, 89 items, all nested.
  - `tickets.count` is 249, not the "near 40" my earlier verdict guessed. That guess counted only the 38 open folders. Closed dotted folders and the 138 checkouts bring it to 249. An independent listing matched the collector's key set exactly (249 both, empty difference each way). The handoff keys a ticket by its folder with no closed-folder exclusion, so this is in contract.
- C11 no em dash in the three files and `git diff --check`: pass. Evidence: exit 0. The negated grep goes red (exit 1) on a scratch copy with a planted em dash. The untracked `fleet_detect.py` has 0 whitespace findings under `git diff --no-index --check`.
- C12 `check.sh` runs the selftest and the docs have the entry: pass. Evidence: exit 0. Both greps exit 1 against `git show HEAD:` copies of the two files. `bash -n check.sh` exits 0.
- C13 (gate) `check.py`: pass. Evidence: `ok: 19 role levels, 9 agents checked`, exit 0.
- C14 (gate) `tickets.py --root .sdlc check`: pass. Evidence: `ok: 309 tickets, roadmap current`, exit 0.
- Earlier fail, the nested layout run end to end (rule 2): now pass.
  - Same repro outside any git repo (two tickets of 3 planner rows, one size M handoff with 25 criteria). Nested gives `by_ticket {'tickets/0001-a': {'planner': 3}, 'tickets/0002-b': {'planner': 3}}`, no planner finding, and `size_m_criteria tickets.items[0].criteria 25 > 20`. The flat control gives the same findings under plain folder names.
  - Live maison detect: the false `runs.by_ticket["tickets"].planner 79` finding is gone. `first-wave-components` at 11 remains.
  - Lane overrides and `by_ticket` now use the same `tickets/<folder>` key form.
  - `size_m_criteria` is silent on maison because the largest size M handoff has 9 criteria. A separate awk scan of the handoffs gives the same top three (9, 8, 8). The handoff says this finding is not required.
- Steelman: five `planner_results_per_ticket` findings now surface on maison (for example `tickets/0105-structured-component-contracts` at 20). Draft concern: these are artifacts of the rekeying. Check: a separate recount of 0105 across 64 `runs.jsonl` files, deduped by `attempt_id`, gives 20 unique planner attempts and 0 rows without an id. The concern is dropped; the findings are real and were hidden by the earlier collapse.

Constraints checked:
- No model call: `subprocess` in `fleet_detect.py` appears only at lines 502 to 503, where the selftest calls itself.
- Read-only: the only `open(..., 'w')` calls in `fleet_detect.py` are inside the selftest's `tempfile.TemporaryDirectory`.
- No model or effort file is in the diff: `git status` on `run.sh`, `adapters`, `agents` and `skills` shows 0 lines.
- The one em dash in `handoff.md` is line 43, the grep pattern of C11 itself.

Not run: the full `check.sh` suite. It is not a criterion; the one added line was run directly (C1) and the file parses.

## Out of scope changes
None.
- `.sdlc/0306-fleet-detect/handoff.md`: the diff only adds the `## Acceptance criteria` section, which the solo lane writes. Compared with the 12 criteria in my earlier verdict, none was removed or loosened; two were added (C9, C10) and the preamble now names the nested layout.
- `plugins/sdlc-lite/scripts/fleet_collect.py`: sanctioned by the preamble as additive, and additive by evidence. The pre-build collector and the built one were run on agent-ui at the cutoff. All 109 old key paths are present in the 250 new ones, the only additions at the old levels are `tickets` and `runs.by_ticket`, and every old value under `runs` and `plan_review_share` is equal.
  - The `env.plugin` differences in that comparison come from running the pre-build copy out of a temp dir (its `path` is the temp dir). They are not a collector regression.
- `plugins/sdlc-lite/scripts/check.sh` and `docs/maintenance/sdlc-internals.md`: named by C12. The docs entry and the collector docstring (lines 18 to 22) carry the `tickets/<name>` wording.
- `base-sha`, `skips.md`, `runs.jsonl`, the `verifier-L3*` files: runner records.
- Dependents: `git grep -lE 'fleet_collect|fleet_detect'` finds only `check.sh`, the docs entry, the collector itself and ticket handoffs. There is no other consumer of the fingerprint.
- My own footprint: `git status` is the same 11 lines as on arrival, the throwaway worktree is removed, no `__pycache__` was written, the stash list is empty, and HEAD is still b5186e46.

## For the next attempt
None.
