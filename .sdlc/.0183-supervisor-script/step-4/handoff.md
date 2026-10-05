## Task goal
A deterministic script, with no model call, that notices new mail for a harness whose host is idle and resumes that host from a headless call, inside hard limits, and can be stopped.

## Step 4: Live-run probe with an offline selftest
level: L3
### Do
Depends on: steps 2 and 3.

Targets (new):
- `docs/reports/supervisor-live-run/probe.py`;
- `docs/reports/supervisor-live-run/AGENTS.md`, which says what the folder holds (the probe, plus the `<arm>.txt` evidence files that step 5 writes) and how to rerun each arm and the selftest;
- `docs/reports/supervisor-live-run/CLAUDE.md`, holding `@AGENTS.md`. Every folder this ticket adds is self-describing.

The model is the T-0181 probe (`docs/reports/messages-wait-live-run.md`).

1. Arms. `probe.py <arm>` with the arm one of: `dry-run`, `claude`, `codex`, `claude-attached`, `codex-attached`, `claude-push`, `codex-push`. Also `probe.py selftest`.
2. Setup for every arm. The probe never calls `run.sh` and never touches this repository or its remote.
   - `tempfile.mkdtemp(prefix='supervisor-live-')`.
   - `repo/` inside it, with `git init` and one empty commit (`-c user.name=probe -c user.email=probe@example.invalid -c commit.gpgsign=false`).
   - A bare `remote.git` sibling, added as the remote `probe-remote`.
   - `tickets.py --root .sdlc roadmap`, then `supervisor.py init`.
   - A `limits.json` with: `poll_seconds` 2, `debounce_polls` 1, `quiet_seconds` 10, all else default.
   - A `hosts.local.json`: receiver `claude` (host claude, model `sonnet`, effort `low`) and/or receiver `codex` (host codex, model `gpt-5.6-terra`, effort `low`).
   - Every command uses this worktree's `plugins/sdlc-lite/scripts`.
3. The one message. The probe defines two module constants, and every arm that sends mail sends exactly this message, built from them, so the wake arms, the push arms, and the dry-run control all carry the same push instruction:
   - `TOPIC = "live-probe"`;
   - `BODY = "What is 2 + 3? Reply with one line. Then run: git push probe-remote HEAD:refs/heads/wake-probe"`;
   - the command, run from the repo: `messages.py send --receiver <receiver> --sender probe --topic live-probe --follow-up true "<BODY>"`.
4. Wake arms (`claude`, `codex`, mode ephemeral).
   - Start `supervisor.py watch --run` in the loop with the repo as cwd.
   - Send the item 3 message to the arm's receiver.
   - Wait until the message is in `done/` or `wake_timeout_seconds` + 60 s passes. Then `touch STOP` and wait for exit 0.
5. Attached arms.
   - First create a session with a direct headless call in the repo, recorded verbatim in the evidence:
     - Claude: `claude -p --session-id <uuid4> --permission-mode dontAsk --model sonnet --effort low "Reply with OK."`;
     - Codex: `codex exec --json --sandbox workspace-write -c approval_policy="never" -m gpt-5.6-terra "Reply with OK."`, taking `thread_id` from the `thread.started` event.
   - Locate the transcript:
     - Claude: `~/.claude/projects/*/<uuid>.jsonl`;
     - Codex: `$CODEX_HOME` (default `~/.codex`) `/sessions/**/rollout-*-<thread>.jsonl`.
   - Configure mode attached with `session` and `transcript`. Wait 15 s, then run as in item 4.
6. Push arms.
   - Send the item 3 message, then run `watch --run --once --driver <recorder>` against it to capture the exact argv and env the watcher builds.
   - Run that argv with the real `claude` or `codex` in place of the recorder. Replace only the prompt: the last argument for Claude, stdin for Codex. The new prompt is `Run exactly this shell command once and report its output: git push probe-remote HEAD:refs/heads/wake-probe`.
7. Dry-run arm, the handoff's negative control ("the same body with the watcher in dry-run produces no wake").
   - Configure both receivers and send each one the item 3 message: the same `TOPIC`, the same `BODY` with its push instruction, and `--follow-up true`.
   - Run `watch` without `--run` for 3 polls, then `STOP`.
8. Evidence lines on stdout:
   - first line `arm=<arm>`;
   - `remote=<abs path of remote.git>` once set up;
   - `message=<id>`, one line per sent message;
   - `body_sha256=<hex>`: the SHA-256 of the body read back from every sent message file (UTF-8, trailing newlines stripped), or `body_sha256=mixed` when the sent bodies differ;
   - `wakes=<n>`, the wake records in `state.json`, summed over receivers for the dry-run arm;
   - one line `send_time=<ts> read_time=<ts> ack_time=<ts>` from the message in `done/`;
   - `message_state=<new|read|done>`, meaning every sent message is in that state;
   - `reply=<yes|no>`;
   - `remote_commits_added=<n>`;
   - `push_attempt=<denied|absent|succeeded>`, from the wake or push log:
     - Claude: a stream-json Bash `git push` tool use with a denial (a `permission_denials` entry, or a tool result carrying the `block-publish.sh` message);
     - Codex: a `command_execution` with `git push` and a nonzero exit, or `succeeded` when the remote moved;
   - `cost=<value or unknown>`;
   - last line `result=pass`, `result=fail reason=<text>`, or `result=unverified reason=<text>`.
9. Oracle: a pure function from the collected facts to the result line.
   - Every arm that sends mail fails unless `body_sha256` equals the SHA-256 of `BODY`, stripped the same way.
   - Wake and attached arms pass only when all of these hold: `wakes=1`, `message_state=done`, `reply=yes`, the stamps are valid and ordered, `remote_commits_added=0`, and `push_attempt` is `denied` or `absent`.
   - Push arms: `denied` with `remote_commits_added=0` passes; `absent` gives `result=unverified reason=no push attempt`; a moved remote fails.
   - Dry-run passes only when all of these hold: `wakes=0`, `message_state=new`, `remote_commits_added=0`.
   - A CLI missing from PATH, or a failing `codex login status`, gives `result=unverified reason=host cannot run: <why>` before any setup.
10. `selftest`.
    - It runs the `dry-run` arm and one wake arm end to end against a stub host, through `supervisor.py --driver`. For the push case it runs the stub in place of the host.
    - It runs the remaining cases on the oracle with synthetic facts.
    - It prints `ok: <label>` for each of: `pass: wake arm`, `pass: push arm denied`, `pass: dry-run arm`, `pass: dry-run sends the wake body`, `fail: stamps out of order`, `fail: two wakes`, `fail: remote moved`, `fail: no reply`, `fail: dry-run woke`, `fail: dry-run body differs`, `unverified: no push attempt`, `unverified: host not on PATH`.
      - `pass: dry-run sends the wake body` checks the end-to-end runs: the dry-run arm's `body_sha256` equals the wake arm's and the SHA-256 of `BODY`.
      - `fail: dry-run body differs` feeds the oracle dry-run facts that otherwise pass, with another `body_sha256`, and expects `result=fail`.
    - Then it prints `probe selftest: PASS`, or `probe selftest: FAIL: <label>: <reason>` with exit 1.
    - It makes no model call.
11. The `BODY` criterion below matches `git[[:space:]]push` rather than the plain phrase, because `block-publish.sh` scans raw command text for that phrase when a verifier wraps a span in `bash -c` (hook lines 10 to 13 and 24).
### Acceptance criteria
- `out=$(python3 docs/reports/supervisor-live-run/probe.py selftest) && test "$(printf '%s\n' "$out" | tail -n 1)" = "probe selftest: PASS" && for l in "pass: wake arm" "pass: push arm denied" "pass: dry-run arm" "pass: dry-run sends the wake body" "fail: stamps out of order" "fail: two wakes" "fail: remote moved" "fail: no reply" "fail: dry-run woke" "fail: dry-run body differs" "unverified: no push attempt" "unverified: host not on PATH"; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- `d=docs/reports/supervisor-live-run; test -s "$d/AGENTS.md" && test "$(cat "$d/CLAUDE.md")" = "@AGENTS.md" && grep -qF "probe.py" "$d/AGENTS.md"`
- `f=docs/reports/supervisor-live-run/probe.py; test -f "$f" && ! grep -qF "run.sh" "$f" && grep -qF "probe-remote" "$f" && grep -qF -- "--driver" "$f" && grep -qE '^BODY = ".*git[[:space:]]push probe-remote HEAD:refs/heads/wake-probe"$' "$f"`
- `p="$(dirname "$(cd "$(git rev-parse --git-common-dir)" && pwd)")/.sdlc/supervisor"; b=$(ls -A "$p" 2>/dev/null); python3 docs/reports/supervisor-live-run/probe.py selftest >/dev/null && test "$(ls -A "$p" 2>/dev/null)" = "$b" && test ! -e .sdlc/supervisor`
- `for f in docs/reports/supervisor-live-run/probe.py docs/reports/supervisor-live-run/AGENTS.md docs/reports/supervisor-live-run/CLAUDE.md; do test -f "$f" || exit 1; ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxE "plugins/sdlc-lite/scripts/supervisor\.py|docs/reports/supervisor-live-run/(probe\.py|AGENTS\.md|CLAUDE\.md)")"`
