---
date: 2026-05-06
---

# `[Unreleased]` block bloat detection

**Added:** 2026-05-02 after the AdiaUI repo's root `CHANGELOG.md` accumulated 933 lines of stale-promoted content that already existed in dated entries above.

## The drift class

Each release cut authors a new dated entry (`## [YYYY-MM-DD — …]`) but doesn't wipe the `[Unreleased]` content that was just promoted. Over weeks, `[Unreleased]` accumulates content that's already shipped.

Effects:

- File size bloats (root CHANGELOG was 3118 → 2202 lines after wipe).
- New readers can't tell what's actually pending — the long block looks like a backlog about to ship.
- `[Unreleased]` becomes a duplicate-content hazard for grep ("was this fixed?" → it appears in 3 places).

## Detection

```bash
# Count lines per package's [Unreleased] block
for f in CHANGELOG.md packages/**/CHANGELOG.md; do
  unreleased_lines=$(awk '/^## \[Unreleased\]/,/^## \[/' "$f" 2>/dev/null | wc -l)
  echo "$f: $unreleased_lines lines"
done | sort -t: -k2 -n -r
```

**Threshold:** > 30 lines is a smell. Likely duplicates the dated entry below. The actual content of `[Unreleased]` should be:

- Short (1-3 lines) summary of pending work for the next cut, OR
- `_No pending changes._` when nothing is staged

## Fix recipe

1. Read the next dated entry below `[Unreleased]`.
2. For each item in `[Unreleased]`, check if it's covered in the dated entry. If yes, delete from `[Unreleased]`. If no, the content is genuinely pending — leave it (or move to a more accurate dated entry if it shipped earlier).
3. Verify: line count drops; `git diff` shows only the wipe.

Python helper for the bulk wipe (when `[Unreleased]` is fully duplicate content):

```python
import pathlib
p = pathlib.Path("CHANGELOG.md")
text = p.read_text()
lines = text.splitlines()
ur_start = next(i for i, l in enumerate(lines) if l.startswith("## [Unreleased]"))
next_section = next(i for i in range(ur_start+1, len(lines)) if lines[i].startswith("## [2026-"))
sep_idx = next(i for i in range(next_section-1, ur_start, -1) if lines[i].startswith("---"))

replacement = ["## [Unreleased]", "", "_No pending changes._", ""]
new_lines = lines[:ur_start] + replacement + lines[sep_idx:]
p.write_text("\n".join(new_lines) + "\n")
```

## Prevention

After every release cut:

1. Wipe the released-package `[Unreleased]` to `_No pending changes._` OR a 1-3 line summary of what's staged for the next cut.
2. Wipe the root CHANGELOG `[Unreleased]` (if applicable).
3. Verify: `wc -l <changelog>` is consistent with prior cuts.

This is item #5 of the lockstep-release post-publish admin checklist.

## Related

- See [`feedback_changelog_unreleased_drift.md`](`~/.claude/projects/<repo>/memory/`) — the user-memory entry capturing this lesson.
- `stale-audit` skill — runs this check as part of its 7-check sweep.
