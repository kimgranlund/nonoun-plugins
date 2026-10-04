---
id: T-0186
title: "proposals/ folder and proposals.py mining runs and notes for candidate changes"
type: feature
status: done
size: M
priority: P2
depends: [T-0185]
created: 2026-10-01
---

## Goal
Repeated failures in past runs become evidence-backed candidate proposals in a folder, and nothing is applied without an eval.

## Intent
- Do: add `.sdlc/proposals/` with `AGENTS.md` (and `CLAUDE.md`) documenting the format and the procedures, and `plugins/sdlc-lite/scripts/proposals.py` with `scan`, `list`, `show`, `accept`, `reject`, and `promote`. `scan` reads every `runs.jsonl` and `<role>-<level>*.md` result under the ticket root and `.sdlc/notes.md` and finds: a step with two or more verifier fails; a task with a replan or a builder bump; the same `## For the next attempt` text (normalized) in two or more steps; a `plan defect:` verdict; and repeated `fix-now:` or `decide:` follow-ups with the same normalized text. Each pattern with at least two occurrences becomes a candidate at `.sdlc/proposals/<slug>/proposal.md` with front matter `id` (`P-NNNN`), `title`, `status` (`candidate`, `accepted`, `rejected`, `promoted`), `pattern`, `occurrences`, `created`, and `eval` (empty), and a body with `## Evidence` (one line per occurrence: the file path, the line or section, and the quoted text) and `## Proposed change` (a one-line description of what to examine, never a patch). `scan` is idempotent: a known pattern updates `occurrences` and evidence, never duplicates. `scan` reads sources only and writes only under `.sdlc/proposals/`.
- Transitions, each stamped and tested: `candidate -> accepted` (`accept <id> --eval <eval file>`) refuses unless the cited file is a valid eval under `.sdlc/evals/`; `candidate -> rejected` (`reject <id> --reason TEXT`); `accepted -> promoted` (`promote <id>`) calls `tickets.py new idea` with the proposal's title and evidence in the ticket body and records the ticket id; a proposal never moves backward and is never applied automatically.
- Non-goals: auto-merge, editing any plugin file, running experiments, changing model defaults.
- Done when: the selftest, negative controls, and common checks pass.

## Context
The run record format is `runs.jsonl` (one line per run: role, level, model, effort, cost, duration, file) next to each task and step handoff; result sections are fixed by the role contracts (`plugins/sdlc-lite/agents/*.md`, and `scripts/results.py` once T-0184 lands). `.sdlc/notes.md` holds follow-ups with `- <tag>: <text>` lines under `## T-NNNN: title (date)` headings. `tickets.py new <type> <slug> "title"` stamps tickets. Evals: `plugins/sdlc-lite/scripts/evals.py` (T-0185).

Selftest on seeded records in a temp project: a seeded two-fail step, a replan, a repeated next-attempt text, and a repeated follow-up each produce one candidate with the right evidence lines; a pattern seen once produces none; a second `scan` changes nothing (byte-identical tree); `accept` without an eval, with a missing file, and with an invalid eval is refused; `accept` with a valid eval passes and stamps the date; `promote` before `accept` is refused; `promote` after `accept` creates a ticket and records its id; a backward move is refused; the source files (`runs.jsonl`, results, `notes.md`) are byte-identical after any command (read-only on source). Negative control: a patched copy of `proposals.py` that writes to a source file or accepts without an eval fails the matching case. Live proof (`docs/validation/proposals-live-run.md`): run `scan` on this repository's own `.sdlc/` (read-only), list the candidates it finds with their evidence, and show the source tree unchanged and nothing under `plugins/` touched.

## Constraints
Read-only on source. Nothing applied without an accepted eval-backed proposal, and even then `promote` only files a ticket. No model default changes.

## Common rules
Rules for this ticket, from the user (2026-10-01): every folder this ticket adds is self-describing through its own `AGENTS.md` (with a `CLAUDE.md` containing `@AGENTS.md`), so a role that reads one file learns the system and no skill is added; progressive disclosure holds (a short router line in `.sdlc/AGENTS.md`, details in the folder); every status or state transition is covered by a selftest case that asserts the folder or file state and the stamped fields, plus a negative control that fails when the rule is removed; a live run proves the behavior with a negative control and is recorded in a dated `docs/validation/<name>.md` (environment, exact commands, evidence, limits; an arm that cannot run is recorded unverified, never replaced by a fixture); checks to run before merging locally: `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, and every selftest; update `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` layout list, and `plugins/sdlc-lite/AGENTS.md` when behavior or layout changes; do not bump versions, tag, push, or publish; generated Codex agent TOML is never edited by hand; no em dashes anywhere.

## Closed

2026-10-04: built by /chain in 3 steps, each verified; merged into main with check.sh, packaging, generate and proposals selftest green; no whole-branch verifier by the user's cost decision
