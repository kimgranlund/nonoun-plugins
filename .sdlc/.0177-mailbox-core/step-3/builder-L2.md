<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: added a header paragraph for the mailbox notice, and added the guarded notice block inside the `{ ... }` group, just before the lifecycle exec.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: added a header paragraph and a notice case before the final PASS line. The case uses a throwaway repo `$tmp/mrepo` and covers (a) through (d), with failures reading `notice: <reason>`.
- `plugins/sdlc-lite/scripts/check.sh`: added `python3 "$root/scripts/messages.py" selftest || fail=1` after the traces line, and named messages.py in the header's selftest list.

## Checks
- Criterion 1 (no-mailbox dry run is silent, then 1 message): exit 0
- Criterion 2 (role plus backend count is 2, no body printed): exit 0
- Criterion 3 (real run prints the notice once, no body): exit 0
- Criterion 4: the grep and `bash plugins/sdlc-lite/scripts/run-selftest.sh` both pass, printing "run selftest: PASS"
- Criterion 5 (check.sh grep): exit 0
- Criterion 6 (awk check that the block is inside the group): exit 0
- Guard (no em dash in added lines), with SDLC_BASE_SHA taken from step-3/base-sha: exit 0
- Guard (scope): exit 0, out empty
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: PASS
- `git diff --check`: clean
- `shellcheck`: not installed on this host, so it did not run

## Notes
- The selftest already has an `nrepo` (the .nvmrc cases), so my first draft of the new case reused that name and picked up its .nvmrc. I renamed the case's repo to `mrepo` and the case now passes.
- In the case's real run (d) the mailbox holds a planner message and a claude message, so the asserted line says 2. It is still checked to appear exactly once.
- Did not run the full `check.sh`; ran its new messages.py line and the run selftest on their own.
