---
date: 2026-10-16
slug: cli-trace-field-test
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: field tester
    agent: general-purpose (fog-cli-trace-proof)
    model: claude-sonnet-5-5
    did: ran the new and the pre-fix scripts on real Claude Code and Codex traces, read-only, outputs in /private/tmp/claude-501/scratch/fog-cli-proof/
  - role: conductor
    agent: sdlc-lite conductor (main session)
    model: claude-opus-5-5
    did: wrote this entry from the field report
project: the skill itself; traces from the user's Claude Code (adia-ui-kit, 28,491 lines) and Codex (4 rollouts) sessions
verification: field test only, no independent verifier; this entry records findings, no skill file changed
backup: none (no skill file changed)
---

# 2026-10-16: field test of the script fixes on real CLI traces

Tests the `scripts/diagnostics.py` and `scripts/wrapped.py` fixes from `20261016-runtime-harness-learnings`, which unit tests alone had proven (web-chat bundles have no tool calls).

## Verified in the field
- `lookup_request` / `shell_lookup` (Claude trace A, 2,133 Bash calls): `cat > file` writes counted as lookups went from 263 to 0 (of 264). Lookup-matched Bash calls went from 1,575 to 435, and failed-discovery findings from 4 to 1. Two false positives are gone: heredoc writes whose script content printed "No such file". A true positive is kept: `sed -n` on a named missing file.
- Codex: failed-discovery assessed went from 35 to 3 and from 11 to 1. Two heredoc writes are no longer counted.
- `wrapped.py`, `cat a b`: exercised once (Codex). That call's exposures went from 0 to 3, one per file.
- `wrapped.py`, a Promise.allSettled batch plus an ascending indexed `for` loop: `parse_calls` went from 0 calls to 3 (Codex). There were no parse regressions across 249 wrapped inputs (194 parsed before, 195 after).

## Open (defects, not applied)
1. `shell_lookup` drops any segment holding a `>` token, so `cat X 2>/dev/null` and `cat X 2>&1 | head` return `[]` and a real read is hidden by a stderr redirect. Only a stdout redirect to a file should end a lookup.
2. A leading `cd DIR; sed -n ... file` (or `cd DIR && cat file`) returns `[]`, inherited from the `cd` guard in `read_requests`, so real reads in `cd` compounds are lost.
3. A variable target such as `ls -la $ST` is returned literally, so an error line naming the expanded path never matches and the finding is dropped.
4. Pairing is not proven end to end: the harness merged truncated outputs into one text block, so `pair_outputs` correctly returns None (block count is not call count). Add a regression fixture for a real truncated-output batch with an indexed loop; a reversed loop was not seen in any trace.
- Hydrating a 55k-line Claude trace ran over 9 minutes and was stopped; `--repo /tmp` makes Codex hydration crawl. Both are performance notes.
- Only one Claude trace backs fix 1, and three of the Codex rollouts were checked at parse level only.
