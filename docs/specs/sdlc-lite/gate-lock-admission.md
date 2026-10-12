# Gate lock as the shared admission authority

Built as `gate_lock.py` protocol `sdlc-gate/2` by ticket T-0409 (2026-10-09), after the maintainer approved the build and the numbers. Version 0.1, 2026-10-08, ticket T-0386. Where this design and the build differ, the build notes at the end say how; the current behavior is in the `gate_lock.py` entry of [sdlc-internals](../../references/sdlc-internals.md). The text below is the original design, kept as written, so its statements that the numbers 6 and 3 are not approved are superseded by the build notes.

## 1. Answer in one paragraph

Agree on the origin, counter-design the size. `plugins/sdlc-lite/scripts/gate_lock.py` becomes the one admission authority for heavy work on a host, for one OS user, across repos, worktrees, plugin versions, and terminals. There is no repo scheduler and no daemon; a repo gets a thin client and entry guards. Version 1 fixes the four defects the code actually has (a namespace split by TMPDIR, a cap each caller sets itself, one slot per command whatever its weight, and a bare boolean for nesting), adds a plugin-owned policy with weighted vector demand, a FIFO-per-repo and round-robin-across-repos queue (weights make starvation real, so a queue is needed), workload liveness by process group with an exact process start identity, and separate wait and run timing. It defers the parts of the proposal that the evidence does not yet call for: the start-barrier helper, capability tokens with delegation chains, sibling partitioning, request UUID idempotence, and the full event stream. Each deferral names the run result that would bring it back.

## 2. Sources

- The proposal, read as data: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0300-shared-resource-lease-design/` files `interface-contract.md`, `regression-cases.md`, `author-message.md`, `native-architect-response.md`. It inspected the installed 0.21.3 cache; the line numbers below are from this repo at commit `d85d9eef`, which match it for `gate_lock.py`.
- This repo: [gate_lock.py](../../../plugins/sdlc-lite/scripts/gate_lock.py), [fanout.py](../../../plugins/sdlc-lite/scripts/fanout.py) `gate_argv` and `gate_slots_off` (lines 436 to 449) and its selftest `gate_env` (line 2139), [check.py](../../../plugins/sdlc-lite/scripts/check.py) item 35, the conductor's heavy-gate rule in [conductor.md](../../../plugins/sdlc-lite/agents/conductor.md), and the `gate_lock.py` entry in [sdlc-internals](../../references/sdlc-internals.md).
- Probes run on this host (macOS, 20 logical CPUs) on 2026-10-08: `proc_pidinfo(pid, PROC_PIDTBSDINFO)` through ctypes returns 136 bytes with start seconds and microseconds for an own process and 0 bytes for pid 1 (so the byte count must be checked); `ps -o lstart= -p <pid>` returns an absolute start time at one-second resolution; `sysctl -n kern.bootsessionuuid` returns a boot identifier. Linux equivalents (`/proc/<pid>/stat` field 22, `/proc/sys/kernel/random/boot_id`) were not run here and are unverified.
- Codex host behavior was not run live here and is unverified throughout (see section 9).

## 3. Today, the proposal, and this design

| Concern | gate_lock.py today | Proposal (maison T-0300) | This design (v1) |
|---|---|---|---|
| Namespace | `${TMPDIR:-/tmp}/sdlc-gate-locks` (`lock_dir`, line 52): callers with different TMPDIR values do not see each other | One state root per host and OS user, from the OS account | Agree. Root from the account's home in the password database, never from TMPDIR, HOME, XDG variables, cwd, or the plugin cache path. `SDLC_GATE_DIR` overrides it for tests only |
| Capacity | Each caller passes `--slots N` or `SDLC_GATE_SLOTS` (default 2); mixed values give no common cap (`try_acquire`, line 105) | One authority policy; callers send demand only | Agree. `policy.json` in the state root; `--slots` and `SDLC_GATE_SLOTS` become a demand share, never a cap |
| Weight | One slot per command: a three-worker Playwright run and a `tsc` cost the same | Vector `(compute_units, browser_jobs)` derived from a workload class | Agree on vector demand, all or none. Counter on classes: the caller declares the vector; a resource absent from the policy is uncapped. Classes wait for calibration |
| Worker hint | `SDLC_GATE_WORKERS = max(1, cpus // slots)`, advisory; maison hardcodes `workers: 3` and never reads it | Effective workers must equal the grant | Agree. `SDLC_GATE_WORKERS` is the granted compute units; the repo guard enforces it |
| Waiting | Poll every 0.2 s with no queue: random barging | FIFO per repo, round robin across repos, no backfill | Agree, run by whoever holds the mutex, no daemon |
| Liveness | Wrapper pid, start reconstructed from `ps` elapsed time with 5 s slack (`proc_start` line 68, `holder_alive` line 86) | Exact owner and payload identity, boot id | Agree. Exact start identity compared for equality; boot id; the command's process group keeps the charge after the wrapper dies |
| Wrapper death | Slot stolen as soon as the wrapper pid is dead, while the child group may still run | Charge held until the workload is proven gone | Agree, by process group membership |
| Leader exits first | Slot released; group members left running (`run`, line 216 kills only when the immediate child is alive) | Drain before release | Agree: drain the group, then release |
| Spawn window | Not handled | Start-barrier helper that never execs if the wrapper dies before registration | Defer (section 8) |
| Nesting | `SDLC_GATE_LOCK_HELD=1` trusted (line 176) | Opaque capability token, one synchronous child, siblings fail | Counter: grant id plus same process group check; siblings share as today |
| Timing | One "got a slot after Ns" stderr line | Six monotonic measures and a versioned event stream | Counter: four monotonic measures in an optional JSON receipt |
| Failure | Timeout exits 3; `SDLC_GATE_SLOTS=0` and `--no-gate-lock` run bare | Required mode fails closed; no production escape | Split: the plugin fails closed on its own errors; the explicit opt-out stays; "required" is a repo entry-guard choice |
| Coverage | Only fanout integration gates use it (`gate_argv`); `run.sh`, `dispatch.py`, role shell checks, and repo test entries do not | Repo entry guards on every heavy path | Agree; repo-owned (section 7) |
| Reap | Manual `reap` by process name and orphan parent | Never used for lease recovery | Agree: unchanged, never called by admission |

What the evidence supports about the load false reds (load 20 to 57 on 20 logical CPUs in the maison retro): the only admitted path is the fanout integration gate, so role-run checks and direct `npm test` or `npx playwright test` runs were never admitted; maison runs three workers per invocation regardless of `SDLC_GATE_WORKERS`; and one slot per command ignores weight. A TMPDIR split is plausible (sandboxed hosts and selftests set their own TMPDIR) but was not observed. How much of the load each cause produced was not measured. Coverage of repo entries is therefore the largest lever, and it is repo-owned.

## 4. Interface (protocol `sdlc-gate/2`)

All commands keep `gate_lock.py` as the implementation. Existing `run` syntax stays valid.

| Command | Purpose |
|---|---|
| `run [--need RES=N[,RES=N...]] [--slots N] [--name X] [--repo PATH] [--nice] [--timeout SECS] [--receipt FILE] -- <cmd...>` | Queue, wait for a grant, run the command in its own process group, drain the group, release. The normal client operation, unchanged for callers that pass no new flag |
| `context [--json]` | Exit 0 and print the grant (id, need, repo, `SDLC_GATE_WORKERS`) when the calling process runs inside a valid grant; exit 1 otherwise. For repo entry guards; grants nothing |
| `capabilities --json` | Read only: protocol, state root, boot id, policy in force (file or built in), resources, legacy holders seen |
| `status [--json]` | Grants, queue, orphaned groups, legacy holders. Human text as today without `--json` |
| `policy show`, `policy set RES=N... [--default RES=N...]`, `policy reset` | Operator only, under the mutex. Never a caller flag |
| `reset --confirm` | Operator only: replaces an unparseable ledger with an empty one, keeping the old file beside it. Refused while the ledger parses |
| `reap`, `selftest` | Unchanged in purpose; `reap` is never called by admission |

Environment given to the command: `SDLC_GATE_GRANT=<grant id>`, `SDLC_GATE_WORKERS=<granted compute_units>`, `SDLC_GATE_DIR=<state root>` (so nested clients resolve the same root even with an override), and `SDLC_GATE_LOCK_HELD=1` (kept only so old nested clients skip, section 6).

Environment read: `SDLC_GATE_DIR` (test or isolated namespace override), `SDLC_GATE_SLOTS` (0 or below runs bare, the explicit unprotected opt-out as today; N of 1 or more is a demand share), `SDLC_GATE_REPORT_SECS` (unchanged).

Exit status: the command's own status, 128 plus a signal, 127 or 126 when the command cannot start, all unchanged. Every admission failure exits 3 with one first stderr line `gate_lock: <code>: <detail>`. The wait timeout keeps today's `gate_lock: timeout after ...` text, which `fanout.py` and its docs rely on. Codes: `timeout`, `too_large`, `bad_context`, `state_unavailable`, `ledger_corrupt`. Exit 3 can also be a child's own status, so a caller that must tell them apart reads the receipt's `outcome`.

Receipt (`--receipt FILE`, JSON, written last): `protocol`, `grant`, `name`, `repo`, `need`, `outcome` (`ok`, `child_failed`, `signal`, `spawn_failed`, or an admission code), `rc`, `wait_ms`, `run_ms` (null when the command never started), `cleanup_ms`, `total_ms`. Durations come from the monotonic clock; one UTC timestamp (`enqueued_at`) is kept for correlation only.

## 5. State, policy, and admission

### State root

`$SDLC_GATE_DIR` when set, else `<home>/.local/state/sdlc-lite/gate-lock/`, where `<home>` is the account's home directory from the password database (`pwd.getpwuid(os.getuid())`). Environment-derived paths are rejected as the default because they are what split the namespace today. Scope is one OS user on one host; a home on a network filesystem shared by several hosts is unsupported and not detected in v1. Other OS users and commands that never call the authority are outside the guarantee; they consume headroom.

Files: `.mutex` (the existing short `flock`), `ledger.json` (replaced atomically: write a temp file, fsync, rename, all under the mutex), optional `policy.json`, and the launcher if the discovery decision adopts it (section 7). A state root that cannot be created or written fails closed with `state_unavailable`; there is no fallback to TMPDIR and no bare run.

### Ledger

`ledger.json` holds `protocol`, `boot` (the boot id), `seq`, `rr` (the repo granted last), `grants`, and `queue`. Each entry: `id` (128 random bits, hex), `seq`, `repo`, `name`, `cmd` (first 200 characters), `need`, `pid`, `pid_start`, `pgid` (null until spawned), `enqueued_at`, and a `granted` flag for queue entries promoted by another process. A ledger whose `boot` differs from the current boot id is from before a reboot: every entry in it is dead and the ledger starts empty. An unparseable ledger fails closed with `ledger_corrupt` (atomic rename makes this a disk fault, not a race); `status` names it, and recovery is the operator's `reset --confirm` after checking that no gate runs. No live entry is ever forgotten automatically.

### Policy

`{"capacity": {"compute_units": C, "browser_jobs": B}, "default_need": {"compute_units": D}}`, every field optional. With no policy file the built-in default is `default_need` of `max(1, cpus // 2)` compute units, `compute_units` capacity of twice that (the logical CPU count on an even count), and no `browser_jobs` cap. That reproduces today's default on every host: two undeclared gates run at once and each gets `SDLC_GATE_WORKERS = max(1, cpus // 2)`. Any other value (the proposal's 6 and 3, a browser-job cap, per-class weights) is a policy change that needs calibration from real runs and the maintainer's approval, applied with `policy set`.

- A run with no `--need` asks for `default_need`. `--slots N` or `SDLC_GATE_SLOTS=N` (N of 1 or more) asks for `max(1, cpus // N)` compute units, the worker share `SDLC_GATE_WORKERS` gives it today. How many such runs fit together follows from the shared capacity, not from N, so neither can raise capacity.
- A need above capacity in any capped resource fails at once with `too_large`; nothing shrinks it silently.
- A need naming a resource the policy does not cap is recorded and not charged, so a repo can declare `browser_jobs=1` before a browser cap exists.
- A policy change applies at the next scheduling decision. A reduction never stops a holder; new grants wait until usage fits.

### Admission

1. Under the mutex: prune, enqueue this run, schedule, read its own state. Release the mutex.
2. Poll every 0.2 s, repeating step 1 without the enqueue, until granted, timed out, or signalled. Report progress on stderr every `SDLC_GATE_REPORT_SECS`, now with the queue position.
3. Granted: spawn the command in a new session, then record its `pgid` under the mutex. Wait.
4. Child exit: drain the group (SIGTERM, 5 s, SIGKILL) until `killpg(pgid, 0)` reports no member, then remove the grant and schedule, under the mutex.

Prune removes queue entries whose waiter is dead and grants that are dead (below). Schedule orders the repos with queued entries cyclically by first appearance, starts at the repo after `rr`, and offers that repo's oldest entry. If its need fits every capped resource, it is granted on the owner's behalf, `rr` moves, and the next repo is offered. If it does not fit, scheduling stops: no backfill, so the selected entry keeps its turn until enough work drains. This is admission-turn fairness, not equal CPU time.

Repo identity is the real path of `git rev-parse --git-common-dir` from the caller's cwd (shared by all worktrees of a repo), the real cwd outside git, or `--repo`.

A signal while queued removes the queue entry and exits 128 plus the signal with no child. A signal while running kills the group as today, then releases only when the group is empty. The wait timeout removes the queue entry and exits 3. gate_lock adds no execution timeout; callers keep their own and start it after admission.

### Liveness and identity

- A grant stays charged while its wrapper is alive with the recorded start identity, or while its process group has any member (`killpg(pgid, 0)` does not fail with ESRCH). A dead wrapper with a live group stays charged and is shown as an orphaned group; admission never kills it.
- A queue entry is live while its waiter is alive with the recorded start identity.
- Start identity: macOS `proc_pidinfo(PROC_PIDTBSDINFO)` start seconds and microseconds through ctypes, checked on this host; fallback `ps -o lstart=`; Linux `/proc/<pid>/stat` field 22, unverified here. Compare for equality, with no slack. A pid that `kill(pid, 0)` reports alive but whose identity cannot be read counts as alive.
- Liveness must not spawn one `ps` per holder per poll, as `proc_start` does today: with twenty waiters that load is part of the problem.
- Known limits, all in the safe direction or named: a reused pgid holds a charge longer than needed; descendants that leave the group (setsid, detached process groups such as maison's `harness.check.mjs`) are not tracked, so the repo must keep heavy work in the gate's group or admit each detached group with its own top-level `run`.

## 6. Nesting

- A `run` that sees `SDLC_GATE_GRANT` checks under the mutex that the grant exists, is live, and that the caller's own process group equals the grant's `pgid`. Valid: it runs its command in the same group (no new session, so deeper nested runs still validate; on a signal it therefore signals its child's pid, not a group of its own), with no queue entry and no new charge; `SDLC_GATE_WORKERS` is the smaller of its own need and the grant's. A need above the grant's fails with `too_large`. Invalid (unknown or dead grant, another group): `bad_context` before the command starts; no silent reacquire.
- `SDLC_GATE_LOCK_HELD=1` without `SDLC_GATE_GRANT` (an old parent, or a variable leaked into a terminal) is a top-level request in the new namespace. An old parent holds capacity only in the legacy domain, so this cannot deadlock against itself.
- Concurrent nested siblings inside one grant share it, as today; the parent's declared need must cover its own internal parallelism. The proposal's one-synchronous-child rule with sibling failure is deferred: it breaks gates that run sub-steps in parallel today, and no run has shown siblings oversubscribing.

## 7. Owner split

| Owner | Owns |
|---|---|
| Plugin (`gate_lock.py`) | State root, policy, ledger, queue and fairness, vector grants, liveness and identity, process-group drain, nesting validation, `context`, `capabilities`, receipts, the legacy bridge, the launcher if adopted, selftests with negative controls |
| Plugin (`fanout.py`, docs, checks) | `gate_argv` keeps wrapping every gate (optionally passing `--receipt` into the lane log dir); the conductor rule, the `fanout.py` docstring (lines 191 to 193), the sdlc-internals entry, and check.py item 35 updated in the same change |
| Repo (maison) | A transport-only client that calls the plugin; every heavy entry (npm test, focused gate, full gate, direct standard-config Playwright, the exported harness entry) either runs inside a valid grant or wraps itself in one before its first side effect; Playwright workers set from `SDLC_GATE_WORKERS`, conflicting values refused; admission before `prepareHarnessFixtures`; no detached heavy group outside the grant; the host grant taken before the same-worktree data lock and never awaited while holding it; whether its entries are required (fail without a grant) or self-wrapping |
| Maintainer and user | The policy numbers after calibration, the client discovery mechanism, retiring maison's three-verifier containment after a discriminating rerun |

Client discovery is a decision item. Recommendation: every `run` refreshes a stable launcher at `<state root>/bin/gate-lock` that execs the newest installed `gate_lock.py` that has run on the host (newest by plugin version, so two versions do not flip it), and `gate_lock.py install` writes it on demand. A repo client calls that fixed path; before any plugin run it does not exist, and a required entry fails with a provisioning message rather than running bare. Hosted CI provisions the plugin first or stays unprotected by explicit choice.

## 8. Deferred and not adopted

| Proposal item | Status | Brought back when |
|---|---|---|
| Start-barrier helper for the fork-before-registration window | Deferred. The grant is recorded with the wrapper identity before the spawn and the `pgid` right after; only a SIGKILL of the wrapper inside that millisecond window leaves one job uncharged | A run shows an uncharged job after a wrapper kill |
| Capability tokens, subgrant chains, one synchronous child, sibling failure | Deferred; grant id plus process group covers leaked and forged context for same-user cooperative clients, which the proposal itself says is not a security boundary | A run shows nested siblings exceeding the grant |
| Request UUIDs, duplicate attach, conflicting reuse | Not adopted; each wrapper is one request, and a second release finds nothing to remove | A caller needs retries of one request |
| Six measures and a versioned event stream | Reduced to four measures in a receipt | A consumer needs launch time apart from wait |
| `recovery_required` state machine and quarantine | Reduced: unknown identity counts as alive and charged; a corrupt ledger fails closed | Charges stuck by unknown identity show up in runs |
| Host id in the namespace | Not adopted; a shared network home is unsupported | A shared home is a real setup |
| Workload classes with authority-derived weights | Deferred until calibration | Calibration data exists |
| Removing `SDLC_GATE_SLOTS=0` and `--no-gate-lock` | Not adopted; they stay the explicit, unprotected opt-out, and fanout's selftest and check.py item 35 rely on them | The maintainer decides the escape must go |
| Reserving the whole vector for an undeclared gate | Not adopted; it would halve today's throughput with no evidence. Undeclared keeps today's half share | Calibration shows undeclared gates overrun |

## 9. Migration from old plugin paths

- Old installed versions (0.22.x and earlier, in the Claude and Codex plugin caches) keep using `${TMPDIR:-/tmp}/sdlc-gate-locks/slot-*` and do not see the new ledger. A running session keeps the version it loaded, so old clients live until sessions restart.
- One-way bridge: when scheduling, the new authority reads legacy slot files in its own `${TMPDIR:-/tmp}/sdlc-gate-locks` and in `/tmp/sdlc-gate-locks`, and charges each live legacy holder the `default_need`. It never deletes, steals, or signals a legacy slot or holder. Legacy holders under other TMPDIRs stay invisible; `status` and `capabilities` report legacy holders seen, and protection is called partial while any exists.
- No run holds a legacy slot and a new grant in series.
- New parents export `SDLC_GATE_LOCK_HELD=1` so old nested clients skip, as they do today.
- check.py item 35 pins `SLOT-CAP`, `SDLC_GATE_WORKERS`, `SDLC_GATE_SLOTS`, and `sdlc-gate-locks` in gate_lock.py, `gate_lock.py` and `--no-gate-lock` in fanout.py, `gate_lock.py run` in conductor.md, and `gate_lock.py` in sdlc-internals. The build keeps `sdlc-gate-locks` (the bridge reads it), moves the `SLOT-CAP` marker to the capacity comparison that the negative control removes, and adds `SDLC_GATE_DIR` and `SDLC_GATE_GRANT`, with each new phrase's negative control.
- Selftest isolation moves from TMPDIR to `SDLC_GATE_DIR`: fanout's `gate_env` (line 2139) and every gate_lock selftest case set it to a temp dir, or they would share the real user namespace. Fanout's case 21 probe reads `gate_lock.py context` instead of `cat "$TMPDIR"/sdlc-gate-locks/slot-*`.
- Codex (unverified): `run.sh` does not wrap gates, so Codex roles are admitted only through fanout or a repo entry. A Codex sandbox whose writable roots exclude the state root gets `state_unavailable` and fails closed; the Codex config may need the state root added to its writable roots. This was not run live here.
- Order: plugin release with the bridge, sessions restarted, repo client and entries landed, repo entries made required, then the discriminating rerun. Maison's three-verifier containment retires only after that rerun.

## 10. Regression cases

Every v1 case runs in a temp `SDLC_GATE_DIR` with dummy commands that write start and stop markers, never a real browser, inside the selftest's bounded time, and each has a negative control in the style the selftest already uses for `SLOT-CAP`: a copy of the script with one comparison removed must fail the case.

| Case | Status | Negative control |
|---|---|---|
| R01 weighted aggregate cap | v1, policy `compute_units=4, browser_jobs=2` | Remove the compute comparison |
| R02 independent browser cap | v1 | Remove the browser comparison |
| R03 concurrent registration, six clients, two repos | v1, repeated bounded rounds | Skip the mutex in the copy |
| R04 cross-repo fairness | v1 | Always prefer one repo |
| R05 large request keeps its turn | v1 | Enable backfill |
| R06 scope coherence: two TMPDIRs, two worktrees of one repo | v1 | Derive the root from TMPDIR |
| R07 foreign scope | v1 as a foreign boot id; host and UID tokens not adopted | Ignore the boot id |
| R08 caller cannot raise the cap; reduction keeps holders | v1 (the total charge stays within capacity whatever `--slots` says) | Let `--slots` set capacity |
| R09 dead queued owner | v1 | Leave the dead entry at the head |
| R10 wrapper dies before registration | Deferred with the start barrier | |
| R11 wrapper dies, live payload | v1 | Reclaim on wrapper death alone (today's code) |
| R12 leader exits, descendant alive | v1 | Release on leader exit |
| R13 pid reuse, including within 5 s | v1, injected identity reader | Compare pid alone, or restore the 5 s slack |
| R14 old but live owner | v1 (no age in liveness) | Reclaim by age |
| R15 unknown owner, malformed ledger | v1 (charged; fail closed) | Treat a read failure as dead |
| R16 cancel while waiting | v1 | Spawn after the signal |
| R17 grant and cancel race | v1 reduced: a signal between grant and spawn starts no child and releases; no crash-point injection | Spawn after a pending signal |
| R18 cancel while running, unrelated sentinel alive | v1 | Release before the drain, or signal the sentinel |
| R19 all or none | v1 | Charge resources one at a time |
| R20 idempotent retry | Not adopted; second release is a no-op (v1) | |
| R21 spawn failures 127 and 126 | v1, grant released | Skip release on spawn error |
| R22 valid nesting, one charge | v1; subgrant ids deferred | Charge the nested run |
| R23 nested oversize; siblings | Oversize v1; siblings deferred | Skip the need check |
| R24 stale or forged context | v1: unknown grant or another group gives `bad_context`; `SDLC_GATE_LOCK_HELD=1` alone is a top-level request, not a bypass | Trust the variable |
| R25 metering | v1 with an injected monotonic clock | Start run time at enqueue |
| R26 wait timeout never starts the payload | v1; execution timeouts are the caller's | Start the payload at timeout |
| R27 state or ledger failure | v1: no bare run, no fallback | Fall back to TMPDIR |
| R28 legacy holders | v1: counted, never touched, status says partial | Ignore legacy slots |
| R29 repo entry matrix | Repo | Per the proposal |
| R30 host grant before worktree data lock | Repo | Per the proposal |
| P01 built-in policy equals today | v1: no policy file, two undeclared runs hold, a third waits, each sees `max(1, cpus // 2)` workers | Remove the capacity comparison (`SLOT-CAP`) |
| P02 explicit opt-out | v1: `SDLC_GATE_SLOTS=0` and `--no-gate-lock` run bare with no grant | Ignore the opt-out |
| P03 reboot | v1: a ledger with another boot id is empty | Keep entries across boots |
| P04 selftest isolation | v1: the real state root is untouched by every selftest | Unset `SDLC_GATE_DIR` in the copy |

## 11. Decisions for the maintainer

1. Accept this counter-design for v1, or the proposal as written.
2. Client discovery: the stable launcher in the state root (recommended), or another mechanism.
3. Draining a group whose leader exited before release (a behavior change: today leftover members keep running after the slot is freed).
4. Keep `SDLC_GATE_SLOTS=0` and `--no-gate-lock` as the explicit opt-out (recommended) or remove them.
5. No numbers: the built-in policy keeps today's behavior until calibration from real runs; 6 and 3 stay unapproved.

## 12. Build notes (T-0409, 2026-10-09)

- Numbers: the maintainer approved capacity 6 compute units and 3 browser jobs. The built-in policy is exactly that, with a default need of 3 compute units so that two undeclared gates still run at once, as before. Section 5's built-in default (`max(1, cpus // 2)` per gate, twice that in capacity) is replaced; `SDLC_GATE_WORKERS` for an undeclared gate is 3 instead of `cpus // 2`, and `--slots N` or `SDLC_GATE_SLOTS=N` asks for `max(1, 6 // N)` compute units (N of 1 asks for all 6) instead of `max(1, cpus // N)`, because a share larger than the capacity would otherwise be `too_large` for every current caller.
- Priority: the design had none. Maison's acceptance (`codex-live-admission-followup.md`) adds it, so `run --priority P` (env `SDLC_GATE_PRIORITY`, default 0) orders the queue by highest priority, then arrival; round robin across repos applies among the repos at the top priority; a running holder is never preempted. `status` prints `admitted` and `queued` rows with the queue position and priority.
- Not built, as section 8 deferred or section 7 leaves open: the start-barrier helper, capability tokens, request ids, the event stream, workload classes, the stable launcher (`install`, decision item 2), and the repo-owned entry guards. Group drain on leader exit (decision item 3) is built as designed.

## 13. Gate weight and lock timeouts in fanout (T-0456, 2026-10-12)

The machine-wide queue is shared across repos, and the head keeps its turn until it fits (no backfill), so a default-need gate (3 compute units) can wait the full 1800 s behind a peer's browser jobs while a check that needs one core would have fit. T-0446 and T-0450 went `red: ... generate --check rc=3` that way: rc 3 is the lock's `gate_lock: timeout` line, the command never ran, and it exits 0 on its own. The capacity (6 and 3) and the default need are unchanged; `fanout.py` changes how it asks and how it reports:

- Weight. A cheap gate asks for `--need compute_units=1`. A gate is cheap when its command has `check.py` or `check-packaging.py` as a word, or is `claude_roles.py` or `codex_roles.py` `generate --check`. `--gate-need [PREFIX::]RES=N[,RES=N...]` (on `run`, `prep`, `land`, `roll`; repeatable) sets the need of the gates whose command starts with PREFIX (every gate when PREFIX is omitted); the first matching spec wins over the cheap default, and a spec naming no browser resource leaves the gate uncharged for it. Heavy gates (`check.sh`, `npm test`, browser shards) keep the default need.
- Wait limit. `SDLC_GATE_TIMEOUT=SECS` in fanout's environment becomes `--timeout SECS` on each gate's `gate_lock.py run` (unset: the lock's 1800 s default).
- Report. Gate rc 3 with the `gate_lock: timeout after Ns` line in the log is never `red`: the gate is run once more (a new `a<n>` log), and a second timeout resets the merge and ends the ticket as `gate waited N s for a slot, not run: <gate>`, so the lane can land again. A gate command that exits 3 on its own has no such line and stays `red: <gate> rc=3`.
