## Task goal
Every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move.

## Step 2: run.sh validates through results.py; check.py's plan-reviewer guard reads the schema
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.

In `plugins/sdlc-lite/scripts/run.sh`:
- Delete the per-role `case "$role" in builder) sect=Status; allowed=...` table (lines 124 to 134) and its comment.
- In the child path, just before the `events=` result pick (line 450), set `sect=$(python3 "$plugin_root/scripts/results.py" key "$role")`. The jq pick at line 451 keeps using `## $sect` unchanged.
- Replace the awk `val=` / `bad=` block (lines 472 to 486) with a call to `python3 "$plugin_root/scripts/results.py" validate "$result" --role "$role"`. On any nonzero exit, take the reason by stripping the literal prefix `results.py: $result: ` from its output line, print `run.sh: $role result <reason>; see $result` on stderr, and exit 3. On success, keep `echo "$result"; exit 0`.
- Exit codes and the `run.sh: <role> result ... ; see <file>` shape are unchanged.
- The missing-section message becomes `run.sh: builder result lacks ## Status (done|blocked|inherited red: <tests>); see ...`, which still satisfies every existing grep: `run-selftest.sh` 257, 264, 266, 275 and `codex-selftest.py` 102 (`lacks ## Map`).
- Keep all new code inside the `{ ... }` group (self-edit rule, header lines 82 to 87).
- Rewrite the header comment lines 17 to 21: the result check is `scripts/results.py validate` against the table that `results.py schema` prints (header line, key section with builder `inherited red: <tests>` and verifier `inherited red: <tests>` accepted, declared section order), and the result-pick heading comes from `results.py key`. The words `inherited red` must stay in run.sh, because `check.py` `INHERITED_RED_DOCS` (line 163) requires them.
- The Codex backend shares this path (`run.sh` builds `cmd` for `codex_exec.py`, and the check runs after it), so no Codex transport change is needed. `codex_exec.py` has no section check of its own (`grep` found none).

In `plugins/sdlc-lite/scripts/run-selftest.sh`, after line 276, add an order case: `want_rc 3 verifier L1` with a result holding `## Criteria` before `## Verdict` (pass), then `grep -q 'comes before' "$tmp/rerr"`, failing otherwise.

Contract dependent: `plugins/sdlc-lite/scripts/check.py` lines 344 to 352 pin the deleted line `plan-reviewer) sect=Verdict; allowed='pass|replan|blocked' ;;`. Replace that guard:
- Import `results` with `sys.path.insert(0, str(root/'scripts'))`.
- Require `results.SCHEMA['plan-reviewer']` to have key `Verdict` and allowed tokens exactly pass, replan, blocked.
- Require run.sh to contain `results.py" validate`.
- Keep the `plan-reviewer:L1` row check and a negative control that a mutated schema copy and a run.sh text without the validate call are each flagged.
- Remove the constant `PR_SECT`.

`lifecycle-selftest.py` pins none of these messages (grep found no `lacks`); run it as a guard.

### Acceptance criteria
- `grep -qF 'results.py" validate' plugins/sdlc-lite/scripts/run.sh`
- `grep -qF 'results.py" key' plugins/sdlc-lite/scripts/run.sh`
- `! grep -qE "allowed='|sect=[A-Z]" plugins/sdlc-lite/scripts/run.sh`
- `grep -qF 'comes before' plugins/sdlc-lite/scripts/run-selftest.sh`
- `! grep -qF 'PR_SECT = "plan-reviewer) sect=' plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `grep -qF 'inherited red' plugins/sdlc-lite/scripts/run.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py | { ! grep -q .; }`
