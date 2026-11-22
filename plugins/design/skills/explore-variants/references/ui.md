# Recipe: a UI layout or interaction

Read before step 3 of the procedure when the question is how something on screen is laid out or operated.

| | |
|---|---|
| Specimen | A live mock, rendered from the fixture by script and operable where the idea depends on operation (choose a day, open a column). A static picture of an interactive idea hides its cost. |
| Fixture | Real content, the same in every variant, including the cases that make the problem hard (the long title, the overlap, the very short item, the empty day). Never lorem ipsum. |
| Stress | A slider or toggle on what makes the problem hard (width, count, length, time), applied to every variant at once. A second control only when a later round needs it (a "now" scrubber for time-dependent states). |

## Choosing variants

The usual axes: what carries the text, what carries the quantity, whether the frame is kept or dropped,
orientation, all at once or one in focus, where detail lives. Besides the tests in step 3: no two variants share a
silhouette at thumbnail size.

## The fixture when a variant stands for a kind of product

The fixture is that product in use (the player playing, the article being read, the game being played), with no
navigation or headline about it. A landing page is a fixture only when the subject is a landing page.

## Rules for the mocks

- Use the product's own tokens in the mocks, and follow its standing rules there (for example no borders, neutral
  selected states), or the reader judges the wrong thing.
- State by shape as well as colour (hollow and filled, size, weight), so a variant is judged without colour.
- A specimen that stands for a system takes that system's own values (its label on a solid, its ramp steps, its
  lengths), in both schemes. Where a value is the page's own stand-in, the page says so.
- A page built from values derived at build time (a size system's rows, a palette) keeps each round's derived
  values with that round's file. Rebuilding an earlier round must not redraw it with today's values.
- When a round fixes something the user pointed at, say whether the fix was looked at in a render, and in which
  schemes and states it was not.
