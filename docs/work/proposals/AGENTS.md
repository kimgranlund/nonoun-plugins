# Proposals

This folder holds candidate changes that `proposals.py scan` mines from past runs: `runs.jsonl` files, builder and verifier results, and `docs/work/NOTES.md`. Nothing is applied automatically. `accept` needs a valid eval in `docs/work/evals/`, and `promote` only files an idea ticket through `tickets.py new idea`. The script never edits a plugin file, runs an experiment, or changes a model default. Run every command from the repository root; `P` below means `python3 plugins/sdlc-lite/scripts/proposals.py`.

## File format

Each proposal is one folder `<kind>-<8 hex>/proposal.md`, where the hex is the first 8 characters of the sha256 of its `pattern` value; a clash on an existing folder appends `-2`, `-3`. The front matter fields, in this order:

- `id`: `P-NNNN`, the next number above every proposal in the folder.
- `title`: one line.
- `status`: `candidate`, `accepted`, `rejected`, or `promoted`.
- `pattern`: `<kind> <subject>` (`plan-defect` has no subject). scan matches known proposals by this value.
- `occurrences`: the number of evidence lines.
- `created`: `YYYY-MM-DD`, the scan that filed it.
- `eval`: empty until `accept` stamps the repo-relative eval path.

The stamps, each written only by its move: `accepted: YYYY-MM-DD`; `rejected: YYYY-MM-DD` and `reason: <text>`; `promoted: YYYY-MM-DD` and `ticket: T-NNNN`.

The body has two sections. `## Evidence` holds one line per occurrence, `- <repo-relative path>:<line> (<where>) "<quote>"`, where `<where>` is the heading above the line or `run` for a `runs.jsonl` line. `## Proposed change` holds one line saying what to examine, never a patch. scan rewrites the evidence and `occurrences` of a known pattern and keeps everything else.

Example, `replan-1a2b3c4d/proposal.md`:

```
---
id: P-0001
title: Repeated planner runs in docs/work/.0183-supervisor-script
status: candidate
pattern: replan docs/work/.0183-supervisor-script
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- docs/work/.0183-supervisor-script/runs.jsonl:1 (run) "role=planner level=L3 file=planner-L3.md"
- docs/work/.0183-supervisor-script/runs.jsonl:9 (run) "role=planner level=L3 file=planner-L3-2.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

## Patterns

| Kind | Source | Subject | One occurrence | Quote |
|---|---|---|---|---|
| `verifier-fail` | `verifier-L<n>*.md` | its dir | a result whose `## Verdict` is `fail` | the verdict |
| `replan` | `runs.jsonl` | its dir | a line with role `planner` | `role=... level=... file=...` |
| `builder-bump` | `runs.jsonl` | its dir | each distinct builder level | `role=... level=... file=...` |
| `next-attempt` | verifier results | the lowercased `## For the next attempt` text | that text in a different dir (`None` skipped) | the text |
| `plan-defect` | failing verifiers and blocked builders | none | a line starting `plan defect:` | the line |
| `follow-up` | `docs/work/NOTES.md` | `<tag> <lowercased text>` | a `- fix-now:` or `- decide:` line | the line |

A pattern with two or more occurrences becomes a candidate; one occurrence files nothing. A subject dir is repo-relative, with the leading dot dropped from a closed ticket folder `.NNNN-<slug>`, so a ticket's pattern survives the close rename. scan skips the top-level `proposals/`, `messages/`, `runtime/`, and `dogfood/` folders and the `--proposals` dir, and follows no symlink.

## Statuses

`candidate`, `accepted`, `rejected`, `promoted`. The three allowed moves:

- `candidate` to `accepted` by `accept`: stamps `eval` and `accepted`.
- `candidate` to `rejected` by `reject`: stamps `rejected` and `reason`.
- `accepted` to `promoted` by `promote`: stamps `promoted` and `ticket`.

No move goes backward, and any other move is refused.

## Procedures

- Scan: `python3 plugins/sdlc-lite/scripts/proposals.py scan`. Add `--proposals <dir>` before `scan` for a look that writes elsewhere. It prints one line per new or updated proposal and ends `proposals scan: <n> new, <n> updated, <n> unchanged`.
- List: `python3 plugins/sdlc-lite/scripts/proposals.py list` prints id, status, occurrences, folder, and title per proposal.
- Show: `python3 plugins/sdlc-lite/scripts/proposals.py show <id>`.
- Accept: add the eval first by following `docs/work/evals/AGENTS.md`, then `python3 plugins/sdlc-lite/scripts/proposals.py accept <id> --eval docs/work/evals/<file>`. It refuses with no eval, a missing file, a file outside `docs/work/evals/`, or an invalid eval.
- Reject: `python3 plugins/sdlc-lite/scripts/proposals.py reject <id> --reason TEXT`.
- Promote: `python3 plugins/sdlc-lite/scripts/proposals.py promote <id>` files an idea ticket through `tickets.py new idea` and records its id.
- Never edit a proposal's front matter by hand.

Exit codes: 0 ok, 1 refusal (`proposals.py: <reason>` on stderr), 2 usage error.

## Limits

- Quotes collapse whitespace, write an em dash as a hyphen, and are cut at 160 characters.
- `next-attempt` reads verifier results only. Follow-ups come from `notes.md` only, and `fix-now:` items rarely reach it, because they are finished before close.
- Ids are not unique across parallel worktrees: scan refuses a duplicate id until it is renumbered.
- A folder moved other than by the close rename starts a new pattern. scan never deletes a proposal.
- A proposal citing an open ticket folder makes `tickets.py close` refuse (its `git grep` reference check) until `--rewrite-refs` or `--force`.
