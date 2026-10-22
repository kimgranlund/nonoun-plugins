---
id: T-0704
title: "Role hooks resolve a named teammate by its real agent type"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every role hook knows the role of a named teammate from its real agent type, not from a pattern in its spawn name.

## Intent
- Do: find where a named teammate's real type is available to a PreToolUse hook (the payload, or the transcript `meta.json` field `customAgentType` that T-0702 found), and have `plugins/sdlc-lite/hooks/_role.sh` use it before the T-0702 name inference; keep the name inference only as a fallback.
- Non-goals: changing spawn names.
- Done when: the criteria pass.

## Context
T-0702 Outcome: "For a teammate the hook payload's `agent_type` is the spawn name (`solo-0702`, `0702-solo-L2`), not `sdlc-lite:solo-L1`." Still open there: "a teammate whose name matches neither pattern still gets no role. An exact fix would need the payload to carry the real type, or the hook to read `customAgentType` from `meta.json`."

## Acceptance criteria
1. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 with a new case: a teammate named `reviewer-x` whose real type is `sdlc-lite:builder-L2` is resolved as builder; the case fails with the change reverted.
2. The Outcome names where the real type was read from and how that was observed.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0.

## Outcome
Where the real type is: not in the hook payload. A teammate's PreToolUse payload carries `agent_type` (the spawn name), `agent_id`, and the parent session's `transcript_path`, and no other type field. The real type is `customAgentType` in the transcript sidecar `<transcript_path minus .jsonl>/subagents/agent-<agent_id>.meta.json`, and that file exists by the teammate's first tool call.

How it was observed: an interactive `claude` session (run under `script` in a throwaway project in the scratchpad, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, the project's own `.claude/settings.json`) spawned a custom agent `probe-builder` with the name `reviewer-x`. Its PreToolUse(Bash) hook logged the raw payload: `agent_type: reviewer-x`, `agent_id: areviewer-x-e98ae2e33e93e366`, `transcript_path: .../456a1ac0-....jsonl`. In the same call the hook read `.../456a1ac0-.../subagents/agent-areviewer-x-e98ae2e33e93e366.meta.json`, which already held `customAgentType: probe-builder`, `taskKind: in_process_teammate`. This lane's own sidecar fits the same shape (`agent-asolo-0704-....meta.json`, `customAgentType: sdlc-lite:solo-L2`). A `claude -p` probe made no teammate: the named spawn's payload `agent_type` was `probe-builder` and its meta had no `customAgentType`.

Fix: `_role.sh` reads that sidecar for a colon-free `agent_type` (agent_id limited to `[A-Za-z0-9_-]`); a `customAgentType` it finds decides the role, so a real non-role type such as `general-purpose` is no role even for a name like `solo-0799`. With no sidecar or field the T-0702 name inference runs as before. `claude-hooks.md` and the selftest comments are updated.

Checks: `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exit 0. `python3 plugins/sdlc-lite/scripts/check.py` exit 0. `python3 scripts/check-packaging.py` exit 0. `git diff --check 12785ab2` exit 0. shellcheck on `_role.sh` clean.

Red control: with `_role.sh` from base 12785ab2 the selftest fails on `teammate reviewer-x with real type sdlc-lite:builder-L2 must resolve builder (T-0704)`; base resolves `reviewer-x` (with sidecar) to no role and `solo-0799` (sidecar `general-purpose`) to solo, and `block-disk-scan` lets the `reviewer-x` `find / -name x` through (exit 0, exit 2 after). The no-sidecar fallbacks and the slash `agent_id` case are regression pins, green before and after.

Still open: the sidecar path and field are undocumented Claude Code internals; if a release moves them the resolver silently falls back to name inference.

## Outcome

2026-10-21 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 12785ab2d7d8
- Changed: see commits
- Commits: 3b50756 T-0704: role hooks resolve a named teammate by its real agent type
- Check: 1 hook-selftest passes with a new reviewer-x case that fails when reverted: pass
- Check: 2 Outcome names where the real type was read from and how it was observed: pass
- Check: 3 check.py exits 0 and git diff --check exits 0: pass
