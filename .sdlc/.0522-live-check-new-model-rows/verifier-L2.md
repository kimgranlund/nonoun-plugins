<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
The handoff has no bulleted acceptance criteria, so I took its Intent `Do` lines and its `Done when` as the criteria.

- #1 Dispatch one run each for planner, architect, plan-reviewer, verifier L1 and L3, scout, researcher L1, filer, ui-designer L1, and the messenger and conductor. Record the model and effort the host reports: pass. Evidence:
  - I read the host transcripts under `~/.claude/projects/-private-tmp-t0522-1v2wMg-proj` myself, taking `message.model` and `effort` from each record (a python scan of `subagents/agent-*.jsonl` and the session jsonl files).
  - The results match the report's table and `adapters/claude/levels.json` for all 10 leveled rows:
    - planner-L1: sonnet-5-5, high
    - planner-L3: opus-5-5, high
    - architect-L1: opus-5-5, xhigh
    - plan-reviewer-L1: fable-5-1, high
    - verifier-L1: opus-5-5, low
    - verifier-L3: fable-5-1, xhigh
    - scout-L1: sonnet-5-5, low
    - researcher-L1: sonnet-5-5, high
    - filer-L1: sonnet-5-5, low
    - ui-designer-L1: opus-5-5, medium
  - The messenger sub-agent ran sonnet-5-5 at low, matching `agents/messenger.md` lines 4-5.
  - The messenger and conductor session-agent runs (`70621d7a`, `920652c9`, `c077a261`, `d5fb3674`, `8d73fa15`, `b0ffd175` and others) match the report's table.
  - `transcript-models.txt` shows no `model` or `effort` key on any of the 11 spawns, so the rows resolved from the agent type alone.
  - The driver ran at haiku and max, so an inherited value would have shown.
  - Check that bites: the calibration runs (haiku at low, high and max) reported those effort values in the transcript, so the effort field follows the session.

- #2 Confirm whether `effort:` in the messenger and conductor front matter is honored or ignored, and say which: pass. Evidence:
  - The report says honored on a sub-agent spawn (messenger low under a max driver, transcript `a2c350ad` shows low).
  - It says ignored for a session started with `--agent`: `8d73fa15` (conductor under project effort high) ran at high, not the front matter's medium.
  - `b0ffd175` (messenger session under project effort high) ran at high, not low.
  - `model:` is honored: the conductor ran opus-5-5 and the messenger sonnet-5-5 under a sonnet project default.
  - The caveat that the `"agent"` settings key was not tried is stated in the report.

- #3 Write `docs/reports/<date>-live-model-rows.md` with the evidence and anything unverified: pass. Evidence:
  - `docs/reports/2026-10-13-live-model-rows.md` exists and follows the 2026-10-12 report's pattern.
  - Its supporting files are in `docs/reports/2026-10-13-live-model-rows/`.
  - The "does and does not show" section lists what was not checked: other rows, the `dispatch.py prepare` path, Codex, one run per row.

- #4 Done when: each row is marked verified or unverified with a reason, and a wrong-model row is filed as a bug: pass. Evidence:
  - Every row in both report tables carries "verified" with a reason or source.
  - No row launched with the wrong model: all 11 sub-agent rows and the session-agent rows match, so no bug is owed.
  - The conductor `effort: medium` no-op is recorded as a follow-up, not a wrong-model launch.

- Hygiene: pass. Evidence:
  - `git diff --check` exits 0.
  - The em dash count is 0 in all six added files.
  - `verify_scope.py 35fdddae --handoff ...` prints `docs-only` and exits 0.

## Out of scope changes
None. The six untracked or intent-to-add files are all the new report and its evidence directory. `git status --short` shows no modified tracked files. The builder's `git add -N` is intent-to-add only, with no content staged.

## For the next attempt
None

## Notes
- `docs/reports/2026-10-13-live-model-rows.md`, header: the report says the rows are "the ones T-0519 and T-0520 landed for 0.22.7" while `plugin.json` still reads 0.22.6. The report states this itself, so the evidence binds to commit `35fdddae`, not to a release.
- `/tmp/t0522.1v2wMg` was left behind as scratch. It is harmless, and the builder disclosed it.
