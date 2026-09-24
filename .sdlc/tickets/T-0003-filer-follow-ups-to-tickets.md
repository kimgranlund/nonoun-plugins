---
id: T-0003
title: "Filer follow-ups become tickets; /file closes the task"
type: feature
status: proposed
size: M
priority: P2
depends: [T-0001, T-0002]
created: 2026-09-24
source: setup-sdlc-lite-generative-ui session, from gen-ui-system-svelte-lite setup
---

## Goal
Finishing a task records its follow-ups in the task system and marks the task done, instead of only offering to publish them as GitHub issues.

## Intent
- Do: in /file, after the filer runs, a close step that refuses when the filer's Warnings section is not "None" (unless forced), files each follow-up bullet as a `proposed` idea ticket with `from: <id>`, sets the ticket `done`, and regenerates the roadmap. Put the ticket id in the PR title.
- Non-goals: publishing anything without the user's approval.
- Done when: a fixture task with follow-ups closes into idea tickets, a task with warnings is refused, and check.sh passes.

## Context
- Today `agents/filer.md` returns "Follow-ups" as prose and `skills/file` step 3 only offers outward publishing.
- Reference implementation: `tickets.py close <slug>` in `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/scripts/tickets.py`.

## Constraints
Publishing still requires AskUserQuestion approval.
