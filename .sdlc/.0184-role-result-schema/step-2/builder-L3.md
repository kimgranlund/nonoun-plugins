<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: deleted the per-role `sect=`/`allowed=` table and its comment. In the child path, `sect` now comes from `results.py key "$role"` just before the `events=` pick, and the jq pick still uses `## $sect`. The awk `val=`/`bad=` block is replaced by `results.py validate "$result" --role "$role"`. On a nonzero exit run.sh strips `results.py: $result: ` from the output, prints `run.sh: $role result <reason>; see $result` on stderr and exits 3. All new code is inside the `{ ... }` group. I rewrote header lines 17 to 23 to describe the results.py check, the schema table, the allowed values (each `inherited red: <tests>` is kept whole on one line), the section order and where the pick heading comes from. I also changed the exit-code line from "3 result lacks its section" to "3 result fails the result check".
- `plugins/sdlc-lite/scripts/run-selftest.sh`: after the `## Findings` plan-reviewer case, added `want_rc 3 verifier L1` with `## Criteria` before `## Verdict` (pass), then `grep -q 'comes before' "$tmp/rerr"`, which fails otherwise.
- `plugins/sdlc-lite/scripts/check.py`: removed `PR_SECT`. It now imports `results` through `sys.path.insert(0, str(root/'scripts'))`. The guard checks three things: the `plan-reviewer:L1` row exists, `results.SCHEMA['plan-reviewer']` has key `Verdict` and allowed tokens exactly pass, replan, blocked, and run.sh contains `results.py" validate`. There are three separate negative controls (row removed, schema copy mutated, run.sh text without the validate call), and each must produce its own error.

## Checks
- `grep -qF 'results.py" validate' plugins/sdlc-lite/scripts/run.sh`: exit 0
- `grep -qF 'results.py" key' plugins/sdlc-lite/scripts/run.sh`: exit 0
- `! grep -qE "allowed='|sect=[A-Z]" plugins/sdlc-lite/scripts/run.sh`: exit 0
- `grep -qF 'comes before' plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0
- `! grep -qF 'PR_SECT = "plan-reviewer) sect=' plugins/sdlc-lite/scripts/check.py`: exit 0
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0, "run selftest: PASS"
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: exit 0
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: exit 0
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0, "ok: 19 role levels, 9 agents checked"
- (guard) `grep -qF 'inherited red' plugins/sdlc-lite/scripts/run.sh`: exit 0
- (guard) scope diff against `$SDLC_BASE_SHA` f45649e: exit 0 (no files outside the allowed five)
- Negative control on a temp copy of the plugin: replacing the run.sh validate call made check.py print `FAIL scripts/run.sh: plan-reviewer role: no result check "results.py" validate"`. Removing `replan` from the results.py plan-reviewer schema made it print `FAIL ... results.py SCHEMA plan-reviewer is not key Verdict with allowed pass, replan, blocked`. The copy was removed afterwards.
- `bash -n plugins/sdlc-lite/scripts/run.sh`: syntax ok. `git diff --check -- plugins`: clean.

## Notes
- run.sh exit 3 now also covers a disallowed key value, a bad header and wrong section order, not only a missing section. Some prose outside this step's scope still says "lacks its section" / "required section": `docs/maintenance/sdlc-internals.md:11`, `plugins/sdlc-lite/agents/conductor.md:29`, the run-selftest.sh header comments at lines 10 and 17, and the comment in `traces/detectors/thresholds.py:17`. Step 5 and step 6 handoffs reference sdlc-internals or conductor.md, so they may already cover this. I did not edit those files because the scope guard forbids it.
- If results.py prints no output on failure, the stderr line falls back to the reason `failed the result check`, so the `run.sh: <role> result ...; see <file>` shape still holds.
