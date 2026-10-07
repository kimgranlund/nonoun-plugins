<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: new `# --- lane ---` section between review and swap. It adds `LANE_MAX_STEPS`, `LANE_MAX_CRITERIA`, `LANE_CONTRACTS`, `is_lane_contract`, `scope_entry`, `scope_entries`, `agents_owner`, `lane_sticky`, `lane_action`, `lane_record`, `lane_text`, `record_lane`, and `cmd_lane`. It also adds `criteria_count`, which `lean_warnings` now calls, and `is_scope_span` and `repo_path_ok`, which `widen` now calls. Other edits: the `lane` subparser and its dispatch in `main`, the docstring `Usage:` line and the `  lane      lane <task dir>: ...` entry, and 9 `(lane)` selftest cases.
- `docs/references/sdlc-internals.md`: a `lane <task dir>` clause in the `## scripts/steps.py` paragraph, right after the `review` clause that ends "(/chain 3 runs it after each planner run)".

## Checks
- All 13 acceptance criteria, run verbatim through `bash -c` from the repo root: 13/13 PASS. That covers criteria 1 to 10 and the three guards: `results.py selftest`, the em dash grep, and the scope diff against `$SDLC_BASE_SHA`.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: `steps selftest: PASS`. The 9 `(lane)` labels print `ok:`, and the existing `(lean)` and `widen:` cases still pass after the refactor.
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0, "ok: 19 role levels, 9 agents checked". The SCHEMA_COPY check is not tripped.
- `git diff --check`: clean.
- Mutation controls on a temp copy of the scripts dir. Each mutation turned the selftest red:
  - `LANE_MAX_CRITERIA = 13`: the full-after-planning case failed.
  - L mapped to lean before planning: the before-planning case failed.
  - `or {}` removed: a traceback.
  - Owner threshold changed to `> 2`: the full-after-planning case failed.
  - Sticky reason removed: the recorded-full case failed.
- Manual write-error case: `skips.md` made a directory, then `steps.py lane <dir>`. Output was one `steps lane: cannot write <path>: [Errno 21] Is a directory: ...` line on stderr, nothing on stdout, rc 1.
- Manual smoke run on `mktemp -d` dirs: a size M handoff gives `lean` and creates the exact skips.md, a second call appends a duplicate line, and `lane /nonexist` exits 1 with one stderr line.

## Notes
- After planning, rules 8 to 11 are collected rule by rule, not step by step. All step criteria-count reasons come first, in plan order, then all no-allow-list reasons, then the non-path entries, then the contract paths, then rule 12. Within one step, scope entries are deduplicated in order.
- `lane_text` adds a newline to a `skips.md` whose last line has none, so the inserted record starts on its own line. That is the only change to an existing line. Otherwise skips.md is read and written with `newline=''`, so CRLF bytes are kept.
- The `cannot write <path>` OSError path has no selftest label, because the handoff listed none. It was checked by hand as shown above.
- `import tickets` sits inside `lane_action` with a comment saying why. The results.py selftest copies steps.py beside only order.py and results.py, and its guard stays green.
- `lean_warnings` now uses `criteria_count`, and `widen` now uses `is_scope_span` and `repo_path_ok`. Behavior is unchanged, and the existing `(lean)` and `widen:` selftest cases cover both.
- I did not run `steps.py lane` on the real `.sdlc/0197-lane` dir, so no stray `skips.md` was written there.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md` is untouched, as the handoff says; step 3 adds the skips.md entry.
