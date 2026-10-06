# Parked tickets review, 2026-10-06

Nine tickets parked on 2026-10-04 were reviewed against the four pillars (`docs/sdlc-lite/pillars.md`) and the actionability test (evidence, mechanism, right owner, not already fixed). Code checked at main 41d6f096 under `plugins/sdlc-lite/scripts/`.

Common finding: every ticket tuned the orchestrated chain or the `.sdlc/` layout for the lean-chain design (`docs/sdlc-lite/design.md` v0.4, "Nothing here is built"). Solo is now the default lane and has run on real tickets (`docs/reports/solo-vs-lean-benchmark-2026-10-04.md`, `docs/reports/solo-live-run.md`); plan review is limited to L4 and L5 steps. None of the nine moved a pillar measure that is still in flight.

| Id | Verdict | Why | Evidence |
|---|---|---|---|
| T-0187 board-overview | MERGE-INTO T-0312 | Not built (no `--overview` in `board.py`). T-0183 landed (`supervisor.py`, `status.json`), so the data exists; per-repo unread mail ids and supervisor state belong in the fleet-status Moving rows, which already own cross-folder status. Line added to T-0312. | `scripts/board.py`, `scripts/supervisor.py`, `.sdlc/0312-fleet-status-render/handoff.md` |
| T-0200 plan-merge | DROP | Replan by delta serves chain replans only; plan review now runs for L4 and L5 steps. Never built: no `revises` and no `resolve` subcommand in `steps.py`. | `scripts/steps.py` (subcommands at the `add_parser` list), `pillars.md` |
| T-0201 anchor | DROP | Anchor rule for planner step blocks, depends on T-0200; chain-only text, no measure in flight. Not built (no anchor resolution in `steps.py lint`). | `scripts/steps.py` |
| T-0205 layout-resolver | DROP | The topic layout (`layout: topics`) was never built. The root-clutter pain is covered by numbered folders, `tickets.py archive` (dot folders hide closed work) and `ticket_root`. Size L, no measured pillar benefit. | `scripts/tickets.py` (`archive`, `number`, `ticket_root`; no `layout` key), `skills/ticket/SKILL.md` |
| T-0206 migrate-layout | DROP | Migration for the layout dropped with T-0205; no `migrate-layout` command exists. | `scripts/tickets.py` |
| T-0207 layout-readers-docs | DROP | Readers for the dropped layout (depends on T-0206). The docs schema (T-0240 to T-0243) is a separate, merged system for `docs/`. | `scripts/docs_check.py`, `scripts/board.py` |
| T-0208 live-evidence | DROP | Lean vs full footprint runs are superseded by the solo-vs-lean benchmark, with `lane` live evidence in docs/reports/solo-live-run.md and sub-agent evidence owned by open ticket T-0287 (a headless chain run on Codex stays unproven, which matters less with solo as default); its dependencies T-0201 and T-0207 are dropped. | `docs/reports/solo-vs-lean-benchmark-2026-10-04.md`, `.sdlc/0287-subagent-live-evidence/handoff.md` |
| T-0211 spec-gate-red | DROP | `specgate.py` ships `check` only (T-0210); `red` (the run-before-build control) runs at chain `split` time; `check` already parses the `(red)` tag and solo criteria are not split. If red-first is wanted for solo criteria, file a new ticket with its own evidence. | `scripts/specgate.py` (only `check`), `scripts/steps.py` |
| T-0213 replan-delta-checklist | DROP | Replan handoff, planner checklist and `replans` metric all serve chain replans; depends on dropped T-0200, T-0201 and T-0211. No `replan-handoff` command and no `replans` metric in `footprint.py`. | `scripts/footprint.py`, `scripts/steps.py` |

KEEP rows: none.

Recording: `tickets.py close --reason` sets status done, so dropped is recorded by front matter `status: dropped` plus a `## Dropped` section in each handoff (the pattern of earlier dropped tickets). Folders are not archived.

## Update, 2026-10-06 (later the same day)

The user reinstated T-0205, T-0206 and T-0207 (the topic layout as a unit; T-0206 depends on T-0205 and both need the readers in T-0207). They are `proposed` again with a `## Reinstated` note; the DROP rows above for those three no longer apply.
