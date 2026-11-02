# Lessons

The human-readable companion to `run.json`: what the runs showed, in sentences a reviewer can check. Add a finding when a run confirms or refutes a claim someone will act on. Keep findings that did not hold, marked as such, so nobody re-tests them blind. When the target version a gate pins moves past a finding's runs, mark the finding `re-measure` until a run on the new version settles it. Field semantics: `references/model.md`.

| Claim | Runs | Numbers | Target version | Status |
|---|---|---|---|---|
| Replace with one claim, for example "The prompt links the refund policy on refund tickets." | Replace with the run ids, for example support-reply-20261101T090000Z. | Replace with counts and intervals, for example 10 of 10, 0.72 to 1.00. | Replace with the version the runs measured. | holds |

Status is one of:

- `holds`: the runs support the claim on the target version named.
- `did not hold`: the runs refute it; keep the row and say what was tried.
- `re-measure`: the target version moved since these runs; re-run before acting on the claim.
