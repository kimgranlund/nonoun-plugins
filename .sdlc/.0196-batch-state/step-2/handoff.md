## Task goal
Teach steps.py and board.py the step state of a whole-ticket (task-dir) verifier result so batched verification is visible and a rebuild after the batch is detected.

## Step 2: Board renders batched verification, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1, which provides `steps.batch_verified(step_dir)`.

Implementation targets:
1. In `plugins/sdlc-lite/scripts/board.py`:
   - Add `import steps  # same scripts/ dir: the batch verification rule (steps.batch_verified)` beside the existing `import order`. steps.py imports only `order` and `results`, so there is no cycle.
   - In `step_row`, right before the final `return '🟡', f'built · builder {level_of(last_build)}, awaiting verify{tries}', LADDER['built']`, call `bv = steps.batch_verified(step)`. When it returns a path, return `('🟢', f'pass · builder {level_of(last_build)} · batch verifier {level_of(pathlib.Path(bv))}{tries}', LADDER['verified'])`.
   - Running, blocked, inherited and per-step verifier rows keep their precedence because they return earlier.
   - `--summary` counts the step as passed with no change, because `summary` counts `🟢`.
   - Add one docstring sentence after the inherited-red verifier lines: a step whose newest build a task-dir verifier lists under `## Verified` with Verdict pass (`steps.batch_verified`, the same rule `steps.py next` uses) renders as `🟢 pass · builder <level> · batch verifier <level>`.
   - In `selftest()`, add a positive case and a negative case (the listed step rebuilt renders `built ... awaiting verify`). On success each prints a line starting `ok: batch:`.
2. In `docs/references/sdlc-internals.md`, add one clause to the `scripts/board.py` entry naming the batched render.
3. Run every gate below. Fix any red that step 1 or this step introduced, within the scope criterion's files.

All gates were green at plan time, so a red gate is new. A gate already red at the build-start HEAD is reported as Status `inherited red`.
### Acceptance criteria
- `r=$(mktemp -d) && t=$r/x && export SDLC_BOARD_STATE_DIR=$r/state && mkdir $t && printf "## Goal\ng\n" > $t/handoff.md && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-2 2 b && vf step-1/builder-L2.md && python3 plugins/sdlc-lite/scripts/board.py --root $r --task x | grep -F "1. a" | grep -qF "🟢 pass · builder L2 · batch verifier L3"`
- (guard) `r=$(mktemp -d) && t=$r/x && export SDLC_BOARD_STATE_DIR=$r/state && mkdir $t && printf "## Goal\ng\n" > $t/handoff.md && mk(){ mkdir -p $t/$1 && printf "## Step 1: %s\nlevel: L2\n" "$3" > $t/$1/handoff.md && printf "\074!-- role=builder level=L%s model=opus effort=low -->\n## Status\ndone\n" "$2" > $t/$1/builder-L$2$4.md; } && vf(){ printf "\074!-- role=verifier level=L3 model=fable effort=xhigh -->\n## Verdict\npass\n\n## Verified\n" > $t/verifier-L3.md && for p in "$@"; do printf -- "- %s\n" "$p" >> $t/verifier-L3.md; done; } && mk step-1 2 a && mk step-1 2 a -2 && mk step-2 2 b && vf step-1/builder-L2.md && python3 plugins/sdlc-lite/scripts/board.py --root $r --task x | grep -F "1. a" | grep -qF "built · builder L2, awaiting verify"`
- `out=$(python3 plugins/sdlc-lite/scripts/board.py selftest) && printf "%s\n" "$out" | grep -qF "ok: batch:"`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/scripts/board.py | grep -q .`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
