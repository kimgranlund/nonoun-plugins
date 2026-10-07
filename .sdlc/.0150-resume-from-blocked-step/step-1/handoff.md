## Task goal
The bug is fixed and a test that failed before the fix passes after it.

## Step 1: Add `steps.py resume` with selftest cases and wire it into /chain
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Current behavior (confirmed at plan time): `steps.py next` takes a single step dir and never picks between steps. No script or skill text says which step a resumed /chain starts from. For a task where step-1 passed, step-2 has a blocked builder, and step-3 has a done builder, `next` prints `done`, `replan`, and `verify L1`. A conductor that picks "the newest step with work" therefore goes to step-3. gen-ui's local stepn.sh worked around this gap.

1. In `plugins/sdlc-lite/scripts/steps.py`, add a read-only `resume <task dir>` subcommand:
   - Candidates are the task dir's direct children whose name fully matches `step-\d+`. `step-<n>.superseded-<k>/` dirs are left out. Sort candidates by the integer n, not by string, so step-2 comes before step-10.
   - For each candidate in order, call the existing `next_action`. The first one whose action is not `done` wins. Print its path as `<task dir as given>/step-<n>` (via `pathlib.Path(task) / f'step-{n}'`) as line 1. Then print exactly what `cmd_next` prints for that dir: the action line (`<action>` or `<action> L<n>`), `reason: ...`, and the `read: ...` lines. Exit 0.
   - When every candidate is `done`, print `done` and then `reason: every step-<n>/ passed`, and exit 0.
   - A missing task dir, or a task dir with no `step-<n>/`, prints one line starting `steps resume: ` on stderr (for no steps, tell the user to run `steps.py split` first), prints nothing on stdout, and exits 1. A `Fail` from `next_action` on a candidate is re-raised as a `steps resume: ` line and exits 1.
   - It writes nothing and never reads file times.
2. In the same file, add a `resume` entry to the module docstring (`  resume    ...` at the same indent as `next`, and in the Usage line) and an argparse subparser.
3. Add selftest cases whose names start with `resume` (they print `ok: resume ...`) for these scenarios:
   - A blocked step-2 is chosen over a later step-3 that has a done builder.
   - Every step passed prints `done`.
   - A superseded dir is ignored, and step-2 is chosen before step-10.
   - No step dirs exits 1 with `steps resume:` on stderr.
   
   These cases are the failing test. They land with the fix, never after it.
4. In `plugins/sdlc-lite/skills/chain/SKILL.md`, add a short resume rule at the start of section 4:
   - A /chain run on a task that already has `step-<n>/` dirs first checks for stale attempts. It runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_lifecycle.py recover .sdlc/<task>/step-<n>` on a step dir whose attempt is stale when explicit recovery is required (always on Codex native transport; see handoff-format/run-operations.md), then inspects that step's artifacts and the working tree.
   - Then it runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py resume .sdlc/<task>` and continues from the step dir it prints, following its action line as in the rest of section 4. A `replan` there takes the 4.2 path. It never starts from the newest or highest step dir.
   - Add `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_lifecycle.py:*)` to the `allowed-tools:` frontmatter line.
5. In `docs/references/sdlc-internals.md`, in the `scripts/steps.py` entry, add a clause for `resume <task dir>` (read-only; the lowest-numbered non-superseded step whose `next` action is not `done`, its path and then its `next` output; `done` when all pass; exit 1 with `steps resume:` on stderr for a missing dir or no steps). Also extend the closing sentence to say that /chain runs `resume` when it resumes a task.
### Acceptance criteria
- `t=$(mktemp -d); for n in 1 2 3; do mkdir -p $t/step-$n; printf "## Task goal\ng\n\n## Step 1: x\nlevel: L2\n" > $t/step-$n/handoff.md; done; printf "## Status\ndone\n" > $t/step-1/builder-L2.md; printf "## Verdict\npass\n\n## For the next attempt\nNone\n" > $t/step-1/verifier-L1.md; printf "{\"file\": \"builder-L2.md\"}\n{\"file\": \"verifier-L1.md\"}\n" > $t/step-1/runs.jsonl; printf "## Status\nblocked\n\n## Notes\nx\n" > $t/step-2/builder-L2.md; printf "{\"file\": \"builder-L2.md\"}\n" > $t/step-2/runs.jsonl; printf "## Status\ndone\n" > $t/step-3/builder-L2.md; printf "{\"file\": \"builder-L2.md\"}\n" > $t/step-3/runs.jsonl; out=$(python3 plugins/sdlc-lite/scripts/steps.py resume $t) && test "$(printf "%s\n" "$out" | sed -n 1p)" = "$t/step-2" && test "$(printf "%s\n" "$out" | sed -n 2p)" = replan`
- `t=$(mktemp -d); for n in 1 2; do mkdir -p $t/step-$n; printf "## Task goal\ng\n\n## Step 1: x\nlevel: L2\n" > $t/step-$n/handoff.md; printf "## Status\ndone\n" > $t/step-$n/builder-L2.md; printf "## Verdict\npass\n\n## For the next attempt\nNone\n" > $t/step-$n/verifier-L1.md; printf "{\"file\": \"builder-L2.md\"}\n{\"file\": \"verifier-L1.md\"}\n" > $t/step-$n/runs.jsonl; done; out=$(python3 plugins/sdlc-lite/scripts/steps.py resume $t) && test "$(printf "%s\n" "$out" | sed -n 1p)" = done`
- `t=$(mktemp -d); for n in 1 2 10 2.superseded-1; do mkdir -p $t/step-$n; printf "## Task goal\ng\n\n## Step 1: x\nlevel: L2\n" > $t/step-$n/handoff.md; done; printf "## Status\ndone\n" > $t/step-1/builder-L2.md; printf "## Verdict\npass\n\n## For the next attempt\nNone\n" > $t/step-1/verifier-L1.md; printf "{\"file\": \"builder-L2.md\"}\n{\"file\": \"verifier-L1.md\"}\n" > $t/step-1/runs.jsonl; printf "## Status\nblocked\n\n## Notes\nx\n" > $t/step-2.superseded-1/builder-L2.md; out=$(python3 plugins/sdlc-lite/scripts/steps.py resume $t) && test "$(printf "%s\n" "$out" | sed -n 1p)" = "$t/step-2" && test "$(printf "%s\n" "$out" | sed -n 2p)" = "build L2"`
- `t=$(mktemp -d); python3 plugins/sdlc-lite/scripts/steps.py resume $t 2>$t/err; rc=$?; test $rc -eq 1 && grep -q "^steps resume: " $t/err`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -q '^ok: resume'`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest >/dev/null`
- `grep -qE '^  resume ' plugins/sdlc-lite/scripts/steps.py`
- `grep -qF 'steps.py resume' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'run_lifecycle.py recover' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qE '^allowed-tools:.*scripts/run_lifecycle.py' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'resume <task dir>' docs/references/sdlc-internals.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/skills/chain/SKILL.md -e docs/references/sdlc-internals.md`
