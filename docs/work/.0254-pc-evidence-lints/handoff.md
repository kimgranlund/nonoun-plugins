---
id: T-0254
title: "Handoff and evidence lints with citation resolver"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add warning-level lints: no template placeholder text in a closed ticket, and a citation resolver that opens every path:line in a document.

## Intent
- Do: Extend tickets.py check for placeholder text in closed tickets, and add a short script that resolves every backticked path:line in a named doc and that each cited evidence path is tracked in git. Start as warnings.
- Done when: positive and negative controls exist for both lints and the gap analysis doc itself resolves clean.

## Context
Gap analysis R6. Both failures happened: placeholder text in .sdlc/verify-0224/verifier-L3.md:15 and an unbacked record in .sdlc/verify-0229/verifier-L3.md:11. The architect review found three wrong citations a resolver would catch (docs/reports/progressive-context-gap-analysis-review.md). Lane: solo. Philosophy: Done is better than perfect.

## Constraints
No push, tag, version bump, or publish. No em dashes. Preserve other agents' worktrees.

## Acceptance criteria
1. The placeholder lint has positive and negative controls and they pass: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 (its `(ph)` controls cover a closed unfilled ticket warning, an open ticket staying quiet, a filled ticket keeping the template's default Goal and Constraints lines staying quiet, a dropped ticket, the five-line cap with a count line, a `_templates` override, and the exempt list staying in a shipped template).
2. A real unfilled closed ticket is flagged and exit stays 0: `t=$(mktemp -d); tk() { python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" "$@"; }; tk new bug x "X" >/dev/null; tk check | grep -c "x/handoff.md:.*closed ticket still holds bug template placeholder text"; tk close x --reason r >/dev/null; tk check | grep -c "x/handoff.md:.*closed ticket still holds bug template placeholder text"` prints 0 (open ticket) then 1 (closed ticket).
3. The repository's own tickets still pass with warnings only, at most five placeholder lines plus one count line: `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0, its first line starts with `ok:`, and `... | grep -c "placeholder text"` prints 6 or less.
4. The citation resolver has positive and negative controls and they pass: `python3 plugins/sdlc-lite/scripts/cite_check.py selftest` exits 0 (a clean document with alias, bare, partial, other-repository, fenced and non-citation spans prints no warning; a document with one of each defect, past the end, missing, untracked, git-ignored, ambiguous, backwards range and line 0, prints one warning each).
5. The resolver rejects bad citations on a real tree: `d=$(mktemp -d) && printf '`plugins/sdlc-lite/scripts/tickets.py:99999` and `docs/no-such-file.md:1`\n' > $d/d.md && python3 plugins/sdlc-lite/scripts/cite_check.py $d/d.md --root "$PWD" --strict` exits 1 and prints two `warning` lines, one `is past the end` and one `no tracked file matches`.
6. The gap analysis document resolves clean: `python3 plugins/sdlc-lite/scripts/cite_check.py docs/generative-constructs/progressive-context-gap-analysis.md --strict` exits 0, prints no line starting `warning`, and its last line starts `ok:`.
7. Wiring and records: `grep -c 'cite_check.py" selftest' plugins/sdlc-lite/scripts/check.sh` prints 1; `grep -c 'scripts/cite_check.py' docs/maintenance/sdlc-internals.md` prints 1 or more; `grep -c 'Placeholder lint (T-0254)' docs/maintenance/sdlc-internals.md` prints 1; `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0; `python3 scripts/check-packaging.py` exits 0.
8. Hygiene and scope: `git diff --check` exits 0; `python3 -I -c "import subprocess;fs=subprocess.run(['git','diff','--name-only'],capture_output=True,text=True).stdout.split()+['plugins/sdlc-lite/scripts/cite_check.py'];print([f for f in fs if chr(0x2014) in open(f,encoding='utf-8').read()])"` prints `[]`; `git status --short` lists only `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/scripts/check.sh`, `plugins/sdlc-lite/scripts/tickets.py`, `plugins/sdlc-lite/skills/ticket/SKILL.md`, `plugins/sdlc-lite/scripts/cite_check.py`, and this ticket's folder.

## Notes
Read-only for the verifier: report pass or fail per criterion with evidence. The resolver proves a cited file is tracked and the line exists; it does not prove the line says what the claim says, and that limit is documented, not a defect.

## Closed

2026-10-07: built by fanout lane batch3-lints (cite_check.py, evidence lints), merged in 0.21.1
