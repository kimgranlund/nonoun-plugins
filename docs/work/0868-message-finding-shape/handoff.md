---
id: T-0868
title: "Two sessions can exchange findings through the mailbox in a light, parseable shape, and either side can list w"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Two sessions can exchange findings through the mailbox in a light, parseable shape, and either side can list which findings are open, fixed or won't fix.

## Intent
- Do: define an optional finding body shape and reply shape, and add a read-only `messages.py findings` listing built from them.
- Non-goals: a new message kind (older readers refuse unknown kinds); changing delivery, claim or ack rules; a changelog generator.
- Done when: the criteria below hold.

## Context
- #96: about 30 findings arrived as prose; "tracking which were fixed, which were worked around, and which commit to pin took manual bookkeeping." Ask: `finding: id, file:line, repro, worked-around: yes/no, blocking: yes/no` and a reply shape `fixed-in: <sha> | wontfix: reason`.
- `plugins/sdlc/scripts/messages.py`: `KINDS = ('question', 'handoff', 'ack')` (line 296) and validation at line 567 refuse an unknown kind, so a `finding` kind would break an older reader on the same mailbox. Put the shape in the body; the topic starts `finding <id>`.
- Body shape (lines of `key: value`, any order, extra prose allowed after a blank line): `finding: <id>`, `where: <file:line>`, `repro: <one line>`, `worked-around: yes|no`, `blocking: yes|no`. Reply shape: first line `fixed-in: <sha>` or `wontfix: <reason>` or `worked-around: <how>`.
- `messages.py findings [--receiver NAME]`: reads message files in new, read and done (bodies of messages whose topic starts `finding `, and their replies by `--re`), prints one row per finding: id, where, blocking, state (open, fixed-in <sha>, wontfix), sender. It is read-only: it claims nothing and moves nothing. Check the existing `list` (never prints a body) and `read` (claims) rules and keep `findings` within the registry and trust rules the docstring states; say in the docstring why reading bodies here is safe or limit it to messages the caller sent or received.
- The protocol text the skill and agents read lives in the docstring block around lines 330-390 (`{{launcher}}` placeholders); add the shapes there.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Add the `findings` command and its parser.
2. Add selftest cases: two findings, one answered `fixed-in: abc1234`, one open; a body without the shape is ignored; nothing moves between new, read and done.
3. Document the shapes and the command in the docstring protocol text and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/messages.py selftest` exits 0 and includes the new cases; with the reply parser stubbed to return open, the fixed case fails (state the observed red).
- `python3 plugins/sdlc/scripts/messages.py send --kind finding ...` still exits 1 (no new kind).
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- Message file format and front matter keys do not change.
