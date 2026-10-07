## Task goal
Verify T-0309 (branch HEAD, one commit on top of main): the product is named `SDLC Lite` in prose, the folder docs/lean-sdlc/ moved to docs/specs/sdlc-lite/, and a check.py guard keeps retired spellings out of live files. Read-only: do not edit files. Read `.sdlc/0309-naming-sdlc-lite/handoff.md` for scope and `docs/reports/naming-sdlc-lite.md` for the builder's claims. Run each criterion from the repository root and report pass or fail with the output.

## Step 1: Verify the naming change
level: L3

### Do
Run the criteria below. Also inspect `git diff HEAD~1 --stat` and a sample of the prose diff for any rewrite that changed meaning or touched an identifier (`sdlc-lite`, `SDLC_*`, `.sdlc/`). Identifiers, model and effort values, `onboard.py` and `tickets.py` must be unchanged. The full `check.sh` is run separately from a /tmp copy; do not run it.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py`
- `test ! -e docs/lean-sdlc && test -f docs/specs/sdlc-lite/design.md && test -f docs/specs/sdlc-lite/README.md`
- `! git grep -q -I -E 'Lean SDLC|lean SDLC|SDLC-Lite|sdlc lite' -- . ':!docs/reports' ':!.sdlc/.[0-9]*' ':!.sdlc/verify-*' ':!.sdlc/*0309*' ':!plugins/sdlc-lite/bench/results' ':!plugins/sdlc-lite/scripts/check.py'`
- `python3 plugins/sdlc-lite/scripts/rename_refs.py check docs/lean-sdlc --allow 'docs/reports/*' --allow '.sdlc/.[0-9]*' --allow '.sdlc/verify-*' --allow '.sdlc/lean-sdlc-*' --allow '.sdlc/wave-b-verify/*' --allow '.sdlc/*0309*' --allow '.sdlc/AGENTS.md' --allow '.sdlc/roadmap.md' | grep -q 'check: 0 stale'`
- `python3 plugins/sdlc-lite/scripts/rename_refs.py links | head -1 | grep -q ' 12 broken'`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && python3 scripts/check-packaging.py && python3 plugins/sdlc-lite/scripts/tickets.py check && git diff --check HEAD~1`
- `git diff --quiet HEAD~1 -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json plugins/sdlc-lite/scripts/onboard.py plugins/sdlc-lite/scripts/tickets.py`
- `! git diff HEAD~1 -U0 -- plugins/sdlc-lite/adapters/codex/agents | grep -E '^[+-](model|model_reasoning_effort) '`
- Negative control: append the line `planted Lean SDLC` to docs/references/sdlc-internals.md, run `python3 plugins/sdlc-lite/scripts/check.py` and confirm it exits 1 naming that file, then `git checkout docs/references/sdlc-internals.md`.
- No new em dash: the count of changed lines with an em dash is equal before and after (8 and 8, all pre-existing text in generated Codex agent bodies): `git diff HEAD~1 -U0 | grep -E '^\+' | grep -v '^+++' | grep -c '—'` equals `git diff HEAD~1 -U0 | grep -E '^-' | grep -v '^---' | grep -c '—'`.
