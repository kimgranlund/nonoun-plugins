## Task goal
In a numbered-mode repo, a user who opted in at /fanout's confirm step gets each merged ticket closed on the integration branch even when other files cite its folder: `fanout.py run --rewrite-refs` passes `--rewrite-refs` to `tickets.py close` and the `close <id>` commit carries the rewritten files. Without the flag, behavior is unchanged (`merged, close refused: ...`), and the refusal outcome tells the user the flag exists.

Done when:
- `fanout.py run --rewrite-refs` passes the flag through to `tickets.py close`; `--dry-run` shows it in the plan.
- The `close <id>` commit stages every file the close rewrote, not only files under the ticket root (today it runs `git add -A -- <rel>`, which would leave rewritten files outside `.sdlc/` uncommitted and dirty in the integration worktree).
- `fanout.py selftest` proves, on a numbered-mode throwaway repo with a file outside the ticket root citing `<rel>/NNNN-<slug>`: without the flag the outcome is `merged, close refused` and the ticket stays open; with it the outcome is `merged`, the folder is `.NNNN-<slug>`, the citing file holds the dot path in the `close <id>` commit, and the integration worktree is clean.
- `skills/fanout/SKILL.md` step 2 (Confirm) offers the flag as a choice when the repo is in numbered mode (never added silently); `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` describe the flag; `scripts/check.sh` passes.

## Step 2: Document the flag in /fanout, CLAUDE.md, and the author agent
level: L1
### Do
- **`plugins/sdlc-lite/skills/fanout/SKILL.md`**:
  - Add `[--rewrite-refs]` to `argument-hint`.
  - Step 1 (Dry run): the plan's `close:` line shows whether the repo is in numbered mode.
  - Step 2 (Confirm): when the plan's `close:` line says `numbered folders`, add `--rewrite-refs` as a separate AskUserQuestion choice. The choice text says it rewrites files that cite a closed ticket's folder to its `.NNNN-<slug>` path. It is never added without the user picking it (T-0113 decision). Step 3 then runs with the flag only if the user picked it.
  - Mention that a `merged, close refused` outcome naming `--rewrite-refs` means a citing file blocked the close.
- **`CLAUDE.md`**, in the `scripts/fanout.py` Layout bullet:
  - Add `[--rewrite-refs]` to the usage.
  - Add one sentence: `--rewrite-refs` (opt-in, numbered mode) passes the flag to `tickets.py close`, and the `close <id>` commit stages every file the close rewrote. Without it, a citing file gives `merged, close refused: ...` with a hint naming the flag. The dry run's `close:` line shows the mode.
- **`.claude/agents/sdlc-lite-author.md`**: add the same fact on a line that mentions fanout, for example beside the existing "Keep `scripts/fanout.py`, the /fanout skill ... in sync" line.
### Acceptance criteria
- `sed -n '/^## 2. Confirm/,/^## 3/p' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q -- --rewrite-refs`
- `grep '^argument-hint:' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q -- --rewrite-refs`
- `grep '^- .scripts/fanout.py.:' CLAUDE.md | grep -q -- --rewrite-refs`
- `grep -n 'fanout' .claude/agents/sdlc-lite-author.md | grep -q -- --rewrite-refs`
- Observable: SKILL.md step 2 presents `--rewrite-refs` as a user-selectable choice, only in numbered mode, and never adds it without the user's pick.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
