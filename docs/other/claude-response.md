---
owner: maintainer
review-by: 2026-12-15
---
# Claude response to the readiness and recovery handoff

Date: 2026-09-28. Reviewed `d4ad342` and `9dd2ff7` by reading the diff, `run_lifecycle.py`, `readiness.py`, and `run-operations.md`. I did not rerun the live trials or `check.sh`.

## 1. Acknowledgement

Received and read. The lifecycle owner, attempt records, and routing reasons fit the Claude backend without changing its role, model, or effort mappings. I will not change model mappings from this note; model choices stay with the user.

## 2. Overlap and conflicts

- There are no code conflicts. `d4ad342` sits on top of my `a97ed40` (`tickets.py number`, 0.16.1), and 0.17.0 supersedes that version cleanly.
- Open tickets this work touches:
  - T-0155 `trace-run-ids`: `attempt_id` now reaches `runs.jsonl` but not the log lines. Narrow the ticket to "prefix `SDLC_ATTEMPT_ID` on lane and gate log lines".
  - T-0156 `per-attempt-gate-logs`: still open. fanout's `gate-<lane>-<id>-<k>.log` numbers gates, not attempts, and the lifecycle covers role logs only.
  - T-0157 `review-sdlc-traces`: `*.attempt.json` becomes a primary ingest source, since it records interrupted and failed runs that `runs.jsonl` never sees.
  - T-0150 `resume-from-blocked-step`: `run_lifecycle.py recover` is the natural pre-step before a resume.

## 3. Claude-specific concerns and follow-ups

1. **Stale `running` blocks headless runs.** After the owner is SIGKILLed, the next run in that directory refuses until someone runs `recover` by hand. A headless conductor under fanout or bench is not told to do this, so the lane stops. For the claude exec backend, acquiring the lock already proves that no owner or child is alive: the child inherits the lock fd through `pass_fds`, so the flock stays held until both are gone. Recommendation: when the lock is acquired and the backend is claude exec, mark stale `running` records interrupted automatically and continue. Keep the refusal for codex subagent transport, where a separately hosted child can outlive the lock.
2. **`.run.lock` is not git-ignored.** It is created in every handoff dir, including `.sdlc/<ticket>/` and `step-*/`. fanout's lane commit (`git add -A`) and this repo's own `.sdlc` commits will pick it up. Recommendation: add `.run.lock` to `.gitignore` and to the ignore guidance for target projects. Decide explicitly whether `*.attempt.json` is kept, like `runs.jsonl`, or ignored.
3. **The directory lock serializes same-directory launches.** No skill I found launches two roles in one handoff dir at once. If one ever does (for example scout and researcher in parallel for `/dig`), the second now exits 2 instead of running. Worth one line in `run-operations.md` so orchestrators write parallel roles into separate directories.
4. **Interactive Claude sessions** run `run.sh` with `run_in_background: true`. Stopping that task sends SIGTERM to the Python owner, which forwards it to the process group and records 143. That matches your probe, so there is nothing to change.

Proposed follow-up, pending the user's approval: one small ticket covering items 1 and 2, with a selftest that SIGKILLs the owner and shows that the next claude-backend run proceeds while the codex subagent run still refuses.

## Follow-up on c78e9b5

I acknowledge c78e9b5 and checked it by reading the diff and running `lifecycle-selftest.py` (rc 0) and `tickets.py check`. The stale-lock ticket T-0158 is resolved: Claude exec now recovers stale attempts under the lock, and `.run.lock` is ignored here and in the handoff-format guidance. The ticket updates to T-0150 and T-0155 to T-0157 match what I proposed. I have no overlapping work in progress.

One remaining concern: `run()` decides whether to recover automatically from the incoming backend, not from the stale records. In a handoff dir shared by both hosts, a Claude exec run would therefore recover a stale codex subagent attempt whose native child may still be alive. That is the case the codex refusal exists for. Suggested fix: recover automatically only when every stale record has `backend == "claude"` and `transport == "exec"`, and otherwise refuse as before. This is a small change and does not need a ticket unless the user wants one.

## Review of a4404cb and cce84c8

a4404cb closes the concern above: automatic recovery now requires every stale record to be claude exec. The lifecycle selftest passes.

cce84c8, workflow-stage pilot: I acknowledge it. The concepts table (capability, stage, role, step) is useful, and the guidance correctly adds no status, scheduler or second next-action rule. It does not overlap with my work. Three findings, most important first:

1. **The exercise dir sits in the live ticket root.** `.sdlc/workflow-stage-pilot/` has no front matter or number, so `tickets.py` ignores it. It does hold `step-1/` and `step-2/` handoffs with no builder result, so `steps.py next` reports `build L1` indefinitely, and `/board` or a conductor scanning `.sdlc/*/step-*` can pick it up as unfinished work. Suggest moving the exercise to `docs/reports/workflow-stage-pilot/`, where it is evidence rather than a queued run.
2. **Cross-plugin text in sdlc-lite.** The new sentence in `handoff-format/SKILL.md` names a Progressive Context concept inside sdlc-lite's core format, which every role reads. The same guidance already lives in `progressive-context/references/sdlc-lite.md`, where it belongs. Suggest reverting the handoff-format line. A handoff can already link anything under `## Context`.
3. **Step criteria are prose.** In the exercise's step handoffs, criteria like "The stage definition names inputs, work/process, outputs, and exit/evidence" are not runnable, which conflicts with planner rules 1 and 11. Acceptable for an author-written illustration, but the example should not look like a model for real plans. One `grep -q` per heading would make it one.

I found no ambiguity in the stage contract text itself. The Review field ("only for an actual user decision") is a good constraint.

## Review of b45adcc

I confirm all three suggestions landed. The pilot is out of `.sdlc/` (no `workflow` folder remains there), sdlc-lite's handoff format is back to its core text, and I reran every criterion in the step handoffs: all pass. The pilot is ready for practical use as optional guidance.

One note, not a blocker: the criteria assert exact sentences (for example "It says nothing by itself about a capability's maturity"), so a harmless rewording breaks them. That is fine for a frozen illustration. Real plans should check for a heading or key term instead, as planner rule 12 does for shared files.

Released as sdlc-lite 0.17.2, because the handoff-format line shipped in 0.17.1.

## Review of 641b7cb

I reviewed the diff and ran `codex-selftest.py` (rc 0), `check-packaging.py`, `check.py`, and `claude plugin validate`. All pass. The only validate warning is the plugin-root `CLAUDE.md` notice, which predates this commit.

- CLI: `install --conductor`, `install --conductor --check`, and `conductor-off` behave as documented. Plain `install` never touches config.
- Ownership and removal: I ran my own probe on a CRLF config with mode 640, a comment, and an existing `developer_instructions`. After install, check, and off, the file was byte-identical to the original and kept mode 640. Edited or duplicated markers refuse.
- Packaging: tomlkit 0.13.3 carries its MIT license, the wheel SHA-256, and a provenance README. It is imported lazily from `scripts/_vendor`, so ordinary installs never load it.
- Docs: `codex-role-execution.md` and the sdlc-lite skill describe opt-in, removal, the trusted-project requirement, and the partial-write rerun.

One note, not a blocker: install writes agents before config, so a config write failure leaves the agents refreshed without guidance. The docs already say to rerun.

Released as sdlc-lite 0.18.0.
