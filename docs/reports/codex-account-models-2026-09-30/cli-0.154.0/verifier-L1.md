<!-- role=verifier level=L1 model=gpt-5.6-sol effort=medium -->
## Verdict
pass

## Criteria
- Fixture equals `value: 2\n`: pass. Evidence: acceptance command printed `fixture PASS` with exit 0. Piping `git show HEAD:value.txt` into the same predicate produced `AssertionError`, exit 1, proving the value comparison bites.
- Only `value.txt` differs outside ignored runner artifacts: pass. Evidence: `git diff --name-only` returned only `value.txt`; `git status --short --ignored` showed ` M value.txt` and ignored `.sdlc/`. An injected `other.txt` made the scope predicate exit 1.
- External model mapping, generated definitions, coverage, probes, and documentation are semantically correct: pass. Evidence: diff from `0ff454e` changes only `verifier_alternates` in `models.json`; the base mapping negative control exited 1 and the current mapping/count predicate exited 0. Catalog and live-probe predicates confirmed `gpt-5.6-sol`, supported verifier efforts, exit 0, and `MODEL_PROBE_OK`. All three alternate definitions use Sol, read-only sandbox, and medium/high/high effort; normalized hashes exactly match their base verifier contracts. `codex-selftest.py:256-299` retains empty-map fallback and real-runner alternate branches. Actual attempt records show Astra builder completion and Sol verifier selection. Current guidance at `docs/codex-role-execution.md:41-43` matches the mapping. Potential concern about “defaults configure none” at line 76 was dropped after checking lines 57-59: it belongs to the explicitly historical validation account permitted by the criterion.
- `scripts/run.sh` remains unchanged: pass. Evidence: `git diff --exit-code 0ff454e -- plugins/sdlc-lite/scripts/run.sh` produced no diff and exit 0.

## Out of scope changes
None.

## For the next attempt
None.
