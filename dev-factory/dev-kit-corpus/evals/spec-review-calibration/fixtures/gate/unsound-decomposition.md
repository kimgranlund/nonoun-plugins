---
name: unsound-decomposition
description: >
  A palette exporter, decomposed — but one parent criterion is covered by no child (an orphan).
---
# unsound decomposition

**Intent.** Export a palette to JSON and CSS. **Non-goals.** Sketch export.

```json
{ "title": "Palette exporter", "cell": "spec.system.unsound-decomposition",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [ { "id": "ex-json", "check": "exports a valid DTCG JSON" }, { "id": "ex-css", "check": "exports :root custom properties" } ],
  "non_goals": [ "Sketch export" ],
  "decomposition": {
    "parent": { "criteria": [ "ex-json", "ex-css" ] },
    "cells": [ { "id": "capability.system.json-export" } ],
    "tickets": [ { "target_cell": "capability.system.json-export", "acceptance": { "rubric_cell": "rubric.system.json-export" }, "covers": [ "ex-json" ] } ]
  } }
```
