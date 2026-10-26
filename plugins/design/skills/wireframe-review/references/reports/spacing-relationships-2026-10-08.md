# Spacing relationship verification

Implemented the local inset relationship contract in product foundation, artifact styling, composition, the style contract and a linked spacing recipe. SKILL.md routes form/card builds to the recipe. Existing review-shell spacing remains independently scoped.

Observed cause: flow margins could be reset by fieldset margin rules; card padding used 2.5 insets while field and option gaps used unrelated values. Replaced flow margins with parent grid gap; nested groups reset their relationship. Cards use one inset. Semantic plain fieldsets avoid repeated borders/padding. Geometry resolver recalculates local roles on descendants: tests therefore use real data-size contexts, not a body-only override of the resolved g-inset.

Verification: six cases (360/1200px, product tier, medium scale, small/medium/large sizes), with 24 detected mutations for zero gap, excessive option gap, excessive inset and extra child margin. Thirteen existing product checks and the declared-behavior positive/negative gate pass; 26 selftests pass. Six style-contract browser cases and four negative controls pass. Skill frontmatter validation passes.

Evidence: /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/wireframe-spacing-rTwPD9/report.json and /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/wireframe-product-nRxLYU/report.json; /tmp/wireframe-spacing-style-check/report.json (see directory for actual report filename).

Limits: Chromium; WebKit executable unavailable. Authored recipes establish implementation behavior, not fresh-agent adherence or aesthetic optimality of every relationship. Global artifact checks still need evaluator bindings; no claim that the recipe checker detects all arbitrary markup defects. Frozen paired-run artifacts were not rebuilt.

The product checker now always creates a fresh output child directory, addressing the observed test-fixture overwrite. Continue updating the owning rule/recipe after verified learning; keep untested proposals and experiment results out of mandatory normative prose.

## Visual feedback correction

User review found the one-inset card boundary too compact. Superseded that default with two local insets, retaining one-inset content gaps and half-inset tight relationships. Relationship consistency does not imply equal padding and gap. This is a user-reviewed design correction; geometry checks verify its implementation, not aesthetic optimality.

## Second visual calibration

User review still found card padding and vertical rhythm too tight. Doubled content relationships and card padding: tight content 1u, field/group separation 2u, section separation and card inset 4u. Fixed control internals remain unchanged. These supersede the earlier ratios above. Validate geometry separately from visual preference; passing a ratio test alone did not establish adequate breathing room.

## Accepted hierarchy: 32 / 24 / 16 / 8

User selected padding / major groups / fields / related content at 4u / 3u / 2u / 1u. The recipe now separates scope fields, direction and execution footer. A new negative control rejects flattening the major-group gap to the field gap. Earlier ratios above are historical experiments, superseded by this contract.
