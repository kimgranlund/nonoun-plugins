# Codex live lane smoke, 2026-10-15 (T-0570)

One L1 ticket ran through a lane on Codex under the sibling worktree root: open, solo, verify, land, close. It ran twice, once under the `workspace-write` sandbox and once with full access. Under full access every step passed, after two plugin defects were repaired by hand (T-0598, T-0599). Under `workspace-write` every step that writes git state or the lane tree failed.

## Setup

- codex-cli 0.162.1. Conductor model `gpt-6-astra`, effort medium. Plugin: the T-0570 working tree (`plugins/sdlc-lite`, version 0.23.1).
- Two throwaway repos, made outside the sandbox: `$TMPDIR/sdlc-lite/t0570/full/smoke-full` and `$TMPDIR/sdlc-lite/t0570/ws/smoke-ws`. `$TMPDIR` is `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/`. Each repo holds `greeting.txt` and `check.sh`, which greps for `hello from sdlc`. It also holds ticket `T-0001` (`.sdlc/greeting`, size L1, criterion `sh check.sh` exits 0) and the 29 project agents from `codex_roles.py install <repo>`. `sh check.sh` exited 1 on the base, so the criterion was red before the change.
- Each step is its own `codex exec` call from the main checkout: `codex exec -C <repo> -m gpt-6-astra -c 'model_reasoning_effort="medium"' -c agents.enabled=true -c 'approval_policy="never"' --output-last-message <file> -`. The prompt goes on stdin. The call runs under `perl -e 'alarm shift @ARGV; exec @ARGV' 540` (a 9 minute cap). Codex runs the plugin commands itself and reports `EXIT=<n>` for each one. Each result was then checked against the repo state (`git log`, `git worktree list`, the ticket's `status:` line).
- Full access: `--dangerously-bypass-approvals-and-sandbox`.
- `workspace-write`: `--sandbox workspace-write -c sandbox_workspace_write.exclude_tmpdir_env_var=true`, with `TMPDIR=/tmp` for the Codex process. By default Codex makes `$TMPDIR` writable, and that would have made the sibling `smoke-ws.worktrees/` writable. A probe confirmed it: with the defaults, `touch ../probe-sibling` exited 0. With `$TMPDIR` excluded, the same command failed with `Operation not permitted`. In both cases `.git` stayed read-only: `git commit` exited 128 on `.git/index.lock`. The ws open, solo and first verify calls also excluded `/tmp` (`exclude_slash_tmp=true`). For the verify call that broke shell here-documents (`cannot create temp file for here document`), so it was rerun with `/tmp` writable, and only the rerun is counted below. The open and solo failures were on `.git/index.lock`, the sibling `smoke-ws.worktrees` dir and `.git/worktrees/<lane>/solo_run.lock`, none of them temp paths, so those results stand.
- Every `codex exec` call exited 0, including the calls whose commands failed. The exit codes below are the codes of the commands Codex ran.

## Results

| Step | Command (run by Codex) | Full access | `workspace-write` |
|---|---|---|---|
| open | `tickets.py claim T-0001 --by codex`; `git commit`; `lanes.py open greeting --kind solo --ticket T-0001` | 0; 0; 0 | 0; 128; 1 |
| solo | `cd <lane> && SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent python3 solo_run.py run --backend codex --task-dir .sdlc/greeting --tier L1 --brief-file <brief> --no-worktree`, then spawn `sdlc-solo-l1` and `codex_exchange.py <request> <report>` | exchange 0, wrapper 0, `sh check.sh` 0 | wrapper 1, no request, no agent |
| verify | `cd <lane> && SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent bash run.sh verifier L1 .sdlc/greeting/handoff.md`, then spawn the agent the request names and `codex_exchange.py` | first try 2 (T-0598); after `codex_roles.py install <lane>`: install 0, exchange 0, runner 0, Verdict pass | install 2; runner 2, no request |
| land | `fanout.py land lane/T-0001-greeting --ticket T-0001 --gate "sh check.sh" --no-gate-lock` | 0 (`merged`; it runs `tickets.py close` on `fanout/2026-10-15`) | 1 |
| close | `fanout.py settle fanout/2026-10-15 --forward --gate "sh check.sh" --no-gate-lock`, then `grep '^status:'` in main | first try 2 (T-0599); after `git commit` of the lane record: 0, `status: done` in main | commit 128; settle 0 (`nothing to settle`); `tickets.py close greeting --reason ...` 0, but its commit 128 |

### Errors under `workspace-write`

- open: `git commit` fails with `fatal: Unable to create '<repo>/.git/index.lock': Operation not permitted`. `lanes.py open` fails with `PermissionError: [Errno 1] Operation not permitted: '<parent>/smoke-ws.worktrees'`.
- solo: `PermissionError: [Errno 1] Operation not permitted: '<repo>/.git/worktrees/T-0001-greeting/solo_run.lock'`, before any request file.
- verify: `codex_roles.py install <lane>` fails with `[Errno 1] Operation not permitted: '<lane>/.codex'`. `run.sh` fails with `mkdir: <lane>/.sdlc/runtime: Operation not permitted` and `run.sh: cannot make the records dir <lane>/.sdlc/runtime/tasks/greeting`.
- land: `PermissionError: [Errno 1] Operation not permitted: '<parent>/smoke-ws.worktrees/fanout'`.
- close: no integration branch exists to settle, so the settle succeeds without doing anything. `tickets.py close` edits only files inside the checkout, so it exits 0 and sets `status: done` in the working tree. The commit that would record that fails on `.git/index.lock`, so main still says `status: claimed`.

So that the ws run could reach each step, the launcher repaired the state outside the sandbox after each failed step. It committed the claim and ran `lanes.py open`, then made the solo's change and commit (`51a70c6`). The ws verifier was not repaired, because an L1 land needs no verifier result.

### Full-access run

- Lane worktree: `/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/t0570/full/smoke-full.worktrees/T-0001-greeting`, branch `lane/T-0001-greeting`. The integration worktree was `.../smoke-full.worktrees/fanout/integration`. Settle removed it and kept `refs/archive/2026-10-15/fanout/2026-10-15`.
- Solo: the request named `sdlc-solo-l1`. The report's first line was `profile: 0.23.1+4c3e5fa89273`. The `runs.jsonl` row records `backend codex`, `transport subagent`, model `gpt-6.1-sol`, `cost_usd` null with `codex reports no cost`, and `profile_check ready`. The solo made lane commit `bdf0a08 T-0001: Add the greeting line`.
- Verify: the request named `sdlc-verifier-l1` (model `gpt-6-luna`, so no alternate was needed against the solo's `gpt-6.1-sol`). It returned `profile: 0.23.1+7cc6a076e028` and Verdict pass. `run.sh` printed `loaded context not recorded: rollout absent`.
- Main after settle: `a20d0c2 cover 00165ec: rc=0`, `00165ec settle --forward: main c95a5ef into fanout/2026-10-15`, `c95a5ef T-0001: record lane`, `43e2617 close T-0001`, `2cff2bf Merge lane/T-0001-greeting: T-0001`. `.sdlc/greeting/handoff.md` reads `status: done`, and `git status --short` in main is empty. The lane worktree remains for `lanes.py sweep` once it passes `lane_min_age_hours`.

## Failures under full access, filed

- T-0598: the first `run.sh verifier` in the lane exited 2 with `agents missing or stale: sdlc-archaeologist-l1.toml, ...; run python3 ".../codex_roles.py" install "<lane>" and start a fresh Codex chat`. The generated agents are git-ignored, so a new lane has none. `solo_run.py` does not check for them; `run.sh` does.
- T-0599: `lanes.py open` writes the ticket's `branch:` and `worktree:` lines, the router and the roadmap in main, and leaves them uncommitted. The first settle then exited 2: `fanout/2026-10-15 is not a fast-forward of main: error: Your local changes to the following files would be overwritten by merge`.

## Other findings

- T-0600: the request files are not where the docs say. `codex-role-execution.md` and `adapters/codex/instructions.md` place them in the ticket folder (`solo-<level>-<attempt>.request.json` in the ticket folder, "beside the handoff"). The run found both under `<lane>/.sdlc/runtime/tasks/greeting/`. Codex's glob on the documented path failed: `zsh:1: no matches found: .sdlc/greeting/solo-L1-*.request.json`.
- `fanout.py land` printed `T-0001 land lane/T-0001-greeting (lane full)` for a lane that `lanes.py open --kind solo` made for an L1 ticket. Not filed.
- The verifier's records dir kept `verifier-L1.request.lock`, `verifier-L1.request.owner.lock` and `verifier-L1.request.response.json` after the runner exited. Its `runs.jsonl` row has `exit_code` null. The solo wrapper removes its own lock and response files. Not filed.

## Guidance change

The T-0564 note said that lane open, land and close write `.git` and so need full access under Codex. The run contradicts the implied limit: the solo wrapper and the verifier runner also fail under `workspace-write`, on `.git/worktrees/<lane>/solo_run.lock` and on the lane's records dir. The note now names the solo and verifier runs as well, in `AGENTS.md`, `plugins/sdlc-lite/AGENTS.md`, `docs/specs/repo-onboarding/design.md` and the managed block in `plugins/sdlc-lite/scripts/onboard.py`. That block counts as stale by its text, so setup replaces it in consumer repos with no version bump. Nothing contradicted the rest of the note.
