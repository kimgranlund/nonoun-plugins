# Compaction prompt replay: the prompt arm against a free /compact on three fixtures

Date: 2026-10-12. Ticket: T-0465, step 2.

## Method

Three fixture transcripts were written for this replay, one per session kind the spec names (`docs/planning/compaction-prompt.md` section 9): [plan-doc-run](2026-10-12-compaction-prompt-replay/plan-doc-run.md), [lane-wave](2026-10-12-compaction-prompt-replay/lane-wave.md) and [design-thread](2026-10-12-compaction-prompt-replay/design-thread.md). Each is a turn-numbered session of 17 or 18 turns with one goal, two standing rules, three decisions with who and date, open items, and five probe questions with the answer each expects.

Each fixture has two arms.

- Arm `prompt`: the prompt was authored as `plugins/sdlc-lite/skills/plan/references/compaction.md` says. The command list of its section 2 cannot run on a fixture, so the STATE, OPEN, NEXT and POINT facts come from the fixture text. The first return was piped to `python3 plugins/sdlc-lite/scripts/plan_check.py compaction` before any fix. Then the summary a summarizer would keep under that prompt was written.
- Arm `free`: the summary of a bare `/compact` was written.

The blocks are `<fixture>.prompt.txt` and the summaries are `<fixture>.summary-prompt.md` and `<fixture>.summary-free.md` in [the sibling folder](2026-10-12-compaction-prompt-replay/).

Scoring, per arm, against the fixture: "Re-asked" counts the probe questions (of 5) the summary cannot answer, "Rule violated" counts the standing rules (of 2) absent from it, "Decision lost" counts the decisions (of 3) absent from it, and "Words carried" is the `wc -w` of the summary file. Lines is the `lines:` count of the lint.

Limits of this method:

- This replay was run by the builder of step 2, who wrote the fixtures, the prompts, both summaries and the scores. It is unverified: not an independent run.
- No summarizer model ran and no `/compact` ran. All six summaries are the builder's writing. The free summary is the builder's estimate of what a bare compaction keeps, so the gap between the arms is an assumption of the method and not a measurement.
- No turn after a compaction was run. The scores read the summary against the probe questions; they do not count what an agent did in 5 real turns.
- A rule counts as absent when the summary does not state it as a rule. In `design-thread`, the free summary says a Redis queue was rejected and does not state the rule "no new runtime dependency"; the rule counts as absent and probe 2 counts as answered.

## Result

| Fixture | Arm | Lines | First-return lint | Re-asked | Rule violated | Decision lost | Words carried |
|---|---|---|---|---|---|---|---|
| plan-doc-run | prompt | 21 | `ok: compaction plan passes` | 0 | 0 | 0 | 111 |
| plan-doc-run | free | n/a | n/a | 3 | 2 | 1 | 73 |
| lane-wave | prompt | 21 | `ok: compaction plan passes` | 0 | 0 | 0 | 117 |
| lane-wave | free | n/a | n/a | 2 | 1 | 1 | 79 |
| design-thread | prompt | 21 | `ok: compaction plan passes` | 0 | 0 | 0 | 108 |
| design-thread | free | n/a | n/a | 1 | 2 | 0 | 71 |

Outcome metric of the ticket (re-asked questions and violated standing rules after a compaction, the prompt arm against a free `/compact`), summed over the three fixtures: the prompt arm has 0 re-asked of 15 and 0 rules violated of 6; the free arm has 6 re-asked of 15 and 5 rules violated of 6. The prompt arm lost 0 decisions of 9 and the free arm 2. The prompt arm carries 336 words and the free arm 223. The before value stays unmeasured until a live run: these counts come from builder-written summaries, so they are a first baseline for the scoring method and not evidence that the prompt helps.

Notes on the rows:

- All three first returns passed the lint with no `FAIL` and no `warn` line, so no fix round ran. The lint printed `pin: 10 of 40`, `pin: 11 of 40` and `pin: 11 of 40`.
- Free arm, what is absent. `plan-doc-run`: both rules (no push without asking, commits under 200 changed lines) and the decision to drop the streaming writer. `lane-wave`: the rule that no ticket closes on a verifier fail, and the decision to pause T-0102 when the replan fails. `design-thread`: both rules as rules; the unit of durations is the one probe it cannot answer.
- The prompt arm carries more words than the free arm on every fixture (336 against 223 in total).

## Run on this repository

The skill was followed once in this lane (`.worktrees/fanout54/f`, branch `fanout/wave54-f`) in an unattended builder run with no `--write-handoff`, under the unattended rule of the reference (return the block, write no file, ask no question). The variable `SDLC_HEADLESS=1` was not exported in the shell; the kind asks no question and writes no file without the write flag, so no command of the run reads it. Invocation: `/sdlc-lite:plan compaction finish step 2 of T-0465 and verify it`.

The command list, run for real:

- `compaction_handoff.py status --file CLAUDE.local.md` printed `none`.
- `git status --short` listed 7 modified tracked files; `git branch --show-current` printed `fanout/wave54-f`.
- `gh pr list` exited 0 and printed nothing.
- `dispatch.py status .sdlc/0465-compaction-prompt/step-2` printed `builder-L2 running builder-L2 parent_pid=79245`.
- `steps.py next .sdlc/0465-compaction-prompt/step-2` printed `build L2` and `reason: no builder result; handoff level L2`.
- `report.py render` printed `recent: verified step 1 T-0465 | pass | 2026-10-13 01:36Z (+4 more)`; the step 1 fact comes from that line.
- The ticket `handoff.md` front matter reads `status: proposed`.

The session was a headless builder run with no user turn, so RULES is `none` and GOAL and both decisions carry `[U]`.

The returned fence:

```
Continue T-0465 step 2; keep the sections below.
GOAL
Record the replay and the live check of T-0465 in a dated report, gates green | [U]
RULES
none
DECISIONS
agent 2026-10-12 replay evidence is a dated report | repository home for evidence | [U]
agent 2026-10-12 handoff write stays off by default | reload unverified | [U]
STATE
Branch `fanout/wave54-f`, 7 modified tracked files, 0 open pull requests
`builder-L2` is running in `.sdlc/0465-compaction-prompt/step-2`
Ticket T-0465 has status `proposed`; step 1 is verified, pass
POINT `.sdlc/0465-compaction-prompt/handoff.md` -> goal, constraints, done-when
POINT `.sdlc/0465-compaction-prompt/step-2/handoff.md` -> the step and its criteria
OPEN
Live check of the `CLAUDE.local.md` reload after `/compact` is not run
NEXT
planned: build step 2 at level L2
DROP
DROP tool output, gate logs, the fixture drafts
NEXT finish step 2 of T-0465 and verify it
```

Returned with it:

```
lines: 21 of 60
Run: /compact <paste the block above>
```

`plan_check.py compaction` on first return, exit 0, last line:

```
ok: compaction plan passes
```

The block is `repo-run.prompt.txt` in the sibling folder. No file was written by the skill run.

## Live skill run

The run above was a builder following the reference by hand. This run is the skill itself, invoked once in a headless Claude Code session (version 2.1.296) that loaded this lane's plugin. It was run by the builder of step 3 from the tree root of `.worktrees/fanout54/f`, with no `--write-handoff`.

Command:

```
SDLC_HEADLESS=1 claude -p --plugin-dir plugins/sdlc-lite --model sonnet --dangerously-skip-permissions '/sdlc-lite:plan compaction "finish the loose ends of T-0465"'
```

Model: `sonnet`. The child exited 0 with empty stderr. The parent shell had `SDLC_ROLE=conductor` and the child inherited it; no hook refused the child, so `SDLC_ROLE` was not unset. `git status --porcelain` was the same before and after the child ran, apart from the saved stdout: the skill wrote no file.

The full stdout is [live-skill-run.out.txt](2026-10-12-compaction-prompt-replay/live-skill-run.out.txt). The fence body, byte for byte and with no fix, is [live-skill-run.prompt.txt](2026-10-12-compaction-prompt-replay/live-skill-run.prompt.txt).

- The `lines:` line the skill returned: `lines: 23 of 60 (lint: pin 10 of 40)`.
- Fences in the output: one (two fence marker lines).
- The `Run: /compact` line: present, as `Run: /compact <paste the block above>`.
- The output also held one sentence before the fence and three attention lines and one next-action line after the `Run:` line.

`python3 plugins/sdlc-lite/scripts/plan_check.py compaction --file docs/reports/2026-10-12-compaction-prompt-replay/live-skill-run.prompt.txt` on the saved prompt, exit 0, with no `FAIL` and no `warn` line. Last line:

```
ok: compaction plan passes
```

## Live check

unverified [U]: whether Claude Code loads `CLAUDE.local.md` again after `/compact` was not checked. A headless builder cannot run `/compact`, and no live run is on record. `--write-handoff` stays off by default.

## Follow-up

- An independent live replay in real sessions: run `/compact` with the prompt and bare on recorded sessions of the three kinds, by a session that did not build the skill, and score the next 5 turns, so the before value and the arm difference are measured and not builder-written.
- The one live check of the `CLAUDE.local.md` reload after `/compact`, in an interactive Claude Code session.
