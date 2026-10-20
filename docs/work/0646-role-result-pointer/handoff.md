---
id: T-0646
title: "Every role writes its result file and ends with a one-line pointer"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A dispatched role's result reaches the conductor as a file, not as its final message: every role writes its result to the records dir path the brief names and ends with one line `<role> <status> <path>`, so completion notices stop carrying full results into the conductor's context.

## Intent
- Do: (1) In `dispatch.py prepare`, give every role the `Report file:` line verifiers get today, and replace "Your final message is saved verbatim as ..." with "End with one line: `<role> <status> <path>`" (status is the role's Status or Verdict value, else `done`). `record` keeps reading the file first; when the file is missing and stdin is a one-line pointer, it fails naming the missing path, as it does for a verifier. (2) In each shared role file (`agents/scout.md`, `researcher.md`, `architect.md`, `archaeologist.md`, `planner.md`, `plan-reviewer.md`, `builder.md`, `filer.md`, `ui-designer.md`), the output paragraph says: when the brief has a `Report file:` line, write the result there and end with the one-line pointer; otherwise the final message is the result as now. Regenerate the level variants with `claude_roles.py generate` and `codex_roles.py generate`. (3) `agents/conductor.md` step 3 and `skills/chain/SKILL.md:20` say the result is the file; read it only when the status needs action (fail, blocked, replan, no verdict).
- Non-goals: Codex `run.sh` behavior (it keeps the final message as the result, which the conditional wording preserves). Solo dispatches from `fanout.py prep` and `solo_run.py`. Changing any result format or `results.py` rule.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #10 (part a: role side and record side; the conductor reading rule rides along as doc text), ui-kit-neue audit 2026-10-20.
- Evidence: one 0.27.0 conductor session carried 528 completion notices, 1.52M characters, capped at 4,064 characters each; 109 repeated notices from 74 resumed roles; weighted cost about 98.7M cache_read (10.4% of the conductor total); idle notices triggered 273 conductor requests (148M).
- Verifier precedent: `plugins/sdlc-lite/scripts/dispatch.py:1125-1128` adds `Report file: <result>` and record fails when it is missing. The shared prompt line is `dispatch.py:1117` ("Your final message is saved verbatim as %s"). `record` reads the file first, then stdin, then the transcript: `dispatch.py:1544-1560`; a stdin with no `## ` heading is error text (`dispatch.py:1547-1555`), so a pointer line on stdin with no file is already a failure; make its message name the path.
- Selftest anchors that pin the prompt text: `dispatch.py:2424` (prepare parity with the run.sh dry run starts with "Your final message is saved verbatim") and `dispatch.py:3040` (verifier Report file). Update the parity case to compare the shared lines and allow the new per-role lines.
- Every role file already says "When the brief asks you to write a result file, write the same text there ...": `agents/builder.md:34`, `planner.md:85`, `scout.md:16`, `researcher.md:16`, `architect.md:18`, `archaeologist.md:16`, `filer.md:14`, `ui-designer.md:43`, `plan-reviewer.md:50`; `verifier.md:44` is the model to follow.
- Level variants are generated from `plugins/sdlc-lite/adapters/claude/levels.json` by `scripts/claude_roles.py` and from `adapters/codex/models.json` by `scripts/codex_roles.py`; never hand-edit them.
- Fits L2: one script change plus mechanical text in nine role files. If the builder finds record-side work beyond the message above, split the agent-text half into a new ticket rather than widening this one.
- T-0645, T-0667 and T-0659 also edit `conductor.md:41` or `chain/SKILL.md`; do not run them in the same wave.

## Constraints
No model or effort change. Result formats and `results.py` validation are unchanged. A role run without a `Report file:` line (Codex, bench) behaves as today.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases: a prepared builder, planner and scout brief each carries `Report file: <its result path>` and the one-line pointer instruction; record with the result file written and a one-line stdin pointer exits 0 and validates the file; record with no file and a one-line stdin pointer exits non-zero naming the result path. The brief cases fail with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0 and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
3. `python3 plugins/sdlc-lite/scripts/claude_roles.py selftest` exits 0.
4. `grep -L 'Report file' plugins/sdlc-lite/agents/{scout,researcher,architect,archaeologist,planner,plan-reviewer,builder,filer,ui-designer}.md` prints nothing.
5. `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0 (run.sh behavior unchanged).
6. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Outcome
- `dispatch.py prepare`: every brief now carries `Report file: <result>` (write the result there, headerless, validate with `--role <role> --headerless`) and `End with one line: <role> <status> <path>`, replacing "Your final message is saved verbatim as ...". The verifier keeps its run-rules line; its old separate Report file line folded into the shared one.
- `dispatch.py record`: with no file and a one-line stdin pointer it fails with `no result file at <path> (the <role> ended with the pointer ...)`.
- Role files (the nine listed plus `verifier.md`): conditional output paragraph; level variants regenerated (Claude and Codex).
- `conductor.md` step 3 and `skills/chain/SKILL.md`: the result is the file, read only when the status needs action. `hooks/block-role-write.sh` message names `Report file: <path>`.
- Checks: dispatch selftest, claude/codex generate --check, claude_roles selftest, run-selftest, hook-selftest, check.py, git diff --check, check-packaging all exit 0; criterion 4 grep -L prints nothing (BSD grep exit 1).
