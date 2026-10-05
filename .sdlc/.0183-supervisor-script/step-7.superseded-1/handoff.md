## Task goal
A deterministic script, with no model call, that notices new mail for a harness whose host is idle and resumes that host from a headless call, inside hard limits, and can be stopped.

## Step 7: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 to 6.

1. Run every gate from the repository root:
   - `bash plugins/sdlc-lite/scripts/check.sh` in full, with the Bash timeout at 1800000. It now includes the supervisor selftest.
   - `python3 scripts/check-packaging.py`
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
   - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
   - `python3 docs/reports/supervisor-live-run/probe.py selftest`
   - `git diff --check`
2. Why the guards split `check.sh` into groups: `steps.py split --only` runs each guard span under a 300 s limit and refuses a timeout (`--guard-timeout`, steps.py docstring). One span running all of `check.sh` took 307 s in the plan review. Its parts summed to 273 s at plan time under load average 18 to 28, before the supervisor selftest was added. Each guard below runs one group of `check.sh` lines, in `check.sh` order. Plan-time times per group: 1 s, 43 s, 57 s, 34 s, 45 s, 60 s, 33 s, and 0 s.
   - The supervisor selftest guard runs only when `check.sh` lists that selftest. It is green before step 2 and binding from step 2 on: if `check.sh` lists it and the file is missing or red, the guard is red.
   - The probe selftest guard runs only when the step 5 record exists, with the same effect.
   - shellcheck is not installed on this host, so `check.sh` prints `skip: shellcheck not installed`. No guard covers shellcheck, because its red cannot be observed here.
3. Fix any red the earlier steps introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as `inherited red`. All gates were green at plan time.
4. Confirm that no em dash (U+2014) was added in any changed or new file, including the untracked files.
5. Do not bump versions, tag, push, or publish. Never edit generated Codex TOML by hand.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py && python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py && python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite && python3 plugins/sdlc-lite/skills/decompose/scripts/coverage_check.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest && python3 plugins/sdlc-lite/scripts/board.py selftest && python3 plugins/sdlc-lite/scripts/steps.py selftest && python3 plugins/sdlc-lite/scripts/order.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest && python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest && python3 plugins/sdlc-lite/scripts/messages.py selftest`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh && bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `claude plugin validate plugins/sdlc-lite`
- (guard) `if grep -qF 'supervisor.py" selftest' plugins/sdlc-lite/scripts/check.sh; then python3 plugins/sdlc-lite/scripts/supervisor.py selftest; fi`
- (guard) `if test -e docs/reports/supervisor-live-run.md; then python3 docs/reports/supervisor-live-run/probe.py selftest; fi`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- (guard) `for f in $(git ls-files --others --exclude-standard -- . ":(exclude).sdlc"); do ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `f=plugins/sdlc-lite/scripts/supervisor.py; if test -e "$f"; then ! grep -qE "shell=True|os\.system\(|os\.popen\(" "$f"; fi`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh -e docs/README.md -e plugins/sdlc-lite/scripts/tickets.py -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/ticket-stages/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxE "plugins/sdlc-lite/scripts/supervisor\.py|docs/reports/supervisor-live-run\.md|docs/reports/supervisor-live-run/(probe\.py|AGENTS\.md|CLAUDE\.md|[a-z-]+\.txt)")"`
