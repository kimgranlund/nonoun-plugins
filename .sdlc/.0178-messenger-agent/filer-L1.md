<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0178: Messenger agent with Codex mapping and check.py coverage

## PR body
### Summary
Adds `messenger` as a declared session agent for Claude and Codex. It polls the mailbox through `messages.py` and reports claimed messages to its parent. `check.py` now fails when the agent file or its Codex mapping is missing. Depends on T-0177 for the `messages.py` commands.

### Changes
- `plugins/sdlc-lite/agents/messenger.md` is new. It is a long-lived session sub-agent, not a `run.sh` role, pinned to `claude-haiku-4-5`.
  - It polls with `messages.py count --receiver` and `list` every 10 seconds.
  - It claims each message with `messages.py read <id> --receiver <harness>`, as the built `messages.py` requires.
  - It reports each claimed message's id and its path `read/<harness>/<id>.md`.
  - It never acts on a message body.
  - It sends and ack's only through `messages.py`, and no ack on `follow_up_requested` before the parent has replied.
  - It defers to `.sdlc/messages/AGENTS.md` for the procedure.
  - It states the Claude and Codex host limits separately, so one host working says nothing about the other.
- `adapters/codex/models.json` gains a `messenger` entry at the scout tier (`gpt-5.6-terra`). `scripts/codex_roles.py` adds `messenger` to the `workspace-write` tuple. The Codex agent `sdlc-messenger-l1.toml` is generated, not hand-edited.
- `scripts/check.py` has a new messenger check for the agent file, the `models.json` entry and the generated TOML. It includes three inline negative controls.
- `skills/level-rubric/SKILL.md` says the messenger is not a `run.sh` role, in prose rather than a table row. The planner and plan-reviewer TOMLs that preload that skill were regenerated.
- `docs/codex-role-execution.md` gains a Messenger row, a count of 25 agents (21 base), and a paragraph on the Codex and Claude limits.
- `plugins/sdlc-lite/AGENTS.md` and the repo `AGENTS.md` now list the `conductor` and `messenger` session agents.
- The `docs/ticket-stages/design.md` Message bus status line now says the messenger is built in T-0178.
- `run.sh`, its role table, `agents/conductor.md`, the hooks, and all version numbers are unchanged.

### Verification
- **Step 1, agent file, mapping and check.py (verifier L2: pass):**
  - The body literals, the model pin, and the `models.json` and TOML assertions were checked, and there are no em dashes.
  - In temp copies, removing the agent file, the `models.json` entry, or the TOML each made `check.py` print its own `FAIL messenger:` line and exit 1. An unmutated copy printed only `ok: 19 role levels, 9 agents checked`.
- **Step 2, docs and messenger CLI alignment (verifier L1: pass):**
  - All 17 criteria passed, including the five regenerated TOMLs, the doc count derived at run time, the `--receiver` and `read/<harness>/<id>.md` wording, and the changed-file allowlist.
  - The `--receiver` check was red against the old line.
- **Step 3, all gates green (verifier L1: pass):**
  - `codex_roles.py generate --check`, `scripts/check-packaging.py`, `codex-selftest.py` (installed 25 project agents), `check.py` and `bash plugins/sdlc-lite/scripts/check.sh` all passed.
  - In a detached temp worktree, deleting `agents/messenger.md` and removing the `models.json` entry each turned `check.py` red. Removing the `models.json` entry also made `generate --check` exit 2 with an orphan-TOML drift error.
- Not covered: live validation on either host belongs to T-0179. Nothing here shows the messenger running on Claude or Codex.

## Changelog entry
- Added the `messenger` session agent for Claude and Codex. It polls `messages/new/<harness>` every 10 seconds through `messages.py` and reports claimed messages to its parent. `check.py` now fails when the agent file or its Codex mapping is missing.

## Follow-ups
- note: `check.sh` skipped shellcheck in both step runs because it is not installed, so the shell checks there were not run.
- note: the step 3 `run.sh` unchanged guard compared against `SDLC_BASE_SHA`, which equalled HEAD, so it could not go red there. The `run.sh` diff was not otherwise independently inspected in the artifacts.
- note: the messenger has not been run live on Claude or on Codex. That evidence is T-0179's scope.
