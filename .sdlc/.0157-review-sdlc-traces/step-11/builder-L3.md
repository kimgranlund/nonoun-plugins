<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/findings.py` (new): has `make`, `finding_id`, `load`, `write` and `clusters`, as the handoff specifies.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added three `findings:` cases (rewrite keeps ids, stale marking, clusters).
- `plugins/sdlc-lite/scripts/traces/__init__.py`: added `findings` to the module list in the docstring.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings`: exit 0, 3 `ok: findings: ...` lines, PASS.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings | grep -q '^ok: findings: '`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/findings.py`: exit 0.
- (guard) scope command from the handoff: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (all families): exit 0, 29 ok, PASS.
- `git diff --check`: clean.
- Negative controls: I broke `findings.py` four ways, one at a time, ran `selftest -k findings` after each (exit 1 every time), then restored the original. The four breaks were:
  - `clusters` counts stale findings: the clusters case fails.
  - A known id loses its original `first_seen`: the stale case fails.
  - A finding missing from the second run is dropped: the stale case fails.
  - The id depends on evidence order: the rewrite case fails.

## Notes
- The id hashes the detector name plus every evidence entry, with each entry's keys sorted and the entries themselves sorted. So it ignores the summary, family, severity and the order of the evidence.
- Severity accepts either an int from 1 to 3 or `high`/`medium`/`low`, and is stored as the int.
- `make` raises `ValueError` for a bad severity or layer, an absolute `cause_file`, or an evidence entry that has neither `{path, line}` nor `{attempt_id}`.
- Every finding written in the current run gets `stale: False`. A finding missing from the run keeps its old `last_seen` and gets `stale: True`. If it shows up again later, it keeps its `first_seen` and becomes live again.
- A cluster is `{file, severity (highest), count, ids}`. Clusters sort by severity (highest first), then count (largest first), then file name, with `None` last.
- `findings.jsonl` rows are sorted by id.
