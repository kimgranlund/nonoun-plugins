---
date: 2026-04-27
coverage: canonical
peers:
  - orphan-detection.md
  - stale-content.md
  - staleness-tooling.md
  - entry-file-coverage.md
  - ../recipes/self-healing-hooks.md
primary_sources:
  - https://github.com/lycheeverse/lychee — fast Markdown/HTML link checker (Rust)
  - https://daringfireball.net/projects/markdown/syntax#link — original Markdown link syntax (Gruber)
  - https://spec.commonmark.org/0.31.2/#links — CommonMark 0.31.2 link grammar
status: research-verified
---

# Pointer validation (delivers Promise 1, "less-wasteful" + Promise 3, "less-prone-to-staleness")

> **The premise.** A pointer that doesn't resolve is worse than no pointer. The agent follows the link, hits a 404, and either gives up (silent failure) or hallucinates (loud failure). This audit catches every relative-path reference in the repo's instruction graph and verifies it lands on a real file before the agent ever has to.

## What this pattern catches

Five classes of broken pointer:

| # | Class | Example | Severity |
| --- | --- | --- | --- |
| 1 | **Pointer to a renamed/moved file** | AGENTS.md says `docs/architecture.md`; file was moved to `.agents/brain/architecture/overview.md` six months ago | High |
| 2 | **Pointer to a never-existed file** | Author typo: `.agents/brain/runbooks/databse.md` (missing the `a`) | High |
| 3 | **Pointer to a folder without an index** | AGENTS.md says `.agents/brain/adrs/`; folder exists but no `README.md` to land on | Medium |
| 4 | **Pointer from canonical file to missing file** | AGENTS.md links `[Memory primitives](docs/memory.md)`; that file is gone | **Critical** |
| 5 | **Repo-root file using `docs/`-relative paths** | `PLAN.md` at repo root has `[spec](./specs/foo.md)`; resolves to `./specs/foo.md` (404), should be `./docs/specs/foo.md` | **Critical** |

Class 4 is the load-bearing case: the canonical entry file is the agent's single source of truth, and a broken link from it is a broken promise to every agent on every session.

Class 5 is a particularly nasty failure mode that surfaces when a doc gets moved between directories without its links being rewritten. **Watch for it** when `PLAN.md` / `ROADMAP.md` / `CHANGELOG.md` move from `docs/` to repo root (or vice versa), or when `docs/foo/bar.md` is hoisted to `docs/bar.md`. The check below catches it because relative-path resolution starts from the source file's directory — but human reviewers miss it constantly because the _display text_ often shows the correct path while the link itself is wrong:

```markdown
[`docs/specs/genui-multiturn.md`](./specs/genui-multiturn.md)
                                    ↑ broken — file is at root, not docs/
```

Observed in the wild on 2026-04-29: 25+ broken intra-repo links across `PLAN.md` + `ROADMAP.md` after the files were moved from `docs/` to repo root. Display text was correct on every link; targets all wrong.

## Scope: what files we validate pointers from

| File | Why |
| --- | --- |
| `AGENTS.md` | Canonical entry; every link must resolve |
| `CLAUDE.md` (when fat) | Same as AGENTS.md while it's still fat; once thin-pointered the only link is to AGENTS.md |
| `README.md` | Human + agent landing |
| `CONTRIBUTING.md` | Often points at `docs/dev-setup.md` etc. |
| `.agents/brain/**/*.md`, `docs/**/*.md` | Doc-to-doc links must resolve too |
| `.cursor/rules/*.mdc`, `.windsurfrules`, `.github/copilot-instructions.md` | If fat, validate; if thin pointers to AGENTS.md, only the one link to validate |
| `.github/pull_request_template.md` | Often points at ADR conventions / contribution guides |

Validate **relative paths only**. External URLs are `lychee`'s job — see `staleness-tooling.md` for the tool wiring. `lychee` will _also_ check intra-repo paths, but the skill implements its own check so the audit can run offline and produce structured findings independent of `lychee` being installed.

## The bash check (intra-repo links)

The link-extraction grammar (CommonMark 0.31.2 §6.3) is `[text](target)` with optional title. We capture `target` and check it.

```bash
#!/usr/bin/env bash
# scripts/check-pointers.sh
# Validate every relative-path link in entry + docs files.
set -euo pipefail

# Files we extract pointers from.
candidates=(
    AGENTS.md CLAUDE.md README.md CONTRIBUTING.md
    .cursorrules .windsurfrules
    .github/copilot-instructions.md
    .github/pull_request_template.md
)
for f in .agents/brain/**/*.md .agents/brain/*.md docs/**/*.md docs/*.md .cursor/rules/*.mdc 2>/dev/null; do
    [ -f "$f" ] && candidates+=("$f")
done

fail=0
for src in "${candidates[@]}"; do
    [ -f "$src" ] || continue
    # Extract the (target) of every Markdown link, drop quoted titles.
    grep -oE '\]\([^)]+\)' "$src" \
        | sed -E 's/^\]\(//; s/\)$//; s/[[:space:]]+["\x27].*$//' \
        | sort -u \
        | while read -r target; do
            # Skip empty, anchors-only, mailto:, and absolute URLs.
            case "$target" in
                ''|'#'*|mailto:*|http://*|https://*|ftp://*|file://*) continue ;;
            esac
            # Strip fragment (#section) before resolving.
            path="${target%%#*}"
            [ -z "$path" ] && continue
            # Resolve relative to the source file's directory.
            src_dir=$(dirname "$src")
            resolved="$src_dir/$path"
            # Folder pointer? Accept if folder exists and has a README.md or any *.md.
            if [ -d "$resolved" ]; then
                if [ -f "$resolved/README.md" ] || ls "$resolved"/*.md >/dev/null 2>&1; then
                    continue
                fi
                echo "EMPTY-FOLDER-POINTER: $src -> $target (folder exists but no .md inside)"
                fail=1
                continue
            fi
            # File pointer.
            if [ ! -f "$resolved" ]; then
                echo "BROKEN-POINTER: $src -> $target (resolved: $resolved)"
                fail=1
            fi
        done
done
exit $fail
```

Dedupe is done by `sort -u` per file — the same target referenced 5 times in one file emits only one finding.

## The dedupe step (why it matters for the report)

A 200-line AGENTS.md often references `.agents/brain/adrs/` 4-6 times (Where-to-find-things, Memory-primitives, Conventions, etc.). Without dedupe, a single broken folder produces a 6-line report. Dedupe per-source-file before reporting; the same target broken from multiple files is genuinely worth multiple findings (it tells you _where_ to fix).

## Folder-pointer special case

A pointer like `.agents/brain/adrs/` is not a file — it's a folder. The check passes if:

1. The folder exists, AND
2. The folder has a `README.md`, OR
3. The folder contains at least one `.md` file (so the agent can list and pick).

A folder with `.png` and `.svg` only is not a valid landing target for a doc pointer. Flag it with `EMPTY-FOLDER-POINTER`.

## External link validation (out of scope for this check)

External URLs (`https://...`) are validated by `lychee` per `staleness-tooling.md`. Reasons we keep them separate:

- External checks need network; intra-repo checks must run offline.
- External links rate-limit; intra-repo links are free.
- External links are validated weekly (cron) per `../recipes/self-healing-hooks.md`; intra-repo links are validated on every commit.

If you want a one-shot "all links" pass, run both sequentially:

```bash
bash scripts/check-pointers.sh   # intra-repo, fast, offline
lychee --no-progress '.agents/brain/**/*.md' 'docs/**/*.md' '*.md'   # external + intra-repo, network-bound
```

The intra-repo check is allowed to be redundant with `lychee --offline`; what it adds is structured output the audit pipeline can ingest without parsing `lychee` JSON.

## Severity rubric

| Finding | Severity | Why |
| --- | --- | --- |
| Broken pointer **from AGENTS.md** to a canonical file (`.agents/brain/adrs/`, `.agents/brain/postmortems/`, `.agents/brain/architecture/`) | **Critical** | Agent's primary memory map is wrong; trust collapses |
| Broken pointer from any other entry file (`CLAUDE.md`, `README.md`, `.cursor/rules/`) | High | Agent following that tool will hit 404 |
| Broken doc-to-doc pointer in `.agents/brain/**` or `docs/**` | High | Reachable but breaks navigation graph |
| Empty-folder pointer (`.agents/brain/runbooks/` exists, no `.md` inside) | Medium | Agent lands but finds nothing actionable |
| Pointer with stale fragment (`docs/foo.md#old-section` where the file exists but the anchor doesn't) | Low | File loads, agent skim-reads; advisory |

The fragment check (`#section-name` resolves to a real heading slug) is supported by `lychee --include-fragments` and is the cleanest way to catch class 5. Don't reimplement slug-generation in bash; pay the lychee dependency.

## What this pattern is NOT for

- **External links** — `staleness-tooling.md`'s `lychee` integration owns those.
- **Symbol references inside prose** — "the `FooHandler` class" is a _content_ claim, not a pointer; it's covered by `stale-content.md`.
- **Image / asset paths** — same machinery works (`![alt](path/to/img.png)`), but assets are usually checked-in alongside the doc, so failures are rare. The check above will catch them anyway.
- **Reference-style links** (`[text][ref]` with `[ref]: target` later in the file) — the bash above doesn't parse them. CommonMark §6.3.2. If your repo uses them, swap to a Python parser (`markdown-it-py`) or run `lychee --offline` which handles them natively.

## How AGENTS.md's pointers become self-healing

The pre-commit hook in `../recipes/self-healing-hooks.md` runs this check on every commit that touches `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, or any file under `.agents/brain/**` or `docs/**`. A broken pointer fails the commit — the author is forced to fix it locally. This is the cheapest place to catch it; by the time it reaches CI, the author has already context-switched.

The weekly cron (`repo-brain-weekly.yml`) re-runs the check across the whole repo (in case a PR touched a target without touching the source pointing at it — the canonical "rename without re-link" case).

## Cross-references

- Orphan detection (the inverse — files no one points at): `orphan-detection.md`
- Stale content (symbol-level rot): `stale-content.md`
- External link checking: `staleness-tooling.md`
- Entry-file coverage (the precondition — entry files exist): `entry-file-coverage.md`
- Self-healing hooks (where the check runs automatically): `../recipes/self-healing-hooks.md`
