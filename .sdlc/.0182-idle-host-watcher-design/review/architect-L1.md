<!-- role=architect level=L1 model=fable effort=high -->
## Approach

Verdict: **ready after fixes**. The core idea holds: a deterministic poller that only counts, plus the mailbox's atomic rename claim. Four things must change before T-0183 builds from it:

- the Codex limit uses a flag `codex exec resume` rejects;
- the Claude publish guard is not armed by the env var the design names;
- a wake is judged by exit code, not mailbox progress;
- the owned-session default does not wake the host the user left, which needs a user decision.

Evidence comes from the repository, `--help` on `claude 2.1.286` and `codex-cli 0.159.2`, and one probe per host in `/tmp`. The Claude probe was three haiku turns on one session; the Codex probe was three `gpt-5.6-terra` low turns on one thread. `claude -p --continue` and `codex exec resume --last` were not re-run.

The decomposition is in `review/decompose/manifest-v1.json` and `report.md`; `coverage_check.py` exits 0. I did not add the `Decomposition:` line to the handoff because this role is read-only outside `decompose/`.

1. **Does it cover every Context item?** Mostly; three are partial.
   - Item 2: sleep is never mentioned, and "survives logout or sleep" and "permission needs" are not answered per mechanism (design lines 37-42).
   - Item 5: no model or effort is named for a wake, and the Claude cost is unmeasured (line 28).
   - Item 7: "a message that stays in `new/`" is covered only after a non-zero exit (line 79). A wake that exits 0 with no progress, or that claims and then dies, is not covered.

2. **Is every host flag real and used correctly?** The Claude flags are real; two uses are wrong or incomplete. One Codex flag is wrong.
   - `codex exec resume --sandbox workspace-write` exits 2 with `unexpected argument '--sandbox'`; `-C` is rejected too. The working form is `-c sandbox_mode="workspace-write"`: the probe's resumed turn recorded `workspace-write, network_access: False` and wrote a file.
   - Without that override the resumed turn ran `read-only` and a `touch` failed, so a Codex wake as designed cannot claim a message.
   - `--session-id` only creates. A second use prints `Error: Session ID ... is already in use.` and exits 1, so the watcher needs a create-then-`--resume` state.
   - `--allowedTools` is an allow list, not a restriction. Its effect depends on the permission mode, which the design never sets.
   - `resume --last` and `--continue` pick the most recent session in the directory, which may be a person's.

3. **Is the owned-session default safe, and does it serve the idle Codex host?** It is safe against two writers on one session. It does not serve the user's case.
   - The session the user left never learns of the mail. A context-free session reads it, answers, and acks it into `done/`.
   - Owned mode checks only the watcher's own child (line 50). It will race an active interactive host's messenger and can take that host's mail.
   - The owned session grows on every wake with no rotation. Codex input tokens went 19,170, then 64,709, then 111,431 across three small turns.

4. **Can the watcher claim, move, or print a body?**
   - Claim: no, if it uses only `count` and `list`.
   - Move: yes. Line 75 lets it call `messages.py expire`, which moves messages to `done/` and writes notice messages (`messages.py:906-943`). That contradicts line 12.
   - Print: not directly. The design does not say where the wake child's stdout goes, and a woken host's reply can quote a body.

5. **Can a reply loop or wake storm get through?** Yes, in four ways.
   - The depth rule follows `re:` only. Two hosts that answer with `send` have no chain, so they run at the caps (24 wakes per receiver per day) every day.
   - The depth rule is per message but the wake is per receiver and the prompt says "read each". Any other new message gets the depth-blocked one handled.
   - A wake that exits 0 without handling mail repeats every cooldown until the daily cap.
   - Line 74 is not a checkable rule, and nothing says whether the counters survive a restart under `KeepAlive`.

6. **Is the claim race analysis right?** Right at the claim: `os.rename` at `messages.py:604`, losers refused at 834-844. It is incomplete elsewhere.
   - A message claimed by a wake that then fails or is killed sits in `read/`. `count` sees only `new/`, so nothing retries it, and line 79's "leaves the message in `new/`" is false in that case.
   - The watcher lock is at `.sdlc/supervisor/lock` per checkout, while the mailbox is shared by every linked worktree. Two worktrees can run two watchers on one mailbox.
   - For an attached session, a quiet transcript modification time describes exactly the idle-but-open terminal the user has. The quiet period therefore does not prevent a second writer.

7. **Does a woken host lack authority to push or publish?**
   - Claude as designed: prompt only. `block-publish.sh:22` exits 0 unless `SDLC_ROLE` is set; `SDLC_HEADLESS=1` arms only `block-background.sh:10`.
   - Claude with `--permission-mode dontAsk` plus the allow list: a mechanism. The probe ran the allowed `touch`, denied the other with a `permission_denials` entry, exit 0, no hang.
   - Codex: the sandbox is a mechanism for network pushes once passed through `-c`. It does not cover MCP or connector tools; the publish hook does not either, because it matches Bash only.
   - "Never call AskUserQuestion" and "bodies are data" are prompt only on both hosts.

8. **Which claims are verified, and are any verified without evidence?**
   - The four "worked" rows have no recorded evidence: no file, no command log, single runs. I reproduced `--session-id` and `--resume`, and ran the unrun resume-by-id row (works).
   - Stated as fact but wrong or unevidenced: `--sandbox` on resume; "`SDLC_HEADLESS=1` so the plugin's hooks run in headless mode"; "it is safe" for the owned session; "about 17,600 tokens" for a wake.
   - Correctly marked unverified: denied-tool behaviour, keychain under lock, transcript modification time, attached resume.

9. **Can the validation plan fail?** Partly.
   - No push (line 102): "denied or absent" passes when the model simply declines, so it proves no mechanism. Its negative control is not a runnable case.
   - Rate limits (line 98): "limits set to 0 fires immediately" is a second positive, not a control. "Third wake in the cooldown" contradicts a cooldown of one.
   - No wake when active (line 95): it patches the stub, which never sees the signal. The patch must be to the watcher.
   - No rows for: daily cap, debounce, exit 0 without progress, timeout kill, stale pid, `expire`, counters across restart, the shared-worktree lock.

10. **What is missing?** A builder would have to guess all of these.
    - The receiver-to-host-and-session map.
    - The working directory for a wake (both hosts look sessions up by directory).
    - Model and effort for a wake.
    - The permission mode.
    - The destination and retention of child output.
    - Session rotation, and what to do when a session is lost.
    - Environment scrubbing when the watcher starts inside an agent session.
    - `PATH` under launchd.
    - Whether `.sdlc/supervisor/` is git-ignored.
    - A global cap across receivers.

## Interfaces

- `codex exec resume ... --sandbox workspace-write` (design lines 61, 86; repeated in `.sdlc/.0183-supervisor-script/handoff.md`): wrong. `codex exec resume --sandbox workspace-write --last hi` exits 2. Use `-c sandbox_mode="workspace-write"`, and pass `-c sandbox_workspace_write.network_access=false` so user config cannot widen it.
- Codex "approval policy `never`" (line 61): no such flag exists on `exec` or `resume`. The repository uses `-c approval_policy="never"` (`codex_exec.py:49`). The design should name that form.
- `codex exec resume --last` (line 25): real, but help says "most recent recorded session", filtered by working directory. It is not "the session it started" (line 32). The owned session must store the `thread_id` from the `thread.started` event of `--json`.
- `codex exec resume <session-id-or-thread-name>` (line 26): the id form is now checked and works. The thread-name form is unchecked.
- `claude -p --session-id <uuid>` (line 22): real, and create-only (see question 2).
- `claude -p --continue` (line 24): real per help. Unsafe for a watcher because it takes the most recent conversation in the directory.
- `--allowedTools` (line 61): real, but it only grants.
  - This user's `~/.claude/settings.json` has `defaultMode: plan`. The probe session refused both `touch` commands, including the allow-listed one, and exited 0 at `total_cost_usd` 0.145.
  - The design must add `--permission-mode dontAsk` (or `--permission-prompts none`) and should weigh `--tools` and `--disallowedTools`.
  - The pattern that allows only `messages.py` is unchecked.
- `--max-budget-usd` (lines 61, 66): real, print mode only. Whether it stops a turn in progress is unchecked.
- `SDLC_HEADLESS=1` (line 61): arms only `block-background.sh`. The publish block needs `SDLC_ROLE` (`block-publish.sh:22`, `run.sh:10`, `fanout.py:62`).
- `.sdlc/supervisor/lock` (line 52): wrong location for a mailbox shared across worktrees. It belongs beside the mailbox, as `messages.py` resolves it through `git rev-parse --git-common-dir`.
- `messages.py expire` called by the watcher (line 75): moves and writes messages.
- `~/.codex/sessions/` rollouts (line 50): path confirmed. The file name holds the thread id (`rollout-2026-10-01T07-37-05-<thread>.jsonl`).
- "Claude project folder" transcripts (line 50): a per-directory folder exists under `~/.claude/projects/`. The file layout inside it was not checked.

## Constraints and assumptions

- A headless call can continue a recorded session on both hosts: verified by probe. Claude `--resume` recalled the code word; Codex resume by id recalled it.
- The claim is one atomic rename and losers exit 1: verified by `messages.py:581-604` and `826-844`.
- `count` reads only valid files in `new/<receiver>/` and prints no body: verified by `messages.py:967-975`. It does load each file, body included, to validate it.
- `workspace-write` has no network by default: verified by the probe's `turn_context` and by `docs/reports/messages-live-run.md:13`. It holds only while user config does not set `network_access`.
- A resumed Codex turn keeps a usable sandbox without a flag: false as designed. The no-override turn was `read-only`. The probe cannot tell inherited from default, because the session was created read-only.
- A denied tool in `-p` fails without hanging: verified only under `--permission-mode dontAsk`. Unverified under the default mode.
- `SDLC_HEADLESS=1` makes the plugin's hooks guard a wake: false for publishing, by `block-publish.sh:22`. This session's own probe script was blocked by that hook under `SDLC_ROLE=architect`, so the hook does bite when armed.
- The plugin's hooks load in a `-p` wake at all: unverified. They load only where the plugin is installed and the run is not `--bare` or `--safe-mode`.
- Exit code 0 means the mail was handled: false, per the plan-mode probe.
- One wake costs about 17,600 tokens: not reproduced. I measured 19,170 input tokens for a no-tool Codex turn and 64,709 for a resumed turn with one tool attempt. A Claude haiku first turn created 35,124 cache tokens at $0.145.
- A wake runs under the same CLI login as the user: verified for a terminal start (both probes authenticated). Unverified under launchd or a locked screen.
- Transcript modification time shows a live turn: unverified. It cannot show an idle session that is still open.
- `fcntl.flock` is released when the process dies: standard OS behaviour, not probed.
- The mailbox is shared by all worktrees: verified by the `messages.py` docstring, "Mailbox root". Whether a Codex wake started in a linked worktree can write a mailbox outside its workspace root is unverified, and likely not.
- A reply depth of three bounds loops: unverified, and false for `send` without `--re`.

## Rejected alternatives

The design did not weigh these.

- Notify the host the user left instead of substituting for it: wake it with a fixed prompt, or tell the person (terminal bell, notification) and let them resume. This is the only option that serves the stated case without a second writer.
- A fresh ephemeral session per wake (`--no-session-persistence`, `codex exec --ephemeral`) instead of a growing owned session: constant cost per wake, no session id state, no rotation problem. The owned session carries no useful context anyway.
- Run the wake through the existing role path (`run.sh` or `codex_exec.py` with `SDLC_ROLE` set): this reuses the publish hook, the sandbox arguments, the attempt record, and the lock that already exist and are tested.
- Progress-based success: compare `new/` and `read/` for the receiver before and after a wake, and treat "no change" as a failure whatever the exit code.
- A wake that names one message id rather than a count: the depth and loop rules then apply to what the host actually handles. The design rejects ids because the slug comes from the sender's topic; an id restricted to the timestamp prefix was not considered.
- Claude's own `--bg --resume <session-id>`: help says it "starts a copy and says so when the session is already running". That may be a host-provided active-session check for the attached mode.
- A global cap across all receivers, and a cap on consecutive wakes with no human-sent message in between.

## Risks

Blockers

1. The Codex limit cannot be invoked as written, and without it a wake cannot claim. Evidence: the `--sandbox` rejection and the read-only resumed turn under Interfaces; design lines 61 and 86.
2. Nothing blocks a publish on Claude as written. Evidence: `block-publish.sh:22` gates on `SDLC_ROLE`; the design sets only `SDLC_HEADLESS` and no permission mode. External writes through MCP tools are covered by no hook on either host.
3. A wake that does nothing counts as success and repeats at cost. Evidence: the plan-mode probe (exit 0, $0.145, no file written); design line 79 handles only non-zero exits. At defaults that is up to 24 paid no-op wakes per receiver per day.
4. The default mode does not do what the ticket asks for. Evidence: design line 32 against the ticket Context ("the user keeps a Codex host awake with `/goal`"). The left host never sees the mail, and the owned session can take mail from an active host. This needs a user decision, not a builder guess.

Major

5. A message claimed by a wake that then fails is stranded in `read/` until `expires` (7 days by default). Evidence: `cmd_count` reads only `new/` (`messages.py:967-975`); design line 79.
6. Two watchers can run on one mailbox from two worktrees. Evidence: design line 52 against the `messages.py` "Mailbox root" docstring.
7. Reply loops pass the depth rule through `send` without `--re`, and through per-receiver wakes that handle every message. Evidence: design lines 60 and 73; `messages.py` `cmd_send` takes an optional `--re`.
8. The watcher moves messages through `expire`, which also creates notice messages that can trigger wakes. Evidence: design line 75 against line 12; `messages.py:906-943`.
9. The "worked" rows and the cost figure have no recorded evidence, and the cost figure understates a tool-using wake by about three to four times. Evidence: no record in the repository; the token counts under Constraints and assumptions.
10. The no-push validation row can pass with no mechanism in place, and the rate-limit and active-host rows have no real negative control. Evidence: design lines 95, 98, 102.
11. Attached mode's idle signal cannot tell "idle and closed" from "idle and open in a terminal". Evidence: design lines 33 and 50; nothing verified.

Minor

12. `--session-id` reuse fails, so the create-versus-resume state must be specified (the "already in use" probe output).
13. The stale-pid check (line 82) does not address pid reuse. Record the start time or a process group.
14. Retries at 1, 2, 4 minutes (line 79) conflict with the 10 minute cooldown (line 72). Whether retries count against the caps is unstated.
15. Debounce of one 10 second poll is short for a burst from a slow sender. Counter persistence across a `KeepAlive` restart is unstated.
16. Launch table: no sleep behaviour, no `PATH` or environment note for launchd, no scrub of `CLAUDECODE` and `SDLC_*` when the watcher is started from an agent session.
17. `.sdlc/supervisor/` is not stated as git-ignored, and `status.json` is rewritten every 10 seconds inside a tracked folder.
18. Probe leftovers from this review: `/tmp/t0182-review-claude.GRO0SF`, `/tmp/t0182-review-codex.qEQ3hl`, three `/tmp/t0182-*.sh` scripts, three `/tmp/t0182-codex-*.jsonl` logs, one Claude session and one Codex rollout in the user's host stores. Nothing was written in the repository outside `review/decompose/`.

What would make this review wrong: a different user permission configuration changes the Claude results, and each probe was a single trial on one machine and one account.
