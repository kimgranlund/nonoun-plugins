# Evidence: live headless filer emits parseable Follow-ups

## Fresh run (2026-09-24)
- `scripts/run.sh filer L1` on a scratch copy of `.sdlc/ticket-numbered-folders` (id changed to T-0099, own filer output removed). Result kept as `fresh-filer-L1.md`; its run line is appended to `runs.jsonl`. The scratch folder was deleted afterwards.
- Follow-ups: three top-level `- ` bullets, one line each. Warnings: `None`.
- `tickets.py --root <tmp>/root close spike` (status reset to ready in the tmp copy): rc 0, `T-0099 done; 3 follow-up ticket(s): tickets-py-roadmap-does-not, numbered-mode-new-and-close, planner-criteria-that-grep-for`; each new ticket is `type: idea`, `status: proposed`, ids T-0100..T-0102.
- Negative control: same tmp copy with Follow-ups rewritten as one prose sentence: `close` exits 1 with "Follow-ups is prose with no top-level bullet", and writes no ticket.

## Every live filer output in this repo
Parsed with `tickets.py`'s own `section`/`is_none`/`bullets`: all 11 `.sdlc/*/filer-L*.md` (including the fresh one) have `## Warnings` and `## Follow-ups`, and every Follow-ups is either `None` (2) or at least one top-level bullet (9). None is prose. `runs.jsonl` records 10 prior live filer L1 runs (Opus low) on 2026-09-24, all after T-0003 changed the filer prompt to bullet-only.

## Conclusion
The plan risk from T-0003 does not show up in practice: the live filer emits bullet-only Follow-ups or `None`, and `close` consumes them. The prose refusal still guards a regression. No code change needed.
