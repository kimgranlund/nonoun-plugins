# Handoff to sdlc-lite-author: review, upsert, and file `/plan compaction`

From: conductor session in ultimate-tokens (2026-10-12). Not filed anywhere. Nothing written to your repo.

## Ask
1. Review the spec below against the `/plan` skill ticket now in progress.
2. Upsert it: if a ticket for a compaction mode already exists, merge into it; else file one.
3. Mark it blocked on the `/plan` skill ticket. Run it only after that ticket is done and merged.
4. Tell the user (Kim) the ticket id and any spec changes you made.

## Goal
`/plan compaction [focus]` returns one prompt the user pastes into a manual `/compact <prompt>`. Prompt has high signal to noise: fixed shape, controlled language, pointers instead of copied content. It may also write a short, replaceable handoff section into a file the host reloads after compaction.

## Spec

### Mode: compaction
Arguments: `compaction [focus]`; focus is one phrase naming the next task; `compaction clear` removes the handoff section.
Output: one fenced prompt plus a one-line size note. Never run the compaction. Read-only except section 6, which writes only after the user picks /compact.

### 1. Sweep (read-only)
Collect from the session, citing ids and paths, never prose:
- Goal: the current ask, verbatim if under 20 words.
- Decisions: each with who (user or me) and date.
- State: branch, open PRs, running agents, dirty files, failing checks.
- Open: unanswered questions, held items, user-only actions.
- Rules: standing user instructions still in force.
- Next: the single next action.
Drop anything recoverable by one command (git log, gh pr view, ls); keep the command, not the output.

### 2. Classify
Each item gets exactly one tag:
- PIN: unrecoverable; loses work or breaks a rule if lost.
- POINT: recoverable; keep the locator only.
- DROP: narration, finished attempts, tool output, superseded plans, resolved errors.
PIN total at most 40 lines; over that, demote the oldest to POINT.

### 3. Write the prompt (controlled language)
- Fixed section order: GOAL, RULES, DECISIONS, STATE, OPEN, NEXT, DROP.
- One fact per line, max 20 words. No paragraphs.
- Allowed leading verbs only: KEEP, POINT, DROP, NEXT.
- Present tense, active voice, state not event: "PR #833 merged", not "we then merged".
- Literal identifiers (paths, ids, shas, commands in backticks). One term per concept; no synonyms.
- No hedges, no degree adjectives, no pleasantries, no em dashes.
- Each DECISION line carries its reason in 5 words or fewer.
- POINT lines: `locator -> what it answers`.
- DROP lists classes: `DROP tool output, retry history, superseded plans, resolved errors`.
- Last line: `NEXT <one action>`.

### 4. Check before returning
- Loss test on every PIN line: if gone, would the next turn err or re-ask? If not, demote.
- No line duplicates CLAUDE.md or AGENTS.md (they reload on their own).
- Prompt at most 60 lines; state the count.
- Never record an approval the user did not give in their own words (summaries drift "I assumed" into "user said").

### 5. Return
One fence, then `Run: /compact <paste>`.

### 6. Handoff section (optional, on by default)
Host detection, first match wins:
1. `CLAUDECODE=1` or `CLAUDE_CODE_ENTRYPOINT` set: host is Claude. Target `CLAUDE.local.md` at repo root (create if missing).
2. `CODEX_HOME` or `CODEX_SANDBOX` set, or the caller says Codex: host is Codex. Target `AGENTS.md` at repo root.
3. Neither: ask once.
Never write both.

Section key is the exact H2 `## Compaction handoff` (one per file):
- Replace: delete the existing H2 through the next H2 or EOF, then append the new one at EOF.
- Touch nothing outside that span.

Body, max 8 lines:
```
## Compaction handoff
Written <YYYY-MM-DD HH:MM> by /plan compaction. Obsolete after the next task starts: delete this section.
GOAL <1 line>
STATE <branch, open PRs, running agents>
OPEN <user-only items, max 3>
NEXT <1 action>
POINT <path -> what it answers>   (max 3)
```
Guards:
- Claude target: `git check-ignore CLAUDE.local.md` must pass; if tracked, stop and ask.
- Codex target: `AGENTS.md` is tracked. Run `git status -s AGENTS.md` first; if dirty, show the diff and ask. Never stage it. Remind the user to run `/plan compaction clear` before committing.
- Show the section in the reply; write only after the user picks /compact.
- At the start of every run, grep both files for the H2; if older than 24 hours, report it and offer to clear.
- Suggested extra: a pre-commit check that fails when `## Compaction handoff` appears in a staged file.

## Why these choices
- Verb whitelist and fixed order: the summarizer matches sections instead of improvising prose.
- POINT over copy: a re-read costs one command; carried content costs tokens every later turn.
- Skip CLAUDE.md and AGENTS.md content: reloaded after compaction anyway.
- Replaceable H2 plus timestamp: a handoff cannot stack or outlive its task (stale steering is a defect).
- `CLAUDE.local.md` for Claude: gitignored, no dirty tree. `AGENTS.md` for Codex is the only reloaded file there and is tracked, hence the guards.

## Unverified, please check
- Env vars for host detection (`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, `CODEX_HOME`, `CODEX_SANDBOX`): named from memory, not tested.
- That Claude Code loads `CLAUDE.local.md` after `/compact` in the version you target.
- Whether Codex rereads `AGENTS.md` after its own compaction.
- Where `/plan` keeps modes, so section numbering and the `clear` argument fit its router.

## Context
Raised in ultimate-tokens, where the `/plan` skill is not tracked; ticket id for the `/plan` skill ticket unknown to this session. In that repo `AGENTS.md` carries uncommitted Codex edits, which is why the dirty-tree guard exists.
