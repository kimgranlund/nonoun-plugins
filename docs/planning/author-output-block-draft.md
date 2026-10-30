---
status: proposed
owner: maintainer
---
# Author agent output block, tightened draft

Status: proposal. Version 1 is applied in `.claude/agents/nonoun-author.md` (commit eae4ebd3). This draft tightens it with the controlled language of `docs/specs/doc-standards/core.md` and `prompts.md`. It is not applied: swap it in only for the next session that is meant to compare.

## 1. Version 2 text

```
## Output
Handles: Answer-first, Status-line, Anchor, Decision, Evidence, One-next.
1. Answer-first: the first line MUST be the result or the next action.
2. Status-line: state what happened, what still runs and what is the user's, in one or two lines. "Nothing to do until <X> reports." is a complete status.
3. Anchor: start a line with one emoji, first on the line, followed by the item and the reason; the emoji MUST be the first character of its line and appear once, never alone, never mid-sentence, at most 8 anchored lines per reply. State: 🟢 done, 🟡 attention, 🔴 blocked, ⏳ waiting. Direction: 👉 next action, ❓ decision for you, 🔁 retry. Event: 🏆 win, 🚀 shipped, 🔀 merged, 🎫 filed, 🧹 cleaned. Guard: ⚠️ likely problem, 🛑 stopped by a rule, 🐛 defect, 🔑 needs your authorization. Measure: 📊 metric, 💰 cost, ⏱️ time, 🧪 experiment. Meanings: docs/references/visual-anchors.md.
4. Decision: put each decision for the user in one AskUserQuestion call, 2 to 4 options, recommendation first.
5. Evidence: write one fact per sentence, at most 20 words, with ids and paths in backticks; mark anything unchecked [U]; give numbers with units and a source; write "unverified" for a check that did not run.
6. One-next: when work remains, the last line MUST be 👉 and one next action that starts with Run, Open, Edit, Paste, Wait or Decide and takes under two minutes.
7. Say the answer, then stop. Leave out preamble, recaps, closing offers and em dashes.
8. Depth: an analysis or design request gets the answer first, then the full reasoning under headers. Answer-first and One-next still apply.
9. Confirm a destructive action before taking it. This outranks every line above.
```

## 2. What changed from version 1

| Change | Technique | Version 1 |
|---|---|---|
| Handle line and a handle at the start of each rule | named handles, so an eval or lint can cite a rule | none |
| Three MUST gates: Answer-first, One-next, destructive action | RFC 2119 force on 3 gates, the salience budget | no modal force |
| Line 7 states the target (say the answer, then stop) and lists exclusions after it | affirmative framing | a prohibition list |
| One-next starts with a verb from a closed list | closed lead-verb vocabulary | an open verb |
| Line 5 merges the evidence rules | one rule per concept | rules 5 and 6 |
| Line 8 names the two rules that still apply in depth mode | a priority rule | an exception only |
| Line 9 ranks safety above the rest | explicit priority order | absent |

Emoji, added 2026-10-12 at the maintainer's request and extended the same day to 20 anchors in five groups (state, direction, event, guard, measure; the table is `docs/references/visual-anchors.md`): one per line at the start, never decoration, never in code, commit messages, tickets or documents, and never alone. Add a glyph to the set only with a measured use. Version 1 received the same change in `.claude/agents/nonoun-author.md`, so the V1 arm below includes it from that commit.

Not changed: the 20-word cap, the `[U]` mark and the AskUserQuestion rule.

## 3. How to compare

The three arms are sequential, not randomized, so the task mix differs and the result is suggestive only.

| Arm | Session | Output block |
|---|---|---|
| Baseline | the long session that ran before version 1 existed (transcript 66c988ad) | none |
| V1 | the next session in this repo | version 1, with the emoji set (commit named in the report) |
| V2 | a later session, after swapping in this text | version 2 |

Score a sample of 20 assistant replies per arm with `reply_lint.py` (T-0466): the first line is a result or next action; a closing `Next` line starts with a listed verb when work remains; sentences over 20 words; forbidden openers and closers; em dashes; a status line with a glyph, an item and a reason. Add two outcome signals per session: how often the user asks "any updates?" or "what do you need from me?", and how often a reply is followed by a clarifying question. Report the numbers and name the confound. A change that does not move a measure stays a suggestion.

## 4. Unverified

- Whether a MUST in an agent body raises compliance over plain imperatives (no measurement yet).
- Whether the session agent body is read again after `/compact` (the compaction prompt should point to it, not copy it).
