<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/check.py: added docstring item 10 and a read-first route check over the seven files. The check has a replace-based negative control.

## Checks
- `python3 plugins/sdlc-lite/scripts/check.py`: printed `ok: 18 role levels, 8 agents checked`, rc=0.
- Criterion 1, with `Read first` replaced by `Read later` in agents/builder.md: exit 1 and a matching FAIL line. Pass (ac=0).
- Criterion 2, same sed on skills/fix/SKILL.md: exit 1 and a matching FAIL line. Pass (ac=0).
- `git diff --check`: clean.

## Notes
If one of the files is missing, the check reports it as a miss with the same message, `read-first route missing "Read first"`.
