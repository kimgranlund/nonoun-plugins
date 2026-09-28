<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- Each of the four files has at least 1 `--ack-warnings`: pass. Evidence: `grep -c -- "--ack-warnings" plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` gives 1, 2, 1 and 1. In a throwaway worktree at HEAD the same command gives 0 for all four, so this check can fail.
- The "Acknowledge with a reason" option is present and the options are in order: pass. Evidence: `grep -n "Acknowledge with a reason"` matches at plugins/sdlc-lite/skills/file/SKILL.md:12, step 3.1. `grep -o` on that file returns `"Leave open"`, then `"Acknowledge with a reason"`, then `"Force close"`. "Leave open" is marked recommended and says stop. The ack option adds `--ack-warnings "<why>"` to every later call (dry run and real close). Force close adds `--force`. At HEAD the grep exits 1, so it can fail.
- The unattended rule is stated: pass. Evidence: `grep -n "never acks or forces\|never ack"` matches at file/SKILL.md:12 ("An unattended run stops on open warnings and never acks or forces."). At HEAD it exits 1, so it can fail.
- No new em dashes: pass. Evidence: `git diff | grep -P "^\+.*\x{2014}"` is empty (rc=1). As a positive control, `printf '+a \xe2\x80\x94 b\n' | grep -P "^\+.*\x{2014}"` matches (rc=0), so the pattern does catch an em dash.
- `check.sh` exits 0, with the CLAUDE.md validate warning as the only allowed warning: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` gives `check rc=0`. `grep -i warn` finds no warning lines. The output ends with `run selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.
- The Do items were each checked against the diff:
  - ticket/SKILL.md `argument-hint` has `[--ack-warnings "<why>"]`.
  - ticket/SKILL.md item 4 covers the behavior, the refusals and dry-run.
  - The CLAUDE.md clause sits next to the `--reason` clause, in the same style.
  - Line 16 of sdlc-lite-author.md has the sync sentence naming tickets.py, /ticket, /file and CLAUDE.md.
  - The doc text matches the step-1 tickets.py code: the refusals for `--force`, `--reason`, empty text and no open warnings are at tickets.py diff lines 45-64, and the `## Closed` section with the quoted warnings is at lines 86-91.

## Out of scope changes
None made by this step. The working tree also changes `plugins/sdlc-lite/scripts/tickets.py`, which is step 1 of this task, and `.sdlc/0057-close-ack-warnings/handoff.md`, which is the task Intent filled in upstream. Neither is step-2 builder work.

## For the next attempt
None
