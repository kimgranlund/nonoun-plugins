## Task goal
Prove that the account can run an Astra builder and a Sol verifier through the actual SDLC runner, and independently review the narrowly scoped maintenance changes.

## Context
This is a throwaway Git project. The plugin launcher is /Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite/scripts/run.sh. The external repository at /Users/kimgranlund/Projects/nonoun/sdlc-lite is read-only evidence. Its maintenance base is 0ff454e. User authorized adding only gpt-6-astra -> gpt-5.6-sol as verifier alternate, regenerating agents, updating affected guidance/tests, and repairing the local config default. No other model or effort default may change, and scripts/run.sh must stay unchanged.
The account catalog and completed probes are /tmp/sdlc-codex-account-20260930/models.json, probes.json, and catalog-limits.json. No API-key account was tested. The host config now names gpt-6-astra; the config-after.events.jsonl records a completed turn with no -m override.

## Constraints
Do not edit the external repository or host config. Do not commit. Do not create another agent. Only value.txt is in the builder's implementation scope. .sdlc/ is ignored runner evidence.

## Step 1: Bump the fixture
level: L1
### Do
Change value.txt from value: 1 to exactly value: 2 followed by a newline. Run the acceptance checks. For the external maintenance criteria, inspect existing changes only; report any issue without fixing it.

### Acceptance criteria
- Run `python3 -c "from pathlib import Path; assert Path('value.txt').read_bytes() == b'value: 2\n'; print('fixture PASS')"`. It must print fixture PASS. Confirm this predicate rejects the base version with value: 1 (read it with git show; the verifier need not write a copy).
- Inspect `git diff --name-only` and `git status --short` in this throwaway project: only value.txt may differ outside ignored runner artifacts.
- Independently inspect `git -C /Users/kimgranlund/Projects/nonoun/sdlc-lite diff 0ff454e -- plugins/sdlc-lite/adapters/codex/models.json plugins/sdlc-lite/scripts/codex-selftest.py docs/references/codex-role-execution.md` and the three untracked generated sdlc-verifier-l*-alternate.toml files. All existing role models/efforts must be preserved. The alternate must map gpt-6-astra to the catalogued and live-probed gpt-5.6-sol, and generated alternate definitions must retain verifier contracts, read-only sandbox and configured efforts. Test fixtures must still exercise shared-model fallback with an empty alternate map and alternate routing through the real runner, rather than removing that coverage. Check current documentation for consistency with the mapping; historical dated observations may remain historical. Report semantic defects if any.
- Confirm `git -C /Users/kimgranlund/Projects/nonoun/sdlc-lite diff 0ff454e -- plugins/sdlc-lite/scripts/run.sh` is empty.

## Verification notes
Inspect the actual evidence and diff, not only the builder's claims. This is a single-account, single-machine transport smoke test, not broad model quality qualification. Parent runs the full selftest, packaging and generation checks outside your sandbox; do not substitute those structural results for your independent semantic review.
