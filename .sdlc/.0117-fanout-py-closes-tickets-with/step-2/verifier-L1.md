<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `sed -n '/^## 2. Confirm/,/^## 3/p' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q -- --rewrite-refs`: pass. Evidence: it exits 0 in the tree. In a throwaway worktree at HEAD it exits 1, so the check can fail.
- `grep '^argument-hint:' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q -- --rewrite-refs`: pass. Evidence: it exits 0 in the tree and 1 at HEAD. The diff adds `[--rewrite-refs]` to `argument-hint`.
- `grep '^- .scripts/fanout.py.:' CLAUDE.md | grep -q -- --rewrite-refs`: pass. Evidence: it exits 0 in the tree and 1 at HEAD. The diff adds the flag to the usage and adds the sentence the handoff asked for, word for word.
- `grep -n 'fanout' .claude/agents/sdlc-lite-author.md | grep -q -- --rewrite-refs`: pass. Evidence: it exits 0 in the tree and 1 at HEAD. The new line sits right after the "Keep `scripts/fanout.py`... in sync" line.
- Observable: step 2 of SKILL.md presents `--rewrite-refs` as a user-selectable choice, only in numbered mode, and never adds it without the user's pick: pass. Evidence: the new paragraph in `## 2. Confirm` reads "When the plan's `close:` line says `numbered folders`, also ask, as a separate AskUserQuestion choice, whether to add `--rewrite-refs`... Never add it unless the user picks it; step 3 runs with the flag only if they did." The trigger phrase matches the dry-run output at `plugins/sdlc-lite/scripts/fanout.py:313`, which prints `close: tickets.py close <slug> (numbered folders: ...` only when `ctx['numbered']` is set and the flag is absent (lines 309-316). A plain repo prints `close: tickets.py close <slug>`, so the choice is not offered there. This criterion is prose-only, so a document read is the right evidence. The paragraph also covers the `merged, close refused` hint, and step 1 now says the `close:` line shows the mode.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it in the tree and it exited 0. The tail shows the order, fanout, run, hook, and hook live probe selftests as `PASS`, plus `ok: shellcheck` and `ok: plugin validate`.

## Out of scope changes
None from this step. `git diff --stat` also lists two other files:
- `plugins/sdlc-lite/scripts/fanout.py`: this is step 1's work. `.sdlc/0117-fanout-py-closes-tickets-with/step-1/` holds `builder-L2.md` and `verifier-L1.md`, and the dry-run `close:` lines this step documents live there (lines 309-316).
- `.sdlc/0117-fanout-py-closes-tickets-with/handoff.md`: the task handoff's Goal and Constraints were filled in. This is the task setup that step-2's own handoff quotes as its Task goal.

## For the next attempt
None
