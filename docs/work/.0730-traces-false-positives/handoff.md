---
id: T-0730
title: "traces.py detect skips evidence logs, fanout lanes and declared preview worktrees"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`traces.py detect` stops flagging deliberately tracked evidence logs (`docs/evidence/**` by default, or a declared path), fanout lane branches recorded in report.md, and worktrees a repo marks as intentional.

## Intent
- Do: Fix `fanout.py land` to write sub-agent lanes as regular lanes in report.md (not `external branch ... at None`), and make `traces.py` detectors skip: lanes with a `.lane.json` or worktree; evidence paths; and an opt-out marker for intentional worktrees.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #66 (quoted):

> **Observed** on one consumer repo: 496 findings, of which:
> - `tracked-runtime-file` (398): `docs/evidence/*.stdout.log` etc. are deliberately tracked evidence, not runtime files.
> - `unregistered-external-branch` (54): reads `fanout/report.md` and flags the fanout's own lane branches (`fanout/2026-10-21-testcaps`) as unregistered external branches.
> - `stray-worktree`: flags a deliberate long-lived preview worktree (`.worktrees/tmp/preview`).
>
> **Expected**: detectors skip paths a repo declares as evidence (or `docs/evidence/**` by default), know fanout lane branches, and allow an opt-out marker for intentional worktrees.
>
> **Evidence**: `.sdlc/runtime/traces/<repo>/findings.jsonl` from `traces.py detect`.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

GitHub issue #53 (quoted):

> ## What happened
> With Claude-host sub-agent lanes, which are opened with `lanes.py open --kind fanout` and landed with `fanout.py land <branch> --ticket T-x`, the lanes-dir `report.md` lists each lane as an external lane:
>
> ```
> - Lane `fanout-2026-10-21c-appdedupe`: external branch `fanout/2026-10-21c-appdedupe` at `None`
> ```
>
> These lanes are ordinary lanes.py lanes with a worktree and a `.lane.json`, not `external_branch:` entries. `traces.py detect` then reads the lines literally. On one repo it raised 269 `unregistered-external-branch` findings ("external branch fanout/...-X is not registered in the ticket config"), which bury the real findings.
>
> ## Expected
> `land` writes these lanes as regular lanes in report.md, or `traces.py` skips lanes that have a `.lane.json` or a worktree.
>
> ## Repro
> 1. Run `lanes.py open x --kind fanout --ticket T-1 --into <integration> ...`.
> 2. Commit in the lane.
> 3. Run `fanout.py land fanout/<integration>-x --ticket T-1 ...`.
> 4. `grep "external branch" <lanes-dir>/report.md`.
> 5. `traces.py ingest . --lanes-dir <lanes-dir>`, then `traces.py detect`.
>
> Seen on sdlc-lite 0.30 to 0.33.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `traces.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/traces.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Root cause (#53): `fanout.py land` builds its lane as `Lane(name, [tid], branch)`, so the branch lands in the `external` slot and `report()` wrote every landed branch (and each journal-replayed one, whose tip is None) as `external branch ... at <sha|None>`. `report()` now writes a land lane as a regular lane, `` - Lane `<name>`: `<worktree>` (branch `<branch>`) `` or `` - Lane `<name>`: branch `<branch>` ``; land.jsonl lines carry the `worktree` for the replay. The merge path still reads `lane.external` unchanged.
- traces: `sources/fanout.read` adds `landed` (branches from logs/land.jsonl), and `hygiene` skips an external lane whose branch is in that list or checked out in a worktree holding `.lane.json` (this clears pre-fix reports too); `tracked-runtime-file` skips `docs/evidence/` and each docs/layout.md home of kind `reports`; `stray-worktree` skips a worktree holding a `.sdlc-keep` file at its root.
- Red control: with the traces change reverted, `traces.py selftest -k hygiene` printed `- hygiene: tracked evidence logs, landed or lane-recorded fanout lanes, and a kept worktree are no findings (T-0730): [{... 'detector': 'stray-worktree' ...` and `traces selftest: FAIL`. With the report change reverted, `fanout.py selftest` exited 1 on `case 23 land (T-0730): report.md writes each landed branch as a regular lane, no external branch line`.
- Checks: `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/traces.py selftest` exit 0; `fanout.py selftest` (gate_lock) exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` PASS; `git diff --check 83a3a4e6` exit 0.
- Open: a Codex external branch checked out in a plain worktree (no `.lane.json`) still counts as external, by design. The `.sdlc-keep` marker is untracked in the kept worktree; a repo can list it in info/exclude.

## Outcome

2026-10-22 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: 83a3a4e63e21
- Changed: see commits
- Commits: db67116 T-0730: traces.py detect skips evidence logs, fanout lanes and declared preview worktrees
- Check: 1 A traces.py selftest case reproduces the issue repro and fails with the change reverted: pass
- Check: 2 gate_lock traces.py selftest exits 0: pass
- Check: 3 check.py exits 0, check-packaging passes, git diff --check clean: pass
- Check: 4 Conductor note, skips do not hide real findings: pass
- Check: 5 Conductor note, `.sdlc-keep` documented: pass
- Follow-up: note: plugins/sdlc-lite/scripts/traces/detectors/hygiene.py... -> notes.md
