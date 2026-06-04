---
date: 2026-04-27
coverage: canonical
peers:
  - self-healing-hooks.md
  - ../doc-types/adr-pattern.md
  - ../doc-types/postmortem-pattern.md
  - ../guidance/llm-doc-writing.md
primary_sources:
  - https://code.claude.com/docs/en/best-practices — Anthropic's iterate pattern
  - https://www.humanlayer.dev/blog/writing-a-good-claude-md
  - https://sre.google/workbook/postmortem-culture/
status: research-verified
---

# Continuously-learning loop (delivers Promise 5)

> **The premise.** A repo that doesn't learn from each session reverts to its baseline competence every Monday. The continuously-learning loop captures three classes of insight — _agent corrections_, _architectural decisions_, _incident lessons_ — at the moment they happen, into structured memory that compounds.

## What "continuously-learning" means concretely

A continuously-learning repo:

1. **AGENTS.md gets smarter every week.** When the agent makes a mistake, the user (or the agent itself) adds a correction. Over weeks, the file converges on what's load-bearing for that repo.
2. **Architectural decisions get captured at decision time** as ADRs in `.brain/adrs/`, not retroactively reconstructed from PR descriptions six months later.
3. **Incidents get post-mortems within 1 week.** Blameless. The post-mortem is linked from AGENTS.md's "Memory primitives" section so future agents know to check it.
4. **The decision log compounds.** A repo with 100 ADRs has more institutional memory than one with 10, _as long as the index stays current and the AGENTS.md pointer stays accurate_.

If any of these flows are broken, the repo isn't learning — it's just sitting on a snapshot.

## Three flows

### Flow 1 — The Anthropic iterate pattern (AGENTS.md corrections)

Source: [Anthropic Claude Code best practices](https://code.claude.com/docs/en/best-practices) and [HumanLayer's "Writing a good CLAUDE.md"](https://www.humanlayer.dev/blog/writing-a-good-claude-md).

**The mechanism.** When Claude / any LLM coding agent makes a mistake during a session, the user (or the agent itself) adds a one-line correction to AGENTS.md _during that same session_. Examples:

```markdown
# AGENTS.md (...)

## Conventions

- Tests: use Vitest, not Jest. (Reminder added 2026-04-27 after agent
  reached for Jest config three sessions in a row.)
- Imports: ESM only. No `require()` in source files.
- Migration files in `db/migrations/` are append-only — never edit existing
  ones; create a new migration. (Added 2026-03-15 after agent edited
  20260301-create-users.sql.)
```

The dated parenthetical is critical — it lets the user _delete_ the correction six months later when it's clearly load-bearing rather than a one-off.

**The audit check.** A healthy AGENTS.md shows evidence of iteration: dated correction notes, recently-added bullet points, occasional pruning. A frozen AGENTS.md (last commit 8 months ago) is a sign the loop isn't running.

**The trip-wire (soft).** AGENTS.md modified within the last 90 days for any active repo. If not, the audit emits an advisory finding: "AGENTS.md hasn't been updated in 8 months; either the repo is stable or the iterate-pattern isn't running."

**Pitfall.** Teams that _only_ add to AGENTS.md and never delete from it grow it past the 200-line ceiling within a year. The token-waste-detection trip-wire (Promise 2) catches this.

### Flow 2 — ADR-on-architectural-change

**The mechanism.** When a PR introduces an architectural change (new service, framework swap, schema rewrite, performance migration, dependency choice), the PR template requires an ADR to land alongside the code.

#### `.github/pull_request_template.md` (excerpt)

```markdown
## What

[summary]

## Why

[motivation]

## Architectural impact

- [ ] No architectural change (no ADR needed)
- [ ] Architectural change — ADR added at: `.brain/adrs/NNNN-*.md`
- [ ] Architectural change — ADR exemption granted by: [name]
      Reason: [why no ADR]
```

**The auto-detection.** A pre-merge CI job can flag PRs that touch likely-architectural surfaces (`docs/ARCHITECTURE.md`, top-level config files, `package.json` major-version bumps, new top-level directories) without an accompanying ADR.

```yaml
# .github/workflows/adr-required.yml (excerpt)
- name: Architectural-impact ADR check
  run: |
    base=origin/${{ github.base_ref }}
    arch_files_changed=$(git diff --name-only $base...HEAD -- \
      'docs/ARCHITECTURE.md' 'package.json' 'pyproject.toml' \
      ':(top)*.config.*' ':(top)*.toml' ':(top)Dockerfile*' || true)
    new_adrs=$(git diff --name-only $base...HEAD -- '.brain/adrs/*.md' | grep -c '^' || echo 0)
    if [ -n "$arch_files_changed" ] && [ "$new_adrs" -eq 0 ]; then
      echo "::warning::PR changes likely-architectural files but adds no ADR. Verify exemption box is ticked."
    fi
```

**The trip-wire.** `.brain/adrs/` should grow over time at a rate consistent with the repo's architectural-change rate. A 5-year-old repo with 2 ADRs is suspicious — either the team's not capturing decisions or they're capturing them somewhere else (PR descriptions, Slack, code comments). The audit flags repos with `<1 ADR per year of repo age` for `>1 year` repos.

### Flow 3 — Postmortem-on-incident

**The mechanism.** Within 1 week of a SEV-1 or SEV-2 incident, a blameless post-mortem lands in `.brain/postmortems/YYYY-MM-DD-name.md`. See `../doc-types/postmortem-pattern.md` for the template.

The flow itself runs _outside_ the repo (incident response, retrospective meeting, write-up) — but the _artifact_ lands in the repo and gets indexed.

**The trip-wire.** If the repo has had production incidents (heuristic: search `git log` for `revert`, `hotfix`, `incident`, `outage`, `rollback`) but `.brain/postmortems/` is empty, the audit flags it. False positives are fine — the prompt to write a post-mortem is the value.

## How AGENTS.md should expose the memory primitives

The "Memory primitives" section of AGENTS.md tells the agent _when to read_ each memory type. Without this, the agent doesn't know to consult ADRs before architectural changes or post-mortems before debugging.

```markdown
## Memory primitives

- **Before architectural changes**, read `.brain/adrs/` newest-first. If
  your proposed change conflicts with an `Accepted` ADR, write a new ADR
  superseding it; don't silently override.

- **When debugging a production issue**, search `.brain/postmortems/` for
  prior occurrences. Many "new" bugs are repeats.

- **When you make a mistake the user has to correct**, ask: "Should I add
  this to AGENTS.md so I don't repeat it?" Most of the time the answer
  is yes. Add a one-line correction with a dated parenthetical.

- **When a runbook is needed for a recurring operation**, file it in
  `.brain/runbooks/` rather than embedding it in AGENTS.md.
```

This section is what makes the loop _closed_ — without it, the artifacts exist in the repo but the agent doesn't know to consult them.

## The compounding effect (why this matters more over time)

Year 1: AGENTS.md is small, ADRs are 5-10, post-mortems are 1-2.

Year 3: AGENTS.md is still ~150 lines (because the iterate pattern includes pruning), ADRs are 30-40 (mostly historical, some active), post-mortems are 8-15. The repo has _learned_ what its actual gotchas are.

Year 5: An LLM agent dropped into this repo for the first time has access to 5 years of explicit institutional memory in a navigable format. That's the compound interest.

The opposite case: AGENTS.md was written once 5 years ago, never updated. ADRs don't exist. Post-mortems live in Slack. An agent dropped into this repo has no advantage over an agent dropped into any random repo.

## Verification — what the audit checks

| Flow | Check | Severity if missing |
| --- | --- | --- |
| Iterate AGENTS.md | AGENTS.md last-modified date < 90 days for active repos (heuristic: repo has commits in last 90 days) | Advisory |
| ADR-on-architectural-change | `.brain/adrs/` exists and contains ≥1 ADR per year of repo age (rough heuristic) | Medium |
| ADR PR template | `.github/pull_request_template.md` includes architectural-impact checkbox | Low |
| Postmortem-on-incident | If `git log` has incident-shaped commits, `.brain/postmortems/` is non-empty | Medium |
| AGENTS.md "Memory primitives" section | Section exists and points to ADRs + postmortems | High (closes the loop) |

A repo can pass all the _self-healing_ checks (Promise 4) and still fail _continuously-learning_ (Promise 5) — they're orthogonal. The hooks keep the surface clean; the loop makes it grow smarter.

## Common anti-patterns

- **AGENTS.md is in `Proposed` status forever** — corrections never get accepted into the canonical file. Loop is broken at the merge step.
- **ADRs in PR descriptions** — they don't compound; nobody can find them. Move into `.brain/adrs/`.
- **Post-mortems in private docs (Notion, Confluence)** — unreachable from the agent. Either move to `.brain/postmortems/` or link aggressively from AGENTS.md.
- **Memory primitives section missing from AGENTS.md** — artifacts exist, agent never reads them. Single most common loop break.
- **Post-mortems blame individuals** — chills future post-mortem candor. Audit the _language_, not just existence.

## Cross-references

- Self-healing hooks (Promise 4 — keeps the surface clean): `self-healing-hooks.md`
- ADR pattern: `../doc-types/adr-pattern.md`
- Post-mortem pattern: `../doc-types/postmortem-pattern.md`
- LLM-doc-writing guidance (length / iteration): `../guidance/llm-doc-writing.md`
- AGENTS.md spec: `../standards/agents-md-spec.md`
