---
status: proposed
owner: maintainer
---
# Compaction prompt: `/sdlc-lite:report compaction`

Status: proposal. Raised in ultimate-tokens as `/plan compaction` (handoff of 2026-10-12, kept in `.sdlc/0465-compaction-prompt/source-handoff.md`). This version is the original spec reviewed and aligned with the report skill (T-0460), the controlled language (T-0461), the document standards (T-0447), the lane lifecycle and the resolve-and-ship posture (T-0464).

## 1. Answer

One command returns one prompt that the person pastes into a manual `/compact <prompt>`: fixed shape, controlled language, pointers instead of copied content. It never runs the compaction. Most of its content is derived by script from the same record as `/sdlc-lite:report`; only goal, rules and decisions come from the conversation. The original optional handoff file write is cut to a Claude-only, off-by-default step, and the `AGENTS.md` write is dropped.

## 2. What changed from the original, and why

| # | Original | Now | Reason |
|---|---|---|---|
| 1 | A mode of `/plan` | A view of `report`: `/sdlc-lite:report compaction [<focus>]` | The sweep fields (state, open, next, running agents, dirty files) are the `session-status/1` record. `/plan` kinds produce plans (steps, doc, goal, campaign, fanout); a compaction prompt is a state report written for a summarizer. T-0462 (plan merge) does not need to host it. If it later chooses to, `/plan compaction` is an alias with the same contract |
| 2 | The model sweeps state from the session | The script derives STATE, OPEN and NEXT from the report record, `git` and `gh`; the model supplies GOAL, RULES and DECISIONS | A script cannot drift "I assumed" into "user said", and the state is the same as `report` shows. `next` carries `planned` or `intended` |
| 3 | Writes `AGENTS.md` for Codex | Dropped. The Codex prompt ends `NEXT run /sdlc-lite:report summary` | Root `AGENTS.md` is a tracked entry file with a managed block; transient state in it is a stale-context defect, dirties the tree and can be committed. The snapshot under `.sdlc/runtime/report/` is already the replaceable, ignored state |
| 4 | Handoff file on by default | Claude only, off by default (`--write-handoff`) until the reload is verified (section 8) | Four assumptions were untested; two are removed by item 3 |
| 5 | Verbs KEEP, POINT, DROP, NEXT; present tense | Kept for the instruction lines; fact lines use the status grammar of `core.md` | Two jobs, two forms (section 4) |
| 6 | No evidence marks | Each DECISION and RULE carries a pointer to its turn or `[U]` | The retro rule: a claim with no pointer is `[U]` |
| 7 | Six sections of guards | MVP is sections 1 to 5 of the original; the handoff write is a later step | Resolve and ship; add the guards when the reload is shown to work |

## 3. Command and arguments

`/sdlc-lite:report compaction [<focus>] [--clear] [--write-handoff]`. Hint form per the skill hint standard (T-0463): `compaction [<focus phrase>] [--write-handoff] | compaction --clear`. `<focus>` is one phrase naming the next task. `--clear` deletes the handoff section and nothing else. Output: one fenced prompt, a size note (`lines: N of 60`), and `Run: /compact <paste>`.

## 4. Derivation

| Section | Source | By |
|---|---|---|
| GOAL | the current ask, verbatim if under 20 words, else one sentence | model, with a transcript pointer |
| RULES | standing user instructions of this session that are not in `CLAUDE.md` or `AGENTS.md` | model, each `[U]` unless quoted |
| DECISIONS | who (user or agent), date, reason in 5 words or fewer | model, each with a pointer to the turn |
| STATE | branch, dirty files, open PRs, running agents and lanes, failing checks, the open ticket and its status | script: report record, `git status`, `gh pr list`, `dispatch.py status` |
| OPEN | unanswered questions, held items, user-only actions | script: report `needs` plus the transcript's last open question |
| NEXT | the single next action, `planned` or `intended` | script: `next` of the report record |
| POINT | `locator -> what it answers`: the ticket handoff, the plan doc, `plan-state.json`, the report snapshot | script |

Drop what one command recovers: keep the command, not its output. Plan docs and ticket folders already survive compaction, so the prompt points to them and never copies them.

## 5. Grammar (controlled language)

Two jobs, one form each.

| Job | Form | Example |
|---|---|---|
| Facts to keep | one fact per line, at most 20 words, present tense, active, state not event, literal identifiers in backticks | `PR 833 merged` |
| Instructions to the summarizer | imperative, leading verb from the closed list `KEEP`, `POINT`, `DROP`, `NEXT` | `DROP tool output, retry history, superseded plans, resolved errors` |

- Fixed order: GOAL, RULES, DECISIONS, STATE, OPEN, NEXT, DROP. The last line is `NEXT <one action>`.
- One term per concept, from `docs/references/glossary.md`; aliases are a lint warning.
- No hedges, no degree adjectives, no pleasantries, no em dash.
- A DECISION line: `<who> <date> <decision> | <reason, 5 words or fewer> | <pointer>`.
- Identity first, imperatives last: the first line states what the prompt is (`Continue T-0465; keep the sections below`), per the `prompts.md` card.
- Approvals appear only as the user's own words in quotes; an inferred approval is marked `[U]`.

## 6. Checks before returning

- Loss test on every PIN line: if it is gone, would the next turn err or re-ask? If not, demote it to POINT.
- No line duplicates `CLAUDE.md` or `AGENTS.md` (script compares lines).
- Prompt at most 60 lines, PIN items at most 40 lines, with the count stated.
- A lint script checks line length, the verb list, section order, the 60 and 40 caps, em dashes, duplicated entry-file lines, and a DECISION without who, date and pointer.

## 7. Handoff file (optional, Claude only, off by default)

- Target `CLAUDE.local.md` at the repo root, created if missing, only with `--write-handoff`, and only after the person picks `/compact`.
- Guard: `git check-ignore CLAUDE.local.md` must pass. It does not pass in this repository today, so the build adds the `.gitignore` entry (or the guard stops and says so).
- Section key is the exact H2 `## Compaction handoff`, one per file. Replace the span from that H2 to the next H2 or end of file, then append the new one. Touch nothing else.
- Body at most 8 lines: `Written <YYYY-MM-DD HH:MM> by /sdlc-lite:report compaction. Delete this section when the next task starts.`, then GOAL, STATE, OPEN (max 3), NEXT, POINT (max 3).
- At the start of every run, look for the H2; if it is older than 24 hours, report it and offer `--clear`.
- Codex: no file write. Verification of whether Codex rereads `AGENTS.md` after its compaction is not needed once the write is dropped.

## 8. Verified and unverified

| Claim | State |
|---|---|
| `CLAUDECODE=1` and `CLAUDE_CODE_ENTRYPOINT=cli` are set in a Claude Code CLI session | verified in this session [V] |
| Codex host variables (`CODEX_HOME`, `CODEX_SANDBOX`) | unverified [U]; only needed for host detection, which the Codex path no longer uses beyond printing the final line |
| Claude Code loads `CLAUDE.local.md` after `/compact` in the targeted version | unverified [U]; gates `--write-handoff`; the build tests it live once and records the result |
| `CLAUDE.local.md` is gitignored here | false today: `git check-ignore` printed nothing [V] |

## 9. Measurement

No data yet shows that a controlled compaction prompt helps. The build records a replay: fixture transcripts (a plan-doc run, a lane wave, a design thread) compacted with the prompt and with a free `/compact`, then the next 5 turns scored for re-asked questions, a violated standing rule, a lost decision and tokens carried. The report names the result and marks it unverified if it was not an independent run. `report signals` gains an advisory line, `consider compaction: peak context 78 percent`, driven by the same context-fill signal as the context hygiene grade.

## 10. Build split and dependencies

One ticket, after T-0460 (the report record and views) and T-0461 (the grammar and closed verb lists in `core.md`). It extends `scripts/report.py` with the `compaction` view and a `compaction_lint` selftest, adds the `report` skill argument and its row in `views.md`, and records the replay. It is not blocked on T-0462.
