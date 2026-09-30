## Task goal
When a step edits a shared contract (a catalog entry, a type, an exported API), the planner or verifier finds its dependents (tests, fixtures, lint fixtures) and puts them in scope before a later step trips on them.

## Step 1: Planner and verifier trace contract dependents, pinned by check.py
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
1. In `plugins/sdlc-lite/agents/planner.md`, add a new section `## Contract dependents` between `## Criteria that can pass` and `## Entry files`. Its body must use the lowercase phrase `contract dependents` at least once. It says:
   - A shared contract is anything other files consume by name or shape: a catalog or registry entry, a type or interface, an exported function or symbol, a schema key, a CLI flag, or an output format.
   - When a step changes one, search the repo for its dependents before writing the step. Use `git grep` on the symbol, key, or path. Cover tests, fixtures, lint fixtures, snapshots, and generated files that pin it.
   - Each dependent the change can break goes into that same step: name it in the Do, add it to the step's scope criterion, and add a file-scoped or test-scoped criterion that runs it.
   - A dependent this step leaves untouched on purpose is named in the Do with the reason.
   - Why this exists: a later step, or the final gates step, otherwise trips on the stale dependent. This happened in the gen-ui-system-svelte-lite overnight run, 2026-09-28.
2. In `plugins/sdlc-lite/agents/verifier.md`, extend numbered item 2 (the diff inspection). When the diff changes a shared contract, trace its contract dependents with `git grep` and run the ones the change can break, file-scoped or test-scoped.
   - A broken dependent the step's scope allowed is an ordinary `fail`.
   - A broken dependent outside the step's scope is a `fail` whose `## For the next attempt` starts with `plan defect:` and names the dependent paths, so the replan widens that step.
   - Keep the existing `plan defect:` and swap wording intact.
3. In `plugins/sdlc-lite/scripts/check.py`, add this entry to `PLAN_DEFECT_DOCS`: `'contract dependents': ('agents/planner.md', 'agents/verifier.md'),`. Place it next to `'owns that budget'`.
4. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate the Codex agent TOMLs under `plugins/sdlc-lite/adapters/codex/agents/`. Do not edit the TOMLs by hand.
5. The check.py pin is a new gate, so it needs a negative control: the check.py criterion below proves it on a temp copy. This step proves the wording and the gate only. Live role behavior on a throwaway project is not proven here.
### Acceptance criteria
- `grep -qF '## Contract dependents' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'contract dependents' plugins/sdlc-lite/agents/planner.md`
- `awk '/^## Contract dependents/{f=1;next} /^## /{f=0} f' plugins/sdlc-lite/agents/planner.md | grep -qF 'lint fixture'`
- `awk '/^## Contract dependents/{f=1;next} /^## /{f=0} f' plugins/sdlc-lite/agents/planner.md | grep -qF 'scope criterion'`
- `grep -qF 'contract dependents' plugins/sdlc-lite/agents/verifier.md`
- `grep -qF "'contract dependents': ('agents/planner.md', 'agents/verifier.md'" plugins/sdlc-lite/scripts/check.py`
- `grep -qF 'Contract dependents' plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l2.toml`
- `grep -qF 'contract dependents' plugins/sdlc-lite/adapters/codex/agents/sdlc-verifier-l1.toml`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/" && sed -i.bak "s/contract dependents/contract users/g" "$d/sdlc-lite/agents/verifier.md" && out=$(python3 "$d/sdlc-lite/scripts/check.py" 2>&1); rm -rf "$d"; printf "%s\n" "$out" | grep -qF 'missing "contract dependents"'`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE '^plugins/sdlc-lite/(agents/(planner|verifier)\.md|scripts/check\.py|adapters/codex/agents/[^/]+\.toml)$'`
