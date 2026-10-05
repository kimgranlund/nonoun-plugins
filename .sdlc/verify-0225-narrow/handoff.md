# Re-verify T-0225: the two defects the first L3 verifier found

## Goal
Independently re-verify the fix commit 14ecb97 on branch solo-cost (T-0225) for exactly the criteria that failed the first pass (`.sdlc/verify-0225/verifier-L3.md`).

## Acceptance criteria
1. With `SDLC_ATTEMPT_ID` and `SDLC_ROUTING_REASON` exported in the shell (as they are in a role process), `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0, and with both unset it also exits 0. Show both runs.
2. The fix is real, not cosmetic: with a stub `claude` first on PATH printing a result with `total_cost_usd` 3.25, two `solo_run.py run` calls on one ticket with `budget_usd: 10` and `SDLC_ATTEMPT_ID=fixedid` set meter `spend: 6.50` in `budget.py status` (the first pass metered 3.25), the two records have different `attempt_id` values, and neither equals `fixedid`; `routing_reason` is `solo lane, tier <X>` even with `SDLC_ROUTING_REASON` set.
3. The selftest can fail on this defect: in a detached throwaway copy, change `attempt = uuid.uuid4().hex` back to `os.environ.get('SDLC_ATTEMPT_ID') or uuid.uuid4().hex` and show `solo_run.py selftest` exits non-zero. Do not edit the branch's file.
4. `git diff --check main..HEAD` exits 0, and the changes since the first pass are limited to `solo_run.py`, `docs/validation/solo-cost-live-run.md` and `docs/validation/solo-cost-live-run/solo-session.patch` (`git diff <first-pass-head>..HEAD --stat`, first-pass head is the commit `e6539cc`).
5. `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (run it once); `python3 plugins/sdlc-lite/scripts/check.py` exits 0.

Report each criterion pass or fail with the command and its output, then a verdict.
