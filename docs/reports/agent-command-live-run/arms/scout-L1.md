<!-- role=scout level=L1 model=claude-haiku-4-5 effort=low -->
## Map
- mathkit/stats.py:4: `mean(values)` function implementation
- mathkit/stats.py:7-8: empty sequence check that raises ValueError
- mathkit/__init__.py:1: mean exported from package
- tests/test_stats.py:2: mean imported for testing
- tests/test_stats.py:9-11: test_empty method testing ValueError on empty list

## Entry points
Execution enters via `mathkit/__init__.py:1` which imports and exports `mean` from `mathkit.stats`. Tests import via `from mathkit import mean` (test_stats.py:2).

## Not found
None

## Carry forward
- mean is defined at mathkit/stats.py:4-9 and raises ValueError("mean of empty sequence") when passed empty sequence
- Tested in tests/test_stats.py:9-11 with assertRaises(ValueError) in test_empty method
- mean is exported from mathkit/__init__.py:1 for public API access
