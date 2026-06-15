---
name: wrong-layer
description: >
  A spec asset whose cell is a rubric.* cell, not a spec.* cell — the spec gate validates spec-layer only.
---
# wrong layer

**Intent.** (mislabeled layer). **Non-goals.** none-of-note.

```json
{ "title": "Mislabeled", "cell": "rubric.system.wrong-layer",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [ { "id": "w-01", "check": "something checkable" } ],
  "non_goals": [ "x" ] }
```
