# Composition negative-case checklist

Use these five cases under the existing rubric IDs. Inspect one relevant narrow
and wide state, plus the wrap threshold or expanded/completed state named below.
Reuse existing captures when they bind the current artifact. Add a capture only
when a finding exposes missing coverage. These are visual observations, not new
automatic gates or universal pixel thresholds. Record state and evidence for
each applicable judgment; absent compositions may be marked not applicable.

## Collection overflow

Rubric: `responsive.adaptation`.

- **Fail:** the next row is only a clipped border arc or unreadable fragment, with
  no meaningful cue that more records are available. A hidden scrollbar and
  generic instructions elsewhere do not make that fragment self-explanatory.
- **Pass:** complete visible rows have a discoverable overflow/count affordance,
  or an intentional partial row reveals meaningful identifying content with a
  clear continuation cue. All records remain reachable.
- **Inspect:** initial and filtered collections at narrow/wide widths; enlarged
  text when row heights change. Check scrolling and keyboard access separately
  from screenshot appearance. Use actual row heights, not a compact-control
  nominal height, for multiline collection cards.

## Nested boundaries

Rubric: `density.proximity`.

- **Fail:** opening nested disclosures produces adjacent duplicate rules or empty
  framed strips for a single logical boundary. Correct horizontal text rails do
  not excuse this block-axis noise.
- **Pass:** each logical boundary has one visible owner; spacing and headings
  distinguish inner groups without repeating the same boundary paint.
- **Inspect:** open all relevant levels together and inspect full-size boundary
  crops. Preserve meaningful separate group boundaries and focus indicators;
  this is not a rule to delete every border.

## Helper wrapping

Rubric: `content.reading`.

- **Fail:** a short helper leaves an example such as “MC” or a final token alone
  because it inherits a narrow input width while the field group has useful
  unused width. A prose minimum-width audit passing is insufficient evidence.
- **Pass:** the helper uses an intentional reading width independent of a short
  entry field, or concise copy fits coherently. Wrapping at genuinely constrained
  widths preserves meaning and remains readable.
- **Inspect:** wait for fonts, compare the wide layout with the wrap threshold
  and narrow layout, and inspect enlarged text where applicable. Do not force a
  single line, shrink type or truncate necessary help to obtain a pass.

## Action rails

Rubric: `layout.rails`.

- **Fail:** adjacent action/helper text has an unexplained first-baseline mismatch,
  or a quiet action label sits inward of the intended surrounding text rail.
  Equal outer-box centers do not establish text-baseline alignment.
- **Pass:** the action and helper share the intended first baseline or deliberately
  stack; the quiet action follows an explicitly chosen frame or label rail that
  is coherent with its group. Record the choice and visible relationship.
- **Inspect:** compare text and frame edges at actual size in narrow/wide and
  wrapped states. Preserve normal button slots and targets: ghost appearance
  does not remove geometry. A label-rail offset belongs to the composition and
  must leave focus/hover paint contained; check logical alignment in RTL when
  supported. Do not globally strip ghost-button padding.

## Completed action

Rubrics: `purpose.emphasis`, `interaction.transitions`.

- **Fail:** after success, a filled control merely relabeled “Ready” still reads
  as the available primary command, duplicates adjacent success copy and competes
  with the next useful task. Successful state mutation alone does not pass this
  visual check.
- **Pass:** completion is clear without relying on color, status is distinguishable
  from an available command, and the next meaningful action or selection is easy
  to identify. A repeatable command may remain prominent when its purpose and
  availability are clear; record that justification.
- **Inspect:** capture immediately after completion before navigating away; compare
  initial and completed hierarchy. Verify semantics and actual focus destination
  if the command changes or disappears. A screenshot cannot establish those
  behavioral checks.
