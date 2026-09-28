<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits non-zero, and the failure output names the new cases: pass. Evidence: I ran it and got rc=1 with "tickets selftest: FAIL, these did not bite:". It listed four new cases:
  - "new --numbered writes config with the numbered line"
  - "after new --numbered, plain check fails a renamed 0009-gamma: rc=0 ''"
  - "new --numbered keeps existing config lines and adds the numbered line once"
  - "new --numbered (twice) leaves one ticket_folders: numbered line: ''"
- The negative control (the plain `new` case) is already green: pass. Evidence: "plain new writes no config" is absent from the failure list. The "line present" case, which passes today, is also absent.
- The five requested cases are present in the diff (tickets.py lines 597-621): pass. Evidence:
  - The renamed-folder case asserts rc 1 and the exact "folder prefix 0009- does not match id 'T-0003'" message on a plain `check`.
  - The config-written, existing-config, no-duplicate (twice and line present) and plain-mode cases are all there.
  - The red observed for the rename case (rc=0 with empty stderr) shows that assertion can fail.

## Out of scope changes
None. `git diff` shows only tickets.py changed, +27 lines. The other entries in `git status` are untracked `.sdlc/` task artifacts.

## For the next attempt
None
