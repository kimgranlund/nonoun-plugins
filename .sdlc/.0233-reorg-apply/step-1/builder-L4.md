<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/reorg.py` (new): `apply PLAN [--root DIR] [--dry-run] [--approve DIGEST]` and `selftest`. It has the refusals, in-memory batch rewriting, digest, per-batch commits, final check, restore, and managed-block hash refresh. The rules are in the header docstring. It imports `onboard`, `rename_refs`, and `inventory` as plain lines after `sys.path.insert`.
- `plugins/sdlc-lite/scripts/check.sh`: added `python3 "$root/scripts/reorg.py" selftest || fail=1` after the `inventory.py` line.

## Checks
- `python3 plugins/sdlc-lite/scripts/reorg.py selftest`: exit 0. Prints `ok <gate> positive` and `ok <gate> negative` for all 15 gates, then `reorg selftest: PASS`. Runs in about 20 s.
- Acceptance criteria 1 to 12, each run as written through `bash -c`: all PASS. Afterwards one refusal message was corrected (a tracked link-fix file that is a symlink or missing was called "frozen"; it now says "not a tracked Markdown file"). On the final file, criteria 1, 2, and the guard (12) were rerun: PASS. Criteria 3 to 11 were rerun: PASS.
- Looked directly at the restore-fixture output: the dry run listing is correct; the apply prints `final check failed: docs/b.md: missing.md` and `restored to <sha>`; `git status --short` is empty afterwards.
- Usage error (`--approve` with no value): exit 2.
- On the managed fixture, `onboard.run_check` labels `AGENTS.md` as `stale`, not `edited`, and the hand-edited `docs/AGENTS.md` keeps hash `000000000000`.
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: exit 0.
- `python3 plugins/sdlc-lite/scripts/rename_refs.py selftest`: exit 0, PASS.
- `python3 plugins/sdlc-lite/scripts/inventory.py selftest`: exit 0, PASS.
- `git diff --check`: clean. `bash -n plugins/sdlc-lite/scripts/check.sh`: ok.
- `ast.parse(..., feature_version=(3,9))` passed, and everything above ran on system Python 3.9.6.
- No linter ran: pyflakes, ruff, and flake8 are not installed.
- `__pycache__` is ignored by Git, so the guard sees no stray files.

## Notes
1. Link fixes. A fix claims its span before rules 1 to 3 and writes `new` as given. That span is only examined again in later batches. The listing prints one `fix` line per matching occurrence.
2. Link span. The span a link claims is the whole regex match, and for `INLINE_LINK` that starts at `](`. So a mention in the link text is rewritten too: `[a.md](a.md)` becomes `[topic/a.md](topic/a.md)`.
3. NUL bytes. A file containing a NUL byte is treated as not text, even if it decodes as UTF-8. If it holds the bytes of a `from`, the plan is refused instead of rewriting the file.
4. Rule 7f. A fenced or non-Markdown citation whose text is exactly the repo-root `from`, or `/` plus `from`, is handled as a token rewrite, not a refusal.
5. Baseline lines print once, after all batches and just before `digest`.
6. The case-fold check against untracked paths uses `--exclude-standard`, so untracked files Git ignores are not compared.
7. The `running` gate starts short-lived child processes to hold `.run.lock` flocks. They exit when their stdin closes, and only those PIDs are waited on or killed.
8. In `check.sh` only the selftest line was added; the header comment is unchanged.
