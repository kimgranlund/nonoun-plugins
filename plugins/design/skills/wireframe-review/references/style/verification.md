# Style contract verification

Run `node scripts/check-style-contract.mjs /absolute/path/to/playwright /absolute/output-directory` from any working directory. It writes a reviewable fixture and JSON evidence. Chromium is required; WebKit is attempted and explicitly reported unavailable if not installed. The fixture is authored, not model generated. Tests cover fixed icon geometry, parent gaps, stable menu height/half-inset offset, section/header edges, overflow and keyboard disclosure in two schemes and three widths. Four deliberate mutations must be rejected. They prove detector sensitivity only for those mutations.

## Model benchmark protocol

Use the same model/version, sampling settings and task brief across three conditions: foundation tokens/styles only; those plus contract.json and composition.md; those plus relevant recipes. Do not give recipes or screenshots of held-out tasks. Record model, settings, exact input, artifact, condition, repeat, elapsed time, token use if available, and all corrective prompts. Do not count corrections as first-pass success.

Use three independent repeats per condition and task initially. Familiar tasks: native select with icons; account menu; searchable sidebar. Held-out tasks: agent approval card with plan alternatives and bounded approval; evidence comparison with citations and uncertainty; branching task selector that preserves an alternate path. Stress each with wrapping text, empty/missing optional content, disabled/pending/error states, narrow containers and both schemes. Freeze the briefs before running. Do not tune the contract against held-out outputs; reserve a fresh set after tuning.

Run mechanical checks adapted to each artifact's semantics, not mandatory class names. Audit authored declarations for unapproved literal foundation values; allow documented content-specific geometry. A variable reference alone does not prove it resolves or has the right semantic role. Inspect keyboard focus, names, dismissal and state transitions separately from screenshots.

Blind the visual review: randomize output IDs, hide condition, and show reference-family components alongside the unseen outputs. Rate spacing/alignment, typography hierarchy, shape/density, state treatment and overall family resemblance on a 1-5 scale with anchored examples. Also rate task clarity and usefulness to avoid rewarding uniform but inappropriate layouts. Prefer two reviewers and record disagreement.

Predeclare acceptance: zero critical interaction failures, all applicable geometric invariants pass, no unexplained foundation overrides; contract condition improves median family resemblance by at least one point versus tokens-only without reducing task clarity. Report raw scores and variation; nine tasks/repeats are exploratory evidence, not a general statistical claim. Recipe-assisted success alone does not establish generalization. Record untested browsers and unavailable usage data explicitly.

The local harness is the first verification leg. The controlled model benchmark and blind review remain separate runs; do not describe hand-authored fixtures as independent generations.

## Conditional error coverage

For affected validation behavior, identify every affected control or semantic group from its contract. Verify each has the supported association to visible, nonempty error feedback after invalid activation; an alert or one linked control is insufficient. Check an unresolved edit retains established errors, including unrelated choices within the affected group. Test partial recovery before Save: only resolved predicates clear feedback/invalid flags. Check valid recovery clears invalid state and obsolete errors while retaining legitimate helper descriptions. Qualify new assertions with missing association on each target, unrelated-only references, hidden feedback and stale invalid flags. Verify mutations reach the exercised source. DOM association is separate from actual screen-reader observations.

## Native-select pilot

Start at discovery.json, then select/contract.json and bootstrap.md. `node scripts/observe-select.mjs` regenerates select/observation.json from source hashes; `--check` rejects stale observations, unsupported contract versions or missing dependencies. This is source identity/provenance, not inferred API support. The pilot deliberately does not claim a complete generated component inventory.

Run `node scripts/check-select-contract.mjs PLAYWRIGHT OUTPUT` to exercise `compileControls` and its shipped styles with JavaScript disabled. It checks compilation idempotence, native naming/value/disabled behavior, keyboard focus traversal, nested size with inherited semantic color, slot geometry, overflow and deliberate slot distortion. Outputs include a standalone specimen, screenshots and a JSON report. The source freshness gate runs first. Native popup keyboard choice, visual glyph delivery, full accessibility conformance, independent model generation and unavailable browser engines remain separate evidence requirements. Test code is outside the generated fixture; this local check is not an independent reviewer certification.

## Token membership regression

Run `node scripts/check-token-membership.mjs` after changing token inspection. Manifest build, artifact verification and standalone inspection share the same lexical scanner. Unknown references fail even when a fallback is present; declare intentional local or optional external properties in authored CSS. Only CSS and HTML style regions are inspected, excluding displayed snippets, comments and scripts. Passing establishes declaration membership, not scoped availability, cascade, semantic pairing or contrast. The regression uses isolated temporary files and exercises valid cases and deliberate faults through the real command-line entry points.
