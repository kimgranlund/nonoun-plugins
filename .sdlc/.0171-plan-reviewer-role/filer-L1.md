<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0171: Add an independent plan-reviewer role that gates risky plans and replans

## PR body
### Summary
A cross-cutting or risky plan, or any replan, now gets a fresh-context review before any builder starts. The new `plan-reviewer` role returns `pass`, `replan`, or `blocked` with findings tied to steps. It never rewrites the plan or edits code. It runs on a different model family from the planner, on both Claude Code and Codex, through `scripts/run.sh`.

All six steps passed their verifiers. Step 6's first builder attempt was killed with exit 137 while `check.sh` ran. The rerun is the one recorded in the artifacts.

### Changes
- **Planner contract (step 1):** `agents/planner.md` gains a `## Assumptions` section. Each item reads `verified by <how>` or `unresolved: <decision>`. Each `### Do` must now name targets, settled interface decisions with evidence, `Depends on:`, and focused checks. Rule 9 gains the `plan review:` replan handling.
- **Claude role (step 2):**
  - `agents/plan-reviewer.md` is new. It checks seven things and the verdict rules.
  - `run.sh` gets an Opus high row for L1, the required section `Verdict` with values `pass|replan|blocked`, and read-only tools.
  - The family rule: after an Opus planner L2 the review moves to Fable high. After a Fable or Sonnet planner it stays Opus high.
  - `level-rubric` gets the row and a `## When a plan is reviewed` section.
  - `order.py` and `check.py` accept the hyphenated role name.
  - `run-selftest.sh` covers the swap.
- **Routing (step 3):**
  - New `steps.py review <task dir>` prints `review L1`, `split`, `replan`, or `stop`.
  - A review is required for planner L3, any step at L4 or L5, a `Merge` step, and any plan with `## Plan review`.
  - A second `replan` verdict, a `blocked` verdict, or an `unresolved:` item stops for the user.
  - `split` refuses a plan whose review said `replan`.
  - `/chain`, the conductor, `/plan`, `handoff-format`, `docs/references/sdlc-internals.md`, and `check.py` are updated to match.
- **Codex (step 4):** `models.json` gets `plan-reviewer` L1 at `gpt-6-astra` high. The alternate follows the newest planner's recorded model, so `gpt-6.1-sol` high reviews Astra plans. Regenerated TOML profiles, `codex_roles.py`, `codex_exchange.py`, `instructions.md`, and `docs/references/codex-role-execution.md` are updated, with new selftests. The base and alternate profiles now number 24 project agent definitions.
- **Live validation doc (step 5):** `docs/reports/plan-reviewer-live-run.md`, its copied evidence, and one `docs/README.md` entry.
- **Gates (step 6):** no fixes were needed.

### How each step was verified
Each step was checked by an independent verifier against its acceptance criteria.
- **Step 1 (verifier L1, pass):** four greps for `## Assumptions`, `unresolved:`, `plan review:`, and `Depends on:`. Each is absent at base, so each can go red. `check.py` and the scope guard passed.
- **Step 2 (verifier L2, pass):**
  - The dry run prints `--model opus --effort high`. The Opus planner case gives `--model fable`. The Fable planner case gives `--model opus`.
  - The tool ban and the required section line are present.
  - The verifier set the fable line back to `opus` in a temp copy, and the check went red, so the family rule is what makes it pass.
  - `check.py` (19 role levels, 9 agents), `run-selftest.sh`, and `order.py selftest` passed.
- **Step 3 (verifier L2, pass):**
  - 13 routing cases ran verbatim: routine → `split`, each trigger → `review L1`, `pass` → `split`, `replan` → `replan`, two replans → `stop`, `blocked` → `stop`, `unresolved:` → `stop`, and the split refusal.
  - `steps.py selftest` has 22 new `(r)` cases with negative forms. At base, `review` is an invalid choice and `split` of a replan-rejected plan writes `step-1`.
  - The verifier called the `grep -q 'ok: (r'` predicate weak, because 3 such lines already exist at base. It counted the new cases directly instead.
- **Step 4 (verifier L2, pass):**
  - `resolve plan-reviewer L1` gives `gpt-6-astra high`. The Astra planner fixture gives `gpt-6.1-sol high`. The Sol planner fixture gives `gpt-6-astra high`, which is the negative case.
  - Both new selftests go red at base.
  - `codex_roles.py generate --check` and the full `codex-selftest.py` (22 tests) passed.
  - `check-packaging.py` printed PASS.
- **Step 5 (verifier L2, pass):**
  - The live run in a throwaway project is documented in `docs/reports/plan-reviewer-live-run.md`.
  - On Claude, the reviewer returned `replan` on the hand-written defective plan. `runs.jsonl` records it at `opus`/`high`.
  - On Codex, the reviewer returned a rejecting verdict (`replan` or `blocked`) on the defective plan. The result header shows `model=gpt-6.1-sol`.
  - The sound plan passed on the first review. It went through split, builder L1, and verifier L1 with a `pass` verdict.
  - The verifier replayed `steps.py review` and `split` on copies of the evidence. It also ran the family rule itself under `SDLC_DRY_RUN=1`, with a `sonnet` control.
  - The model runs themselves were not re-run.
- **Step 6 (verifier L1, pass):** `bash plugins/sdlc-lite/scripts/check.sh` returned rc=0. Shellcheck was skipped because it is not installed. `check-packaging.py` printed PASS. `git diff --check` was clean.

### Limits
- No benefit is claimed. Completion time, replans, rebuilds, and correctness are not yet measured against the same tasks without the reviewer. The `Done when` measurement is not part of this change.
- The sound-path live run passed on the first review, so the `/chain` replan loop did not run live.
- No existing Claude or Codex model row was changed.

## Changelog entry
- Added the `plan-reviewer` role on Claude Code and Codex. It reviews plans by planner L3, plans with an L4 or L5 step or a merge step, and every replan before a builder starts.
  - It returns `pass`, `replan`, or `blocked` with findings tied to steps.
  - It uses a different model family from the planner.
  - `steps.py review` routes the verdict.
  - The planner handoff now carries an `## Assumptions` section and settled interface decisions.

## Follow-ups
- decide: `steps.py review` is enforced only by docs, the `check.py` route words, and the `split` refusal. A conductor that never runs it on a plan with no reviewer result still splits, and no script catches that.
- fix-now: The `run.sh` comment near line 217 still describes only the verifier, though the code resolves the Codex alternate for every role (step 4 builder note).
- note: `verifier_alternates` and `shared_with_builder` keep their names while also serving the plan-reviewer, so the names understate their scope.
- note: `/chain` 4.2 mid-build replans still go straight to `steps.py split --only` without `steps.py review`, and the 4.2 item text was left unchanged (step 3 builder note).
- note: The bench comparison against the same tasks without the reviewer is not done. That measurement is required before any claim the reviewer helps.
