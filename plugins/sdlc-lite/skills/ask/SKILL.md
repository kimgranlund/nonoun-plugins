---
name: ask
description: "Sweep the thread, task folder, tickets, run results, and notes for open questions and blockers, then ask them in one AskUserQuestion round with reasoned options, and take prose input when an answer needs it. Use for \"what is still open\", \"what is blocking us\", \"ask me what you need\", or before a long unattended run. NOT for guessing at questions nobody raised."
argument-hint: "[topic or task dir]"
allowed-tools: Read, Grep, Glob, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*), Bash(git log:*), Bash(git status:*), Bash(ls:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host's question mechanism. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (a topic, or a task dir such as `.sdlc/tickets/<slug>/`; empty means the whole session and the current task).

## 1. Sweep

Collect every item that needs the person, and cite where each came from. Look in:

- **The conversation:** a question asked and never answered, a decision deferred, an assumption stated and not confirmed.
- **The task folder:** `(gap: ...; default: ...)` lines in the handoff `## Intent`, unanswered `## Plan review` entries, builder `## Notes`, a verifier `fail` or `## For the next attempt`, filer `decide:` follow-ups.
- **Tickets and notes:** tickets with status `blocked` or a `## Deferred` note, and `.sdlc/notes.md` (`.sdlc/notes/notes.md` with `layout: topics`).
- **Run results:** a failed, interrupted, or `inherited red` result.
- **External blockers the thread names:** a rate or weekly limit, a missing credential, a permission denial, a failing check.

Run the searches before you ask anything; the conversation alone is not the sweep. Run every command from the repository root, never from the task dir: root and ticket paths come from `.sdlc/config`, and a supplied task dir only narrows what is reported. Let `<scope>` be the task dir you were given, else `.sdlc`.

- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc blockers` lists open tickets with status `blocked` or a `## Deferred` note in whatever layout the repo uses (flat, `ticket_root: tickets`, or `layout: topics`), never a closed or done one. With a task dir add `--scope <task dir>`. Read each hit. `none` means no ticket qualifies; an error naming a missing directory is a finding to report, not `Nothing open.`.
- `grep -rl -A1 '^## Verdict' --exclude-dir='.[0-9]*' <scope>` to list result files, and read any whose verdict line is `fail` or whose status is `blocked` or `inherited red`.
- `grep -rn --exclude-dir='.[0-9]*' 'gap:' <scope>` for unresolved gap lines, and read the notes file (`.sdlc/notes.md` (`.sdlc/notes/notes.md` with `layout: topics`)) and any `## Plan review` entries.

Never invent an item. Drop one already answered or made stale since it was raised. If nothing qualifies, say `Nothing open.` and stop.

## 2. Reason the options

For each item write 2 to 4 distinct options. Each option's description carries its consequence in one line: cost, risk, and what it unblocks. Put an option first marked `(Recommended)` only when evidence in the thread or repo supports it, and name that evidence in the description; otherwise leave the options unranked. Use the `preview` field when options are code, config, or layout to compare.

## 3. Ask once

Make exactly ONE AskUserQuestion call of 1 to 4 questions. Order blockers before nice-to-decide items, and the highest stakes first. With more than 4 items, ask the 4 most consequential and name the rest in the framing ("4 of 7 open"). Header chips stay under 12 characters. Never a second round in the same turn. If AskUserQuestion is unavailable in this session (a headless run, for example), ask the same round as numbered plain-text questions with the same options and consequences, then end the turn; say that it is plain text.

## 4. Take prose when an answer needs it

AskUserQuestion has no rich text field: the automatic "Other" box is plain text. When an item needs prose (a spec, a long answer, pasted content), say so in the question and include the option `Write it in chat`; choosing it ends your turn so the person can reply in full. For a long structured answer, offer to create a small file (for example under `.sdlc/` or `docs/`) for the person to edit, then wait. Never present the "Other" box as rich text.

## 5. Resolve

After the answers, record a decision where it belongs only when the person asked or a task folder clearly owns it (the handoff `## Intent` line or a line in the notes file). Then state in two lines what is now decided and what is unblocked. A declined question is recorded as declined, not asked again.

## Unattended

Headless (`SDLC_HEADLESS=1`, `SDLC_ROLE` set) or no person present: never call AskUserQuestion. List the open items and blockers as plain lines in the final report, each with its source and any stated default.

The shorter task-folder-only version of this sweep is `/sdlc-lite:open-questions`.
