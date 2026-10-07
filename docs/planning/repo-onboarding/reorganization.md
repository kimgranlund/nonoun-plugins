---
status: proposed
---
# Document reorganization

Status: v0.7. Recorded: 2026-09-29, updated 2026-10-06. Apply is built in `reorg.py` by T-0233, and the inventory in `inventory.py` by T-0232. Glob classification and `onboard plan` are not built.

Three review rounds each found new edge cases in these rules, so they were settled by building. The read-only inventory and the model-written plan are in [the plan procedure](reorganization-plan-procedure.md); apply, its refusals, and its final check are in `reorg.py`, whose header is the authoritative statement of its rules. The [open findings](#open-findings) record how each finding was settled, and [the apply live run](../../reports/reorg-apply-live-run.md) is the evidence on this repository.

This document covers moving existing files to match a repository's layout. Entry files and the default layout are defined in the [onboarding design](../../specs/repo-onboarding/design.md). Evidence is in the [first review](../../reports/repo-onboarding-design-review.md), the [second review](../../reports/repo-onboarding-design-review-2.md), and the [third review](../../reports/repo-onboarding-design-review-3.md).

## Decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| Flow | Plan, approve, apply | Moves touch links across the whole repository and may collide with concurrent work. |
| Mechanics | Deterministic scripts own the inventory (`inventory.py`) and the refusals, moves, and final check (`reorg.py`); a model session writes the plan | A refusal has to come from something that can be tested with a negative control. |
| Classification | Globs in `docs/layout.md` (not built) | No content is read to guess a type, and no role judges a file. |
| User decisions | Recorded in the plan the user approves, or by editing `docs/layout.md` | The approval is the digest of the dry run, which covers the plan, so an edited plan needs a new dry run. |
| Who applies | The skill, in the user's session | A role holds a run lock while it works, which would trip the running check. |
| Link rewriting | A new rewriter in the script | The rewriting in `tickets.py` replaces only the ticket folder's own component of a cite. |
| Broken links | Compared with a baseline | A repository can hold links that were already broken before any move. |

## Layout file

The format of `docs/layout.md` is defined in the [onboarding design](../../specs/repo-onboarding/design.md#layout-file). Its parser is built in T-0160.

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

The plan is a JSON file kept outside the repository: numbered batches, each with moves (`from`, `to`) and optional link fixes (`file`, `old`, `new`). It is written by a model session from the inventory ([plan procedure](reorganization-plan-procedure.md)) or by hand. There is no plan ticket. The format and its refusals are in `reorg.py`'s header.

### Digest

The digest is the SHA-256 of sorted lines: the path of every tracked file outside `.sdlc/`, the path and content hash of every tracked file outside `.sdlc/` that is not frozen (always including `docs/layout.md`), and the plan itself. A change under `.sdlc/` does not change it. Any edit to a document, to `docs/layout.md`, or to the plan does, and the dry run has to be repeated. The exact lines are in `reorg.py`'s header.

## Approve

`reorg.py apply PLAN --dry-run` runs every refusal except the approval, computes every batch in memory, and prints every move, link fix, and rewrite, the links already broken before the first batch, and the digest. It writes nothing. The user reviews that listing and approves by passing its digest: `reorg.py apply PLAN --approve <digest>`.

## Apply

`reorg.py apply` is run in the user's session and never by a role. It recomputes the listing and digest before any write and refuses unless `--approve` equals the digest. Then, per batch, in order:

1. Moves each file with `git mv`.
2. Rewrites citations in tracked files that are not frozen, including inside each moved file: Markdown links, Markdown mentions of tracked paths, and repo-root path tokens in any file. The link forms are the ones `inventory.py` defines, so inventory and apply share one definition of a link. A batch reads every file as the earlier batches left it.
3. Runs the final check on the real tree.
4. Commits `reorg: <name>`, so `git revert` undoes one batch.

On any failure after the first write, it restores the start: HEAD, every touched path, and its index entry, removes folders it created, leaves unrelated changes and untracked files byte-identical, and exits 1. The rewrite rules, the managed-block hash refresh, and restore are in `reorg.py`'s header.

### Refusals

All run before any write, and also in the dry run: a malformed plan; `docs/layout.md` missing or unparsable; a move source that is not a tracked file, is frozen, or is an entry file or `docs/layout.md`; a destination that is frozen, exists, or collides with another destination or a tracked or untracked path after case folding; a path moved twice; a link fix that matches nothing; a citation the script cannot rewrite; a staged change; uncommitted changes to a file a move or rewrite touches; a `.run.lock` held by a running role; and, outside the dry run, a missing or different `--approve`. Each prints `reorg.py: refused: <reason>`. The full list is in `reorg.py`'s header.

### Final check

- Every link in every tracked Markdown file that is not frozen resolves, except links that were already broken before the first batch.
- No tracked file that is not frozen still holds a repo-root path token of a moved source.
- Every tracked frozen file is unchanged.

A failure prints `reorg.py: final check failed: <file>: <target>` and restores.

## Validation

Each gate has a positive case and an observed negative control in `reorg.py selftest`, which `check.sh` runs.

| Gate | Positive case | Negative control | Selftest gate |
| --- | --- | --- | --- |
| Classification | A fixture yields the expected placed, misplaced, and unplaced lists. | A file in `docs/` that no glob matches gets no destination. | None: glob classification is not built. |
| Frozen | A listed path and an ignored path are left alone. | A plan that moves a frozen file is refused. | `frozen` |
| Link rewrite | A move to another folder updates relative links in citing files and inside the moved file. | A link to a different file with the same name is unchanged. | `rewrite`, `citation`, `batches`, `linkfix` |
| Baseline | A fixture with one link that was already broken applies and passes the final check. | A rewrite that is skipped on purpose leaves a new broken link and fails the final check. | `baseline` |
| Digest | An unchanged fixture applies. | A document or plan edited after the dry run makes apply refuse. A change under `.sdlc/` does not. | `digest`, `approve` |
| Running check | A leftover `.run.lock` that nobody holds does not block apply. | A `.run.lock` held by another process makes apply refuse. | `running` |
| Collision | A free destination is accepted. | A destination that differs from an existing file only by case is refused. | `collision` |
| Restore | A passing apply leaves the moves in place. | A failing final check leaves the working tree as it was before apply. | `restore`, `dirty` |
| Commits and dry run | One commit per batch; the dry run prints the listing. | A single commit, or a dry run that writes, is flagged. | `commit`, `dryrun` |
| Managed blocks | A rewrite inside an onboard managed block refreshes its hash. | A block edited by hand keeps its hash. | `managed` |
| End to end | On a clone of this repository, dry run and apply complete, and the final check passes. | The same plan with no `--approve`, or after an edited document, refuses. | None: [the apply live run](../../reports/reorg-apply-live-run.md). |

## Open findings

From the third review. Each was input to the spike and the apply build; the last column says how it ended.

| # | Finding | Outcome |
| --- | --- | --- |
| N1 | Planning again cannot go through `tickets.py new`. In numbered mode a second call creates a second ticket, and in plain mode it refuses. A ticket already at `ready` would stay approved for a plan nobody reviewed. The plan ticket needs a defined slug, type, and lookup, and planning has to reset or refuse an approved ticket. | Settled: there is no plan ticket. The plan is a file outside the repository and the approval is the dry run's digest, so planning again means a new dry run. |
| N2 | Three inputs are ambiguous: a file that matches globs of two homes, two files with the same name headed for one destination, and a move into a home that is also frozen. | Settled: two plan entries with one destination, and a destination that is frozen, are refusals in `reorg.py`. A file matching two homes cannot arise because glob classification is not built. |
| N3 | Listing a topic as a home to give it a glob removes it from the topic rules. A glob on a topic needs its own form. | Not applicable: glob classification is not built, so homes carry no globs. |
| N5 | "Link" is undefined. The forms to rewrite and check have to be listed: inline, reference style, autolinks, HTML, anchors, and links in code fences. This repository also cites documents as backticked paths, which a link rewriter does not see. | Settled: the link forms are defined once in `inventory.py` and reused by `reorg.py`, and the rewrite rules for links, mentions, and repo-root path tokens (backticked paths included) are in `reorg.py`'s header. A citation in fenced code the script cannot rewrite is refused. |
| N8 | Restore is unspecified: index state after `git mv`, new folders, files with unrelated uncommitted changes, and failures before the final check. | Settled: restore returns HEAD, every touched path and its index entry, removes created folders, and leaves unrelated changes byte-identical; a failure at any point after the first write restores. |
| N9 | "Writes nothing outside the plan ticket" is false. `tickets.py new` also rewrites `.sdlc/roadmap.md` and can write `.sdlc/config`, and it refuses when any existing ticket has a problem. No command sets a ticket's status, and a hand edit makes `tickets.py check` report a stale roadmap until it is regenerated. | Settled: `reorg.py` does not call `tickets.py` and writes nothing under `.sdlc/`; no ticket status is involved, the approval is the dry run's digest. |
| N15 | `plan.json` decides over the tables the user reviews, and the digest covers inputs only, so a hand edit to `plan.json` would be applied. | Settled: the plan is one of the digest's inputs, so a hand edit to it after the dry run refuses. |

## First trial: this repository

This repository does not match the default layout, which makes it a realistic first case:

- Four documents sit directly in `docs/`: `claude-handoff.md`, `claude-response.md`, `codex-role-execution.md`, and `plugin-compatibility.md`. (`readiness-recovery-validation.md` sat there until T-0246 moved it into `docs/reports/`.)
- `docs/reports/` holds dated evidence. It is listed as frozen in `docs/layout.md`. It was `docs/validation/` until T-0246 renamed it to match the schema; earlier tags and published release notes keep the old paths, which is the accepted limit for frozen records.
- `plugins/sdlc-lite/bench/results/` and `plugins/sdlc-lite/adapters/codex/agents/` are listed as frozen in `docs/layout.md`. T-0244 applied the move step by hand with `rename_refs.py`, since this apply step is not built.
- `docs/`, `docs/specs/generative-constructs/`, and `docs/specs/repo-onboarding/` use `README.md` as their index and have no `AGENTS.md`.
- `docs/` paths are cited by the root `AGENTS.md`, the root `README.md`, `plugins/sdlc-lite/AGENTS.md`, and both plugins' `HARNESS-NOTES.md`. A move would change those cites.
- Two links already do not resolve on a machine without the sibling UI project: one in `docs/specs/generative-constructs/README.md` and one in `docs/specs/generative-constructs/progressive-context-plugin.md`. They belong in the baseline.

## Unverified assumptions

- `git mv` followed by link rewriting keeps file history readable in `git log --follow`. Measured once in [the apply live run](../../reports/reorg-apply-live-run.md): Git followed `codex-role-execution.md` (87 lines, 4 rewritten) across the move. A small file with a large share of rewritten lines may not be followed, so this stays unverified in general.
- Globs classify enough files to be useful. The share of unplaced files in a real repository is unknown.
- Restoring the working tree after a failed final check is reliable when moves and rewrites are the only changes. The refusal on uncommitted changes is meant to guarantee that.
