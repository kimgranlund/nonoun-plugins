---
id: T-0543
title: "Lean records D: Close writes the Outcome (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0541, T-0542]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Close writes the Outcome: part D of SDLC Lite 0.23.0 lean work records (wave 3).

## Intent
- Do: build part D of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for D, Interfaces and Risks). Files: `tickets.py` (`cmd_close` Outcome composer, verdict gate, follow-ups from verifier `## Notes`, `--filer`, `--changed`, `--reason` writes an Outcome, T-0529 placeholder gate, citation scan skips `runtime/` plus T-0535 `citation_skip:`, `skip_problems` reads open folders only, claim staleness from `.running` at :1363 through `records_dir`, help text and selftests that name `## Closed` at :53,91,94,3528,4248,6052, router close procedure :1815-1825), `redck.py` (`deviations` subcommand; no `process-deviations.md`), `steps.py` (split refusal becomes a `## Plan review` line; no `refusals.jsonl`), `check.py` :186,:695, `agents/{conductor,verifier,builder,solo,filer}.md` plus regenerated agents (`claude_roles.py`, `codex_roles.py`), `skills/{chain,file,fix,ticket,open-questions}/SKILL.md` (/fix and chain loose ends write hand-written step handoffs under `order.py records-dir`)
- Non-goals: the other parts (A to F) of the same design.
- Done when: `tickets.py selftest` and `redck.py selftest` exit 0 with: a close over a passing verifier result appends `## Outcome` with `lane:`, `verdict: pass`, `Check:` and `Commits:` lines; a failing newest verifier makes close refuse (negative control); a handoff still holding the bug template's Repro prompt refuses and the filled-in one closes (T-0529); a marked inventory file is skipped by the citation scan and the unmarked one refuses (T-0535); no `process-deviations.md` or `refusals.jsonl` exists after the fixtures run. Generated-agent parity check passes

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.

## Plan review
plan review: replan: /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout70/d/.sdlc/runtime/tasks/0543-close-writes-outcome/plan-reviewer-L1.md
plan review: replan: step 3: goal coverage: a chain whose `Loose ends` step is not finished can no longer close. Chain 5.4 keeps a failed or unverified loose-ends verifier as it is and goes to section 6, and step 2 item 2 makes the default close refuse on any live step whose newest verifier is not `pass` and no `- skip: verifier; step: <n>` line covers it; step 3 item 1 rewrites sections 5 and 6 without saying how the close passes that gate (a skip line written in section 6, or `--reason`), so the builder would make that design decision. Today `skip_missing` asks only that the verifier ran, so the gap is new. Evidence: `plugins/sdlc-lite/skills/chain/SKILL.md:82` ("Any other outcome (verifier fail, no verdict, blocked builder, `inherited`) → one report line ... then section 6. It is never a rebuild"); `plugins/sdlc-lite/scripts/tickets.py:1578-1588` (`ran` checks a result exists, not its verdict); planner-L3.md:72-75 and :162.
plan review: replan: step 3: builder readiness: item 1 orders the :31 line to read "Sections 5 and 6 apply unchanged, with no new `close` gate", which is false once step 2 lands (the verdict gate is a new close gate), so the step writes a confidently false prose line into the skill. Evidence: planner-L3.md:160 against planner-L3.md:71-75; current text at `plugins/sdlc-lite/skills/chain/SKILL.md:31`.
plan review: replan: step 1: interfaces: item 4 tells the builder to write `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/redck.py" deviations <artifacts dir>` into verifier.md, filer.md and builder.md, which yields the substring `redck.py" deviations`; criteria 7 and 8 (`grep -qF "redck.py deviations"`) and the new check.py pin `'redck.py deviations'` from Do item 5 match only the unquoted form, so the builder passes only by deviating from the Do, and check.py flags verifier.md and filer.md otherwise. The repo convention carries the quote: `agents/builder.md:28` holds `redck.py" record` and check.py pins `'redck.py" record'`. Evidence: `plugins/sdlc-lite/scripts/check.py:693-695`; `plugins/sdlc-lite/agents/builder.md:28`; planner-L3.md:35,47-48.
plan review: replan: step 3: notes-fix: the `/fix` skill's `steps.py lint` target stays one space-free token ending `/step-1/handoff.md` (check.py `fix_lint_bad` reads `steps\.py lint (\S+?)` up to a backtick and flags any other shape, so a `$(... order.py records-dir ...)` target with a space inside turns check.sh red); name `order.py records-dir` in the prose beside it. Evidence: `plugins/sdlc-lite/scripts/check.py:600-606`; planner-L3.md:165,190.
plan review: replan: step 2: notes-fix: the `--help` criterion runs the top-level `tickets.py --help`, which prints each subparser's `help=` string and none of its arguments, so `--filer` and `--changed` go into the `add_parser('close', help=...)` text the way `--ack-warnings` is there today. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py --help 2>&1 | grep -c -- "--ack-warnings"` prints 1; `plugins/sdlc-lite/scripts/tickets.py:6027,6039-6043`.
plan review: replan: step 2: notes-fix: `outside_refs` leaves out `runtime/` under the `.sdlc` base (the `scan` argument when given, else `root`), because its `root` is the tickets dir `td` and under `ticket_root: tickets` the runtime dir is not `<td>/runtime/`. Evidence: `plugins/sdlc-lite/scripts/tickets.py:906,2410-2411` (close passes `td` as root and `root` as scan).
plan review: replan: step 2: acceptance criteria: the `(T-0543 no side files)` case cannot go red inside `tickets.py selftest`: nothing tickets.py runs writes `process-deviations.md` or `refusals.jsonl` (the writers are redck.py:302 and steps.py:1761, exercised only by their own selftests, which step 1 covers). Cosmetic; it mirrors the handoff's Done-when wording. Evidence: `grep -n "process-deviations\|refusals.jsonl" plugins/sdlc-lite/scripts/tickets.py` prints nothing.
plan review: replan: step 2: acceptance criteria: the label criterion greps the nine `(T-0543 ...)` strings in tickets.py source, which a label in a comment also satisfies; `tickets.py selftest` prints only `tickets selftest: PASS` with no per-case `ok:` lines, so the guard's exit 0 is the only bite. Cosmetic. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS`; `plugins/sdlc-lite/scripts/tickets.py:2981` `def expect(label, cond)`.
plan review: replan: plan: scope: step 2 edits `plugins/sdlc-lite/scripts/fanout.py`, which neither the handoff's Intent file list nor design row D names; the plan justifies it as a `## Closed` dependent and the `close_reason` docstring already defers to T-0543. Noted, not a replan on its own. Evidence: `plugins/sdlc-lite/scripts/fanout.py:940-949,5061-5062`.

## Outcome

2026-10-14 · lane: full L3 · verdict: pass · verifier: verifier-L2 (sonnet) · base: 678d28c3b050
- Changed: see commits
- Commits: 42e9d83 T-0543: Lean records D: Close writes the Outcome (0.23.0)
- Check: step-1#1 `redck.py deviations <missing dir>` prints nothing: pass
- Check: step-1#2 (guard) `redck.py selftest`: pass
- Check: step-1#3 redck selftest prints both T-0543 labels: pass
- Check: step-1#4 `record_refusals` gone, `record_plan_review` present: pass
- Check: step-1#5 (guard) `steps.py selftest`: pass
- Check: step-1#6 steps selftest prints both T-0543 labels: pass
- Check: step-1#7 no `process-deviations.md` in verifier.md, filer.md, builder.md: pass
- Check: step-1#8 `redck.py" deviations` in all three role files: pass
- Check: step-1#9 check.py and redck.py pins: pass
- Check: step-1#10 (guard) generate --check for claude_roles and codex_roles: pass
- Check: step-1#11 (guard) `check.py`: pass
- Check: step-1#12 (guard) scope: pass
- Check: step-2#1 (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass
- Check: step-2#2 label loop over the eight `(T-0543 ...)`, `(T-0529)`, `(T-0535)` tags: pass
- Check: step-2#3 `'## Closed' in inspect.getsource(tickets.cmd_close)` exits 0: pass
- Check: step-2#4 `tickets.py --help` names `--filer` and `--changed`: pass
- Check: step-2#5 `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass
- Check: step-2#6 `grep -qF "close <folder> --filer" .sdlc/AGENTS.md`: pass
- Check: step-2#7 `grep -qF "'--filer'" plugins/sdlc-lite/scripts/fanout.py`: pass
- Check: step-2#8 `! grep -qF "## Closed" plugins/sdlc-lite/scripts/fanout.py`: pass
- Check: step-2#9 (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass
- Check: step-2#10 (guard) scope: pass
- Check: step-3#1 no `Dispatch filer L1` and no `always runs the filer` in chain/SKILL.md: pass
- Check: step-3#2 `reason: loose end not finished` in chain, and the `'writes the Outcome': ('skills/chain/SKILL.md...: pass
- Check: step-3#3 `order.py records-dir` in chain and fix, and `steps.py lint <records-dir>/step-1/handoff.md` in fix: pass
- Check: step-3#4 no `skip: filer` in fix, and `--changed` in fix: pass
- Check: step-3#5 ticket/SKILL.md has `--filer`, `--changed`, `citation_skip:` and `## Outcome`, and file/SKILL.md ...: pass
- Check: step-3#6 no `## Closed` in ticket or handoff-format, no `The newest filer result` in open-questions, no fi...: pass
- Check: step-3#7 (guard) `claude_roles.py generate --check && codex_roles.py generate --check`: pass
- Check: step-3#8 (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass
- Check: step-3#9 (guard) `python3 scripts/check-packaging.py`: pass
- Check: step-3#10 (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`: pass
- Check: step-3#11 (guard) fresh-clone `check.sh` with TMPDIR unset: pass
- Check: step-3#12 (guard) scope and untracked check against base: pass
- Follow-up: decide: The throwaway-worktree hook blocked git worktree add here... -> notes.md
- Follow-up: decide: Observed runs under the tmp prefix removed afterwards: a... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/tickets.py:1001: a citation_skip: glob... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/tickets.py:2606-2612: on a ticket whose... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/agents/verifier.md Notes section: the line before... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/skills/chain/SKILL.md sections 5 and 6: removing... -> notes.md
