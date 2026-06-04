---
description: Migrate an adia-ui app — upgrade across @adia-ai versions, port to adia-ui, or change rendering mode.
argument-hint: "[upgrade|port|mode] [target]"
---

Migrate an adia-ui app. **$ARGUMENTS**

Hand off to **`adia-ui-migrate`** and run its 5-step discipline: read the migration guide → audit call sites (`git grep`) → apply mechanical sweeps (flag judgment items, don't auto-apply) → run the verify gates (`adia-lint` + render + the leftover-drift grep) → report what changed and what's left.

The skill owns the discipline + the breaking-change history; don't restate it here.
