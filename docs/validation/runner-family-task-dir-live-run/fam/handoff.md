## Goal
`greet.sh` prints `hello <name>` for its first argument and `hello world` with none.

## Context
One step, built in `step-1/`. Verify the whole task against the criteria below.

## Acceptance criteria
- `test "$(bash greet.sh Ada)" = "hello Ada"`
- `test "$(bash greet.sh)" = "hello world"`
