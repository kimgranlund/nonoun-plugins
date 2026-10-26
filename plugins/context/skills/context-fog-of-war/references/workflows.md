# Workflow completion

Use optional `workflows` to assess a known requirement, not to guess a task from tool frequency. Each workflow has an id, title, four ordered stages (`guidance`, `action`, `evidence`, `outcome`), nextStep and uncertainty. Each stage has summary, state and evidence. States: complete (that stage's scoped criterion met), incomplete (explicit unmet required work), failed (explicit adverse result), unknown (insufficient records). Review completion and acceptance are separate claims. Guidance returned is not understood; command activity is not success; screenshots opened are not proof of cognition. A stopped trace does not prove abandonment or explain its cause.

Evidence entries contain label and exact excerpt plus either eventId or artifact and JSON pointer. Event excerpts must occur in the referenced event. External JSON citations are verified during attachment and embedded as snapshots; their paths are provenance, not executable instructions. Use unknown for unsupported claims. Never infer missing requirements from silence. Capture explicit requirements, final-artifact identity and review scope before computing completion. Record actionable next steps and uncertainty, including alternative explanations.

Attach a JSON array matching `workflows` in session.schema.json:

```
python3 scripts/workflow.py --data session.json --manifest workflows.json --out assessed.json
python3 scripts/library.py publish assessed.json
```

For a base-ui peer review containing outcome-map.json, inspection-adjudication.json and trace decision citations:

```
python3 scripts/workflow.py --data traces/cueforge.json --peer-review /absolute/evidence-directory --app cueforge --out assessed.json
```

Run once for each author; do not merge event IDs across sessions. The adapter uses the peer's adjudicated sample coverage and receipt outcomes, not new independent visual judgments. Review its citations and scope. UI: Workflow completion opens four stage cards; each opens embedded evidence and event/timeline inspection. `#workflow` opens this overlay on entry. Older reports without assessments show an explicit unknown-coverage empty state.

Shell review: use the maintained ghost appearance attribute. Source/finding selection uses wrapping buttons under a searchable disclosure; do not restore single-line native options for unbounded paths. Stage selection focuses its evidence heading. The workflow dialog isolates background controls, supports Escape and restores its launcher. Check light/dark and doubled text at 320/390/768/1440, including expanded JSON and empty search; distinguish source-report findings from the shell’s own review results.
