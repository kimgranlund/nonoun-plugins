# Design principles and subtraction review

Good design makes the task understandable with the least unnecessary visual and verbal work. Mechanical correctness is necessary, but does not establish composition quality.

| Principle | Decision rule | Evidence required |
|---|---|---|
| Simple | Give each label, sentence, border and scale tier a distinct job. Remove duplication before adding explanation or containers. | Identify repeated meanings and show what can be removed without losing naming, context or feedback. |
| Clear | Make the current object, next action and consequence evident. Use one authoritative instruction for each task. | Trace the task in reading order and inspect accessible names separately. |
| Balanced | Organize related content into stable rails and groups with proportional visual weight. Balance does not require symmetry or equally sized columns. | Compare full-size narrow and wide views, headings, text rails and control baselines. |
| Spacious | Use proximity to express relationships and negative space to separate tasks. Use deliberate pauses; avoid padding every nested surface. | Compare within-group and between-group space and the distance to the next useful action. |
| Contrasting | Reserve stronger size, weight, fill and color for meaningful priority. Quiet supporting material without making it illegible. | Identify the primary focal point and competing emphasis; measure text contrast separately. |
| Consistent | Reuse a small role-based scale and familiar control behavior. Departures must explain a different task or state. | Compare repeated roles and document why any exception exists. |

## Required subtraction pass

Before recording composition passes, inspect a normal-size screenshot and ask of every heading, label, help sentence and boundary: what unique information or relationship would disappear if this were removed? Record at least one concrete removal candidate or a specific reason no redundant element exists. Never use added labels, cards or help as automatic evidence of improvement.

A single chooser does not need both “Choose a lot to review” and “Shipment lot”. Prefer one visible label, such as “Review lot”, associated with the select via label/for. If a section heading supplies essential structure and names exactly one control, associate that heading using aria-labelledby instead of duplicating it. Keep distinct labels when a group contains multiple fields or the heading does not identify the control. Placeholder-only naming is not an alternative. Do not conceal necessary error, unit or consequence information to reduce word count.

Long option names should distinguish records with compact identifiers and useful short names; put the complete selected record title in the detail region. Verify ambiguous/truncated options rather than treating clipping as simplification.

Compare before/after on both task effectiveness and visual cost. A shorter chooser may improve navigation while still failing content economy. A pass in geometry, semantics or keyboard behavior cannot override that failure. Checklist validation checks record structure, not design judgment. Preserve mistaken prior verdicts and publish a correction rather than rewriting historical evidence.

## Progressive explanation and compact choices
Keep decision-critical facts, units, errors and confirmations visible. Put definitions, methodology and repeatable reference material in a named disclosure near its task; preserve its open state across rerenders. Do not hide required instructions merely to reduce apparent density. Empty error/status slots should not consume visible flow space.

Native select labels cannot wrap. The [compact option recipe](../../assets/recipes/compact-options.js) accepts explicit distinct optionLabel values while preserving IDs as values. Show complete selected record titles in wrapping detail, including the comparison record. Do not automatically slice names or assume a tooltip repairs clipped text. Review every option at narrow widths and enlarged text. Where concise choices would be ambiguous, use wrapping record choices instead.
