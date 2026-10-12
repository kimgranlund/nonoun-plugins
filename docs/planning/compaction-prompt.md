---
status: proposed
owner: maintainer
---
# Compaction prompt: `/sdlc-lite:plan compaction <prose>`

Status: proposal. Raised in ultimate-tokens as `/plan compaction` (handoff of 2026-10-12, kept in `.sdlc/0465-compaction-prompt/source-handoff.md`). This version is the original spec reviewed and aligned with the plan skill family (`plan-goal`, `plan-loop`, T-0462), the controlled language (T-0461), the document standards (T-0447), the lane lifecycle and the resolve-and-ship posture (T-0464). The report skill (T-0460) is an optional data source, not the home.

## 1. Answer

One command returns one prompt that the person pastes into a manual `/compact <prompt>`: fixed shape, controlled language, pointers instead of copied content. It never runs the compaction. State facts come from commands the skill runs; only goal, rules and decisions come from the conversation. It authors a block and a lint checks it, the same pattern as `plan-goal` and `plan-loop`. The original optional handoff file write is cut to a Claude-only, off-by-default step, and the `AGENTS.md` write is dropped.

## 2. What changed from the original, and why

| # | Original | Now | Reason |
|---|---|---|---|
| 1 | A mode of `/plan` | Kept: the kind `compaction` of the existing `plan` skill, invoked `/sdlc-lite:plan compaction <prose>`, linted by a new `plan_check.py compaction` kind | The maintainer fixed the invocation. It is a block-returning kind like the `/goal` and `/loop` skills, so it authors one copy/paste `/compact` prompt. A `report` view was wrong: a report states status, this authors text for a summarizer. T-0462 folds the other plan skills into the same router later |
| 2 | The model sweeps state from the session | The skill runs a fixed command list for STATE, OPEN, NEXT and POINT (`git status`, `gh pr list`, `dispatch.py status`, `steps.py next`, the ticket and plan-doc paths); the model supplies GOAL, RULES and DECISIONS | Commands cannot drift "I assumed" into "user said". `next` carries `planned` or `intended`. When the `report` record exists (T-0460), the skill reads it instead of re-running the commands |
| 3 | Writes `AGENTS.md` for Codex | Dropped. The Codex prompt ends `NEXT run /sdlc-lite:report summary` | Root `AGENTS.md` is a tracked entry file with a managed block; transient state in it is a stale-context defect, dirties the tree and can be committed. The snapshot under `.sdlc/runtime/report/` is already the replaceable, ignored state |
| 4 | Handoff file on by default | Claude only, off by default (`--write-handoff`) until the reload is verified (section 8) | Four assumptions were untested; two are removed by item 3 |
| 5 | Verbs KEEP, POINT, DROP, NEXT; present tense | Kept for the instruction lines; fact lines use the status grammar of `core.md` | Two jobs, two forms (section 4) |
| 6 | No evidence marks | Each DECISION and RULE carries a pointer to its turn or `[U]` | The retro rule: a claim with no pointer is `[U]` |
| 7 | Six sections of guards | MVP is sections 1 to 5 of the original; the handoff write is a later step | Resolve and ship; add the guards when the reload is shown to work |

## 3. Command and arguments

`/sdlc-lite:plan compaction [--write-handoff] [--clear] [<prose>]`. The first word `compaction` selects the kind; flags, when present, come right after it; everything after them is `<prose>`, passed through verbatim as the focus (the next task, or any extra thing to carry). The prose is data: an instruction inside it is carried as text and never followed. Hint per the skill hint standard (T-0463): `[L1|L2|L3] <handoff.md | goal> | compaction [--write-handoff|--clear] [<prose>]`. `compaction` is a reserved first word of `/plan`; a goal that starts with it is written `goal compaction ...` or quoted. `<focus>` is one phrase naming the next task. `--clear` deletes the handoff section and nothing else. Output: one fenced prompt, a size note (`lines: N of 60`), and `Run: /compact <paste>`.

## 4. Derivation

| Section | Source | By |
|---|---|---|
| GOAL | the current ask, verbatim if under 20 words, else one sentence | model, with a transcript pointer |
| RULES | standing user instructions of this session that are not in `CLAUDE.md` or `AGENTS.md` | model, each `[U]` unless quoted |
| DECISIONS | who (user or agent), date, reason in 5 words or fewer | model, each with a pointer to the turn |
| STATE | branch, dirty files, open PRs, running agents and lanes, failing checks, the open ticket and its status | commands: `git status`, `gh pr list`, `dispatch.py status`, `tickets.py`, or the report record when present |
| OPEN | unanswered questions, held items, user-only actions | commands and the last open question in the transcript; the report `needs` list when present |
| NEXT | the single next action, `planned` or `intended` | `steps.py next` and the ticket `depends:` order; the report `next` when present |
| POINT | `locator -> what it answers`: the ticket handoff, the plan doc, `plan-state.json`, the report snapshot when present | commands |

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
- `plan_check.py compaction` lints the block: line length, the verb list, section order, the 60 and 40 caps, em dashes, duplicated entry-file lines, and a DECISION without who, date and pointer. `check.py` item 31 pins the phrase set of a block-returning plan skill; the new skill meets it.

## 7. Handoff file (optional, Claude only, off by default)

- Target `CLAUDE.local.md` at the repo root, created if missing, only with `--write-handoff`, and only after the person picks `/compact`.
- Guard: `git check-ignore CLAUDE.local.md` must pass. It does not pass in this repository today, so the build adds the `.gitignore` entry (or the guard stops and says so).
- Section key is the exact H2 `## Compaction handoff`, one per file. Replace the span from that H2 to the next H2 or end of file, then append the new one. Touch nothing else.
- Body at most 8 lines: `Written <YYYY-MM-DD HH:MM> by /sdlc-lite:plan compaction. Delete this section when the next task starts.`, then GOAL, STATE, OPEN (max 3), NEXT, POINT (max 3).
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

No data yet shows that a controlled compaction prompt helps. The build records a replay: fixture transcripts (a plan-doc run, a lane wave, a design thread) compacted with the prompt and with a free `/compact`, then the next 5 turns scored for re-asked questions, a violated standing rule, a lost decision and tokens carried. The report names the result and marks it unverified if it was not an independent run. When the report skill exists, `report signals` may add an advisory line, `consider compaction: peak context 78 percent`, driven by the context-fill signal; that line belongs to T-0460, not to this skill.

## 10. Build split and dependencies

One ticket. It adds the kind router to `plugins/sdlc-lite/skills/plan/SKILL.md` (the first word `compaction` selects `references/compaction.md`; any other input follows today's planner path unchanged), the reference with the grammar and a worked example, the `compaction` kind in `plan_check.py` with a selftest, its `check.py` phrase set, and the replay record. It follows T-0461 (the grammar and closed verb lists in `core.md`). It does not need T-0460 (the report record is an optional input) and is not blocked on T-0462: the router it adds is the one the plan merge extends with `steps`, `doc`, `goal`, `campaign` and `fanout`.
