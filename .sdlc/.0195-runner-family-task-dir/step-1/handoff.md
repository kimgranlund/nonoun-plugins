## Task goal
Make the verifier model-family rule fire for a verifier launched at the task directory, on Claude and on Codex.

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
