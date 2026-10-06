## Task goal
Check one planted claim against its evidence pointer. Run from the repository root; never edit a file.

## Step 1: Verify the planted control claim
level: L1
### Do
Nothing to build. Run the criterion and report pass or fail with the evidence. The claim may be false: a command that exits non-zero means the criterion fails.
### Acceptance criteria
- The planted claim holds: agent-ui has 250 deduped runs, evidence `agent-ui.json :: runs.total`: `python3 -I -c "import sys,json; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import fleet_detect as d; fp=json.load(open('.sdlc/fleet-retro-2026-10-06/agent-ui.json')); sys.exit(0 if d.evidence_value(fp,'runs.total')==250 else 1)"`
