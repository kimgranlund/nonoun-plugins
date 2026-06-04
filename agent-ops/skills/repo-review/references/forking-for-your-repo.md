---
date: 2026-05-16
---

# Forking repo-review for Your Repo

A team that runs this skill on the same codebase repeatedly will quickly want a **repo-specific variant** — `repo-review-<your- product>` — that bakes in the team's conventions, repo-type specialization, anti-pattern catalog, and in-repo exemplars. This file explains when forking pays off and how to do it cleanly.

---

## When to Fork

Fork when **two or more** of these are true:

- You run repo reviews on the same codebase more than once a quarter.
- The repo has stable, team-agreed conventions that diverge from the default rubric (e.g., custom CSS architecture, in-house state pattern, specific framework dialect).
- The team has known recurring anti-patterns it wants the skill to scan for specifically.
- You have in-repo exemplars (files the team agrees are "5/5") that can ground audit-agent calibration far better than industry anchors.
- The repo's type is a hybrid that doesn't fit cleanly into one row of `repo-type-adaptations.md` (e.g., a framework + reference app
  - docs site monorepo).

**Don't fork** if you're only running the review once, or if your conventions match the defaults — the upstream skill is the better default to maintain.

---

## What to Customize (and What NOT to)

| Customize | Keep as-is from upstream |
| --- | --- |
| Default cap values (e.g., your team uses 5/5/10) | The cascade model itself |
| Rubric weights for your repo type | The 5-wave structure |
| Added dimensions (e.g., "i18n discipline", "telemetry coverage") | The HITL gate pattern |
| Removed dimensions (e.g., drop "accessibility" for a backend service) | Adversarial pass requirement |
| Repo-specific anti-patterns to scan for | Output tree structure |
| In-repo exemplars (file:line refs to your "5/5" patterns) | Per-finding format (severity, evidence, etc.) |
| Repo-specific terminology in agent prompts | Tier Boundary Decisions section |
| Pre-loaded discovery findings (your repo's known shape) | Re-dispatch protocol for failing agents |

The **structure** (waves, gates, cascade, adversarial) is the value. The **defaults** (rubric, weights, exemplars) are what gets customized.

---

## The Fork Process

### Step 1 — Copy the skill

```bash
cp -r ~/.claude/skills/repo-review \
      ~/.claude/skills/repo-review-<product>
cd ~/.claude/skills/repo-review-<product>
```

Rename:

- Directory: already done by the copy
- `SKILL.md` frontmatter `name:` → `repo-review-<product>`
- `skill.json` `name:` → `repo-review-<product>`
- `skill.json` `lineage:` → `"repo-review"` (mark the fork)

Confirm three-way consistency:

```bash
grep "name:" SKILL.md skill.json
ls
```

All three must read `repo-review-<product>` exactly.

### Step 2 — Customize the description

The frontmatter `description` is the trigger surface. Make it repo-specific:

```yaml
description: >
  Multi-wave repo review specialized for the {Product} codebase
  (web-components framework + docs site + reference app monorepo).
  Specialized rubric: weights {custom dimensions list}; added
  dimensions: {list}; in-repo exemplars for calibration. Use whenever
  reviewing the {Product} repo or any of its sibling packages.
  Triggers on: "review {product}", "audit our framework", "rubric for
  {product}", etc.
```

Stay under 1024 chars. Keep the trigger surface aggressive — the specialized version should beat the generic one when the engineer is working in this repo.

### Step 3 — Specialize the rubric

Edit `default-rubric.md` (or fork it as `<product>-rubric.md`):

- **Set weights.** Pre-fill the rubric weights for your repo type so the Wave 2 HITL gate becomes "confirm these weights" instead of "build them from scratch."
- **Add dimensions** specific to your team's concerns. Use the same format: definition, positive/negative signals, scoring guidance.
- **Drop dimensions** that don't apply. Document why in the rubric file's preamble.
- **Lock-in scoring rationale.** For each dimension, add a section "What 5/5 looks like in {Product}" with file:line refs to in-repo examples.

### Step 4 — Add repo-specific exemplars

Edit `exemplars.md` (or fork it as `<product>-exemplars.md`):

- **Replace generic anchors** with in-repo file:line refs the team considers "5/5". A team-internal anchor calibrates an agent far better than a third-party reference.
- **Add anti-pattern exemplars.** Cite specific file:line refs to patterns the team has explicitly rejected. The audit agents will flag any new instances.

Example structure for a customized entry:

```markdown
## 1. API Symmetry — In-Repo Exemplar

**5/5 example:** `packages/web-components/button/button.js` —
the prop shape (`{ disabled, loading, size, variant, …}`) is the
team's canonical pattern. New components should mirror this.

**Anti-pattern example:** `packages/web-components/legacy-modal/
modal.js` lines 12-40 — pre-2025 modal API that used `{ isOpen,
onDismiss }` instead of the now-canonical `{ open, onClose }`.
Slated for migration; any new component echoing this pattern is a
blocker.

**Scoring for this repo:**
- 5/5 — Mirrors button.js shape
- 3/5 — Inconsistent but documented
- 1/5 — Echoes legacy-modal pattern
```

### Step 5 — Pre-load discovery findings

In `<product>-discovery.md` (new file), capture the things Wave 1 would otherwise re-discover every time:

```markdown
# Pre-loaded Discovery — {Product}

This file pre-fills Wave 1's discovery-notes.md for the {Product}
repo. The Discover agent should still verify these claims but doesn't
need to derive them from scratch.

## Repo shape
- Monorepo: 4 packages (web-components, web-modules, docs, examples)
- TypeScript, Vite, vitest, pnpm
- …

## Declared conventions
- AGENTS.md at root (canonical agent rules)
- CONTRIBUTING.md outlines PR conventions
- Style guide at docs/contributing/style.md
- …

## Repo-type classification
- Framework (web-components) + design system + reference app
- Hybrid: use Type 1 (framework) weights for /packages/web-components,
  Type 7 (design system) for /packages/web-modules, Type 2 (app) for
  /examples, Type 3 (library) for shared utilities.
- …
```

Then reference this in the Wave 1 brief: "Verify and extend the pre-loaded discovery at `<product>-discovery.md`. Update any claims that have changed."

### Step 6 — Add team-specific anti-patterns

In `<product>-antipatterns.md`:

```markdown
# Anti-Patterns to Scan For — {Product}

These are recurring failure modes the team has explicitly rejected.
The Wave 3 audit agents should grep for these patterns specifically.

## AP-1. Direct DOM manipulation inside connectedCallback
- pattern: `this.querySelector(…)` or `document.querySelector(…)`
  inside `connectedCallback`
- why-rejected: race condition with light-DOM children
- canonical-fix: use slotchange event or MutationObserver
- example-violation: `packages/legacy-modal/modal.js:42` (slated for migration)

## AP-2. …
```

In Wave 3 dispatch briefs, add:

> "Before scoring, grep for each anti-pattern in `<product>-antipatterns.md`. Any new instance is at minimum a P2 (cluster) or P0 (in a hot file)."

### Step 7 — Update the CHANGELOG and skill.json

Add a CHANGELOG entry:

```markdown
## [1.0.0-{product}.1] — {YYYY-MM-DD}

Fork of repo-review v{version}. Specialized for {Product}.

### Customizations from upstream
- Default caps: 5 P0 / 5 P1 / 10 P2 (team prefers wider net)
- Added dimensions: i18n discipline, telemetry coverage
- Dropped dimensions: none (all 11 apply)
- Repo-type weights: hybrid framework + design system + app
- In-repo exemplars: replaced industry anchors with team file:line refs
- Pre-loaded discovery: skip Wave 1's full topology scan
- Anti-pattern catalog: 12 team-specific patterns
```

Update `skill.json`:

- `version`: start at `1.0.0-{product}.1` (or your team's versioning)
- `lineage`: `"repo-review"`
- `tags`: add `"{product}"` for discoverability
- `files`: list every new/changed file

### Step 8 — Test the fork

Run the forked skill against the target repo. Verify:

- Wave 1 produces the expected discovery summary (with pre-loads)
- Wave 2 surfaces your custom weights at the HITL gate
- Wave 3 dimension agents reference your in-repo exemplars
- Wave 5 adversarial pass still produces tier movement (don't lose the adversarial discipline in the fork)

---

## Maintaining the Fork

Upstream `repo-review` will evolve. To stay in sync:

1. **Diff against upstream periodically.** Look for changes in `SKILL.md`, `wave-protocols.md`, `output-templates.md` — these are the structural files. Adopt changes that improve the workflow.
2. **Don't drift on the cascade model or HITL gates.** If you find yourself wanting to remove them, write a postmortem first.
3. **Promote stable customizations back upstream.** If your repo's "added dimensions" turn out to be useful for other repos, send them to the upstream maintainer to fold into defaults.

---

## Worked Example — Hypothetical "AcmeUI" Fork

`repo-review-acmeui` exists in `~/.claude/skills/repo-review-acmeui/`.

Customizations:

- **Caps:** 5/5/10 instead of 3/3/6 (team prefers visibility on more items)
- **Repo type:** monorepo with framework (web-components), design system (tokens + recipes), and docs site
- **Dropped:** none
- **Added:** _Token discipline_ (semantic vs primitive layering), _Composability_ (do primitives compose without fighting?)
- **In-repo exemplars:**
  - `packages/web-components/button/button.js` → 5/5 API symmetry
  - `packages/web-modules/forms/recipe.js` → 5/5 composability
- **Anti-patterns scanned:**
  - Direct DOM manipulation in connectedCallback
  - Custom state-management layered over framework state
  - Token names matching `--legacy-*` (deprecated namespace)

Triggers on: "review acmeui", "audit our framework", "P0 in acmeui", "rubric for acmeui". Beats the upstream skill in trigger ranking when working in this repo.

---

## When NOT to Fork

If you're tempted to fork but only have one of these conditions, do this instead:

- **Single review session** → run upstream skill, pass overrides in the invocation. ("Use caps 5/5/10. Use my in-repo file `docs/style.md` as the team rubric." The Wave 2 HITL gate surfaces these for confirmation.)
- **Pre-loaded discovery for one repo** → keep a `REVIEW-CONTEXT.md` in the repo root and feed it to the Wave 1 agent as context. Cheaper than maintaining a fork.
- **Custom weights for one type of audit** → the rubric's HITL gate already supports per-engagement weighting. Use it.

A fork is a _long-term commitment to a custom skill artifact_ — it's worth it only when you'd otherwise be repeating the customization in every session.
