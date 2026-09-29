## Task goal
It is known whether SDLC Lite's Codex defaults work on a ChatGPT account, and a role launched at a default level either runs or fails with a message that names the cause.

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
