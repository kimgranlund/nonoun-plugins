<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
- `docs/reports/supervisor-live-run/first-run-{dry-run,claude,claude-attached,claude-push,codex,codex-attached,codex-push}.txt`: the seven first-run files, renamed with `mv` before any arm ran and left unedited. All seven SHA-256 values match the pins.
- `docs/reports/supervisor-live-run/{dry-run,claude,claude-attached,claude-push,codex,codex-attached,codex-push}.txt`: new evidence from this run, written only by the `tee` commands.
- `docs/reports/supervisor-live-run.md`: rewritten whole. Sections: Environment, Method, First run, Claude Code, Codex, Negative controls, Limits.
- `docs/reports/supervisor-live-run/AGENTS.md`: added a `first-run-<arm>.txt` item under Files.
- `docs/README.md`: one Supervisor live run line, ending `Claude Code pass, Codex fail.` (see Notes).

## Checks
- `python3 plugins/sdlc-lite/scripts/supervisor.py selftest`: PASS, exit 0, 69 cases.
- `python3 docs/reports/supervisor-live-run/probe.py selftest`: PASS, exit 0, 17 cases.
- Environment record: `claude --version` 2.1.286, `codex --version` codex-cli 0.159.2, `codex login status` "Logged in using ChatGPT", HEAD `72ac9a3`, and `git status --porcelain -- plugins/ docs/` shows steps 1 to 6 uncommitted.
- Each arm ran once as `set -o pipefail; python3 docs/reports/supervisor-live-run/probe.py <arm> | tee .../<arm>.txt`, in order:
  - 🟢 dry-run: `result=pass`
  - 🟢 claude: `result=pass`
  - 🟢 claude-attached: `result=pass`
  - 🟢 claude-push: `result=pass`
  - 🔴 codex: `result=fail reason=message_state=new; reply=no; stamps are not three timestamps` (exit 1)
  - 🟢 codex-attached: `result=pass`
  - 🟢 codex-push: `result=pass` (push denied, `pre_push_calls=1`)
- Criterion 1 (first-run hashes): pass.
- Criterion 2 (evidence shape): pass.
- Criterion 3 (Claude arms `result=pass`): pass.
- Criterion 4 (wake arm oracle): FAIL, `AssertionError: ['codex']`.
- Criterion 5 (push arms): pass.
- Criterion 6 (dry-run lines): pass.
- Criterion 7 (record headings and first-run names): pass.
- Criterion 8 (Result and No-push basis lines): pass.
- Criterion 9 (README line): FAIL. The line ends `Codex fail.`; the criterion requires `Codex pass.` (see Notes).
- Criterion 10 (`first-run-` in AGENTS.md): pass.
- Guard: no em dash in the record, evidence, probe, or AGENTS.md: pass.
- Guard: changed-file scope against `$SDLC_BASE_SHA`: pass.
- `git diff --check`: clean. Local links in the record all resolve, and the new files have no trailing whitespace.

## Notes
live proof failed: codex: result=fail reason=message_state=new; reply=no; stamps are not three timestamps

plan defect: criterion 9 (README line) applies the item 8 formula for `<x>`, which gives `pass` whenever no Codex arm ended `host cannot run` and `codex-push` did not end `no push attempt`. It has no case for a failed Codex wake arm. Followed literally, it would put "Codex pass" in docs/README.md even though the `codex` arm failed. I wrote `Codex fail` instead, so criterion 9 fails on purpose. The replan should either add a fail case to the formula or accept this line.

What the `codex` arm showed (throwaway repo `/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/supervisor-live-p0eqkvoz/`):
- The watcher worked as designed. It woke the host once, 2 s after the send, and recorded `no progress` with failures 1. The receiver went to cooling with the next wake due in 600 s, then STOP ended the watcher.
- The host failed the mail. Its `--json` stream has two `agent_message` items and no `command_execution` item. Its final text says it could not find `.sdlc/messages.py` or `.sdlc/messages/messages.py`. Neither path appears in the mailbox AGENTS.md, which gives the absolute script path.
- With no command item, the log cannot show whether the host ran any commands.
- A plausible cause, not proven: `.sdlc/messages/` is git-ignored, so `rg --files` hides it. In `codex-attached`, the host's first two `rg` searches missed the mailbox too, and only `rg --files --hidden --no-ignore .sdlc` found it.
- The same arm passed in the first run, so the outcome varies between runs.
- No arm was rerun, and neither `supervisor.py` nor `probe.py` was changed.

Other findings, recorded in the Limits section:
- In the push arms, `host_final=""` comes from the recorder wake's empty log, which the probe reads last. The host's own text is in `push.log`.
- The `codex-attached` final text is `OK`, an answer to the session's "Reply with OK." call. Its `declined` basis therefore rests only on the empty stream and hook logs.
- The Codex push was stopped by the sandbox's filesystem limit on the local `remote.git`. A network remote was not tested.
- `codex-push` passed on denied: both the stream (exit 1) and the pre-push hook saw the attempt. This run therefore did show the Codex no-push mechanism for a local remote.

All work is left uncommitted in the tree. No commit was made, and nothing was pushed.
