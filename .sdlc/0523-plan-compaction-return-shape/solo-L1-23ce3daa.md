<!-- role=solo level=L1 model=sonnet effort=high -->
## Output
🟢 T-0523 is fixed. The kind now states one return shape, and the selftest checks it. I didn't run `/plan compaction` itself, so I haven't checked a live replay against the new text.

**What was wrong:** the `lines:` and `pin:` lines were already separate in the lint output. The skill text just never forbade extra lines. Section 6 said "block, `lines:` line, `Run:`" without saying it was the whole reply. Section 1 also said to "report" the stale line, which added attention lines.

**Files changed**
- `plugins/sdlc-lite/skills/plan/references/compaction.md`: section 6 is now the single statement of the shape. The reply is the fenced block, `lines: N of 60`, `pin: M of 40` and `Run: /compact <paste>`, with nothing before the fence or after `Run:`. A `stale:` line from section 1 is the only allowed exception, and it goes before the fence.
- `plugins/sdlc-lite/scripts/plan_check.py`:
  - Adds `compaction --reply`, which checks the whole reply under the rule `compaction-return`.
  - The selftest has two positive cases and eight negative controls. The negatives are a sentence before the fence, a line after `Run:`, `lines:` and `pin:` merged, a wrong count, a missing `Run:`, an unclosed fence, and a CLI exit-1 case. The last case is the example block in `compaction.md` run through the shape check.
- `plugins/sdlc-lite/skills/plan/evals/06-compaction.expected.md` and `README.md`: replay step 3 now includes the `--reply` command.

**Checks**
- `plan_check.py selftest` passes (333 checks, all new `compaction-return` lines ok).
- `compaction_handoff.py selftest` passes.
- `scripts/check.py` passes.
- `scripts/check-packaging.py` passes.
- `git diff --check` is clean, and the added lines contain no em dashes.

No acceptance criteria were written and no verifier ran, because the ticket is L1. Nothing is committed.

**Still open:** a live `/plan compaction` run, to see whether the model follows the new section 6 text. That needs a separate replay.
