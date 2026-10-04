## Task goal
Teach steps.py and board.py the step state of a whole-ticket (task-dir) verifier result so batched verification is visible and a rebuild after the batch is detected.

## Step 1: Batch verification step state in steps.py next and resume
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none.

Implementation targets:
1. In `plugins/sdlc-lite/scripts/steps.py`, add one public function `batch_verified(step_dir)`. It returns the path of the task-dir verifier result that verified this step's newest build in a batch, or `None`. Put it next to `next_action`. This is the only copy of the rule. Step 2's `board.py` imports it, so the two cannot drift. The rule, in order:
   - The step dir name must fullmatch `step-\d+`. The task dir is its parent.
   - Return `None` (the step needs per-step verification) when any of these hold:
     - `b = order.newest(step_dir, 'builder')` is `None`, or its `build_status_or_none(b)` is not `done`.
     - `result_level(b) >= 4`. The per-step L4/L5 constraint comes from the handoff, and the build level is the one that counts after a bump.
     - The step handoff's `## Step <n>: <title>` line (`STEP_RE`) has a title that starts with `Merge `. Precedent: `plan_facts`/`review` use `startswith('Merge ')`.
     - The title contains `gates green`, compared case-insensitively. Evidence: 42 of the step titles holding "gate" in this repo's `.sdlc` plans read `Gates green` or `gates green`, and others embed it, such as "Records in sync and gates green".
     - The step is the highest-numbered live `step-<n>/` in the task dir. Planner rule 14 puts the gates on the final step, and in a one-step plan that step is the gates green step, so this catches gates steps with other titles, such as "Update the docs and run the gates".
     - A sibling `step-<n>.superseded-<k>/` exists. A replan reuses the same relative path `step-<n>/builder-L<k>.md`, and cross-dir order cannot be compared because `order.py` ranks lines inside one `runs.jsonl` (design.md:202). An old listing would otherwise match a new build.
   - `want = f'step-<n>/{basename(b)}'`. "Unchanged" means the listed path equals the step's current newest builder by `order.py`. File times are never read.
   - Walk `reversed(order.ordered(task_dir, 'verifier'))`. For each result, read `section(w, 'Verified')` and extract paths with `re.findall(r'(?<![\w./-])step-\d+/builder-L\d+(?:-\d+)?\.md(?![\w.-])', line)`. A list item may hold the path bare or inside a code span.
   - Skip results that do not list `want`. The newest result that lists it decides: return its path when `results.structure_error(w, 'verifier') is None and verdict_or_none(w) == 'pass'`, else `None`.
   - Why newest-listing rather than just the newest task verifier: two batches over disjoint steps both stay valid, and a later fail on the same build overrides an earlier pass.
2. In `next_action`, find the branch where no step verifier counts after the build (`if v is None or not order.counts_after(v, b):`, currently around line 1107). Before it returns `verify`, call `batch_verified(d)`. When that returns a path, return `('done', None, f'batch verifier {<task-dir-relative name>} lists {want} with Verdict pass', read + [path])`.
   - A step-dir verifier that counts after the build still decides first, so pass, fail, plan defect, swap, no-verdict and inherited routing are unchanged. This preserves the swap rules and the missing-verdict versus plan-defect distinction.
   - `resume` inherits the rule through `next_action` with no code change.
3. Update the module docstring:
   - In the `next` rules, add a line after `no verifier result counts after the build -> verify`. It states the batch rule, names the `## Verified` section literally, and lists every exclusion above.
   - In `resume`, add one sentence saying a batch-verified step counts as done.
4. Add selftest cases in `selftest()`, each named with the prefix `next batch: ` and printed through `check()`:
   - Positive: `next` prints `done`, and `resume` prints `done`.
   - A newer builder. Use a step `runs.jsonl` whose line order contradicts the `-2` name order (records `builder-L2-2.md` then `builder-L2.md`), so newest follows `order.py` and not the name fallback. Listing `builder-L2-2.md` gives `verify`. Listing `builder-L2.md` gives `done`.
   - An unlisted step.
   - L4 and L5 builds.
   - A `Merge ` title.
   - A `gates green` title.
   - The last step.
   - A superseded sibling.
   - A listing with Verdict fail.
   - A newer fail listing over an older pass listing.
   - A structurally invalid task verifier.
   - A per-step fail counting after the build that wins over a pass listing (`rebuild`).
5. In `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, add a section `## Batched verifier result (task dir)` before `## Free-text arguments`. It covers:
   - A verifier launched at the task dir writes `verifier-L<k>.md` in the task dir.
   - It adds a `## Verified` section after `## For the next attempt`, with one item `- step-<n>/builder-L<k>[-j].md` (relative to the task dir) per builder result it verified.
   - `steps.py next`/`resume` treat a listed, unchanged step as verified, and `board.py` renders it.
   - The exclusions above, and the newest-listing rule.
   - Undeclared headings are fine because `results.structure_error` ignores them (docs/maintenance/sdlc-internals.md:15).
6. In `docs/maintenance/sdlc-internals.md`, in the `scripts/steps.py` entry's `next` description, add the same rule in one clause naming `## Verified`.

Left untouched on purpose:
- `agents/verifier.md`, `agents/conductor.md` and `skills/chain`: teaching the conductor to batch and the verifier to emit the listing belongs to design row L7 (T-0192 conductor-rules, design.md:236).
- `results.py`: no schema change is needed.
- `order.py` and `run.sh`: row V already landed in T-0195.

No agent preloads handoff-format (`grep -rn handoff-format plugins/sdlc-lite/agents` finds nothing), so no Codex regeneration is needed.

Focused checks: `python3 plugins/sdlc-lite/scripts/steps.py selftest`, `python3 plugins/sdlc-lite/scripts/order.py selftest`, `python3 plugins/sdlc-lite/scripts/results.py selftest` (results.py runs `steps.py next`).

If the rule grows past one function plus one call site, stop with builder Status blocked and say so. The design's row S risk then defers batching.
### Acceptance criteria
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 b && mk step-3 2 c && printf "\074!-- role=verifier level=L1 model=sonnet effort=medium -->\n## Verdict\npass\n" > $t/step-3/verifier-L1.md && vf step-1/builder-L2.md step-2/builder-L2.md && test "$(python3 $S resume $t | head -1)" = done`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 b && mk step-2 2 b -2 && mk step-3 2 c && vf step-1/builder-L2.md step-2/builder-L2.md && test "$(python3 $S resume $t | head -2 | tr "\n" " ")" = "$t/step-2 verify L1 "`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 b && mk step-3 2 c && vf step-1/builder-L2.md && test "$(python3 $S resume $t | head -2 | tr "\n" " ")" = "$t/step-2 verify L1 "`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 4 b && mk step-3 2 c && vf step-1/builder-L2.md step-2/builder-L4.md && test "$(python3 $S resume $t | head -2 | tr "\n" " ")" = "$t/step-2 verify L3 "`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 "Merge lane-a" && mk step-3 2 c && vf step-1/builder-L2.md step-2/builder-L2.md && test "$(python3 $S resume $t | head -2 | tr "\n" " ")" = "$t/step-2 verify L1 "`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 "Docs and gates green" && mk step-3 2 c && vf step-1/builder-L2.md step-2/builder-L2.md && test "$(python3 $S resume $t | head -2 | tr "\n" " ")" = "$t/step-2 verify L1 "`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 b && vf step-1/builder-L2.md step-2/builder-L2.md && test "$(python3 $S resume $t | head -2 | tr "\n" " ")" = "$t/step-2 verify L1 "`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/steps.py && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 b && mk step-3 2 c && mkdir $t/step-2.superseded-1 && vf step-1/builder-L2.md step-2/builder-L2.md && test "$(python3 $S resume $t | head -2 | tr "\n" " ")" = "$t/step-2 verify L1 "`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: next batch:"`
- `for f in plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/skills/handoff-format/SKILL.md docs/maintenance/sdlc-internals.md; do grep -qF "## Verified" "$f" || exit 1; done`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e docs/maintenance/sdlc-internals.md | grep -q .`
