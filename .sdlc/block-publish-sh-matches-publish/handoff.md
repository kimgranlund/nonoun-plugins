---
id: T-0077
title: "block-publish.sh matches publish commands inside heredoc and file..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0065
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0065 (fanout-py-s-default-lane/filer-L1.md):

block-publish.sh matches publish commands inside heredoc and file text, not only real commands: a builder's Bash edit whose text contained "git push" was blocked in T-0065, and the builder had to work around it with a temp script.

## Constraints
What must not change. "None" if none.
