---
id: T-0702
title: "Lane agents ran find / for hours despite block-disk-scan"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane role can never start a whole-disk search, and its brief says to search only inside its Tree and Artifacts dir.

## Intent
- Do: find why `plugins/sdlc-lite/hooks/block-disk-scan.sh` did not stop `find / -name docs_check.py` and `bfs / -name ui-designer-L1.md -path *ux0246*` from solo and builder sub-agents (check that `_role.sh` resolves level-variant agent types such as `sdlc-lite:solo-L1` and `sdlc-lite:builder-L2`, and that the hook is registered for sub-agents); fix the cause. Add `mdfind` with no `-onlyin` to the blocked commands. Add one line to the prompt `dispatch.py prepare` and `solo_run.py` build: search only inside Tree and the Artifacts dir.
- Non-goals: blocking searches below a project folder.
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "Solo and builder agents ran `find / -name docs_check.py` and `bfs / -name ui-designer-L1.md -path *ux0246*` to locate a file. They ran from lane trees at full CPU for up to 6 hours, and `find /` survived SIGTERM." Seen from a ui-kit-neue conductor session on 0.29.0. The hook's own header says it blocks find and bfs on `/` inside a role run.

## Acceptance criteria
1. The hook's regression check (`bash plugins/sdlc-lite/scripts/check.sh` job that covers hooks, or the hook test it names) exits 0 with new cases: agent type `sdlc-lite:solo-L1` running `find / -name x` is blocked; `mdfind x` is blocked; `mdfind -onlyin . x` is allowed. Each new blocked case is observed passing (exit 0) with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and a prepared prompt holds the search-scope line.
3. The Outcome names the cause found.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0.

## Outcome
Cause: the role was never resolved, because the lane agents were in-process teammates. In a session with agent teams on (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), an Agent spawn with a `name` becomes a teammate whose hook payload `agent_type` is its spawn name (`solo-0702`, `0702-solo-L2`, `0697-verifier-L2-2`), not its `sdlc-lite:` type. The transcript `meta.json` shows this: `agentType` holds the name, `customAgentType` holds `sdlc-lite:solo-L1`, and `taskKind` is `in_process_teammate`. `_role.sh` resolved no role for those names, so every role hook (disk-scan, background, stdin, pattern-kill, and the rest) exited 0. Evidence: in this session the teammate `solo-0702` ran `find / -maxdepth 0 -name x` unblocked, and its command was not wrapped by close-role-stdin. An unnamed `sdlc-lite:scout-L1` sub-agent in the same session was wrapped and blocked. Three `claude -p` probes with and without a name, in the foreground and the background, were blocked too, because there `agentType` stays `sdlc-lite:<role>-L<n>`. The ticket's two suspects are cleared: `_role.sh` already resolved `sdlc-lite:solo-L1` and `sdlc-lite:builder-L2`, and the hook is registered and fires for sub-agents. The installed 0.29.0 hook blocks both incident commands when the agent_type is the sdlc-lite type. One step is inferred, not captured: that the hook payload's `agent_type` equals `meta.json` `agentType`. A teammate's payload cannot be captured without editing the parent session's settings.

Fix:
- `_role.sh`: a colon-free agent_type also resolves when it holds `<role>-L<n>` as whole hyphen parts, or starts or ends with `solo`. Other names (`ticket-author`, `plan-driver-hardening`) still have no role.
- `block-disk-scan.sh` blocks `mdfind` unless every `-onlyin` folder is below the root set. The fail-closed path covers it too.
- `dispatch.SEARCH_SCOPE` is a new line in every `dispatch.py prepare` brief and, through `solo_run.report_lines`, in the solo and fanout briefs: search only inside Tree and the Artifacts dir.
- `claude-hooks.md` and `sdlc-internals.md` are updated.

Checks: `bash plugins/sdlc-lite/scripts/hook-selftest.sh` PASS. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0 (`ok: T-0702 the brief bounds file searches...`), and `prepare --dry-run verifier L2` prints the line. `solo_run.py selftest` and `fanout.py selftest` PASS. `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check a8680df4` exit 0.

Red controls, using the base hooks (a8680df4): every new mdfind block case and the teammate-name cases (`solo-0702`, `0702-solo-L2`, `0697-verifier-L2-2`, `T-0702-solo`) exit 0, and they exit 2 after the change. The `sdlc-lite:solo-L1` case named in criterion 1 exits 2 before the change too. It is a regression pin, not a red control, because that path was never broken.

Still open: a teammate named outside these patterns still has no role. Exact resolution would need the payload to carry the custom type, or the hook to read `customAgentType` from `meta.json`.
