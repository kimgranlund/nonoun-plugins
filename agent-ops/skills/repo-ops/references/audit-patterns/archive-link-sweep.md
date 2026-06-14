---
date: 2026-05-06
---

# Archive-link sweep (per-file relative-path rewrites)

**Added:** 2026-05-02 after the lockstep cut's plan archival surfaced 5 broken intra-repo links — each with a different relative-path depth.

## The drift class

When a doc moves via `git mv` from one tree location to another (typically `docs/plans/X.md` → `.agents/brain/archive/YYYY-Q/PLAN-X.md`), intra-repo links from other files break. **Each linking file has a _different_ relative-path depth** — sed alone can't fix them in one pass.

Example drift surface (from the 2026-05-02 plan archival):

```text
Linking file              Old → new
------------------------  ----------------------------------------------------------------
CHANGELOG.md (root)       ./docs/plans/X.md        → ./.agents/brain/archive/YYYY-Q/PLAN-X.md
ROADMAP.md (root)         same
docs/conventions/Y.md     ../plans/X.md            → ../../.agents/brain/archive/YYYY-Q/PLAN-X.md
docs/journal/YYYY/MM/Z.md ../../../plans/X.md      → ../../../../.agents/brain/archive/YYYY-Q/PLAN-X.md
packages/<pkg>/CHANGELOG  ../../../docs/plans/X.md → ../../../.agents/brain/archive/YYYY-Q/PLAN-X.md
```

5 files, 4 different relative-path patterns. A `sed -i 's|docs/plans/X|.agents/brain/archive/Y/PLAN-X|g'` doesn't work — the prefix segments differ.

## Detection

```bash
node scripts/check-links.mjs --all 2>&1 | head -20
```

Look for `resolves to: <path> (not found)` entries.

## Fix recipe (Python with explicit per-file tuples)

```python
import pathlib

ROOT = pathlib.Path("/path/to/repo")

# Each tuple: (linking_file, old_fragment, new_fragment)
EDITS = [
    (ROOT / "CHANGELOG.md",
     "./docs/plans/X.md",
     "./.agents/brain/archive/2026-Q2/PLAN-X.md"),
    (ROOT / "ROADMAP.md",
     "./docs/plans/X.md",
     "./.agents/brain/archive/2026-Q2/PLAN-X.md"),
    (ROOT / "docs/conventions/Y.md",
     "../plans/X.md",
     "../../.agents/brain/archive/2026-Q2/PLAN-X.md"),
    (ROOT / "docs/journal/2026/05/Z.md",
     "../../../plans/X.md",
     "../../../../.agents/brain/archive/2026-Q2/PLAN-X.md"),
    (ROOT / "packages/foo/CHANGELOG.md",
     "../../../docs/plans/X.md",
     "../../../.agents/brain/archive/2026-Q2/PLAN-X.md"),
]

for path, old, new in EDITS:
    text = path.read_text()
    if old in text:
        path.write_text(text.replace(old, new))
        print(f"  ✓ {path.relative_to(ROOT)}")
    else:
        print(f"  ✗ {path.relative_to(ROOT)} — old fragment not found")
```

After running, verify:

```bash
node scripts/check-links.mjs --all
```

Expected: zero broken intra-repo links.

## Prevention

This is mechanical drift — there's no preventing it without making all references absolute. Two practical mitigations:

1. **Pre-commit hook** runs `check-links.mjs` on every staged markdown change. The hook would catch the move + link rot in the same commit.
2. **The `stale-audit` skill** includes this check as part of its 7-check post-release sweep.

## Related

- See [`feedback_relative_path_after_archive.md`](`~/.claude/projects/<repo>/memory/`) — the user-memory entry capturing the lesson.
- Sibling concern to `feedback_directory_rename_outbound_refs` (which is about renames, not archive moves) and `feedback_git_mv_audit_imports` (which is about code imports inside moved files, not links from elsewhere TO the moved file).
- `stale-audit` skill check #4.
