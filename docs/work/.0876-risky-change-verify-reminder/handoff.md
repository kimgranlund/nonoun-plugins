---
id: T-0876
title: "In a Claude session, a commit or merge that touches a configured risky path reminds the agent once per change"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0870]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-20
branch: lane/T-0876-t0876
worktree: ../sdlc-lite.worktrees/T-0876-t0876
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
In a Claude session, a commit or merge that touches a configured risky path reminds the agent once per change to offer `/sdlc:verify`.

## Intent
- Do: add a non-blocking PreToolUse(Bash) hook, turned on by a `risky_paths:` config line.
- Non-goals: blocking a commit; detecting public exports by parsing code; a Codex equivalent (Codex runs no hooks).
- Done when: the criteria below hold.

## Context
- #98: live-mode rules say to offer `/sdlc:verify` once before a risky change, but "during a long session with breaking prop renames, a public-API change and a changelog check, the offer was never made". A comment adds a merge that moved auth screens without the offer. Ask: "when a commit touches paths configured as risky (`hash_bound:`, a `risky_paths` list) or changes a public export, remind the agent once, per change".
- Rule text: `plugins/sdlc/agents/live.md:16`. Hooks are registered in `plugins/sdlc/adapters/claude/hooks.json` (PreToolUse Bash list). Model the script on `plugins/sdlc/hooks/warn-handoff-edit.sh` (warn mode, exit 0). `tickets.hash_bound_globs` (`scripts/tickets.py:739`) parses `hash_bound:`; parse `risky_paths: <glob>...` the same way from `.sdlc/config`.
- The hook cannot tell a live session from a factory when the agent is declared in `.claude/settings.json` (`docs/references/claude-hooks.md`: `agent_type` is only seen with `--agent`), so it acts in any session with no role, but only when `.sdlc/config` has a `risky_paths:` line (opt-in; `hash_bound:` alone does not turn it on, so factory repos that declare hash-bound paths get no new reminders; a repo may list its hash-bound globs under `risky_paths:` too); it is silent for a role (`_role.sh`).
- Trigger: a `git commit` (staged paths) or `git merge <ref>` (paths from `git diff --name-only HEAD...<ref>`) in command position. Once per change: a marker under the git dir keyed by the sorted hit paths and the staged tree or the merged ref's sha. Output must reach the model without blocking; use the channel `claude-hooks.md` documents for that (for example `hookSpecificOutput.additionalContext`) and confirm it with the opt-in live probe, or report it unverified.
- Keep the hook linear in command length (`claude-hooks.md` line 68).
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `docs/references/claude-hooks.md` first.

## Do
1. Write `hooks/warn-risky-change.sh` and register it under the Bash matcher.
2. Add fixtures to `scripts/hook-selftest.sh`: a commit staging a risky path reminds once and a second identical call is silent; a non-risky commit is silent; a role session is silent; a repo with only `hash_bound:` and no `risky_paths:` is silent.
3. Add `risky_paths:` to the config docs, a section to `docs/references/claude-hooks.md`, a clause to `agents/live.md:16` naming the hook, and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- `bash plugins/sdlc/scripts/hook-selftest.sh` exits 0 with the new fixtures; with the path match stubbed to never hit, the reminder fixture fails (state the observed red).
- `bash plugins/sdlc/scripts/hook-live-probe.sh --selftest` exits 0.
- `python3 plugins/sdlc/scripts/check.py`, `python3 scripts/check-packaging.py`, `codex_roles.py generate --check` and `claude_roles.py generate --check` exit 0.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- The hook always exits 0.
- Claude only; say so in the doc section.

## Outcome

2026-11-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 1c83656083e8
- Changed: see commits
- Commits: cc6f12b T-0876: a hook reminds a live session to offer /sdlc:verify before a risky change (#98)
- Check: 1 hook-selftest exits 0 with the new fixtures; stubbed match fails the reminder fixture: pass
- Check: 2 `bash plugins/sdlc/scripts/hook-live-probe.sh --selftest` exits 0: pass
- Check: 3 check.py, check-packaging.py, codex_roles.py generate --check, claude_roles.py generate --check e...: pass
- Check: 4 `check.sh --fast` exits 0 and `git diff --check` clean: pass
- Follow-up: note: plugins/sdlc/scripts/hook-selftest.sh:1272 trap 'rm -rf "$wrt"'... -> notes.md
- Follow-up: note: additionalContext delivery to the model is unconfirmed by a live... -> notes.md
