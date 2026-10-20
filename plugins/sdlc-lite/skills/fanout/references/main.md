# Bringing the integration branch into main

Detail for the fanout skill's step 5 (Main).

## Light merge gate

When `.sdlc/config` has a `merge_gate: light` line, light merges reached the integration branch behind the light set only, so the main step runs two commands in place of that settle, after the user picks it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py cover <integration> --gate "<cmd>"...` runs the full gate set at the integration tip and commits a `gate-ledger.jsonl` entry (red prints a `git bisect start <to> <from> --first-parent` line: stop and show it), then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py settle <integration> --require-covered`, which refuses (exit 2) an uncovered tip and otherwise performs the fast-forward and closes the integration tree as above.
