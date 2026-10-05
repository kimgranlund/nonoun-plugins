# Supervisor live run

This folder holds the live probe for `plugins/sdlc-lite/scripts/supervisor.py` (T-0183) and its evidence.

## Files

- `probe.py`: the probe. Each arm builds a throwaway git repo under the system temp dir (prefix `supervisor-live-`) with a bare `remote.git` added as the remote `probe-remote`, the mailbox, and the supervisor folder, then sends one fixed message whose body asks the host to push. It never calls the sdlc runner and never touches this repository or its remote. Every arm installs a pre-push hook in the throwaway repo, which logs each push that reaches git to `.probe-pre-push.log`, so a push is seen even when a host's event stream omits it. The docstring at the top of `probe.py` gives every arm's steps, the evidence lines, and the oracle.
- `<arm>.txt`: the stdout of one live arm (`dry-run.txt`, `claude.txt`, `codex.txt`, `claude-attached.txt`, `codex-attached.txt`, `claude-push.txt`, `codex-push.txt`), written by the live-run step. The dated record of the run is `docs/reports/supervisor-live-run.md`.
- `codex-rerun-<N>.txt` (N = 1, 2, 3): the stdout of the three `codex` arm reruns after the wake prompt fix, written with `set -o pipefail; python3 docs/reports/supervisor-live-run/probe.py codex | tee docs/reports/supervisor-live-run/codex-rerun-<N>.txt`. The record's section Codex wake arm after the prompt fix describes them; `codex.txt` stays the pre-fix run.
- `first-run-<arm>.txt`: the stdout of the first live run (2026-10-03), one file per arm, kept unchanged as the evidence for the fixes described in the record's First run section.
- `AGENTS.md`, `CLAUDE.md`: this description; `CLAUDE.md` imports it.

## Arms

| Arm | What it shows |
|---|---|
| `dry-run` | The negative control: both receivers get the same message, and `watch` without `--run` wakes nobody. |
| `claude`, `codex` | `watch --run` wakes an ephemeral host, which reads, replies, and acks the message and does not push. |
| `claude-attached`, `codex-attached` | The same for a session made first by a direct headless call and resumed in mode `attached`. |
| `claude-push`, `codex-push` | The exact wake command the watcher builds, run with a prompt that asks only for the push, is denied. |

The last stdout line is `result=pass`, `result=fail reason=<text>`, or `result=unverified reason=<text>`. Exit codes: 0 pass, 1 fail, 2 setup error, 3 unverified. A host CLI missing from PATH, or a failing `codex login status`, is unverified before any setup.

## Rerun

Run from the repository root. Each live arm calls a real model and is slow (a wake arm waits up to `wake_timeout_seconds` plus 60 s).

1. Run the offline selftest first; it makes no model call:
   `python3 docs/reports/supervisor-live-run/probe.py selftest`
   It ends with `probe selftest: PASS`.
2. Run one arm and keep its stdout as the evidence file:
   `python3 docs/reports/supervisor-live-run/probe.py <arm> > docs/reports/supervisor-live-run/<arm>.txt`
   Progress notes, including the kept throwaway repo path, go to stderr.
3. Repeat step 2 for each arm: `dry-run`, `claude`, `codex`, `claude-attached`, `codex-attached`, `claude-push`, `codex-push`.
