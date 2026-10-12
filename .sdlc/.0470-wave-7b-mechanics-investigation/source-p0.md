# P0 for sdlc-lite-author: wave 7b took about 36 hours; investigate the plugin mechanics behind it

Filed by the ui-kit-maison conductor, 2026-10-12. Evidence is in this repo: `.sdlc/tickets/0439-integration-wave-7b/` (plans v1 to v4, step-1, step-1.superseded-1, step-2.superseded-1/2), `.sdlc/notes.md` (dated entries 2026-10-11 and 10-12), `.sdlc/fleet-retro-2026-10-12-00.md`. Collector numbers: 814 runs, $577.83 over the window.

## Scope fence (do not interfere)
You are doing linguistic and output improvements. This ticket is about MECHANICS only: gates, lint, record, dispatch, locks, criteria semantics, liveness. Change no prompt wording, report format text or tone. If a fix needs a wording change, record it in the investigation report and leave it for your language pass.

## Ask
Run a Fable XHigh investigation (one agent, read-only first, host agent `sdlc-lite-author` as the owner) and return: for each finding below, confirm or refute from the plugin code, name the file and rule at fault, and propose the smallest change with a red check. Start with the host agent / conductor definitions, then `dispatch.py`, `steps.py`, `gate_lock.py`, `fanout.py`. Do not touch this repo.

## Findings (all observed in wave 7b, T-0439)
1. Criteria encode history, not state. Plan criteria grep for exact commit subjects and counts; the sequence changed four times, so step criteria went stale and every role reported `blocked` or `fail` for a plan defect. Need: a criterion form on state (subject contains X, tree equals Y) and a supported way to supersede stale criteria without hand-rewriting a handoff.
2. No way to mark a criterion `[owner: integration]`. Four L2 verifiers (T-0468, T-0474, T-0475, T-0476) wrote Verdict fail only because criterion 5 (owner generation, installed proof) is deferred. `record` treats the header verdict as final. Need: a deferred-owner clause that `record` and `steps.py next` accept as pass-with-deferral.
3. `dispatch.py prepare` link lint refuses a step handoff that cites a path its own run will create (`evidence/phase-b`, `completion.json`, `full-check.log`) and false-positives on python string concatenation (`P + '/.sdlc/...'` read as `//.sdlc/...`). Only an unlisted placeholder directory unblocked it. Need: a way to declare outputs the step creates, and a lint that ignores concatenated expressions.
4. `dispatch.py record` fails "no result" when a role ends without writing its report file, although the final message exists in the sub-agent transcript. I recovered it by hand 6+ times. Need: `record --transcript` fallback to the last assistant message.
5. Silent running agent is invisible. `0439-s1-builder-L4-2` showed "running" for 2.5 hours with no transcript activity and no reply to SendMessage. Need: a liveness check (last transcript write age) in `dispatch.py status`/`ListAgents`, and a documented stop-and-redispatch path that closes the open attempt.
6. Resumed work trips the red-checkpoint. A second builder on an already-committed branch gets `retrospective/missing` for `(red)` criteria whose red state was produced by an earlier attempt. Need: red controls bound to the step, not the attempt, or an explicit resume mode.
7. Gate lock: legacy holders from an older plugin version hold slots the lock "never touches", other repos queue on the same 2 slots, and a queued final gate waited about 70 minutes. Need: legacy-holder expiry, per-repo fairness or priority, and queue ETA in `gate_lock.py status`.
8. `fanout.py` cannot run when `.sdlc` is gitignored (handoffs not committed). This repo declares that hazard in AGENTS.md; I hand-ran every lane with `solo_run.py` plus an Agent spawn. Need: fanout reading tickets from the primary checkout path.
9. The dispatch prompt names no worktree for roles that must work in a lane worktree; I had to append a "Verification target" section to each handoff (which changes the handoff hash and forces a new `prepare`). Need: `prepare --tree <worktree>`.
10. `steps.py widen` refuses ("criterion lines have a git diff --name-only span with a grep -v allow-list") on perfectly ordinary scope criteria, forcing hand edits under a recorded scope decision.
11. The lane gate (`.sdlc/lane-gate.sh`, repo-owned) omits `check:adapters` and `check:renderers`, so two verifier fails (T-0467, T-0469) were test bugs a gate stage would have caught. Out of plugin scope unless you ship a gate template: say so.
12. Output paths in a worktree-per-lane model: the Bash tool's `run_in_background` hook, 10-minute foreground limit and a 75 to 90 minute gate force a nohup-and-poll pattern that every role reinvents. Need: a documented long-gate recipe.

## What I measured (collector, ticket records)
- Wave 7b: created 2026-10-11, still gating 2026-10-12 13:15 PDT; 4 plan versions (planner $34.07), 4 step-1 builder attempts plus 2 earlier, 3 Codex L3 rounds.
- Verifier is the largest spend: 303 runs, $216.35, 867 min.
- 477 of 814 runs unmetered.

## Done when
A written investigation report at `.sdlc/` of the plugin repo with each finding marked confirmed, refuted or unchecked, a ranked change list with red checks, and the first three changes landed or ticketed. Report back to this conductor with one line.
