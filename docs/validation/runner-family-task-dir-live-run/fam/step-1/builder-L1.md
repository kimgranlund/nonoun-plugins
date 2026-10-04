<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- greet.sh: added `name=${1:-world}` and changed the output to `echo "hello $name"`.

## Checks
- `test "$(bash greet.sh Ada)" = "hello Ada"`: passed.
- `test "$(bash greet.sh)" = "hello world"`: passed.

## Notes
None
