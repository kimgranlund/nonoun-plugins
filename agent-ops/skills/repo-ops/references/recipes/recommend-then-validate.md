---
date: 2026-04-27
coverage: canonical
peers:
  - self-healing-hooks.md
  - audit-existing-repo.md
  - ../guidance/reliability-dial.md
  - ../audit-patterns/audit-history-ledger.md
primary_sources:
  - Steve Yegge, "Welcome to Gas City" — multi-agent consensus pattern
  - https://docs.anthropic.com/en/docs/claude-code/sub-agents — Claude Code subagent pattern
status: research-verified
---

# Recommend-then-validate (the two-agent fix pattern)

> _"You should never just have one coding agent managing infrastructure… you should always have at least two or three working together on a little crew. Any agent can go temporarily insane, at any time, and make a bad call."_ — Steve Yegge, "Welcome to Gas City"

## What this delivers

A single agent's apply-mode pass is **one source of truth, no consensus**. If that agent hallucinates a fix, the bad fix lands. The recommend-then-validate pattern splits the work:

1. **Recommender** — reads the audit; proposes specific fixes; produces a structured fix plan.
2. **Validator** — receives the fix plan; dry-runs each fix against the trip-wires; vetoes any fix that would break an invariant; opens the PR with only the surviving fixes.

The validator is _not_ a critic. It's an execution gate that runs the same trip-wires after a hypothetical fix and confirms they still pass. A fix that introduces a new violation gets rejected.

This pattern is **required for `strict` strictness** (per `../guidance/reliability-dial.md`) and **optional but recommended for `normal`** for any apply-mode pass touching >5 files.

## The fix-plan contract

The recommender emits a structured plan; the validator consumes it.

```yaml
# .agents/brain/fix-plan-2026-04-27.yaml (transient; consumed then discarded)
strictness: normal
findings_addressed:
  - id: DRIFT-CLAUDE-AGENTS
    severity: critical
fixes:
  - kind: symlink
    target: CLAUDE.md
    points_to: AGENTS.md
    reason: "Eliminates drift; satisfies Promise 1."
  - kind: edit
    file: AGENTS.md
    description: "Compress 'Conventions' from 80 to 30 lines (Promise 2)."
    diff_preview: |
      [diff body]
  - kind: archive
    file: docs/old-plan.md
    move_to: .agents/brain/archive/old-plan-2026-04-27.md
    reason: "Orphan, last modified 2024-08-15."
```

Each fix is _typed_ (`symlink | edit | archive | create | delete`). The validator knows how to dry-run each kind.

## The validator's veto rules

After a hypothetical fix, the validator re-runs the relevant trip-wires:

| Fix kind | Validator checks |
| --- | --- |
| `symlink` | Symlink target exists; ownership/permissions correct |
| `edit` | Resulting file still <200 lines (entry files); frontmatter still valid; no new broken links introduced |
| `archive` | File is genuinely orphaned (per `../audit-patterns/orphan-detection.md`); not within active grace window |
| `create` | Path valid; doesn't conflict with existing file; YAML frontmatter present |
| `delete` | **Always vetoed.** Move to `.agents/brain/archive/` instead. Hard rule, no overrides. |

If any veto fires, the fix is dropped from the plan and a finding is emitted: `VETO — <fix> rejected because <rule>`. The PR opens with the surviving fixes only.

## Implementation paths

### Path A — Sequential within Claude Code (simplest)

Use the Claude Code subagent pattern. Main agent acts as recommender; spawns a validator subagent via the Agent tool with a fresh context.

```text
1. Main agent runs the audit, builds fix plan, writes .agents/brain/fix-plan-*.yaml
2. Main agent spawns validator subagent: "Read .agents/brain/fix-plan-*.yaml;
   dry-run each fix; emit veto report."
3. Validator subagent returns veto list (fresh context — can't share rationalization)
4. Main agent removes vetoed fixes from plan; opens PR with remainder
```

The validator runs in fresh context, so it can't accidentally rationalize the recommender's earlier reasoning. Independent re-evaluation is the load-bearing property.

### Path B — Distributed via GitHub Actions

Two-job CI workflow. Job 1 (recommender) emits the fix plan as a workflow artifact. Job 2 (validator) downloads the artifact, dry-runs, opens the PR.

```yaml
# .github/workflows/repo-fixer-apply.yml
jobs:
  recommend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/audit.sh > /tmp/audit.json
      - run: bash scripts/build-fix-plan.sh /tmp/audit.json > /tmp/fix-plan.yaml
      - uses: actions/upload-artifact@v4
        with: { name: fix-plan, path: /tmp/fix-plan.yaml }

  validate:
    needs: recommend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: fix-plan }
      - run: bash scripts/validate-fix-plan.sh fix-plan.yaml > /tmp/vetoes.txt
      - run: bash scripts/apply-survivors.sh fix-plan.yaml /tmp/vetoes.txt
      - uses: peter-evans/create-pull-request@v6
        with:
          title: '[repo-fixer] Apply audited fixes'
          body-path: /tmp/pr-body.md
```

Job isolation ensures the validator can't share state with the recommender — Yegge's insight in cleanest form.

## Iterating within a budget (autoresearch DNA)

> Inspired by the `autoresearch` project — autonomous propose-evaluate-iterate within a fixed budget. Repo-fixer scopes the spirit, not the overnight unattended shape: bounded rounds, deterministic eval, every iteration logged to the audit history ledger.

The base pattern above is one round. For high-finding-count audits or `strict` strictness, that single round may leave fixes on the table — vetoed because of a _fixable_ issue (e.g., a proposed AGENTS.md compression would still exceed 200 lines, but a tighter version wouldn't).

The iterate-within-budget extension: when the validator vetoes fixes, feed the veto reasons back to the recommender and let it re-propose. Bounded by an explicit budget.

### Configuration

`.agents/brain/config.toml`:

```toml
[repo-ops.iteration]
enabled = false       # default: false (opt-in)
max_rounds = 3        # hard cap; loop exits early if no new fixes survive
wall_clock_seconds = 300  # 5 minutes total across all rounds
```

Each round, the recommender receives:

1. The original audit findings (unchanged)
2. The previous round's veto report (new — the agent reads "your symlink fix was vetoed because the target wasn't valid; here's why")
3. The set of already-applied fixes from prior rounds (so it doesn't re-propose them)

Each round logs to the audit history ledger as a separate entry within the run.

### When iteration helps

| Scenario | Outcome with 1 round | Outcome with 3 rounds |
| --- | --- | --- |
| Recommender proposes 200-line AGENTS.md compression that would exceed the budget | Vetoed; user gets a TODO | Round 2 produces a 150-line version that passes |
| Recommender suggests archiving a doc still in the 30-day grace window | Vetoed | Round 2 skips that doc; archives others |
| All fixes pass first-round validation | PR with N fixes | Same PR — loop exits early |

### When iteration doesn't help

- Single-finding fixes (no benefit beyond round 1)
- Vetoes that are fundamentally un-fixable (e.g., `delete-always-vetoed` — the rule will never let it through)
- `lax` strictness (over-engineered for the use case)

### Stop conditions

The loop terminates when ANY of:

1. All proposed fixes pass validation (early success)
2. Two consecutive rounds produce zero new survivors (convergence)
3. `max_rounds` reached
4. `wall_clock_seconds` exhausted

The PR opens with the union of surviving fixes across rounds, plus a final veto report listing what didn't survive.

### How autoresearch DNA maps in (and where it stops)

Autoresearch runs overnight, fully unattended, hill-climbing on a single file with a single metric. This loop runs in a single CI invocation, budgeted in minutes, human-reviewed via PR. We take _bounded propose-evaluate-iterate with a deterministic eval function_ — we don't take overnight autonomy. Yegge alignment ("shepherds, not auto-pilots") stays intact.

## When NOT to use this pattern

- **Single-file fixes.** Symlinking CLAUDE.md once doesn't need two agents; the trip-wire itself is the validation.
- **`lax` strictness on prototypes.** Friction unjustified.
- **Repos with no production cost of doc breakage.** Solo side projects.

The pattern earns its keep on multi-file passes where one bad fix can cascade.

## Anti-patterns

- **Recommender and validator share context.** Defeats the purpose. Validator must run in fresh context (subagent or separate CI job).
- **Validator can edit the plan.** No. Validator only vetoes; the recommender's fixes are immutable inputs. Editing happens in the next round.
- **Skipping the veto report.** The PR body should include the full veto list — humans need to see what _wasn't_ applied and why.
- **Auto-merging the PR.** No. The validator gate is necessary but not sufficient; humans still review and merge.
- **Three or more agents in parallel for the same plan.** Diminishing returns; coordination cost dominates after two. Yegge says "two or three" for _different problems_, not redundant validators on one problem.

## Cross-references

- Reliability dial (which `strictness` levels require this pattern): `../guidance/reliability-dial.md`
- Self-healing hooks (the trip-wires the validator runs): `self-healing-hooks.md`
- Audit recipe (the input to the recommender): `audit-existing-repo.md`
- Audit history (vetoes get recorded): `../audit-patterns/audit-history-ledger.md`
