---
id: T-0466
title: "reply_lint.py: score assistant replies against the author output rules, and run the 3-arm comparison"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A deterministic script scores assistant replies against the author output rules, so the output block of `.claude/agents/sdlc-lite-author.md` can be compared across sessions by numbers.

## Intent
- Do: add `plugins/sdlc-lite/scripts/reply_lint.py` (`score <transcript.jsonl> [--last N=20]`, `selftest`) that reads a Claude Code session transcript (the assistant text messages, not tool calls) and prints per-reply and total counts for: first line is a result or next action (not a preamble opener from the forbidden list); a closing `Next` line starting with Run, Open, Edit, Paste, Wait or Decide when work remains; sentences over 20 words; forbidden openers and closers (`Let me`, `I'll`, `Sure`, `Great question`, `Hope this helps`, `Let me know`); em and en dashes; a status line that starts with one glyph of the closed set (the 20 anchors of `docs/references/visual-anchors.md`), followed by an item and a reason; an emoji outside the set, more than 8 anchored lines in a reply, per-anchor use counts over the sampled replies (an anchor unused across the sample is listed for pruning), an emoji not at the start of a line, two emojis on one line, an emoji with no text after it, an emoji inside a code block; a last line starting with 👉 when work remains; unmarked inferences (a number with no unit or no source is informational only). Mechanical checks only; it never judges quality. The one rule list lives in `docs/specs/doc-standards/core.md` and `docs/planning/author-output-block-draft.md`; read the draft's section 1 for the version 2 text and section 3 for the scoring list. Selftest with an observed-red control per rule on fixture transcripts. Then run the comparison the draft describes (section 3): score 20 replies from the baseline session (transcript 66c988ad-c130-4e4f-9955-2f1db3b3b83c) and, once they exist, from a version 1 session and a version 2 session, and write `docs/reports/<date>-author-output-comparison.md` with the numbers, the two outcome signals (follow-ups like "any updates?" and clarifying questions per session) and the confound (sequential arms, different task mix).
- Non-goals: editing `.claude/agents/sdlc-lite-author.md` or swapping in the version 2 block (the maintainer decides); judging reply quality; a model or effort change.
- Done when: `python3 plugins/sdlc-lite/scripts/reply_lint.py selftest` exits 0 with each rule observed red before it; `reply_lint.py score` on the baseline transcript prints counts for all rules; `check.sh` exits 0; the comparison report exists for the arms that have transcripts and lists the missing arms as unverified.
- outcome metric: share of replies whose first line is a result or next action, and share ending in one `Next` action, version 1 arm versus baseline, before: unmeasured (this ticket records the baseline)

## Context
Origin: the maintainer asked how the author agent can apply a controlled language and linguistic techniques; version 1 of the block was applied in commit eae4ebd3; the tightened draft is `docs/planning/author-output-block-draft.md`. Session transcripts live under `~/.claude/projects/-Users-kimgranlund-Projects-nonoun-sdlc-lite/`. Related: `scripts/prompt_lint.py` (smell counts for prompt text), T-0461 and T-0447 (grammar), the i-have-adhd skill (`~/.claude/skills/i-have-adhd`) for the original rules.

## Constraints
Read-only against transcripts. No model call. No quoting of a transcript beyond the counted fragments in the report. No model or effort change.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/reply_lint.py selftest` exits 0 and prints a `red=` count above 0 and `green=0` for each of R-1 to R-14.
2. `python3 plugins/sdlc-lite/scripts/reply_lint.py score ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-sdlc-lite/66c988ad-c130-4e4f-9955-2f1db3b3b83c.jsonl --before 2026-10-12T12:55:18Z` exits 0 and prints totals for R-1 to R-14, per-anchor use counts and the prune list.
3. `bash plugins/sdlc-lite/scripts/check.sh` exits 0 and runs the reply_lint selftest.
4. `docs/reports/2026-10-12-author-output-comparison.md` holds baseline numbers that match criterion 2's output, the two outcome signals, the confound, and lists the V1 and V2 arms as unverified.
5. `.claude/agents/sdlc-lite-author.md` is unchanged and the script reads transcripts only (no write to them).
