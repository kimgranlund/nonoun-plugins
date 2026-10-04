<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0196: Step state for a whole-ticket (batched) verifier result

## PR body
### Summary
A task-dir verifier result can now verify several steps at once, and the step tools can read it. A passing result lists the builder result files it verified under `## Verified`. `steps.py next` and `resume` treat a listed, unchanged step as verified, and `board.py` shows it. A step rebuilt after the listing, or one not listed, still resumes at `verify`.

This ships the reader only. Nothing yet tells a task-dir verifier to write `## Verified`. That producer text is a later ticket (T-0199 conductor rules).

### Changes
- `plugins/sdlc-lite/scripts/steps.py`:
  - New `batch_verified(step_dir)` and `BATCH_PATH_RE`. This is the one copy of the rule. Newest-result ordering comes from `order.py`, not file mtime.
  - `next_action` calls it once, only when no step-dir verifier counts after the build.
  - The step keeps per-step verification when any of these hold:
    - the build is L4 or L5;
    - the step title starts with `Merge `;
    - the title contains `gates green`;
    - it is the last step;
    - it has a superseded sibling dir;
    - the verdict is fail, or the task verifier is structurally invalid.
  - A newer fail listing overrides an older pass for the same build.
  - Docstring updated, plus 16 `next batch:` selftest cases.
- `plugins/sdlc-lite/scripts/board.py`: imports `steps` and renders `🟢 pass · builder <L> · batch verifier <L>` when `steps.batch_verified` returns a path. A step rebuilt after the batch shows `built · builder <L>, awaiting verify`. Two `batch:` selftest cases.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: new section `Batched verifier result (task dir)`, which is the result contract.
- `docs/maintenance/sdlc-internals.md`: one clause each for the `steps.py` and `board.py` entries.

### Verification
Both steps got an independent verifier verdict of pass. Step 1 was built at L3 and verified at L2. Step 2 was built at L2 and verified at L1.
- Step 1:
  - All 10 criteria and the scope guard pass. Each new-behavior criterion was run on the built tree (rc=0) and at the base SHA (rc=1), so each can go red.
  - `steps.py selftest` prints 16 `ok: next batch:` lines. `order.py` and `results.py` selftests pass.
  - Negative controls, all run in mutated copies of `steps.py`. The builder disabled each of these in turn and the matching case failed:
    - the L4/L5 exclusion;
    - the `Merge ` and `gates green` title checks;
    - the last-step check;
    - the superseded check;
    - the structure-error check;
    - the newest-listing rule.
  - The verifier separately re-disabled the superseded check, and its case failed.
- Step 2:
  - `board.py selftest` prints two `ok: batch:` lines. A selftest run in a detached worktree at the pre-change HEAD printed none.
  - The positive render and the rebuilt-after-batch guard both pass.
  - The scope guard allows only `board.py` and `sdlc-internals.md`, and it passes.
- Gates run by the verifiers (all exit 0):
  - `bash plugins/sdlc-lite/scripts/check.sh`
  - `python3 scripts/check-packaging.py`
  - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
  - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
  - `git diff --check`

Known limits:
- No live host run, as the burn-down brief set. Evidence is selftests, gates and the verifiers.
- `check.sh` skipped shellcheck because it is not installed.

## Changelog entry
- A whole-ticket verifier result that lists builder results under `## Verified` now marks those steps verified in `steps.py next` and `resume`, and `board.py` shows them as batch-verified. A step rebuilt after the listing, or one not listed, still resumes at `verify`. Steps at L4 or L5, merge steps, gates green steps, the last step and replanned steps always keep per-step verification.

## Follow-ups
- note: Nothing instructs a task-dir verifier to write `## Verified` yet, so batching is inert until the conductor, chain and verifier text change (T-0199).
- note: Gates and last-step exclusion is heuristic (title contains `gates green`, or highest step number). A non-last gates step with another title could be batch-verified, and a stricter marker would be a planner contract change.
- note: A step handoff with no `## Step <n>:` line counts as an empty title, so it is not excluded and can be batch-verified. The handoff does not cover this case.
- note: A conductor that reruns a batch after a partial fail must re-list the passing steps, or they fall back to per-step `verify`. This costs one extra verify and is deliberate.
