# Two-host rehearsal: Claude Code and Codex in one repo

Date: 2026-10-15. Ticket: T-0592. Scripts: this lane's `plugins/sdlc-lite/scripts` (branch `lane/T-0592-t0592` at `20204aed`), called by absolute path; below `$S` stands for that folder.

## Result

- Exactly one host won the shared claim: Codex took `refs/sdlc/claims/T-0001`; Claude's claim at the same moment refused with exit 1 and wrote nothing.
- Both tickets ended `status: done` in main, each through its own lane, a cross-family verifier and `lanes.py finish`. No work was lost (`a.txt` and `b.txt` both end with `done` in main), no claim or ready ref was left behind, and no lane or branch remained.
- One failure: the first `lanes.py ready` in the fresh repo exited 1 because no conductor mailbox was registered. Filed as T-0610.
- Pi did not run: it is not installed here (`which pi` printed `pi not found`). Per the plan review amend the rehearsal ran two hosts, so criterion 1's "three tickets" reads "two tickets" (one per host). Pi follow-up: T-0611.

## Setup

- Hosts: Claude Code (this session, Opus 5.5, `SDLC_HOST=claude`) and Codex (`codex-cli 0.162.1`, `SDLC_HOST=codex`).
- Every Codex call was `codex exec --dangerously-bypass-approvals-and-sandbox -C <dir> -o <last message file> "<instruction>"`, not `--full-auto`: `--full-auto` is the workspace-write sandbox, which blocks `.git` writes and the lanes root outside the repo, so a Codex claim would have failed on the sandbox, not on the claim ref. Repo guidance says lane open, ready, land and close need full access under Codex.
- Throwaway repo: `$TMPDIR/sdlc-lite/rehearsal/repo` with a bare `origin.git` beside it as `origin` (main does not track it; nothing was pushed). Lanes root: `$TMPDIR/sdlc-lite/rehearsal/repo.worktrees`.
- The brief named `tickets.py init`; no such command exists. `tickets.py --root .sdlc new` starts a root and was used instead.

## Commands and exit codes

| # | Host | Command | Exit | Output (key line) |
|---|---|---|---|---|
| 1 | claude | `git init -q --bare origin.git; git init -q -b main repo`; commit `a.txt`, `b.txt`, `.gitignore`; `git remote add origin ...` | 0 | |
| 2 | claude | `python3 $S/tickets.py --root .sdlc new chore alpha "Append a line to a.txt"` | 0 | T-0001 |
| 3 | claude | `python3 $S/tickets.py --root .sdlc new chore bravo "Append a line to b.txt"` | 0 | T-0002 |
| 4 | claude | set both `status: ready`, `size: L1`, one criterion each; `tickets.py --root .sdlc roadmap`; `tickets.py --root .sdlc check` | 0, 0 | `ok: 2 tickets, roadmap current` |
| 5 | codex | `bash .sdlc/runtime/codex-claim.sh` (touch a ready marker, spin on a go file, then `SDLC_HOST=codex python3 $S/tickets.py --root .sdlc claim T-0001`) | inner 0, `codex exec` 0 | `alpha: claimed_by: codex:01a14304 2026-10-15` |
| 6 | claude | at the same moment (go file touched once Codex was spinning): `SDLC_HOST=claude python3 $S/tickets.py --root .sdlc claim T-0001` | 1 | `already claimed by codex:01a14304 2026-10-15 (refs/sdlc/claims/T-0001); ... nothing written` |
| 7 | claude | `git for-each-ref refs/sdlc/claims` | 0 | one ref, `refs/sdlc/claims/T-0001` holding `codex:01a14304 2026-10-15` |
| 8 | claude | `SDLC_HOST=claude python3 $S/tickets.py --root .sdlc claim T-0002` | 0 | `bravo: claimed_by: claude:66c988ad 2026-10-15` |
| 9 | claude | `tickets.py --root .sdlc check`; `git commit` of both claims (conductor) | 0, 0 | |
| 10 | claude | `SDLC_HOST=claude python3 $S/lanes.py open T-0002-bravo --kind solo --ticket T-0002 --root .sdlc` | 0 | lane `T-0002-t-0002-bravo`, `locked: claude:66c988ad T-0002`, `committed: 89a2bea` |
| 11 | claude | in the lane: `echo done >> b.txt`; `grep -qx done b.txt` | 0, 0 | |
| 12 | claude | `SDLC_HOST=claude python3 $S/lanes.py ready` | **1** | ref pinned, unlocked, then `not sent to conductor: ... receiver conductor is not registered (registered: none)` (T-0610) |
| 13 | claude | `python3 $S/messages.py register --name conductor --harness claude` (in main) | 0 | |
| 14 | claude | `SDLC_HOST=claude python3 $S/lanes.py ready` (rerun) | 0 | `ready: refs/sdlc/ready/T-0002 c13d2274`, `sent: ready T-0002 to conductor` |
| 15 | codex | `SDLC_HOST=codex python3 $S/lanes.py open alpha --kind solo --ticket T-0001 --root .sdlc` | 0 | lane `T-0001-alpha`, `locked: codex:01a14304 T-0001`, `committed: d3bfd97` |
| 16 | codex | in the lane: `echo done >> a.txt`; `grep -qx done a.txt` | 0, 0 | |
| 17 | codex | `SDLC_HOST=codex python3 $S/lanes.py ready .` | 0 | `ready: refs/sdlc/ready/T-0001 532ed09e`, `sent: ready T-0001 to conductor`; `codex exec` 0 |
| 18 | claude | `python3 $S/lanes.py list --ready` | 0 | two rows, T-0001 and T-0002, neither stale |
| 19 | codex | verify T-0002 (Claude's lane) at pinned `c13d2274`: `git show c13d22747fc9:b.txt \| grep -qx done`; `git diff --name-only 5b6fef730a53 c13d22747fc9` (only `b.txt`); `grep -qx done b.txt`; negative control on the base | 0, 0, 0, 1 | wrote `verifier-L2.md` (pass); `codex exec` 0 |
| 20 | claude | `python3 $S/results.py validate <bravo records>/verifier-L2.md --role verifier` | 0 | |
| 21 | claude | verify T-0001 (Codex's lane) at pinned `532ed09e`: `git show 532ed09e27ca:a.txt \| grep -qx done`; `git diff --name-only 89a2bea85063 532ed09e27ca` (only `a.txt`); `grep -qx done a.txt`; negative control on the base | 0, 0, 0, 1 | wrote `verifier-L2.md` (pass) |
| 22 | claude | `python3 $S/results.py validate <alpha records>/verifier-L2.md --role verifier` | 0 | |
| 23 | claude | `SDLC_HOST=claude python3 $S/lanes.py finish T-0002-t-0002-bravo` (main) | 0 | verdict pass, commit, land, settle `main at 8d5c477`, close, lane closed |
| 24 | claude | `SDLC_HOST=claude python3 $S/lanes.py finish T-0001-alpha` (main) | 0 | verdict pass, commit, land, settle `main at 764146f`, close, lane closed |
| 25 | claude | `grep -H "^status:" .sdlc/*/handoff.md` | 0 | both `status: done` |
| 26 | claude | `git for-each-ref refs/sdlc/`; `git worktree list`; `git branch -a` | 0 | only `refs/sdlc/ids/T-0001`, `T-0002`; one worktree; only `main` |
| 27 | claude | `tickets.py --root .sdlc check`; `lanes.py list --all` | 0, 0 | `ok: 2 tickets, roadmap current`; no lanes |

Final main history, newest first: `4c7ed50 T-0001: lane T-0001-alpha closed`, `764146f close T-0001`, `29d0093 Merge lane/T-0001-alpha: T-0001`, `05a49e0 T-0001: Append a line to a.txt`, `7559378 T-0002: lane ... closed`, `8d5c477 close T-0002`, `cbe3ab5 Merge lane/T-0002-...: T-0002`, `2c342e0 T-0002: Append a line to b.txt`, `d3bfd97` and `89a2bea` (lane records), `5b6fef7` (claims), `80aa290` (tickets), `84825c1` (init).

## Observations

- The race: Codex's script spun on the go file, so both `tickets.py claim` processes started within milliseconds. Codex created the ref first; Claude's claim read the ref, refused naming the holder, and left the handoff unchanged. `tickets.py check` showed no disagreement between front matter and refs.
- Workers committed nothing; `lanes.py ready` pinned a snapshot commit (`sdlc ready snapshot: <id> in <lane>`, with a `Lane-Base:` trailer) and each verifier read that sha. `finish` committed and landed each lane from main.
- The two lanes were opened one after the other, since `open` commits the lane record in main; only the claim was raced.
- The verifier results were written by hand to each lane's records dir in the role schema (`results.py validate` exit 0), not through `dispatch.py prepare verifier`; `finish` reported `record: nothing pending` for that reason.
- The Claude lane leaf doubled its ticket (`T-0002-t-0002-bravo`) because the name passed to `open` already held the id; `open` prefixes the ticket. Naming slip in the rehearsal, not a defect.

## Codex time

Three `codex exec` calls: claim 11 s, lane work 37 s, verify 29 s; 77 s in all, under the 15 minute cap.

## Failures filed

- T-0610: `lanes.py ready` exits 1 in a freshly onboarded repo because no conductor mailbox is registered; the ref is pinned and the lane unlocked first, so the exit code reports a missing notice, not lost work.
- T-0611: rehearse a Pi host beside Claude Code and Codex once Pi is installed.
