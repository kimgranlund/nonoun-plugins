# Delivery records

Commits, pull requests, review comments, changelogs, and releases: the record of what shipped. [Core rules](core.md) apply to all of them.

| Type | Shape | Machine-checked |
|---|---|---|
| Commit messages | Consumer repos: Conventional Commits. Subject in the imperative, a body that says why, a footer with issue references and breaking-change markers. This repo: see below. | none |
| PR title and body | Title in the Conventional Commits shape. Body per [pr-body.tmpl](../../assets/templates/pr-body.tmpl): what changed, why (a link, not a repeat), how to verify (commands and expected output), risks and rollback, a filled checklist. Cite the requirement IDs it implements. | none |
| PR review comments | Conventional Comments: a label (suggestion, issue, nitpick, question, praise) with a blocking or non-blocking decoration, so the reader knows the action asked for. | none |
| Changelog / release notes | Keep a Changelog sections (Added, Changed, Deprecated, Removed, Fixed, Security) under a semantic version. | none |
| Release / milestone | Keep a Changelog, aggregated from the merged changes and scoped to one version, with the closed issues listed by ID. | none |

## Rules

1. A record links to the ticket, issue, or requirement it serves. It does not repeat it.
2. "How to verify" gives the command and the output a reader expects to see.
3. A review comment's label states the action asked for. An unlabeled comment is read as non-blocking.
4. A release lists what changed for its users, not the commit log.

## This repository

This repository does not use Conventional Commits. Commit subjects here stay plain imperative sentences, often led by the ticket ID (for example `T-0447: SDLC-native prompt standards`), and each commit made by an agent ends with its `Co-Authored-By` trailer, as the root `AGENTS.md` Completion section states. Conventional Commits is the standard this card sets for consumer repos, not for this one. No check enforces either form.

Since 0.23.0 a ticket's delivery record is the `## Outcome` that `tickets.py close` appends to its handoff (what changed, the `T-NNNN:` commits, each verifier criterion, deviations and follow-ups); the SDLC Lite filer drafts a PR title and body, a changelog entry, and follow-ups only when asked (`/file`, `close --filer`). [pr-body.tmpl](../../assets/templates/pr-body.tmpl) is the shape for a repository without that role. A release's changelog entry is built from the `T-NNNN:` commit subjects since the last tag (`git log --format=%s <last tag>..HEAD`).
