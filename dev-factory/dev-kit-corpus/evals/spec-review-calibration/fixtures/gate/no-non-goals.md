---
name: no-non-goals
description: >
  A keyboard shortcut (Cmd+J) toggles the theme. Scope: the global toggle.
---
# no non goals

**Intent.** Cmd+J toggles the theme.

```json
{ "title": "Theme keyboard shortcut", "cell": "spec.system.no-non-goals",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [ { "id": "kb-01", "check": "Cmd+J flips data-theme between light and dark" } ] }
```
