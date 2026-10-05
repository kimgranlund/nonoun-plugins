<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- docs/reports/role-result-schema-live-run.md: new. Live run evidence with Environment, Commands, Evidence and Limits sections.

## Checks
- Live runs in throwaway project `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/role-result-probe.jIfogzYTz9`, made with `mktemp -d` (one commit `a4b263f`). Each run went through a wrapper that unsets the `CLAUDE*` and `SDLC_*` env vars and then runs `bash <repo>/plugins/sdlc-lite/scripts/run.sh "$@"`:
  - Arm 1, first try, `run.sh builder L1 .sdlc/t/step-1/handoff.md`: exit 0. The model ignored the override and wrote `## Status done`. `steps.py next` printed `verify L1`.
  - Arm 1, stronger rerun, same step dir: exit 3. stderr was `run.sh: builder result lacks ## Status (done|blocked|inherited red: <tests>); see .../builder-L1-2.md`. `steps.py next .sdlc/t/step-1` printed `rebuild L1`.
  - Arm 2: headerless copy of `builder-L1-2.md` in `.sdlc/t2/step-1`, with its own handoff and runs.jsonl line. `steps.py next` printed `invalid result: .sdlc/t2/step-1/builder-L1.md: first line is not a <!-- role=... --> header`. `results.py validate --role builder` exited 1.
  - Arm 3, `run.sh builder L1 .sdlc/t3/step-1/handoff.md`: exit 0 with empty stderr. `steps.py next` printed `verify L1`, and `greet.sh` printed `hello world`.
- Criterion 1 (the loop over the required strings): rc 0.
- Criterion 2 (the `2026-..-..` date grep): rc 0.
- Guard (allowed file list): rc 0.
- `git diff --check` and a trailing-whitespace grep on the new doc: clean. The doc has no em dashes (count 0).

## Notes
- The first malformed try produced a valid result, so I reran once with a stronger instruction as the handoff allows. Both tries are in the doc. The rerun wrote `builder-L1-2.md` in the same step dir, and `steps.py next` read that newest result.
- All runs used the uncommitted T-0184 working tree on top of `f45649e`. The doc records SHA-256 hashes of `run.sh`, `results.py` and `steps.py`.
- My `rm -rf` of the throwaway project was denied by permissions. It is still at `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/role-result-probe.jIfogzYTz9` (outside the repo, with role logs) and can be deleted by hand.
- No Codex run was made. The doc's Limits section records the Codex arm as unverified.
