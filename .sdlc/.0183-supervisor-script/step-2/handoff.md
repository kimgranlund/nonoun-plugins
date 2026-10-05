## Task goal
A deterministic script, with no model call, that notices new mail for a harness whose host is idle and resumes that host from a headless call, inside hard limits, and can be stopped.

## Step 2: supervisor.py core: init, config, lock, STOP, poll, wake commands, and their selftest
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1. The spec is `docs/ticket-stages/watcher-design.md` v0.2 (D1 to D21).

Targets:
- new file `plugins/sdlc-lite/scripts/supervisor.py`;
- `plugins/sdlc-lite/scripts/check.sh`.

Constraints:
- Standard library only.
- Python 3.9 compatible: the host's `python3` is 3.9.6, so no `match` and no `X | Y` annotations evaluated at runtime.
- No model call.
- Every subprocess gets an argument list. Never use `shell=True`, `os.system`, or `os.popen`.
- The file holds the line `if __name__ == '__main__':` exactly once, at the end. The selftest controls insert their rebinding right before it (D20).

1. Reuse `messages.py`, do not copy it.
   - Put `sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))`, then the exact line `import messages`, at module level.
   - Resolve the mailbox with `messages.mailbox(root)`. The supervisor folder is its sibling `supervisor` (D5).
   - Get the valid new ids with `messages.wait_ready(mbox, receiver)`. It applies `count`'s `messages.check` rule but skips an invalid file instead of exiting (messages.py:991-1003).
   - Read the front matter fields with `messages.load_or_none` and catch `messages.Refuse`.
   - Use `messages.stamp`, `messages.TS_FMT`, and `messages.valid_name`.
   - Define no function named `parse`, `check`, `load`, `load_or_none`, `wait_ready`, `mailbox`, or `message_ids`.
2. Docstring and CLI.
   - Write a module docstring in the style of `messages.py`: usage, commands, layout, limits, exit codes.
   - The argparse subcommand metavar is exactly `{init,watch,status,reset,selftest}`, with a global `--root DIR`.
   - Implement D6: `init`, `watch` with `--run`, `--once`, `--now`, and `--driver`, `status`, and `reset --receiver NAME`.
     - `reset` takes the lock non-blocking. While a watcher runs it refuses with `supervisor.py: a watcher is running; stop it first`. Otherwise it clears `failures` and `failed`.
   - `status` prints:
     - `watcher: running` or `watcher: not running` (probe with a non-blocking flock and release it at once);
     - then `status: none yet` when there is no status file, or else one line per receiver: `<receiver>\t<state>\t<pending>\t<last_wake or ->\t<reason>`.
   - The lock refusal is `supervisor.py: another watcher holds <lock path>`.
3. `init` and the files.
   - `init` writes the D5 entry files and the D7 and D15 defaults.
   - The `AGENTS.md` it writes has these sections, each with exact commands that use the absolute `{{scripts}}` path the way `messages.py` `entry_files()` renders it: `## Setup`, `## Start`, `## Stop`, `## Status`, `## Limits`, `## Files`, `## Woken hosts`.
     - `## Setup` shows one example receiver per mode.
     - `## Stop` covers `touch STOP` and Ctrl-C.
     - `## Limits` gives every D7 key with its default, floor, and cap.
     - `## Woken hosts` gives the unattended rules and the attached-mode warning.
   - Validate `limits.json` (D7) and `hosts.local.json` (D15).
4. The poll loop (D8). In this step, implement the decision order without the step 3 rules (failed, depth, active, cooldown and backoff, caps). Step 3 inserts them in D8 order.
   - Implement: debounce by `send_time`, dry-run with its stdout line, notify (D17), and `STOP` (no wake, then exit 0).
   - Kill children on exit or on TERM/INT/HUP (D12 group kill), recording `stopped`.
   - Write `status.json` with `waking` before each child starts.
   - `--once` waits for children up to `wake_timeout_seconds`.
   - Record wakes in `state.json` (D16) with `pid` and `pid_start` from `ps -o lstart= -p <pid>`, stripped.
   - Logs follow D18.
   - The wake result in this step is `ok` on exit 0, else `exit <n>`. Step 3 replaces this with D9.
5. Wake commands. Build the exact D2 argv for both hosts and both modes, the D4 prompt, and the D2 env scrub.
6. Rule functions. Each rule below lives in its own module-level function, and every caller looks it up by its module-level name at call time (no module-level table, default argument, or closure holds it), so a control that rebinds that one name in a patched copy removes exactly that rule (D20). The builder picks the names.
   - the `init` entry-file writer;
   - the `limits.json` validator and the `hosts.local.json` validator;
   - the pending count;
   - the receiver state decision, which stamps `waking` for a receiver whose wake is starting or running;
   - the dry-run gate;
   - the debounce check;
   - the prompt builder;
   - the Claude argv builder and the Codex argv builder;
   - the env scrub;
   - the mode dispatch (notify or wake);
   - the folder resolver (D5);
   - the lock taker;
   - the STOP check.
7. `selftest`, in the style of `messages.py`.
   - It runs in throwaway git repos under `tempfile.mkdtemp`. It drives `supervisor.py` and `messages.py` as subprocesses with `sys.executable`, from an env without `SDLC_*` and `GIT_*`, so it never touches the caller's repo or mailbox.
   - It prints `ok: <label>` per case, then `supervisor selftest: PASS`. On the first failure it prints `supervisor selftest: FAIL: <label>: <reason>` and exits 1.
   - Wait loops poll their condition against a deadline of at least 20 s and never rely on one fixed sleep, so host load slows the selftest without flaking it. The plan-time host ran at load average 18 to 31.
   - The stub driver is an executable Python script written into the temp dir.
     - It appends one JSON line per call to `calls.jsonl`, with argv, env, stdin, cwd, and the bytes of `.sdlc/supervisor/status.json` at call time.
     - It reads `stub.json`, which sets `exit`, `sleep`, `handle` (`none`, `ack`, `claim`, or `send`), `receiver`, and the `messages.py` path.
     - `ack` runs `messages.py` read, then reply when follow-up is requested, then ack.
   - Controls (D20). One helper runs a case function against a patched copy. It writes a copy of `supervisor.py` with one rebinding inserted right before the `if __name__ == '__main__':` line, writes a copy of `messages.py` beside it, and runs the case against that copy.
     - The control passes only when the case fails with the reason prefix of the check its rule backs, the way `messages.py` `case_wait_claim_control` requires `wait changed the mailbox`.
     - A case that passes on the copy, or fails with any other reason (a syntax error, an earlier check), fails the control with `supervisor selftest: FAIL: <control label>: <reason>`.
   - Each case checks the property its rule backs before other fields where it can, so its control fails at that check. Where a case allows it, the process under test runs `watch --once`, so a control fails fast instead of at a deadline: the second watcher in both lock cases runs `watch --once`. Keep the whole selftest under 150 s on this host, half the 300 s limit that step 7's supervisor guard runs under in `steps.py split --only`.
   - Every positive case is followed by its control. `stop: removing STOP lets a wake happen` is the handoff's own STOP negative control and pairs with `control: a copy that ignores STOP wakes`.
   - Cases, with these exact labels, in this order:
     - `init: entry files, limits, and git-ignore`: the three entry files, `limits.json` with every D7 default, `hosts.local.json` as `{"receivers": {}}`, the D5 `.gitignore` lines, and a second `init` that rewrites nothing.
     - `control: a copy whose init writes no git-ignore fails the init check` (rebinds the entry-file writer to skip `.gitignore`).
     - `config: a bad limit or host entry is refused`: an out-of-range value, an unknown key, a wrong type, an invalid receiver name, a `session` starting with `-`, and a relative `cwd` each exit 1 with one `supervisor.py: ` stderr line naming the key.
     - `control: a copy without limit validation accepts a bad limit` (rebinds the `limits.json` validator to accept anything).
     - `control: a copy without host validation accepts a bad host entry` (rebinds the `hosts.local.json` validator to accept anything).
     - `status: idle with no mail`: it plants an invalid message file (bad front matter) and a non-`.md` file in `new/<receiver>/`; the state is `idle`, `pending` 0, and no call happens. This also pins the valid-file rule shared with `count`.
     - `control: a copy that counts raw files is not idle` (rebinds the pending count to count every file name in `new/<receiver>/`).
     - `wake: one call on arrival, status waking`: one stub call, and the `status.json` bytes the stub recorded show `waking` for the receiver.
     - `control: a copy that never stamps waking fails the waking check` (rebinds the state decision to report `idle` where it would report `waking`).
     - `dry-run: no call without --run`: zero calls, the stdout line `dry-run: would wake <receiver>: 1 message(s)`, state `idle`, reason `dry-run`.
     - `control: a copy that ignores dry-run calls the host` (rebinds the dry-run gate to say run).
     - `debounce: a young message waits`: with `--once --now` set before `send_time + debounce_polls * poll_seconds`, no call and reason `debounce`; at that time, one call.
     - `control: a copy without the debounce wakes a young message` (rebinds the debounce check to always eligible).
     - `wake: the mailbox is byte-identical`: the mailbox tree, every path and its bytes, is the same before and after a wake by a stub with `handle: none`.
     - `control: a claiming copy fails the byte-identity check`.
     - `prompt: no body and no topic`: a marker planted in both the body and the topic never appears in the recorded argv or stdin.
     - `control: a topic-leaking copy fails the prompt check` (rebinds the prompt builder to add the topic).
     - `argv: claude ephemeral and attached`: the recorded argv equals the D2 list exactly, with and without `model` and `effort`.
     - `control: a copy without --max-budget-usd fails the claude argv check` (rebinds the Claude argv builder to drop that flag and its value).
     - `argv: codex ephemeral and attached`: the same for Codex, prompt on stdin.
     - `control: a copy without approval_policy fails the codex argv check` (rebinds the Codex argv builder to drop the `-c approval_policy="never"` pair).
     - `env: scrubbed, SDLC_ROLE and SDLC_HEADLESS set`: the watcher runs with `CLAUDECODE`, a `CLAUDE_CODE_*` name, an `SDLC_*` name, and `CODEX_THREAD_ID` set; the stub's env holds none of them and holds `SDLC_ROLE=supervisor` and `SDLC_HEADLESS=1`.
     - `control: a copy without the env scrub fails the env check` (rebinds the env scrub to copy the environment unchanged).
     - `notify: no call, one line`: zero calls, the stdout line `notify: <receiver>: 1 message(s) waiting`, a wake record with no pid and result `notified`.
     - `control: a copy that wakes in notify mode fails the notify check` (rebinds the mode dispatch to wake a notify receiver).
     - `lock: a second watcher exits 1, a restart succeeds`.
     - `control: a lockless copy lets two watchers run` (rebinds the lock taker to take no lock).
     - `lock: a linked worktree shares the lock`: with a watcher running in the main checkout, `init` run from a linked worktree changes nothing, and a watcher started there exits 1 naming the main checkout's lock path.
     - `control: a copy with a per-worktree folder lets two watchers run` (rebinds the folder resolver to `<git toplevel>/.sdlc/supervisor`, so the worktree's `init` writes its own config and its watcher runs).
     - `stop: STOP exits 0 with no call`: with `STOP` present before the first poll, and with `STOP` touched while the loop runs, the watcher exits 0 and the stub is never called.
     - `control: a copy that ignores STOP wakes` (rebinds the STOP check to never see the file).
     - `stop: removing STOP lets a wake happen`.
   - Each status case asserts the `state`, `reason`, `last_wake`, `wakes_hour`, `wakes_day`, and `failures` fields.
8. In `check.sh`:
   - add `python3 "$root/scripts/supervisor.py" selftest || fail=1` after the `messages.py` line;
   - in the header comment, change `traces.py, and messages.py selftests` to `traces.py, messages.py, and supervisor.py selftests`.
9. Contract dependents: none yet. T-0187 will read the D16 `status.json` format; it is not built and is not touched here. `messages.py` stays unchanged, a ticket non-goal.

Focused checks: `python3 plugins/sdlc-lite/scripts/supervisor.py selftest`, `python3 plugins/sdlc-lite/scripts/messages.py selftest`.
### Acceptance criteria
- `p="$(dirname "$(cd "$(git rev-parse --git-common-dir)" && pwd)")/.sdlc/supervisor"; b=$(ls -A "$p" 2>/dev/null); out=$(python3 plugins/sdlc-lite/scripts/supervisor.py selftest) && test "$(ls -A "$p" 2>/dev/null)" = "$b" && test ! -e .sdlc/supervisor && test "$(printf '%s\n' "$out" | tail -n 1)" = "supervisor selftest: PASS" && for l in "init: entry files, limits, and git-ignore" "control: a copy whose init writes no git-ignore fails the init check" "config: a bad limit or host entry is refused" "control: a copy without limit validation accepts a bad limit" "control: a copy without host validation accepts a bad host entry" "status: idle with no mail" "control: a copy that counts raw files is not idle" "wake: one call on arrival, status waking" "control: a copy that never stamps waking fails the waking check" "dry-run: no call without --run" "control: a copy that ignores dry-run calls the host" "debounce: a young message waits" "control: a copy without the debounce wakes a young message" "wake: the mailbox is byte-identical" "control: a claiming copy fails the byte-identity check" "prompt: no body and no topic" "control: a topic-leaking copy fails the prompt check" "argv: claude ephemeral and attached" "control: a copy without --max-budget-usd fails the claude argv check" "argv: codex ephemeral and attached" "control: a copy without approval_policy fails the codex argv check" "env: scrubbed, SDLC_ROLE and SDLC_HEADLESS set" "control: a copy without the env scrub fails the env check" "notify: no call, one line" "control: a copy that wakes in notify mode fails the notify check" "lock: a second watcher exits 1, a restart succeeds" "control: a lockless copy lets two watchers run" "lock: a linked worktree shares the lock" "control: a copy with a per-worktree folder lets two watchers run" "stop: STOP exits 0 with no call" "control: a copy that ignores STOP wakes" "stop: removing STOP lets a wake happen"; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- `f=plugins/sdlc-lite/scripts/supervisor.py; test -f "$f" && grep -qxF "import messages" "$f" && grep -qF "messages.wait_ready(" "$f" && grep -qF "messages.mailbox(" "$f" && ! grep -qE "^def (parse|check|load|load_or_none|wait_ready|mailbox|message_ids)\(" "$f"`
- `f=plugins/sdlc-lite/scripts/supervisor.py; test -f "$f" && test "$(grep -cxF "if __name__ == '__main__':" "$f")" -eq 1`
- `f=plugins/sdlc-lite/scripts/supervisor.py; test -f "$f" && ! grep -qE "shell=True|os\.system\(|os\.popen\(" "$f" && ! grep -qF "$(printf '\342\200\224')" "$f"`
- `h=$(python3 plugins/sdlc-lite/scripts/supervisor.py --help) && printf '%s\n' "$h" | grep -qF "{init,watch,status,reset,selftest}" && w=$(python3 plugins/sdlc-lite/scripts/supervisor.py watch --help) && for o in --run --once --now --driver; do printf '%s\n' "$w" | grep -qF -- "$o" || exit 1; done && python3 plugins/sdlc-lite/scripts/supervisor.py reset --help | grep -qF -- "--receiver"`
- `grep -qF 'python3 "$root/scripts/supervisor.py" selftest' plugins/sdlc-lite/scripts/check.sh && grep -qF "messages.py, and supervisor.py selftests" plugins/sdlc-lite/scripts/check.sh`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/supervisor.py)"`
