---
id: T-0097
title: "block-publish.sh no longer blocks a publish run from an interpreter..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0077
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0077 (block-publish-sh-matches-publish/filer-L1.md):

block-publish.sh no longer blocks a publish run from an interpreter one-liner such as `python3 -c 'os.system("git push")'` or `node -e`, which it blocked before T-0077 only as a side effect. Decide whether to add interpreter words to the raw-scan fallback.

## Constraints
What must not change. "None" if none.
