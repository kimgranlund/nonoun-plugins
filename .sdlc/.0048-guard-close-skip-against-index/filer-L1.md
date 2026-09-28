<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0048: Guard close --skip against follow-up index drift with --expect digest

## PR body
### Summary
`tickets.py close <slug> --skip N[,N...]` could skip the wrong follow-ups. That happened when the filer file's Follow-ups list changed between the `--dry-run` that showed the indices and the `--skip` call. Now the dry run prints a digest of the exact list it indexed. `--skip` has to pass that digest back with `--expect <digest>`. If the list has changed, close refuses and writes nothing.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`
  - New `follow_digest(items)`: the first 12 hex characters of a sha256 over the full ordered bullet texts. It hashes full texts, not titles, because `follow_up_title` cuts titles at 70 characters, so a rewording past that point would otherwise go unnoticed.
  - `--dry-run` ends with an `expect <digest>` line.
  - A writing close with `--skip` and no `--expect` refuses.
  - An `--expect` that does not match refuses, and the message names the drift (`does not match the current Follow-ups in <filer>`).
  - `--reason` now also refuses with `--expect`.
  - Help text and the module docstring are updated.
  - Selftest cases (p), (q), (r) and (t) are updated. A new case (v) covers:
    - a reordered list refusing and writing nothing
    - an unchanged list closing
    - `--skip` without `--expect` refusing
    - plain close still needing no token
    - a rewording past character 70 refusing
- `plugins/sdlc-lite/skills/file/SKILL.md` step 3:
  - Keep the dry run's digest and pass `--expect <digest>` with `--skip`, including in unattended mode.
  - On `does not match`, rerun the dry run and ask again.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `[--expect DIGEST]` added to argument-hint, and item 4 describes the guard.
- `CLAUDE.md`: the tickets.py bullet describes the `expect` line, the `--skip` requirement and the mismatch refusal, and adds `--expect` to the flags that do not combine with `--reason`.
- `.claude/agents/sdlc-lite-author.md`: the sync rule now names `--expect`.

### Verification
**Step 1 (builder L2, verifier L1 Sonnet): pass**
- `tickets.py selftest` prints PASS.
- Negative control: in a scratch copy, the mismatch check was made a no-op. The selftest then failed on (v1) and (v5).
- Temp-root CLI runs:
  - The dry run ends in `expect <12 hex>`.
  - `--skip 2` with no `--expect` exits 1, and stderr ends with `nothing written`.
  - A reordered list with the old digest exits 1, and a hash of `.sdlc` showed nothing changed.
  - An unchanged list with the matching digest exits 0.
- `close --help` lists `--expect DIGEST`.

**Step 2 (builder L1, verifier L1 Opus): pass**
- `--expect` now appears in all three docs. At HEAD the count was 0 for each.
- The /file step 3.4 and 3.5 text matches what the script actually does when run.
- No new em dashes.
- `scripts/check.sh` exits 0, including `tickets selftest: PASS`. As a check that the gate can fail, an injected syntax error made it exit 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py close --skip` now requires `--expect <digest>` from the `--dry-run`'s last line. If the filer file's Follow-ups list has changed since that dry run, it refuses and writes nothing, so stale indices can no longer skip the wrong follow-ups. (T-0048)

## Follow-ups
None
