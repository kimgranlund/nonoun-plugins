<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0037: close a ticket finished by other work with `tickets.py close --reason`

## PR body
### Summary
Sometimes a ticket's work gets done by other tickets. `tickets.py close <slug> --reason "<text>"` now marks that ticket done and records why, with no filer file. Before this, closing needed a `filer-L*.md` even with `--force`, so a ticket like that could not be closed without faking one.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `cmd_close` takes a `reason`. With it, close skips the filer lookup, files no follow-ups, skips the warnings check, sets `status: done`, appends a `## Closed` section (`YYYY-MM-DD: <reason>`) to the handoff, and regenerates the roadmap.
  - Every existing refusal still applies and writes nothing (bad slug, not a ticket, ticket problems, already done, no status line).
  - An empty or whitespace-only reason is refused and writes nothing.
  - `--force` is accepted with `--reason` and has no effect. `--numbered` still persists the config.
  - The normal filer and refusal path now shares the `fm`/`head` setup with the reason path.
  - The usage docstring and argparse help are updated.
  - New selftest cases (k) to (o).
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `argument-hint` and the close item now describe `--reason`.
- `CLAUDE.md`: the `tickets.py` bullet mentions `close <slug> --reason "<text>"`.
- `.claude/agents/sdlc-lite-author.md`: says to keep `--reason` in sync across tickets.py, the /ticket skill and CLAUDE.md.
- `skills/file/SKILL.md` is unchanged. It needed no pointer.

### Verification
- Step 1 (verifier L1, pass):
  - `tickets.py selftest` prints PASS.
  - Negative control: in a copy with the reason branch turned off, selftest fails on (k), (l), (n) and both (o) cases.
  - Case (m) does not fail without the new code: the old code refuses an empty reason too, just with a different error.
  - CLI runs in a temp root:
    - `--reason "done by T-0002"` exits 0, writes `## Closed` / `2026-09-24: done by T-0002`, updates the roadmap, and `check` passes.
    - `--reason "  "` exits 1 and writes nothing.
    - A plain `close` with no filer still refuses and points to `/file`.
- Step 2 (verifier L1, pass):
  - `grep -c -- '--reason'` finds at least one match in each of the three doc files and zero in each at HEAD.
  - `scripts/check.sh` exits 0 with no warnings.
  - `git diff --stat` shows only the expected files.

One deviation from the handoff: the `## Closed` line writes the date once (`YYYY-MM-DD: reason`). The handoff's `<YYYY-MM-DD> (<date>)` wording was ambiguous. The verifier accepted this because the acceptance criteria only require the date and the reason.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added: `tickets.py close <slug> --reason "<text>"` closes a ticket that other work already finished. It needs no filer file, files no follow-ups, and records the reason in a `## Closed` section of the handoff. An empty reason is refused. (T-0037)

## Follow-ups
- tickets.py selftest case (m), empty `--reason`, passes without the new code because it checks only rc 1 and an unchanged tree; also assert the "empty --reason" error text so the case proves the new refusal path.
