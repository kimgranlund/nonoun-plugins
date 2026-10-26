# Status and reconciliation

## Confirmed latest decisions
Base u=4; control font=2u+6px; transparent border default 0; composite requested inset default 0u; control and container curvature Soft; composite gap equals inset; label edge default 1.5u; chip label edge half control; text badge inline edge .5u; checkbox radius 1u; cards/collections have separate density; container curvature has no pill.

## Experimental / incomplete
- Multiline uses confirmed collection spacing; final row height remains content-driven.
- Current typography covers controls, chips, badges and captions; a complete page heading/body type scale is not yet designed.
- Multi-digit count badge overflow/truncation and content localization need an explicit rule.
- Currency uses a custom chip trigger with a chip-sized listbox. Full assistive-technology auditing and type-ahead are not yet completed.
- Shared border setting is supported. Independent parent/child border widths and deeper composite nesting need new tests and contracts.
- The specimen uses physical-space clipping and browser radius fitting; explicit width-aware nested radius resolution is not integrated there.
- Responsive breakpoints, touch target sizes, contrast and assistive-technology behavior have not been comprehensively audited.
- The specimen includes accumulated CSS overrides and a document-level keyboard-mode listener. It is frozen evidence, not the preferred implementation architecture.
- Label and slot border ownership is deliberately not identical: label wrappers have no decorative border; an editable input may own its declared border. Do not infer text shrinkage from icon artwork fitting.

## Deprecated
- Badge-sized composed-input prefixes/suffixes/selectors; use chips.
- Composite default .5u and curvature default 2u; now 0u and Soft 3u.
- Multiline residual composite subtraction; use collection density and container curvature.
- Old curvature names none/crisp/default/round/pill.
- Chip label compensation equal to full control margin; now half.
- Text badge inline edge 1u; now .5u.
- Checkbox inheriting pill curvature.
- Independent composite gap slider; gaps now equal requested inset.
- Nested wrapper/slot shrinking and gap compensation to force control-height alignment.
- Density-dependent label margin deductions.

## Change procedure
Identify the rule ID, describe intent and geometry consequence, decide whether the change is confirmed or experimental, update contract and resolver together, add an independent boundary/golden test, update visual matrix, then verify the relevant specimen. Increment package version and add a changelog entry. A visual fix must not silently redefine unrelated families.
