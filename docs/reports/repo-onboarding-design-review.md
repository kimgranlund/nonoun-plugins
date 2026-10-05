# Repository onboarding design review

Recorded: 2026-09-29. Independent review of the onboarding design at v0.1, before it was committed. The reviewer was a fresh agent with no access to the authoring conversation. It was read-only and changed no file in this repository.

Subject: `docs/repo-onboarding/design.md` v0.1, an uncommitted working copy. The closest committed revision is v0.2 in 3ac677c, which already contains the fixes. The v0.1 text was not preserved, so these findings cannot be rechecked against the exact material reviewed.

Verdict: ready after fixes. No blockers, 8 major findings, 5 minor.

## Findings

| # | Severity | Finding | Reviewer's evidence | Outcome |
| --- | --- | --- | --- | --- |
| 1 | Major | The rule that `.sdlc/AGENTS.md` must not cite tickets relied on `tickets.py close`, which does not refuse when Git ignores `.sdlc/`. | Throwaway repository with `.sdlc/` ignored and an entry file citing `0001-beta`: `close` returned 0 and left the cite. | Fixed in v0.2. The skill checks its own block. |
| 2 | Major | `tickets.py` link rewriting cannot express a move to another directory. | `tickets.py:330-331, 367`. A call to `rewrite_files` for `docs/reports.md` to `docs/reports/validation.md` left relative links unchanged. | Fixed in v0.2. A new rewriter is planned. |
| 3 | Major | Dated evidence was frozen, yet the first trial listed it as a mismatch to move. | `docs/reports/readiness-recovery-validation.md` line 3. | Fixed in v0.2. Frozen material stays in place. |
| 4 | Major | A single `docs/reports/` home was attributed to Progressive Context. | Progressive Context `SKILL.md:24, 28`. | Fixed in v0.2. It is stated as this skill's default. |
| 5 | Major | `.sdlc/AGENTS.md` copied facts owned by plugin skills, with no staleness check. | `handoff-format/SKILL.md:12-30, 51-71`, `ticket/SKILL.md:18`. | Fixed in v0.2. Routes only, plus a version marker and check mode. |
| 6 | Major | Several validation rows could not fail. | Root `AGENTS.md` requires an observed negative control per gate. | Fixed in v0.2 and extended in v0.4. |
| 7 | Major | No component was named as the one that refuses, and nothing guarded against a stale plan. | `run_lifecycle.py:29, 44`, and the `--expect DIGEST` pattern in `tickets.py`. | Fixed in v0.2. One script, with a digest recheck. |
| 8 | Major | Upsert appended a block unconditionally and would duplicate existing routes. | Root `CLAUDE.md` and root `AGENTS.md` in this repository. | Fixed in v0.2. Target detection was specified in v0.4. |
| 9 | Minor | The final check covered only changed or moved files. | The design's own step 5 and move safety text. | Fixed in v0.2. |
| 10 | Minor | "SDLC Lite has no setup step" ignored the Codex install. | `codex_roles.py:197-198`, `skills/sdlc-lite/SKILL.md:48-50`. | Fixed in v0.2. |
| 11 | Minor | The first trial listed the wrong citing files and omitted two loose documents. | `grep` of `plugins/progressive-context/AGENTS.md` found no `docs/` path. | Fixed in v0.2. |
| 12 | Minor | `.codex/` does not exist in this repository, and existing entry files exceed the proposed size targets. | `ls`, and line counts of 70 and 40. | Fixed in v0.2. |
| 13 | Minor | The proposed link from Progressive Context would be its first cross-plugin link. | `scripts/check-packaging.py:51-56`. | Fixed in v0.2. The skill is named, not linked. |

## Checked by the reviewer and found correct

- `tickets.py close` refuses on a cite and scans `.sdlc/AGENTS.md` when `.sdlc/` is tracked (`tickets.py:299-306`, observed exit 1). A bare folder name with no slash did not block.
- An `AGENTS.md` in the `.sdlc/` root did not disturb `tickets.py` (check, roadmap, close, archive dry run), `board.py` (default, summary, lanes), or a `fanout.py` dry run. Their root enumerations read directories only.
- `.sdlc/roadmap.md` is generated (`tickets.py:142`).

## Not checked by the reviewer

- `steps.py`, `run.sh`, a real fanout run, and the Codex paths with an `AGENTS.md` in the `.sdlc/` root.
- Host loading of nested entry files and token cost. These were measured later in the [loading probe](nested-entry-file-loading.md).

## Limits

- Correction, 2026-09-29. An earlier version of this record said that `handoff-format/SKILL.md:32` says nothing about ignoring `.sdlc/`. That was wrong. The line ends with "Add `.sdlc/` to the project's `.gitignore` unless the user wants the trail committed." The author of this record had read a truncated view of the line. The reviewer's citation in finding 1 is correct, and an ignored `.sdlc/` is the documented default for a consumer project. This repository tracks `.sdlc/` by choice.
- The review did not cover the number prefix section, the split into two documents, or anything added from v0.3 on.
- The reviewer's findings were not independently rerun, apart from spot checks of the cited line counts, file lists, and `tickets.py` source.
