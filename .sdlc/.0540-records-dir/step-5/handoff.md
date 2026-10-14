## Task goal
Records dir: part A of SDLC Lite 0.23.0 lean work records (wave 1).

## Step 5: Loose ends
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Two `fix-now:` follow-ups from `.sdlc/0540-records-dir/filer-L1.md`:
- `plugins/sdlc-lite/scripts/specgate.py` `red_target` (around :149, `d = task_dir / f'step-{step}'`): find the step dir through `steps.step_dirs(task_dir)` (records side preferred, task side kept) so `specgate.py red --step N` reads a records-side step dir and its `base-sha`. Keep the fallback to `task_dir` when no step dir exists.
- `plugins/sdlc-lite/scripts/steps.py` selftest: add a case labelled `(records dir) step_dirs lists a task-side step dir`, printed through the existing check so it reads `ok: (records dir) step_dirs lists a task-side step dir`. It builds a task whose records dir exists (runtime layout) and a hand-written `step-1/` beside the task handoff with no records twin, and asserts `step_dirs(task)` returns that task-side dir for 1. It must fail if `step_dirs` reads only the records side.
### Acceptance criteria
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/le.XXXXXX") && python3 -c "import os, sys, pathlib; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import specgate; d = sys.argv[1]; r = pathlib.Path(d + '/.sdlc/runtime/tasks/0001-a'); (r / 'step-1').mkdir(parents=True); os.makedirs(d + '/.sdlc/0001-a'); open(d + '/.sdlc/0001-a/handoff.md', 'w').write('## Goal\nMake a.\n'); (r / 'planner-L2.md').write_text('## Goal\nMake a.\n\n## Step 1: Make a\nlevel: L1\n### Do\nCreate a.txt.\n### Acceptance criteria\n- (red) \`test -f a.txt\`\n\n## Assumptions\n- none\n\n## Risks\nNone\n'); got = specgate.red_target(d + '/.sdlc/0001-a', 1)[2]; assert os.path.realpath(got) == os.path.realpath(r / 'step-1'), got" "$d"`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && printf '%s\n' "$out" | grep -qF "ok: (records dir) step_dirs lists a task-side step dir"`
- `python3 plugins/sdlc-lite/scripts/specgate.py selftest && python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/.*)$" | { ! grep -q .; }`
