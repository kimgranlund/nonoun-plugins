---
date: 2026-10-17
slug: targeted-cycle-field-test
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.4 conductor session)
authors:
  - role: solo
    agent: sdlc-lite:solo-L2 (0341-solo-L2)
    model: claude-opus-5-5
    did: applied references/experiment-series.md to a targeted cycle (planning, cap, report) and wrote this entry
project: a generative UI runtime's live evaluation series, targeted cycle after a full cycle
verification: pending
backup: none (no skill file changed)
---

# 2026-10-17: field test of the experiment-series reference on a targeted cycle

## Verified in the field
- Section 2 (alternate targeted and full) framed the cycle: last cycle's failures plus the runs each fix touches, with the next cycle planned as full.
- Section 4's verdict set covered every fix; "not exercised" was needed for three of seven fixes and kept them from being counted as fixed.

## Open
- **Mixed sample counts against a one-sample baseline.** The cycle ran 3 samples on unstable cases against a baseline of 1. Section 3's transitions assume equal sample counts; a cell rule "pass only when every sample passed" turns a 2-of-3 case into fail to fail. The report had to compare sample 1 with the baseline by hand and give the other samples as a rate. A rule for this (compare like samples; report the extra samples as a rate) belongs in section 3.
- **A cap checked before each case can still be passed.** Section 5 asks for an estimate and a hard cap, but a runner that checks spend only before starting a case can pass the cap on the last, dearest case. The cycle needed a per-case estimate the runner reads to skip a case that would pass the cap. Section 5 or live-evaluation.md should require it.
- **The estimate source undercounts a case that stopped early.** "The last identical cycle's measured spend" is low for a case that halted at its first step last time. The cycle used the larger of the last two cycles per case; the reference does not say so.
- **"Not exercised" because another fix removed the condition.** One fix's condition (a repair after a dropped surface) never occurred because an earlier fix in the same batch removed what triggered it. That is different from a condition that simply did not come up, and it means the later fix may never be exercised live; the verdict set has no word for it.
