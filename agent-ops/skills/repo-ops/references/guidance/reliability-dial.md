---
date: 2026-04-27
coverage: canonical
peers:
  - llm-doc-writing.md
  - context-budget.md
  - ../recipes/self-healing-hooks.md
  - ../recipes/recommend-then-validate.md
primary_sources:
  - Steve Yegge, "Welcome to Gas City" — https://steve-yegge.medium.com/welcome-to-gas-city-57f564bb3607
  - https://code.claude.com/docs/en/best-practices
status: research-verified
---

# Reliability dial (configurable strictness)

> _"Reliability, friends, is a dial. You choose where to set it. More rounds of review, more backstops, more guardrails… you can get agentic workers to be as reliable as you need."_ — Steve Yegge, "Welcome to Gas City"

## What this delivers

Yegge's load-bearing insight: trying to set one absolute level of strictness for every repo is wrong. A solo side project and a regulated production codebase need different friction. `repo-ops` exposes a single explicit knob — **strictness** — and routes every trip-wire's threshold through it.

Three positions:

| Position | Posture | When to use |
| --- | --- | --- |
| **`lax`** | Discoverable but never blocks | Side projects, prototypes, exploration phases |
| **`normal`** | Default. Pre-commit warns/fails on critical | Most production repos |
| **`strict`** | Every promise's trip-wire must pass; multi-agent review required for any apply-mode fix | Regulated codebases, monorepos with many contributors, repos where doc breakage is costly |

Explicit knob beats implicit severity rubric: the team picks its dial position once, in `.agents/brain/config.toml`, and every check derives from there.

## The config file

`.agents/brain/config.toml` at repo root:

```toml
[repo-ops]
strictness = "normal"  # lax | normal | strict
version = "1.1"

# Optional per-trip-wire overrides
[repo-ops.overrides]
entry_file_max_lines = 200       # default for "normal"; "strict" = 150
orphan_grace_days = 30           # default for "normal"; "strict" = 7
doc_age_threshold_days = 365     # default for "normal"; "strict" = 180

# Tool adapter — map repo-ops's logical operations to THIS repo's stack (defaults assume Node + GitHub)
[repo-ops.tools]
link_check  = "lychee"               # or "node scripts/check-links.mjs", "markdown-link-check", "mlc"
hook_runner = "pre-commit"           # or "husky" (Node), "lefthook", "none"
skill_audit = "npm run audit:skills" # or "" to disable (repo has no skills/)
ci_provider = "github-actions"       # or "gitlab-ci", "circleci", "none"
ci_dir      = ".github/workflows"    # where the PR + scheduled trip-wire workflows live
```

For Node projects, equivalent block in `package.json`:

```json
{
  "repo-ops": { "strictness": "normal" }
}
```

For Python projects, `pyproject.toml`:

```toml
[tool.repo-ops]
strictness = "normal"
```

## Tool adapter (repo-stack commands)

`repo-ops` is **stack-agnostic**: its trip-wires are _logical operations_ (link-check, hook-run, skill-audit, CI), and the concrete commands resolve through `[repo-ops.tools]`. The defaults assume **Node + GitHub** (`lychee`, `npm run audit:skills`, `.github/workflows/`); a Python repo, a GitLab repo, or a repo with no skills overrides them:

| Logical operation | `[repo-ops.tools]` key | Default | Python / GitLab / none examples |
| --- | --- | --- | --- |
| Link checking | `link_check` | `lychee` | `markdown-link-check`, `mlc`, a wrapper script |
| Pre-commit hooks | `hook_runner` | `pre-commit` | `husky` (Node), `lefthook`, `none` |
| Skill audit | `skill_audit` | `npm run audit:skills` | an `audit-skills` script in your repo's tooling dir, `""` to disable |
| CI provider + dir | `ci_provider` / `ci_dir` | `github-actions` / `.github/workflows` | `gitlab-ci` / `.gitlab-ci.yml`, `none` |

**Why this matters:** every command in the recipes (`self-healing-hooks.md`, the Decompose Tier-1 table) is a _default_, not an assumption. When a recipe says `lychee` or `.github/workflows/`, read it as "the configured `link_check` / `ci_dir`." The named war-stories (e.g. the `adiahealth/gen-ui-kit` tag-push incident) are **illustrative**, not a claim about your stack. A non-Node, non-GitHub repo sets its equivalents here and every trip-wire follows — no fork, no hard-wiring. (This is the third orthogonal config knob: **strictness** = how loud, **git-sync** = where the brain lives, **tools** = which commands.)

## The resolver — strictness → thresholds (the single source of truth)

**This table is the resolver: the one authoritative map from strictness to every trip-wire's concrete threshold.** No recipe or script defines a threshold independently — each reads its value from here (via `.agents/brain/config.toml`). A `strict` level that does not change a value is visible _in this table_, never hidden in a script; that is what makes "reliability is a dial" a mechanism, not a slogan. Both the doc trip-wires and the six skill-stewardship signals route through it.

| Trip-wire | `lax` | `normal` | `strict` |
| --- | --- | --- | --- |
| **Entry-file length** | Warn >250 lines | Warn >150, fail pre-commit >200 | Fail pre-commit >150 |
| **AGENTS.md/CLAUDE.md drift** | Warn | Fail pre-commit | Require symlink (`ln -s AGENTS.md CLAUDE.md`) |
| **Broken intra-repo links** | Report only | Fail PR | Fail pre-commit |
| **Broken external links** (lychee) | Report weekly | Fail PR | Fail PR + fail pre-commit |
| **Doc frontmatter dates** | Suggest | Require on new docs | Require on all docs; review every 365d |
| **Orphan grace period** | 90 days | 30 days | 7 days |
| **AGENTS.md "Memory primitives" section** | Recommend | Require | Require + fail audit if missing |
| **`.agents/brain/adrs/` for repos > 1 year old** | Recommend | Recommend (medium severity) | Required (high severity) |
| **Apply-mode fixes** | Single agent | Single agent | Recommend agent + validate agent (see `../recipes/recommend-then-validate.md`) |
| **Auto-archive PR** | Manual review | Manual review | Multi-agent review |
| **Skill: pattern-recurrence → draft candidate** | ≥ 3 sessions | ≥ 2 sessions | ≥ 2 (≥1 as info) |
| **Skill: memory-citation → promote** | ≥ 5 citations | ≥ 3 citations | ≥ 2 citations |
| **Skill: description-vs-body churn** | ≥ 200 lines | ≥ 100 lines | ≥ 60 lines |
| **Skill: pairwise description Jaccard** | ≥ 0.70 | ≥ 0.60 | ≥ 0.50 |
| **Skill: stale path/tag ref** | info | warn | fail audit |
| **Skill: graduation-without-skill** | recommend | info | warn |
| **Trip-wire liveness window** (Promise 4) | 90 days | 30 days | 8 days |

## Choosing your position

The dial is **not a quality scale**. `lax` isn't bad and `strict` isn't good. They're matched to _cost of failure_.

```text
                cost of doc breakage to your team
   low ←───────────────────────────────────────→ high

   lax        normal                           strict
   │           │                                 │
solo prototype  most production repos      monorepo, regulated,
                                           high-stakes shared codebase
```

If `strict` causes more friction than it prevents, you're at the wrong position. Try `normal` first.

## Git sync (where the brain lives)

By default, `.agents/brain/` is committed to git — the brain _is_ shared across the team. But not every team wants this. Solo developers, research-survey notebooks, individual scratch repos, or teams that sync memory through a non-git mechanism (internal wiki, S3, Notion) may prefer to keep `.agents/brain/` local.

Two modes:

| Mode | What gets committed | Promise 5 (continuously-learning) | When to use |
| --- | --- | --- | --- |
| **`shared`** (default) | `.agents/brain/{adrs,postmortems,runbooks,archive,architecture,audit-history,changesets,config.toml}` (`cache/` + `cold-start/working/` always gitignored) | Applies to the team — artifacts compound across contributors | Most repos with >1 contributor |
| **`local-only`** | Nothing in `.agents/brain/` is committed; entire `.agents/brain/` is gitignored | Applies to **your local clone only** — your individual brain compounds; the team's doesn't | Solo, prototypes, or repos where memory syncs via a non-git system |

Configure in `.agents/brain/config.toml`:

```toml
[repo-ops.git-sync]
mode = "shared"   # shared | local-only
```

Default is `shared` — when omitted, behavior is identical to v1.5.0.

### What `local-only` changes

When `mode = "local-only"`:

- `.gitignore` should include `.agents/brain/` at the top (greenfield adds this automatically when configured).
- Every contributor maintains their own `.agents/brain/`. Your ADRs are not your teammate's ADRs.
- The **auto-archive PR workflow is disabled** (no PRs because nothing is tracked).
- The audit-history-ledger remains useful as a _local_ diagnostic but is not a SOC2-grade shared trail.
- The `concurrent-learnings-merge.md` recipe is irrelevant (no shared brain to merge into).
- The `cold-start-harvest.md` recipe is irrelevant (no shared brain to import into).
- Promise 5 still applies — but to _you_, not the team.

Switching `local-only` → `shared` later: remove `.agents/brain/` from `.gitignore`, set `mode = "shared"`, then `git add .agents/brain/` to stage what you've accumulated. The reverse direction (`shared` → `local-only`) requires deciding what to do with already-committed artifacts (typically: leave them committed for history; new artifacts go local).

### Granular per-subdir sync (advanced)

Some teams want finer control — e.g., share ADRs but keep `audit-history/` local-only (less PR noise; the SOC2 trail kept on a separate machine):

```toml
[repo-ops.git-sync]
mode = "shared"

[repo-ops.git-sync.committed]
adrs = true
postmortems = true
runbooks = true
archive = true
architecture = true
changesets = true
config = true            # config.toml itself
audit-history = false    # opt out of committing audit-history; stays local
```

Defaults match the `shared` mode table above. The audit warns if a subdir is gitignored when the chosen mode says it should be committed (or vice versa).

### Why this is separate from strictness

Strictness controls _how loud_ the audit/hooks are. Git-sync controls _where the brain lives_. The two are orthogonal:

- A **`local-only` + `strict`** brain is fine — you take your own notes very seriously.
- A **`shared` + `lax`** brain is fine — the team gathers but doesn't enforce.
- A **`shared` + `strict`** brain is the regulated-codebase posture (the original v1.1 default).
- A **`local-only` + `lax`** brain is the personal-scratch posture.

## How the audit honors the dial

When the audit runs, it loads `.agents/brain/config.toml` and threshold-routes every check. Findings include the dial position they were evaluated against:

```markdown
- **DRIFT — CLAUDE.md vs AGENTS.md** (severity: critical, evaluated at strictness=strict)
  - At `lax`: would have been a warning.
  - At `normal`: would have failed pre-commit.
  - At `strict`: requires symlink. Recommended fix: `ln -s AGENTS.md CLAUDE.md`.
```

This makes the dial _visible_, not just operative — when a finding fires, the team can see whether re-tuning the dial is the right answer or fixing the issue is.

## Anti-patterns

- **Setting `strict` and ignoring half the trip-wires.** Inconsistent. Either commit to the position or move to `normal`.
- **Setting `lax` permanently as a way to silence findings.** That defeats the purpose. Lax is for prototypes; if a real repo lives at `lax` for a year, escalate.
- **Per-file overrides everywhere.** Override sparingly. The defaults exist because they're empirically reasonable; per-file exceptions become drift over time.
- **Changing the dial mid-PR to make a check pass.** The dial belongs to the team and the repo, not to a single change.

## Cross-references

- The trip-wires themselves: `../recipes/self-healing-hooks.md`
- Recommend-then-validate (the multi-agent pattern `strict` requires): `../recipes/recommend-then-validate.md`
- Token-budget defaults (entry-file lengths): `context-budget.md`
- LLM-doc-writing (content quality): `llm-doc-writing.md`
- Audit history (where the dial position is recorded per run): `../audit-patterns/audit-history-ledger.md`
