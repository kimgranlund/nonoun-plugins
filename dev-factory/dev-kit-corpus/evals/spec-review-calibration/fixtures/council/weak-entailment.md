---
name: weak-entailment
description: >
  A palette exported to DTCG JSON re-imports to the identical palette — a lossless round-trip between tools.
---
# Palette round-trip — export then import is lossless

**Intent.** Exporting a palette to DTCG JSON and re-importing it yields a palette **identical** to the
original; a designer moves a palette between tools without loss.

**Non-goals.** CSS round-trip; partial/merge import.

```json
{ "title": "Palette round-trip", "cell": "spec.system.weak-entailment",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [
    { "id": "rt-01", "check": "export(p) is valid DTCG JSON" },
    { "id": "rt-02", "check": "import accepts valid DTCG JSON without error" },
    { "id": "rt-03", "check": "import(export(p)) deep-equals p" } ],
  "non_goals": [ "CSS round-trip", "partial/merge import" ],
  "decomposition": {
    "parent": { "criteria": [ "rt-01", "rt-02", "rt-03" ] },
    "cells": [ { "id": "capability.system.json-export" }, { "id": "capability.system.json-import" } ],
    "tickets": [
      { "target_cell": "capability.system.json-export", "acceptance": { "rubric_cell": "rubric.system.json-export" }, "covers": [ "rt-01" ] },
      { "target_cell": "capability.system.json-import", "acceptance": { "rubric_cell": "rubric.system.json-import" }, "covers": [ "rt-02", "rt-03" ] } ]
  } }
```
