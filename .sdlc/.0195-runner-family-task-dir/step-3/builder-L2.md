<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/validation/runner-family-task-dir-live-run/dry-run-base.txt: rewritten by shell redirection from the pre-fix run.sh at 171e13b. It now shows `--model sonnet`.
- docs/validation/runner-family-task-dir-live-run/dry-run-fixed.txt: rewritten by shell redirection from the current run.sh. It shows `--model opus`.
- docs/validation/runner-family-task-dir-live-run.md: new report.
- docs/README.md: added one index line after the Messages wait live run line.

## Checks
- Item 1 records:
  - `claude --version`: 2.1.286
  - HEAD: e0f7d2e
  - run.sh blob: e5308edf87a23bd02eb179eab631250a1bf24819
  - base: 171e13b72a516ccad2472d866f072add289079cf
  - pre-fix run.sh blob: dc34865ecd542cb3e55516cc4803a7071f3b7364
- Rebuilt project dry runs, run through the wrapper W with no model call:
  - The base run printed `--agent sdlc-lite:verifier --model sonnet --effort medium`.
  - The fixed run printed `--model opus --effort medium`.
  - The project's `.sdlc/fam` was unchanged after both runs.
  - The project and the extracted plugin were removed afterwards.
- Old temp dir init model ids:
  - verifier-L1.log: `claude-opus-5-5`
  - builder-L1.log: `claude-sonnet-5-5`
- Acceptance criteria 1 to 7: all pass.
- Guards:
  - opus in the fixed file: pass.
  - The two dry-run files match once normalized: pass.
  - The inline pre-fix and fixed dry-run guard: pass.
  - `fam/` unchanged against `$SDLC_BASE_SHA`: pass.
  - The `fam/` headers, `runs.jsonl` and `attempt.json`: pass.
  - The changed-file allowlist: pass.
- `git diff --check` flags trailing whitespace on line 1 of both dry-run files.

## Notes
`git diff --check` flags both dry-run files because run.sh's dry-run output itself ends with a trailing space. The handoff says these files are written only by shell redirection, so I left that space in place.

No live role was rerun. The first attempt's temp dir was left in place, as the handoff asks.
