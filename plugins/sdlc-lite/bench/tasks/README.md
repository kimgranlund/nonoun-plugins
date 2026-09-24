One file per benchmark task, `<name>.md`. Only add a task after red/green: `check` fails on `base` with the hidden tests copied in, and passes on `solution`.

```
repo: /abs/path/to/repo
base: <sha before the real change>
solution: <sha of the real change>
level: L1..L5            expected builder level (the planner is not told)
tests_from: <sha>        where the hidden tests come from (usually = solution)
test_paths:
  - path/to/test.ts      hidden tests, copied in only after /chain finishes
setup: <install command>
check: <one shell command; exit 0 = pass>

## Goal
## Context
## Constraints
```

The Goal must state every name, field, path, and message format the hidden tests pin, and nothing the tests check may be missing from it. Otherwise a correct build fails on naming (the figma-stale-skip-report baseline, 2026-09-24). Grep the hidden tests for what they import and assert on before writing the Goal. Constraints must let builders update existing tests that the change legitimately breaks (the real solution usually did); a blanket "do not edit test files" makes typecheck or tests unreachable (the button-geometry-model baseline blocked twice on it).

Everything from `## Goal` down becomes the task handoff. Nothing above it is shown to the agents.
