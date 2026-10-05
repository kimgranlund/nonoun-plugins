<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- `python3 docs/reports/messages-live-run/probe.py selftest`: pass. Evidence: ran in the tree, five `ok:` lines (a to e) then `probe selftest: PASS`, rc 0. It bites: on a copy in a throwaway worktree at `$SDLC_BASE_SHA`, six planted defects each went red.
  - Oracle returning no reasons: FAIL at b.
  - Isolation always yes: FAIL at d.
  - Mention counter forced to 0: FAIL at e, `counts [0, 0]`.
  - Empty-stamp check dropped: FAIL at c.
  - Folder check dropped: FAIL at b.
  - Fixture `mv` changed to `cp`: FAIL at c.
  - With the copy restored: PASS, and `cmp` showed it identical to the built file. At base with no probe: rc 2.
- `python3 docs/reports/messages-live-run/probe.py claude`: pass. Evidence: live run, rc 0, `isolation=yes skills=0 slash_commands=0 sdlc_agents=0 skill_calls=0`, `result=pass`.
  - Checked on disk in `messages-live-7u8sx45h`: the message is only in `done/claude/` with `send_time` 10:07:54.002 <= `read_time` 10:08:00.041 <= `ack_time` 10:08:00.176, and `new/probe/` holds a reply with `topic: live-probe` and `re: <id>`.
  - Raw init event: `skills: []`, `slash_commands: []`, agents `claude, Explore, general-purpose, Plan`, no `Skill` tool.
  - The role's only calls were Read of the message, Read of `.sdlc/messages/AGENTS.md`, and one Bash running `read`, `reply`, `ack`.
  - Red form: the `--defect` run below exits 1 through the same oracle.
- `out=$(... probe.py claude --defect); rc=$?; test "$rc" -eq 1 && ... grep -q "^result=fail"`: pass. Evidence: live run, probe rc 1, `result=fail reason=empty read_time, ack_time; no reply ...`, criterion rc 0. The trace shows the role ran the injected `mkdir -p ... && mv ...`. The biting variable is the entry-file content: the same isolated role passes with the generated files.
- `python3 docs/reports/messages-live-run/probe.py codex; rc=$?; test "$rc" -eq 0 -o "$rc" -eq 3`: pass. Evidence: live run, rc 0, `isolation=yes ignore_config_sdlc_mentions=0 with_config_sdlc_mentions=68`, state lines new, read, done, `result=pass`. Red form observed: an extra live `probe.py codex --defect` exited 1 with `result=fail`, and the criterion's `test` then gave rc 1. Also `PATH=/usr/bin:/bin probe.py claude` printed `result=unverified reason=claude is not on PATH`, rc 3.
- Evidence-file results (`claude.txt`, `claude-defect.txt`, `codex.txt`, `codex-messenger.txt`): pass. Evidence: rc 0 in the tree. Red at base (rc 2), and red on copies with `claude.txt` set to `result=fail`, the defect file set to `result=pass`, and `codex-messenger.txt` set to `result=fail` (rc 1 each).
  - The stamps line of all five evidence files matches the message files still on disk in the builder's temp projects.
  - Non-biting conjunct: on Codex, `messenger_spawned=yes` comes from the `cat` of `.sdlc/messages/AGENTS.md`, which names the agent, so it prints with or without a spawn. The Do specifies this mechanism and no criterion asserts it for Codex.
  - The builder's rollout claim holds. The parent rollout for thread `01a0f6e5-c982...` has `spawn_agent` with `agent_type: sdlc-messenger-l1`. The subagent rollout `01a0f6e5-fb54...` has `agent_role: sdlc-messenger-l1`, that `parent_thread_id`, `gpt-5.6-terra low`, and ran `count`, `list`, `read`, then `reply` and `ack`.
- `claude-messenger.txt` (result, spawn, state order): pass. Evidence: rc 0 in the tree. Red at base, and red on copies with the `state=read` line deleted and with `messenger_spawned=no` (rc 1 each). The builder's raw stream in `messages-live-noy14goj` confirms it:
  - init `agents` holds `sdlc-lite:messenger` from `sdlc-lite@inline`;
  - three `Agent` calls with `subagent_type: sdlc-lite:messenger` and `run_in_background: false`;
  - the subagent (haiku) ran `count`, `list`, `read`;
  - the parent (sonnet) ran `reply` and `ack`.
- Isolation lines (`claude.txt`, `codex.txt`): pass. Evidence: rc 0 in the tree. Red at base, and red on copies with `isolation=no skills=1` and with `ignore_config_sdlc_mentions=2` (rc 1 each). The builder's Codex rollout `01a0f6eb-bd97...` has 0 `sdlc-lite` mentions in the 12 lines before the first tool call, as the doc says.
- Doc `Recorded:` line and eight `##` sections: pass. Evidence: rc 0 in the tree. Red at base (rc 2) and on a copy with `## Limits` renamed (rc 1).
- Doc `Result:` lines (python check): pass. Evidence: rc 0 in the tree. Red at base (rc 1) and on a copy with the Negative control line set to `Result: fail` (`AssertionError: ['Negative control']`).
  - Every quoted block line is verbatim in its evidence file.
  - Environment claims reproduced: `claude --version` 2.1.286, `codex --version` 0.159.2, `git rev-parse --short HEAD` f93894d, and `git status --porcelain -- plugins/` empty.
- `grep -qF "(validation/messages-live-run.md)" docs/README.md`: pass. Evidence: rc 0 in the tree, rc 1 at base. `git diff` shows one added line, after the `Ticket root and router live run` line, with the handoff's text.
- `test -f "$d/probe.py" && ! grep -rqF <em dash> ...`: pass. Evidence: rc 0 in the tree. Red at base (rc 1, no `probe.py`, so the path guard holds) and on a copy with an em dash appended (rc 1).
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest`: pass. Evidence: `messages selftest: PASS`, rc 0, and rc 0 at base. It bites: on a throwaway copy with the ack refusal removed, `FAIL: read to done, follow-up true after a reply`, rc 1. `messages.py` is unchanged in the diff.
- (guard) no em dash in added lines of `messages.py` and `docs/README.md`: pass. Evidence: rc 0. Red on a throwaway copy with an em dash line appended to `docs/README.md` (rc 1).
- (guard) scope: pass. Evidence: rc 0. The changed and untracked files are `docs/README.md`, `docs/reports/messages-live-run.md`, and seven files under `docs/reports/messages-live-run/`. Red on a throwaway copy with a stray `docs/stray.md` and with an edit to `plugins/sdlc-lite/scripts/board.py` (rc 1 each).

Other checks behind accepted claims and dismissals:
- **Probe matches the Do.** Imported the module: both parent prompts equal the handoff text; the `claude` and `claude-messenger` argv equal the handoff commands; `clean_env` removed all five kinds of variable and kept an unrelated one.
- **Codex argv quoting.** The Codex argv differs from the handoff only by passing `model_reasoning_effort="medium"` and `approval_policy="never"` with literal quotes. Dismissed: the rollout `turn_context` records `gpt-6.1-sol medium never`, so the effect is the same.
- **Neighbors.** `git grep` for dependents of `docs/README.md` found only `onboard.py`, which checks that an adopting repo's README exists, not this file's content. `python3 scripts/check-packaging.py` printed PASS. Local links in the doc and README resolve. `git diff --check` is clean and the new files have no trailing whitespace.
- **Steelman.** Draft fail: the Codex spawn check cannot bite, so file a plan defect. Builder's rebuttal: the Do fixes that mechanism, no criterion depends on it, and the doc discloses it and proves the spawn from rollout files. I checked those files and the rebuttal holds, so the finding is dropped as a fail and recorded above.
- **Tree state.** The throwaway worktree is removed and `git status` matches the start.

## Out of scope changes
None

## For the next attempt
None
