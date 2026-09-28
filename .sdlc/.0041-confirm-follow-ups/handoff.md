---
id: T-0041
title: "close confirms follow-ups before filing them"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Follow-up tickets are proposed to the user, or checked against the task's artifacts, before close files them, so already-answered and duplicate follow-ups never land.

## Intent
Literal ask: Follow-up tickets are proposed to the user, or checked against the task's artifacts, before close files them, so already-answered and duplicate follow-ups never land. Suggested: `close --dry-run` listing the proposed follow-ups, which /file shows through AskUserQuestion, and a duplicate check against existing tickets.
Deltas:
- How the user picks a subset after the dry run: defaulted: a new `close` option (for example `--skip 2,3`, 1-based indices from the dry-run listing) files every follow-up except the named ones; an index out of range refuses and writes nothing.
- What counts as a duplicate: defaulted: a follow-up whose normalized title (lowercase, words only) equals, or whose slug base equals, an existing ticket's normalized title or slug, any status; the dry run marks it `duplicate of T-NNNN (<slug>)`. Plain `close` (no `--skip`) skips a marked duplicate automatically and reports it, so a duplicate never lands even when nobody confirms. Fuzzy matching is out.
- "Checked against the task's artifacts" (already answered): defaulted: this is the conductor's judgment during /file, not code. /file tells the conductor to drop, via `--skip`, any follow-up the task's artifacts (plan, builder, verifier files) already resolve, and to say why.
- Unattended /file (no person to answer AskUserQuestion): gap: no user to confirm; default: file the non-duplicate follow-ups minus those the artifacts already answer, and state the choice in the report.
Do: In `scripts/tickets.py`: add `close --dry-run` (prints each proposed follow-up with its 1-based index, title, slug, and any duplicate mark; writes nothing; still applies the same refusals as a real close, such as open warnings without --force); add `close --skip N[,N...]`; skip marked duplicates on a real close and name them in the output; extend `selftest` so each new behavior has a case that fails if the behavior is removed. Update `skills/file/SKILL.md` step 3 to run the dry run first, drop artifact-answered items, confirm with AskUserQuestion (multiSelect, recommendation first) when a person is present, then close with `--skip`. Update the usage docstring and argparse help, `skills/ticket/SKILL.md`, the repo root `CLAUDE.md` tickets.py line, and `.claude/agents/sdlc-lite-author.md` if it describes close.
Non-goals: fuzzy or semantic duplicate detection; changing the filer agent's output format; changing `close --reason`; publishing.
Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes with new cases for dry-run-writes-nothing, --skip filing the rest, --skip out-of-range refusing, and duplicate auto-skip; `plugins/sdlc-lite/scripts/check.sh` passes; /file step 3 describes dry run, confirm, then close with --skip.

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. On 0.3.0, `close` on four small tickets filed 15 follow-ups, some already answered in the same session. Partly covered since 0.4.2: the filer now lists only follow-ups that change behavior or close a real risk (3 became 1 in a live rerun). Still missing: a confirm step (for example `close --dry-run` listing the proposed follow-ups, which /file then shows through AskUserQuestion) and a duplicate check against existing tickets.

## Constraints
What must not change. "None" if none.
