---
date: 2026-04-27
coverage: canonical
peers:
  - staleness-tooling.md
  - pointer-validation.md
  - orphan-detection.md
  - redundancy-detection.md
  - ../recipes/self-healing-hooks.md
  - ../recipes/continuous-learning-loop.md
primary_sources:
  - https://djw.fyi/portfolio/preventing-drift/ — Daryl White, "Avoiding the Silent Stale Doc Problem"
  - https://git-scm.com/docs/git-log — git log committer-date semantics
  - https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
status: research-verified
---

# Stale-content detection (delivers Promise 3, "less-prone-to-staleness")

> **The premise.** A doc can have intact links, no orphans, and a clean structure — and still be wrong. _Stale content_ is the case where the prose, examples, or commands no longer match the code they describe. This is the hardest staleness class to detect because there's no broken pointer to grep for; the rot is semantic. Three heuristics catch most of it cheaply. The rest needs LLM-on-diff (covered in `staleness-tooling.md`).

## Where this fits

`staleness-tooling.md` covers the _tools_ (lychee, Vale, markdownlint, LLM-on-diff). This file covers the _patterns_ — the heuristic checks the audit runs against the repo. Pair them: the tool tells you _what to run_, the pattern tells you _what to look for_.

## Three heuristics

| # | Heuristic | What it catches | Cost |
| --- | --- | --- | --- |
| 1 | **Git-mtime + missing dated frontmatter** | Docs nobody has touched in 6+ months that also nobody has explicitly re-affirmed | Cheap (one `find` + one `grep`) |
| 2 | **Symbol/path references in prose vs `git ls-files`** | Docs that mention class/function/file names that no longer exist in the codebase | Cheap (grep + set diff) |
| 3 | **Commands in docs vs current package manifest** | AGENTS.md says `npm install` but `pnpm-lock.yaml` is the only lockfile; or `python setup.py` but the project moved to `uv` | Medium (a few `jq` / file-existence checks) |

These three together catch the bulk of stale content. The long tail (semantic rot in prose) needs LLM-on-diff per `staleness-tooling.md`.

## Heuristic 1 — git-mtime + missing dated frontmatter

A doc unmodified for >6 months _and_ without a `_Last reviewed: YYYY-MM-DD_` line is probably stale. The "AND" is critical: a 4-year-old `docs/architecture.md` re-reviewed quarterly is not stale.

```bash
#!/usr/bin/env bash
# scripts/find-stale-by-age.sh
set -euo pipefail
threshold_days=180
now=$(date +%s)
find .agents/brain docs -type f -name '*.md' \
    -not -path '.agents/brain/archive/*' -not -path '.agents/brain/adrs/*' -not -path '.agents/brain/postmortems/*' \
    -not -path 'docs/archive/*' -not -path 'docs/adrs/*' -not -path 'docs/postmortems/*' \
    | while read -r f; do
        last=$(git log -1 --format=%ct -- "$f" 2>/dev/null || echo 0)
        [ "$last" -eq 0 ] && continue
        age=$(( (now - last) / 86400 ))
        [ "$age" -le "$threshold_days" ] && continue
        if rev=$(grep -oE '_Last reviewed:[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$f" \
                 | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1); then
            ru=$(date -j -f '%Y-%m-%d' "$rev" +%s 2>/dev/null \
                 || date -d "$rev" +%s 2>/dev/null || echo 0)
            [ $(( (now - ru) / 86400 )) -le "$threshold_days" ] && continue
            echo "STALE-AGE: $f (commit ${age}d ago; review $(( (now - ru) / 86400 ))d ago)"
        else
            echo "STALE-AGE: $f (commit ${age}d ago; no _Last reviewed:_ line)"
        fi
    done
```

Excluded folders: ADRs (immutable — see `../doc-types/adr-pattern.md`) and post-mortems (describe a fixed past event). Use `git log` committer-date, not filesystem mtime — `clone`/`rebase`/`worktree` clobber filesystem mtime.

## Heuristic 2 — symbol/path references vs `git ls-files`

A doc _names_ something (class, function, file path) that the code no longer contains. Catches the canonical class-renamed-doc-not-updated case.

```bash
#!/usr/bin/env bash
# scripts/find-stale-symbols.sh
set -euo pipefail
all_paths=$(git ls-files | sort -u)
find .agents/brain docs -type f -name '*.md' \
    -not -path '.agents/brain/archive/*' -not -path '.agents/brain/adrs/*' -not -path '.agents/brain/postmortems/*' \
    -not -path 'docs/archive/*' -not -path 'docs/adrs/*' -not -path 'docs/postmortems/*' \
    | while read -r f; do
        # Backticked file paths.
        grep -oE '`[a-zA-Z0-9_./-]+\.(ts|tsx|js|jsx|py|go|rs|java|rb|json|toml|yaml|yml)`' "$f" \
            | tr -d '`' | sort -u | while read -r ref; do
                grep -qxF "$ref" <<<"$all_paths" || echo "STALE-PATH: $f -> $ref"
            done
        # Backticked PascalCase identifiers (cheap class-name proxy).
        grep -oE '`[A-Z][a-zA-Z0-9_]{3,}`' "$f" \
            | tr -d '`' | sort -u | while read -r sym; do
                git grep -q -wF "$sym" -- ':!*.md' ':!.agents/brain/**' ':!docs/**' 2>/dev/null \
                    || echo "STALE-SYMBOL: $f -> $sym"
            done
    done
```

False-positive sources: symbols inside before/after code blocks; aliased symbols (`Foo = Bar`); test-only definitions. Emit as **advisory** — human reviews before acting.

## Heuristic 3 — commands vs package manifest

AGENTS.md says `npm install` but only `pnpm-lock.yaml` exists; the agent runs npm and pollutes the repo with `package-lock.json`. Precise enough to gate as a pre-commit check.

````bash
#!/usr/bin/env bash
# scripts/check-commands-vs-manifest.sh
set -euo pipefail
fail=0
pm=""
if   [ -f pnpm-lock.yaml ];                      then pm=pnpm
elif [ -f yarn.lock ];                           then pm=yarn
elif [ -f bun.lockb ] || [ -f bun.lock ];        then pm=bun
elif [ -f package-lock.json ];                   then pm=npm
fi
for f in AGENTS.md CLAUDE.md README.md CONTRIBUTING.md; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    if [ -n "$pm" ]; then
        awk '/^```(bash|sh|shell|console)/,/^```$/' "$f" \
            | grep -oE '\b(npm|pnpm|yarn|bun)\b' | sort -u | while read -r p; do
                [ "$p" != "$pm" ] && { echo "STALE-CMD: $f uses '$p'; lockfile is '$pm'"; fail=1; }
            done
    fi
    if [ -f uv.lock ]; then
        awk '/^```(bash|sh|shell|console)/,/^```$/' "$f" \
            | grep -qE '\b(pip install|python setup\.py)\b' \
            && { echo "STALE-CMD: $f uses pip/setup.py; uv.lock present"; fail=1; }
    fi
done
exit $fail
````

Extend per ecosystem: Cargo, Go modules, Bundler. Same pattern — canonical manifest vs command-block PM/runner mismatch.

## Putting the three together

The full stale-content pass:

```bash
echo "=== Heuristic 1: age ==="
bash scripts/find-stale-by-age.sh

echo "=== Heuristic 2: symbols ==="
bash scripts/find-stale-symbols.sh

echo "=== Heuristic 3: commands ==="
bash scripts/check-commands-vs-manifest.sh
```

Run weekly per `../recipes/self-healing-hooks.md`'s scheduled cron. Findings are filed as a single weekly issue, not as commit-blocking errors — these heuristics produce false positives and shouldn't gate merges.

The exception: heuristic 3 is precise enough to gate. If `pnpm-lock.yaml` exists and AGENTS.md says `npm install`, that's an unambiguous bug — wire it as a pre-commit check.

## Severity rubric

| Finding | Severity | Why |
| --- | --- | --- |
| Heuristic 3 — command mismatch (AGENTS.md says `npm` + `pnpm-lock.yaml`) | High | Agent will run wrong PM and pollute repo |
| Heuristic 2 — symbol referenced in AGENTS.md no longer exists | High | Canonical doc misleads agent on every session |
| Heuristic 2 — symbol referenced in `.agents/brain/**` or `docs/**` no longer exists | Medium | Lower visibility but still wrong |
| Heuristic 1 — doc >6mo old, no review line | Medium | Likely-but-not-certainly stale; advisory |
| Heuristic 1 — doc >12mo old, no review line | High | Almost certainly stale |

## What this pattern is NOT for

- **Broken intra-repo links** — that's `pointer-validation.md`. Stale content is about _correct prose about wrong code_, not about links.
- **External link rot** — `staleness-tooling.md`'s lychee.
- **Live external links pointing at outdated content** — that's a separate concern. `lychee` confirms the URL responds; it doesn't check whether the _fetched content still matches what the doc claims_. For that, see `../recipes/external-reference-verification.md` (WebFetch-powered, autoresearch-DNA).
- **Outdated dependency versions in lockfiles** — out of doc-audit scope; that's a Dependabot / Renovate problem.
- **Generic "the doc is too short / shallow"** — quality issues, not staleness; covered by `../guidance/llm-doc-writing.md`.

## Companion: when these heuristics aren't enough

For semantic rot the heuristics miss ("the doc says we use Postgres but actually we migrated to PlanetScale six months ago" — no symbol-name overlap, no command-block giveaway), the answer is **LLM-on-diff** per `staleness-tooling.md`. On every PR, an LLM compares the code diff against `AGENTS.md` and `.agents/brain/**` + `docs/**` and flags doc sections that should have changed. It's the most expensive layer (API calls per PR) and it's gated on `vars.LLM_DOC_DRIFT_ENABLED` per `../recipes/self-healing-hooks.md`.

The three heuristics in this file are the cheap baseline; LLM-on-diff is the deeper-but-pricier complement.

## Cross-references

- Tooling for staleness (lychee, Vale, markdownlint, LLM-on-diff): `staleness-tooling.md`
- Pointer validation (link-level rot): `pointer-validation.md`
- Orphan detection (unreachable docs): `orphan-detection.md`
- Redundancy detection (drift between fat files): `redundancy-detection.md`
- Self-healing hooks (where the cron runs): `../recipes/self-healing-hooks.md`
- Continuous-learning loop (how AGENTS.md _stops_ going stale): `../recipes/continuous-learning-loop.md`
- External-reference verification (WebFetch-powered; catches the gap above): `../recipes/external-reference-verification.md`
