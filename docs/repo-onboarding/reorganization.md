# Document reorganization

Status: proposed v0.4. Recorded: 2026-09-29. Nothing in this document is implemented. Ticket: T-0161, which depends on T-0160.

This document covers moving existing files to match a repository's layout. The layout and the entry files are defined in the [onboarding design](design.md). Evidence is in the [design review](../validation/repo-onboarding-design-review.md).

## Decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| Flow | Read-only scan, then a move plan filed as a ticket, then approval | Moves touch links across the whole repository and may collide with concurrent work. |
| Mechanics | One deterministic script owns inventory, the link graph, refusals, and the final check | A refusal has to come from something that can be tested with a negative control. |
| Classification | Path and name rules in the script | A file the rules cannot place goes to the user. No role judges it. |
| Link rewriting | A new rewriter in the script | The rewriting in `tickets.py` replaces only the last path component of a cite, so it cannot express a move to another directory. |

## Inputs

The script reads two sections of `docs/AGENTS.md`. Each is a list of paths relative to `docs/`, one per line, in backticks.

- `## Layout` lists the homes. The text after the colon on each line names the document types that belong there.
- `## Frozen paths` lists paths the script never moves or rewrites.

A `docs/AGENTS.md` without both sections makes the script stop with a message that names the missing section.

## Steps

1. **Inventory.** List tracked Markdown files and the entry files the onboarding skill manages. Classify each by path and name rules. List a file the rules cannot place as unclassified. Build the link graph. This step writes nothing.
2. **Plan.** Write a move plan as a normal ticket in `.sdlc/`: each source path, its destination, the reason, every link that must change, the frozen candidates, the unclassified files, and a digest of the inventory.
3. **Approve.** The user reviews the ticket, decides each unclassified file and frozen candidate, and marks the ticket ready. Nothing moves before that.
4. **Apply.** The script recomputes the inventory digest and refuses when it differs from the plan's. Moves use `git mv`. Links are rewritten in citing files and inside each moved file.
5. **Check.** Every link in every file that is not frozen resolves. Frozen files are byte-identical to their state before the run.

## Frozen material

The script never moves or rewrites:

- Ticket folders and run records under `.sdlc/`.
- Benchmark results, including stored diffs.
- Generated files: `.sdlc/roadmap.md`, a consumer project's `.codex/agents/`, and in this repository `plugins/sdlc-lite/adapters/codex/agents/`.
- Vendored paths and paths Git ignores.
- Every path listed under `## Frozen paths` in `docs/AGENTS.md`.

The inventory proposes further candidates: a file with a date in its name or a `Recorded:` line near its top. Detection only proposes. A candidate becomes frozen when the user adds it to `docs/AGENTS.md`.

Frozen material that does not match the layout is not a defect to fix by moving. It stays where it is, and new records follow the layout.

A frozen record may cite a path that has since moved. That is accepted. The record describes the material that was assessed at the time, and rewriting it would break the binding between evidence and the revision it checked.

## Refusals

The script refuses, writing nothing, when:

- A destination collides with an existing path after case folding. macOS and Windows would overwrite silently.
- The plan would leave a broken link in any file that is not frozen.
- The plan moves or rewrites a frozen path.
- A `.run.lock` or `*.running` marker exists under `.sdlc/`, which means a role is running.
- The inventory digest differs from the one in the plan.

## Validation required before shipping

Each gate needs a positive case and an observed negative control.

| Gate | Positive case | Negative control |
| --- | --- | --- |
| Script selftest | The selftest passes. | Each refusal above is observed in the selftest. |
| Inventory | A fixture repository yields the expected classification and link graph. | A fixture with an unplaceable file lists it as unclassified and does not guess a home. |
| Link rewrite | A move to another directory updates relative, root-relative, and in-file links. | A link to a different file with the same name is left unchanged. |
| Frozen | Frozen files are byte-identical after a run. | A plan that cites a frozen path as a source is refused. |
| Staleness | A plan applies when the inventory is unchanged. | A file added after planning makes apply refuse. |
| End to end | In a throwaway project, the plan ticket passes verification and no link is broken. | The same run with one broken link seeded fails the final check. |

## First trial: this repository

This repository does not match the default layout, which makes it a realistic first case:

- Five documents sit loose in `docs/`: `claude-handoff.md`, `claude-response.md`, `codex-role-execution.md`, `plugin-compatibility.md`, and `readiness-recovery-validation.md`.
- `docs/validation/` and `docs/readiness-recovery-validation.md` are dated evidence. They are frozen, so they stay where they are and `docs/AGENTS.md` lists them.
- `docs/`, `docs/generative-constructs/`, and `docs/repo-onboarding/` use `README.md` as their index and have no `AGENTS.md`.
- `docs/` paths are cited by the root `AGENTS.md`, the root `README.md`, `plugins/sdlc-lite/AGENTS.md`, and both plugins' `HARNESS-NOTES.md`. A move would change those cites.

## Unverified assumptions

- `git mv` followed by link rewriting keeps file history readable in `git log --follow`. Not tested.
- Path and name rules classify enough files to be useful. The share of unclassified files in a real repository is unknown.
