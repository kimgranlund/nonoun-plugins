# Recipe: work already done

Read before step 3 of the procedure when the question is whether to keep what was built or changed, one decision
at a time.

| | |
|---|---|
| Specimen | Before and after as two variants of one moment, each shown as it is or was, not as a summary of the change. |
| Fixture | The same case in both, chosen to show the difference the change makes. |
| Stress | The control the original decision turned on (the scheme, the size, the state), when there was one. |

## Setting up the page

- One moment per decision: both variants carry the same `data-moment`.
- `data-verdicts="keep:Keep,revert:Go back"` on the container, the positive one first, so the reader answers the
  question the page asks.
- `data-pick="one"` on the container or on a wrapper around a moment, so one click answers the moment.
- Each moment carries its own `data-aspects`, specific to that decision.
- Say on the page where a specimen is hand-built and not the product's own component.
- Act only on moments that were judged.
