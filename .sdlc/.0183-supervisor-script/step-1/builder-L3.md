<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/ticket-stages/watcher-design.md`: rewritten to Version 0.2.
  - Header starts `Version 0.2, 2026-10-01.` and no longer says "four blockers open".
  - Sections 1 to 10 are revised. Decisions D1 to D21 are each tagged once, where they are stated.
  - The "Owned session (default)" bullet, the claim that the watcher may call `expire`, and "about 17,600 tokens" are removed.
  - A `## Review findings applied` table has rows 1 to 17, and a note line covers finding 18.
- `docs/validation/idle-host-watcher-design-review.md`: added one `## Applied` paragraph that points to Version 0.2. The findings above it are unchanged.

## Checks
- Each acceptance criterion, run as written with `SDLC_BASE_SHA=5774f077677f9e15cb993a4d07736aa2a54c286b`:
  - Version line: pass
  - Findings table rows 1 to 17: pass
  - Tags (D1) to (D21): pass
  - Required flag and term strings: pass
  - All 11 limits keys: pass
  - The five supervisor.py commands: pass
  - Removed phrases absent: pass
  - Prompt text: pass
  - `## Applied` mentions Version 0.2: pass
- Em dash guard: pass. Scope guard (only the two docs changed outside `.sdlc`, no untracked files): pass.
- After a final header edit I re-ran the version, table-row, string, and removed-phrase criteria, and checked each (D1) to (D21) tag again: all pass.
- `git diff --check -- docs/`: clean.
- Counted each `(Dn)` tag: every tag appears exactly once, after removing a duplicate (D1)/(D21) mention from the header.
- Local links `design.md` and `../validation/idle-host-watcher-design-review.md` both resolve.

## Notes
- In the D19 evidence table, the `--continue` and `codex exec resume --last` rows say plainly that the review did not re-run them. Those rows cite the raw review for that fact, and the watcher does not use either command.
- The D20 validation table adds a "Status fields" row taken from the ticket's selftest list, alongside the rows the handoff required.
- The review doc's Verdict line still says "no finding has been applied yet". I left it as written because it is part of the review's record; the new `## Applied` section records the change.
- Nothing was committed.
