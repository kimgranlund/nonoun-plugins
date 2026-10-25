---
id: T-0782
title: "block-disk-scan does not refuse a heredoc body"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`hooks/block-disk-scan.sh` judges only the shell command a role runs, not the body of a heredoc fed to it on stdin, so a `python3 - <<'EOF' ... EOF` file edit whose text mentions a search command is not refused; a real `find /` in the command line still is.

## Intent
- Do: reproduce with the two refused commands (below), find which pattern matched inside the heredoc body, and strip heredoc bodies (`<<'X' ... X`, `<<X ... X`, `<<-X`) before matching. Add the negative and positive cases to `plugins/sdlc-lite/scripts/hook-selftest.sh`.
- Non-goals: other hooks.
- Done when: the criteria pass.

## Context
T-0769 solo (2026-10-25) was refused twice by block-disk-scan (0.35.0 copy): `Blocked for sdlc role 'solo': searching the whole filesystem or a home folder (find /, ...)` for `cd <lane> && python3 - <<'EOF'` edits of `plugins/sdlc-lite/scripts/lanes.py`; the solo fell back to the Edit tool. The full refused commands are the Bash tool_use inputs whose tool_result names block-disk-scan in /Users/kimgranlund/.claude/projects/-Users-kimgranlund-Projects-nonoun-sdlc-lite/66c988ad-c130-4e4f-9955-2f1db3b3b83c/subagents/agent-asolo-0769-ea5cf465dde74b1d.jsonl (read-only).

## Acceptance criteria
1. A `hook-selftest.sh` case: a heredoc edit whose body holds the matched text is allowed, and `find / -name x` on the command line is still refused; with the change reverted the heredoc case fails (state the FAIL line).
2. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`hooks/block-disk-scan.sh` now cuts each heredoc marker and body (`<<X`, `<<'X'`, `<<"X"`, `<<-X`, closed by its terminator line) before matching, so a `python3 - <<'EOF'` edit whose text mentions a search command passes. A body with no terminator, a leftover shell or evaluator word (`bash <<EOF`, `cat <<EOF | sh`), and a search on the command line itself are judged whole and still blocked. Cause: any `<<` made the analyzer fail closed to the raw-text loose match, which read the body.
- hook-selftest.sh: new T-0782 allow cases (4 heredoc shapes) and block cases (5). Negative control: with the hook reverted to HEAD the first allow case fails, FAIL line ends `...git status': exit 2, want 0`.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exit 0, `python3 plugins/sdlc-lite/scripts/check.py` exit 0, `python3 scripts/check-packaging.py` exit 0, `git diff --check 8b232fc80d6bdb134e2dc476b830dc650bbd1159` exit 0.
- Not covered: two heredocs on one line leave the second marker, which fails closed as before.
