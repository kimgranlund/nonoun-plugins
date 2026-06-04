---
date: 2026-04-27
coverage: canonical
peers:
  - pointer-validation.md
  - redundancy-detection.md
  - token-waste-detection.md
  - entry-file-coverage.md
  - ../recipes/self-healing-hooks.md
primary_sources:
  - https://en.wikipedia.org/wiki/Reachability — graph reachability (the formal model behind orphan detection)
  - https://github.com/lycheeverse/lychee — secondary; lychee's `--reachable` mode does similar accounting
  - https://djw.fyi/portfolio/preventing-drift/ — Daryl White on doc archival flows
status: research-verified
---

# Orphan detection (delivers Promise 1, "less-wasteful")

> **The premise.** A doc no one references is a doc no one reads — but it still costs tokens when a globbed `.brain/**/*.md` or `docs/**/*.md` load picks it up, still costs trust when a future reader finds it and can't tell whether it's current, and still drifts because no PR ever touches it. Orphans are the silent compounding cost of an unmaintained doc tree.

## The graph model

Treat the repo as a directed graph:

- **Nodes:** every Markdown file under `.brain/**` and `docs/**` plus the top-level entries (`AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, etc.).
- **Edges:** every relative-path link from one node to another (extracted by the same grammar `pointer-validation.md` uses).
- **Roots:** `AGENTS.md` is the canonical root. `CLAUDE.md` (when fat), `README.md`, and `CONTRIBUTING.md` are secondary roots.
- **Orphan:** any node in `.brain/**` or `docs/**` that is **not reachable** from any root.

Reachability is transitive — if `AGENTS.md` links `ARCHITECTURE.md` and `ARCHITECTURE.md` links `docs/services/auth.md`, then `auth.md` is reachable.

## What this pattern catches

| # | Class | Example | Severity |
| --- | --- | --- | --- |
| 1 | **Orphaned active doc** | `docs/setup-2024.md` not referenced; still describes current behavior | Medium |
| 2 | **Orphaned stale doc** | `docs/old-redis-setup.md` not referenced AND last touched 18 months ago | Medium |
| 3 | **Orphaned generated content** | `docs/api/Foo.md` from a typedoc dump nobody linked | Low (fix is `.gitignore`, not archive — see `redundancy-detection.md`) |
| 4 | **Orphan with inbound link from outside `docs/`** | `docs/onboarding.md` linked from a `package.json` script comment but not from any doc | Low (advisory — re-link from AGENTS.md) |

## The bash check

Two-pass set-difference: build the set of _files in `.brain/` + `docs/`_, build the set of _files referenced from a root or its transitive closure_, diff.

```bash
#!/usr/bin/env bash
# scripts/find-orphan-docs.sh — find .brain/*.md and docs/*.md unreachable from any root.
set -euo pipefail

all_docs=$(find .brain docs -type f -name '*.md' 2>/dev/null | sort -u)

roots=()
for r in AGENTS.md CLAUDE.md README.md CONTRIBUTING.md \
         .cursorrules .windsurfrules \
         .github/copilot-instructions.md .github/pull_request_template.md \
         .brain/README.md .brain/INDEX.md docs/README.md docs/INDEX.md; do
    [ -f "$r" ] && roots+=("$r")
done

# Extract resolved relative-path link targets from a Markdown file.
extract_links() {
    local src_dir; src_dir=$(dirname "$1")
    grep -oE '\]\([^)]+\)' "$1" \
      | sed -E 's/^\]\(//; s/\)$//; s/[[:space:]]+["\x27].*$//; s/#.*$//' \
      | while read -r path; do
            case "$path" in ''|http://*|https://*|mailto:*|file://*) continue ;; esac
            if [ -d "$src_dir/$path" ]; then
                find "$src_dir/$path" -maxdepth 1 -name '*.md' 2>/dev/null
            else
                python3 -c "import os,sys; print(os.path.normpath('$src_dir/$path'))"
            fi
        done
}

# Transitive closure: BFS from roots.
declare -A reachable
queue=("${roots[@]}")
while [ "${#queue[@]}" -gt 0 ]; do
    src="${queue[0]}"; queue=("${queue[@]:1}")
    [ -n "${reachable[$src]:-}" ] && continue
    reachable[$src]=1
    [ -f "$src" ] || continue
    while read -r t; do [ -f "$t" ] && queue+=("$t"); done < <(extract_links "$src")
done

for f in $all_docs; do
    [ -z "${reachable[$f]:-}" ] && \
        echo "ORPHAN: $f (last modified: $(git log -1 --format=%cs -- "$f"))"
done
```

Notes: `python3` only normalizes paths (swap for `realpath --relative-to=.` if unavailable). Reference-style links (`[text][ref]`) aren't parsed — use `lychee --include-paths` if needed.

## What to do with each orphan (the three-way choice)

For every `ORPHAN: <file>` finding, the audit recommends one of three actions. **Always via PR**, never silently:

### (a) Re-link — orphan is still relevant

The doc is current but unpointed. Add a link from AGENTS.md's "Where to find things" or the area `docs/<area>/README.md`:

```markdown
# AGENTS.md (excerpt)

## Where to find things

- **Architecture:** `.brain/architecture/`
- **ADRs:** `.brain/adrs/`
- **Onboarding:** `docs/onboarding.md`   <-- newly re-linked
- **Post-mortems:** `.brain/postmortems/`
```

### (b) Archive — orphan is obsolete-but-historic

Cutting loses institutional memory; keeping in place invites confusion. Move to `.brain/archive/`:

```bash
git mv docs/old-redis-setup.md .brain/archive/old-redis-setup.md
git commit -m 'docs: archive old-redis-setup.md (orphan, obsolete since 2025-10 Redis -> Memorystore migration)'
```

The `.brain/archive/` folder gets its own `README.md` listing what's in there and why it's archived. The audit _excludes_ `.brain/archive/**` from the orphan scan (everything in there is intentionally orphaned).

### (c) Delete — if the orphan adds no value

Truly obsolete content with no historical interest. **In a PR**, never silently:

```bash
git rm docs/notes-from-old-design-meeting.md
git commit -m 'docs: remove obsolete design-meeting notes (orphan, no longer relevant)'
```

The PR description must say _why_ — so a future reader who finds the deletion in `git log` understands the rationale.

## The 30-day grace period

Per `../recipes/self-healing-hooks.md`, the auto-archive workflow does _not_ archive on the first scan after a doc goes orphaned. The grace period is **30 days** of being orphaned-and-untouched before auto-archive proposes a PR.

Reasons: (1) a PR in flight may temporarily orphan a doc while a link is being moved; (2) a planned re-link may be queued; (3) genuine forgotten orphans accumulate dust within 30 days regardless. The audit _report_ always lists current orphans; the _auto-archive workflow_ applies the 30-day floor before acting.

## Always-referencing files (avoid false positives)

Some files act as _indices_ — they enumerate every file in a folder, so every file in that folder is reachable by virtue of the index existing. Treat these as ALWAYS_REFERENCING in the orphan-scan reachability graph:

| File                           | What it indexes                       |
| ------------------------------ | ------------------------------------- |
| `.brain/adrs/README.md`        | every ADR (`0001-*.md` … `NNNN-*.md`) |
| `.brain/postmortems/README.md` | every postmortem                      |
| `.brain/runbooks/README.md`    | every runbook                         |
| `docs/specs/INDEX.md`          | every spec                            |
| `docs/journal/README.md`       | every dated journal entry             |

Without them in the entry-file set, every ADR / postmortem / runbook / spec / journal entry shows up as an orphan — a false-positive cluster that drowns the real findings. Observed in the wild on 2026-04-29: an audit pass flagged seven ADRs as orphans because the orphan-scan didn't include `.brain/adrs/README.md` as a referencer. Adding it resolved all seven.

The rule is index-shaped: any folder with a `README.md` whose body is a _table_ listing the folder's files counts as a referencer. Apply this in the entry-file set:

```bash
ENTRY_FILES=(
  "AGENTS.md" "CLAUDE.md" "README.md" "PLAN.md" "ROADMAP.md"
  ".brain/adrs/README.md"          # ← add these
  ".brain/postmortems/README.md"
  ".brain/runbooks/README.md"
  "docs/specs/INDEX.md"
  "docs/journal/README.md"
)
```

## Excluding intentional orphans

Some docs are intentionally orphaned. Mark them so the audit doesn't keep flagging:

| Convention                                      | What it does              |
| ----------------------------------------------- | ------------------------- |
| Place file under `.brain/archive/**`            | Excluded from orphan scan |
| Add YAML frontmatter `orphan: intentional`      | Excluded from orphan scan |
| Add file to `.brain/ignore` (one path per line) | Excluded from orphan scan |

The skill recommends `.brain/archive/` as the default — it's the most discoverable. Frontmatter and ignorefile are escape hatches.

## Severity rubric

| Finding | Severity | Why |
| --- | --- | --- |
| Orphaned doc that contradicts AGENTS.md (stale active content) | High | Causes drift if anyone finds and follows it |
| Orphaned active doc (matches code/AGENTS.md but unlinked) | Medium | Useful content, agent never finds it |
| Orphaned stale doc (>6mo old, no `_Last reviewed:_`) | Medium | Obsolete; archive candidate |
| Orphaned generated content (typedoc/sphinx/etc.) | Low | Fix is `.gitignore`, not archive — see `redundancy-detection.md` |
| Orphaned doc with inbound link from non-doc source (script comment, code) | Low | Re-link from AGENTS.md and move on |

## What this pattern is NOT for

- **Files outside `.brain/` and `docs/`** — orphan-detection scope is `.brain/**` and `docs/**`. Top-level files (`LICENSE`, `package.json`) aren't candidates.
- **Code files** — dead-code detection is a separate problem. This audit is about _documentation_.
- **Folders with no `.md`** — assets-only folders (`docs/images/`) don't get scanned. They're referenced from inside `.md` files via `![alt](images/foo.png)`, which is a `pointer-validation.md` concern.

## Cross-references

- Pointer validation (the inverse — links that don't resolve): `pointer-validation.md`
- Redundancy detection (sibling Promise 1 audit): `redundancy-detection.md`
- Token-waste detection (orphans contribute to glob-load tax): `token-waste-detection.md`
- Entry-file coverage (the precondition — roots exist): `entry-file-coverage.md`
- Auto-archive workflow + 30-day grace: `../recipes/self-healing-hooks.md`
