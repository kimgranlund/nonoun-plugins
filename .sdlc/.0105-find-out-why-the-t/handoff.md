---
id: T-0105
title: "Find out why the T-0072 background hook did not stop the run in..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0103
---

## Goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Context
Follow-up from T-0103 (run-result-format-check/filer-L1.md):

Find out why the T-0072 background hook did not stop the run in T-0103 (likely an Agent or Monitor background route); confirm after T-0076 ships.

Evidence, 2026-09-26: in an interactive Claude Code session, a plain Bash call (no run_in_background) running `check.sh` passed the default 120s timeout, and the harness reported "Command did not complete within its 120s timeout and was moved to the background". So Bash auto-backgrounds on timeout without the run_in_background flag, which PreToolUse hooks can't see. A likely fix is launchers setting BASH_DEFAULT_TIMEOUT_MS high, which bench.sh and dogfood do already, plus a check that run.sh and fanout set it too.

## Intent
Literal ask: find the cause of the T-0103 abandon and fix all three routes (folded in 2026-09-26, commit 579f73d).
Deltas:
- Constraints say "read-only investigation", but the later Context line sets scope to "find the cause and fix all three routes": defaulted: the later scope line wins; plugin edits in this repo are in scope; the peer repo stays read-only; no commits, pushes, or publishing.
- Cause: defaulted: archaeologist-L1.md is the recorded root-cause finding (Bash auto-backgrounds a foreground call past its timeout; no PreToolUse hook sees it; Monitor unguarded). No live repro is required for done.
- (gap: exact BASH_DEFAULT_TIMEOUT_MS value; default: match bench.sh's values.)
Do: fix the three routes in plugins/sdlc-lite:
  1. Auto-background on timeout: run.sh exports BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS high for every role run (same values as bench.sh) unless already set higher, and fanout.py sets them for lane drivers; a check proves both.
  2. Late task notification as last turn: run.sh saves the last result that is not a task-notification origin (log result JSON `origin.kind: task-notification`), or the last one holding the role's required heading, instead of a trailing notification turn; covered by run.sh's selftest.
  3. Background gate runs: hooks/block-background.sh also denies Monitor in headless sessions (hooks.json gets a Monitor matcher), with hook-selftest fixtures; agents/builder.md and agents/verifier.md say to run gates and tests in the foreground and never end the turn waiting on background work.
  Update docs that describe these (CLAUDE.md, .claude/agents/sdlc-lite-author.md, conductor/chain wording that lists what block-background denies) in the same change.
Non-goals: Workflow guarding; live repro of the peer run; any change in the peer repo; hook-live-probe live mode for Monitor.
Done when: scripts/check.sh is green, and each of the three fixes has a selftest or check that fails without it.

## Question
Why did the abandoned run end its turn with "Waiting for the background job to notify." without the T-0072 hook denying it? Which tool call backgrounded the work (Bash run_in_background, Agent, Monitor, Workflow, or something else), what did the hook see (was it installed, matched, was SDLC_ROLE/SDLC_HEADLESS set, which plugin version was loaded), and does the current hook set (plugins/sdlc-lite/hooks/hooks.json, block-background.sh at 0.11.1) cover that route? If not covered, name the gap precisely for a follow-up ticket.

## Evidence
- Abandoned run transcript: /Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/.worktrees/ports/.sdlc/sync-ports-2/step-1/builder-L2.log and builder-L2.md (peer repo, plugin 0.9.0 per T-0103). Read-only; never change that repo.
- Hook history in this repo: git log -- plugins/sdlc-lite/hooks/ (T-0072 commit 753993b, T-0076 commit 12c0c9f).
- T-0103 notes: .sdlc/.0103-run-result-format-check/filer-L1.md; T-0072: .sdlc/.0072-headless-background-abandon/; T-0076: .sdlc/.0076-headless-conductors-can-still-abandon/.
- Plugin cache for which version the peer loaded: ~/.claude/plugins (read only).

More cases from the peer (gen-ui, 0.11.1), same family: (1) a late task notification became the run's last turn ("stale monitor ... no action needed"), so run.sh saved that instead of the real report and lost the `## Verdict` (log result JSON: `origin.kind: task-notification`). Fix: run.sh takes the last result that is not a task-notification origin, or the last one holding the role's required heading. (2) A verifier ended its turn waiting on its own background gate runs. Fix: the hook denies Monitor in role runs, the verifier and builder prompts say to run gates in the foreground, and the launcher sets BASH_DEFAULT_TIMEOUT_MS high so Bash never auto-backgrounds. Scope of this ticket: find the cause and fix all three routes.

## Constraints
Read-only investigation. No edits in either repo, no git state changes.
(Superseded for this repo by the fix scope in Intent: the peer repo stays read-only; this repo gets the fixes, with no commits, pushes, or git state changes by roles other than the builder's working-tree edits.)
