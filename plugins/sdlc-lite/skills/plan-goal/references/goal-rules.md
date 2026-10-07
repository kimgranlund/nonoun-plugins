# Goal rules

Evidence labels: observed here (a file or transcript of this repo's work), from the host (Claude Code's own `/goal` output), or inferred.

| Rule | Why | Label |
|---|---|---|
| Done when is checkable: a command exit code, a file, a published tag, a closed ticket. Never "looks good" | The stop hook evaluates the condition on each turn; a vague condition cannot end the goal or keeps it open | from the host: `/goal` reports a session-scoped Stop hook with the condition; it defers evaluation while background work runs |
| Done when also covers stopping on a limit with state written | An overnight goal that hits a limit must end in a known state | observed: the 0.20.8 overnight goal (`docs/reports/release-0.20.8.md`) |
| Scope is a numbered list verified with `tickets.py check` first | Stale or duplicate tickets waste a night | observed: `tickets.py check` gates every release in `docs/reports/` |
| Lane first with `steps.py lane`; solo for ticket levels L1 and L2; replan cap one, then record a limit | The chain cost about ten times a solo run on the same tasks | observed: `docs/reports/solo-vs-lean-benchmark-2026-10-04.md` |
| Scope freeze, one writer per file, at most three lanes at once, merge one at a time with main merged in first | Merge conflicts in `check.py` guard numbers, `check.sh`, root `AGENTS.md`, `docs/README.md` cost the most time | observed: the 0.20.5 to 0.20.7 lane merges |
| Stop rules carry numbers: total cap, per-ticket cap, a rate or weekly limit, three 529s in a row; state goes to the notes file (`.sdlc/notes.md` (`.sdlc/notes/notes.md` with `layout: topics`)); no retry loops | Weekly limits stopped two build agents; a retry loop spends the cap silently | observed: this repo's build lanes; `budget.py` levels L1 $5, L2 $30, L3 $60 |
| A verifier `fail` means fix and re-verify; never merge on a fail | Verifiers caught real defects on most tickets | observed: the 0.20.x verifier records |
| Authorization is explicit; publish, push, tag, and external writes are never implied | Silent publish rights are the costly mistake | root `AGENTS.md` shared invariants |
| Every status claim comes from a command or a committed file | Release records overstated until checked | observed: the 0.20.7 fact-check passes |
| A goal pasted as plain text is not registered until it is run as `/goal` | A text paste starts no stop hook | observed in this repo's thread |

## Example block (it passes `plan_check.py goal`)

```
/goal Overnight: ship T-0001 and T-0002, then stop.

Scope (verify with tickets.py check first):
1. T-0001 add the report flag
2. T-0002 document it

How to work: lane first with steps.py lane; solo for ticket levels L1 and L2; one writer per file; replan cap one, then record a limit; every status claim from a command or a committed file.
A verifier fail means fix and re-verify; never merge on a fail.

Budget and stop rules: stop and write state to .sdlc/notes.md at $40 total, $15 per ticket, a rate or weekly limit, or three 529s in a row. No retry loops.

Authorization: publish, push, and tag are not implied. None of them is authorized.

Done when: tickets.py check exits 0 and T-0001 and T-0002 are closed on main, or the goal stopped on a limit with state written to .sdlc/notes.md.
```

The example names the flat notes path; in a `layout: topics` repo write `.sdlc/notes/notes.md` instead. `plan_check.py` accepts either.
