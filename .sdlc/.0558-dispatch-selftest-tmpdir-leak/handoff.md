---
id: T-0558
title: "dispatch.py selftest accept-all controls fail when an unmarked folder sits under TMPDIR/sdlc-lite"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py selftest` passes regardless of what other runs left under `$TMPDIR/sdlc-lite/`.

## Repro
1. Leave an unmarked folder under `$TMPDIR/sdlc-lite/` (any scratch without `.owner.json`).
2. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`.

## Expected
PASS: the selftest's fixtures use their own scratch root.

## Actual
The 3 accept-all negative controls fail because `record` prints `unmarked:` for the foreign folder (T-0545 builder, 2026-10-14; same on unchanged HEAD). `check.sh` went red once for this reason.

## Context
T-0550 made the sweep cover every repo's scratch under `$TMPDIR/sdlc-lite/`. Guess: the selftest should point the scratch root at a private temp dir.

## Constraints
The failing test lands before or with the fix. Target 0.23.1.

## Acceptance criteria
- (red) `python3 -c "import os,sys,tempfile; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import dispatch, wtroot; b=os.path.realpath(tempfile.mkdtemp()); old=tempfile.gettempdir(); c=dispatch.private_tmpdir(b); t=c.__enter__(); ok=wtroot._under(str(wtroot.scratch_root('.')), b) and os.environ['TMPDIR'].startswith(b); c.__exit__(None,None,None); sys.exit(0 if ok and tempfile.gettempdir()==old else 1)"`
- `d=$(mktemp -d) && mkdir -p "$d/sdlc-lite/foreign-0000/leftover" && TMPDIR="$d" python3 plugins/sdlc-lite/scripts/dispatch.py selftest`
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`

## Outcome

2026-10-14 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: 20104bf87b00
- Changed: see commits
- Commits: 3332a4e T-0558: dispatch.py selftest uses a private TMPDIR
- Check: 1 (red) private_tmpdir unit probe: pass
- Check: 2 foreign unmarked folder under `$TMPDIR/sdlc-lite`, selftest: pass
- Check: 3 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`: pass
- Follow-up: note: my first parallel batch showed FAIL the 3 accept-all controls for... -> notes.md
- Follow-up: note: the selftest takes minutes at load average ~18; one round of three... -> notes.md
