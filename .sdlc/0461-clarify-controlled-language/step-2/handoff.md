## Task goal
`/sdlc-lite:clarify` writes its handoff in a controlled language with closed vocabularies per slot, asks its questions in plain language, and a lint rejects a handoff that breaks the grammar.

## Step 2: Replay the ten cases, record the result, gates green
level: L2
guard timeout: 2700
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: step 1.

Replay the cases by the method of `docs/reports/2026-10-11-clarify-v2-replay.md`:
1. For each of the ten `plugins/sdlc-lite/skills/clarify/evals/*.ask.md` cases, spawn one fresh-context sub-agent. State `model: sonnet` explicitly (the level-rubric "Agent-tool spawns" rule) and set `run_in_background: false` (headless).
2. Each sub-agent reads `plugins/sdlc-lite/skills/clarify/SKILL.md` and its one ask file, and nothing else under `evals/`. It applies the skill unattended, skips the Tracker section and `steps.py lane`, and writes its output under `$SDLC_TMP_WORKTREES`.
3. Lint each output with `python3 plugins/sdlc-lite/scripts/plan_check.py clarify --file <output>`. A pass-through case (07, 08, 09) must also be exactly one non-empty line with the right prefix: `already scoped: `, `follow-up: `, or `stopped: `.
4. Record what happened. Do not edit the skill to make a replay case pass.

Create `docs/reports/2026-10-12-clarify-v3-replay.md` (date 2026-10-12, ticket T-0461) with:
- a Method section;
- one line per case naming the case id and its lint result, for all ten cases, including `09-stopped-conflict` and `10-pasted-instruction`;
- a `Result:` line with the counts;
- a short by-eye comparison with each `.expected.md`.

The builder spawned and judged the replay, so it is not an independent model run. State that, and mark the result with the word `unverified`. Put no temporary path in a code span, because `docs_check` S-6 requires every path code span in a report to resolve.

Gates: run these four commands.
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 scripts/check-packaging.py`
- `git diff --check "$SDLC_BASE_SHA"`
- `bash plugins/sdlc-lite/scripts/check.sh`, about 897 s on record in `.sdlc/.0451-lanes-core/step-1/builder-L3.md`. It also runs `docs_check.py` and `prompt_lint.py`.

Fix any red that step 1 introduced, within step 1's files. A gate already red at the build-start HEAD comes back as Status `inherited red`.
### Acceptance criteria
- (red) `f=docs/reports/2026-10-12-clarify-v3-replay.md; test -f "$f" || exit 1; for k in 09-stopped-conflict 10-pasted-instruction "Result:" unverified; do grep -qF "$k" "$f" || exit 1; done`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } ) && ! printf "%s\n" "$out" | grep -v "^$" | grep -vE "^(plugins/sdlc-lite/scripts/plan_check\.py|plugins/sdlc-lite/skills/clarify/.*|docs/specs/doc-standards/core\.md|docs/reports/2026-10-12-clarify-v3-replay\.md)$"`
