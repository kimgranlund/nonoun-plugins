# Rubric application — skills-studio (2026-06-10, cold)

**Candidate:** the maintainer's global `skills-studio` skill (the skill-lifecycle tool — plugins-factory's own structural ancestor; 88 files, 28-rubric manifest, 12 foundations, 9 critic personas, 10 scripts). **Verdict: CONDITIONAL** — P1 4 · P2 3 · P3 4 · **P4 3** · **P5 2** · P6 4 · **P7 3** · P8 4 · P9 4.

## The findings that set the verdict

- **P5 = 2 — the candidate fails its own gates, mechanically:** `quick_validate.py . --strict` exits 1 on the candidate itself (description over the 1024-char cap); SKILL.md and skill.json descriptions have diverged (two sources of truth); skill.json fails the meta-schema it ships *and declares canonical* (5 of 10 required fields missing) — each violating its own §SelfAudit non-exemption clause. The validator also imports PyYAML and uses 3.9+ syntax (breaks the marketplace's stdlib-only/3.8+ rule).
- **P5×P7 cross-finding:** the over-length description means 1024-truncation **cuts the tail of the NOT clause** — degrading exactly the anti-trigger hand-off its own adversarial corpus depends on.
- **P4 = 3:** documentation-level reaches outside the root (a feedback doc, a sibling-repo best-practices file, library-level gate scripts holding the recorded F1 baseline, provenance paths into `~/Downloads` and a sibling repo); self-acknowledged unpruned eval machinery (two parallel HTML viewers).
- **P2 = 3:** critic isolation is a **hopeful guarantee** ("earlier critics must not bias later ones" enforced by prose; parallel sub-agents optional); the three agents lack frontmatter (not loadable as agents as-is); seven modes route through one description with no command entry.
- **P9 note for distribution:** nine real living practitioners named in critic files — the marketplace's own convention obscures these at carve time. Script blast radius (writes into the user's project, spawns `claude -p`, strips the nesting guard) documented in docstrings but not at the contract level.
- **Strengths:** P8 4 — best-in-class changelog (16 versioned entries, merge lineage preserved); P6 4 — near-exemplary progressive disclosure; the foundations-coverage gate runs green in-tree.

## Top 3 carve fixes

1. Clear the self-gate failures first: description under the cap (byte-identical across files), skill.json valid against its own shipped schema, stdlib-only validator.
2. Promote modes → commands and critics → isolated read-only agents (frontmatter + duplicated trust-boundary block + obscured names) — turning the isolation prose into structure.
3. Install-clean the bundle: vendor or drop the out-of-tree gate/baseline pieces; fix stale counts and outside-root references; neutralize provenance paths; resolve the acknowledged dead weight.

## Calibration notes

P5 discriminated hardest — pure execution (the candidate's own validator exiting 1), zero judgment required. P4 separated load-bearing paths (clean) from documentation pointers (dirty) — a distinction worth stating in the anchors. P2 was the carve-shaping dimension. P1/P3 collapsed to the same question on a single-skill candidate (measure one property twice); P6 near-auto-passed. P9 wants an explicit `bin/` blast-radius-at-contract-level probe.
