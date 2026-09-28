## Task goal
The `steps.py` `||` lint (split and lint) also checks compound criteria (`for`/`while`/`until`/`if`/`{`) that end in a trailing redirect or pipe after their closing keyword, such as `while read x; do ...; done < f`, so an unlinted `||` fallback inside them is refused like any other; its selftest proves the new case fires and that allowed forms still pass.

## Step 2: Gates green
level: L1
### Do
Run the project's whole gate, `bash plugins/sdlc-lite/scripts/check.sh`, from the git toplevel. Fix any red that step 1 introduced (for example, a check.py doc-sync guard or a shellcheck finding), and keep step 1's behavior. If a gate was already red at `$SDLC_BASE_SHA`, report builder Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
