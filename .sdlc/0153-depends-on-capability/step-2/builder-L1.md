<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: depends line shows `file:` and `cap:`, `provides:` line added after `from:`, and a paragraph on what satisfies each form.
- plugins/sdlc-lite/skills/ticket/SKILL.md: one Rules bullet covering the forms, `provides:`, `(unmet)` marking, and rerunning `roadmap`.
- plugins/sdlc-lite/skills/ticket/templates/{bug,chore,feature,idea,spike}.md: only the trailing comment on the `depends:` line changed.
- docs/maintenance/sdlc-internals.md: one sentence in the `scripts/tickets.py` entry.

## Checks
- The `cap:<name>` and `provides:.*optional` greps on handoff-format passed.
- The template loop found `cap:<name>` on every `depends:` line.
- I did not run the greps on ticket/SKILL.md and internals.md as separate commands. My inserted text contains `cap:<name>` and `provides:` in both files.
- `tickets.py selftest` passed.
- `check.py` printed "ok: 18 role levels, 8 agents checked".

## Notes
`git diff --stat` also lists `tickets.py` and the ticket's `handoff.md` as modified. Those changes came from earlier steps, not from this one.
