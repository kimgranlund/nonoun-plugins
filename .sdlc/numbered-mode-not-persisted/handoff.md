---
id: T-0024
title: "new --numbered does not turn on the numbered check"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A repo that uses numbered folders gets the prefix/id check without a separate step.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Review 2026-09-24: `new --numbered` names the folder but writes no `.sdlc/config`, so `check` stays in plain mode and a renamed 0009-bar holding T-0002 passes (exit 0). With `ticket_folders: numbered` in .sdlc/config the same tree fails (exit 1). gen-ui-system-svelte-lite uses numbered folders with no config. Options: `new --numbered` writes the config line when absent, or `check` warns when every folder has an NNNN- prefix but the config is missing.

## Constraints
The failing test lands before or with the fix, never after.
