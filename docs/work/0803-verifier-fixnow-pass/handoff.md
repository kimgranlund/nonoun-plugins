---
id: T-0803
title: "a full verifier passes a build whose fix-now note says the Goal is not met"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A verifier never returns `pass` while its own note says the change does not do what the handoff Goal asks; a vacuous criterion that lets such a build through is a fail with a `plan defect:` line, as the diff-scoped brief already does.

## Repro
1. The T-0801 control: Goal "title_case capitalizes each word", criterion `grep -q "def title_case" textkit.py`, build `def title_case(s): return s`, Outcome claiming `Hello World`.
2. `dispatch.py prepare verifier L1` with the full brief (no `Scope: diff` line).

## Expected
Verdict `fail`, naming the vacuous criterion.

## Actual
`docs/reports/2026-10-28-speed-experiment.md` (control row): the full verifier returned `pass` with `fix-now: textkit.py: ... prints hELLO wORLD, not the Goal's Hello World; the Outcome claim is false and criterion 1 does not test behavior`. The diff-scoped verifier on the same build returned `fail`.

## Context
Verifier contract `plugins/sdlc-lite/agents/verifier.md` (notes vs verdict; `fix-now`), and the `Scope: diff` wording in `plugins/sdlc-lite/scripts/dispatch.py` (SCOPE_DIFF), which produced the fail. One sample only.

## Acceptance criteria
1. `plugins/sdlc-lite/agents/verifier.md` says a criterion that passes on a build contradicting the Goal is vacuous and fails the verdict with a `plan defect:` line; generated agents regenerate (`check.py` exits 0).
2. `python3 scripts/check-packaging.py` exits 0.

## Constraints
Wording change only; model and effort tables unchanged.

## Outcome
`plugins/sdlc-lite/agents/verifier.md` now says a criterion that passes on a build contradicting the Goal is vacuous: the verdict is `fail` with a `plan defect:` line, never `pass` with a `fix-now:` note. Regenerated the Claude verifier-L1/L2/L3 agents and the six Codex verifier TOMLs.
Checks: `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `claude_roles.py generate --check` and `codex_roles.py generate --check` exit 0; `git diff --check` clean. Not run: a live verifier on the T-0801 control (one-sample repro; wording change only).
