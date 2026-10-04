## Task goal
`greet.sh` prints `hello <name>` for its first argument and `hello world` with none.

## Step 1: Name argument for greet.sh
level: L1
### Do
In `greet.sh`, use `name=${1:-world}` and print `hello $name`.
### Acceptance criteria
- `test "$(bash greet.sh Ada)" = "hello Ada"`
- `test "$(bash greet.sh)" = "hello world"`
