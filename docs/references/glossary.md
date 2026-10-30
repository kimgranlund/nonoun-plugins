# Glossary

One term, one part of speech, one definition. An alias in the last column is unapproved: do not write it, and replace it where you find it. The rules for this file are in [the knowledge and operations card](../specs/doc-standards/knowledge-ops.md).

| Term | Part of speech | Definition | Unapproved aliases |
|---|---|---|---|
| close-first | adjective | Of the doctrine that builders, solo, and the factory lean toward closing and merging a step or ticket, not toward layered verification (T-0428). | close-early |
| fanout lane | noun | A git worktree whose tickets run one at a time, in parallel with other fanout lanes, merged into an integration branch behind gates (`/fanout`). | worker, shard |
| handoff | noun | The self-contained file a role reads as its whole brief: a task's or ticket's `handoff.md`, or a step's `step-N/handoff.md`. | brief file, prompt file |
| lane | noun | The route a ticket runs through, one of fix, solo, or chain, as `steps.py lane` prints it. | track, mode, pipeline |
| level | noun | A rung from L1 to L5. A ticket's `size:` is its level; a role's level fixes its model and effort (`adapters/claude/levels.json`). | size class, rank |
| plan doc | noun | One file with the goal, outcome block, measures, authorization, stop rules, and ordered ticket steps with runnable criteria, linted by `plan_check.py plan` and run by `run-plan`. | plan file |
| step | noun | One ordered unit of a plan, with acceptance criteria and a builder level, briefed in `step-N/handoff.md`. | phase |
| status verb | noun | One verb from the closed list built, verified, merged, closed, filed, released, blocked, deferred, stopped, queued, waiting, used in a status line; its tense is the status: past for finished work, present progressive for running work, future with a trigger for next work ([core.md](../specs/doc-standards/core.md)). | status action |
| ticket | noun | One typed unit of work with a `T-NNNN` id, a folder under `.sdlc/`, and front matter per [ticket.json](../assets/schemas/ticket.json). | work card, story |
| verifier | noun | The role that independently checks one built step or ticket against its acceptance criteria and returns pass or fail with evidence; it never edits. | checker, QA |
