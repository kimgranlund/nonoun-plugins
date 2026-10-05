## Task goal
Independently fact-check docs/reports/release-0.20.3.md against this repository (branch release-0.20.3, built from commit dd14392 on top of tag v0.20.2) before the release is published. Read-only: edit nothing outside your own result file.

## Step 1: Fact-check the release record
level: L3

### Do
Read docs/reports/release-0.20.3.md and compare every concrete statement with the repo and with `git diff v0.20.2..HEAD` and `git log v0.20.2..HEAD`. Check at least: the `messages.py wait` flags, bounds, exit codes and output format against `messages.py wait --help` and its code; messenger.md and the regenerated Codex agents; results.py subcommands, the header line, `run.sh` and `steps.py` using it, `check.py` guards; `footprint.py` outputs and `check` flags; the chain skill `## Lean chain` text, the planner `## Coarse steps` rule, the `steps.py lint` warning conditions; the claim that no flow calls footprint.py and no script computes the lean lane; the filed ticket ids and their statuses under .sdlc/; the idle-host limit docs; the upgrade notes (is `codex_roles.py install` right, is the old-result "invalid result" statement true: reproduce it on a result with no header line using a temp copy); the Known limits (each cited doc says what the record says); every command in "Checks run for the release" actually exits 0 when you run it; the version numbers in all four manifests; that the record names nothing that is not in the diff and omits nothing material that is. Also check the record for em dashes and unsupported words like "verified" without a cited record.

### Acceptance criteria
- Every concrete claim in docs/reports/release-0.20.3.md is confirmed by a command or a file read, or listed in your result as wrong, unsupported or missing, one line each with evidence.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
- The record contains no em dash character.
