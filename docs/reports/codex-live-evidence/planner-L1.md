<!-- role=planner level=L1 model=gpt-6.1-sol effort=medium -->
profile: 0.22.4+a31917d883df

## Goal
Make `greet(name)` return `"Hello, <name>!"` while preserving the existing tests.

## Step 1: Fix greeting and keep gates green
level: L1
### Do
Depends on: none. In `kit/greet.py`, retain the signature `greet(name)` and replace the constant return with an f-string producing `"Hello, <name>!"`. The format is specified by `.sdlc/greet/handoff.md` and asserted by `tests/test_greet.py`, test `T.test_greet`.

The contract-dependent search using git grep found only that test and the handoff. Keep the test unchanged. Change only `kit/greet.py`; add no dependencies or files outside `.sdlc/greet/`. Existing launcher artifacts are outside implementation scope.

Run the focused checks below, then the handoff’s final gate, `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.
### Acceptance criteria
- (red) `python3 -B -m unittest discover -s tests -p test_greet.py -v` exits 0 and reports at least one executed test.
- (red) `python3 -B -c 'from kit.greet import greet; assert all(greet(name) == "Hello, " + name + "!" for name in ("Ada", "Grace", ""))'` exits 0.
- The final discovery gate exits 0 with at least one executed test.
- Inspection of tracked changes against the build-start base and newly untracked files confirms that implementation changes affect only `kit/greet.py`, the test remains unchanged, and no new files appear outside `.sdlc/greet/`.

## Assumptions
- One mechanical L1 step suffices: verified by reading the two-line implementation and the existing test.
- Both runnable behavior criteria are red because the greeting is missing: each probe exited 1; the existing test failed and the additional names assertion failed.
- No non-root entry instructions apply: `kit/AGENTS.md` does not exist.

## Risks
The read-only host emitted temporary-cache warnings, but both probes reached their assertions. Full discovery remains for the builder and verifier.
