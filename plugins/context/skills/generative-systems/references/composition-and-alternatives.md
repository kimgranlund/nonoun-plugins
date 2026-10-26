# Composition and alternatives

Use for structural design, spacing relationships or contrasting alternatives. Begin with the user's outcome and workflow: what must be selected, understood, changed and confirmed, and which information belongs beside each action?

## Compose relationships

Use the kit's owners for page gutter, container inset, group gaps, field spacing and inline contents. A consistent numeric scale can still produce a flat list. Related content should read as a group, with stronger separation between groups than inside a field. Define the relationship between card inset and content gaps; do not independently increase every gap. The wireframe choice of 32/24/16 is an example of a local relationship, not a portable default.

Nested controls need split ownership. A segmented control's outer inset and item padding should compose instead of duplicating a full inset. Derive contained shapes using the kit's rules, not a universal radius formula. Wrapping should grow height while preserving the owned gutters. An inner choice body should not introduce another card inset.

Keep semantic heading rank separate from visual typography role. Product panels can use conservative UI headings while editorial sections use content roles. Resolve foreground against its actual surface, including open states and selected states; raw token use alone does not prove contrast.

Nesting must preserve semantics. Options belonging to a selected workspace can sit in the same container as its primary choice, with independent controls as siblings rather than inside the primary radio label. On narrow screens keep selector, detail, evidence and consequential action in understandable reading/focus order. Verify grouping through actual use and distance, not only token compliance.

## Choose behavior owners

Prefer native semantics and CSS where they meet the required behavior in the supported environment. Use small JavaScript for state, coordination, focus orchestration or interactions the native baseline does not supply. Avoid assuming every accessible pattern has a CSS-only equivalent. Verify current platform support when a design depends on it; neither a remembered support fact nor one emulation proves the full browser matrix.

## Make alternatives meaningful

Offer the requested count. Give each alternative a hypothesis about task completion, such as guided sequence, direct editing or selection-led detail. Identify the structural decision axis and tradeoff before varying presentation. Preserve comparable content, defaults and evaluation fixtures so cosmetic differences do not masquerade as strategy.

Respect the kit's semantic and behavioral invariants across alternatives while allowing genuine structural contrast. Previewing does not select a design or authorize external operations. Review mechanics belong to [feedback and review](feedback-and-review.md); a well-functioning comparison shell does not compensate for broken variant behavior.
