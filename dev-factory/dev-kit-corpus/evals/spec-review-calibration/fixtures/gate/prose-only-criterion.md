---
name: prose-only-criterion
description: >
  A toast notification when the user switches color mode — should feel snappy and look polished.
---
# prose only criterion

**Intent.** Show a toast when the theme changes. **Non-goals.** Sound, haptics.

```json
{ "title": "Theme-change toast", "cell": "spec.system.prose-only-criterion",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [ { "id": "tc-01", "note": "it should feel snappy and look polished" } ],
  "non_goals": [ "sound", "haptics" ] }
```
