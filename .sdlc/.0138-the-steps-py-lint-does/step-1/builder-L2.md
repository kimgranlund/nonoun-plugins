<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/steps.py: `is_command` now also counts a compound span as a command when a trailing redirect or pipe follows its closing keyword. The docstring and usage text say so, and four (k2) selftest cases are added.
- CLAUDE.md: the `scripts/steps.py` bullet now says compound criteria are linted when they end in a trailing redirect or pipe after the closing keyword (for example `done < f`).

## Checks
- Criterion 1 (`while ... done < f` with `|| echo` gets a lint finding): exit 0
- Criterion 2 (`for ... done | cat` with a fallback gets a finding): exit 0
- Criterion 3 (`done 2>/dev/null` is a command, and its fail-fast `|| exit 1` stays allowed): exit 0
- Criterion 4, guard (`for each file done < f` is not a command): exit 0
- Criterion 5 (`steps.py selftest` passes and prints `trailing redirect`): exit 0. All four new cases print `ok`, and no existing case failed.
- Criterion 6 (`grep -qF 'trailing redirect or pipe'` on steps.py): exit 0
- Criterion 7 (`grep -qF 'trailing redirect or pipe'` on CLAUDE.md): exit 0
- `plugins/sdlc-lite/scripts/check.sh`: exit 0

## Notes
The trailing-tail form needs a `;`, `&`, or newline before the closing keyword. The handoff's wider rule (whitespace alone before the keyword is enough) would make the guard prose `for each file done < f` a command, and the guard requires it to stay a non-command. The end-of-span rule is unchanged.
