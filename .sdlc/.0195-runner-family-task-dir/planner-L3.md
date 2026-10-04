<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Make the verifier model-family rule fire for a verifier launched at a task dir, on Claude (`run.sh`) and on Codex (`codex_roles.resolve`). When the handoff dir holds no builder result, the rule reads the newest builder result of the highest-numbered live `step-<n>/` under it. The change ships with negative controls, updated guidance, and a Claude live run.

## Step 1: Claude family rule reads live step dirs when the handoff dir has no build
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets:
- `plugins/sdlc-lite/scripts/run.sh`: the verifier family block (lines 196-208) and the header "Family rules" paragraph (lines 22-26).
- `plugins/sdlc-lite/scripts/run-selftest.sh`: a new task-dir block and a header paragraph.
- `docs/maintenance/sdlc-internals.md`: the `scripts/run.sh` entry (line 11).

Depends on: none.

The settled rule (step 2 mirrors it in Python):
1. Read the newest builder result in the handoff dir with `order.py newest "$dir" builder`, as today. When it prints a path, nothing changes.
2. When it prints nothing, look only at direct children of the handoff dir whose name is exactly `step-<n>` (`^step-[0-9]+$`).
   - This leaves out `step-<n>.superseded-<k>/`, the name /chain 4.2 gives a replaced step dir (`steps.py:16`, `steps.py:889`).
   - It follows the convention of `STEP_DIR_RE` fullmatch (`steps.py:1120`, `fanout.py:615`) and `live_step_dirs` (`board.py:79-81`).
3. Run `order.py newest "<step dir>" builder` for each such dir. Among the dirs that print a path, take the one with the largest integer n. That file is the build to compare. A live step dir with no builder result is skipped.
4. The existing compare stays as it is: the first `model=[a-z]*` token of that file. If it equals the verifier's model and that model is fable or sonnet, the verifier runs on opus at the same effort.

Why step number and not run time:
- `order.py` ranks results by line index inside one dir's `runs.jsonl` (`order.py:59-79`) and never reads file times (plugin AGENTS.md).
- Steps run in ascending number: `steps.py resume` takes the lowest-numbered step that is not done (`steps.py:1123-1145`). So the highest-numbered live step that holds a builder result holds the newest build.
- `scripts/order.py` is not edited, because the handoff's non-goals exclude files outside run.sh, codex_roles.py, and the two selftests.

run.sh constraints:
- New code stays inside the `{ ... }` group (self-edit guard, header lines 87-92).
- `/bin/bash` on this host is 3.2.57:
  - no associative arrays, no `mapfile`, no `${x,,}`;
  - an unmatched glob stays literal, so test `[[ -d ]]` and the name regex;
  - guard each command substitution with `|| true`, like line 199, so `set -euo pipefail` never aborts;
  - compare n with `10#$n`.
- Add one comment line naming `codex_roles.resolve` as the Codex twin of this rule.
- Header "Family rules" paragraph: add a sentence saying this. "A verifier whose handoff dir holds no builder result (a verifier launched at the task dir) reads instead the newest builder result, by scripts/order.py, of the highest-numbered step-<n>/ under it that holds one. step-<n>.superseded-<k>/ dirs are left out. scripts/codex_roles.py resolve applies the same rule on Codex." The sentence must hold the literal `step-<n>.superseded-<k>`.

run-selftest.sh, new block:
- Place it directly after the existing verifier model swap block (the block ending with the T-0108 skill-file check, near line 151) and before the plan-reviewer block. A reverted rule then fails fast here.
- Fixtures live under `$repo/.sdlc/td`, with the task handoff at `.sdlc/td/handoff.md`. Result files carry headers in the existing `<!-- role=builder level=Lx model=... effort=... -->` style.
- Every failure is `fail "task dir: <reason>"`, so its line reads `run selftest: FAIL: task dir: ...`.
- Cases are dry runs of `run.sh verifier <level> <handoff>`, asserting the printed `--model X --effort Y`. Case 1 comes first.
  1. Task dir with no builder result, `step-1/builder-L1.md` with model=sonnet:
     - verifier L1 prints `--model opus --effort medium`;
     - verifier L2 prints `--model opus --effort high`.
  2. Newest live build is model=fable (builder L5): verifier L3 prints `--model opus --effort xhigh`.
  3. Superseded dirs are ignored:
     - `step-1/` sonnet, `step-2/` with a handoff only, `step-2.superseded-1/` opus: verifier L1 prints `--model opus --effort medium`;
     - `step-1/` opus, `step-2.superseded-1/` sonnet: verifier L1 stays `--model sonnet --effort medium`.
  4. Step order is numeric, not lexical:
     - `step-2/` opus, `step-10/` sonnet: verifier L1 prints `--model opus`;
     - `step-2/` sonnet, `step-10/` opus: verifier L1 stays `--model sonnet`.
  5. One live step holds `builder-L5.md` (fable) and `builder-L1.md` (sonnet), and its `runs.jsonl` lists L5 then L1: verifier L1 prints `--model opus`. The step's newest result comes from order.py.
  6. Task dir holds its own `builder-L3.md` (opus) and `step-1/` holds sonnet: verifier L1 stays `--model sonnet --effort medium`. The handoff dir's builder wins.
  7. No builder result anywhere (only `step-1/handoff.md`):
     - verifier L1 stays `--model sonnet --effort medium`;
     - verifier L3 stays `--model fable --effort xhigh`.
  8. Verifier at `.sdlc/td/step-3/handoff.md` (a live step with no builder result) while `step-1/` holds a sonnet build: stays `--model sonnet --effort medium`. The fallback reads only under the handoff dir.
- Header: add a comment paragraph that starts `# Task dir: `, describes these cases and the `task dir: <reason>` failure form, and sits beside the existing per-case paragraphs.

sdlc-internals.md, `scripts/run.sh` entry: replace `the Fable-never-verifies-Fable swap` (the phrase is only there, and stale) with this text. "the verifier family rule (a verifier never runs on the build's model family: a Fable or Sonnet build moves it to Opus at the same effort; the build is the newest builder result in the handoff dir or, when it holds none (a verifier launched at the task dir), the newest builder result of the highest-numbered `step-<n>/` under it that holds one, leaving out `step-<n>.superseded-<k>/` dirs; `run-selftest.sh` case `task dir`)".

Left untouched on purpose:
- `skills/level-rubric/SKILL.md` line 40 is still true. It is preloaded into the conductor, planner, and plan-reviewer agents, so an edit would force a Codex agent regeneration.
- `agents/verifier.md`: the task-dir verifier contract belongs to T-0196 and T-0199.
- `scripts/order.py`: excluded by the handoff's non-goals.

Focused checks: `bash plugins/sdlc-lite/scripts/run-selftest.sh` (65 s at plan time) plus the criteria below. shellcheck is not installed here, so there is no shellcheck criterion.
### Acceptance criteria
- `r=$PWD; t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git -C "$t" init -q && git -C "$t" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -q --allow-empty -m init && mkdir -p "$t/.sdlc/td/step-1" "$t/.sdlc/td/step-2" "$t/.sdlc/td/step-2.superseded-1" && echo '## Goal' > "$t/.sdlc/td/handoff.md" && echo 'role=builder level=L1 model=sonnet effort=low' > "$t/.sdlc/td/step-1/builder-L1.md" && echo 'role=builder level=L3 model=opus effort=high' > "$t/.sdlc/td/step-2.superseded-1/builder-L3.md" && out=$(cd "$t" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/td/handoff.md 2>/dev/null) && printf '%s\n' "$out" | grep -qF -- '--agent sdlc-lite:verifier --model opus --effort medium'`
- `r=$PWD; t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git -C "$t" init -q && git -C "$t" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -q --allow-empty -m init && mkdir -p "$t/.sdlc/td/step-2" "$t/.sdlc/td/step-10" && echo '## Goal' > "$t/.sdlc/td/handoff.md" && echo 'role=builder level=L3 model=opus effort=high' > "$t/.sdlc/td/step-2/builder-L3.md" && echo 'role=builder level=L1 model=sonnet effort=low' > "$t/.sdlc/td/step-10/builder-L1.md" && out=$(cd "$t" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" verifier L2 .sdlc/td/handoff.md 2>/dev/null) && printf '%s\n' "$out" | grep -qF -- '--agent sdlc-lite:verifier --model opus --effort high'`
- (guard) `r=$PWD; t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git -C "$t" init -q && git -C "$t" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -q --allow-empty -m init && mkdir -p "$t/.sdlc/td/step-1" && echo '## Goal' > "$t/.sdlc/td/handoff.md" && echo 'role=builder level=L3 model=opus effort=high' > "$t/.sdlc/td/builder-L3.md" && echo 'role=builder level=L1 model=sonnet effort=low' > "$t/.sdlc/td/step-1/builder-L1.md" && out=$(cd "$t" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/td/handoff.md 2>/dev/null) && printf '%s\n' "$out" | grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium'`
- (guard) `r=$PWD; t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git -C "$t" init -q && git -C "$t" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -q --allow-empty -m init && mkdir -p "$t/.sdlc/td/step-1" "$t/.sdlc/td/step-2" && echo '## Goal' > "$t/.sdlc/td/handoff.md" && echo '## Step 2' > "$t/.sdlc/td/step-2/handoff.md" && echo 'role=builder level=L1 model=sonnet effort=low' > "$t/.sdlc/td/step-1/builder-L1.md" && out=$(cd "$t" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/td/step-2/handoff.md 2>/dev/null) && printf '%s\n' "$out" | grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium'`
- `t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C "$t" && cp plugins/sdlc-lite/scripts/run-selftest.sh "$t/plugins/sdlc-lite/scripts/run-selftest.sh" && ! bash "$t/plugins/sdlc-lite/scripts/run-selftest.sh" > "$t/out" 2>&1 && grep -q '^run selftest: FAIL: task dir: ' "$t/out"`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `sed -n '1,/^set -euo pipefail/p' plugins/sdlc-lite/scripts/run.sh | grep -qF 'step-<n>.superseded-<k>'`
- `sed -n '1,/^set -euo pipefail/p' plugins/sdlc-lite/scripts/run-selftest.sh | grep -q '^# Task dir: '`
- `awk '/^## .scripts\/run\.sh./{f=1;next} /^## /{f=0} f' docs/maintenance/sdlc-internals.md | grep -qF 'step-<n>.superseded-<k>'`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/maintenance/sdlc-internals.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

## Step 2: Codex resolve reads live step dirs when the handoff dir has no build
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets:
- `codex_roles.resolve` in `plugins/sdlc-lite/scripts/codex_roles.py` (lines 100-120).
- A new test method `CodexTests.test_verifier_task_dir_reads_newest_live_step_builder` in `plugins/sdlc-lite/scripts/codex-selftest.py`, placed after `test_verifier_shares_builder_model_without_alternate` (line 256).
- `docs/codex-role-execution.md` line 46.

Depends on: none. It runs after step 1, and its scope criterion includes step 1's files because builders never commit.

The settled rule:
- Applies only when `role == 'verifier'` and `order.newest(Path(directory), 'builder')` returns None.
- Then apply step 1's rules 2 and 3 in Python: direct child dirs whose names match `re.fullmatch(r'step-(\d+)', name)`, `order.newest(child, 'builder')` for each, and take the result with the largest `int(n)`.
- The existing `model=` regex and the alternate or shared logic then apply to the file found.
- The plan-reviewer path is unchanged. Planner results never live in step dirs, and T-0171 behavior must stay.
- The `resolve(role, level, directory=None)` signature and its `(model, effort, shared)` return are unchanged.
- Add one comment or docstring line naming run.sh's verifier family rule as the Claude twin.
- Host python3 is 3.9.6.

The test method:
- Each sub-case gets its own fresh dir under `self.repo`.
- Patch `codex_roles.verifier_alternates` with `unittest.mock.patch.object` to return `{'gpt-6-luna': 'fixture-alt', 'gpt-6-astra': 'fixture-alt'}`, unless a sub-case says otherwise.
- Write builder files like the existing tests do (`<!-- role=builder level=L1 model=gpt-6-luna effort=low -->` then `## Status` and `done`).
- Use `assertEqual` on the whole tuple, so a reverted rule fails with `AssertionError`. Sub-case 1 comes first.
  1. Task dir with no builder result, `step-1/builder-L1.md` on luna:
     - resolve verifier L1 equals `('fixture-alt', 'low', False)`;
     - with alternates patched to `{}`, it equals `('gpt-6-luna', 'low', True)`.
  2. Superseded dirs are ignored:
     - `step-1/` luna, `step-2/` with a handoff only, `step-2.superseded-1/` with model=other-model: `('fixture-alt', 'low', False)`;
     - `step-1/` other-model, `step-2.superseded-1/` luna: `('gpt-6-luna', 'low', False)`.
  3. Step order is numeric:
     - `step-2/` other-model, `step-10/` luna: the alternate;
     - `step-2/` luna, `step-10/` other-model: `('gpt-6-luna', 'low', False)`.
  4. Task dir holds its own `builder-L3.md` with other-model, and `step-1/` holds luna: `('gpt-6-luna', 'low', False)`.
  5. plan-reviewer L1 on a task dir with no planner result and `step-1/planner-L3.md` with model=gpt-6-astra: `('gpt-6-astra', 'high', False)`.

The defaults (verifier L1 is gpt-6-luna low, plan-reviewer L1 is gpt-6-astra high) come from `adapters/codex/models.json`, as the existing tests at lines 256-311 assume.

`docs/codex-role-execution.md` line 46: after the sentence beginning "When a pipeline verifier's model matches the latest builder's model", add a sentence saying this. "The latest builder result is the newest in the verifier's handoff dir; a verifier launched at the task dir, whose dir holds none, reads the newest builder result of the highest-numbered `step-<n>/` under it that holds one, leaving out `step-<n>.superseded-<k>/` dirs, the same rule run.sh applies on Claude Code."

No regeneration is needed: `definitions()` does not read `resolve`, so the generated TOML files do not change. `generate --check` runs in step 4.

Focused check: `python3 plugins/sdlc-lite/scripts/codex-selftest.py` (20 s at plan time).
### Acceptance criteria
- `PYTHONPATH=plugins/sdlc-lite/scripts python3 -c 'import pathlib, tempfile, codex_roles as c; m,e=c.models()["verifier"]["L1"]; alt=c.verifier_alternates()[m]; d=pathlib.Path(tempfile.mkdtemp()); (d/"step-1").mkdir(); (d/"step-1"/"builder-L1.md").write_text("role=builder level=L1 model="+m+" effort=low\n"); r=c.resolve("verifier","L1",d); c.verifier_alternates=lambda: {}; r2=c.resolve("verifier","L1",d); print(r, r2); raise SystemExit(0 if (r, r2)==((alt,e,False),(m,e,True)) else 1)'`
- `PYTHONPATH=plugins/sdlc-lite/scripts python3 -c 'import pathlib, tempfile, codex_roles as c; m,e=c.models()["verifier"]["L1"]; alt=c.verifier_alternates()[m]; b=pathlib.Path(tempfile.mkdtemp()); w=lambda p,t: (p.parent.mkdir(parents=True,exist_ok=True), p.write_text(t)); w(b/"a/step-1/builder-L1.md","role=builder model="+m+"\n"); w(b/"a/step-2/handoff.md","## Step 2\n"); w(b/"a/step-2.superseded-1/builder-L3.md","role=builder model=other-model\n"); w(b/"z/step-2/builder-L3.md","role=builder model=other-model\n"); w(b/"z/step-10/builder-L1.md","role=builder model="+m+"\n"); got=[c.resolve("verifier","L1",b/x) for x in ("a","z")]; print(got); raise SystemExit(0 if got==[(alt,e,False)]*2 else 1)'`
- (guard) `PYTHONPATH=plugins/sdlc-lite/scripts python3 -c 'import pathlib, tempfile, codex_roles as c; m,e=c.models()["verifier"]["L1"]; d=pathlib.Path(tempfile.mkdtemp()); (d/"step-1").mkdir(); (d/"builder-L3.md").write_text("role=builder model=other-model\n"); (d/"step-1"/"builder-L1.md").write_text("role=builder model="+m+"\n"); r=c.resolve("verifier","L1",d); print(r); raise SystemExit(0 if r==(m,e,False) else 1)'`
- `r=$PWD; t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; set -- $(PYTHONPATH=plugins/sdlc-lite/scripts python3 -c 'import codex_roles as c; m,e=c.models()["verifier"]["L1"]; print(m, c.verifier_alternates()[m], e)') && m=$1 alt=$2 e=$3 && git -C "$t" init -q && git -C "$t" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -q --allow-empty -m init && mkdir -p "$t/.sdlc/td/step-1" && echo '## Goal' > "$t/.sdlc/td/handoff.md" && echo "role=builder level=L1 model=$m effort=low" > "$t/.sdlc/td/step-1/builder-L1.md" && out=$(cd "$t" && SDLC_BACKEND=codex SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/td/handoff.md 2>/dev/null) && printf '%s\n' "$out" | grep -qF -- "--model $alt --effort $e"`
- `t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C "$t" && cp plugins/sdlc-lite/scripts/codex-selftest.py "$t/plugins/sdlc-lite/scripts/codex-selftest.py" && ! python3 "$t/plugins/sdlc-lite/scripts/codex-selftest.py" CodexTests.test_verifier_task_dir_reads_newest_live_step_builder > "$t/out" 2>&1 && grep -q '^AssertionError' "$t/out"`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_verifier_task_dir_reads_newest_live_step_builder`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `grep -qF 'step-<n>.superseded-<k>' docs/codex-role-execution.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/codex-role-execution.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

## Step 3: Live run of a task-dir verifier on Claude Code
level: L2
### Do
Targets:
- `docs/validation/runner-family-task-dir-live-run.md`, modeled on `docs/validation/plan-reviewer-live-run.md`.
- The evidence folder `docs/validation/runner-family-task-dir-live-run/`, holding `fam/` (a copy of the throwaway task dir), `dry-run-base.txt`, and `dry-run-fixed.txt`.
- One line in `docs/README.md`.

Depends on: steps 1 and 2.

This step runs this worktree's fixed `plugins/sdlc-lite/scripts/run.sh` on purpose, because that file is what is under test. Nothing edits run.sh during this step, and the conductor still launches this builder from the main checkout's run.sh.

1. Record these, for the report:
   - `claude --version` (2.1.286 at plan time);
   - `git rev-parse --short HEAD`;
   - `git hash-object plugins/sdlc-lite/scripts/run.sh`, which binds the evidence to the run.sh blob assessed;
   - `git status --porcelain -- plugins/`. Steps 1 and 2 are uncommitted because builders never commit, and the report says so.
2. Define a shell function `W` that runs `env` with these arguments, in order:
   - `-u CLAUDECODE`;
   - one `-u` for every set variable named `CLAUDE_CODE_*` or `SDLC_*`;
   - `SDLC_BACKEND=claude`;
   - then W's own arguments.

   Calls look like `W bash <run.sh> ...` and `W SDLC_DRY_RUN=1 bash <run.sh> ...`. A nested run then inherits no base sha, attempt id or name, lifecycle-child flag, or temp-worktree prefix (precedent: the Method section of `plan-reviewer-live-run.md`). `<repo>` below is this worktree's absolute path.
3. Build the throwaway project at `P=$(mktemp -d)/claude`, outside this repository:
   - `git init`;
   - `greet.sh` holding `#!/usr/bin/env bash` and `echo hello`;
   - `.gitignore` holding `.sdlc/` and `.worktrees/`;
   - one commit, `init`.

   Then write two handoffs by hand:
   - `.sdlc/fam/handoff.md`:
     - a Goal section: `greet.sh` prints `hello <name>` for its first argument and `hello world` with none;
     - a Context section: one step, built in `step-1/`; verify the whole task against the criteria below;
     - an Acceptance criteria section with the two checks `test "$(bash greet.sh Ada)" = "hello Ada"` and `test "$(bash greet.sh)" = "hello world"`.
   - `.sdlc/fam/step-1/handoff.md`, in the step template:
     - a `## Step 1: Name argument for greet.sh` line;
     - `level: L1`;
     - a Do subsection saying to use `name=${1:-world}` and print `hello $name`;
     - an Acceptance criteria subsection with the same two checks.

   No builder result is ever written in `.sdlc/fam/` itself.
4. From `$P`, run `W bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/fam/step-1/handoff.md`. This is a live Sonnet low run. It must exit 0, and its result's first line must be `<!-- role=builder level=L1 model=sonnet effort=low -->`. Any Status is acceptable for this evidence.
5. Negative control, with no model call:
   - Extract the base plugin with `git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C <tmp>`.
   - From `$P`, run `W SDLC_DRY_RUN=1 bash <tmp>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md` and redirect stdout to `dry-run-base.txt`.
   - Run the same command with `<repo>/plugins/sdlc-lite/scripts/run.sh`, stdout to `dry-run-fixed.txt`.
   - Write both files only by redirection, never by hand. Expected: the base file holds `--model sonnet --effort medium` and the fixed file holds `--model opus --effort medium`.
6. From `$P`, run `W bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md` (live).
   - Expect exit 0. Verdict pass or fail are both fine, because the evidence is the model.
   - The result's first line must be `<!-- role=verifier level=L1 model=opus effort=medium -->`.
   - Read the `"model"` field of the init event in `.sdlc/fam/verifier-L1.log` (expected `claude-opus-*`) and record it. Do the same for the builder log. Logs never enter this repo.
7. Copy the task dir with `rsync -a --exclude '*.log' --exclude '*.running' --exclude '.run.lock' "$P/.sdlc/fam/" docs/validation/runner-family-task-dir-live-run/fam/`. Then remove `$P` and the base extract.
8. Outcomes:
   - The live proof failed if item 4 or item 6 exits non-zero, or if item 6's header is not `model=opus effort=medium`. In that case:
     - still write the report, with `Result: fail`;
     - end with Status blocked, with the first Notes line `live proof failed: <what>`;
     - never rerun a live role, because a rerun is the user's call at the replan.
   - Otherwise the result is `Result: pass`.
9. Write the report `docs/validation/runner-family-task-dir-live-run.md`:
   - `# Runner family task dir live run`, a blank line, then `Recorded: <YYYY-MM-DD>`.
   - An intro paragraph: for T-0195, a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in `step-1/`.
   - `## Environment`: the versions, the commit, the run.sh blob hash, the uncommitted step 1 and 2 changes, macOS, the temp project path, and the log model ids.
   - `## Method`: the wrapper, the project setup, and the exact commands of items 4 to 6.
   - `## Results`: a table of arm, result, and evidence for:
     - the builder header;
     - the base dry run (Sonnet) and the fixed dry run (Opus);
     - the verifier header and its `runs.jsonl` line;
     - the log model ids.

     Below the table, exactly one line `Result: pass` or `Result: fail`.
   - `## Limits`:
     - one trial, on Claude only;
     - Codex is covered by `codex-selftest.py` and a dry run, not a live run;
     - the live run has one step, so the choice across steps by number is exercised only by the selftests.
   - No em dash (U+2014). If a quoted evidence line holds one, write it as `\u2014` and say so under Limits. Copied evidence files stay verbatim.
10. In `docs/README.md`, add this line directly after the `- [Messages wait live run](validation/messages-wait-live-run.md): ...` line (line 40). It is a shared file, so the check is membership only.
    `- [Runner family task dir live run](validation/runner-family-task-dir-live-run.md): dated live run for T-0195 showing that a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in step-1/, where the pre-fix run.sh kept Sonnet.`
### Acceptance criteria
- `test "$(head -n 1 docs/validation/runner-family-task-dir-live-run/fam/step-1/builder-L1.md)" = "<!-- role=builder level=L1 model=sonnet effort=low -->"`
- `tail -n 1 docs/validation/runner-family-task-dir-live-run/fam/step-1/runs.jsonl | jq -e '.role == "builder" and .level == "L1" and .model == "sonnet" and .file == "builder-L1.md"'`
- `test "$(head -n 1 docs/validation/runner-family-task-dir-live-run/fam/verifier-L1.md)" = "<!-- role=verifier level=L1 model=opus effort=medium -->"`
- `tail -n 1 docs/validation/runner-family-task-dir-live-run/fam/runs.jsonl | jq -e '.role == "verifier" and .level == "L1" and .model == "opus" and .effort == "medium" and .file == "verifier-L1.md" and .backend == "claude"'`
- `jq -e '.status == "completed" and .model == "opus"' docs/validation/runner-family-task-dir-live-run/fam/verifier-L1.attempt.json`
- `test -d docs/validation/runner-family-task-dir-live-run/fam && test -z "$(find docs/validation/runner-family-task-dir-live-run/fam -maxdepth 1 -name 'builder-*.md')"`
- `grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium' docs/validation/runner-family-task-dir-live-run/dry-run-base.txt && grep -qF -- '--agent sdlc-lite:verifier --model opus --effort medium' docs/validation/runner-family-task-dir-live-run/dry-run-fixed.txt`
- `f=docs/validation/runner-family-task-dir-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## Results" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done`
- `grep -qxF 'Result: pass' docs/validation/runner-family-task-dir-live-run.md`
- `grep -qF "$(git hash-object plugins/sdlc-lite/scripts/run.sh)" docs/validation/runner-family-task-dir-live-run.md`
- `f=docs/validation/runner-family-task-dir-live-run.md; test -f "$f" && ! grep -qF "$(printf '\342\200\224')" "$f"`
- `grep -qF 'validation/runner-family-task-dir-live-run.md' docs/README.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/codex-role-execution.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/validation/runner-family-task-dir-live-run(\.md|/)")"`

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2, and 3.

1. From the repository root, run every gate the handoff's Done-when names:
   - `bash plugins/sdlc-lite/scripts/check.sh` (259 s at plan time; it runs the codex, lifecycle, run, hook, and other selftests plus `check.py`);
   - `python3 scripts/check-packaging.py`;
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`;
   - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`;
   - `git diff --check "$SDLC_BASE_SHA"`, excluding `.sdlc`.
2. Fix any red that steps 1 to 3 introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as Status `inherited red`.
3. If a fix changes `plugins/sdlc-lite/scripts/run.sh`, the step 3 evidence belongs to the earlier blob. Say so under Limits in `docs/validation/runner-family-task-dir-live-run.md`, naming both `git hash-object` values. Never edit the evidence files.
4. Confirm that no em dash (U+2014) was added in any changed tracked file.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/codex-role-execution.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/validation/runner-family-task-dir-live-run(\.md|/)")"`

## Assumptions
- Pre-fix behavior, which every new-behavior criterion relies on, was confirmed by running probes on HEAD 99d29b8:
  - A task-dir fixture with only `step-1/builder-L1.md` (model=sonnet): the run.sh dry run printed `--agent sdlc-lite:verifier --model sonnet --effort medium`.
  - `codex_roles.resolve('verifier','L1',<task dir>)` returned `('gpt-6-luna','low',False)`.
  - The Codex run.sh dry run printed `--model gpt-6-luna --effort low`.
- Every step 1 and step 2 new-behavior criterion was red on HEAD, and every guard was green. Each guard's command shape was seen red on a fixture:
  - a task-dir sonnet builder, or a sonnet builder in the step dir;
  - an archive copy with run.sh's `fable|sonnet) model=opus` swap removed: `run selftest: FAIL: L1 newest`;
  - an archive copy with `model = alternate` removed: three codex-selftest FAILs;
  - for the gates: a drifted TOML, an emptied plugin.json, a duplicate ticket id, trailing whitespace, and an added em dash.
- The negative controls were red on HEAD:
  - the base archive plus the current `run-selftest.sh` passes;
  - the current codex-selftest has no such test: `AttributeError`.
- The draft plan's criteria pass `steps.py lint`. The only findings were `### Read first` paths, because the draft sat outside git; `plugins/sdlc-lite/AGENTS.md` exists.
- A live step dir is named exactly `step-<n>`, and a replaced one is renamed `step-<n>.superseded-<k>`: checked in `steps.py:16`, `steps.py:889`, `steps.py:1120`, `fanout.py:615`, `board.py:79-81`.
- The highest-numbered live step that holds a builder result holds the newest build: checked in `steps.py:1123-1145` (resume goes in ascending numeric order) and `order.py:59-79` (ranks are line indices inside one dir's runs.jsonl, with no cross-dir order).
- The fallback fires only when the handoff dir holds no builder result, and only for the verifier: from the handoff Do ("when the handoff dir holds no builder result") and Goal ("verifier model-family rule"); `PAIRED` at `codex_roles.py:36` covers the plan-reviewer too, so step 2 limits the fallback to the verifier.
- The Claude swap reads the first `model=[a-z]*` token anywhere in the file (`run.sh:201`), and Codex uses `\bmodel=([^\s>]+)` (`codex_roles.py:113`). So the fixture lines without a `<!-- -->` wrapper exercise both; the probe printed `--model sonnet` from a bare line.
- `scripts/order.py` is not edited: the handoff non-goal "anything outside the files below" and its owning-file list. Guidance edits (`docs/maintenance/sdlc-internals.md`, `docs/codex-role-execution.md`, the live-run report, and the `docs/README.md` index line) come from Done-when "affected guidance is updated" and the root AGENTS.md rule that dated validation evidence goes in its own reports.
- `skills/level-rubric/SKILL.md` stays unedited: its family sentence stays true, and the conductor, planner, and plan-reviewer agents preload it (`grep -ln level-rubric plugins/sdlc-lite/agents/*.md`).
- The only dependents of `resolve` and of the run.sh family rule are run.sh line 226, `codex-selftest.py` lines 256-311, and `run-selftest.sh` lines 133-151 (`git grep`). No existing selftest fixture puts `step-*` dirs under a verifier's handoff dir. lifecycle-selftest runs only scout.
- Host facts:
  - `/bin/bash` is 3.2.57 and python3 is 3.9.6;
  - shellcheck is not installed, so check.sh prints `skip: shellcheck not installed`;
  - jq is at `/usr/bin/jq`.
- Timings on HEAD, all exit 0: `run-selftest.sh` 65 s, `codex-selftest.py` 20 s, `check.sh` 259 s. `check-packaging.py`, `generate --check`, and `tickets.py --root .sdlc check` each took under 1 s.
- A builder can launch nested live run.sh roles through an env-scrubbing wrapper on this host: `docs/validation/plan-reviewer-live-run.md`, written from T-0171 step 5 on 2026-09-30.
- A `git archive` extract of `plugins/sdlc-lite` runs both selftests and run.sh correctly: probes S1.5, S1.6, S2.5, and S2.7 ran that way.
- run.sh writes the result header `<!-- role=... level=... model=... effort=... -->` (`run.sh:460`). runs.jsonl and the attempt record carry `model`, `backend`, and `status` (checked in the precedent evidence and in `planner-L3.attempt.json`).

## Risks
- The cross-step choice by step number misses a rebuild of a lower-numbered step made after a higher one was built. That cannot happen in today's sequential /chain, but it can once T-0196 batched verification lands. When batched steps have mixed families, one verifier cannot avoid all of them: the rule follows only the newest build, as the design says. T-0196 can revisit this.
- The rule exists twice, in bash (run.sh) and in Python (`resolve`), and the copies could drift. The mirrored selftest fixtures and the twin comments are the mitigation.
- `check.sh` took 259 s, close to the 300 s default guard timeout of `steps.py split --only`. A replan that re-splits step 4 on a loaded host may need `--guard-timeout`.
- Step 3 makes two live model calls. Failures from auth (the wrapper drops `CLAUDE_CODE_*`, as the precedent did), hooks, or the host block the step with no retry, which spends a replan.
- Verbatim evidence files copied in step 3 may hold model-written em dashes. Only the report and tracked diffs are checked for them.
