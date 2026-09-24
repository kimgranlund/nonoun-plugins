<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `src/routes/+page.svelte`: imported `Icon` next to `Button`. Replaced the `<span>×</span>` child in the "Icon only" section with `<Icon name="x" />`. `aria-label="Close"` is kept.

## Checks
- `grep -n '<Icon name="x"' src/routes/+page.svelte` matched at line 34.
- `grep -n "×" src/routes/+page.svelte` matched only line 56, `<h2>Tier × scale × size</h2>`. That is an existing heading, not the icon child, so I left it.
- `pnpm vitest run src/routes`: 1 file, 1 test passed.
- `pnpm check`: 0 errors, 0 warnings. The `echo check=$?` after it printed 0, but that reports the exit of `tail`, not of `pnpm check`.
- `pnpm lint`: Prettier reported all files formatted. The output was cut to the last 5 lines, so I did not see the eslint result or the exit code.
- `pnpm build`: publint reported "All good!". I did not check the exit code.
- `pnpm test`: 6 files, 28 tests passed. I did not check the exit code.

## Notes
- The "grep finds nothing" criterion is not met literally. The remaining `×` is in an unrelated `<h2>` heading. The icon-only Button no longer uses it.
- I piped every command through `tail`, so exit codes were not captured. The output shows no failures, but a strict exit-code check has not been run.
