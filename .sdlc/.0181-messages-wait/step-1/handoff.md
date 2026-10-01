## Task goal
A parent host can wait for mail with one blocking command instead of a polling subagent, and the command never claims, moves, or prints a message body.

## Step 1: messages.py wait subcommand and its selftest cases
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets: `plugins/sdlc-lite/scripts/messages.py` only. Depends on: none. The system `python3` is 3.9.6, so use no syntax newer than Python 3.9.

1. Add `cmd_wait(a)`, register it in `COMMANDS`, and add a `wait` subparser to `parser()` right after `count`.
   - Subparser: `allow_abbrev=False`, help `block until a message is in new/<receiver>/; never claims it`.
   - Flags:
     - `--receiver NAME`, help `required: the receiver`.
     - `--timeout SECONDS`, help `give up after this many seconds: an integer from 1 to 600 (default 120)`.
     - `--interval SECONDS`, help `check this often, in seconds: an integer of at least 1 (default 5)`.
   - Parse `--timeout` and `--interval` as strings (`default=None`, no `type=`). An argparse `type=int` would make a non-integer a usage error (exit 2), and the handoff requires exit 1.
2. Validate in this order. Each failure raises `Refuse`: exit 1, one `messages.py: <reason>` stderr line, nothing on stdout, nothing written.
   - The receiver goes through `arg_name(a.receiver, '--receiver')`.
     - A missing receiver gives `--receiver is required` (`need`, messages.py:720-723).
     - A bad receiver gives `--receiver must match ...` (messages.py:726-731).
   - The timeout (default `'120'`) must fullmatch `[0-9]{1,9}` and lie from 1 to 600. Otherwise the reason is `--timeout must be an integer from 1 to 600: <short(value)>`.
   - The interval (default `'5'`) must fullmatch `[0-9]{1,9}` and be at least 1. Otherwise the reason is `--interval must be an integer of at least 1: <short(value)>`.
   - The 9-digit cap copies `TTL_RE` (messages.py:181) and keeps `int()` under Python 3.11's digit limit. There is no other interval maximum, because each sleep is `min(interval, time left)`.
3. Add a helper `wait_ready(mbox, receiver)`. It returns a list of `(mid, path)`, sorted by id, with `path = msg_path(mbox, 'new', receiver, mid)`. It holds one entry for each `mid` in `message_ids(os.path.join(mbox, 'new', receiver))` whose `load_or_none(path, 'new', receiver)` is not None.
   - It catches `Refuse` per file and skips that file, so a malformed file never wakes a waiter and never makes `wait` exit 1.
     - Evidence: `load` raises `Refuse` on an invalid file (messages.py:413-420).
     - Reusing `load_or_none` bare, as `count` does, would make `wait` exit 1, and `case_malformed` asserts that `count` refuses. Handoff case 5 says `wait` ignores the file.
   - `path` never goes through `realpath`, so it equals the path `send` prints for the same mailbox. `mailbox()` makes the path absolute without resolving symlinks (messages.py:443-456), and a macOS `mktemp -d` path is a symlink.
   - `count` itself is not changed (a non-goal).
4. `cmd_wait` holds exactly one line with the literal text `ready = wait_ready(mbox, receiver)`, inside its loop. The negative control patches that line. The loop works on a `time.monotonic()` deadline:
   - It checks at once, before any sleep. When `ready` is non-empty, it calls `emit` with one `<id>\t<path>\n` line per entry, in sorted order, and returns 0.
   - Otherwise, once the deadline has passed, it calls `emit('no new messages\n')` and returns 3.
   - Otherwise it runs `time.sleep(min(interval, remaining))` and loops.
   - A missing mailbox creates nothing.
   - `wait` never calls `claim`, `write_entries`, `deliver`, `write_replace`, or `Lock`, and never prints front matter or a body.
   - `main` already returns the command's code, so exit 3 needs no other change.
5. Update the module docstring:
   - Usage: after the `count` line, add `messages.py [--root DIR] wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]`.
   - Exit paragraph: add `Exit 3 only when wait times out.`
   - Commands: add a `wait` entry after `count` that says:
     - It checks new/<receiver>/ every --interval seconds (default 5, at least 1) for up to --timeout seconds (default 120, 1 to 600).
     - It prints `<id>\t<absolute path>` per valid message, sorted by id, and exits 0. At the timeout it prints `no new messages` and exits 3.
     - It skips an invalid file. It never claims, moves, writes, stamps, or prints a body.
   - Schema paragraph: "Every subcommand validates every message file it opens or counts" becomes "Every subcommand except wait validates every message file it opens or counts". After that sentence add `wait skips an invalid file instead.`
   - Layout: the sentence "list, count, and expire on a missing mailbox create nothing" (line 74-75) also names `wait`.
   - The `add_subparsers` metavar becomes `{send,list,read,ack,reply,expire,count,wait,selftest}`.
6. Add seven selftest functions in the existing `Harness`/`Box` style and append them to `SELFTEST_CASES` with exactly these labels. Use timeouts of 1 to 3 seconds, except case 2's 10 seconds. Kill any child process still running in a `finally`.
   1. `wait: a present message returns at once, state unchanged`
      - Put the body in `st_wait_present(h)`, which raises `SelftestFail`. It runs `mid, path = b.send()`, then `before = b.snap()`, then `b.run('wait', '--receiver', 'bob', '--interval', '5', '--timeout', '3')` timed with `time.monotonic()`.
      - Assert in exactly this order, each check with its own `st_fail` message:
        - (a) exit 0, else `wait exited <code>: <stderr>`;
        - (b) under 2 s, else `wait took <s> s`;
        - (c) stdout exactly `f'{mid}\t{path}\n'`, else `wait printed <stdout>`;
        - (d) `b.snap() == before`, else a message that starts with `wait changed the mailbox`, followed by the paths that differ;
        - (e) `b.only(mid, 'new', 'bob')`;
        - (f) the file's `read_time` is empty.
   2. `wait: wakes on a message sent mid-wait`
      - Start `subprocess.Popen` on `wait --receiver bob --timeout 10 --interval 1` (cwd `b.repo`, env `h.env`). Sleep about 1.5 s, then run `mid, _ = b.send()`.
      - Assert it exits 0 within 10 s of its start and that the first tab-separated field of its stdout is `mid`.
   3. `wait: timeout exits 3, state unchanged`
      - On a box holding a message for carol only (`b.send(receiver='carol')`), take `b.snap()`, then run `wait --receiver bob --timeout 1 --interval 1`.
      - Assert exit 3, stdout exactly `no new messages\n`, and `b.snap()` unchanged.
   4. `refused: wait with a bad receiver, timeout, or interval`
      - First run `b.send()`, a message for bob, so a `wait` that wrongly accepts a value exits 0 at once instead of blocking.
      - Then make exactly these seven calls:
        - `b.refused('wait', want='--receiver is required')`
        - `b.refused('wait', '--receiver', 'Bob', want='--receiver must match')`
        - `b.refused('wait', '--receiver', 'bob', '--timeout', '601', want='--timeout must be an integer from 1 to 600')`
        - the same call with `'0'` in place of `'601'`
        - the same call with `'1.5'` in place of `'601'`
        - `b.refused('wait', '--receiver', 'bob', '--interval', 'abc', want='--interval must be an integer of at least 1')`
        - the same call with `'0'` in place of `'abc'`
      - Every call after the second passes `--receiver bob`, so the timeout and interval branches are reached, and `want` (`Box.refused`, messages.py:1116-1131) pins which branch refused.
   5. `wait: ignores a malformed file and another receiver`
      - Run `b.put('bob', '20260101T000000000000Z-alice-garbage', b'not a message\n')` and `b.send(receiver='carol')`.
      - Run `wait --receiver bob --timeout 1 --interval 1`. Assert exit 3 and stdout exactly `no new messages\n`.
      - Then run `mid, path = b.send()` and `wait --receiver bob --timeout 3 --interval 1`. Assert exit 0 and stdout exactly `f'{mid}\t{path}\n'`, which excludes the garbage id.
   6. `wait: never prints a body`
      - Send a body holding a unique marker. Assert that `wait` exits 0 and that neither its stdout nor its stderr holds the marker.
   7. `wait: a claiming wait is caught`
      - Build the anchor string from two pieces (`'ready = wait_' + 'ready(mbox, receiver)'`), so the source holds the whole anchor only in `cmd_wait`. Assert the anchor occurs exactly once in this file's source.
      - Create a fresh folder under `h.tmp` and write the source there as `messages.py`, with the anchor replaced. The replacement is the anchor followed, on the same line after `; `, by a list comprehension. For each `(m, p)` in `ready`, the comprehension calls `os.makedirs(os.path.join(mbox, 'read', receiver), exist_ok=True)` and `claim(p, msg_path(mbox, 'read', receiver, m))`. Keeping it on one line keeps the indentation valid.
      - Create a second fresh subfolder of `h.tmp` and build a second `Harness` on it, so its `repo-<n>` folders cannot collide with `h`'s. Set its `me` to the patched copy.
      - Run `st_wait_present` on the second harness inside a `try`.
        - `except SelftestFail as e`: when `str(e)` does not start with `wait changed the mailbox`, call `st_fail(f'the claiming copy failed another check first: {e}')`. Otherwise the case passes.
        - `else`: call `st_fail('the state check passed a wait that claims the message')`.
      - So the case passes only when the state-unchanged check (d) fired. A patched copy that crashes fails check (a), and then this case fails. The patched copy prints the `new/` path, because the path is computed before the claim, so checks (a) to (c) hold and (d) is the first check to fire.

Focused check: `python3 plugins/sdlc-lite/scripts/messages.py selftest`.

Contract dependents:
- `case_entry_parses` pins the set of subcommands the entry files run (messages.py:1729). This step leaves `ENTRY_TEMPLATE` unchanged, so `want` stays correct; step 2 changes both together.
- `run.sh` calls only `count` (run.sh:236), which is unchanged.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/messages.py selftest) && printf "%s\n" "$out" | grep -qxF "messages selftest: PASS" && for l in "wait: a present message returns at once, state unchanged" "wait: wakes on a message sent mid-wait" "wait: timeout exits 3, state unchanged" "refused: wait with a bad receiver, timeout, or interval" "wait: ignores a malformed file and another receiver" "wait: never prints a body" "wait: a claiming wait is caught"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && p=$(python3 $S --root "$d" send --receiver bob --sender alice --topic t --follow-up false hi) && id=$(basename "$p" .md) && before=$(cat "$p") && s=$SECONDS && out=$(python3 $S --root "$d" wait --receiver bob --interval 5 --timeout 10) && test $((SECONDS - s)) -lt 3 && test "$out" = "$(printf "%s\t%s" "$id" "$p")" && test "$(cat "$p")" = "$before"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d); out=$(python3 $S --root "$d" wait --receiver bob --timeout 1 --interval 1); rc=$?; test "$rc" -eq 3 && test "$out" = "no new messages" && test -z "$(ls -A "$d")"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d); e=$(mktemp); for a in "--receiver Bob" "--receiver bob --timeout 601" "--receiver bob --timeout 0" "--receiver bob --timeout 1.5" "--receiver bob --interval abc" "--receiver bob --interval 0"; do f=$(printf "%s\n" $a | grep -- "^--" | tail -n 1); out=$(python3 $S --root "$d" wait $a 2>"$e"); rc=$?; test "$rc" -eq 1 || exit 1; test -z "$out" || exit 1; grep -q -- "^messages.py: $f must " "$e" || exit 1; done; test -z "$(ls -A "$d")"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && mkdir -p "$d/messages/new/bob" && printf "not a message\n" > "$d/messages/new/bob/20260101T000000000000Z-alice-garbage.md" && python3 $S --root "$d" send --receiver carol --sender alice --topic t --follow-up false hi >/dev/null && out=$(python3 $S --root "$d" wait --receiver bob --timeout 2 --interval 1); rc=$?; test "$rc" -eq 3 && test "$out" = "no new messages"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && python3 $S --root "$d" send --receiver bob --sender alice --topic t --follow-up false "BODYMARK-5e1c" >/dev/null && out=$(python3 $S --root "$d" wait --receiver bob --timeout 2 --interval 1 2>&1) && test -n "$out" && ! printf "%s\n" "$out" | grep -qF "BODYMARK-5e1c"`
- `h=$(python3 plugins/sdlc-lite/scripts/messages.py wait --help) && printf "%s\n" "$h" | grep -qF -- "--timeout" && printf "%s\n" "$h" | grep -qF -- "--interval"`
- `grep -qF "wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]" plugins/sdlc-lite/scripts/messages.py`
- `test "$(grep -cF "wait changed the mailbox" plugins/sdlc-lite/scripts/messages.py)" -ge 2`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/messages.py)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/messages.py)"`
