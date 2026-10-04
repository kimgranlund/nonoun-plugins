## Task goal
Independently verify T-0218: check.py docstring guards are numbered 1..N once each, comment references agree, and a new guard rejects a duplicate number or a missing cited item.

## Step 1: Verify the guard renumbering
level: L2

### Do
Read-only, in this worktree. Read the diff of plugins/sdlc-lite/scripts/check.py against 244d0af. Confirm every docstring heading is unique and sequential, each "docstring item N" comment names the guard it sits above, and no living doc outside docs/validation cites an old number. Then run the criteria.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite $d/p && sed -i.bak 's/^19\. Conductor rules/18. Conductor rules/' $d/p/scripts/check.py && ! python3 $d/p/scripts/check.py $d/p`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite $d/p && printf '\n# x (docstring item 99)\n' >> $d/p/scripts/check.py && ! python3 $d/p/scripts/check.py $d/p`
