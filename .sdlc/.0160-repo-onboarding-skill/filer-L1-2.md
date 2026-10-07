<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0160: Add the `onboard` skill for entry files, docs layout, and check mode

## PR body
### Summary
A repository adopting SDLC Lite can run one script to get entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout. Anything the repository already wrote in those files stays as it was. This implements `docs/specs/repo-onboarding/design.md` v0.7, including the role routing line in the root managed block. All six steps have a verifier verdict of pass.

### Changes
- `plugins/sdlc-lite/scripts/onboard.py` (new, standard library only, run on Python 3.9.6):
  - Commands are `setup --dry-run`, `setup [--force]`, `check`, and `selftest`.
  - The `docs/layout.md` parser (`## Homes` and `## Frozen paths`) reports errors with a file and line number. Setup and check stop on a parse error and write nothing.
  - The five design templates, with start markers that carry a template version and a content hash.
  - The ordered upsert table, rows 1 to 8, where the first match wins.
  - Check mode labels each file and exits nonzero when a file is not current.
  - Setup and check exit 1 with "not a Git work tree" outside a Git repository, and write nothing.
- `plugins/sdlc-lite/skills/onboard/SKILL.md` (new): the skill, with its commands, check labels, workflow, and rules.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: a route table row for `onboard`.
- `plugins/sdlc-lite/scripts/check.sh`: runs the `onboard.py` selftest.
- `plugins/progressive-context/skills/progressive-context/references/sdlc-lite.md`: one sentence that names the `onboard` skill, with no path link.
- `docs/specs/repo-onboarding/design.md` and `docs/specs/repo-onboarding/README.md`: the status now says the design is implemented and the reorganization is not.
- `docs/AGENTS.md` template (design and script): links an existing `docs/README.md` first under `## Contents`, and adds no line when it does not exist. `TEMPLATE_VERSION` stays 1.
- `docs/reports/onboard-live-run.md` (new), linked from `docs/README.md` and `docs/specs/repo-onboarding/README.md`: the dated live run report.

### How each was verified
- Selftest: `onboard.py selftest` exits 0 and prints eight gates, each `positive ok, negative ok`: layout-parsing, import-detection, create, preserve, idempotence, row-order, malformed-markers, and check-mode.
- Negative controls: the step 2 verifier put ten defects into a temp copy of the script, one at a time, and the matching gate printed FAIL for each. The step 1 verifier did the same for the parser and import gates.
  - One mutant survived: `digest()` hashing the wrong input. The gates only compare marker and text with each other. The verifier checked the real hashes with `shasum`, and all four matched.
- Templates: the verifier extracted the five ```markdown blocks from the design and compared them with the script constants. All five are identical.
- Preservation: a file with existing user content keeps its bytes before the appended block. A CRLF file stays CRLF. An edited block is reported and left alone unless `--force` is given.
- Live run gate: a plain session with tools disabled, on Claude Code 2.1.285 and on Codex (codex-cli 0.154.0, `gpt-6-astra`).
  - With the block present, both hosts quoted `Managed by SDLC Lite onboard, template 1.`.
  - With the block deleted, both answered `ABSENT`.
  - The step 4 verifier reran all four arms in a fresh project and got the same results.
- Repository gates (step 5): `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, and `git diff --check` all passed. shellcheck was skipped because it is not installed.
- Loose ends (step 6): the README link appears in `docs/AGENTS.md` when `docs/README.md` exists, and the selftest asserts it. "T-0161" no longer appears in the skill description. The design status reads "implemented v0.7." The selftest still passes.
- Not verified: no repo or host skill validator is installed. The user's house linter `skill_lint.py` reported 2 F2 failures and 1 W2 warning on both the `onboard` and Progressive Context skills. Those are the user's own rules, not a repository gate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added the `onboard` skill and `plugins/sdlc-lite/scripts/onboard.py`. It creates or updates `AGENTS.md`, `CLAUDE.md`, `docs/AGENTS.md`, `docs/CLAUDE.md`, and `docs/layout.md` from the design templates without changing existing user content. `check` reports each file's state and exits nonzero when a file is not current.

## Follow-ups
- decide: The house linter `skill_lint.py` flags F2 (`disable-model-invocation` and `user-invocable` not declared) and W2 (no "Use when" phrasing) on the `onboard` and `progressive-context` skills, and no repo or host skill validator has run on either; decide whether to adopt those rules.
- note: The step 4 and step 5 builders and the step 4 verifier left throwaway projects in the OS temp folder, because `rm -rf` was denied.
- note: The design's "Unsettled" items are not covered by any artifact: whether an installed plugin can read its own template version on both hosts, and the token cost of nested entries in a real role run.
- note: The selftest's `digest()` mutant survives, since the gates only compare marker and text with each other; the real hashes were confirmed once by `shasum`, not by a gate.
