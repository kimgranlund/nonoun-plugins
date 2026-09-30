<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added the `corpus` family, which runs ingest and all four detector families over this repo's `.sdlc` traces. It checks attempt coverage, the run-line to row mapping, and the five known findings. When the fixture data is missing it prints a `skip:` line instead.
- `plugins/sdlc-lite/scripts/traces/ingest.py`: `task_dirs` now also reads `.`-prefixed task folders that hold a `handoff.md`. The docstring says so.
- `plugins/sdlc-lite/scripts/check.sh`: added `python3 "$root/scripts/traces.py" selftest || fail=1` after the onboard selftest line, and named traces.py in the header comment.

## Checks
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`: exit 0, 91 `ok:` lines, `traces selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest | grep -q '^ok: corpus: '`: passes.
- `grep -qF 'traces.py' plugins/sdlc-lite/scripts/check.sh`: passes.
- (guard) scope test (`git diff`/`ls-files` against `$SDLC_BASE_SHA`): passes.
- Negative control: changed the expected `.0134` evidence path to `verifier-L9.md` in a temporary copy. `-k corpus` printed `traces selftest: FAIL`. The original file was restored.
- `git diff --check`: clean.
- `bash plugins/sdlc-lite/scripts/check.sh` was not run.

## Notes
- Ingest change: the corpus assertion first failed because ingest skipped `.sdlc/.onboard-digest-gate`. That is a closed task folder whose name is not `.NNNN-<slug>`, and it holds 2 attempt files. The handoff requires dot folders to be walked, so ingest now reads any `.`-prefixed folder that has a `handoff.md`.
- Run-line check scope: this is narrower than the literal wording. It only covers `runs.jsonl` files in the task dirs and step dirs that ingest reads. Three lines live in subfolders that ingest never walks, so they belong to no row: `.sdlc/.0106-extend-claude-agents-sdlc-lite/verify/runs.jsonl#0` and `.sdlc/.0016-ticket-numbered-folders/old-step-3/runs.jsonl#0` and `#1`. Covering them would mean widening ingest beyond this step. If they matter, a planner could make that a follow-up.
- The `overwritten-gate-log` part printed `skip: corpus: overwritten-gate-log: .worktrees/fanout-night/logs is absent`, because this worktree has no `.worktrees/` directory. That branch has not been exercised.
