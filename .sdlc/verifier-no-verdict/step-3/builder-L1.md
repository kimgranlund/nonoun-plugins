<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/chain/SKILL.md: added `reverify` to the `steps.py next` action list, and added rule 5 (a no-verdict rule) to section 4.
- plugins/sdlc-lite/agents/conductor.md: added a clause to the escalation line for a verifier result with no verdict.
- CLAUDE.md: the `steps.py` bullet now lists `reverify` and says the `next` error clause covers a bad dir or builder result only. It also states that a no-verdict verifier is never counted as a fail and that two in a row stop.
- .claude/agents/sdlc-lite-author.md: added a "No-verdict route" invariant after the Plan-defect route line.

## Checks
- `grep 'reverify'` finds it in all four files: pass. I ran this as a combined grep rather than each criterion's own command line. I did not run the separate `grep -q 'no verdict'` on chain SKILL.md; the rule 5 text contains "no verdict".
- Em dash check on the added diff lines: 0 found.
- `plugins/sdlc-lite/scripts/check.sh` (the guard): ran, and the tail showed all selftests, shellcheck and plugin validate passing. I only read the last 8 lines, so I did not check the earlier output.

## Notes
- I wrote the "second consecutive no verdict → stop" rule only in the docs. Step 3 does not change `steps.py`, so I did not check whether `steps.py next` enforces it.
- A scripted no-op replace ran on the author file before the real edit and changed nothing.
