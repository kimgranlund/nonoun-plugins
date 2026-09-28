<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/check.py`: added docstring item 6 and a merge-step template check placed after the plan-defect route checks. It extracts the block, compares the two copies, runs `steps.py lint` in a temp dir that it then deletes, and requires `git merge --no-ff` in `agents/builder.md`.

## Checks
- Criterion 1 (handoff-format block changed): check.py exited 1 with "merge-step block differs", so the criterion exits 0.
- Criterion 2 (`wc -w)` broken in both files), run verbatim under bash: check.py failed with "fails steps.py lint: … does not parse", and the lint's stderr was in the message. The criterion exits 0.
- Criterion 3 (`--no-ff` removed from builder.md): check.py exited 1 with `agents/builder.md: missing "git merge --no-ff"`.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0 (`ok: 18 role levels, 8 agents checked`).
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. The selftests, shellcheck and plugin validate all passed.

## Notes
The lint runs with `python3` from PATH, because the handoff specifies that command.
