# Fresh-context spacing transfer

Two independent fresh-context agents used the same frozen skill and different briefs. One attempt each, no product repairs. This is exploratory transfer evidence, not a paired comparison or reliability estimate.

## Results

| Observation | Settings | Expedition card |
|---|---|---|
| Card inset | 32px | 32px |
| Major groups | 24px | 24px |
| Fields / content groups | 16px | 16px |
| Related content | 8px | 8px |
| Semantic grouping | Identity, workspace, notifications, footer | Identity, evidence, unresolved issue, editable handoff, footer |
| Independently exercised behavior | Edit, reset, save, timezone/digest persistence | Edit note, checklist readiness, prepare, edit invalidation |
| Narrow rerender state | Retained | Retained |
| Startup and document overflow | Passed observed routes | Passed A routes only |

Root browser measurements cover actual 390px and 1200px iframe widths in both schemes. The frozen 360px requirement is untested: the review shell enforces its 390px mobile viewport. Requested-width filenames are not evidence of actual viewport size; audit.json stores the measured width. Screenshot captures may clip the lower card through the review shell and are not full visual certification.

## Defects and limits

- Expedition shell retains B/C controls and three-proposal copy despite a single proposal. Selecting B errors (agent-recorded shell-limitation.json). The delivered review experience is not fully passing.
- Settings uses a copied builder without its cached token index. Its final gate fails freshness and lacks a task adapter; separate behavior evidence does not turn that gate green.
- Both agents initially attempted parseFloat on an unresolved CSS expression. Settings leaves the resulting assertions failed; the card agent resolved geometry through a rendered probe.
- Settings calls its 8px action-cluster gap a defect against an intended 16px value. The maintained contract explicitly assigns inline actions a tight gap; this is an expectation mismatch, not evidence that the 32/24/16/8 hierarchy failed.
- Settings omits the product typography class: its oversized heading is visible in the narrow screenshot. Spacing adherence alone does not establish complete family resemblance.
- Contrast was not independently quantified; Safari, 200% zoom, full control coverage and export/import remain untested. No broad accessibility or visual pass.

## Learning and follow-up

Keep the accepted spacing hierarchy. It transferred to both new compositions without supplying ratio hints in the brief. This does not prove causality or reliability from two attempts.

Update verification guidance to resolve CSS expressions through rendered lengths and distinguish action clusters from field groups. Next fix single-proposal shell support centrally so agents do not copy and patch the builder. Require product typography for product forms and inspect headings as well as gaps. Then address previously recorded workflow/menu/control defects and run repeated paired trials.

Evidence lives in evaluation/, agent result.md and retrieval.md, and frozen first-pass/ directories. No actual token telemetry or blind review. Corpus and brief hashes unchanged; artifact/input equality recorded in evaluation/integrity.json.

Run directory: /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/wireframe-spacing-transfer-wkooq0fc
