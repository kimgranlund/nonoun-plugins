<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0160: Add the `onboard` skill for entry files, docs layout, and check mode

## PR body
### Summary
A repository adopting SDLC Lite can now run one script to get entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout. Anything the repository already wrote in those files stays as it was. This implements `docs/specs/repo-onboarding/design.md` v0.7, including the role routing line in the root managed block.

### Changes
- `plugins/sdlc-lite/scripts/onboard.py` (new, standard library only, Python 3.9.6 in the runs):
  - `setup --dry-run`, `setup [--force]`, `check`, and `selftest` commands.
  - The `docs/layout.md` parser (`## Homes` and `## Frozen paths`) reports errors with a file and line number. Setup and check stop on a parse error.
  - The five design templates. Start markers carry a template version and a content hash.
  - The ordered upsert table, rows 1 to 8, where the first match wins.
  - Check mode labels each file, and it exits nonzero when a file is not current.
  - Both commands exit 1 with "not a Git work tree" outside a Git repository, and write nothing.
- `plugins/sdlc-lite/skills/onboard/SKILL.md` (new): the skill, with its commands, check labels, workflow, and rules.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: a route table row for `onboard`.
- `plugins/sdlc-lite/scripts/check.sh`: runs the `onboard.py` selftest.
- `plugins/progressive-context/skills/progressive-context/references/sdlc-lite.md`: one sentence that names the `onboard` skill, with no path link.
- `docs/specs/repo-onboarding/design.md` and `docs/specs/repo-onboarding/README.md`: the status lines now say the design is implemented and the reorganization is not.
- `docs/reports/onboard-live-run.md` (new), linked from `docs/README.md` and `docs/specs/repo-onboarding/README.md`: the dated live run report.

### How each was verified
All five steps have a verifier verdict of pass.
- Selftest: `onboard.py selftest` exits 0 and prints eight gates, each `positive ok, negative ok`: layout-parsing, import-detection, create, preserve, idempotence, row-order, malformed-markers, and check-mode.
- Negative controls:
  - The step 2 verifier put ten defects into a temp copy of the script, one at a time, and the matching gate printed FAIL for each.
  - The step 1 verifier did the same for the parser and import gates.
  - One mutant survived: `digest()` hashing the wrong input. The gates only compare marker and text with each other. The verifier confirmed the real hashes independently with `shasum`, and all four matched.
- Templates: the verifier extracted the five ```markdown blocks from the design and compared them with the script constants. All five are identical.
- Preservation: a file with existing user content keeps its bytes before the appended block. A CRLF file stays CRLF. An edited block is reported and left alone unless `--force` is given.
- Live run gate: a plain session with tools disabled, run on Claude Code 2.1.285 and on Codex (codex-cli 0.154.0, `gpt-6-astra`). With the block present, both hosts quoted `Managed by SDLC Lite onboard, template 1.`. With the block deleted, both answered `ABSENT`. The step 4 verifier reran all four arms in a fresh project and got the same results.
- Repository gates: `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, and `git diff --check` all passed in step 5. shellcheck was skipped because it is not installed.
- Not verified: skill validation against a repo or host validator, because none is installed. The user-scoped harness linter reported 2 F2 failures and 1 W2 warning on both the `onboard` and Progressive Context skills. F2 is the rule that `disable-model-invocation` and `user-invocable` must be declared explicitly. W2 is the missing "Use when" trigger phrasing. These are the user's own house rules, not a repository gate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added the `onboard` skill and `plugins/sdlc-lite/scripts/onboard.py`. It creates or updates `AGENTS.md`, `CLAUDE.md`, `docs/AGENTS.md`, `docs/CLAUDE.md`, and `docs/layout.md` from the design templates without changing existing user content. `check` reports each file's state and exits nonzero when a file is not current.

## Follow-ups
- decide: The skill validator was not run against `onboard` or `progressive-context`. The house linter flags F2 (`disable-model-invocation` and `user-invocable` not declared) on both skills, so someone must decide whether to adopt that rule.
- note: The design.md status line still begins "proposed v0.7", because step 3 replaced only the "Nothing implemented" sentence.
- note: The step 4 and step 5 builders left throwaway projects in the OS temp folder (`/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.HxvEeKNiKL` for step 4), because `rm -rf` was denied. The step 4 verifier's own temp folder is also still there.
- note: The design's "Unsettled" item, whether an installed plugin can read its own template version on both hosts, is not covered by any artifact. The token cost of nested entries in a real role run is not covered either.
