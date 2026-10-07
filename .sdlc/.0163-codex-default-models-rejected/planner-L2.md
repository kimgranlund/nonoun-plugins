<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make every SDLC Lite Codex default level use a model a ChatGPT account accepts (`gpt-6-sol` becomes `gpt-6-astra`, with efforts unchanged). The verifier's alternate model comes from `models.json` configuration. When no alternate is configured, the verifier shares the builder's model and the runner records that.

## Step 1: Configurable verifier alternate, Astra defaults, regenerated agents, selftests
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Write the failing selftests first, in the same change as the fix.

1. `plugins/sdlc-lite/adapters/codex/models.json`
   - Replace every `gpt-6-sol` with `gpt-6-astra`. Keep each level's effort.
   - Leave `scout` L1 as `["gpt-6-luna", "high"]`. That is not part of the user decision.
   - Add a top-level key `"verifier_alternates": {}`. It maps a builder model to the model the verifier uses when its own configured model equals that builder model. It is empty by default because this account accepts no second model.
2. `plugins/sdlc-lite/scripts/codex_roles.py`
   - `models()` must return only role entries, so `definitions()`, `codex_exchange.py` (`models()[role][level]`) and `readiness.py` keep working.
   - Read the alternates map through its own accessor. The literal `gpt-6-*` model names leave this file entirely.
   - `definitions()` yields a `sdlc-verifier-lN-alternate` profile only when the alternates map has an entry for that level's model. The profile uses the mapped model.
   - `resolve(role, level, directory)` returns `(model, effort, shared)`. When the newest builder's `model=` equals the verifier's model:
     - If the map has an alternate for that model, switch to it (`shared=False`).
     - Otherwise keep the builder's model with `shared=True`.
   - The `resolve` CLI prints `model effort`, plus a third token `shared` when shared.
   - `generate` deletes `adapters/codex/agents/sdlc-*.toml` files that no definition produces. `generate --check` reports such orphans as drift. Without this, stale Sol alternate profiles would still be installed by `install`, which globs every `*.toml`.
3. `plugins/sdlc-lite/scripts/run.sh`, Codex resolve block (about line 183)
   - Read the optional third token: `read -r model effort shared`.
   - When it is `shared`, append ` shared_with_builder=yes` to the result header comment (the `<!-- role=... -->` line, about line 376). Do not put a `model=` substring in that token, because `codex_roles.resolve` greps `\bmodel=`.
   - Add a boolean `shared_with_builder` field to the `runs.jsonl` record (false on the Claude path and when not shared).
   - Claude model defaults and the Claude verifier switch stay unchanged.
4. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate `adapters/codex/agents/`. The three `-alternate` TOMLs go away.
5. `plugins/sdlc-lite/scripts/codex-selftest.py`
   - Replace `test_verifier_uses_different_model` with three tests:
     - `test_verifier_shares_builder_model_without_alternate`: a builder header with `model=gpt-6-astra` gives `('gpt-6-astra','medium',True)` for verifier L1.
     - `test_verifier_alternate_comes_from_config`: patch the alternates accessor or a models fixture to map `gpt-6-astra` to another model. Assert that resolve switches to it with `shared=False`, and that `definitions()` then yields the alternate profile.
     - `test_runner_records_shared_verifier_model`: run `run.sh verifier L1` through the stub CLI with a builder-L1 header of `gpt-6-astra`. Extend the stub with a mode whose text has a `## Verdict` section of `pass`. Assert the result header carries `shared_with_builder=yes` and the `runs.jsonl` record has `shared_with_builder` true.

Docs are step 2.
### Acceptance criteria
- `! grep -qF gpt-6-sol plugins/sdlc-lite/adapters/codex/models.json`
- `python3 -c "import json,sys; d=json.load(open('plugins/sdlc-lite/adapters/codex/models.json')); sys.exit(not isinstance(d.get('verifier_alternates'), dict))"`
- (guard) Every level keeps its effort: `python3 -c "import json,subprocess,os,sys; p='plugins/sdlc-lite/adapters/codex/models.json'; old=json.loads(subprocess.check_output(['git','show',os.environ['SDLC_BASE_SHA']+':'+p])); new=json.load(open(p)); sys.exit(any(new[r][l][1]!=e for r,lv in old.items() for l,(m,e) in lv.items()))"`
- (guard) `grep -qF '"scout": {"L1": ["gpt-6-luna", "high"]}' plugins/sdlc-lite/adapters/codex/models.json`
- `! grep -qF gpt-6- plugins/sdlc-lite/scripts/codex_roles.py`
- `d=$(mktemp -d) && printf '<!-- role=builder level=L1 model=gpt-6-astra effort=low -->\n' > "$d/builder-L1.md" && test "$(python3 plugins/sdlc-lite/scripts/codex_roles.py resolve verifier L1 "$d")" = "gpt-6-astra medium shared"`
- A configured alternate is used. Copy `plugins/sdlc-lite` to a temp dir and set `verifier_alternates` to `{"gpt-6-astra": "gpt-6-terra"}` in the copy's `adapters/codex/models.json`. Put a `builder-L1.md` whose header has `model=gpt-6-astra` in a temp step dir. Then the copy's `scripts/codex_roles.py resolve verifier L1 <dir>` prints exactly `gpt-6-terra medium`.
- `! grep -rlF gpt-6-sol plugins/sdlc-lite/adapters/codex/agents`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) No orphan agent files: `cd plugins/sdlc-lite/scripts && python3 -c "import sys, codex_roles; n={x for x,_ in codex_roles.definitions()}; f={p.stem for p in (codex_roles.ADAPTER/'agents').glob('*.toml')}; sys.exit(n!=f)"`
- `grep -qF shared_with_builder plugins/sdlc-lite/scripts/run.sh`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_verifier_shares_builder_model_without_alternate`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_verifier_alternate_comes_from_config`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_runner_records_shared_verifier_model`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_definitions_match_shared_contracts`

## Step 2: Document the shared-model verifier and run the gates
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
1. `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, line 9
   - Replace "switches matching builder/verifier models between Sol and Astra". The new text says the Codex verifier switches to the model `verifier_alternates` in `adapters/codex/models.json` maps the builder's model to.
   - It also says that with no alternate configured, the verifier keeps the builder's model and the runner records `shared_with_builder` in the result header and `runs.jsonl`.
   - Do not touch the Claude tables. `scripts/check.py` checks them against `run.sh`.
2. `docs/references/codex-role-execution.md`
   - Update the agent count on line 25. It is now 19 agents while no alternate is configured.
   - Update the default model mapping table: Sol becomes Astra, efforts unchanged, Scout stays Luna high.
   - Rewrite the verifier paragraph on line 41 as in item 1.
   - Add a dated note (2026-09-29, Codex CLI 0.154.0): a ChatGPT account rejected `gpt-6-sol` and `gpt-6-luna`, and `gpt-6-astra` was accepted. Say that Luna for scout is kept pending a user decision and that API-key accounts were not tested.
   - Leave the historical live-evidence paragraphs as they are.
3. `plugins/sdlc-lite/HARNESS-NOTES.md`
   - Line 19: fix the agent count and alternate-profile wording.
   - Line 27: replace "switch between Sol and Astra" with the same configured-alternate / shared rule.
4. Run every gate below and fix any red that step 1 introduced.
### Acceptance criteria
- `! grep -qF "between Sol and Astra" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qF verifier_alternates plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qF verifier_alternates docs/references/codex-role-execution.md`
- `! grep -qF "| Sol " docs/references/codex-role-execution.md`
- `grep -qF "ChatGPT account" docs/references/codex-role-execution.md`
- `! grep -qF "22 project agent definitions" docs/references/codex-role-execution.md`
- `! grep -qF "between Sol and Astra" plugins/sdlc-lite/HARNESS-NOTES.md`
- `! grep -qF "22 namespaced agents" plugins/sdlc-lite/HARNESS-NOTES.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check`

## Risks
- Nothing here proves that a live role run through `scripts/run.sh` with the Codex backend works on a ChatGPT account. The criteria use stub CLIs only. A focused live run in a throwaway project is still needed, per the root AGENTS.md.
- `gpt-6-luna` (scout L1) is still rejected on this account, so Codex scout runs keep failing until the user decides on it.
- Projects that already installed the old agents keep stale `sdlc-verifier-lN-alternate` TOMLs in `.codex/agents/`. `install` does not remove files it no longer generates. They are unused while no alternate is configured, because `codex_exchange` selects `-alternate` only when the model differs from the default.
- Adding `shared_with_builder` to the result header and `runs.jsonl` could affect parsers that expect an exact header shape. None were found beyond the `\bmodel=` grep in `codex_roles.resolve`, and the new token avoids that pattern.
