<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/supervisor.py`: this is the only file changed. Every part below is in it.
  - **Rules.** Each step 3 rule is its own module-level function, looked up by name at call time:
    - `receiver_failed`
    - `re_hops` and `wake_lineage` (depth)
    - `pid_matches` and `wake_running` (running wake)
    - `stale_result` (stale record)
    - `transcript_active`
    - `cooldown_end` and `backoff_end`
    - `hourly_cap` and `daily_cap`, which share `cap_reached`
    - D9 results: `wake_result` (success judge), `stranded_ids`, `wake_timed_out`, `count_failure`, `failure_stop`
    - `reset_receiver`
    
    `receiver_state` checks them in D8 order.
  - **State.** `load_state` is the one state loader, and it now validates `failures`, `failed`, `stranded`, and every wake record field.
  - **Watcher.** New `Watch` methods: `finish` (records the result, counts failures, applies the failure stop, updates stranded ids), `settle` (sets the state after a wake to `failed`, `cooling`, or `idle`, then recounts), `open_records` (running wakes and the stale-record handler), and `count`.
    - `reap` judges each wake by D9 and kills late ones.
    - `wait_children` no longer has its own deadline; only the timeout check ends a late wake.
    - `status.json` now fills in `next_wake`.
  - **Docs in the file.** The module docstring has a new decision table and two new sections: "Limits in the poll" and "Results and failures". The `cooldown_seconds` text that goes into the generated AGENTS.md now mentions the backoff.
  - **Selftest.**
    - Stub changes:
      - The stub is now a `/bin/sh` wrapper that runs `trap '' TERM` first when it should ignore TERM, then execs `stub.py`.
      - It records its own pid and start time on every call.
      - With `sleep` set, it starts one grandchild `sleep` in its process group and records it.
      - With `ignore_term`, it ignores SIGTERM.
      - `handle` now defaults to `ack`, and a `send_to` option was added.
    - Cleanup: after every case, and before the temp dir is removed, the selftest sends SIGKILL to each recorded pid that is still the same process (checked by start time).
    - There are 35 new cases, with the exact labels and order from the handoff, plus 18 new `CTL_*` controls.
  - **Step 2 cases.** Three were changed so they stay green and keep their labels:
    - The byte-identity case sets `handle: none`.
    - The prompt and argv cases set `cooldown_seconds` 0 and `handle: none`; the argv case also sets `max_failures` 10.

## Checks
- AC1, run verbatim: rc=0 in 71 s at load average about 4. All 35 new labels print, PASS is the last line, the main checkout's `.sdlc/supervisor` is unchanged, and there is no `./.sdlc/supervisor`.
- Guard, run verbatim: rc=0.
- Three full selftest runs: PASS in 72 s, 71 s, and a final run with 67 `ok:` lines, all 32 step 2 labels among them. That is under the 150 s target.
- Each of the 18 new controls, re-run alone with its raw reason printed: every one fails with its rule's own reason prefix, not a crash. The timeout control hits the 20 s limit (20.2 s).
- Mutations to the kill code, outside the official controls:
  - signalling only the stub's pid instead of its group: the timeout case fails ("the stub grandchild ... still runs"), and so does the stop case;
  - TERM with no KILL: the timeout case hits the 20 s limit;
  - a 1 s KILL grace: the timeout case fails because the wake ended 2.07 s after its start, short of 6 s.
- Step 2's static criteria (AC2 to AC5: greps, one main guard, no `shell=True`/`os.system`/`os.popen`/em dash, `--help` output): all rc=0.
- No trailing whitespace. The only lines over 120 characters are ones step 2 already had.
- `ps` after the runs shows no leftover selftest stubs, grandchildren, or `sleep 60` processes.
- Not run: `bash plugins/sdlc-lite/scripts/check.sh`. It is step 7's gate and this step does not require it.

## Notes
- **Where I read the spec one way:**
  - The cooling reason is null for cooldown and backoff, because D8 gives a reason only for the caps. Step 2's notify case also requires null.
  - `next_wake` is set only when the state is `cooling`: the end of the cooldown or backoff, or the moment a capped window frees up. It is null for a cap of 0.
  - Item 3 ("cooling until cooldown or backoff ends") applies even when nothing is pending: in that case the state is `cooling` while the gate holds, or `waking` while a wake runs, and only then `idle`. D8's literal first rule was simply `idle`.
  - `failed` comes after "no pending", as D8 orders it.
  - An `ok` result resets `failures`; `stopped` and `notified` leave the count unchanged.
  - Only failed wakes create stranded ids. A stopped wake does not.
  - The backoff exponent stops growing at `max_failures`, so the time arithmetic cannot overflow.
- **Additions beyond the handoff's list:**
  - Between polls, the loop reaps finished wakes every 0.1 s and rewrites the status, so in `watch --run` a late wake is killed at its deadline rather than at the next poll.
  - After a wake ends, the status recounts `new` and `pending`, so it reflects the mailbox after the wake.
- Timing was measured only at load average about 4. The plan saw load 18 to 31 on this machine. The `/bin/sh` TERM trap keeps the timeout case from depending on Python's startup time, but runtime under that load is unmeasured.
