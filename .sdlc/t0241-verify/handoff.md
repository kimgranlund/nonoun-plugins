## Goal
Independently verify T-0241: `git diff main~0..HEAD` on branch schema (one commit) changes the layout parser in plugins/sdlc-lite/scripts/onboard.py to read `## Kinds` (11-column registry table), `## Decide` and `## Legacy`. Spec: .sdlc/0241-docs-schema-parser/handoff.md and docs/docs-schema/design.md sections "Overriding: docs/layout.md" and "Registry row".

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` passes and the new gates (layout-sections, layout-other-tree) have a positive case and each defective variant is rejected. Show one extra negative control of your own: temporarily break a rule in the parser (revert after) and see a gate fail.
2. Every error the spec lists raises LayoutError naming file and line: unknown kind, a line outside the forms, a kind row for a home missing from `## Homes`, a duplicate heading. Try 3 inputs of your own in a throwaway script, including a table row with an escaped `\|` and a Kinds table inside a code fence (must be ignored).
3. Files without the new sections parse as before: `git stash`-free check by running the OLD parser (`git show main:plugins/sdlc-lite/scripts/onboard.py`) and the new one on 3 layouts and comparing homes and frozen. `onboard.py check` output on this repo is byte-identical to main's (compare, e.g. via a throwaway worktree at main).
4. `bash plugins/sdlc-lite/scripts/check.sh` passes; `git diff --check main`; no em dashes in added lines.

## Constraints
Read-only except throwaway experiments you revert. No push or publish.
