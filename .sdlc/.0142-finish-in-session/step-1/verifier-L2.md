<!-- role=verifier level=L2 model=sonnet effort=high -->
Clean. All criteria pass, the guard is proven to bite via an independent mutation, and the only out-of-scope diff (task-level handoff.md) predates the build by evidence of mtime ordering.

## Verdict
pass

## Criteria
- `close --help` mentions `--ticket`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py close --help | grep -q -- '--ticket'` → rc 0.
- Two `decide:` + one `note:` follow-up, `--ticket 1`: files item 1, item 2 stays a folder-less notes.md entry, note text in notes.md: pass. Evidence: ran the exact criterion span, rc 0 (`test -d add-retry-to-fetch`, `! test -d split-the-runner`, both greps on notes.md succeeded).
- Plain close (decide + fix-now + untagged) files zero tickets, all three land in notes.md, status done: pass. Evidence: ran the exact span, rc 0.
- `--ticket 2` on a `note:` item refuses citing "note", writes no notes.md, status stays proposed: pass. Evidence: ran the exact span, rc 0; stderr observed: `alpha: --ticket 2 is a note: item; only a decide: item can become a ticket; nothing written`.
- `--dry-run --ticket 2`: item 1 marked `note`, item 2 marked `ticket`, last line `expect ...`: pass. Evidence: ran the exact span, rc 0; output showed `1. decide: Add retry to fetch note` / `2. decide: Split the runner [split-the-runner] ticket` / `expect 7ead2872f741`.
- Numbered mode: `--ticket 1` on untagged item files `0002-untagged-legacy-item`, alpha archives to `.0001-alpha`, `note:` item in notes.md, `check` passes: pass. Evidence: ran the exact span, rc 0.
- `--ticket 1` with no `--expect` refuses naming `--expect`, writes no notes.md: pass. Evidence: ran the exact span, rc 0; stderr: `alpha: --ticket needs --expect <digest> from the dry run that listed the indices (run close --dry-run first); nothing written`.
- `grep -q '(cap)' tickets.py`: pass. Evidence: rc 0, and `grep -c '(cap)'` shows 19 occurrences (matches the builder's claimed new selftest cases).
- `grep -q -- '--ticket' ticket/SKILL.md`: pass. Evidence: rc 0; diff shows argument-hint and step 4 both updated with `--ticket N` semantics.
- `grep -q 'notes.md' ticket/SKILL.md`: pass. Evidence: rc 0; step 4 diff describes the notes.md format and dry-run `note` mark.
- `grep -q -- '--ticket' CLAUDE.md`: pass. Evidence: rc 0; diff shows the `scripts/tickets.py` bullet rewritten with tags, cap, `--ticket N`, notes.md.
- `grep -q 'notes.md' CLAUDE.md`: pass. Evidence: same diff, rc 0.
- `grep -q 'notes.md' fanout/SKILL.md`: pass. Evidence: rc 0; diff adds one sentence to section 4 noting fanout's close is the plain form landing follow-ups in notes.md.
- (guard) `python3 tickets.py selftest`: pass. Evidence: `tickets selftest: PASS` on the built tree. Checked the guard can go red (not vacuous): built a throwaway detached worktree at HEAD (`git worktree add --detach "$SDLC_TMP_WORKTREES/verify" HEAD`), applied the working tree's `tickets.py` diff there, confirmed green, then mutated the `--ticket` tag-gate (`if tag != 'decide':` → `if False:`) in that isolated copy only — selftest went red, failing exactly the three `(cap)` tag-gate expects (`--ticket on a note: item refuses...`, `...fix-now...`, `dry run --ticket on a note: item...`) with rc showing the tag check bypassed. Worktree removed afterward (`git worktree remove --force`); main tree untouched throughout (confirmed via `git status --porcelain` before/after, unchanged).

## Out of scope changes
`.sdlc/0142-finish-in-session/handoff.md` is modified in the working tree but the step did not call for it. Checked: its mtime (16:30:43) predates both the planner's run (`planner-L3.md` at 16:53:38) and the builder's run (`builder-L3.md` at 17:16:13), so the edit was already present in the working tree before this step's builder ran — consistent with the builder's own Notes claim ("Pre-existing change ... I did not touch it"), and the diff content (filling in the task's Intent section) is planner-shaped, not builder-shaped. Dismissing as pre-existing, not introduced by this step.

No other out-of-scope diffs: confirmed `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, `plugins/sdlc-lite/skills/file/SKILL.md`, and `plugins/sdlc-lite/scripts/fanout.py` (all named in the Do as explicitly untouched) show no diff (`git diff --stat` empty for all three).

## For the next attempt
None.
