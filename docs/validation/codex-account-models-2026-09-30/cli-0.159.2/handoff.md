## Task goal
Prove the final Astra builder / 6.1 Sol verifier pair through run.sh after the user's CLI update to 0.159.2.

## Context
The current project is a throwaway plain-text fixture. The external repository /Users/kimgranlund/Projects/nonoun/sdlc-lite is read-only evidence with maintenance base 0ff454e. User authorized only the verifier alternate, generated profiles, affected tests/guidance, and local config repair; every other role model/effort and scripts/run.sh must stay unchanged. User prefers 6.1 or 6.0 where possible. New catalog and completed model probes are /tmp/sdlc-codex-account-20260930/cli-0.159.2/models.json and probes.json; all listed models completed, including gpt-6.1-sol. The earlier CLI 0.154.0 rejected that ID. The final alternate is gpt-6-astra -> gpt-6.1-sol.

## Constraints
Builder implementation scope is value.txt only. No commits or external edits. Verifier must inspect actual evidence, not accept builder claims. No further delegation. Parent already ran selftest, generation parity, and negative control; do not rerun those full suites in the read-only role sandbox.

## Step 1: Bump fixture
level: L1
### Do
Change value.txt to exactly value: 2 with one trailing newline. Run the fixture criteria. The maintenance review below is for the verifier; builder does not edit or grade the external changes.

### Acceptance criteria
- `python3 -c "from pathlib import Path; assert Path('value.txt').read_bytes() == b'value: 2\n'; print('fixture PASS')"` prints fixture PASS. The same predicate must reject the base bytes read using git show HEAD:value.txt; this needs no filesystem mutation.
- `git diff --name-only` and `git status --short` show only value.txt outside ignored runner evidence. Scope negative controls may use in-memory candidate path lists instead of creating files.

## Independent maintenance review (verifier)
Also inspect the external repository's actual diff from 0ff454e for models.json, scripts/codex-selftest.py and docs/codex-role-execution.md, plus its three new generated sdlc-verifier-l*-alternate.toml files. Independently compare current JSON to the base: only verifier_alternates changes, to gpt-6-astra -> gpt-6.1-sol. Confirm 6.1 Sol's catalog entry and completed probe. Normalize name/model in each alternate profile against its base profile; contracts, read-only sandbox and medium/high/high efforts must match. Inspect the changed tests: the empty-map fixture must retain sharing coverage and the runner test must exercise both shared and alternate CLI/header/run-record behavior. Inspect current guidance for consistency; historical dated observations may stay historical. Confirm external git diff 0ff454e -- plugins/sdlc-lite/scripts/run.sh is empty. Include your independent semantic findings and observed evidence in Criteria, and fail on a real defect. Do not run unrelated suites or write anywhere.
