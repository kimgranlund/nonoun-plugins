# Repository onboarding design review, second round

Recorded: 2026-09-29. Independent review of the onboarding design at v0.4. The reviewer was a fresh agent with no access to the authoring conversation. It changed no file in this repository.

Subject: commit fbb32d1 on branch `repo-onboarding-design`. Documents: `docs/specs/repo-onboarding/design.md`, `reorganization.md`, `layered-context-pattern.md`, `README.md`, and the handoffs of tickets T-0160 to T-0163.

| Ticket | Verdict |
| --- | --- |
| T-0160 | Ready after fixes |
| T-0161 | Needs rework of the specification, not the architecture |
| T-0162 | Ready after fixes |

## Findings

| # | Severity | Finding | Reviewer's evidence | Outcome in v0.5 |
| --- | --- | --- | --- | --- |
| 1 | Blocker | The existence of `.run.lock` does not mean a role is running, so apply would refuse forever. | `run_lifecycle.py:29` opens the file and holds a lock, and nothing deletes it. `run_lifecycle.py recover` on a scratch folder left a zero-byte `.run.lock`. | The running check tries a non-blocking lock. |
| 2 | Blocker | Approval changed the inputs the digest guards, the digest scope was undefined, and the plan had no machine-readable format. | `reorganization.md` steps 2 to 4 at v0.4. | `plan.json` is defined, the digest scope is defined and excludes `.sdlc/`, and decisions are made by editing the layout and planning again. |
| 3 | Major | The layout format could not be parsed into behavior, and frozen paths could not name anything outside `docs/`. | The `<topic>/` placeholder in the template, and `plugins/sdlc-lite/bench/results/` citing `docs/` paths. | A grammar is defined, frozen globs are relative to the repository root, and every unparsed list line stops the script. |
| 4 | Major | "Every link resolves" already fails in this repository. | Two links into a sibling repository that is absent: `docs/specs/generative-constructs/README.md:19` and `progressive-context-plugin.md:76`. | The final check compares with a baseline. |
| 5 | Major | Upsert rows overlapped, so a stale block with every target was never repaired. | `design.md` upsert table at v0.4. | The rows are ordered and the first match applies. |
| 6 | Major | Blocks without targets were never written to an existing file, and an existing `docs/AGENTS.md` never gained the layout sections. | The `.sdlc/AGENTS.md` and `docs/AGENTS.md` templates at v0.4. | Target detection applies to the import only. The layout moved to `docs/layout.md`, which setup creates when missing. |
| 7 | Major | An ignored `.sdlc/` is the documented default, so the root link to `.sdlc/AGENTS.md` breaks in a fresh clone. | `handoff-format/SKILL.md:32`. | `.sdlc/AGENTS.md` is dropped. The guidance is in the root managed block. |
| 8 | Major | T-0162 did not say whether an ancestor entry counts, and it left out the verifier, handwritten step handoffs, and the regression checks. | `fix/SKILL.md:19`, `chain/SKILL.md:53`. | The ticket names the nearest entry above each changed file and adds those items. |
| 9 | Major | Three validation gates tested other components. | `check-packaging.py:48-56` checks links only in Progressive Context. | Existing checks are listed apart. Every new gate tests the skill's own output. |
| 10 | Minor | The token cost per entry was stated differently in two documents. | `design.md:67` against the probe report. | Both documents now give the probe figures. |
| 11 | Minor | "Loads only through a `CLAUDE.md` beside it" contradicted the probe's bridge arm. | Probe report, bridge arm. | Reworded to an import in a `CLAUDE.md` that is itself loaded. |
| 12 | Minor | Check mode compared a version number only and had no way to see a hand edit. | `codex_roles.py:214-224`. | The start marker carries a content hash. |
| 13 | Minor | Uncovered cases: `@./AGENTS.md`, code fences, malformed markers, two blocks, a newer version. | `design.md` target detection at v0.4. | Each is a defined row or definition. |
| 14 | Minor | The Progressive Context edit was in no ticket, and several setup details were undefined. | `design.md` at v0.4. | The edit is in T-0160. Topic, document, and script ownership are defined. |
| 15 | Minor | T-0160 and T-0162 need a Codex live run and did not mention T-0163. | `models.json`. | Both tickets state which levels can run. |
| 16 | Minor | The template said result formats are owned by `handoff-format`. | Root `AGENTS.md` names `plugins/sdlc-lite/agents/*.md` as the source of output contracts. | The line is reworded. |
| 17 | Minor | No refusal detected a benchmark, and a role applying the plan would trip the running check itself. | T-0161 handoff at v0.4. | The running check covers every `.run.lock` in the repository, and apply is never run by a role. |

## Checked by the reviewer and found correct

- The T-0162 route works. `parse_steps` copies a step block up to the next `## ` line (`steps.py:208-222`). In a scratch task a `### Read first` subsection reached the step handoff unchanged, and `steps.py lint` passed.
- The first trial facts: five loose documents, `README.md` indexes, no `AGENTS.md` under `docs/`, and the citing files.
- `codex_roles.py install --check` exists and returns before any write.
- `.sdlc/roadmap.md` is generated and lists the four tickets with matching dependencies.
- `tickets.py` rewriting changes one path component only.

## Not checked by the reviewer

- Any host loading behavior or token cost. No live host session was run.
- `tickets.py close` against an ignored `.sdlc/`.
- Whether Claude Code removes a duplicate import. Fanout worktrees. Where benchmarks place markers.
- `check.sh`, `check.py`, and the selftests, apart from the commands named above.

## Spot checks by the author

- Finding 7: `handoff-format/SKILL.md` line 32 does end with the instruction to ignore `.sdlc/`. The first review's record was corrected in 01c6560.
- Finding 1: `run_lifecycle.py` takes a non-blocking exclusive lock on `.run.lock` and contains no call that removes the file.
- Finding 9: `check-packaging.py` lines 48 to 56 match the reviewer's description.
- The other findings were accepted from the reviewer's evidence and not rerun.

## Limits

- The outcomes in the findings table describe v0.5, which has not been independently reviewed.
- The reviewer left throwaway files in the session scratchpad. They are not part of this repository.
