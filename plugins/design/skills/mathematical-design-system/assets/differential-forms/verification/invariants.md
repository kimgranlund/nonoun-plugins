# Verification contract

Automated numerical checks cover defaults, typography points, border conservation, stable label margins, density variations, composite extremes, zero-inset curvature, badge widths and primitive shapes. Composite single-row height may grow as borders/insets consume space; do not assert global border invariance beyond the available inset budget.

Visual checks are separate: inspect light/dark, all curvatures, compact with maximum border and inset, zero-inset groups, mixed slot arrangements, filled inputs, narrow layouts, long content, keyboard and pointer focus, chip selector popup behavior, and badge text fitting. Record the actual browser and viewport used. Never mark visual cases passed because numerical tests passed.

Acceptance: no clipped text, no accidental wrapper shrinkage, stable baseline/slot alignment, predictable focus, no unsupported interactive nesting, transparent borders in every state, and requested family-specific density. Tests should assert outcomes and boundaries rather than reproduce every implementation statement.
