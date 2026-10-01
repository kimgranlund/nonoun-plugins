<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `docs/validation/messages-live-run/probe.py`: new. Runs the four arms plus `--defect` and `selftest`, as the handoff specifies.
- `docs/validation/messages-live-run/defect-AGENTS.md`: new. The injected wrong `# Mailbox` procedure (`cat <path>`, then `mkdir -p ... && mv ...`, no reply, no script).
- `docs/validation/messages-live-run/claude.txt`, `claude-defect.txt`, `codex.txt`, `claude-messenger.txt`, `codex-messenger.txt`: evidence from the recorded runs, saved with `| tee`.
- `docs/validation/messages-live-run.md`: new dated validation doc with the eight required sections. Every arm section reads `Result: pass`.
- `docs/README.md`: added the Messages live run line after the Ticket root and router line.
- `plugins/sdlc-lite/scripts/messages.py`: not edited. No run showed the entry files were wrong or unclear.

## Checks
- AC1 `probe.py selftest`: exit 0, all five cases ok, `probe selftest: PASS`.
  - Negative controls on it: with an always-pass oracle it failed at case b; with the mention counter forced to 0 it failed at case e.
- Recorded runs, each with `| tee`:
  - claude: exit 0, `result=pass`.
  - claude `--defect`: exit 1, `result=fail reason=empty read_time, ack_time; no reply ...`.
  - codex: exit 0, `result=pass`, `isolation=yes ignore_config_sdlc_mentions=0 with_config_sdlc_mentions=68`. This arm was recorded a second time after the probe change in Notes.
  - claude-messenger: exit 0, `result=pass`, `messenger_spawned=yes`, state lines new, read, done in order.
  - codex-messenger: exit 0, `result=pass`.
- Live acceptance criteria, rerun on the final probe:
  - AC2 `probe.py claude`: exit 0, pass, isolation yes.
  - AC3 defect check: rc 1 and `result=fail`, criterion exit 0.
  - AC4 `probe.py codex`: exit 0, pass.
- AC5 through AC11: each run verbatim, each exit 0.
- AC12 guard `messages.py selftest`: PASS.
- AC13 guard (no em dash added in the diff from `$SDLC_BASE_SHA` = f93894d): exit 0.
- AC14 guard (scope): exit 0. The changed and untracked files are only `docs/README.md`, the doc, and the `messages-live-run/` folder.
- Extra checks:
  - `git diff --check`: clean.
  - Trailing-whitespace and en/em dash scans of the new files: clean.
  - Every local link in the doc resolves.
  - No probe or host process left running.

## Notes
- **The Codex spawn check passes even when no messenger is spawned.** This is a weakness in the plan's Do, not a defective criterion. The Do prints a `sub=sdlc-messenger-l1` line for any item whose JSON names the agent. The Codex parent prompt makes the parent `cat .sdlc/messages/AGENTS.md`, and that file names the agent, so `messenger_spawned=yes` prints whether or not a spawn happened. In both Codex arms that line came from the `cat` output.
  - The `codex exec --json` stream never contains the `spawn_agent` call. It shows only `collab_tool_call` `wait` items with empty `receiver_thread_ids`.
  - The rollout files do prove a real spawn this run. The parent's rollout (thread 01a0f6e5-c982...) has `spawn_agent` with `agent_type: sdlc-messenger-l1`. A subagent rollout (thread 01a0f6e5-fb54...) has `agent_role: sdlc-messenger-l1`, ran on gpt-5.6-terra low, and ran count, list, read, then reply and ack. That is why the doc records pass and states the caveat in Limits.
  - Suggested follow-up: base the check on the subagent rollout's `session_meta` (`agent_role` plus `parent_thread_id`).
- **Claude messenger finding:** two of its three spawns armed a Monitor and returned "polling" with no claim. Only the parent's spawn-again loop reached the claim. This is recorded in Limits.
- **Probe change after recording:** after four arms were recorded, I made the probe strip trailing whitespace from truncated commands, because codex.txt had one trailing space that `git diff --check` would flag on commit. I re-recorded only the codex arm (still pass) and updated the doc. The other four files contain no line ending in whitespace, so the change does not alter them.
- **Choices the spec left open:**
  - The defect run prints `arm=claude defect=yes`.
  - Empty stamps print as `-`.
  - A timeout before any tool call, or a missing Codex rollout file, is reported unverified.
- **Leftover temp folders:** the throwaway projects stay under the system temp folder, as the spec asks, including the ones from the acceptance reruns. My earlier hand-made scratch folder `.../T/msgtry.U7VgaMmgGq` could not be removed because `rm` was denied. It is outside the repo.
