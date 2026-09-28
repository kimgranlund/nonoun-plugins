## Task goal
Make `/file` close a finished ticketed task: refuse to close while the filer's Warnings are open (unless forced), file each follow-up bullet as a `proposed` idea ticket with `from: <id>`, set the ticket to `done`, regenerate the roadmap, and put the ticket id in the PR title. Publishing still needs the user's approval.

## Step 2: Filer emits bullet follow-ups and a ticket-id PR title; `/file` gains the close step; docs updated
level: L2
### Do
- `plugins/sdlc-lite/agents/filer.md`:
  - PR title: when the task `handoff.md` opens with front matter carrying `id: T-NNNN`, the PR title starts with `T-NNNN: `.
  - Follow-ups: one top-level `- ` bullet per follow-up, one line each, self-contained (each becomes a ticket title and context), or exactly `None`.
  - Warnings: exactly `None` when every step passed.
- `plugins/sdlc-lite/skills/file/SKILL.md`:
  - Add `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*)` to `allowed-tools`.
  - After showing the result, add a close step that runs only if the task handoff has ticket front matter:
    1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc close <slug>`.
    2. On a warnings refusal, show the warnings and ask with AskUserQuestion whether to force-close ("Leave open" recommended first). Rerun with `--force` only on approval.
    3. Report the created follow-up tickets.
  - Keep publishing as the last step, still gated by AskUserQuestion. Follow-ups are now tickets, so offering them as GitHub issues is optional, and only if the user selects that.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add `close <slug> [--force]` to the argument-hint, plus one line saying `/file` normally runs it.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, in the front matter section: one sentence saying `tickets.py close` sets `done` and stamps `from:` on follow-up idea tickets.
- Repo-root `CLAUDE.md`, in the `scripts/tickets.py` bullet under Layout: add `close <slug> [--force]`. If `.claude/agents/sdlc-lite-author.md` lists tickets.py commands, update it to match.
### Acceptance criteria
- `grep -n 'T-NNNN' plugins/sdlc-lite/agents/filer.md` shows the PR-title rule. `grep -n 'None' plugins/sdlc-lite/agents/filer.md` shows the bullet-or-None rule under Follow-ups.
- `grep -n 'tickets.py' plugins/sdlc-lite/skills/file/SKILL.md` shows both the `allowed-tools` entry and the `close` invocation.
- `grep -n -- '--force' plugins/sdlc-lite/skills/file/SKILL.md` appears next to an AskUserQuestion instruction.
- The publish step still says to ask with AskUserQuestion and never publish on your own.
- `grep -n 'close' plugins/sdlc-lite/skills/ticket/SKILL.md plugins/sdlc-lite/skills/handoff-format/SKILL.md CLAUDE.md` matches in all three files.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The only allowed warning is the known validate warning about CLAUDE.md.
- `grep -rn '—' plugins/sdlc-lite/agents/filer.md plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md` finds nothing (no em dashes).

## Plan risks (for reference)
- Only a real LLM run shows whether the filer obeys the bullet format. The step 1 refusal on prose follow-ups makes a non-compliant filer fail loudly rather than drop items, but it can block closes until the filer prompt is followed.
- This repo's own `.sdlc/` has no `roadmap.md`, and it may hold ticket dirs that fail `problems()` (for example, extra `source:` keys are fine, but a bad `depends` is not). Running `close` on the live repo could refuse for reasons unrelated to this change. The acceptance criteria use temp fixtures for that reason.
- mtime ordering of `filer-L*.md` can tie on a fast filesystem. The name tie-break covers it, but selftest case (h) must set mtimes explicitly (`os.utime`).
- The `status:` line is rewritten with a regex. A handoff whose body also has a line starting `status:` is safe only if the substitution is limited to the front matter block.
