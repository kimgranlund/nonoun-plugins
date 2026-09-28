<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0003: Filer follow-ups become tickets; /file closes the task

## PR body
### Summary
When a task finishes, `/file` now closes its ticket. Follow-ups are no longer just offered as GitHub issues. Each one is filed as a `proposed` idea ticket with `from: <id>`, the parent ticket is set to `done`, and the roadmap is regenerated. The close is refused while the filer's Warnings are open unless `--force` is given, and `/file` asks with AskUserQuestion before it forces. Publishing still needs the user's approval.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py` has a new `close <slug> [--force]` command:
  - It refuses and writes nothing when any of these hold: the handoff or front matter is missing, the tickets are invalid, the ticket is already `done`, there is no `filer-L*.md`, the Warnings or Follow-ups section is missing, the warnings are open (without `--force`), or the follow-ups are prose with no bullets.
  - It uses the newest filer file, picked by mtime with the file name as the tie-break.
  - Every new ticket and the status change are computed before anything is written.
  - The `status: done` substitution touches only the front matter and leaves the rest of the file byte-identical.
  - `cmd_new` gains optional `origin` and `context` through a shared `stamp()` helper.
  - Selftest gains cases (a) to (h), plus a check for an mtime tie.
- `plugins/sdlc-lite/agents/filer.md`:
  - The PR title starts with `T-NNNN: ` when the handoff front matter has an id.
  - Follow-ups are one-line `- ` bullets or exactly `None`.
  - Warnings are exactly `None` when every step passed.
- `plugins/sdlc-lite/skills/file/SKILL.md`:
  - `tickets.py` is added to `allowed-tools`.
  - The new step 3 closes the ticket when the handoff is a ticket. On a warnings refusal it asks with AskUserQuestion, recommending "Leave open" first.
  - Publishing is now step 4 and is still gated by AskUserQuestion. Filing follow-ups as GitHub issues is optional.
- `skills/ticket/SKILL.md`, `skills/handoff-format/SKILL.md` and the repo-root `CLAUDE.md` now document `close`. `.claude/agents/sdlc-lite-author.md` does not list tickets.py commands, so it was left unchanged.

### Verification
- Step 1 (builder L3, verifier L2 Fable medium): **pass**.
  - `tickets.py selftest` printed PASS.
  - A hand fixture with Warnings `None` and two bullets closed as `T-0001 done; 2 follow-up ticket(s): add-retry-to-fetch, document-the-flag`. Both new tickets carry `from: T-0001`, and `check` printed ok.
  - A fixture with Warnings open exited 1, and stderr named `--force`. Nothing was written. With `--force` it closed.
  - Negative control: the verifier disabled the warnings guard in a throwaway worktree, and selftest then failed on case (b).
  - The verifier also saw refusals for a missing handoff, prose follow-ups and a second close.
- Step 2 (builder L2, verifier L1 Sonnet medium): **pass**.
  - Grep checks confirmed each doc rule.
  - `--force` sits on the same line as the AskUserQuestion instruction.
  - The publish step still says "Never publish on your own."
  - The three edited files contain no em dashes.
  - `scripts/check.sh` exited 0 with no warnings.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `/file` now closes ticketed tasks: `tickets.py close <slug> [--force]` files each filer follow-up as a `proposed` idea ticket (`from: <id>`), sets the ticket `done`, and regenerates the roadmap. It refuses while filer Warnings are open unless forced. The filer puts `T-NNNN: ` in PR titles and emits follow-ups as bullets.

## Follow-ups
- Run the filer headless on a real task to confirm it emits bullet-only Follow-ups, since `tickets.py close` refuses prose follow-ups (plan risk, untested with a live model).
- Check this repo's live `.sdlc/` against `tickets.py check` and generate its missing `roadmap.md`, so `close` on real tasks does not refuse for unrelated reasons.
