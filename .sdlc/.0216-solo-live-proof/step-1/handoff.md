## Task goal
A recorded live run shows the `solo` agent delivering a real size-M ticket end to end, with one independent batched verifier, on Claude Code and Codex. Read `.sdlc/0216-solo-live-proof/handoff.md` (Intent, Constraints) first.

## Step 1: Run solo on a size-M fixture on both hosts and record the evidence
level: L3

### Read first
- plugins/sdlc-lite/agents/solo.md
- docs/validation/messages-live-run.md (an earlier live run: copy its structure and evidence style)
- plugins/sdlc-lite/scripts/steps.py (the lane section: how lane prints its result)

### Do
Make the smallest change that meets the criteria. This step adds only files under docs/validation/ and one line in docs/README.md. Do not change any agent, table or lane logic (report defects as notes). Report blocked instead of looping. Budget about $15; run each arm once and record a failure honestly as a limit.
1. Build a small throwaway Git project outside this repository with `mktemp -d`: a tiny Python library (a few files) plus a size-M ticket handoff (`.sdlc/<slug>/handoff.md` with front matter `size: M`) asking for one real change that touches two or three files, with a hidden check script kept OUTSIDE the project dir that the delivering agent never sees. Run `python3 plugins/sdlc-lite/scripts/steps.py lane <ticket dir>` there with this repository's plugin root; it must print `solo` first. Save that output.
2. Claude arm: copy the project, then deliver the ticket with the solo agent at tier M (Claude Sonnet, effort xhigh) in a headless session: `claude -p --plugin-dir <this repo's plugins/sdlc-lite> --agent sdlc-lite:solo --model sonnet --effort xhigh "<typed brief: the ticket path, files, check commands, done criterion>"` with the throwaway project as the working directory. Tier M ends with one independent batched verifier through `scripts/run.sh verifier <level> <task dir handoff>` on a different model family than the builder (the solo agent file says how; the runner's family rule applies to a task-dir verifier). Record models and efforts from the run records (`runs.jsonl`, result headers, session log), not from memory.
3. Codex arm: install the generated agents into a fresh copy (`python3 plugins/sdlc-lite/scripts/codex_roles.py install <project copy>`), then deliver the same ticket with the `sdlc-solo-l2` agent (gpt-6.1-sol, high) through Codex (`codex exec`, native subagent or the standalone form the earlier Codex live runs in docs/validation/ used), and run one independent batched verifier on a different model. Record models from the Codex rollout files.
4. For each arm record: the lane output, tier and model per host, whether the hidden check passed, the verifier verdict, cost and wall time (from the session or run records), and any defect in solo.md or the lane as a note. Raw evidence goes in docs/validation/solo-live-run/ (logs trimmed to the relevant lines, run records, the hidden-check output).
5. Write docs/validation/solo-live-run.md (Environment with versions and the commit under test, Method, one section per arm, Limits) and add one line linking it in docs/README.md.

### Acceptance criteria
- `test -f docs/validation/solo-live-run.md`
- `grep -q "solo-live-run.md" docs/README.md`
- `grep -qi "claude" docs/validation/solo-live-run.md && grep -qi "codex" docs/validation/solo-live-run.md`
- `grep -q "gpt-6.1-sol" docs/validation/solo-live-run.md`
- `test -d docs/validation/solo-live-run`
- `git diff --check main -- plugins docs`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `bash plugins/sdlc-lite/scripts/check.sh`
