<!-- role=builder level=L2 model=opus effort=low -->
## Status
blocked

## Changes
- `CLAUDE.md`: the `scripts/tickets.py` bullet now shows `close <slug> [--force] [--rewrite-refs]`. The numbered-mode close sentence now covers the `git grep` reference refusal, `--rewrite-refs` (and its dry-run `rewrite <file>` lines), the `--force` escape, and that there is no scan outside git.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: the numbered-folders bullet now covers the same refusal, `--rewrite-refs` and `--force`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the `.NNNN-<slug>` layout line (23) and the numbered-mode sentence (47) both mention the refusal, `--rewrite-refs` and `--force`.
- `.claude/agents/sdlc-lite-author.md`: the sync line for the dot-prefix rule now includes the reference refusal, `--rewrite-refs`, the `--force` escape and the /file skill.
- `plugins/sdlc-lite/skills/file/SKILL.md`: step 3.1 has a new branch for the reference refusal. It shows the listed files and asks with AskUserQuestion: "Rewrite references" (recommended, adds `--rewrite-refs` to every later call), then "Leave open" (stop), then "Close anyway" (adds `--force`). An unattended run stops on this refusal and never rewrites or forces, and references are never rewritten silently.

## Checks
- `grep -qF -- '--rewrite-refs'` on each of the 5 files: all found.
- `grep -q 'Rewrite references' plugins/sdlc-lite/skills/file/SKILL.md`: found.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (every selftest PASS, shellcheck ok, plugin validate ok).
- `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/tickets.py`: exit 1. The diff is step 1's uncommitted code change. This step did not touch tickets.py.

## Notes
plan defect: `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/tickets.py` cannot pass. Only merge steps commit, so step 1's tickets.py change is still uncommitted when step 2 runs, and this criterion fails whatever step 2 does. To check that this step changes no code, compare tickets.py against a snapshot taken right after step 1 (for example its hash), not against HEAD.

All the doc work above is done and still uncommitted in the tree. The other six criteria pass.
