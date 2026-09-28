<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None. Both steps have a verifier verdict of pass (step-1/verifier-L1.md, step-2/verifier-L1.md).

## PR title
Document optional ticket front matter for handoff.md

## PR body
### Summary
A task's `.sdlc/<task>/handoff.md` can now start with optional YAML front matter that turns it into a ticket. That way a person's decisions (type, status, priority, order) sit next to the brief. Handoffs without front matter work exactly as before. Implements T-0001.

### Changes
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: new section "Ticket front matter (optional)" that documents these fields:
  - `id` (T-NNNN)
  - `title`
  - `type` (feature|bug|chore|spike|idea)
  - `status` (proposed|ready|blocked|done|dropped)
  - `size` (S|M|L|XL)
  - `priority` (P1|P2|P3)
  - `depends` ([T-NNNN, ...])
  - `created` (YYYY-MM-DD)
  - `from` (origin ticket id)

  The section says front matter is purely additive: `run.sh` and `board.py` neither require nor parse it. It also says front matter `status` is a person's decision and never tracks build progress. Build progress stays derived by `/board`.
- `plugins/sdlc-lite/scripts/board.py`: unchanged. It already ignores front matter.

### Verification
- Step 1 (docs), verifier L1 pass. The diff shows all nine fields with their allowed values. It also shows the statements on optionality and on status vs `/board`. `git status` showed no files changed outside the step's scope.
- Step 2 (board.py and checks), verifier L1 pass:
  - `board.py --root .sdlc` exits 0 and lists the `ticket-front-matter` rows. This task's own handoff carries front matter.
  - A scratch `.sdlc/no-front-matter/handoff.md` without front matter renders `| no-front-matter | task | ⏳ not planned | 0 |` and exits 0.
  - `board.py:100-101` uses only the `^## Step` and `^level:` regexes, with no YAML parsing.
  - `scripts/check.sh` exits 0 (`ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added: optional YAML ticket front matter for `.sdlc/<task>/handoff.md` (`id`, `title`, `type`, `status`, `size`, `priority`, `depends`, `created`, `from`), documented in `skills/handoff-format`. Handoffs without it are unchanged, and front matter `status` is separate from the progress `/board` derives.

## Follow-ups
- Optional id and status columns in `scripts/board.py`. T-0001 listed this as optional, and the plan left it out of scope.
- T-0001 still shows `status: proposed`. The user may want to set it to `done` once this merges.
