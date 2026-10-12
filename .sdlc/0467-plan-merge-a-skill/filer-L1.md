<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- Both steps passed their verifiers: step 1 passed at verifier L2 and step 2 at verifier L1. No `process-deviations.md` exists in the artifacts dir or the step folders, so there is no process deviation to report.
- The handoff's done-when asks for a five-ask replay, with goal and fanout at a minimum. Only goal and fanout were run. Steps, doc and campaign were not run.
- The replay is unverified. The step 2 builder ran both the old and the new skill, so identical rows follow from that setup. The report says "unverified: not an independent run".
- The step 1 verifier could not run an external mutant of the `check.py` item 57 gate. The stray-worktree hook blocked `git worktree add` because `SDLC_TMP_WORKTREES` was unset. Only the inline controls that run on every `check.py` run observed the gate rejecting a defect.
- The new skill's reference files, evals and the replay report are untracked, so nothing is committed. `SKILL.md` names its six reference files as code-span paths instead of Markdown links. `check.py` item 32 counts a link from a tracked file to an untracked one as broken.

## PR title
T-0467: Merge plan skills A: new /plan skill with kinds steps, doc, goal, campaign, fanout

## PR body
### Summary
`/sdlc-lite:plan <kind> [args]` is now one skill with kinds `steps` (default), `doc`, `goal`, `campaign` and `fanout`. The shared rules sit in one reference, and a dry run prints before every fenced block. This is ticket A of the design's build split. The four old plan skills are left untouched and still work until B.

### Changes
- `plugins/sdlc-lite/skills/plan/SKILL.md`:
  - It is rewritten as the kind router plus the shared procedure, at 68 lines and 5886 bytes (cap 90 lines and 7168 bytes).
  - The description carries the trigger phrases of all five kinds.
  - Kind resolution is the first argument token, else `steps` when the rest names a `handoff.md`, else one `AskUserQuestion`.
  - The first word of a kind is reserved.
- `plugins/sdlc-lite/skills/plan/references/`:
  - New files are `plan-rules.md`, `steps.md`, `goal.md`, `campaign.md`, `doc.md` and `fanout.md`.
  - `goal.md` and `doc.md` are byte copies of `goal-rules.md` and `plan-doc-format.md`.
  - `steps.md` is the old dispatch procedure moved whole.
  - `fanout.md` differs from `fanout-rules.md` in one label, because `prompt_lint.py` P-2 rejects the flag `fanout.py --help`.
- `plugins/sdlc-lite/skills/plan/evals/`: `README.md` and five ask and expected pairs (goal, fanout, doc, steps, campaign).
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: one `plan <kind>` row added; the old rows are unchanged.
- `plugins/sdlc-lite/scripts/check.py`: new item 57, "Plan kinds (T-0467)", with inline negative controls.
- `docs/reports/2026-10-12-plan-merge-replay.md`: the goal and fanout replay on the old and the new skill.

### Verification
- Step 1 verifier (L2) passed all 12 criteria:
  - The verifier ran the file, line-count, byte-count, phrase, description and entry-row checks and `cmp` on the two copies, all exit 0.
  - `check.py` printed `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
  - `prompt_lint.py` over the new files and its default set (73 files) reported 0 errors.
  - `check-packaging.py` passed, and `plan_check.py selftest` printed `PASS (252 checks)`.
  - The scope guard was empty, and `git diff --check` was clean.
  - `claude_roles.py generate --check` and `codex_roles.py generate --check` both passed.
- Step 2 verifier (L1) passed all 8 criteria: the report contents, `check.sh`, `check.py`, `check-packaging.py`, `plan_check.py selftest`, `git diff --check` and the scope guard.
- Replay result (builder-run, so unverified): old and new skill give the same result on both asks.
  - Goal: 3 warn-questions and 0 refusals in both.
  - Fanout: 1 warn-question and 1 `plan_check.py` refusal (`FAIL overlap`) in both.
  - The `FAIL overlap` was fixed with `--allow-overlap`, and the lint then ended `ok: fanout plan passes`.
- Limits: steps, doc and campaign were not replayed. The `check.py` item 57 gate has not been shown rejecting a defect outside its own run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `/sdlc-lite:plan <kind>`: one skill with kinds `steps` (default), `doc`, `goal`, `campaign` and `fanout`, shared rules in `references/plan-rules.md`, a dry run before each block, and five eval ask pairs. `check.py` item 57 pins it. The four old plan skills still work.

## Follow-ups
- decide: `plan_check.py fanout` refused with `FAIL overlap` for T-0498 and T-0499 because both cite the same evidence report, while `fanout.py run --dry-run` printed `overlap (planned scope): none` for the same pair. The two checks use different overlap definitions, so say which should win (replay report, second follow-up).
- fix-now: run an independent replay of the goal and fanout asks (a fresh reader per skill) and record its questions and refusals counts in `docs/reports/2026-10-12-plan-merge-replay.md`, since the builder-run table cannot show a difference.
- note: the replay did not exercise the `steps`, `doc` and `campaign` kinds, so their dry-run output and first-return lint results are unobserved.
- note: the `cost:` line for a missing spend cap reads `$10 of $unknown ...; warn: no cap given`. The plan rules define `unknown` only for a missing ticket size, so this form was the builder's choice and no rule covers it.
- note: the new reference files are untracked. Track them in the commit; after that the code-span paths in `SKILL.md` could become Markdown links.
