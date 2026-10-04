<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/scout.md: added the `## Carry forward` template section at the end
- plugins/sdlc-lite/agents/researcher.md: added the `## Carry forward` template section at the end
- plugins/sdlc-lite/agents/architect.md: added the `## Carry forward` template section at the end
- plugins/sdlc-lite/agents/archaeologist.md: added the `## Carry forward` template section at the end
- plugins/sdlc-lite/agents/planner.md: added the reader paragraph after "Read the code you plan against. Do not edit anything."
- plugins/sdlc-lite/agents/builder.md: added the reader sentence to the end of the first paragraph
- plugins/sdlc-lite/scripts/results.py: added `'Carry forward'` as the last SCHEMA section for researcher, scout, archaeologist, and architect; updated the selftest bodies and the scout schema-line expectation; added the 2 labelled cases
- plugins/sdlc-lite/scripts/check.py: added docstring item 15 and the `CARRY_FORWARD` guard (comment labelled `(docstring item 15)`), each with a negative control
- plugins/sdlc-lite/adapters/codex/agents/sdlc-{scout-l1,researcher-l1..l3,architect-l1,archaeologist-l1,planner-l1..l3,builder-l1..l5}.toml: regenerated with `codex_roles.py generate`

## Checks
- AC1 (the 4 producers end with `## Carry forward` and contain "at most 15 lines"): PASS
- AC2 (planner and builder reader text present, no heading line): PASS
- AC3 (`results.py schema --role` ends with `|Carry forward` for all 4 roles): PASS
- AC4 (`results.py selftest` prints both new ok lines): PASS. The full selftest printed `results selftest: PASS`.
- AC5 (an out-of-order fixture fails validate with "## Carry forward comes before ## Map"): PASS
- AC6 guard (every committed producer result under .sdlc validates): PASS
- AC7 (plugin copy with the heading removed from scout.md shows "agents/scout.md: result schema: missing ## Carry forward"): PASS
- AC8 (plugin copy with the reader phrase removed from builder.md shows "agents/builder.md: carry-forward text missing"): PASS
- AC9 guard `python3 plugins/sdlc-lite/scripts/check.py`: PASS ("ok: 19 role levels, 9 agents checked")
- AC10 (the regenerated TOMLs contain the new text): PASS
- AC11 guard (changed files stay in the allowed set): PASS
- AC12 guard (no em dashes in the changed agent and script files): PASS
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`: rc 0. Then `generate --check`: "Codex agent definitions verified", rc 0
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: rc 0
- `git diff --check`: clean
- Base negative control: `results.py` taken from `$SDLC_BASE_SHA` accepts the AC5 out-of-order fixture (rc 0). So AC5 was red at base and is green now.

## Notes
- I split the archaeologist and architect SCHEMA entries over several lines, as the architect entry already was. This keeps every line within the file's existing longest line (132 characters). The content is exactly what the handoff specifies.
- Not my change: check.py's existing Lean lane code comment says "(docstring item 13)", but the docstring numbers that item 14. I left it alone.
- I did not run the repo-wide gates (`check.sh`, packaging). The handoff puts them on step 2.
