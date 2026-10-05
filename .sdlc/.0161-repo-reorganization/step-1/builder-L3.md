<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `.sdlc/0161-repo-reorganization/spike/layout.md`: new trial layout. Homes are `maintenance/`, `reference/` (takes `codex-role-execution.md`, `plugin-compatibility.md`) and `reports/` (takes `claude-handoff.md`, `claude-response.md`). It freezes the four required paths. One sentence says `generative-constructs` and `repo-onboarding` stay topics, and why.
- `.sdlc/0161-repo-reorganization/spike/reorg_plan.py`: new read-only plan prototype. It uses Python 3.9 and the standard library only. It imports `parse_layout`, `frozen_match`, `_frozen`, `list_documents`, `scan_lines` and `LayoutError` from `onboard.py`. Options are `--layout` (required) and `--json`.
- `.sdlc/0161-repo-reorganization/spike/plan.json`: exact stdout of the `--json` run.
- `.sdlc/0161-repo-reorganization/spike/plan.txt`: the human-readable tables.
- `.sdlc/0161-repo-reorganization/spike/review.md`: one row per move (there are no unplaced files) marked ok or wrong, with a reason and the verdict a person would give, plus a short summary of the findings.

## Checks
- Criterion 1 (the four paths are frozen by the layout): PASS
- Criterion 2 (all required JSON keys present): PASS
- Criterion 3 (`diff` of a fresh `--json` run against `plan.json`): PASS, no difference
- Criterion 4 (both generative-constructs files are in `baseline_broken`): PASS
- Criterion 5 (no frozen path in moves or rewrites): PASS
- Criterion 6 (all four loose docs are in moves or unplaced): PASS
- Criterion 7 (`cite_forms` values are ints; ambiguity kinds are valid): PASS
- Criterion 8 (`test -s plan.txt`): PASS
- Criterion 9 (every move and unplaced path appears in `review.md`): PASS
- Guard: `git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'` is empty: PASS
- Guard: no untracked files outside `.sdlc/0161-repo-reorganization`: PASS
- Extra: a fresh table-mode run matches `plan.txt` byte for byte. `py_compile` passes on python3 3.9.6.
- Extra: `git grep` for the four file names confirms the cite counts: 12 inline links and 6 backticked paths in non-frozen files, and 25 mentions in frozen files (23 under `.sdlc/`, 2 in `docs/reports`).
- Probe 1: a throwaway layout (`probe-layout.md`, deleted afterwards) triggered `multi_home` and `into_frozen`.
- Probe 2: an in-process run with a simulated tracked `docs/reports/Claude-Handoff.md` triggered a case-folded `name_collision`.

## Notes
- Result on this repository: 16 candidates, of which 12 are placed. There are 4 moves, 0 unplaced files and 0 ambiguities. The moves imply 14 link rewrites, and 2 links are broken before any move (the expected sibling UI project links).
- The review marks 2 of the 4 moves wrong. `claude-handoff.md` and `claude-response.md` are dated correspondence bound to specific commits, so a person would freeze them in place. The frozen-candidate rule missed both: one has a `Date:` line, not `Recorded:`, and the other has no date line at all. This is evidence for the step 2 recommendation.
- Extra JSON keys beyond the required set:
  - `layout`
  - `summary`
  - `unrewritten_cites` (the backtick, code-fence, other and non-Markdown cites, listed per line)
  - `frozen_cites_of_moved`
  - `form` on each rewrite
  - `detail` on each ambiguity
- `cite_forms` always carries all of these keys, as 0 when a form is absent: `markdown_link`, `reference_link`, `html_link`, `autolink`, `anchor`, `backtick_path`, `code_fence`, `other`, `non_markdown`, `in_frozen_files`. A link with a `#fragment` to a moved doc is counted only under `anchor`.
- Choices the rules did not settle:
  - A link that leaves the repository (a `..` prefix after resolving) counts as broken whatever is on disk, so `baseline_broken` does not depend on the machine.
  - A multi_home, name_collision or into_frozen case is held out of `moves` and reported only under `ambiguities`.
  - Frozen-candidate detection also flags a date in a folder name, reported as "date in folder name". With `bench/results/` unfrozen this flagged 128 files.
- The two-sources-one-destination collision code path was not exercised: no two documents under `docs/` share a file name.
- Nothing outside `.sdlc/0161-repo-reorganization/spike/` was written. No ticket was created and nothing was committed.
