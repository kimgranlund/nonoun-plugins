<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
A second builder on a branch that already holds the first builder's commits gets `pre-edit` or `preserved` from `redck.py`, and a control from a different lineage is still refused.

## Step 1: redck phase against the working tree, bind to an ancestor base
level: L3
guard timeout: 1900
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: none. Targets are `plugins/sdlc-lite/scripts/redck.py` (`dirty_paths`, `cmd_record`, `span_status`, the module docstring, `selftest`) and the `scripts/redck.py` section of `docs/references/sdlc-internals.md`. The three rules come from `docs/reports/2026-10-12-maison-wave-7b-mechanics.md` item 6 and its Interfaces line for redck. They are settled as follows.

1. Phase from the working tree. In `cmd_record`, the dirty set becomes the paths that differ from HEAD: `git diff --name-only HEAD --` plus `git ls-files --others --exclude-standard`. This is the handoff's `git status --porcelain` rule on the source paths. `.sdlc/` and the handoff dir stay excluded, and `split_prelude` stays unchanged. Change `dirty_paths` to diff against HEAD, not `base`. `base` is still computed by `steps.base_sha`, still stored as `base_sha`, and still passed to `steps.red_first`. Each control entry gains the key `at_sha`, the output of `git rev-parse HEAD` in `top` (None outside git). The key name comes from the report's Interfaces line.
2. Binding by lineage. In `span_status`, a control binds when its `base_sha` equals the current base, or when `git -C <top> merge-base --is-ancestor <base_sha> HEAD` exits 0. With `top` None, equality alone binds. Cache the ancestor answer per sha within one audit. The criterion_sha256 and old-format handoff_sha256 rules stay as they are.
3. A green own pre-edit control defers to an earlier red. When this attempt's latest pre-edit control is not red, first look for an earlier other-attempt pre-edit red among the bound controls. If one exists, return `preserved` (or `prelude-changed` from `prelude_changed`, as the existing earlier branch does). Only with no such control return `green-baseline`.

Leave `cmd_record`'s exit 1 on a green span unchanged. It is outside the three rules.

Selftest, failing test first. Add the cases below with exactly these `check` titles before changing `dirty_paths`, `cmd_record`, or `span_status`. Run `python3 plugins/sdlc-lite/scripts/redck.py selftest` and paste its FAIL listing into your report. That run is the observed-red control the handoff requires. Then make the fix.

Commits in the shared selftest repo would make later `test -f out.txt` and `dirty == []` cases wrong. Run T1, T3, T4 and T5 in a second `git init` repo under the same tempdir, with their task dirs under that repo's `.sdlc/`. T2 stays in place in the shared repo.
- T1 `T-0473: base kept, A1 work committed: the A3 record is pre-edit at a clean tree and stores at_sha`:
  - Write `base-sha` with the starting HEAD, then record A1 (pre-edit, red).
  - Write `src.txt` and commit only that file. Never `out.txt`: the span would turn green and record would exit 1.
  - Record A3. Assert rc 0, phase `pre-edit`, `at_sha` equal to the new HEAD, and audit A3 `ok`.
- T2 `T-0473: base moved to HEAD, no A3 control: the A1 original on an ancestor base is preserved`:
  - This replaces the check titled `control: a different base sha no longer binds the original` at the current line 394 (the empty `move` commit with `base-sha` set to HEAD).
  - The audit A3 result flips from `missing` to `preserved`.
- T3 `T-0473: a control whose base is not an ancestor of HEAD is not bound (control)`:
  - Take a dir with an A1 pre-edit red control.
  - Rewrite every entry's `base_sha` in `red-checkpoint.jsonl` to a parentless commit made with `git commit-tree` on HEAD's tree and no `-p`, the way the old-format case rewrites entries.
  - Audit A3 must say `missing`.
  - Do not use the dir's `base-sha` file for this. `steps.base_sha` drops a non-ancestor and falls back to HEAD.
- T4 `T-0473: an own pre-edit green defers to an earlier same-lineage pre-edit red: preserved`:
  - Record A1 red at base B0. Commit `out.txt`, then write `base-sha` with the new HEAD.
  - Record A3 (pre-edit, green, rc 1 is expected).
  - Audit A3 must say `preserved`. Today it says `green-baseline`.
- T5 `T-0473: work committed after the base with no earlier red is green-baseline (control)`:
  - Use a fresh dir and write `base-sha` with the pre-commit HEAD. Commit `out.txt` and keep the base at the pre-commit sha.
  - Record A1 (phase pre-edit, green).
  - Audit A1 must say `green-baseline`. Today it says `retrospective`.
  - This covers the report's Risk: committing before the first record never earns a red control.

Every existing check except the line 394 one must keep its verdict. The untracked `src.txt` in the post-edit and resumed-work cases, `out.txt` in the report-claim case, and `primary-dirty.txt` in the T-0420 case stay uncommitted, so they stay `retrospective`. A second flip means a rule is wrong. Stop and report it, and do not edit that check.

Docs (stale-context repair in the same change):
- Rewrite the docstring's phase sentence (lines 11 to 14) to say the phase is read against the working tree at HEAD and that `at_sha` is stored.
- Rewrite the audit binding text (lines 26 to 36) to say the base is the current base or an ancestor of HEAD. The docstring must contain the literal text `ancestor of HEAD`.
- Rewrite the sdlc-internals `scripts/redck.py` paragraph the same way, naming `at_sha`.
- Keep `process-deviations.md` in redck.py, because check.py item 45 requires it there.

Contract dependents, from `git grep -n redck -- ':!.sdlc' ':!docs/reports'`:
- `dispatch.py:1147` and `run.sh:714` call `audit` with unchanged arguments and assert nothing on its output, so they are untouched.
- `agents/builder.md:28` and its generated `builder-L*.md` and Codex TOMLs say "a second `record` is only a base control and is stored as retrospective". That text goes partly stale but stays untouched, because the handoff forbids prompt wording changes.
- The verifier files read only `process-deviations.md` lines, which are unchanged.

Validation scope: the redck selftest; `check.py` (item 45); `git diff --check` on the two files; the scope guard; `check.sh` as the whole gate. Fix any red this step introduces.
### Acceptance criteria
- (red) `python3 plugins/sdlc-lite/scripts/redck.py selftest 2>/dev/null | grep -qxF 'ok: T-0473: base kept, A1 work committed: the A3 record is pre-edit at a clean tree and stores at_sha'`
- (red) `python3 plugins/sdlc-lite/scripts/redck.py selftest 2>/dev/null | grep -qxF 'ok: T-0473: base moved to HEAD, no A3 control: the A1 original on an ancestor base is preserved'`
- (red) `python3 plugins/sdlc-lite/scripts/redck.py selftest 2>/dev/null | grep -qxF 'ok: T-0473: an own pre-edit green defers to an earlier same-lineage pre-edit red: preserved'`
- (red) `python3 plugins/sdlc-lite/scripts/redck.py selftest 2>/dev/null | grep -qxF 'ok: T-0473: work committed after the base with no earlier red is green-baseline (control)'`
- `python3 plugins/sdlc-lite/scripts/redck.py selftest 2>/dev/null | grep -qxF 'ok: T-0473: a control whose base is not an ancestor of HEAD is not bound (control)'`
- (red) `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import redck; sys.exit(0 if 'at_sha' in redck.__doc__ and 'ancestor of HEAD' in redck.__doc__ else 1)" && sed -n '/^## .scripts.redck\.py/,/^## /p' docs/references/sdlc-internals.md | grep -qF at_sha`
- The builder report quotes a redck selftest FAIL run made after the T-0473 cases were added and before the fix, and the misses it lists include the T1, T2, T4 and T5 titles. This is the observed red.
- (guard) `python3 plugins/sdlc-lite/scripts/redck.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/redck.py docs/references/sdlc-internals.md`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/redck.py -e docs/references/sdlc-internals.md)"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Assumptions
- `steps.base_sha` already accepts only a base that is an ancestor of HEAD, so a lineage fixture has to rewrite the jsonl `base_sha`. Verified by `plugins/sdlc-lite/scripts/steps.py:825-839`.
- No selftest outside redck asserts redck output. Verified: `grep -n 'process-deviations\|redck\|red-checkpoint'` over `dispatch.py`, `run.sh` and `run-selftest.sh` shows only the two audit calls (`dispatch.py:1147`, `run.sh:714`).
- The redck selftest passes at HEAD (25 ok lines, about 7 s), and the five T-0473 titles are absent now (each grep exited 1). Verified by running it.
- The docstring has neither `at_sha` nor `ancestor of HEAD`, and the sdlc-internals redck section has no `at_sha`. Verified by the combined probe (exit 1).
- At HEAD, `check.py` exits 0, `git diff --check` on the two files exits 0, and the scope guard exits 0. The scope guard goes red against `HEAD~10`. Verified by running each with `SDLC_BASE_SHA=HEAD`.
- The `check.sh` timeout of 1900 is three times the 615 s run on record in `.sdlc/0233-reorg-apply/planner-L3.md`; another run on record took 513 s. Not re-timed at this HEAD.
- The rule wording, the `at_sha` key, and the rejected sibling-dir alternative come from `docs/reports/2026-10-12-maison-wave-7b-mechanics.md` item 6, its Interfaces line and its Rejected alternatives.

## Risks
- The `check.sh` record is old, and the suite has grown (`dispatch.py selftest` alone took 192 s here). Under concurrent-lane load, 1900 s could be tight. A timeout there means not run, not red.
- `agents/builder.md:28` and its generated copies still say a second record is stored as retrospective. On a branch with committed work it is now pre-edit. The handoff forbids prompt wording changes, so this needs a follow-up wording ticket.
- On a resumed branch whose committed work already makes a `(red)` span green, `redck record` still exits 1. The builder prompt reads that as `plan defect:` (pre-existing, outside the three rules). The audit is fixed (T4), but such a builder may still block. Follow-up ticket.
- Judging the phase against the working tree means a builder that commits before its first record gets `pre-edit`. A green span then still lands on `green-baseline` unless an earlier same-lineage red exists (T5 pins this), so the weakening is bounded by rule 3.
- The ancestor rule accepts any earlier base on the same lineage, including one many commits back. This is the design the report ratified; the sibling superseded-dir read stays rejected.
