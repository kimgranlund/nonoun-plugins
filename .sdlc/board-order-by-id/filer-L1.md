<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0017: Add --sort {recent,id,name} to the board

## PR body
### Summary
`/board` could only list tasks by recency (`st_mtime`). With numbered ticket folders, the board and the roadmap came out in different orders. This PR adds a `--sort` flag, so the board can list tasks by ticket id or by folder name. The default stays `recent`, so `/chain` and the statusline see no change.

### Changes
- `plugins/sdlc-lite/scripts/board.py`:
  - Adds `--sort {recent,id,name}`, default `recent`.
  - Adds a new `sort_tasks()` helper with three modes:
    - `recent`: keeps the existing mtime order.
    - `id`: orders ticketed tasks by the numeric part of `T-NNNN`, then tasks with no ticket by folder name. A front matter id with no `T-<digits>` part counts as no ticket.
    - `name`: orders by folder name.
  - `main()` now sorts first and then applies the `belongs_on_board` filter, so filtering never changes the order.
  - Adds `os` to the imports.
  - Adds selftest case 6.
- `plugins/sdlc-lite/skills/board/SKILL.md`: adds `[--sort {recent,id,name}]` to `argument-hint`. Step 2 passes `--sort <mode>` through when given.

### Verification
The verifier (L1) passed the step on every criterion:
- 🟢 `board.py selftest` passes, and the new case 6 covers all three modes. Case 6 checks:
  - `--sort id` lists T-0002 before T-0003, then the untracked tasks alphabetically.
  - `--sort name` lists folders in strict alphabetical order.
  - With no flag the order is mtime, and it matches `--sort recent` exactly.
- 🟢 Manual fixtures:
  - The T-0003 dir was older than the T-0002 dir. The default order showed T-0003 first and `--sort id` showed T-0002 first, so the two modes really differ.
  - `--sort name` listed `alpha`, `bravo`, `charlie` even though their mtimes were out of order.
- 🟢 Negative control, run by both the builder and the verifier: with the id sort key inverted, the selftest failed. With the key restored, it passed.
- 🟢 `plugins/sdlc-lite/scripts/check.sh`: every section ok (role levels, selftest, tickets and board selftests, shellcheck, plugin validate).
- 🟢 Scope: the diff touches only `board.py` and `skills/board/SKILL.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `/board` takes `--sort {recent,id,name}`, so it can list tasks by ticket id (matching the roadmap) or by folder name. The default stays `recent` (by modification time). (T-0017)

## Follow-ups
- Decide whether `/board` should default to `--sort id` when tasks have tickets (T-0017 kept `recent` to leave /chain and the statusline unchanged)
