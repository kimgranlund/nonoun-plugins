---
name: ui-content
description: Print values and labels in a UI so they read and line up - tabular figures, a true minus, the unit beside every value, the floor of a log scale (−∞), a value's width fixed by its longest value so a control never resizes, time and duration formats, and terse sentence-case labels. Use for "how should this number print", "the readout jumps as it changes", "the minus looks wrong", "label wording", "format a duration", or before building a readout, meter, counter, table column, axis or field that shows a value. NOT for type sizes or lengths (ui-geometry), colours (ui-colors), paint (ui-materials), what is announced or spoken (ui-interaction-dev), a brand's voice, or long-form copy.
---

# UI content

The characters a UI prints for its values and labels, and the width they take: which figures, which sign, where the
unit goes, how a floor and a time are written, and how a label is worded. Each rule holds for any system and any face.
This skill decides only the text; the box it sits in, its ink and what is spoken belong to the siblings named in
[Boundaries](#boundaries).

Contents: [Values](#values) · [Labels](#labels) · [Boundaries](#boundaries)

## Values

**Figures.** A value that changes in place (a readout, counter, timer, meter or slider value) or lines up with other
values (a table column, an axis, a list of amounts) is set in tabular figures, `font-variant-numeric: tabular-nums`,
so every digit has one width. Numbers in running text keep the face's default figures. A numeric column aligns to its
end, or on the decimal mark, and holds one count of decimals. Check a face before relying on it: "1111" and "0000"
measure the same width with the feature on. A face without tabular figures yields to one that has them, for values only.

**Signs.** A negative value prints U+2212 MINUS SIGN (−), never the hyphen-minus (-). A quantity whose sign carries
meaning (a gain, a change, an offset, a delta) prints + above zero; zero prints with no sign, and −0 prints as 0.
`Intl.NumberFormat` gives the hyphen-minus in some locales and U+2212 in others, so format first, then replace a
leading U+002D with U+2212. What a machine reads keeps ASCII: a `value` attribute, a `data-` value, a copied or exported
number. A field that takes a number accepts both − and - as its sign.

**Units.** Every value a reader sees has its unit in sight: beside the value (a readout, a field, a stat), or once at
the head of the set it belongs to (a column header, an axis title, a legend). A bare number the reader must place is
a fault. Join the number and the unit with a no-break space (U+00A0, or U+202F where the face spaces it well), so they
never part at a line end; no space before the degree, minute and second of an angle, as the SI has it. A field's unit
sits beside the field, outside its editable text. A count's unit is its noun ("3 tracks"), and a share of a whole is %.
The unit in an accessible name is ui-interaction-dev's.

**Floors.** A logarithmic scale whose bottom means none (a level in dB down to silence, a send turned fully off)
prints that floor as −∞ (U+2212 U+221E) on its marks and in its readout, not as the lowest number the control reaches.
The floor is a mark of its own, at the end of the travel. The taper is ui-interaction-dev's (`drag.value-taper`).

**Widths that hold.** A readout, counter, timer or control that prints a changing value keeps one width whatever the
value: as wide as the widest text it can show over its whole range. Measure both ends, a step in from each, the floor
(−∞), the sign, the unit and the text for no value. With tabular figures, 1ch is one digit, but a sign or a unit is
not a digit: either add their measured width, or stack an invisible copy of the widest text in the same grid cell as
the value (both in `grid-area: 1 / 1`, the copy `visibility: hidden` and `aria-hidden`), which holds for any glyph.
Align the value inside that width: to its end where values are compared, centred under a control. Recompute when the
range, step, unit or locale changes, never when the value does. Test it: set the value to each end and the floor and
read the box width; the widths are equal. This rule names the texts to measure; the box around them (its height,
insets and the lengths beside it) is ui-geometry's.

**Time.** A position or length in media, and a timer, prints as `m:ss` under an hour and `h:mm:ss` from an hour: the
leading unit unpadded, the rest two digits (0:05, 4:00, 1:02:03). Build it; `Intl.DurationFormat`'s digital style pads
the leading unit. A readout whose length reaches an hour reserves the `h:mm:ss` width from the start (Widths that
hold). Time remaining prints with a minus (−0:42). A duration in a label or in running text names its units
("2 h 5 min", "350 ms"), never a bare count of seconds. A clock time or a date follows the locale
(`Intl.DateTimeFormat`) and carries its ISO 8601 form in `<time datetime>`. A relative time ("3 min ago") keeps the
absolute time in reach: in its `datetime` and in a visible detail. Typing a date is ui-interaction-dev's.

## Labels

**Labels.** A label is the fewest words that name the thing or the action: a noun for a setting ("Volume"), a verb
first for an action ("Save", "Add track"). No article, no trailing colon or full stop, no "Click" or "Please".
Labels, buttons, menu items, headings and column headers are in sentence case: a capital for the first word and for
proper nouns only. Capitals or small caps for display are a style (`text-transform`, `font-variant-caps`) over
sentence-case text, so one style change undoes them. One function has one label wherever it appears (WCAG 3.2.4).

## Boundaries

- Type sizes, line heights and the box around a value (its height, insets and widths beyond the text) are ui-geometry's.
- Ink colour is ui-colors'; paint is ui-materials'.
- The accessible value (`aria-valuetext`), announcements and date entry are ui-interaction-dev's (its `announce` and
  `date` areas).
- This skill decides only the characters printed and the width they take.
