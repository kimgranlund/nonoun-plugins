<!-- role=solo level=L1 model=sonnet effort=low -->
## Output
T-0499 is fixed in `plugins/sdlc-lite/scripts/tickets.py`, but I could not reproduce the failure as the ticket's Repro describes it. Nothing is committed.

The ticket's exact setup already closes. I ran it with `planner-L2.md` and `filer-L1.md` in the folder and a `skips.md` holding only a `## Lane` entry. The skip check passed. In the real agent-ui folder (`ui-product-card`), only `handoff.md` and `skips.md` are left. So I took "a role with a run record" to mean a record in the ticket folder's `runs.jsonl`, not only a result file.

- **Change:** `skip_missing` now treats a role as having run if it has a result file or a `runs.jsonl` record with that role. This covers the planner, the filer and each step's verifier. A role with neither still refuses, and the existing negative cases cover that.
- **Red first:** I added a selftest case where planner and filer have `runs.jsonl` records but no skip lines. It failed before the fix (`rc=1`, "no ## Skipped entry for planner, filer") and passes after.
- **`tickets.py selftest`:** PASS.
- **`check.py`:** ok.
- **`git diff --check`:** clean.

I did not run the full `check.sh` or the packaging checks.

Because the stated repro already passes, the agent-ui refusals may have another cause. The ticket does not name the red-case spans, so I did not run `specgate.py red` or the verbatim-span step. I also did not run the batched verifier or write `## Acceptance criteria`. The ticket is L1, so the brief did not require either.
