<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k cost`: pass. Evidence: I ran it and got exit 0 with 14 `ok: cost: ...` lines and `traces selftest: PASS`. It bites: in a scratch copy under `$SDLC_TMP_WORKTREES`, four separate mutations each turned it to `FAIL`. They inverted the ratio comparison, changed the background regex, forced `load` to `'unknown'`, and removed the no-baseline note. The unmutated copy went back to PASS.
- for-loop over the five detectors, each needing `ok: cost: $d fires` and `ok: cost: $d quiet on control`: pass. Evidence: I ran it and got exit 0. The output lists all 10 lines (cost-over-baseline, many-builder-attempts, polling-loop, background-denial and rate-limit, each with fires and quiet on control). Mutations 1 to 3 above hit the cost-over-baseline, background-denial and polling-loop cases.
- `... selftest -k cost | grep -qF 'no baseline'`: pass. Evidence: exit 0. The case line reads `a None baseline gives the note "cost-over-baseline: no baseline" and no finding`. Mutation 4, which drops the note, turned the selftest to FAIL.
- `test -f plugins/sdlc-lite/scripts/traces/detectors/cost.py`: pass. Evidence: exit 0. I read the file; it defines `detect(rows, aux, thresholds)` returning `(findings, notes)`.
- (guard) scope: pass. Evidence: I ran the command and got exit 0. `git ls-files --others` lists only `plugins/sdlc-lite/scripts/traces.py` and `plugins/sdlc-lite/scripts/traces/**`. The only tracked change outside `.sdlc` is `.gitignore`, which gains `__pycache__/`, and the pattern allows it. The guard does not scan `.sdlc/`, so `.sdlc/0157-review-sdlc-traces/handoff.md` (a 3-line tracked edit) is not covered.
- Spec behaviors I read in the selftest fixtures (lines 1673 to 1817) and saw pass:
  - A step costing 6.0 against a 2.0 baseline gives ratio 3.0, with attempt ids `['cb','cv']`.
  - Six identical `sleep 30` calls give `calls` 6 and `load` `'unknown'`.
  - With a load series passed through `ingest.run(load_series=...)`, `load` is 4.2 (the nearest value, with a malformed entry dropped).
  - A None baseline gives the note and no finding.
  - Three builder rows fire many-builder-attempts.
  - The control cases stay quiet.
- Builder claims: the full `traces.py selftest` exits 0 with PASS (I ran it), and `git diff --check` exits 0.

## Out of scope changes
None. Every changed file is covered by the handoff's allowed paths or `.gitignore`, which the guard allows. The `.sdlc/` artifacts and the tracked `.sdlc/0157-review-sdlc-traces/handoff.md` edit are run records, which the guard excludes. The step's scope did not call for that edit, but it is a task record and does not affect the work.

## For the next attempt
None. The builder's note is that `ingest.run(load_series=PATH)` exists but no `--load-series` CLI flag does yet, so step 16 must add it. `cost.detect` returns a `(findings, notes)` tuple, unlike the other families, so step 16's `detect` subcommand needs to unpack it.
