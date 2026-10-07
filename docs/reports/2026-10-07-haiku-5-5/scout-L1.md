<!-- role=scout level=L1 model=haiku effort=low -->
## Map
- /private/tmp/h55proof/greet.py:1: `def greet(name):` defines the greeting function. Signature: `greet(name)`, one positional parameter, no type hints or defaults.
- /private/tmp/h55proof/greet.py:2: `return f"hello {name}"` returns the string `hello <name>`.

## Entry points
None. The only definition is `greet` in greet.py. Nothing in the tracked tree calls it.

## Not found
- No other definitions or references to "greet" in tracked files, excluding `.sdlc/`. Searched with `git grep -n -i "greet"`.

## Carry forward
- greet.py:1: `def greet(name):` is the only greeting function; signature is `greet(name)`.
- Source: `git grep -n -i "greet"` over the tracked tree, excluding `.sdlc/`.
