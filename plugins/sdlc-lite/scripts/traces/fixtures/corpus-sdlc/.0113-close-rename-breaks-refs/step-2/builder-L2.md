<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: the `tickets.py` close numbered-mode sentence now covers the reference refusal, `--rewrite-refs` and the `--force` escape. This was already in the tree from the superseded attempt; I checked it.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: the numbered-folders bullet covers the refusal and both flags (already present, checked).
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: both `.NNNN-<slug>` lines cover the refusal, `--rewrite-refs` and `--force` (already present, checked).
- `plugins/sdlc-lite/skills/file/SKILL.md`: step 3.1 has the new refusal branch. It asks with AskUserQuestion, options in this order: Rewrite references (recommended), Leave open, Close anyway. An unattended run stops and never rewrites silently (already present, checked).
- `.claude/agents/sdlc-lite-author.md`: the sync line for the dot-prefix rule now names the refusal, `--rewrite-refs` and `--force`, and includes the /file skill (already present, checked).

## Checks
- `grep -qF -- '--rewrite-refs'` on each of the 5 files: all pass.
- `grep -q 'Rewrite references' plugins/sdlc-lite/skills/file/SKILL.md`: pass.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (every selftest PASS, shellcheck ok, plugin validate ok).
- The guard on `git diff --name-only HEAD -- scripts hooks` (only `tickets.py` may differ): pass.
- `python3 plugins/sdlc-lite/scripts/tickets.py close --help | grep -qF -- '--rewrite-refs'`: pass.

## Notes
All of the doc edits were already in the tree from the superseded attempt. I checked each criterion and found no gaps, so this run made no new edits. I did not touch `tickets.py`; it still holds step 1's uncommitted change.
