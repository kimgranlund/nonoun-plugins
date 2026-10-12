<!-- role=builder level=L1 model=gpt-6-luna effort=low -->
profile: 0.22.4+be9ae1335861

## Status
done

## Changes
kit/greet.py: changed `greet(name)` to return `f"Hello, {name}!"`.

## Checks
- `python3 -B -m unittest discover -s tests -p test_greet.py -v` - passed; 1 test ran.
- `python3 -B -c 'from kit.greet import greet; assert all(greet(name) == "Hello, " + name + "!" for name in ("Ada", "Grace", ""))'` - passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` - passed; 1 test ran.
- Compared changes against base `d48ab0d1071aee1fa3ad0c2dde25dd11e48973bf`: only `kit/greet.py` changed; the test is unchanged. Untracked launcher artifacts are present under `.sdlc/greet/`, plus `builder.err` and `builder.out` at the repository root.
- `results.py validate .sdlc/greet/step-1/builder-L1.md --role builder` - failed: requires a role/level/model/effort header on the first line. The requested report format and profile fingerprint were retained.

## Notes
`redck.py record` ran before the edit but recorded retrospective controls, not a pre-edit checkpoint, because source paths already differed from the base. Both red checks were red at base. No implementation changes exist outside `kit/greet.py`.
