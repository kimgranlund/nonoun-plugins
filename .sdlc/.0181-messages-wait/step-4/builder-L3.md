<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/validation/messages-wait-live-run/claude.txt`: new. The probe wrote it through `tee`, live Claude arm, `result=pass`.
- `docs/validation/messages-wait-live-run/codex.txt`: new. The probe wrote it through `tee`, live Codex arm, `result=pass`.
- `docs/validation/messages-wait-live-run.md`: new dated record with Environment, Method, Claude Code, Codex and Limits sections.
- `docs/README.md`: one line added after the Messages live run line: "Claude Code pass, Codex pass".

## Checks
- `python3 docs/validation/messages-wait-live-run/probe.py selftest`: all 12 cases ok, `probe selftest: PASS`, exit 0.
- Environment commands:
  - `claude --version` printed `2.1.286 (Claude Code)`.
  - `codex --version` printed `codex-cli 0.159.2`.
  - `codex login status` printed `Logged in using ChatGPT`.
  - `git rev-parse --short HEAD` printed `bc21b53`.
  - `git status --porcelain -- plugins/` listed 3 modified files: messages.py, messenger.md, and sdlc-messenger-l1.toml.
- Claude arm, `set -o pipefail; python3 docs/validation/messages-wait-live-run/probe.py claude | tee docs/validation/messages-wait-live-run/claude.txt`: exit 0, `result=pass` (wait_calls=1 poll_calls=0, wait_before_send=yes).
- Codex arm, the same command with `codex` and `codex.txt`: exit 0, `result=pass` (wait_calls=1 poll_calls=0, wait_before_send=yes).
- Acceptance criteria 1 to 9, each run exactly as written: all PASS.
  - The first run of AC8 FAILED. The Write tool had turned the `\u2014` I typed in the Limits section into a real U+2014 character.
  - I replaced it with the literal 6 characters `\u2014` and reran AC8: PASS. AC5 and AC6 also pass again on the edited file.
- `git diff --check`: clean.
- The three relative links in the record (probe.py, claude.txt, codex.txt) all point to files that exist.

## Notes
- Each arm ran once and was not rerun. The probe, prompt, send delay and oracle were not changed.
- The raw host streams and the Codex rollout are on this machine only, not in the repo:
  - Claude: `/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-wait-live-mjp7xh_h/`.
  - Codex: `/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-wait-live-59j88hq7/`.
  - Codex rollout: `~/.codex/sessions/2026/10/01/rollout-2026-10-01T09-14-39-01a0f83f-193a-7443-876f-aa387ff555eb.jsonl`.
- Both arms ran the uncommitted step 1 and 2 changes in `plugins/`, and the record says so.
- Probe limits written under Limits:
  - Lines are cut at 160 characters, so the Codex wait command in the evidence ends at `--timeout 12`.
  - `wait_before_send` uses the time the probe received the event. The Codex rollout puts the wait cell 11.7 seconds before the send.
- `SDLC_BASE_SHA` was set to `bc21b53c14b10a42e86f467864e02bf945f26965` in the environment, and that matches `step-4/base-sha`.
