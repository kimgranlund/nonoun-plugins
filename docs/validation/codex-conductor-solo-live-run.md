# Codex conductor solo live run

Recorded: 2026-10-04. One headless Codex conductor session was given only "Deliver the size-M ticket at .sdlc/duration/handoff.md, then close it." in a throwaway project. It is the first live run of a Codex conductor starting solo, with the gaps listed below.

## What ran

- Plugin code: commit `8684437` of this repository, plugin version 0.20.7; `codex-cli 0.160.0`, `Logged in using ChatGPT`.
- Throwaway project outside this repository: package `kit` with a stub `kit/d.py`, a README, a one-test suite, and one ticket edited to size M: add `parse_duration(text)` to `kit/d.py` with tests and a README paragraph. The 28 generated Codex agents were installed with `codex_roles.py install`. `steps.py lane` prints `solo` for it. The prompt names no lane, no solo command and no verifier.
- Hidden check [`hidden.py`](codex-conductor-solo-live-run/hidden.py), 12 cases, kept beside the project and named in no prompt.
- Command, with the Claude and `SDLC_*` variables removed first: `SDLC_BACKEND=codex SDLC_HEADLESS=1 python3 <plugin>/scripts/codex_exec.py conductor L1 "Deliver the size-M ticket at .sdlc/duration/handoff.md, then close it."` (the same launch `fanout.py` uses for a Codex conductor).

## Result

- Exit 0 in 3 minutes 51 seconds (`start.txt` 22:59:45, `end.txt` 23:03:36).
- Hidden check on the final tree: `hidden_check: 12/12 passed` ([`hidden-check.txt`](codex-conductor-solo-live-run/hidden-check.txt)). The change is `kit/d.py` +14, `tests/test_d.py` +36 and `README.md` +6 lines ([`final-state.txt`](codex-conductor-solo-live-run/final-state.txt), [`diff-kit-d-and-readme.txt`](codex-conductor-solo-live-run/diff-kit-d-and-readme.txt)).
- From its own agent files the conductor read the ticket, `skills/agent/SKILL.md`, `agents/solo.md` and the `.sdlc` entry file, ran `steps.py lane .sdlc/duration` (printed `solo`), wrote `Lane: solo because size M selects the solo workflow, with independent verification before closing.` into `skips.md`, claimed the ticket (`claimed_by: codex 2026-10-04`), had a solo agent deliver it (the ticket folder holds the [`solo-report.md`](codex-conductor-solo-live-run/solo-report.md) the solo wrote), ran one independent batched verifier, and closed the ticket. The command list is [`conductor-commands.txt`](codex-conductor-solo-live-run/conductor-commands.txt).
- Verifier: `run.sh` with `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent`. The result header and [`runs.jsonl`](codex-conductor-solo-live-run/runs.jsonl) both say role verifier, level L3, model `gpt-6-astra`, effort high, `shared_with_builder` false, transport subagent. Verdict pass ([`verifier-L3.md`](codex-conductor-solo-live-run/verifier-L3.md)): it ran 342 valid combinations and 23 malformed inputs and ran negative controls in memory.
- Close: `tickets.py close duration --reason "Delivered through size-M solo lane ..."` with the skips guard live; the handoff ends `status: done` and [`skips.md`](codex-conductor-solo-live-run/skips.md) holds the planner and filer `## Skipped` entries, once each, although the lane line appears twice (the cause was not traced; the conductor's command list shows one `steps.py lane` call, and the writer does not duplicate the `## Skipped` entries).

## Limits

- The solo is unmetered on this path. `runs.jsonl` holds only the verifier record: no `role solo` record exists, because the Codex conductor started solo through the native subagent path and not through `solo_run.py`. The 0.20.7 record says solo cost is written to the run records only when solo is started through the wrapper (`docs/validation/release-0.20.7.md` line 7), so the budget gate and the board do not see this solo.
- Which solo ran and on what model is not observed. The `codex exec --json` stream has no spawn item and no Codex rollout for this run was found under `~/.codex/sessions`, so `agent_role` and the model of the solo are unverified. That a solo agent ran rests on `solo-report.md` and the delivered diff; that it was `sdlc-solo-l2` on `gpt-6.1-sol` high is the tier table's declaration, not an observation. The conductor's model (`gpt-6-astra`, medium) is likewise from `models.json`.
- Independence is shown only as far as the run record says: verifier model `gpt-6-astra` against a solo declared as `gpt-6.1-sol`, `shared_with_builder` false.
- The verifier reported that creating its base worktree under `.git/worktrees/base` was blocked by the sandbox, so it claimed no baseline result.
- Usage for the conductor's own turn was 992,932 input tokens (949,504 cached) and 2,917 output tokens; the solo's and verifier's usage is not captured here. Codex reports no cost, so the spend is unknown.
- One run, one machine, one tiny size M ticket, in a project where the plugin was reached by absolute path. The interactive Codex conductor and size S and L tiers were not run.
