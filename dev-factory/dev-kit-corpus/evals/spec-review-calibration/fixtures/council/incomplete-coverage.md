---
name: incomplete-coverage
description: >
  The user's chosen color mode persists across reloads and is applied before first paint (no flash).
---
# Theme persistence — survive a reload, no flash

**Intent.** When a user picks light or dark, the choice survives a full page reload and is applied **before
first paint**, so there is never a flash of the wrong theme — including the first visit and when storage
behaves unexpectedly.

**Non-goals.** Cross-device sync; per-route themes.

```json
{ "title": "Theme persistence", "cell": "spec.system.incomplete-coverage",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [ { "id": "tp-01", "check": "set dark, reload → documentElement[data-theme]==dark (read from localStorage)" } ],
  "non_goals": [ "cross-device sync", "per-route themes" ] }
```
