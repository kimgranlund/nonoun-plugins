---
id: T-0321
title: "Record the T-0307 read-through and state the mark and row rules in interview.md (verifier A4)"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The T-0307 read-through of the fleet-retro interview template has a written record, and `interview.md` states the mark and row rules that read-through showed were missing.

## Intent
- Do: Record the dry read-through of the two root-cause reports present on this machine against the `interview.md` answer format, in this handoff (the T-0307 folder is closed history and is not edited). State in `plugins/sdlc-lite/skills/fleet-retro/interview.md` the rules that let every finding place in one row: one mark per row, weaker mark wins, other marks read as `[U]`; one finding per row; every cell filled (`none`); a gain is a row with Prevention `keep`. Repair the one SKILL.md clause that quotes marks.
- Non-goals: any change to the collector, detect rules, rubric, or the five questions; the gen-ui-kit report (absent here); any model or effort change.
- Done when: the acceptance criteria below pass and one independent verifier passes them.

## Context
The ticket body was an empty template when the lane started; the scope and the done criterion were derived from the title and from the T-0319 verifier finding A4 (`.sdlc/verify-fleet-0307-0310/verifier-L3.md`, A4 and its "For the next attempt" line). T-0307's own criterion was: a dry read-through against the three existing reports shows each finding fits one row of the answer format, with any that do not listed in the ticket notes. T-0307 closed with no such list.

Inputs, outside this repo:
- `/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/root-cause-2026-10-06.md` (agent-ui)
- `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/root-cause-2026-10-06.md` (ui-kit-maison)
- `/Users/kimgranlund/Projects/adia/ui-kit/main/.sdlc/root-cause-2026-10-06.md` (gen-ui-kit): not on this machine (`ls` says no such file; `rubric.md:33` and `docs/reports/fleet-retro-2026-10-06.md:49` agree).

## Constraints
No em dashes. `interview.md` stays under 60 lines (T-0307's limit). No push, tag or publish. Never edit another repo. No change to a model or effort value. Do not edit `.sdlc/.0307-fleet-interview/`.

## Read-through record

Read as of the HEAD before this change, against the answer format (six cells, one mark cell, at most 7 rows). Line numbers are those of each report. A finding is a bullet that names a symptom, a cost, or a gain. Bullets not listed below place in a row as written (one finding, one mark, evidence, a stated or obvious fix).

agent-ui (a) and ui-kit-maison (m):

| Report line | What did not fit the old template | Rule that now covers it |
|---|---|---|
| a7 | `[V]` and `[U on the cause]` in one finding, one mark cell | one mark per row; a mixed row is `[U]`, the unchecked part named in Mechanism |
| a9 | `[V]` timings and `[U, not timed here]` for the heavy phases | same rule |
| a23 | `[V counts]` mark, and four mechanisms in one bullet | same rule; a bullet listing several symptoms is several rows |
| a30 | `[V]` data with a `[U]` suggestion | mixed row is `[U]`; the suggestion goes in Prevention |
| a31 | `[V data, U comparability]` | same rule |
| a17 | cause is the repo's auto-merge setting, no fix | every cell filled; Prevention `none` |
| a32, a34 | an observation and a "not used" note, no symptom | a note that names no symptom, cost, or gain is not a row |
| m3, m10, m11, m29 | `🟡` for unverified, nothing marked `[V]` | any other mark, or none, is written `[U]`; m11 is the same class as a10 (`[U]` ceiling) |
| m31 | two blocked builders, "decisions, not faults" | two rows, Cost `unmeasured`, Prevention `none` |
| m35, m38 | "Faster:" items with no Symptom or Prevention; solo costs in the next bullet | a gain is a row: Symptom what got faster, Cost the measured saving (m38's per-attempt costs), Prevention `keep`. m38's "total spend not summed" names no finding and is not a row |
| m37 | four proposed changes (a) to (d) in one bullet, no symptom or evidence per item | (a) goes in the Prevention of the m20 row, (b) in m15, (c) in m26. (d), the stale board row for T-0039, T-0043, T-0036, is a finding but its evidence is ticket ids, not a command or log path, so `SKILL.md` step 4 deletes the row unless the conductor adds a command: the template working as designed, not a misfit |

Row cap: each report holds more than 7 findings, so a conductor cuts to the 7 costliest. That is the template's cap, not a fit failure.

Part 1: a6 and m7 (machine, load) are the environment fingerprint, not findings.

Marked limitation: m-style reports mark nothing `[V]`, so under the new rule every unmarked row reads `[U]`, including rows that cite a command. That is conservative on purpose; the rubric gates treat `[U]` and `[V]` rows alike.

Claim: with the row rules stated, every finding in the two reports present places in one row. The gen-ui-kit report was not read; for that report the criterion stays unverified until its file exists on this machine, then rerun this table for it.

## Acceptance criteria

Paths are relative to the repo root; `F=plugins/sdlc-lite/skills/fleet-retro/interview.md`.

- [ ] The one-mark rule is stated, and the base lacks it: ``grep -c 'is written `\[U\]`' $F`` prints 1 and `git show HEAD:$F | grep -c 'is written `\[U\]`'` prints 0.
- [ ] The several-rows rule: `grep -c 'several rows' $F` prints 1 and the same grep on `git show HEAD:$F` prints 0.
- [ ] The no-row rule: `grep -c 'names no symptom' $F` prints 1 and the same grep on `git show HEAD:$F` prints 0.
- [ ] The empty-cell rule: ``grep -c 'write `none`' $F`` prints 1 and the same grep on `git show HEAD:$F` prints 0.
- [ ] The gain rule: ``grep -c 'Prevention `keep`' $F`` prints 1 and the same grep on `git show HEAD:$F` prints 0.
- [ ] `test "$(wc -l < $F)" -lt 60` exits 0, and `grep -n -P '\x{2014}|\x{2013}' $F plugins/sdlc-lite/skills/fleet-retro/SKILL.md .sdlc/0321-interview-template-readthrough/handoff.md` exits 1.
- [ ] SKILL.md step 3 carries the clause: `grep -c 'any other mark reads as' plugins/sdlc-lite/skills/fleet-retro/SKILL.md` prints 1, and 0 on `git show HEAD:` of the same file.
- [ ] `## Read-through record` in this file names each flagged line in its table's first column: ``for t in a7 a9 a23 a30 a31 m3 m11 m35 m37; do grep -q -E "^\| (.*, )?$t(,| \|)" .sdlc/0321-interview-template-readthrough/handoff.md || echo missing $t; done`` prints nothing. It states the gen-ui-kit absence: `grep -c 'gen-ui-kit' .sdlc/0321-interview-template-readthrough/handoff.md` is at least 2.
- [ ] The record's reading of the two present reports holds: for each row of the record's table, the cited report line exists and says what the row says (open both reports at the paths under Context).
- [ ] `python3 plugins/sdlc-lite/scripts/check.py` prints `ok:` and exits 0; `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0; `git diff --check` exits 0.
- [ ] Only these files changed: `git status --short` lists `interview.md`, `SKILL.md` of fleet-retro, this handoff, and the lane's own `skips.md`.

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
