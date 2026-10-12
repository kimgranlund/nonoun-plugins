<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0489: fanout.py settle --forward merges main into a diverged integration branch, runs the cover gate, then fast-forwards

## PR body
### Summary
`fanout.py settle <integration> --forward --gate CMD...` now handles an integration branch that has diverged from main. Under the existing `merge.lock`, it does these steps:
- Merges main into the integration branch.
- Regenerates the roadmap and router files.
- Union-merges `notes.md`.
- Runs the T-0481 cover gate at the new tip.
- Fast-forwards main only when the gate is green.

A plain `settle` still refuses a diverged branch. `--forward` without `--gate` exits 2, so a fast-forward is never ungated.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - `cmd_cover`'s locked body became the lock-free `cover_at(...)`. `cmd_cover` still takes `MergeLock` and keeps its output and exit codes.
  - New `settle_forward(a, cwd, head)` does the merge. It resolves conflicts in the generated set: `notes.md` by union, roadmap and router files with `--ours`. It regenerates with `tickets.py roadmap` and commits `settle --forward: <head> <sha7> into <integration>`. It then runs `cover_at` inside one `merge.lock`.
  - A conflict outside the generated set aborts the merge, exits 2 naming the files, and leaves no `MERGE_HEAD`.
  - New settle flags: `--forward`, `--gate`, `--lanes-dir`, `--gate-need`, `--no-gate-lock`, `--allow-empty-gate`. `USAGE` is updated.
  - New selftest case after case 28.
- `docs/references/sdlc-internals.md`: one paragraph on `settle --forward`.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: one sentence in section 5 pointing to `settle --forward --gate` instead of a hand merge.

Where the handoff and the design doc (`docs/planning/merge-ops-and-queue.md`) differ, the handoff won:
- It reuses `merge.lock`, so there is no new `settle.lock`.
- No `land.jsonl` line is written.

### Verification
The verifier L2 returned pass on all 10 criteria.
- **Red controls:**
  - The `settle --help` flag grep, the `cover_at` def grep and the `T-0489` grep were recorded red before the edit, then green.
  - The two doc-grep criteria have no recorded pre-edit control. The builder checked them at base with `git show 5c42e976:<path> | grep -qF ...` (rc 1 each), and the diff shows pure additions.
- **Selftest red:** with only the T-0489 case added and no implementation, `fanout.py selftest` exited 1. Every failing line carried a T-0489 label (`unrecognized arguments: --forward`).
- **Negative control:** a mutated copy with the regeneration call changed from `'roadmap'` to `'--help'` made `fanout.py selftest` exit 1. It listed two T-0489 labels: the roadmap on main lacking T-0001 done and T-0003 proposed, and `tickets.py check` failing with `roadmap.md: stale or missing`.
- **Selftest negative controls:** the case also asserts these:
  - A `README.md` conflict exits 2 with a clean `git status --porcelain`.
  - Plain `settle` on the diverged branch exits 2.
  - A red gate leaves main unmoved.
  - `--forward` without `--gate` exits 2.
- **Guards:**
  - Scope: only the three allowed files changed.
  - `fanout.py selftest` printed PASS.
  - `check.py` and `tickets.py selftest` exited 0.
  - `git diff --check` exited 0.
- The full `check.sh` was not run here. It belongs to this wave's `fanout.py land` gates.

Two places differ from the handoff's literal wording. Both were chosen in the plan and the verifier accepted them.
- **Ledger tip:** cover commits the ledger after the gates, so main cannot equal the pre-ledger tip. The selftest asserts that main equals the archived tip, the newest entry's `to` is `main^1`, and only the ledger changed since `to`. This is the rule `require_covered` already uses.
- **`check.sh` header comment:** it is refused like any non-generated path, not auto-resolved. Nothing generates it, and the design calls it hand-edited residue.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `fanout.py settle <integration> --forward --gate CMD...` merges main into a diverged integration branch under the merge lock, regenerates the roadmap and router files, union-merges `notes.md`, runs the cover gate, and fast-forwards main only on green. A conflict outside the generated files exits 2 and leaves everything unchanged. (T-0489)

## Follow-ups
- decide: The handoff lists the `check.sh` header comment among auto-resolved generated files, but the build refuses it as a hand-edited conflict. Decide whether to add an auto-resolve rule or keep the refusal.
- note: `--forward` writes no `land.jsonl` line, so `report.py` does not see forward settles. Build one only if `report.py` needs to show them.
- note: Cross-wave settle ordering (design section 2) is not built. Concurrent settles into different integration branches serialize only through `merge.lock`.
- note: The T-0489 selftest fixture has no `notes.md`, so the notes-union path is not exercised. The verifier accepted this because the regeneration alone bites.
- note: `fanout.py selftest` takes about 240 to 250 s here against an 800 s guard timeout. A heavily loaded host could approach it.
