---
id: T-0738
title: "Stale open folder drop refuses when the open copy holds edits"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`drop_stale_open` (T-0723) removes a lane's open `NNNN-*` folder only when it holds nothing the closed `.NNNN-*` copy lacks; when the open copy has extra files or different handoff text (beyond the front matter and sections the close itself changes), the merge refuses with a message naming the folder and the differing files, and nothing is dropped.

## Intent
- Do: in `plugins/sdlc-lite/scripts/fanout.py` (`drop_stale_open`, about line 1652), compare the open folder with the closed one (or with the open folder's state at the merge base) and drop only when the open copy adds nothing. Add selftest cases: an unchanged stale open copy is still dropped (T-0723 case passes); an open copy with an extra file or an edited body refuses and keeps both folders.
- Non-goals: merging the edits automatically.
- Done when: the criteria pass.

## Context
T-0723 verifier-L2 (landed):
- plugins/sdlc-lite/scripts/fanout.py:1652 decide: data-loss probe. `drop_stale_open` removes an open folder whenever a closed folder with the same number sits in the index, whatever the open copy holds. In a scratch repo an open `0002-t2` with an extra file and different handoff text was dropped (`D .sdlc/0002-t2/extra.md`, `D .sdlc/0002-t2/handoff.md`). Edits to an open folder do not normally reach this path. A real merge of main's rename into a lane that edited the open handoff keeps the edits in `.0009-t/handoff.md` (checked in a scratch repo), and a rename with too little similarity stops at a modify/delete conflict before the drop. A deliberate re-add that differs from the closed copy is dropped. The content stays in the merge's second parent.
- plugins/sdlc-lite/scripts/fanout.py:1652 decide: the drop is reported only in `merge_gate_close` (land). The other callers (fanout.py:3087 settle, :3314 sync, lanes.py:1116 lanes forward) pass no `dropped` list, so the drop is silent there, although the handoff Outcome says every caller gets it.

## Acceptance criteria
1. The new `fanout.py` selftest cases pass, `case 23 stale open folder (T-0723)` still passes, and with the comparison removed the refusal case fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
