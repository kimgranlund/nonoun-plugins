# Document reorganization

Status: draft v0.6, not ready to build. Recorded: 2026-09-29. Nothing in this document is implemented.

Three review rounds each found new edge cases in these rules, so they will not be settled on paper. Spike T-0161 builds the read-only inventory and plan and runs them on this repository. Its results decide the rules below. Apply is deferred to a later ticket. The [open findings](#open-findings) list what is known to be unsettled.

This document covers moving existing files to match a repository's layout. Entry files and the default layout are defined in the [onboarding design](design.md). Evidence is in the [first review](../validation/repo-onboarding-design-review.md), the [second review](../validation/repo-onboarding-design-review-2.md), and the [third review](../validation/repo-onboarding-design-review-3.md).

## Decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| Flow | Plan, approve, apply | Moves touch links across the whole repository and may collide with concurrent work. |
| Mechanics | One deterministic script owns inventory, planning, refusals, moves, and the final check | A refusal has to come from something that can be tested with a negative control. |
| Classification | Globs in `docs/layout.md` | No content is read to guess a type, and no role judges a file. |
| User decisions | Recorded by editing `docs/layout.md`, then planning again | The plan is always generated. It is never edited by hand. |
| Who applies | The skill, in the user's session | A role holds a run lock while it works, which would trip the running check. |
| Link rewriting | A new rewriter in the script | The rewriting in `tickets.py` replaces only the ticket folder's own component of a cite. |
| Broken links | Compared with a baseline | A repository can hold links that were already broken before any move. |

## Layout file

The format of `docs/layout.md` is defined in the [onboarding design](design.md#layout-file). Its parser is built in T-0160.

## Inventory

- The link graph covers every tracked Markdown file in the repository.
- A candidate is a tracked document under `docs/` that is not frozen. Entry files, stubs, `README.md`, and `layout.md` are never candidates.
- A candidate is placed when it sits under a listed home or under a topic folder, and no glob of another home matches it.
- A candidate is misplaced when a home's glob matches it and it sits elsewhere. Its destination is that home, keeping the file name.
- A candidate is unplaced when it sits directly in `docs/` and no glob matches it. It has no destination and does not move.

The user decides an unplaced file by adding a glob for it to a home in `docs/layout.md`, or by creating a topic folder and listing it as a home with that glob, and then planning again.

## Frozen material

Always frozen, with no listing needed:

- Everything under `.sdlc/`.
- Every path Git ignores.

Frozen by listing in `docs/layout.md`: anything else, such as benchmark results, generated agent files, vendored folders, and dated evidence.

The script never moves or rewrites a frozen file. The plan lists frozen candidates: tracked Markdown files that are not frozen and have a date in the form `YYYY-MM-DD` in their name or a line starting with `Recorded:` in their first ten lines. Detection only proposes. A candidate becomes frozen when the user lists it.

Frozen material that does not match the layout is not a defect to fix by moving. It stays where it is, and new records follow the layout.

A frozen record may cite a path that has since moved. That is accepted. The record describes the material that was assessed at the time, and rewriting it would break the binding between evidence and the revision it checked.

## Plan

`onboard plan` writes nothing outside the plan ticket. It creates one ticket through `tickets.py new` and writes `plan.json` into that ticket's folder.

`plan.json` fields:

| Field | Content |
| --- | --- |
| `version` | Format version, `1`. |
| `digest` | See below. |
| `moves` | List of `{from, to, rule}`. Paths are relative to the repository root. `rule` is the home line that matched. |
| `rewrites` | List of `{file, line, old, new}` for every link that will change. |
| `unplaced` | List of paths. |
| `frozen_candidates` | List of `{path, reason}`. |
| `baseline_broken` | List of `{file, line, target}` for links that do not resolve before any move. |

The ticket's Context section holds the same content as tables, generated from `plan.json`. When the two disagree, `plan.json` decides.

### Digest

The digest is the SHA-256 of these lines, sorted:

- One line per tracked file outside `.sdlc/`: its path.
- One line per tracked Markdown file that is not frozen: its path and the SHA-256 of its working tree content. This includes `docs/layout.md`.

The digest does not cover `.sdlc/`, so changing the plan ticket's status does not change it. Any edit to `docs/layout.md` or to a document changes it, and the plan has to be generated again.

## Approve

The user reviews the ticket. To change the outcome the user edits `docs/layout.md` and runs `onboard plan` again, which replaces `plan.json` and the tables in the same ticket. The user approves by setting the ticket's status to `ready`.

## Apply

`onboard apply <ticket>` is run by the skill in the user's session and never by a role. It:

1. Runs every refusal below.
2. Moves each file with `git mv`.
3. Rewrites links in citing files that are not frozen, and links inside each moved file.
4. Runs the final check. When it fails, the script restores the working tree to its state before step 2 and exits nonzero.

The user then runs setup again to refresh the managed link lists, reviews the diff, and commits.

### Refusals

The script refuses, writing nothing, when:

- The ticket's status is not `ready`.
- The digest recomputed now differs from the one in `plan.json`.
- A move's destination exists, or collides with another tracked or untracked path after case folding.
- A move's source or a rewrite's file is frozen.
- A run owns a handoff directory. The test is a non-blocking exclusive lock on every `.run.lock` file found under the repository, outside `.git/`. A lock that cannot be taken means a run is active. The existence of the file alone means nothing, because it is never deleted.
- The working tree has uncommitted changes to a file that a move or rewrite touches.

### Final check

- Every link in every tracked Markdown file that is not frozen resolves, except the links listed in `baseline_broken`.
- Every frozen file has the same content hash as before the run.

## Validation required before shipping

Each gate needs a positive case and an observed negative control in the script's selftest, except the end-to-end run.

| Gate | Positive case | Negative control |
| --- | --- | --- |
| Classification | A fixture yields the expected placed, misplaced, and unplaced lists. | A file in `docs/` that no glob matches gets no destination. |
| Frozen | A listed path and an ignored path are absent from the candidates. | A plan edited by hand to move a frozen file is refused. |
| Link rewrite | A move to another folder updates relative links in citing files and inside the moved file. | A link to a different file with the same name is unchanged. |
| Baseline | A fixture with one link that was already broken applies and passes the final check. | A rewrite that is skipped on purpose leaves a new broken link and fails the final check. |
| Digest | An unchanged fixture applies. | A document edited after planning makes apply refuse. A status change on the ticket does not. |
| Running check | A leftover `.run.lock` that nobody holds does not block apply. | A `.run.lock` held by another process makes apply refuse. |
| Collision | A free destination is accepted. | A destination that differs from an existing file only by case is refused. |
| Restore | A passing apply leaves the moves in place. | A failing final check leaves the working tree as it was before apply. |
| End to end | In a throwaway project, plan, approve, and apply complete, and the final check passes. | The same project with the ticket left at `proposed` refuses to apply. |

## Open findings

From the third review. Each is unsettled and is input to the spike.

| # | Finding |
| --- | --- |
| N1 | Planning again cannot go through `tickets.py new`. In numbered mode a second call creates a second ticket, and in plain mode it refuses. A ticket already at `ready` would stay approved for a plan nobody reviewed. The plan ticket needs a defined slug, type, and lookup, and planning has to reset or refuse an approved ticket. |
| N2 | Three inputs are ambiguous: a file that matches globs of two homes, two files with the same name headed for one destination, and a move into a home that is also frozen. |
| N3 | Listing a topic as a home to give it a glob removes it from the topic rules. A glob on a topic needs its own form. |
| N5 | "Link" is undefined. The forms to rewrite and check have to be listed: inline, reference style, autolinks, HTML, anchors, and links in code fences. This repository also cites documents as backticked paths, which a link rewriter does not see. |
| N8 | Restore is unspecified: index state after `git mv`, new folders, files with unrelated uncommitted changes, and failures before the final check. |
| N9 | "Writes nothing outside the plan ticket" is false. `tickets.py new` also rewrites `.sdlc/roadmap.md` and can write `.sdlc/config`, and it refuses when any existing ticket has a problem. No command sets a ticket's status, and a hand edit makes `tickets.py check` report a stale roadmap until it is regenerated. |
| N15 | `plan.json` decides over the tables the user reviews, and the digest covers inputs only, so a hand edit to `plan.json` would be applied. |

## First trial: this repository

This repository does not match the default layout, which makes it a realistic first case:

- Five documents sit directly in `docs/`: `claude-handoff.md`, `claude-response.md`, `codex-role-execution.md`, `plugin-compatibility.md`, and `readiness-recovery-validation.md`.
- `docs/validation/` and `docs/readiness-recovery-validation.md` are dated evidence. They are to be listed as frozen and stay where they are.
- `plugins/sdlc-lite/bench/results/` and `plugins/sdlc-lite/adapters/codex/agents/` are to be listed as frozen.
- `docs/`, `docs/generative-constructs/`, and `docs/repo-onboarding/` use `README.md` as their index and have no `AGENTS.md`.
- `docs/` paths are cited by the root `AGENTS.md`, the root `README.md`, `plugins/sdlc-lite/AGENTS.md`, and both plugins' `HARNESS-NOTES.md`. A move would change those cites.
- Two links already do not resolve on a machine without the sibling UI project: one in `docs/generative-constructs/README.md` and one in `docs/generative-constructs/progressive-context-plugin.md`. They belong in the baseline.

## Unverified assumptions

- `git mv` followed by link rewriting keeps file history readable in `git log --follow`.
- Globs classify enough files to be useful. The share of unplaced files in a real repository is unknown.
- Restoring the working tree after a failed final check is reliable when moves and rewrites are the only changes. The refusal on uncommitted changes is meant to guarantee that.
