## Task goal
Independently verify T-0218: check.py docstring guards are numbered 1..N once each, comment references agree, and a new guard rejects a duplicate number or a missing cited item.

## Step 1: Verify the guard renumbering
level: L2

### Do
Read-only, in this worktree. Read the diff of plugins/sdlc-lite/scripts/check.py against 244d0af. Confirm every docstring heading is unique and sequential, each "docstring item N" comment names the guard it sits above, and no living doc outside docs/reports cites an old number. The copy in criteria 3 and 4 holds only plugins/sdlc-lite, so check.py may also print unrelated failures there (docs and .claude are missing); those criteria therefore look for the new guard's own message, not for an exit code. Then run the criteria.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite $d/p && sed -i.bak 's/^19\. Conductor rules/18. Conductor rules/' $d/p/scripts/check.py && python3 $d/p/scripts/check.py $d/p 2>&1 | grep -q 'docstring guard numbers are not'`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite $d/p && printf '\n# x (docstring item 99)\n' >> $d/p/scripts/check.py && python3 $d/p/scripts/check.py $d/p 2>&1 | grep -q 'which does not exist'`
