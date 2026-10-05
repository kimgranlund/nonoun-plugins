---
name: open-questions
description: "Clear a task's unresolved items (open questions, unconfirmed defaults, undecided choices) in one batched AskUserQuestion round at the end of a /chain run or session. Use for \"anything still open\", \"loose ends\", \"close this out\", or \"what's still pending\". NOT for ambiguity before a task starts (/clarify); NOT for filing new work as tickets (/ticket)."
argument-hint: "[task dir]"
allowed-tools: Read, Grep, Glob, AskUserQuestion
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (a task dir such as `.sdlc/<slug>/`; empty means the current task).

## 1. Collect

Scan for items still open:

- `(gap: ...; default: ...)` lines in the task handoff's `## Intent`, written by the /clarify flow.
- `## Plan review` entries in the task handoff that are still unanswered.
- Builder `## Notes`, verifier `## For the next attempt`, and filer output in the task dir that ask for a user decision.
- The newest filer result's `decide:` follow-ups, when /file has not asked about them yet: one question, which one becomes the one ticket, or none.
- Questions raised earlier in this session that got no answer.

Ground every item in something actually raised, and note where. Do not invent items.

Drop stale items: anything already asked in /file's own publishing round, or settled since it was raised.

## 2. Nothing open

If no item qualifies, report one line, `Nothing open.`, and stop.

## 3. Ask once

Make exactly ONE AskUserQuestion call: 1 to 4 questions, each with 2 to 4 options.

- Put an option first, marked recommended, only where a default or lean was actually stated (the `default:` of a gap line, or a stated lean in the source). Otherwise leave the options unranked.
- More than 4 items: ask the 4 most consequential and name the count of the rest in the question framing ("4 of 7 open; 3 minor left").
- Under /chain 7 (its close-out), the /file decide and publish questions ride in this same call and take two of the four slots, leaving two for the other items.
- Never a second round in the same turn.

## 4. Resolve

After the answers, resolve each item by name: one line per item saying what was decided and where it lands (the handoff line, the ticket, the step). A declined or skipped question is recorded as declined and is not re-asked in this session.

## Unattended

Headless (`SDLC_HEADLESS=1`, `SDLC_ROLE` set) or no person present: never call AskUserQuestion. List the open items as plain lines in the final report, each with its source and any stated default, or say `Nothing open.`

## Example

Good: one call, two questions. "Retry budget for the fetch step?" with options `3 (recommended, the gap default)` and `5`; "Keep the legacy flag?" with `Keep` and `Drop`, unranked because nobody stated a lean.

Bad: asking "Anything else you want changed?" (not grounded in a raised item), marking an option recommended with no stated default, or asking again a question the user declined earlier.

For a sweep that also covers blockers and reasons its options, use `/sdlc-lite:ask`.
