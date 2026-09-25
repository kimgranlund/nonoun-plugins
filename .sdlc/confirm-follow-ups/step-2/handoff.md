## Task goal
Follow-up tickets are proposed to the user, or checked against the task's artifacts, before close files them, so already-answered and duplicate follow-ups never land.

## Step 2: Wire the confirm flow into /file and sync the docs
level: L2
### Do
- `plugins/sdlc-lite/skills/file/SKILL.md`: rewrite step 3 as numbered substeps. Keep the "only if ticket front matter" guard.
  1. Run `tickets.py --root .sdlc close <slug> --dry-run`. On an open-Warnings refusal, keep today's AskUserQuestion force-close flow and add `--force` to every later call only if the user approves. On any other refusal, report stderr and stop.
  2. Read the task's artifacts (plan, builder, and verifier files). Mark for dropping any follow-up they already resolve, with a one-line reason each. Items marked `duplicate of` are skipped by close automatically.
  3. When a person is present, ask with AskUserQuestion (multiSelect) which follow-ups to file. Put the recommended set first, which is the non-duplicate items minus the artifact-answered ones.
  4. Run `close <slug> --skip <unselected indices>`, or plain `close` if nothing is skipped.
  5. Unattended (no one to answer): file the non-duplicate follow-ups minus the artifact-answered ones, and state that choice and the reasons in the report.
  6. Report the tickets created, the duplicates skipped, and the items dropped, with reasons.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add `[--dry-run] [--skip N[,N...]]` to the `argument-hint` `close` form. In item 4, say what dry-run and `--skip` do, that exact duplicates of existing tickets (normalized title or slug) are skipped automatically, and that `--reason` does not combine with either.
- Repo root `CLAUDE.md`, the `scripts/tickets.py` bullet: add `--dry-run` (lists the proposed follow-ups with indices and duplicate marks, writes nothing), `--skip N[,N...]`, and duplicate auto-skip to the `close` description. Mention that `/file` runs the dry run and confirms first.
- `.claude/agents/sdlc-lite-author.md` line 16: extend the sync rule so `--dry-run`/`--skip` and duplicate skipping stay in sync across tickets.py, the /ticket skill, the /file skill, and CLAUDE.md.
- Do not change `agents/filer.md` or the `--reason` behavior.
### Acceptance criteria
- `grep -n -- '--dry-run' plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` matches in all four files.
- `grep -n -- '--skip' plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md` matches in all three files.
- `/file` step 3, read in order, has the dry run first, then dropping artifact-answered items with reasons, then AskUserQuestion with multiSelect and the recommendation first, then close with `--skip`, plus an unattended default that is stated in the report.
- `git diff --stat` shows no change to `plugins/sdlc-lite/agents/filer.md`.
- The new text contains no em dash: `git diff -U0 | grep '^+' | grep -c '—'` prints 0.
- `plugins/sdlc-lite/scripts/check.sh` passes.
