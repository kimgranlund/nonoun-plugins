<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/onboard.py`: added the five design templates, `TEMPLATE_VERSION = 1`, marker hashing, the file-set model, block parsing, the ordered upsert table (`ROWS` and `decide`), `plan`, `run_setup` (`--dry-run` and `--force`), `run_check`, the "not a Git work tree" exit, and six new selftest gates. The Step 1 gates and code are unchanged, except that `_parse_layout` now reads the file and calls a new `_parse_layout_text`.

## Checks
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: exit 0 on Python 3.9.6, in about 2.5 s. It printed all 8 lines `gate <name>: positive ok, negative ok`.
- Acceptance criteria 1 to 9, each run through `bash -c` from the repo root exactly as written: all exited 0.
- Per-variant probe: each defective variant was rejected for its intended reason:
  - create: preflight off changed the fixture; no-starter variant gave empty starter text.
  - preserve: a line was written before the start marker.
  - idempotence: the second dry run printed a `Run 1`/`Run 2` diff.
  - row-order: the row 4 fixture was decided as row 6.
  - malformed-markers: the unclosed-start variant appended; the no-fence variant reported malformed.
  - check-mode: the edited and stale fixtures exited 0.
- FAIL path: I passed each gate's defect in as the real implementation. Every gate printed `gate <name>: FAIL ...` and the selftest returned 1.
- Templates: I extracted the five ```markdown blocks from the design's Templates section and compared them with the script constants. All five are identical.
- Exploratory fixture run from a subdirectory, with CRLF `AGENTS.md`, a symlinked `CLAUDE.md`, topics, homes, and a loose file with a space in its name:
  - The diff and writes were correct and the CRLF bytes were kept.
  - The second dry run was empty.
  - `check` returned 1 only because of the symlink.
- Edge probes:
  - A 30-document topic triggers the 30-line size report.
  - An edited block is reported without `--force` and replaced with it; `check` then exits 0.
  - Running inside `.git` gives "not a Git work tree" and rc 1.
  - `docs/layout.md` as a directory: rc 1, nothing written.
  - A non-UTF-8 layout gives `docs/layout.md:2: not valid UTF-8`, rc 1, nothing written.
- `onboard.py check` and `setup --dry-run` on this repo: `git status` and the hashes of every `AGENTS.md`/`CLAUDE.md` were the same before and after.
- `git diff --check`: clean. `python3 plugins/sdlc-lite/scripts/check.py`: exit 0. `python3 scripts/check-packaging.py`: PASS.

## Notes
- The design left several points open. These are the choices I made:
  - **Row 8 append:** no blank separator is added. A newline is added only when the last line has no line ending. Bytes outside the markers are therefore identical for a file that ends in a newline, and equal the original plus one newline otherwise. Inserted lines use the file's first line ending (CRLF stays CRLF). The hash is taken over LF-normalized text.
  - **Row 6 and forced row 4:** these replace the marker lines and the text between them. When the old end marker had no final newline, the replacement has none either.
  - **Malformed markers:** besides the design's three cases, a line that begins `<!-- sdlc-lite:managed:start` without a valid version and hash counts as malformed. So does an end-marker line that is not exact.
  - **Symlinked entry files** are outside the upsert table. `setup` skips them and reports `skipped <path>: symbolic link` on stderr, and `check` labels them `unmanaged`. Writing through a `CLAUDE.md -> AGENTS.md` link would overwrite the root block. As a result, a repo with a symlinked `CLAUDE.md` never gets `check` exit 0.
  - **Topics:** a topic with two or more documents gets an entry and a stub. One document is linked directly. A topic with none gets no link. An entry left over after its topic falls to one document is kept but leaves the managed set, so it is no longer updated or reported.
  - **Documents** must be tracked and also exist on disk. README and home existence are checked on disk.
  - **Frozen paths** only limit writes: a file is left out when its path, or any folder above it, matches. Frozen documents inside a topic that is not frozen are still linked.
  - **Documents under homes:** a document under a home nested inside a topic is not listed in that topic.
  - **`docs/README.md`** is not linked from `docs/AGENTS.md`, because the template has no slot for it.
  - **Link format:** links are list items, `- [text](target)`. A target containing a space or parenthesis is wrapped in `<...>`.
  - **Empty Contents:** with nothing to list, `## Contents` is followed by a blank line and then the end marker. This is the literal result of filling the template.
- Output and exit codes:
  - `setup` without `--dry-run` prints `created <path>` or `updated <path>` on stdout.
  - Size reports use the resulting text for `setup` and the current text for `check`. For this repo, `check` reports `AGENTS.md` at 70 lines.
  - `setup` exits 0 even when it reports rows 2, 3, or 4.
  - Errors exit 1.
  - `docs/layout.md` is listed last in output.
- Gate negatives:
  - The design names only bad inputs as the negatives for create, malformed-markers, and check-mode. Following Step 1's pattern, each of those gates also asserts the bad-input behavior on the real code and runs defective variants that must be rejected. The variants are listed under Checks.
  - The selftest needs `git` on PATH.
  - While fixtures run, the selftest removes `GIT_DIR`-style variables from the environment and restores them afterwards.
- Unverified: Python versions other than 3.9.6, and Windows.
