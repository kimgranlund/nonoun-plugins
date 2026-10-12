<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0496: Pilot: solo L2 closes on green criteria with observed-red controls; verifier by exception

## PR body
Summary
- Adds a second verifier-skip class, `tests-gate`, to `plugins/sdlc-lite/scripts/verify_scope.py`, next to the T-0429 docs-only skip. It is on only where `.sdlc/config` says `tests_gate: pilot`, and this repo sets that. With the flag off, output is unchanged.
- A skip prints `tests-gate` with exit 0. Any other case prints `tests-gate: <label>: <detail>` for the first unmet condition and exits 1, so the verifier still runs. The nine conditions, in check order, are level, lane, criteria, red-control, report, shared-name, size, protected-path and the handoff verifier line.
- `solo_stats.py` now prints `gate: tests-only` and `gate: verifier`. `agents/solo.md` tells solo to record red controls with `redck.py record` and to end its report with `verify: skipped (tests-gate; criteria green, red controls pre-edit)`.

Changes
- Step 1 (`verify_scope.py`, `tickets.py`, `.sdlc/config`):
  - `scope(root, base, handoff=None, report=None, need_report=False)` evaluates the tests-gate class.
  - The CLI gains `--report FILE`.
  - `tickets.py close` writes the skip line `reason: tests-gate diff against ...` into `skips.md` as the close-note record. `docs_waiver` now returns `(base, klass)`, and there is a new `solo_report` helper.
  - `.sdlc/config` gets `tests_gate: pilot`.
- Step 2 (`solo.md`, `solo_stats.py`, docs):
  - `solo.md` changes: the Loop step 2 `redck.py record` sentence and one `## Verification` bullet.
  - `solo_stats.py` adds the count keys `gate_tests_only` and `gate_verifier`, a `--json` field and selftest cases. The two keys are independent counts, not a partition.
  - Regenerated `solo-L1.md`, `solo-L2.md`, `solo-L3.md` and the three `sdlc-solo-l*.toml` files with `claude_roles.py` and `codex_roles.py`.
  - Updated `docs/references/sdlc-internals.md` and `plugins/sdlc-lite/AGENTS.md`.
- Revert rule: set `tests_gate: off` and report if K-005 for pilot tickets falls below 72 percent, or if any pilot ticket is reopened for a defect a verifier would have caught.

How each was verified
- Step 1, verifier L2, pass:
  - `verify_scope.py selftest` is ok and has 4 `tests-gate ok:` cases and 11 `tests-gate red:` cases.
  - The verifier mutated 8 checks in a copy (protected-path, size, shared-name, lane, red-control phase, report, pilot-off, criteria). Each mutation turned the selftest red on the matching case.
  - `tickets.py selftest` and `redck.py selftest` pass, and the legacy docs-only cases are unchanged.
  - The scope guard is green.
- Step 2, verifier L1, pass:
  - `solo_stats.py selftest` passes, including a control where the skip line is absent.
  - `solo_stats.py stats .` prints `gate: tests-only  0` and `gate: verifier    108`.
  - The `solo.md` prohibition count is 19, the same as at base.
  - `claude_roles.py generate --check`, `codex_roles.py generate --check`, `check.py` and `prompt_lint.py` exit 0.
  - `check.sh` exit 0 on the final tree (about 20 minutes under load). `check-packaging.py` and `git diff --check` pass.
- Limits:
  - The qualifying path (a qualifying L2 diff printing `tests-gate`) is covered only by selftest fixtures. No live L2 ticket has used the skip yet.
  - `check.sh` was not run at base. It exited 0, so that was not needed.
  - No step had a `(red)` criterion, so no red-checkpoint record exists for either step.

## Changelog entry
- sdlc-lite: new `tests-gate` verifier-skip class in `verify_scope.py` for solo L2 tickets whose criteria are all command spans with pre-edit red controls. It is pilot-gated by `tests_gate: pilot` in `.sdlc/config` (set in this repo). `solo_stats.py` reports `gate: tests-only` and `gate: verifier`. `solo.md` records red controls with `redck.py` and reports `verify: skipped (tests-gate; ...)`.

## Follow-ups
- decide: `tickets.py close` writes the tests-gate skip line only for a solo ticket with a `step-<n>/` dir, so a real solo ticket with no step dir never gets the line, `gate_tests_only` never counts it, and the pilot barely reaches the tickets it targets; decide whether close should consult the gate on that path.
- decide: the handoff asks `lanes.py` to print `gate: tests-only` or `gate: verifier`, but `lanes.py list` has no per-ticket surface; the unattended run left `lanes.py` untouched and put the field in `solo_stats.py` only (skips.md decision); name a surface (a lane column, the `/report` lanes view) or drop it.
- decide: the 20-ticket readout needs K-005 for tests-gate tickets and rework after close (a reopen, or a follow-up citing a closed ticket within 7 days), and neither is built; `first_pass / verified` excludes tickets with no verifier round, so the revert rule cannot be evaluated yet.
- note: the `shared-name` check counts a removed token on a `+` line only as a whole token, so a rename `helper` to `helper2` still searches `helper`. `protected-path` matches its sensitive words as substrings of any path component (`auth` also matches `author`). Both lean toward keeping the verifier, which lowers the qualifying rate.
