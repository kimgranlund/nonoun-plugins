## Task goal
A deterministic script, with no model call, that notices new mail for a harness whose host is idle and resumes that host from a headless call, inside hard limits, and can be stopped.

## Step 3: supervisor.py limits: cooldown, caps, depth, active host, progress-based success, failures, and their selftest
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 2. The spec is design v0.2: D7, D8 decision order, D9 to D13, and D16.

Target: `plugins/sdlc-lite/scripts/supervisor.py` only.

1. Insert the step 3 rules into the D8 decision order. Each is its own module-level function, called by its module-level name at call time as in step 2, so a control can rebind it:
   - `failed`;
   - reply depth (D11), as two functions: re hops and wake lineage.
     - Depth counts the messages in a chain, the pending one included. A message with no `re`, or whose parent is missing or invalid, has re depth 1, and each parent followed adds 1. A chain of three messages therefore has depth 3 and meets the default `reply_depth_limit` of 3, as the handoff says: "reply-chain depth of three or more records `needs a human`".
     - Lineage is W.depth + 1 (D11).
   - own wake running, with the D12 pid identity check;
   - the stale-record handler (D12: end set to now, result per D9, `lost` counts as a failure);
   - transcript active (D12);
   - cooldown counted from the last wake start, and the D10 backoff, as two functions;
   - the hourly cap and the daily cap, as two functions over rolling windows. A cap of 0 refuses every wake.
2. Replace the step 2 result rule with D9, each piece its own function:
   - the success judge: exit 0 within the timeout and every wake-set id in `done/<receiver>/`;
   - the stranded-id tracker;
   - the timeout check, then TERM to the process group and KILL after 5 s;
   - the failure counter, which never counts `stopped`;
   - the failure stop: `failed` after `max_failures`.
3. After a wake or a notify the state is `cooling` until cooldown or backoff ends. Persist everything per D13 through one state loader function. `reset` clears `failures` and `failed`.
4. Stub driver additions:
   - it records its own pid on each call;
   - with `sleep` set it also starts one grandchild `sleep` in its own process group and records that pid;
   - `ignore_term: true` makes it ignore SIGTERM.
   - Before it removes a temp dir, the selftest sends SIGKILL to every stub and grandchild pid it recorded that is still alive, so a control that outlives its deadline leaves no process behind.
5. Selftest cases, with these exact labels, each positive case followed by its control. Controls use the step 2 helper and follow D20: each rebinds the one function of its rule and passes only when the case fails at that rule's check.
   - `cooldown: a second wake waits, status cooling`
   - `control: a copy without the cooldown wakes twice`
   - `cap: the hourly cap holds` (`max_wakes_per_hour` 2, `cooldown_seconds` 0: the third wake inside the hour is refused, state `cooling`, reason `hourly cap`)
   - `control: a copy without the hourly cap wakes past it`
   - `cap: the daily cap holds` (`max_wakes_per_day` 2, wakes more than an hour apart: the third is refused, reason `daily cap`)
   - `control: a copy without the daily cap wakes past it`
   - `cap: limits set to 0 refuse every wake` (each cap at 0 in turn)
   - `control: a copy that reads a 0 cap as no cap wakes`
   - `depth: a reply chain of three records needs a human` (state `needs a human`, reason `reply depth 3`, no call)
   - `control: a copy without the depth rule wakes`
   - `depth: a chain of two still wakes`
   - `control: a copy that counts one hop too many refuses a chain of two`
   - `depth: a wake-sent chain without re counts`
   - `control: a copy without wake lineage wakes a re-less chain`
   - `active: a running recorded wake skips the wake` (it plants a state record for a live `sleep` child it owns, with that child's lstart; state `waking`, no call)
   - `control: a copy that ignores a running wake starts another`
   - `active: a recent transcript skips the wake` (state `idle`, reason `host active`)
   - `control: a copy that ignores the transcript wakes an active host`
   - `active: a stale pid record is dropped` (a record whose pid is dead, and one whose pid is alive with another lstart: each gets an end and result `lost`, and the poll wakes)
   - `control: a copy that trusts a stale pid never wakes`
   - `failure: backoff, then failed after three` (the second retry is refused at one cooldown after the second failure and allowed at two; after the third failure the state is `failed` and no later poll calls the stub)
   - `control: a copy without the backoff wakes at the plain cooldown`
   - `control: a copy without the failure stop keeps waking`
   - `failure: exit 0 without progress counts` (result `no progress`, `failures` 1)
   - `control: a copy that trusts the exit code counts no failure`
   - `failure: a timed-out wake is killed and counts`
   - `control: a copy without the timeout kill outlives the deadline`
   - `failure: a stranded read message is retried` (stub `handle: claim`; `state.json` lists the id under `stranded`, and the next wake's prompt count includes it)
   - `control: a copy that drops stranded ids does not retry`
   - `stop: a wake ended by STOP or TERM is stopped, not a failure` (a `watch --run` loop with a stub that sleeps; once the call is recorded, `STOP` in one run and SIGTERM to the watcher pid in another: exit 0, the stub and its grandchild gone, result `stopped`, `failures` 0)
   - `control: a copy that counts stopped as a failure`
   - `reset: clears failed` (`failures` 0 and `failed` false after `reset --receiver NAME`, and the next poll wakes)
   - `control: a copy whose reset keeps failed fails the reset check`
   - `restart: counters survive a restart` (a second watcher process sees the first one's `wakes_hour`, `wakes_day`, `failures`, and cooldown)
   - `control: a copy that starts from empty state forgets the counters`
6. Selftest rules:
   - Each status case asserts the `state`, `reason`, `last_wake`, `next_wake`, `wakes_hour`, `wakes_day`, `failures`, and `pending` fields, so `cooling`, `failed`, and `needs a human` are each stamped and checked.
   - Use `--once --now` for clock control. Derive `--now` from each message's own `send_time`.
   - The lineage case runs without `--now`, because `messages.py` stamps `send_time` from the real clock and lineage compares it with wake windows.
   - The timeout case runs `watch --run --once` under a 20 s subprocess limit, with `wake_timeout_seconds` 1 and a stub that sleeps 60 s and ignores TERM. It asserts exit 0, result `timeout`, `failures` 1, and that the stub and its grandchild are gone, so both the group signal and the KILL after 5 s are proven. Its control, whose timeout check never fires, hits the 20 s limit.
   - The whole selftest stays under the 150 s target that step 2 set.
   - The step 2 cases stay green and keep their labels.

Focused check: `python3 plugins/sdlc-lite/scripts/supervisor.py selftest`.
### Acceptance criteria
- `p="$(dirname "$(cd "$(git rev-parse --git-common-dir)" && pwd)")/.sdlc/supervisor"; b=$(ls -A "$p" 2>/dev/null); out=$(python3 plugins/sdlc-lite/scripts/supervisor.py selftest) && test "$(ls -A "$p" 2>/dev/null)" = "$b" && test ! -e .sdlc/supervisor && test "$(printf '%s\n' "$out" | tail -n 1)" = "supervisor selftest: PASS" && for l in "cooldown: a second wake waits, status cooling" "control: a copy without the cooldown wakes twice" "cap: the hourly cap holds" "control: a copy without the hourly cap wakes past it" "cap: the daily cap holds" "control: a copy without the daily cap wakes past it" "cap: limits set to 0 refuse every wake" "control: a copy that reads a 0 cap as no cap wakes" "depth: a reply chain of three records needs a human" "control: a copy without the depth rule wakes" "depth: a chain of two still wakes" "control: a copy that counts one hop too many refuses a chain of two" "depth: a wake-sent chain without re counts" "control: a copy without wake lineage wakes a re-less chain" "active: a running recorded wake skips the wake" "control: a copy that ignores a running wake starts another" "active: a recent transcript skips the wake" "control: a copy that ignores the transcript wakes an active host" "active: a stale pid record is dropped" "control: a copy that trusts a stale pid never wakes" "failure: backoff, then failed after three" "control: a copy without the backoff wakes at the plain cooldown" "control: a copy without the failure stop keeps waking" "failure: exit 0 without progress counts" "control: a copy that trusts the exit code counts no failure" "failure: a timed-out wake is killed and counts" "control: a copy without the timeout kill outlives the deadline" "failure: a stranded read message is retried" "control: a copy that drops stranded ids does not retry" "stop: a wake ended by STOP or TERM is stopped, not a failure" "control: a copy that counts stopped as a failure" "reset: clears failed" "control: a copy whose reset keeps failed fails the reset check" "restart: counters survive a restart" "control: a copy that starts from empty state forgets the counters"; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/planning/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/supervisor.py)"`
