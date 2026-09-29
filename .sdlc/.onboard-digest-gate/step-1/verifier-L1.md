<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qxF "gate digest: positive ok, negative ok"`: pass. Evidence: the selftest printed `gate digest: positive ok, negative ok`, and the grep exited 0. I also broke `digest()` in a temp copy by removing the CRLF normalization. The gate then printed `gate digest: FAIL positive failed: CRLF text hashed to '6612d9c94c2d', expected 'e9024f1a07d2'`, so the check can go red. I recomputed the literal independently: `printf 'line one\nline two\n' | shasum -a 256 | cut -c1-12` gave `e9024f1a07d2`, which matches the literal in the gate. The negative variants (`_digest_raw`, `_digest_prefix(16)`) sit in the gate's negative list and were accepted as rejected, since the negative check reported ok.
- (guard) `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: pass. Evidence: exit 0, and all 9 gates printed "positive ok, negative ok". I did not run the pre-build HEAD comparison because the guard is green.

## Out of scope changes
None. `git status` shows only `plugins/sdlc-lite/scripts/onboard.py` modified (+25 lines: `gate_digest`, the two variants, and the `GATES` entry) plus the untracked `.sdlc/onboard-digest-gate/` artifacts folder. I read the full diff and it touches nothing else.

## For the next attempt
None
