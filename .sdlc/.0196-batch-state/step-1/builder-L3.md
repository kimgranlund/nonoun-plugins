<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added `batch_verified(step_dir)` and the module constant `BATCH_PATH_RE` just above `next_action`. `next_action` now calls it once, in the branch where no step verifier counts after the build, and returns `done` when it names a task-dir verifier result. The module docstring has the new `next` rule (names `## Verified` and every exclusion) and one `resume` sentence. Added 16 selftest cases with the prefix `next batch: `.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: new section `## Batched verifier result (task dir)` placed before `## Free-text arguments`.
- `docs/maintenance/sdlc-internals.md`: added one clause to the `steps.py` `next` description. It names `## Verified`, the newest-listing rule and the exclusions.

## Checks
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS. All 16 `ok: next batch:` lines print, including the positive case (next and resume print done), the newer builder whose runs.jsonl order contradicts the -2 name, unlisted step, L4, L5, Merge title, gates green title, last step, superseded sibling, Verdict fail, newer fail over older pass and the reverse, disjoint batches, structurally invalid task verifier, and per-step fail giving rebuild.
- `python3 plugins/sdlc-lite/scripts/order.py selftest`: PASS.
- `python3 plugins/sdlc-lite/scripts/results.py selftest`: PASS.
- All 11 acceptance criteria, pulled verbatim from the handoff and run under `bash -c`: every one rc=0. The (guard) ran with `SDLC_BASE_SHA=aa145c4a4087daa45bef699c2b1b6292a55e34a8`.
- Negative controls: mutated copies of steps.py in a `mktemp -d` dir, `steps.py selftest` run on each:
  - L4/L5 exclusion disabled: the L4 and L5 cases fail.
  - Merge-or-gates title check disabled: both title cases fail.
  - gates green check alone disabled: the gates green case fails.
  - last-step check disabled: the highest-numbered case fails.
  - superseded check disabled: the superseded case fails.
  - structure_error check dropped: the invalid task verifier case fails.
  - newest-listing "return None" changed to "return w": the fail, newer-fail and invalid cases fail.
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0.
- `python3 scripts/check-packaging.py`: PASS.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: Codex agent definitions verified.
- `git diff --check`: clean.

## Notes
- If a step handoff has no `## Step <n>:` line, the title counts as empty. Such a step is not excluded and can still be batch-verified; the handoff does not cover this case.
- The `next_action` call site rebuilds `step-<n>/<builder>` only for the reason string. The decision rule exists only in `batch_verified`, as one function plus one call site.
- `sdlc-internals.md` does not yet say `board.py` imports `batch_verified`, because that lands in step 2. `handoff-format/SKILL.md` already says `board.py` renders it, because the handoff requires that sentence.
- Scratch files went to `mktemp -d` and `/tmp/*.out`, outside the repo. Nothing was committed.
