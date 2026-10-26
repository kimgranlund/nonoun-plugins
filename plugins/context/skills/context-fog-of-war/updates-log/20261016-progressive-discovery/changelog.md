---
date: 2026-10-16
slug: progressive-discovery
requested_by: user
harness: Codex desktop
authors:
  - role: solo
    agent: Codex
    model: not recorded
    did: reviewed progressive discovery, revised routing documentation, executed before/after tasks and regression checks
project: context-fog-of-war-map
verification: automated regression checks and same-session command tests; no independent verifier
backup: /Users/kimba/Projects/context-fog-of-war-map/artifacts/fog-progressive-review
---

## Added
- `references/discovery.md`, `references/investigation.md`, `references/exposure.md` retain detailed instructions outside the entrypoint.

## Changed
- `SKILL.md` routes by requested deliverable, distinguishes per-detector prerequisites and explicit publication boundaries, and retains evidence and uncertainty rules.
- `references/bundles.md` preserves provider errors by default; filtering is conditional and provenance-preserving.
- `references/engineering.md` names applicable detectors rather than an outdated fixed count.

## Fixed
- Resolved conflicting CLI versus mandatory-publication instructions.
- Removed blanket bundle-telemetry prerequisites for native detectors.
- Zero signals and unresolved causes no longer require invented findings or cause classifications.

## Open
- Three real command tasks passed before and after; no improvement in autonomous task success is established. A fresh-evaluator trial remains needed.
- 192 tests pass; frozen benchmark scores unchanged. No runtime algorithm changed.
