---
id: T-0681
title: "merging main into an integration branch regenerates .sdlc/AGENTS.md and ROADMAP.md"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Bringing main into an integration branch without settling has one supported command that resolves the generated `.sdlc/AGENTS.md`, roadmap, router and notes files the way land does, so the conductor never hand-merges them.

## Intent
- Do: add `fanout.py settle <integration> --catch-up` (`plugins/sdlc-lite/scripts/fanout.py`, the settle parser near line 5675): it runs the merge half of `settle_forward` (near line 2749: find the integration worktree, refuse a dirty one, `merge_generated` under `<lanes dir>/merge.lock`, commit `catch-up: <main> <sha7> into <integration>`) and stops there: no `cover_at`, no fast-forward of main. Factor the shared half out of `settle_forward` rather than copying it.
- Do: add the `--catch-up` row to `## Arguments` in `plugins/sdlc-lite/skills/fanout/SKILL.md`, and one sentence in the fanout skill and in `plugins/sdlc-lite/agents/conductor.md` `## Merge ops`: merge main into an integration branch only with `settle --catch-up` or `settle --forward`, never a hand `git merge`.
- Do: a `fanout.py selftest` case: main and the integration branch each regenerate the roadmap after a new ticket, `settle --catch-up` merges with no conflict, the integration roadmap lists both tickets, and main's HEAD is unchanged.
- Non-goals: a git merge driver or `.gitattributes`; changing `settle --forward`.
- Done when: the criteria pass.

## Context
Source: GitHub issue #34, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- 10 `.sdlc/AGENTS.md` and 7 `docs/work/ROADMAP.md` conflicts when main was merged into the integration branch, across five merges.
- Partly fixed on main already: every plugin-driven merge regenerates these files. `merge_generated` (fanout.py:1607) resolves conflicts in `generated_files` (fanout.py:1596: roadmap, notes, router and mailbox files, from `layout_paths`, so `docs/work/ROADMAP.md` under `work_root: docs/work` is covered) and reruns `tickets.py roadmap`. Land uses it (T-0565, near line 1696), `settle --forward` uses it (T-0489, line 2787), `sync` uses it (line 3015), and `lanes.py` `forward` (line 1038, T-0595) uses it on close.
- The gap is a catch-up merge with no settle: `settle --forward` also runs cover and fast-forwards main, so a conductor that only wanted main's new tickets in the integration branch ran `git merge` by hand, and git cannot resolve generated files.

## Constraints
- A conflict outside the generated files aborts the merge and leaves both branches unchanged, as `settle --forward` does.
- `settle --forward` output and exit codes are unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with the new case, and the case fails with `--catch-up` removed.
2. `git grep -n -- "--catch-up" plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/agents/conductor.md` shows the Arguments row and both sentences.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.

## Outcome
- `fanout.py settle <integration> --catch-up` merges the current branch into the integration branch through the shared `merge_into_integration` (factored out of `settle_forward`: worktree lookup, dirty refusal, `merge_generated` under `<lanes dir>/merge.lock`, the commit), commits `catch-up: <head> <sha7> into <integration>` and stops: no cover, no fast-forward, worktree and branch kept. Nothing to merge exits 0; a running role refuses unless `--force`; `--catch-up` with `--forward` exits 2. `settle --forward` messages, commit subject and exit codes are unchanged.
- Docs: the `--catch-up` Arguments row and a sentence in `skills/fanout/SKILL.md`; a Catch-up line in `agents/conductor.md` `## Merge ops` (Codex conductor TOML regenerated).
- Selftest T-0681: main files T-0003 and the integration branch files T-0004, each regenerating the roadmap; `settle --catch-up` exits 0, the integration roadmap lists both, main is unmoved; a second run prints nothing to merge.
- Checks: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0; with `--catch-up` removed from the parser it exits 1 on both T-0681 expectations. `git grep -n -- "--catch-up" plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/agents/conductor.md` exit 0. `python3 plugins/sdlc-lite/scripts/check.py` exit 0. `git diff --check 6c2467b5` exit 0.
- Not changed: `skills/handoff-format/run-operations.md` `## Merge ops` (outside scope) has no catch-up line.
