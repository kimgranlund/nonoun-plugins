<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Make the verifier model-family rule fire for a verifier launched at a task dir, on Claude (`run.sh`) and on Codex (`codex_roles.resolve`), with a negative control taken from the pre-fix commit, updated guidance, and a Claude live run report.

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

## Step 3: Pre-fix negative control and live run report
level: L2
### Do
This replans the first step 3 attempt (`.sdlc/0195-runner-family-task-dir/step-3.superseded-1/builder-L2.md`, Status blocked, `plan defect:`).
- That attempt ran the live builder and verifier. Its evidence is committed in `docs/validation/runner-family-task-dir-live-run/fam/` (commit e2978f5): builder `model=sonnet effort=low`, verifier `model=opus effort=medium`.
- Its negative control archived `$SDLC_BASE_SHA`, which was the step-2 checkpoint aa59ebc. That commit already holds the fix, so the committed `dry-run-base.txt` shows `--model opus` and does not discriminate.
- This attempt reruns only the two dry runs, with no model call, then writes the report and the index line. Never rerun a live role: the live proof passed, and a rerun is the user's call.

Targets:
- `docs/validation/runner-family-task-dir-live-run/dry-run-base.txt` and `docs/validation/runner-family-task-dir-live-run/dry-run-fixed.txt`: rewritten only by shell redirection, never by hand.
- `docs/validation/runner-family-task-dir-live-run.md` (new), modeled on `docs/validation/plan-reviewer-live-run.md`.
- One line in `docs/README.md`.
- `docs/validation/runner-family-task-dir-live-run/fam/` stays exactly as committed.

Depends on: steps 1 and 2, committed in d87cc4b and aa59ebc.

Settled decisions, with evidence:
- The pre-fix commit is the first line of `.sdlc/0195-runner-family-task-dir/step-1/base-sha`: 171e13b72a516ccad2472d866f072add289079cf (`T-0195 plan split`, the parent of the step-1 commit d87cc4b). run.sh wrote it as step 1's build-start base. `git diff 171e13b HEAD -- plugins/sdlc-lite/scripts/run.sh` is exactly the step 1 change. The pre-fix run.sh blob is dc34865ecd542cb3e55516cc4803a7071f3b7364.
- Never take the base from `$SDLC_BASE_SHA` in this step, because it names a commit that already holds the fix.
- The fixed run.sh is this worktree's `plugins/sdlc-lite/scripts/run.sh`, blob e5308edf87a23bd02eb179eab631250a1bf24819 at replan time. The live runs used that same blob (the first attempt's Checks). Nothing edits run.sh in this step.
- The dry runs use a rebuilt project, not the first attempt's temp project. That project's task dir now holds `verifier-L1.md`, so a dry run there names `verifier-L1-2.md`, which is not the state the live verifier started from.
- A planner probe ran items 3 to 5 in a temp dir:
  - the base run printed `--agent sdlc-lite:verifier --model sonnet --effort medium`;
  - the fixed run printed `--model opus --effort medium`;
  - neither wrote anything under the project's `.sdlc/fam/`, because run.sh exits for a dry run at line 316, before the base-sha write.

1. Record, for the report:
   - `claude --version`;
   - `git rev-parse --short HEAD`;
   - `git hash-object plugins/sdlc-lite/scripts/run.sh`;
   - `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha)` and `git rev-parse "$b:plugins/sdlc-lite/scripts/run.sh"`.
2. Define a shell function `W` as the first attempt did. It runs `env` with `-u CLAUDECODE`, one `-u` for every set variable named `CLAUDE_CODE_*` or `SDLC_*`, then `SDLC_BACKEND=claude`, then its own arguments. A nested dry run then inherits no attempt name, base sha, or role. `<repo>` below is this worktree's absolute path.
3. Rebuild the project at `P=$(mktemp -d)/claude`, outside this repository:
   - `git init`, a `.gitignore` holding `.sdlc/` and `.worktrees/`, and one commit `init`;
   - copy `docs/validation/runner-family-task-dir-live-run/fam/handoff.md` to `$P/.sdlc/fam/handoff.md`;
   - copy `fam/step-1/handoff.md`, `fam/step-1/builder-L1.md`, and `fam/step-1/runs.jsonl` from the same folder to `$P/.sdlc/fam/step-1/`;
   - copy nothing else. The task dir then holds no builder or verifier result, which is the state the live verifier started from.
4. Extract the pre-fix plugin: `X=$(mktemp -d)`, then `git archive "$b" plugins/sdlc-lite | tar -x -C "$X"`.
5. From `$P`, with no model call:
   - `W SDLC_DRY_RUN=1 bash "$X/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/fam/handoff.md > <repo>/docs/validation/runner-family-task-dir-live-run/dry-run-base.txt`
   - `W SDLC_DRY_RUN=1 bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md > <repo>/docs/validation/runner-family-task-dir-live-run/dry-run-fixed.txt`
   - Expected: the base file holds `--model sonnet --effort medium` and the fixed file holds `--model opus --effort medium`. If the base file does not hold Sonnet, write no report. End with Status blocked and the first Notes line `negative control failed: <what>`.
6. Remove `$P` and `$X`. Leave the first attempt's temp dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.PDQbvWuqBm` in place: it is outside this repository, and its removal was denied before.
   - If it still exists, read only the `"model"` field of the init event in its `claude/.sdlc/fam/verifier-L1.log` and `claude/.sdlc/fam/step-1/builder-L1.log`.
   - Otherwise cite the ids in the first attempt's Checks: `claude-sonnet-5-5` for the builder, `claude-opus-5-5` for the verifier.
7. Write the report `docs/validation/runner-family-task-dir-live-run.md`:
   - `# Runner family task dir live run`, a blank line, then `Recorded: <YYYY-MM-DD>` alone on its line.
   - An intro paragraph: for T-0195, a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in `step-1/`, where the pre-fix run.sh kept Sonnet.
   - `## Environment`:
     - Claude Code 2.1.286 at the live run, and the version from item 1;
     - the live runs at commit aa59ebc, with steps 1 and 2 committed in d87cc4b and aa59ebc (not uncommitted);
     - the run.sh blob from item 1, used by the live runs and the fixed dry run;
     - the pre-fix commit `$b` (at least its first 7 characters) and its run.sh blob, used by the base dry run;
     - the HEAD from item 1, where the dry runs were rerun;
     - macOS, Darwin 25.6.0, the temp project paths, and the log model ids from item 6.
   - `## Method`:
     - the wrapper `W`;
     - the live project and its two commands from the first attempt: `W bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/fam/step-1/handoff.md`, then `W bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md`;
     - the rebuilt dry-run project and the two commands of item 5;
     - one sentence saying that the first negative control used the step-2 checkpoint, which already held the fix, and that this one replaced it.
   - `## Results`: a table of arm, result, and evidence, with one row each for:
     - the builder header (`model=sonnet effort=low`);
     - the verifier header and its `runs.jsonl` line (`model=opus effort=medium`, backend claude);
     - the log model ids;
     - the base dry run (`--model sonnet`, pre-fix run.sh);
     - the fixed dry run (`--model opus`).

     Below the table, exactly one line `Result: pass`.
   - `## Limits`:
     - one trial, on Claude only;
     - Codex is covered by `codex-selftest.py` and a dry run, not a live run;
     - the live run has one step, so the choice across steps by number is exercised only by the selftests;
     - the dry runs ran in a rebuilt project at a later commit than the live runs, with the same run.sh blob as the live runs.
   - No em dash (U+2014). Copied evidence files stay verbatim.
8. In `docs/README.md`, add this line directly after the `- [Messages wait live run](validation/messages-wait-live-run.md): ...` line (line 40 at replan time). It is a shared file, so the check is membership only.
   `- [Runner family task dir live run](validation/runner-family-task-dir-live-run.md): dated live run for T-0195 showing that a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in step-1/, where the pre-fix run.sh kept Sonnet.`

Focused checks: the criteria below. This step changes no code, so no selftest runs here. Step 4 runs them all.
### Acceptance criteria
- `grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium' docs/validation/runner-family-task-dir-live-run/dry-run-base.txt`
- `f=docs/validation/runner-family-task-dir-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## Results" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done`
- `grep -qxF 'Result: pass' docs/validation/runner-family-task-dir-live-run.md`
- `grep -qF "$(git hash-object plugins/sdlc-lite/scripts/run.sh)" docs/validation/runner-family-task-dir-live-run.md`
- `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); f=docs/validation/runner-family-task-dir-live-run.md; test -n "$b" && grep -qF "${b:0:7}" "$f" && grep -qF "$(git rev-parse "$b:plugins/sdlc-lite/scripts/run.sh")" "$f"`
- `f=docs/validation/runner-family-task-dir-live-run.md; test -f "$f" && ! grep -qF "$(printf '\342\200\224')" "$f"`
- `grep -qF 'validation/runner-family-task-dir-live-run.md' docs/README.md`
- (guard) `grep -qF -- '--agent sdlc-lite:verifier --model opus --effort medium' docs/validation/runner-family-task-dir-live-run/dry-run-fixed.txt`
- (guard) `d=docs/validation/runner-family-task-dir-live-run; n() { sed -E 's/ --plugin-dir [^ ]+ / /; s/ --model [a-z]+ / /; s/ --append-system-prompt-file [^ ]+ / /' "$1"; }; test -s "$d/dry-run-base.txt" && test "$(n "$d/dry-run-base.txt")" = "$(n "$d/dry-run-fixed.txt")"`
- (guard) `r=$PWD; e=docs/validation/runner-family-task-dir-live-run/fam; b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git archive "$b" plugins/sdlc-lite | tar -x -C "$t" && git init -q "$t/p" && git -C "$t/p" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -q --allow-empty -m init && mkdir -p "$t/p/.sdlc/fam/step-1" && cp "$e/handoff.md" "$t/p/.sdlc/fam/" && cp "$e/step-1/handoff.md" "$e/step-1/builder-L1.md" "$e/step-1/runs.jsonl" "$t/p/.sdlc/fam/step-1/" && o1=$(cd "$t/p" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$t/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/fam/handoff.md 2>/dev/null) && o2=$(cd "$t/p" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/fam/handoff.md 2>/dev/null) && printf '%s\n' "$o1" | grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium' && printf '%s\n' "$o2" | grep -qF -- '--agent sdlc-lite:verifier --model opus --effort medium'`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- docs/validation/runner-family-task-dir-live-run/fam && test -z "$(git ls-files --others --exclude-standard -- docs/validation/runner-family-task-dir-live-run/fam)"`
- (guard) `d=docs/validation/runner-family-task-dir-live-run/fam; test "$(head -n 1 "$d/step-1/builder-L1.md")" = "<!-- role=builder level=L1 model=sonnet effort=low -->" && test "$(head -n 1 "$d/verifier-L1.md")" = "<!-- role=verifier level=L1 model=opus effort=medium -->" && tail -n 1 "$d/runs.jsonl" | jq -e '.role == "verifier" and .level == "L1" and .model == "opus" and .effort == "medium" and .backend == "claude"' >/dev/null && jq -e '.status == "completed" and .model == "opus"' "$d/verifier-L1.attempt.json" >/dev/null && test -z "$(find "$d" -maxdepth 1 -name 'builder-*.md')"`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/README.md -e docs/validation/runner-family-task-dir-live-run.md -e docs/validation/runner-family-task-dir-live-run/dry-run-base.txt -e docs/validation/runner-family-task-dir-live-run/dry-run-fixed.txt)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF docs/validation/runner-family-task-dir-live-run.md)"`

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2, and 3.

1. From the repository root, run every gate the handoff's Done-when names:
   - `bash plugins/sdlc-lite/scripts/check.sh` (253 s at replan time; it runs the codex, lifecycle, run, hook, and other selftests plus `check.py`);
   - `python3 scripts/check-packaging.py`;
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`;
   - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`;
   - the whole-task whitespace and em dash checks in the criteria below.
2. The whole-task checks diff against the task's build-start commit, which is the first line of `.sdlc/0195-runner-family-task-dir/step-1/base-sha` (171e13b at replan time). They do not diff against `$SDLC_BASE_SHA`.
   - Why: the conductor commits each verified step (d87cc4b, aa59ebc). This step's `$SDLC_BASE_SHA` therefore already holds steps 1 to 3, and a diff against it sees only this step's own fixes.
   - The checks name the task's own files and leave out `docs/validation/runner-family-task-dir-live-run/`. The dry-run files there end with the trailing space that run.sh's `printf '%q '` writes, so `git diff --check` flags them. Copied evidence stays verbatim.
3. Fix any red that steps 1 to 3 introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as Status `inherited red`.
4. If a fix changes `plugins/sdlc-lite/scripts/run.sh`, the step 3 evidence belongs to the earlier blob. Say so under Limits in `docs/validation/runner-family-task-dir-live-run.md`, naming both `git hash-object` values. Never edit the evidence files.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); test -n "$b" && git diff --check "$b" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/codex_roles.py plugins/sdlc-lite/scripts/codex-selftest.py docs/maintenance/sdlc-internals.md docs/codex-role-execution.md docs/README.md docs/validation/runner-family-task-dir-live-run.md`
- (guard) `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); test -n "$b" && ! git diff "$b" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/codex_roles.py plugins/sdlc-lite/scripts/codex-selftest.py docs/maintenance/sdlc-internals.md docs/codex-role-execution.md docs/README.md docs/validation/runner-family-task-dir-live-run.md | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/codex-role-execution.md -e docs/README.md -e docs/validation/runner-family-task-dir-live-run.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

## Assumptions
- Steps 1 and 2 passed and are committed: verified by `step-1/verifier-L2.md` and `step-2/verifier-L1.md` (both `pass`), by commits d87cc4b and aa59ebc (`git log --oneline -8`), and by their `git show --stat`. Their blocks are copied unchanged from `planner-L3.md`, so `steps.py split --only` rewrites only steps 3 and 4.
- The pre-fix commit is the first line of `.sdlc/0195-runner-family-task-dir/step-1/base-sha`, which is 171e13b72a516ccad2472d866f072add289079cf. Verified three ways:
  - `cat` of that file;
  - `git show --stat 171e13b`, which touches only `.sdlc/` files;
  - `git diff 171e13b HEAD -- plugins/sdlc-lite/scripts/run.sh`, which shows only the step 1 hunks.
  - Its run.sh blob is dc34865ecd542cb3e55516cc4803a7071f3b7364, and the current run.sh blob is e5308edf87a23bd02eb179eab631250a1bf24819 (`git rev-parse`, `git hash-object`).
- For the committed fam fixture, the pre-fix run.sh prints Sonnet and the current one prints Opus. Verified two ways on HEAD e2978f5:
  - the step 3 reproduction guard exits 0;
  - a full temp simulation of step 3 items 3 to 5 printed `--model sonnet --effort medium` for the base run and `--model opus --effort medium` for the fixed run, and the step 3 same-project guard held on both outputs.
- A dry run writes nothing in the project: run.sh exits at line 316 (`SDLC_DRY_RUN`), before the base-sha write at lines 318-334. In the simulation, `.sdlc/fam/` afterwards held only the copied files. run.sh finds its plugin from `$0` (`run.sh:186`), so the archived run.sh uses the archived plugin.
- The live evidence is committed and supports `Result: pass`: verified by `git show --stat e2978f5` and by the step 3 header guard exiting 0. The committed `dry-run-base.txt` holds `--model opus` (the defect). `dry-run-fixed.txt` already holds Opus, and both files name the same handoff path. So the first step 3 criterion is red now, and those two checks are guards.
- Probe results on HEAD e2978f5 with `SDLC_BASE_SHA=$(git rev-parse HEAD)`:
  - every step 3 new-behavior criterion is red for the right reason: the base file holds Opus, the report is missing (exit 2 or 1), and the README line is missing;
  - every step 3 and step 4 guard is green.
- Each guard's command shape was seen red:
  - the fixed file rewritten to Sonnet;
  - the base file pointed at another project path;
  - the reproduction guard with `b` set to HEAD, which is the defect itself;
  - `SDLC_BASE_SHA=HEAD~1` for the fam guard;
  - a fam copy with the verifier header on Sonnet;
  - `SDLC_BASE_SHA` set to the step-1 base, for both scope guards;
  - the dry-run file added to the whitespace pathspec, and a fixture repo with a trailing space;
  - a fixture repo with an added em dash;
  - in an archive copy: an emptied plugin.json, a drifted generated TOML, and a duplicate ticket id.
- Gate timings on HEAD: `check.sh` exits 0 in 253 s. `check-packaging.py`, `generate --check`, and `tickets.py --root .sdlc check` each exit 0 in under 1 s.
- The conductor commits each verified step, so a later step's `$SDLC_BASE_SHA` holds the earlier steps: verified by `step-2/base-sha` = d87cc4b (the step-1 commit) and `step-3.superseded-1/base-sha` = aa59ebc.
- `step-1/base-sha` stays 171e13b: run.sh writes base-sha only in the handoff dir of a builder or verifier it launches (`run.sh:318-334`), and step 1 is done.
- The dry-run files end with a trailing space (`printf '%q '`, `run.sh:316`): `git diff --check 171e13b -- . ":(exclude).sdlc"` flags both of them, and with the evidence folder left out it exits 0.
- No non-root AGENTS.md governs `docs/`: verified by `git ls-files '*AGENTS.md'`. So step 3 has no `### Read first`.
- The full plan passes `steps.py lint` (`steps lint: ok`), run on an archive copy of HEAD so the `### Read first` paths resolve.
- The first attempt's temp dir still holds `claude/.sdlc/fam/verifier-L1.log`: verified by `ls`.

## Risks
- `check.sh` took 253 s, close to the 300 s default guard timeout of `steps.py split --only`. Re-splitting step 4 on a loaded host may need `--guard-timeout`.
- The step 3 reproduction guard and step 4's whole-task guards read `.sdlc/0195-runner-family-task-dir/step-1/base-sha`. If a sync from main merges into this lane before step 4, the whole-task diffs also include main's changes to the named files (`docs/README.md` is shared). A whitespace error or em dash there would turn step 4 red even though this task did not cause it.
- The live runs (HEAD aa59ebc) and the dry runs (a later HEAD) ran at different commits, so the evidence spans two attempts. The run.sh blob is the same, and the report records both commits.
- Carried from the first plan:
  - the choice across steps by step number misses a rebuild of a lower-numbered step made after a higher one was built, which becomes possible once T-0196 batches verification;
  - the rule exists in bash and in Python, and the two copies could drift.
- The copied evidence files may contain em dashes written by a model. Only the report and the task's named files are checked for them.
