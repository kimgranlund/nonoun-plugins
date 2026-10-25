# Bringing the integration branch into main

Detail for the fanout skill's step 5 (Main).

## Light merge gate

When `.sdlc/config` has a `merge_gate: light` line, light merges reached the integration branch behind the light set only, so the main step runs two commands in place of that settle, after the user picks it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py cover <integration> --gate "<cmd>"...` runs the full gate set at the integration tip and commits a `gate-ledger.jsonl` entry (red prints a `git bisect start <to> <from> --first-parent` line: stop and show it), then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py settle <integration> --require-covered`, which refuses (exit 2) an uncovered tip and otherwise performs the fast-forward and closes the integration tree as above.

## What plain settle does

`settle <integration>` without `--forward` still moves main: when the integration branch is a fast-forward of the current branch it fast-forwards it (no gates run, none needed) and closes the tree; a diverged branch is refused (exit 2) and left whole. Only `--forward` merges main into a diverged branch and runs `--gate` before the fast-forward. When main advanced but lanes are still open into the integration branch, the tree and branch are kept and settle prints `settled: main advanced; integration kept (lanes open: <names>)` and exits 0 (T-0770); exit 1 means nothing merged or a failed close. When host lanes (`worktree-agent-*`) were involved, settle then prints `next: git push origin <main>` if main is ahead of its remote (the next prep refuses an unpushed base) and `git branch -d worktree-agent-<id>` for each landed host branch still present; it runs neither (T-0778). To leave main where it is, do not run `settle` (or run `settle --catch-up`, which never moves main).

## PR merge

PR merge: the plugin ships no PR merge script; a project's own must keep two invariants, and `settle --forward` keeps both for the local path. (a) The branch head contains the base tip before the merge (`git merge-base --is-ancestor origin/main HEAD`, by rebase or merge commit; never a squash of a branch cut before the last merge). (b) The gates ran at that head sha and none is pending (`gh pr checks <n> --watch --fail-fast` is the GitHub form; read-only).
