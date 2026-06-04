---
date: 2026-05-06
---

# Spec dating sweep (git-mtime batch)

**Added:** 2026-05-02 after F-A7 finding identified ~25 spec files lacking date markers.

## The drift class

Files in `docs/specs/` (or the project's spec dir) should have a `date:` frontmatter or `_Last reviewed: YYYY-MM-DD_` line. Without this, future readers can't tell if the spec is current, when it was last reviewed, or whether to cross-check against more recent journal entries.

The standard fix is "add a `_Last reviewed: <date>_` line." But hard-coding today's date is wrong — it asserts a review that didn't happen for files you haven't read.

## Detection

```bash
for f in docs/specs/*.md; do
  if ! grep -qE "^date:|Last reviewed|_Date:_" "$f"; then
    echo "  $(basename "$f")"
  fi
done
```

## Fix recipe (mechanical Python batch using git-mtime)

Use git's last-modification date as the proxy for content freshness:

```python
import pathlib, re, subprocess

ROOT = pathlib.Path("/path/to/repo")
SPECS = ROOT / "docs/specs"

def has_date_marker(text):
    head = text[:1500]
    return bool(re.search(r"^date:\s*\d{4}-\d{2}-\d{2}", head, re.MULTILINE)) or \
           "Last reviewed:" in head or "_Date:_" in head

def git_mtime(p):
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", str(p)],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        return out if out else "TODAY"
    except subprocess.CalledProcessError:
        return "TODAY"

count = 0
for p in sorted(SPECS.glob("*.md")):
    if p.name == "INDEX.md":
        continue
    text = p.read_text()
    if has_date_marker(text):
        continue
    mtime = git_mtime(p)
    lines = text.splitlines()
    h1_idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if h1_idx is None:
        continue
    new_lines = lines[:h1_idx+1] + [""] + [f"_Last reviewed: {mtime}_"] + lines[h1_idx+1:]
    p.write_text("\n".join(new_lines) + "\n")
    count += 1
    print(f"  {p.name} → _Last reviewed: {mtime}_")

print(f"\nDated {count} files")
```

## Why git-mtime, not today's date

- **Accurate:** the file genuinely was reviewed when it was last edited; using that date doesn't lie.
- **Stable:** running the script idempotently doesn't push every spec's "Last reviewed" forward to today.
- **Surface-able:** `find docs/specs -name '*.md' -mtime +180` plus the dated content tells you which specs need an actual review.

## Prevention

The `format-hygiene` audit category catches new undated files. The batch sweep runs once on a backlog; ongoing prevention is via the audit's per-PR check.

## Related

- `format-hygiene` audit pattern (sibling).
- `stale-audit` skill check #5.
