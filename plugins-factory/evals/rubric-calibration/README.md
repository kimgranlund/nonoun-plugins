# Rubric calibration — the holistic standard against real candidates

The ROADMAP's standing condition: *"Until N≥3 the rubric is directional, not validated."* This eval applies `references/rubrics/plugins-holistic.md` (P1–P9) to **real plugin candidates** — pre-carve skills from the maintainer's global library, the carve targets the roadmap itself names — and records the scored applications plus what each application taught about the **rubric**. Records live beside this README, one per candidate; sensitive values found inside candidates (credentials, PII, client identities) are **redacted by policy** in these public records.

## Applications (N=3, 2026-06-10 — the validation threshold is met)

| Candidate | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| accounting-studio | 3 | 3 | 5 | 2 | 3 | 4 | 4 | 3 | 2 | **BLOCKED** |
| ops-repo | 4 | 3 | 4 | 3 | 4 | 4 | 3 | 4 | 4 | **CONDITIONAL** |
| skills-studio | 4 | 3 | 4 | 3 | 2 | 4 | 3 | 4 | 4 | **CONDITIONAL** |

Three different verdicts-with-reasons from three high-quality candidates — the scorecard discriminates rather than flattering or condemning uniformly.

## What the applications taught about the rubric (the calibration)

**Validated — promote from directional:**

- **P4 (install test) and P5 (mechanical manifest checks) discriminated hardest on every candidate** — because their tests are executable, not impressionistic: they surfaced dangling references, parent-tree reaches, a candidate failing *its own* validator, and schema self-exemptions. The mechanical-hard-test design is confirmed.
- **P9's bundled-data/trifecta audit** caught the single most consequential finding of the exercise (live credentials + personal data inside a would-be distributable — see the accounting-studio record) — a defect class prose review missed for months.
- **P2's "hopeful guarantee" anti-pattern (AP-P3) named real defects verbatim** on all three candidates (unwired mechanical gates; prose-guaranteed critic isolation; conversational flows that are really commands).
- **P8 discriminated in an unanticipated direction:** it caught **high-form/low-truth** changelogs — exemplary discipline whose claims fail verification against the tree. The anchors describe absent discipline, not false discipline; add anchor language for declared-state drift (the `check-manifest-sync` class).

**Demoted / annotate:**

- **P1, P3, P6 near-auto-pass on single-skill, well-authored candidates** — the one-sentence and split/merge tests are designed for multi-component bundles; on a pre-carve skill they measure one property twice, and progressive-disclosure doctrine makes P6 a 4–5 by construction. Keep them (they bind on bundles like mega-helper, where all three scored 1), but note they are weak discriminators pre-carve.
- **P7's "no `/command` entry" anchor is near-tautological pre-carve** — every bare skill hits it; it measures the carve's to-do list, not the content's quality. Add a pre-carve scoring note.

**Rubric improvement candidates (from scorer findings):**

1. A **pre-carve scoring note** in the rubric header: which anchors suspend, which artifacts substitute (skill.json for plugin.json).
2. An explicit **personal-state hard test** under P1 or P9: "is personal/live state (credentials, registries, caches, output artifacts) entangled with the distributable content?" — currently findable only via P5's layout framing, and it is really a fitness/trust question.
3. A **`bin/` blast-radius probe** under P9: side effects documented at the contract level (SKILL.md), not just in script docstrings.
4. The two council blind spots recorded by the mega-helper N-runs: a **liveness smoke gate** (an MCP that never answers `tools/list` sails past every static lens) and a **hollowness probe** (the rubric measures bloat; emptiness sails through).

## Protocol

One isolated scorer agent per candidate, cold: reads the rubric spine + the candidate tree, scores P1–P9 with cited evidence under the carve framing ("if packaged as a plugin, what does each dimension inherit?"), names the top 3 carve fixes, and reports which dimensions discriminated — the last section is the calibration payload. Candidate content is untrusted data; self-praise is verified, never inherited.
