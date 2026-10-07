## Task goal
Make the verifier model-family rule fire for a verifier launched at the task directory, on Claude and on Codex.

## Step 2: Codex resolve reads live step dirs when the handoff dir has no build
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets:
- `codex_roles.resolve` in `plugins/sdlc-lite/scripts/codex_roles.py` (lines 100-120).
- A new test method `CodexTests.test_verifier_task_dir_reads_newest_live_step_builder` in `plugins/sdlc-lite/scripts/codex-selftest.py`, placed after `test_verifier_shares_builder_model_without_alternate` (line 256).
- `docs/references/codex-role-execution.md` line 46.

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

`docs/references/codex-role-execution.md` line 46: after the sentence beginning "When a pipeline verifier's model matches the latest builder's model", add a sentence saying this. "The latest builder result is the newest in the verifier's handoff dir; a verifier launched at the task dir, whose dir holds none, reads the newest builder result of the highest-numbered `step-<n>/` under it that holds one, leaving out `step-<n>.superseded-<k>/` dirs, the same rule run.sh applies on Claude Code."

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
- `grep -qF 'step-<n>.superseded-<k>' docs/references/codex-role-execution.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/references/codex-role-execution.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`
