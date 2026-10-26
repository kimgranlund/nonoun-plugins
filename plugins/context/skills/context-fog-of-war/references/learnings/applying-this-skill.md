# Applying this skill

Applies to: both.

How this skill's outputs map to each step of the [learnings](README.md), and the table a run ends with.

| Step | Fog-of-war output | What it settles |
|---|---|---|
| Instrument | bundle mapping, coverage states | which detectors are eligible; `unavailable-telemetry` names the missing field |
| Triage, lost context | `retrieved-not-submitted`, `tool-result-not-propagated`, `truncation` | rules out (a) transport loss |
| Triage, cause | one `decision` per failing cluster, `guidanceEdges` kinds | `explicit` edges support (b) or (c); `inferred` stays qualified |
| Guidance authoring | finding `category` guidance or coverage, `target`, `improvement` | the one place a conflict is settled |
| Validation and repair | finding `verification` | the check or replay that would fail today |
| Test loop | `engineer.py experiment` and `compare` | one bounded change, rerun on the same brief |

End a run with a why-and-fix table, one row per cluster: cluster, runs (any / only), cause class, cited evidence, fix layer, file, keyless test that proves it. Rows marked inferred keep that label.

## From diagnosis to fixes

Moved from SKILL.md on 2026-10-16.

For a runtime harness (a product-side runtime whose producer loop validates generative UI against a schema and runs repair rounds before rendering live), turn findings into fixes with the [learnings](README.md). They are runtime-harness field lessons, each tagged runtime harness or both; CLI-harness learnings go in a separate file with their own tag. Triage order: rule out lost context first (retrieved against framed, tool results received against submitted), then give each failing cluster one cause class: (a) exposure, (b) conflicting or ambiguous guidance, (c) model ignored clear guidance, (d) check, oracle or scenario defect. End with a why-and-fix table. The lessons were observed in one study; confirm each with its check before relying on it.
