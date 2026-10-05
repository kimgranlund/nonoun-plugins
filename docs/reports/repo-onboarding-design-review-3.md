# Repository onboarding design review, third round

Recorded: 2026-09-29. Independent review of the onboarding design at v0.5. The reviewer was a fresh agent with no access to the authoring conversation. It changed no file in this repository.

Subject: commit c7e4921 on branch `repo-onboarding-design`. Documents: `docs/repo-onboarding/design.md`, `reorganization.md`, `layered-context-pattern.md`, `README.md`, and the handoffs of tickets T-0160 to T-0162.

| Ticket | Verdict | New findings |
| --- | --- | --- |
| T-0160 | Ready after fixes | N4, N6, N7, N11, N12 |
| T-0161 | Ready after fixes, specification only | N1, N2, N3, N5, N8, N9, N15 |
| T-0162 | Ready after fixes | N13 |

No blocker. N10 and N14 apply across tickets.

## Status of the second review's findings

| Status | Findings |
| --- | --- |
| Resolved | 1, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17 |
| Partly resolved | 2 (see N1), 3 (bullets other than `- ` were dropped silently), 9 (see N6 and N10), 14 (see N4 and N12), 15 (no level named) |

## New findings

| # | Severity | Finding | Reviewer's evidence | Outcome |
| --- | --- | --- | --- | --- |
| N1 | Major | Planning again cannot go through `tickets.py new`, and approval survives a new plan. | Scratch repositories: numbered mode created a second ticket, plain mode refused with "already exists; nothing written". | Open. Input to spike T-0161. |
| N2 | Major | Ambiguous inputs: two homes matching one file, two files with one destination, a move into a frozen home. | `reorganization.md` inventory and refusals at v0.5, and the default template listing `reports/` as home and frozen. | Open. Input to spike T-0161. |
| N3 | Major | Listing a topic as a home contradicts the topic definition, and homes and loose documents had no route from `docs/AGENTS.md`. | `reorganization.md:54` against `design.md:51`. | Routes fixed in design v0.6. The glob on a topic is open, input to the spike. |
| N4 | Major | Setup needs the layout parser, which belonged to T-0161. | `design.md:51` against the T-0161 handoff. | Fixed in v0.6. The parser and its stop conditions are in T-0160. |
| N5 | Major | "Link" is undefined, and backticked path cites are invisible to a link rewriter. | `docs/claude-handoff.md:9` cites `docs/claude-response.md` in backticks. | Open. Input to spike T-0161. |
| N6 | Major | The live run gate relied on text inside an HTML comment. Not observed by the reviewer. | The reviewer's live probe was declined by its permission system. | Confirmed by the author's probe and fixed in v0.6. The gate reads a visible line with tools disabled. |
| N7 | Major | Check mode had no label for rows 7 and 8, and row 8 would append a block to `docs/layout.md`. | `design.md:97` at v0.5. | Fixed in v0.6. |
| N8 | Major | Restore after a failed apply was unspecified. | `reorganization.md:109` at v0.5, root `AGENTS.md:29`. | Open. Apply is deferred. |
| N9 | Minor | "Writes nothing outside the plan ticket" is false through `tickets.py new`. | `tickets.py:590-600`, observed in scratch repositories. | Open. Input to spike T-0161. |
| N10 | Minor | Several negative controls were second positive cases, and the idempotence control could pass by accident. | Root `AGENTS.md:61`. | Fixed in design v0.6 for T-0160. Open for reorganization. |
| N11 | Minor | "Block text" had no byte boundaries, and the scope of the version number was unstated. | `design.md:90` at v0.5. | Fixed in v0.6. |
| N12 | Minor | T-0160 left the script name, commands, recursion, frozen folders, and behavior outside Git to guesswork. | T-0160 handoff at v0.5. | Fixed in v0.6. |
| N13 | Minor | T-0162 left the format, position, and path base of `### Read first` unstated. The `/fix` skill lints the task folder, which fails. | `steps.py lint .sdlc/fixtask` exits 1 with "no planner-*.md". | Format fixed in the ticket. The `/fix` defect is ticket T-0164. |
| N14 | Minor | The token cost per entry overstated what the probe shows, and the description of `tickets.py` rewriting was imprecise. | Probe report, `tickets.py:323-353`. | Fixed in v0.6. |
| N15 | Minor | A hand edit to `plan.json` would be applied. | `reorganization.md:87, 93-94` at v0.5. | Open. Input to spike T-0161. |

## Checked by the reviewer and found correct

- `run_lifecycle.py:28-35` takes a non-blocking exclusive lock on `.run.lock`, no code removes the file, and `run.sh:188-189` sends every real run of either backend through it.
- A ticket's status is front matter in its `handoff.md`. `tickets.py new` needs a type with a template, a valid slug, a free folder, and a clean ticket set.
- `fix/SKILL.md` step 2 and `chain/SKILL.md` section 5 step 3 write step handoffs by hand. `handoff-format/SKILL.md:32` ends with the instruction to ignore `.sdlc/`.
- A `### Read first` subsection placed after the `level:` line reaches the step handoff through `steps.py split`, and lint passes.
- No conflict with Progressive Context was found.

## Not checked by the reviewer

- Any host loading behavior and all Codex behavior. No live session ran.
- Token costs, `git log --follow`, case-folding collisions, and where a benchmark holds its lock.
- `check.sh` and the selftests.

## Checks by the author

- N6: a live probe on both hosts, recorded in the [loading probe](nested-entry-file-loading.md) under HTML comments. Claude Code removed comment text from `CLAUDE.md` and from an imported `AGENTS.md`. Codex kept it.
- N13: in the reviewer's scratch fixture, `steps.py lint` on the task folder exited 1 and on the step handoff exited 0.
- The other findings were accepted from the reviewer's evidence and not rerun.

## Limits

- The outcomes describe v0.6, which has not been independently reviewed.
- The author ran the N6 probe after the reviewer reported that its own attempt was declined. The probe used the same method and scratch location as the earlier loading probe.
