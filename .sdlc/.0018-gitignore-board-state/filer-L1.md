<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0018: Recommend .gitignore lines for projects that commit the .sdlc/ trail

## PR body
### Summary
`board.py` rewrites `.sdlc/.board-state.json` every time it renders the board. Projects that commit their `.sdlc/` trail get a dirty tree from that file. In gen-ui-system-svelte-lite it made a verifier fail a step whose criterion was "git diff lists only docs". The `handoff-format` skill told projects to ignore all of `.sdlc/`, but it had no lines for projects that commit the trail. This PR adds them.

### Changes
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added a fenced `.gitignore` block right after the existing "Add `.sdlc/` to the project's `.gitignore`" sentence. Each pattern gets a one-line explanation:
  - `.sdlc/.board-state.json`: board cache, rewritten on every `/board` render
  - `.sdlc/**/*.running`: marker for a role run in progress
  - `.sdlc/**/*.log`: raw role transcript
  
  The block ends by saying to keep the results `.md` files and `runs.jsonl` committed. That matches this repo's own `.gitignore`.

This is a docs-only change: no script, agent, or level-table edits.

### Verification
Verifier L1 verdict: pass.
- **Ignore behavior:** the verifier copied the block from the skill file into the `.gitignore` of a fresh scratch repo.
  - `git check-ignore` ignores `.sdlc/.board-state.json`, `.sdlc/t/builder-L1.running` and `.sdlc/t/builder-L1.log`.
  - It does not ignore `.sdlc/t/builder-L1.md`, `.sdlc/t/runs.jsonl` or `.sdlc/t/handoff.md`.
  - Three negative controls show the check can fail: an empty `.gitignore`, the block with the `running` line removed, and an over-broad `.sdlc/` rule.
- **Checks:** `plugins/sdlc-lite/scripts/check.sh` exits 0. Selftests, shellcheck and plugin validate all pass.
- **Scope:** `git diff --stat` lists only the skill file and this ticket's `handoff.md`.
- **Constraints:** no files changed under `scripts/` or `agents/`. The skill file has 0 em dashes. This repo's `.gitignore` is untouched.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Docs: `handoff-format` now recommends `.gitignore` lines for projects that commit the `.sdlc/` trail (`.sdlc/.board-state.json`, `.sdlc/**/*.running`, `.sdlc/**/*.log`), so `/board` renders no longer dirty the tree. (T-0018)

## Follow-ups
- Move the board cache `.sdlc/.board-state.json` out of the working tree so `/board` never dirties a repo, even one that doesn't use the recommended ignore lines (needs changes to board.py and statusline.sh).
