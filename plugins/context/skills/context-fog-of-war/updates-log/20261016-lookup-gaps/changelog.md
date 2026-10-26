---
date: 2026-10-16
slug: lookup-gaps
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: verifier
    agent: sdlc-lite:verifier-L2 (fog-skill-lookup-gaps-verifier-L2)
    model: claude-sonnet-5-5
    did: independent verification, verdict pass; reran trace A hydrate (3 true-positive findings, 0 of 264 writes as lookups)
  - role: solo
    agent: sdlc-lite solo-L2 (fog-skill-lookup-gaps)
    model: claude-opus-5-5
    did: changed scripts/diagnostics.py, added tests in tests/test_diagnostics.py and tests/test_routing.py, wrote this entry
project: the skill itself; Open 1 to 4 of updates-log/20261016-cli-trace-field-test/changelog.md
verification: independent verifier L2 pass (2026-10-16); skill tests 24 of 24
backup: /private/tmp/claude-501/scratch/cfow-backup-1792161488
---

# 2026-10-16: shell_lookup false negatives and a merged-output batch fixture

Closes Open 1 to 4 of `20261016-cli-trace-field-test`.

## Added
- `tests/test_diagnostics.py`: `test_stderr_redirect_and_pipe_keep_lookup`, `test_cd_compound_keeps_relative_target`, `test_variable_target_matches_expanded_tail_only`. All three fail against the backup's scripts and pass now.
- `tests/test_routing.py`: `test_merged_truncated_batch`, a minimal excerpt of a Codex rollout batch (three `exec_command` calls, an ascending indexed loop, outputs merged into one truncated text block). `parse_calls` returns 3 calls and `pair_outputs` returns None; the same code with a reversed loop is rejected. It is a regression fixture for existing behavior, so it also passes against the backup.

## Changed
- `scripts/diagnostics.py` `shell_lookup` parses reader commands itself (`cat`, `head`, `tail`, `sed`, `nl`, `wc`, `less`, `more`) instead of borrowing `wrapped.read_requests`, which stays unchanged for exposure corroboration. `sed` takes any script, so `sed -n '40,60p;90,130p' file` is a lookup; `sed -i` is not.
- A `2>/dev/null`, `2>&1` or `2>>log` redirect is stripped before parsing and a pipe splits segments, so a read stays a lookup. A stdout redirect (`>`, `>>`, `1>`, `>|`, `&>`, `>&`) or a heredoc still ends one.
- A `cd`, `pushd` or `popd` segment no longer empties the command; later targets stay relative, as the error line prints them.
- A `$VAR` target is expanded from `NAME=value` (or `export NAME=value`) segments earlier in the same command. New `names_target` matches a still-unresolved target only when an error-line path ends with the literal tail after its last variable; a bare unresolved target never matches, and `diagnose` records the gap `Lookup target is an unresolved variable`. Session-wide assignments are not tracked.

## Fixed
- Trace A (`7c041c91...jsonl`, 28,438 events), full `fog.py hydrate` rerun into `/private/tmp/claude-501/scratch/fog-lookup-gaps/A.json`: failed-discovery findings went from 1 (16805) to 3 (615, 16771, 16805). 615 is `ls -la $ST` with `ST` assigned in the same command; 16771 is `grep ... $P` with `P` assigned the same way; both name a missing file. Assessed lookups went from 448 to 670. Bash calls matched as lookups went from 435 to 657 of 2,133, and `cat > file` writes counted as lookups stay 0 of 264.
- Lines 1938, 17301 and 17947 are now lookups (stderr redirect plus pipe, and two `cd DIR; sed -n` compounds).

## Open
1. Line 18529 is still not a lookup: its only read is `git show origin/main:docs/tickets/102.md | sed -n '1,45p'`, a `git show REV:PATH` form none of items 1 to 3 covers. Documented as not a lookup in 20261016-open-items; not parsed.
2. Session-wide `VAR=...` assignments across calls are not tracked; only the same command is. Ruled out in 20261016-open-items (reason there).
3. `references/diagnostics.md` does not yet say which shell forms count as a lookup request. Applied in 20261016-open-items.
