<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- No planned step failed. Verdicts: step 1 (verifier L2) pass, step 2 (verifier L1) pass, step 3 (verifier L1) pass. No `process-deviations.md` exists in the artifacts dir or any step folder, so there are no process deviations to list.
- The ticket's Done-when asks for one live check that Claude Code loads `CLAUDE.local.md` after `/compact`. It is unverified. A headless builder cannot run `/compact`, and the report line reads `unverified [U]`. `--write-handoff` stays off by default.
- The replay in `docs/reports/2026-10-12-compaction-prompt-replay.md` is marked "unverified: not an independent run". The step 2 builder wrote the fixtures, the prompts, both summaries per fixture and the scores, and no summarizer model ran. The replay does not show that the prompt helps. The outcome metric still has no measured before value.
- Step 1's verifier did not reproduce the builder's red-first run for the `plan_check.py` rules, because the stub was gone. It ran its own mutant blocks, and each rule fired on its defect. The `compaction_handoff.py` red controls were five sed mutants of a temp copy, run by the builder.
- Step 3's live skill run is one headless run with `--dangerously-skip-permissions` and `SDLC_ROLE=conductor` inherited from the parent shell. The verifier did not re-run it. It checked the saved stdout and the lint only.

## PR title
T-0465: /plan compaction kind authors one linted /compact prompt

## PR body
Summary: `/sdlc-lite:plan compaction [--write-handoff|--clear] [<prose>]` is now a sixth kind of the `plan` skill. It authors one `/compact` prompt in a fixed shape and returns it as a single fence with a `lines: N of 60` note and `Run: /compact <paste>`. It never runs the compaction. The prose argument is passed through as data. `compaction` is a reserved first word, so a goal that starts with it is written `goal compaction ...`.

Changes:
- `plugins/sdlc-lite/scripts/plan_check.py`: new `compaction` kind with nine rules and a good-block selftest. The rules cover:
  - section order and closed verbs;
  - a 20-word line cap;
  - the 60-line and 40-PIN caps;
  - em dash;
  - lines copied from `CLAUDE.md` or `AGENTS.md`;
  - the DECISION shape;
  - `[U]` marking of inferred approvals.
- `plugins/sdlc-lite/skills/plan/SKILL.md`: hint, description, arguments, router row and reserved word. It is 71 lines and 6599 bytes.
- `plugins/sdlc-lite/skills/plan/references/compaction.md`: new, 90 lines, with the grammar and one worked example.
- `plugins/sdlc-lite/skills/plan/scripts/compaction_handoff.py`: new. `--write-handoff` writes only `CLAUDE.local.md`, inside these guards:
  - it needs a Claude Code host;
  - the file must be gitignored;
  - the section is one replaceable `## Compaction handoff` H2 of at most 8 lines;
  - `--clear` removes only that H2 and restores the earlier bytes.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: routing row for `plan compaction`.
- `plugins/sdlc-lite/scripts/check.py` item 31: the kind's phrases, with an inline negative control.
- `plugins/sdlc-lite/scripts/check.sh`: runs the handoff selftest.
- `.gitignore`: adds `CLAUDE.local.md`.
- `plugins/sdlc-lite/skills/plan/evals/`: case `06-compaction` and an updated README.
- `docs/reports/2026-10-12-compaction-prompt-replay.md` and its fixtures folder: the recorded replay (marked unverified, not an independent run) and a live skill run section with its saved stdout and prompt.

Verification:
- Step 1, verifier L2, pass:
  - `plan_check.py selftest` passes (293 checks), and `compaction_handoff.py selftest` passes (6 cases).
  - The reference block lints `lines: 18 of 60`, `pin: 7 of 40`, exit 0.
  - `plan_check.py compaction --text "DROP x"` exits 1 with `FAIL compaction-order`.
  - The verifier's own mutants fired the verb, decision, approval, em dash, long-line, last-NEXT and AGENTS-copy rules.
  - It also probed the handoff script in a temp repo.
  - `check.py`, `prompt_lint.py` (22 files, 0 errors) and `check-packaging.py` pass.
  - The scope diff against the base is empty, and no `AGENTS.md`, `CLAUDE.md`, `plan-loop` or redirect stub changed.
- Step 2, verifier L1, pass:
  - `bash plugins/sdlc-lite/scripts/check.sh` passed, as did `check.py`, `check-packaging.py` and the selftest.
  - `git diff --check` and the scope guard pass.
  - The three fixture prompts and the run on this repository each lint `ok: compaction plan passes`. Their pin counts and the word counts of the six summaries match the report.
- Step 3, verifier L1, pass:
  - `SDLC_HEADLESS=1 claude -p --plugin-dir plugins/sdlc-lite --model sonnet '/sdlc-lite:plan compaction "finish the loose ends of T-0465"'` exited 0 and returned one fence, `lines: 23 of 60 (lint: pin 10 of 40)` and `Run: /compact <paste the block above>`.
  - `plan_check.py compaction` on the saved fence body exits 0. The fence body is byte-identical to the one in the saved stdout.
  - A control with `RULES` changed to `RULEZ` printed `FAIL compaction-order` and `FAIL compaction-verb`.
  - The git status of `CLAUDE.local.md`, `AGENTS.md` and `CLAUDE.md` is clean, and `git diff --check` passes.

Not shown: the `CLAUDE.local.md` reload after `/compact`, and any measured benefit of the prompt over a free `/compact`.

## Changelog entry
- Added `/sdlc-lite:plan compaction [--write-handoff|--clear] [<prose>]`, a plan kind that authors one linted `/compact` prompt, with a `plan_check.py compaction` lint. Optional `--write-handoff` writes a guarded section in the gitignored `CLAUDE.local.md`.

## Follow-ups
- decide: Run one live check that Claude Code reloads `CLAUDE.local.md` after `/compact`, plus an independent replay of prompt vs free `/compact` by a session that did not build the skill. Until then `--write-handoff` stays off and the outcome metric has no before value.
- fix-now: Reconcile the live skill output with the kind's return shape. It printed one sentence before the fence and three attention lines plus a next-action line after `Run:`, and merged the lint's `lines:` and `pin:` lines into one.
- note: `compaction_handoff.py` goes beyond the step handoff in two places: `write` exits 2 on an empty body, and `status` prints `stale: written unknown` when the section has no `Written` line.
- note: Rule readings the handoff left open: `compaction-entry-copy` counts 4 words on the whole line, verb included. `compaction-decision` skips `none` and POINT lines. A `none` line in DROP is flagged by `compaction-verb`.
- note: `docs/reports/AGENTS.md` calls reports immutable. The step 3 builder appended a section to the untracked replay report because the step handoff directed it.
