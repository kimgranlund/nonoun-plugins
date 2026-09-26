---
id: T-0097
title: "block-publish.sh no longer blocks a publish run from an interpreter..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0077
---

## Goal
Inside a role run, `hooks/block-publish.sh` blocks a publish command run through an interpreter's inline-code flag (for example `python3 -c 'import os; os.system("git push")'`, `node -e '...gh pr create...'`, `perl -e`, `ruby -e`), as it did before T-0077, while a plain interpreter run of a script (`python3 scripts/check.py`) and quoted mentions of a publish phrase in non-interpreter commands still pass.

Done when: the hook raw-scans a command in which an interpreter word (at least python, python3, node, perl, ruby, including a path-qualified form like /usr/bin/python3) appears as a command word with an inline-code flag (`-c` for python, `-e`/`-E` for perl/ruby/node, `-p`/`--eval`/`--print` for node); `scripts/hook-selftest.sh` has blocking fixtures for each interpreter and pass fixtures (script run, interpreter with no publish phrase, a quoted mention that is not interpreter code); the hook header comment, CLAUDE.md's block-publish.sh bullet, and `.claude/agents/sdlc-lite-author.md` (if it describes the evaluator list) name the new rule; `scripts/check.sh` is green.

Decision (conductor, unattended, from existing doctrine): extend the fail-closed raw-scan rule, which already covers shell and evaluator words, to interpreter inline code. Scope it to the inline-code flag so ordinary `python3 script.py` runs keep the masked scan and do not gain false positives.

## Context
Follow-up from T-0077 (block-publish-sh-matches-publish/filer-L1.md):

block-publish.sh no longer blocks a publish run from an interpreter one-liner such as `python3 -c 'os.system("git push")'` or `node -e`, which it blocked before T-0077 only as a side effect. Decide whether to add interpreter words to the raw-scan fallback.

## Constraints
- Existing hook-selftest fixtures keep their outcomes (all T-0077 masking behavior stays).
- The hook still exits 0 when `SDLC_ROLE` is unset.
- No em dashes in docs or comments.
