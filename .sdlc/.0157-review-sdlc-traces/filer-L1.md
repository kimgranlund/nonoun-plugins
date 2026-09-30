<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None. All 23 steps have a builder status of done and a verifier verdict of pass. One earlier attempt at step 2 was blocked by a plan defect, then re-planned and passed; it is kept in `step-2.superseded-1/`. Two gaps are listed under Follow-ups: the corpus named in the ticket's done-condition was never run, and the `overwritten-gate-log` branch was skipped in every selftest run.

## PR title
T-0157: add review-traces skill and traces.py to find sdlc-lite waste and bugs in run traces

## PR body
### Summary
This adds a read-only trace analyzer for sdlc run trails. `scripts/traces.py` runs stages 1 and 2: ingest and detect. Both are deterministic and make no model calls. A new `review-traces` skill drives stages 3 to 6: diagnose, verify, propose, and file behind one AskUserQuestion round.

- **Stage 1, `ingest`:** builds one attempt table. `*.attempt.json` is the primary key, so interrupted and failed runs that never reached `runs.jsonl` still get a row.
  - The table joins run rows by `attempt_id`, or by result name for legacy rows that lack one. A row that joins nothing gets a `legacy:<path>` id.
  - Other inputs are results, transcripts, fanout lane and gate logs, git history, tickets and the bench baseline.
  - Ingest is incremental through a cursor.
  - Outputs go to `.sdlc/runtime/traces/`, not into the analyzed repo.
- **Stage 2, `detect`:** runs four detector families over one shared thresholds table. Each finding carries evidence, a cause hint (layer and plugin file), a stable id and a severity. `clusters --max N` caps what reaches a model.
  - Escalation: replan loops, recurring findings, unchanged-verdict bumps, plan-defect refusals, wrong resume order, exit-3 results, statusless builders, verifiers with no verdict, attempts with no run row, stale `.running` markers.
  - Plan quality: criteria that never went red (opt-in `--rerun-criteria`, run in a detached throwaway worktree), contract dependents, scope prose.
  - Hygiene: stray worktrees, tracked runtime files, resets over a dirty tree, stale log lines by run id, overwritten gate logs.
  - Cost and transcript: cost per verified step against the bench baseline, builder attempts per step, polling loops, denials, rate limits.
- **Stages 3 to 6:** the skill covers these. The model-call cap is clusters + findings + 1, bounded by `--max N`. Non-sdlc-lite findings go to `report.md`. An unattended session (`SDLC_HEADLESS=1`) files nothing.

### Changes
- **New scripts:**
  - `plugins/sdlc-lite/scripts/traces.py`: thin entry.
  - `plugins/sdlc-lite/scripts/traces/`: package holding the row schema, the source readers, the store and cursor, the findings writer, the detectors, the CLI and the selftest.
- **New skill:** `plugins/sdlc-lite/skills/review-traces/SKILL.md`.
- **Wiring:**
  - `scripts/check.sh` runs `traces.py selftest`.
  - `agents/conductor.md` gains a route to `/sdlc-lite:review-traces`.
  - `skills/sdlc-lite/SKILL.md` gains a table row, so the Codex conductor definition `adapters/codex/agents/sdlc-conductor-l1.toml` is regenerated.
  - `skills/handoff-format/SKILL.md` documents `.sdlc/runtime/`.
  - `docs/maintenance/sdlc-internals.md` gains a `scripts/traces.py` section.
- **`.gitignore`:** adds `__pycache__/` and `.sdlc/runtime/`.

### How each was verified
- **Steps 1 to 23:** every step had its own builder and an independent verifier, and every verifier passed. The criteria were grep, selftest and scope-guard commands, which each verifier re-ran.
  - Step 1 verification mutated `table.py` in a temp copy: joining by `file`, changing the `legacy:` prefix, and forcing `superseded=False` each turned the selftest red.
  - Every detector has a positive fixture and a paired negative control (the same fixture minus the defect), registered as selftest cases.
- **Selftest:** `python3 plugins/sdlc-lite/scripts/traces.py selftest` gave exit 0 with 91 `ok:` lines and `traces selftest: PASS` at step 17.
- **Corpus case:** the selftest runs ingest and all four detector families over this repo's own `.sdlc` traces. It asserts attempt coverage and five known findings.
  - The builder's negative control changed an expected evidence path and the case went red. The verifier did not reproduce that control.
- **Model-free stages:** step 16 ran `ingest` and `detect` with fake `claude` and `codex` binaries first on PATH that exit 99. Both commands still exited 0.
- **Gates (step 23):** `bash plugins/sdlc-lite/scripts/check.sh` exited 0, and the verifier ran it twice. `python3 scripts/check-packaging.py` gave PASS. `git diff --check` was clean.
- **Codex parity:** `codex_roles.py generate --check` printed "verified" at step 22.
- **Not exercised:**
  - No negative control was run on the step 23 gates.
  - `shellcheck` is not installed on this host, so `check.sh` skipped it.
  - The `overwritten-gate-log` corpus branch printed `skip: corpus: overwritten-gate-log: .worktrees/fanout-night/logs is absent`, because that directory does not exist here.
  - The ticket's done-condition run against the gen-ui-system-svelte-lite traces of 2026-09-28 was not performed. See Follow-ups.

### Notes for review
- Step 2 was first blocked. The scope guard diffs from the chain base SHA, so a later step's guard saw files that earlier steps had created. The plan was reissued and step 2 then passed. The same guard shape is used in later steps' criteria.
- `ingest` now also walks `.`-prefixed closed task folders that hold a `handoff.md`, because the corpus case needed them.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `/sdlc-lite:review-traces` and `scripts/traces.py`. Ingest and detect turn a project's sdlc run traces into an attempt table and flag sdlc-lite waste and bugs, each with evidence and a cause hint, and spend no model calls. The skill then diagnoses, verifies, drafts tickets and files them only after approval. It never edits the analyzed repo. `traces.py selftest` now runs inside `check.sh`.

## Follow-ups
- decide: the done-condition run on the gen-ui-system-svelte-lite traces of 2026-09-28 (batch 3, T-0148 to T-0154) was never run; the architect could not find that repo or `sdlc-feedback-batch3.md` on this machine, and no step's artifacts show the run. Decide whether to supply the corpus or accept the synthetic and self-repo evidence.
- decide: the handoff asks for scout or archaeologist at L2 for diagnosis, but the architect found only L1 exists for those roles in `run.sh`. The artifacts do not show whether the skill settled this, so a person must decide whether to accept L1 or authorize a model change.
- fix-now: three `runs.jsonl` files sit in subfolders that ingest never walks (`.sdlc/.0106-extend-claude-agents-sdlc-lite/verify/`, `.sdlc/.0016-ticket-numbered-folders/old-step-3/`), so their 3 lines map to no row. Walk them in ingest or state the exclusion in the selftest and the internals doc.
- note: the `overwritten-gate-log` corpus branch has never run here, because `.worktrees/fanout-night/logs` is absent on this host.
- note: `detect` fails with a traceback if `events.jsonl` or `aux.json` is missing, since step 16 specified no error handling for that case.
