# Lane lifecycle

Detail for the fanout skill: how lanes open, stop and close, and the external lane and headless run rules.

Lanes open through `lanes.py`, which writes each lane's `.lane.json`. A lane whose tickets all merged is closed after its archive ref `refs/archive/<date>/<branch>` is written, so its tree and branch are gone and `lanes.py archive restore` brings the branch back. A stopped lane stays, and the report says `lane still open: <path> (<outcome>)`. The integration tree stays until main contains the integration branch. `run` and `prep` start with `lanes.py sweep --apply`, which closes every landed lane, unless `.sdlc/config` has `lane_sweep: off`. `roll` removes its scratch tree at the end of every roll. When `.sdlc/config` has `lane_ports: <lo>-<hi>`, each lane gets a port, and its driver and gates see it as `$SDLC_LANE_PORT`. Each `lane_setup: <cmd>` line in `.sdlc/config` (install, codegen, builds) runs in order in every new lane tree, the first failure stops the rest, `open` prints `setup: ok` or `setup: failed rc=<n> (<cmd>)`, and a failed setup keeps the lane.

## Stops and dirty trees

`fanout.py` makes commits only inside the lanes dir (the lane branches and the integration branch); it never touches main and never pushes. When a lane stops on a driver failure or any outcome other than `merged`, a dirty lane tree is committed as `wip(<id>): <outcome>` on the lane branch only (never merged). A tree already dirty before a ticket's sync is WIP-committed as `wip(<id>): dirty before sync` and that ticket stops with the outcome `dirty before sync`, never merged. An integration worktree with uncommitted tracked changes is refused before the merge with the outcome `integration dirty: <path>`; nothing is merged or reset, so the edit survives. Inspect a stopped lane's `wip(` commit on its lane branch.

## External lanes

An external lane (`<lane>@<branch>=<ids>`) names a branch an outside agent (for example Codex) owns, registered with an `external_branch: <branch>` line in `.sdlc/config`. Fanout runs no driver on it, creates no worktree and no `<integration>-<lane>` branch, and never writes that branch. It is merged `--no-ff` into the integration branch under the lock, gated, and its tickets are closed there; a second ticket on the same branch merges nothing new and skips the gates. A `merge conflict` outcome means the outside agent merges the integration branch on their side before the run is repeated. The lane shows in `report.md` but not in `board.py --lanes`, which lists worktrees.

## Headless runs

`hooks/block-background.sh` denies Bash `run_in_background` calls and denies any Agent call unless `run_in_background` is explicitly `false` (Agent runs in the background by default, so a missing field counts as background) whenever `SDLC_ROLE` is set or `SDLC_HEADLESS=1`; bench.sh and fanout set `SDLC_HEADLESS=1`, and any other headless launcher (a dogfood script) must set `SDLC_HEADLESS=1` itself.

## Legacy lane roots

A repo with lanes under a legacy root (`.claude/worktrees/` or `.worktrees/`) runs `${CLAUDE_PLUGIN_ROOT}/scripts/migrate-worktrees.sh` once from its root (a dry run; `--apply` moves).
