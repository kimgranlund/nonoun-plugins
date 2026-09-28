---
id: T-0144
title: "The node, perl, and ruby value-option lists are best-effort the..."
type: idea            # feature | bug | chore | spike | idea
status: dropped       # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0120
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0120 (block-publish-sh-an-option/filer-L1.md):

The node, perl, and ruby value-option lists are best-effort (the builder did not cross-check against `node --help` or the perl/ruby docs) and python/node option sets can change across versions; an unlisted value-taking option before the inline-code flag still falls back to the masked scan and could let a publish call through.

## Constraints
What must not change. "None" if none.

## Decision
Dropped 2026-09-27: speculative hardening with no observed failure; reopen if the form shows up in a real run.
