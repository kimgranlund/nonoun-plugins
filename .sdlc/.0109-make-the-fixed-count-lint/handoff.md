---
id: T-0109
title: "Make the fixed-count lint skip a bare = assignment such as n=26..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0100
---

## Goal
`steps.py lint`/`split` no longer reports "compares a count over a changing set with a fixed number" when the only literal of 2 or more in the span is the value of a bare shell assignment such as `n=26` (a word `name=value` in command position, not a `[`/`test` comparison). A real comparison (`-eq 26`, `= 26`, `== 26`, `!= 26`, `[ "$x" = 26 ]`) in the same kind of span is still flagged.

Done when: a `steps.py selftest` case proves a span with a count tool, a glob/ls/find, and `n=26` passes the lint, an existing refusal case still refuses, and `scripts/check.sh` is green.

## Context
Follow-up from T-0100 (planner-parallel-safe-criteria/filer-L1.md):

Make the fixed-count lint skip a bare `=` assignment such as `n=26`, which is currently flagged when the span also has a count tool and a glob, `ls` or `find`.

## Constraints
Only `fixed_set_count` / `COMPARE_RE` in `plugins/sdlc-lite/scripts/steps.py` and its selftest change, plus any doc line (CLAUDE.md Layout, steps.py docstring) that describes the rule. Every other lint (bash -n, `||`, sha pin) and every existing selftest case keeps its behavior.

## Plan review
- split refusal of planner-L1.md (2026-09-26): steps.py split flagged all four python3 -c criteria of step 1 with "acceptance criterion compares a count over a changing set with a fixed number" because each criterion quotes a sample span (count tool + glob/ls + a literal 26) as a string literal; the lint scans the whole criterion text, so criteria that probe the lint must not embed such a span verbatim (for example, drive the probe through the selftest, or build the sample string so the raw criterion text holds no count tool, set source, and >=2 literal together). Last line: plan defect: replan this step (/chain 3)
