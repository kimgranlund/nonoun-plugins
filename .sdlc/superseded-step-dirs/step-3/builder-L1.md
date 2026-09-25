<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added the `step-2.superseded-1/` layout entry and the rule line on live step dirs versus superseded dirs.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: step 4.2 now has the conductor move each `step-<n>/` (n at or above the blocked step, holding builder or verifier output) to `step-<n>.superseded-<k>/` (first free k), then write fresh `step-<n>/handoff.md` files, before rewriting the remaining step handoffs.

## Checks
- `grep -n superseded` on both files shows the layout entry (handoff-format line 22), the rule line (line 29), and the step 4.2 instruction (chain line 30). Passed.
- `plugins/sdlc-lite/scripts/check.sh` passed end to end: 18 role levels and 8 agents checked, all four selftests, shellcheck, and plugin validate. I saw no CLAUDE.md validate warning in the tail I read.

## Notes
None
