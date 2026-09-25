---
id: T-0074
title: "run.sh uses the node version from .nvmrc when present"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P3         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Headless builders run the Node version the repo pins in .nvmrc.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer setup-sdlc-lite-generative-ui: builders hit the repo's Node version guard because the headless shell's PATH has an older node than .nvmrc. Ask: when .nvmrc exists and nvm has that version, run.sh prepends its bin dir to PATH.

## Constraints
What must not change. "None" if none.
