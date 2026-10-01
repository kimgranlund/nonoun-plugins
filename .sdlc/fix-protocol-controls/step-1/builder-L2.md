<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/messages.py`: the selftest's `st_message` now takes `**values` so a test can override a field. Added helper `st_bad_value`, cases `case_bad_protocol` and `case_bad_follow_up`, and two new `SELFTEST_CASES` entries. No production check changed.

## Checks
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: exit 0, `messages selftest: PASS`.
- The `ok: .*protocol` grep-count criterion: exit 0.
- The `ok: .*follow_up_requested` grep-count criterion: exit 0.
- (guard) changed-file list limited to `messages.py`: exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. It ended with `ok: plugin validate` and printed `skip: shellcheck not installed`.
- Negative controls: I made two throwaway copies of `messages.py`, each with one production check disabled (`if False and ...`), then deleted them.
  - Protocol check disabled: the selftest fails on "refused: protocol value not the mailbox AGENTS.md" because `read` exited 0 instead of 1.
  - `follow_up_requested` check disabled: the selftest fails on "refused: follow_up_requested not true or false" in the same way.

## Notes
- The protocol case writes the file by hand with `protocol: elsewhere/AGENTS.md`.
- Each refusal case checks four things:
  - `read` exits 1 and its error names the bad field.
  - The mailbox is unchanged.
  - The file stays only in `new/bob/`.
  - `read_time` is still empty.
- The `send --follow-up maybe` half of the follow-up case runs in a fresh mailbox. `count` refuses to run while the invalid hand-written file is present, so it can't be compared in the first mailbox. In the fresh mailbox the case sends one valid message, then checks that the refused send leaves the mailbox unchanged and the `count` output the same.
