# Author output block comparison, 2026-10-12

Ticket `T-0466`. Tool: `plugins/sdlc-lite/scripts/reply_lint.py` (mechanical counts, no quality judgment, no model call). Plan: `docs/planning/author-output-block-draft.md` section 3. Only the baseline arm has a transcript. The V1 and V2 arms are unverified.

## Arms

| Arm | Session | Output block | Status |
|---|---|---|---|
| Baseline | transcript 66c988ad, the last 20 replies stamped before 2026-10-12T12:55:18Z (commit `eae4ebd3`) | none | scored |
| V1 | next session in this repo, after `eae4ebd3` and the anchors of `33af8145` | version 1 | unverified: no transcript exists yet |
| V2 | a later session after swapping in the draft text | version 2 | unverified: not swapped in, no transcript |

Command: `python3 plugins/sdlc-lite/scripts/reply_lint.py score <transcript>.jsonl --before 2026-10-12T12:55:18Z`. A reply is all assistant text between two user messages on the main chain (sidechains, tool calls and thinking skipped). The 20 replies span 2026-10-12T11:47Z to 12:53Z.

## Baseline numbers (20 replies)

| Rule | Replies flagged | Occurrences |
|---|---|---|
| R-1 first line is a forbidden opener | 1 of 20 | 1 |
| R-2 work remains, no `Next` / `👉` + listed verb last line | 10 of 20 | 10 |
| R-3 sentences over 20 words | 20 of 20 | 67 |
| R-4 forbidden closer on the last line | 0 of 20 | 0 |
| R-5 em or en dashes | 0 of 20 | 0 |
| R-6 anchored line without item and reason | 0 of 20 | 0 |
| R-7 emoji outside the closed set | 0 of 20 | 0 |
| R-8 more than 8 anchored lines | 0 of 20 | 0 |
| R-9 emoji not at line start | 1 of 20 | 3 |
| R-10 two emojis on one line | 1 of 20 | 1 |
| R-11 emoji with no text after it | 0 of 20 | 0 |
| R-12 emoji in a code block or span | 3 of 20 | 5 |
| R-13 work remains, last line not `👉` | 10 of 20 | 10 |
| R-14 bare numbers and unhedged claims (informational) | 16 of 20 | 63 |

Anchor use over the sample: 🟢 8; the other 19 anchors 0, all listed as prune candidates. That list is not a finding: the set was extended the same day, so the baseline could not have used the new anchors.

Outcome metric (T-0466), baseline: first line not a forbidden opener 19 of 20 (95%); work remains in 10 of 20 replies and 0 of those 10 end in one `Next` action (0%), so 0 of 20 replies overall. Version 1 and version 2 values: unverified.

## Outcome signals, baseline window

| Signal | Value | Source |
|---|---|---|
| User follow-ups ("any updates?", "status", "what's next") | 1 of 20 user messages in the window | regex over user text, crude |
| Replies ending in a question mark (clarifying proxy) | 9 of 20 | last character of the reply |
| Both signals for V1 and V2 | unverified | no transcript |

## Confound and limits

- The arms are sequential, not randomized, so the task mix differs between sessions. The result is suggestive only.
- R-2, R-13 and the work-remains test are a proxy (state or guard anchors, or words such as pending and remaining). A reply it misreads moves both rules together.
- R-1 checks the forbidden list only. It cannot tell a result from a restated question.
- R-14 counts bare numbers and hedge words with no `[U]` mark. It is informational and drives no flag.
- The follow-up regex and the question-mark proxy are crude counts, not a classification of intent.
- The baseline predates the anchors, yet its 8 uses of 🟢 come from the user-level status convention, not from version 1.
- A measure that does not move stays a suggestion; nothing here changes `.claude/agents/sdlc-lite-author.md`.

## Next

Score the V1 session when its transcript exists, then the V2 session after the swap, with the same command and window size.
