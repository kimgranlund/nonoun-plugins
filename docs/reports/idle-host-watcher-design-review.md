# Idle-host watcher design review

Recorded: 2026-10-01. Independent review of `docs/planning/ticket-stages/watcher-design.md` v0.1 (commit 5c1f574 on branch `idle-host-watcher`), ticket T-0182. The reviewer was the `architect` role, `run.sh architect L1`, model `fable` effort high, a different family from the author (Claude Sonnet). It was read-only in the repository except for its own `decompose/` folder. Raw result: `.sdlc/.0182-idle-host-watcher-design/review/architect-L1.md`; handoff: `.sdlc/.0182-idle-host-watcher-design/review/handoff.md`. The reviewer ran one probe per host in `/tmp` with `claude 2.1.286` and `codex-cli 0.159.2`, each a single trial on one machine and account.

## Verdict

Ready after fixes. The core holds: a deterministic poller that only counts, plus the mailbox's atomic rename claim. Nothing is built, and no finding has been applied yet; T-0183 step 1 applies them to the design before any code.

## Findings

| # | Severity | Finding | Evidence (from the review) |
| --- | --- | --- | --- |
| 1 | blocker | `codex exec resume` rejects `--sandbox`; without a sandbox override a resumed Codex turn is `read-only` and cannot claim. Use `-c sandbox_mode="workspace-write"` and `-c sandbox_workspace_write.network_access=false`; approval is `-c approval_policy="never"` | resume with `--sandbox` exits 2; `codex_exec.py:49` |
| 2 | blocker | Nothing blocks a publish on Claude as designed: `block-publish.sh:22` gates on `SDLC_ROLE`, and `SDLC_HEADLESS=1` arms only `block-background.sh`. Add `--permission-mode dontAsk` with an allow list, and set `SDLC_ROLE`. MCP tools are covered by no hook on either host | `block-publish.sh:22`; denial probe |
| 3 | blocker | A wake that exits 0 without handling mail counts as success and repeats up to the daily cap. Judge success by mailbox progress (`new/` and `read/` before and after) | plan-mode probe: exit 0, $0.145, no file written |
| 4 | blocker | The owned-session default does not wake the host the user left, can race an active host's messenger, and grows on every wake. This needs a user decision | design line 32 against the ticket Context; token counts 19,170, 64,709, 111,431 |
| 5 | major | A message claimed by a wake that fails stays in `read/`, and `count` sees only `new/`, so nothing retries it | `messages.py:967-975` |
| 6 | major | The lock is per checkout while the mailbox is shared by worktrees; place it beside the mailbox | `messages.py` "Mailbox root" |
| 7 | major | Reply-loop depth follows `re:` only; `send` without `--re` and per-receiver wakes bypass it | `cmd_send` |
| 8 | major | The watcher calling `expire` moves messages and creates notices, contradicting "never moves" | `messages.py:906-943` |
| 9 | major | The "worked" rows and the cost figure have no recorded evidence; a tool-using wake costs 3 to 4 times the figure | no record in the repository |
| 10 | major | The no-push validation row can pass with no mechanism; rate-limit and active-host rows lack real negative controls | design lines 95, 98, 102 |
| 11 | major | Attached mode's idle signal cannot tell closed from idle-but-open in a terminal | unverified |
| 12 to 17 | minor | `--session-id` is create-only (reuse exits 1), so create-then-resume state is needed; stale-pid check ignores pid reuse; retry backoff conflicts with the cooldown; debounce and counter persistence across restarts; launchd `PATH`, sleep, and environment scrub; `.sdlc/supervisor/` git-ignore | probes and design lines |
| 18 | note | Probe leftovers were left by the review in `/tmp` and in one Claude session and one Codex rollout in the host stores; the repository was not touched | review |

Alternatives the design did not weigh: notify the person or wake the host the user left with a fixed prompt; a fresh ephemeral session per wake; running a wake through the existing role path (`run.sh`, `codex_exec.py`, `SDLC_ROLE`); progress-based success; a wake naming one message id restricted to the timestamp prefix; `claude --bg --resume` as an active-session check; a global cap across receivers.

## Decision from the user

Finding 4, decided 2026-10-01: the default for an idle host is a fresh ephemeral session per wake (it reads the message and entry files, handles it, and exits). Attached-session resume and notify-only stay opt-in. Recorded in `docs/planning/ticket-stages/watcher-design.md` and applied by T-0183.

## What this review does not cover

It did not re-run `claude -p --continue` or `codex exec resume --last`. A different permission configuration changes the Claude results (this user's `defaultMode` is `plan`). Every probe was a single trial.

## Applied

T-0183 step 1 applied findings 1 to 17 to the design, Version 0.2 (`docs/planning/ticket-stages/watcher-design.md`). Its "Review findings applied" table maps each finding to the decisions, tagged D1 to D21, that apply it; finding 18 needed no design change. The findings above stay unchanged as the record of the review.
