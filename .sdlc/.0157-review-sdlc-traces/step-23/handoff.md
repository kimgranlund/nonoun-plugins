## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 23: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root and fix any red that steps 1 to 22 introduced (a `traces.py selftest` failure inside check.sh, a skill without its Codex route, a stale generated Codex agent, whitespace errors). A gate red at the build-start HEAD for a reason outside this task is reported as Status `inherited red: <tests>`. shellcheck is not installed on this host, so check.sh prints `skip: shellcheck not installed`; that is not a red. All three gates were green at replan time (check.sh takes about two minutes here).
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`
