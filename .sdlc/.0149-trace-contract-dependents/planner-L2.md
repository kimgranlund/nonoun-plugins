<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
When a step changes a shared contract (a catalog entry, a type, an exported API, a schema key, an output format), the planner finds the contract's dependents (tests, fixtures, lint fixtures, snapshots) and puts them in the same step's Do and scope criterion. The verifier also traces dependents in the diff and reports any broken dependent the plan left out of scope as a `plan defect:`, so the replan widens that step before a later step runs into it.

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

## Step 2: Gates green
level: L1
### Do
Run every gate below from the repository root and fix any red that step 1 introduced. Keep all edits inside the files step 1 changed. If a generated TOML is stale, rerun `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` rather than editing the TOML. A gate that is already red at the build-start HEAD is reported as Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins`

## Risks
- The ticket's Intent section is empty, so the planner vs. verifier split is my own reading of the Goal's "planner or verifier". Both roles get the rule, and the verifier sends out-of-scope dependents back through the existing `plan defect:` replan route instead of adding a new route.
- I did not read the source run's evidence (gen-ui-system-svelte-lite lane logs), so the list of contract kinds may miss the exact shape that broke there.
- The TOML criteria assume `codex_roles.py generate` puts the full planner and verifier bodies into `sdlc-planner-l2.toml` and `sdlc-verifier-l1.toml`. That matches how T-0148 regenerated the planner TOMLs, but I did not confirm it for verifier TOMLs.
- The step 2 gates were green at plan time, with no side effects. I could not see them go red read-only, so step 1's temp-copy check.py criterion is the observed negative control.
- AGENTS.md asks for a focused live run of changed role behavior on a throwaway project. This plan proves wording and gates only, so the live run is left for the conductor or a follow-up.
