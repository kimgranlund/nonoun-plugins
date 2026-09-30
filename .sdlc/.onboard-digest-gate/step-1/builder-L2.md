<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/onboard.py: added `gate_digest` plus two defect variants (`_digest_raw`, `_digest_prefix`) and registered the `digest` gate in `GATES`, after `import-detection`.

## Checks
- `printf 'line one\nline two\n' | shasum -a 256` gave `e9024f1a07d29d52...`, so the expected literal is `e9024f1a07d2`. The CRLF version, `printf 'line one\r\nline two\r\n'`, gave `6612d9c94c2d...`, which shows the two inputs really differ before normalization.
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: exit 0. All 9 gates printed "positive ok, negative ok", including `gate digest`.
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qxF "gate digest: positive ok, negative ok"`: exit 0.
- Temporary break test: I removed the CRLF normalization from the real `digest()`. The gate then printed `gate digest: FAIL positive failed: CRLF text hashed to '6612d9c94c2d', expected 'e9024f1a07d2'`. I restored the file and reran; the gate passed again.
- `git diff --check`: clean.

## Notes
- The two variants the gate must reject are "hashes without normalizing line endings" and "returns a 16-character prefix".
- The comment above the gate gives the `printf ... | shasum -a 256` command used to compute the expected value.
- During the break test I kept a backup copy in `/tmp/ob.bak` and deleted it afterwards. No worktree was created.
