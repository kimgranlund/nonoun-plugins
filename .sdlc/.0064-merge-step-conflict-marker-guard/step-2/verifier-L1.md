<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `plugins/sdlc-lite/scripts/check.sh` exits 0, and the real templates pass all three cases: pass. Evidence: `check.sh` ended with `ok: plugin validate` and `rc=0`, and its output had no FAIL lines (`grep -c FAIL` printed 0).
- Negative control, old whole-tree form flagged: pass. Evidence: with the templates from 192054c copied into a throwaway plugin copy, check.py printed `FAIL merge-step conflict-marker guard: empty merge flagged` and `FAIL merge-step conflict-marker guard: marker in touched file not flagged`. The criterion's grep exited 0.
- Negative control, inverted guard flagged: pass. Evidence: after the `perl` inversion, check.py printed `FAIL merge-step conflict-marker guard: marker in touched file not flagged` and `FAIL merge-step conflict-marker guard: clean merge flagged`. The criterion's grep exited 0.
- `grep -q "conflict-marker guard" CLAUDE.md`: pass. Evidence: exit 0. The Decisions bullet now reads "runs their conflict-marker guard against a throwaway repo".
- `sed -n 6,14p plugins/sdlc-lite/scripts/check.py | grep -q "conflict-marker guard"`: pass. Evidence: exit 0. Docstring item 6 in the diff carries the text.

## Out of scope changes
- `plugins/sdlc-lite/agents/planner.md` and `plugins/sdlc-lite/skills/handoff-format/SKILL.md` are modified. These are most likely step 1's template fix, and step 2 did not need them.
- `.sdlc/0064-merge-step-conflict-marker-guard/handoff.md` is modified, and the `.sdlc/` artifacts (planner output, `runs.jsonl`, `step-1/`, `step-2/`) are untracked. These are expected bookkeeping.

## For the next attempt
None
