---
date: 2026-10-20
slug: cli-routing-lessons
requested_by: user
harness: Codex desktop
authors:
  - role: solo
    agent: Codex
    model: not recorded
    did: Updated CLI routing guidance, entry links and change log
project: Cross-host repository context-routing study
verification: 49 tests, skill validation and 32 local links passed; independent read-only scenario review passed
backup: /var/folders/rt/2p4p49z17k7fntz7tlyqr2xh0000gn/T/context-fog-of-war-before-79z4vjt1
---

## Added

- `references/learnings/cli-routing.md`: lessons 32 to 38 with scoped observations and practical analyst checks for intent, delivery, reuse, portability, independent outcomes, representation boundaries and evidence freshness.

## Changed

- `SKILL.md` and `references/engineering.md`: route progressive-routing investigations to one CLI reference, without adding detector or report-schema claims.
- `references/learnings/README.md`: index CLI lessons separately, identify study characteristics rather than exclusive host capabilities, and load only relevant steps.

## Fixed

- Removed the implication that every investigation should eagerly read all runtime lessons in sequence.

## Open

- No script, adapter, schema or detector behavior changed. These checks require analyst evidence; no new automated coverage or live outcome improvement is claimed.
- Validation: skill-creator quick validator passed in an isolated Python environment with PyYAML; all 49 existing unit tests and 32 local link/anchor checks passed. Reviewed diffs against the pre-change copy.

- Independent review distinguished incomplete delivery, recovered clipping and unsupported answer claims without inferring causation or new detector coverage. Minor repetition of evidence boundaries remains intentional; no material contradiction found.
