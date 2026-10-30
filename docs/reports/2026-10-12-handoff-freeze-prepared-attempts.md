---
doc-type: report
date: 2026-10-12
scope: T-0505, step 1
---
# Handoff freeze for prepared attempts

`dispatch.py prepare` now writes the running marker beside the handoff, so the handoff edit hook warns or denies for a sub-agent attempt as it does for a `run.sh` run, and `dispatch.py record` and `dispatch.py recover` release it. Offline checks show this end to end with no hand-made marker. A live run in a fresh Claude session was not made and is unverified.

Date: 2026-10-12. Ticket: T-0505, step 1. Base commit: `fdd2254a`. Source finding: F3 of [the Astra review](2026-10-12-sdlc-lite-astra-review.md). **[V]** marks a line a command in this tree showed; **[U]** marks a line no command checked.

## What changed

- **[V]** `plugins/sdlc/scripts/dispatch.py`: `prepare` writes `<role>-<level>.running` after the attempt and dispatch records, under the directory lock. The content is the epoch start in whole seconds, as `run.sh` writes it. `--dry-run` and a refused prepare write none.
- **[V]** `plugins/sdlc/hooks/warn-handoff-edit.sh` is unchanged. It reads the marker only, so there is one source for "an attempt is live".
- **[V]** `record` and both recover paths are unchanged. They already removed the marker by role and level; before this change nothing wrote it for a sub-agent dispatch.

## Baseline

The new hook suite was copied over the base plugin (`git archive` of `fdd2254a`), so it ran the base `prepare`:

```
t=$(mktemp -d) && git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C "$t" && cp plugins/sdlc-lite/scripts/hook-selftest.sh "$t/plugins/sdlc-lite/scripts/hook-selftest.sh" && bash "$t/plugins/sdlc-lite/scripts/hook-selftest.sh"
```

**[V]** It exited 1 and printed this line:

```
hook selftest: FAIL: handoff-edit prepared attempt warn: stderr lacks the freeze warning (prepare left no running marker)
```

**[V]** A direct probe at the base agreed: after a real `prepare scout L1` the task folder held the handoff, the attempt record and the dispatch record, no marker, and the hook exited 0 in deny mode.

## After the change

| Command | Result |
|---|---|
| `bash plugins/sdlc-lite/scripts/hook-selftest.sh` | **[V]** exit 0, `hook selftest: PASS` |
| `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` | **[V]** exit 0, `dispatch selftest: PASS`, 439 `ok:` lines, the six T-0505 labels among them |
| `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` | **[V]** exit 0 |
| `python3 plugins/sdlc-lite/scripts/board.py selftest` | **[V]** exit 0, `board selftest: PASS` |
| `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest` | **[V]** exit 0, `fleet_status selftest: ok` |
| `python3 plugins/sdlc-lite/scripts/docs_check.py` | **[V]** `0 errors`, as at the base |
| Step criterion 1 (deny after a real prepare, silent after `record`) | **[V]** exit 0 |
| Step criterion 2 (warn and one log line after a real prepare) | **[V]** exit 0 |

The prepared-attempt cases in the hook suite each build a throwaway git repo, run the real `dispatch.py prepare scout L1` under `env -i`, and create no marker by hand:

| Case | Observed |
|---|---|
| Warn | **[V]** exit 0, stderr holds `handoff freeze (warning)` and `scout-L1`, `stale-edits.log` holds one `edited while scout-L1 ran` line |
| Deny | **[V]** exit 2 |
| Completed | **[V]** exit 2 before `record`; `record` exits 0 with a valid scout result; then the hook is silent, exit 0 |
| Failed | **[V]** exit 2 before `record`; `record` exits 1 on error text and the attempt is `failed`; then the hook is silent, exit 0 |
| Recovered | **[V]** owner is a reaped child pid; exit 2 before `recover`; `recover` prints `marked interrupted`; then the hook is silent, exit 0 |
| Live attempt of another run | **[V]** owner is the suite's own pid; `recover` prints `no orphaned attempts`; the attempt stays `running` with the same `parent_pid`; deny mode still exits 2 |

## Negative control for the dispatch selftest

**[V]** With the one marker write in `prepare` replaced by `pass`, `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exited 1 with six `FAIL:` lines: five of the six T-0505 labels, and the existing case `a dead-parent attempt is recovered first`, which now expects the retry's own marker. The sixth label, `prepare --dry-run writes no running marker (T-0505)`, stayed `ok:`, because a dry run wrote nothing before the change either. The write was restored before the passing run above.

## Live check

Live fresh-Claude check: unverified

Reason: this step was built by a headless sub-agent. Its loaded plugin is the main checkout, not this tree, and a live probe makes model calls the user opts into. No Claude session was launched. **[U]** What stays unshown is that a fresh Claude Code session, with this tree's plugin loaded, has its Edit of a prepared handoff warned or blocked by the registered hook. The offline cases run the hook script itself on a payload the suite builds, not one a host sent.

Recipe for a later live run, after [the T-0212 record](handoff-freeze-live-run.md):

1. Make a throwaway git project in a temporary folder outside this repository, with one task folder holding a handoff.
2. Register `plugins/sdlc/adapters/claude/hooks.json` from this tree through `--settings`, with the commands rewritten to this tree's plugin path.
3. Run `dispatch.py prepare scout L1` on that handoff. Do not create a marker by hand.
4. Warn arm: start Claude Code with `--permission-mode acceptEdits` and `--allowedTools Read Edit`, and ask it to edit the handoff. Expected: the edit is applied and `stale-edits.log` gains one `edited while scout-L1 ran` line.
5. Deny arm: the same with `SDLC_HANDOFF_EDIT_MODE=deny`. Expected: the handoff is unchanged and the model reports that a hook blocked the edit.
6. Release arm: run `dispatch.py record` with a scout result, then repeat the deny arm. Expected: the edit is applied and the log gains no line.
7. Keep each arm's result JSON as evidence and record the Claude Code version and the model.

## Limits

- **[V]** The marker is named by role and level, not by stem, because `record` and both recover paths unlink it by that name (`close` and `recover_orphans` in `plugins/sdlc/scripts/dispatch.py`, `recover_unlocked` in `plugins/sdlc/scripts/run_lifecycle.py`). Two running attempts of the same role and level in one folder therefore share one marker, and the first to close removes it. Prepare refuses a second attempt in a folder while another session's attempt is alive; an attempt the same session owns does not block it (T-0371), so that is the one way to reach this state.
- **[U]** `board.py` and `fleet_status.py` now see a marker for sub-agent dispatches. Their selftests pass; no board or fleet view of a real sub-agent run was inspected.
- **[U]** Codex has no hooks, so nothing here changes on Codex.
