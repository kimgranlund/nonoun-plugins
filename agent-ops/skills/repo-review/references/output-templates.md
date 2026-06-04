---
date: 2026-05-16
---

# Output Templates

Concrete, copy-pasteable templates for every file in the deliverable tree. The polish agent fills these in — zero inference required.

---

## review/README.md (cover memo)

```markdown
# Repo Review — {REPO_NAME}

**Reviewed:** {YYYY-MM-DD}
**Reviewer:** repo-review skill (multi-wave audit)
**Scope:** {one sentence: what was reviewed, modes/packages included}

## Headline Findings

1. **{P0-1 title}** — {one sentence: what's wrong, blast radius}
2. **{P0-2 title}** — …
3. **{P0-3 title}** — …

## Top Patterns to Preserve

1. **{Tier-1-1 title}** — {one sentence: why it matters}
2. **{Tier-1-2 title}** — …
3. **{Tier-1-3 title}** — …

## Rubric Scorecard

| Dimension | Score | Notes |
|---|---|---|
| API Symmetry | {n}/5 | {≤8 words} |
| Naming & Path Consistency | {n}/5 | … |
| Abstraction Layering | {n}/5 | … |
| Dependency Graph Health | {n}/5 | … |
| Public Surface Discipline | {n}/5 | … |
| Developer Experience | {n}/5 | … |
| Framework Idiom Adherence | {n}/5 | … |
| Semantic Correctness | {n}/5 | … |
| Accessibility | {n}/5 | … |
| Performance Posture | {n}/5 | … |
| Test Posture | {n}/5 | … |
| **Weighted average** | **{n}/5** | |

## Deliverable Tree

- [Rubric](./rubric.md) — the audit rubric used, specialized for this repo
- [Refactor Backlog](./refactor-backlog.md) — P0–P3 prioritized items
- [Tier-1 Patterns](./tier-1-patterns.md) — patterns worth preserving
- [Knowledge Foundation](./knowledge-foundation/) — themes that explain
  this repo to future agents
- [Before/After Sketches](./before-after/) — proposed P0 interventions

## Process Trail

- Audit waves: 5 (Discover → Audit → Synthesize → Adversarial → Polish)
- Audit dimensions evaluated: {n}
- Raw findings: {n} (deduped to {m})
- Adversarial pass: {n} demoted, {n} removed, {n} sharpened, {n} held
- HITL gates: {3 of 3 passed | 2 of 3 — skipped #2 per engineer}
```

---

## review/rubric.md

```markdown
# Audit Rubric — {REPO_NAME}

**Specialized for:** {repo type from discovery}
**Modes audited:** {modes from discovery}
**Date:** {YYYY-MM-DD}

## How This Rubric Was Specialized

{1–2 paragraphs: which dimensions were emphasized, which were dropped or
de-weighted, and why — citing the repo type and modes.}

## Dimensions

### 1. {Dimension name} — weight: {high | medium | low | N/A}

**Definition:** {pulled from default-rubric.md}

**Why this weight for this repo:** {1 sentence}

**Score:** {n}/5 — {2 sentences justifying the score with file:line
references}

**Signals checked:**
- {positive signal observed at file:line}
- {negative signal observed at file:line}

---

{repeat for each dimension}

## Dropped Dimensions

- **{dimension name}** — N/A for {reason: e.g., this is a CLI tool, no
  UI surface to audit}.

## Added Dimensions

- **{custom dimension name}** — {definition} — added because {reason
  tied to the engineer's input or discovered concern}.
```

---

## review/refactor-backlog.md

```markdown
# Refactor Backlog — {REPO_NAME}

**Caps:** {3 P0 / 3 P1 / 6 P2 / ∞ P3 — or override}
**Total items:** P0={n}, P1={n}, P2={n}, P3={n}

## How to Read This

Priorities are **cascade-ranked**. All candidate findings are scored
on (severity × blast-radius × compounding × theme-anchor × rubric-
weight); the top 3 land in P0, the next 3 in P1, the next 6 in P2,
and the remaining S-effort items in P3. When a finding falls out of
P0 in the adversarial pass, it cascades into P1 — bumping the
weakest P1 into P2, and so on. No finding is dropped silently.

The Tier Boundary Decisions section below records the closest calls
at each boundary — these are the rankings the team must defend
publicly.

Before/after sketches for every P0 are in `./before-after/`.

---

## P0 — Top {n}

### P0-1. {title}

- **Dimensions:** {dimension(s) this finding hits}
- **Severity:** {blocker | major}
- **Blast radius:** {single file | single package | cross-package | public API}
- **Effort:** {S | M | L | XL}
- **Priority score:** {value} — {leading factor: e.g., "blocker × public-API + compounding"}
- **Evidence:**
  - `{file}:{line}` — {one-line excerpt or description}
  - `{file}:{line}` — …
- **Observation:** {what the code does, neutrally stated}
- **Why it matters:** {cost to user, developer, or future change — be
  concrete; quantify if possible}
- **Suggested direction:** {1–3 sentences; the before/after sketch
  contains the full proposal}
- **Considered alternative:** {strongest counter-argument from the
  board-defense pass — what makes this not obvious to leave alone}
- **Cascade history:** {e.g., "Held P0 through adversarial pass —
  challenger argued for swap with P1-1; defender held citing
  compounding cost." OR "Promoted from P1 after adversarial pass
  demoted original P0-2."}
- **Before/after:** [`p0-1-{slug}.md`](./before-after/p0-1-{slug}.md)

### P0-2. {title}
{same shape}

### P0-3. {title}
{same shape}

---

## P1 — Top {n}

### P1-1. {title}

- **Dimensions:** {…}
- **Severity:** major
- **Blast radius:** {…}
- **Effort:** {…}
- **Priority score:** {value}
- **Evidence:**
  - `{file}:{line}` — {…}
- **Observation:** {…}
- **Why it matters:** {…}
- **Suggested direction:** {…}
- **Cascade history:** {e.g., "Originally a P0 candidate; cascaded
  to P1 after adversarial swap promoted P0-2 over this. Closest
  P0/P1 boundary call." OR "Held P1 through adversarial." }

{repeat for P1-2, P1-3}

---

## P2 — Top {n}

### P2-1. {title}
{abbreviated format — title, dimensions, evidence (1 cite), one-line
observation, one-line suggested direction, effort, cascade history
where notable}

{repeat for P2-2 … P2-6}

---

## P3 — Quick Fixes (uncapped)

| # | Title | File:Line | Effort | Suggested |
|---|---|---|---|---|
| P3-1 | {title} | `{file}:{line}` | S | {one line} |
| P3-2 | … | … | S | … |

---

## Tier Boundary Decisions

The closest calls at each boundary — the rankings most likely to be
challenged. Each line documents why the cut fell where it did **after
the adversarial pass settled**.

### P0 / P1 boundary

- **P0-3 {title}** earned P0 over **P1-1 {title}** because {1
  sentence — usually the dominant priority_score factor: e.g.,
  "blast radius hits public API while P1-1 is contained to one
  package"}.
- **Closest alternative swap considered:** {if the consultant pass
  recommended a swap that was rejected, note it here with the
  rationale.}

### P1 / P2 boundary

- **P1-3 {title}** held P1 over **P2-1 {title}** because {1 sentence}.

### P2 / P3 boundary

- **P2-6 {title}** held P2 over the closest P3 because {1 sentence —
  usually "fix isn't trivial enough for a quick grab"}.

---

## Adversarial Pass Audit Trail

For accountability: what moved, why, and where it landed.

| Item | Pre-adversarial | Post-adversarial | Reason |
|---|---|---|---|
| {title} | P0 candidate | P1 | Consultant promoted {other item}; cascade |
| {title} | P1 candidate | P2 | Board defense verdict: SHRINK; smaller fix moved tier |
| {title} | P0 candidate | REMOVED | Evidence collapsed under verification |
| {title} | Uncategorized | P2 | Promoted from pool to fill cascade slot |
```

---

## review/tier-1-patterns.md

````markdown
# Tier-1 Engineering Excellence — {REPO_NAME}

These are patterns this repo gets right. They are load-bearing for the
architecture and easy to lose accidentally in a refactor. Treat as a
**preservation contract**: when the next refactor touches one of these,
the burden is on the refactorer to justify the change.

---

## 1. {Pattern title}

**Where:** `{file}:{line}` (and {n} other locations cited inline)

**What it does:** {1–2 sentences describing the pattern concretely}

**Why Tier 1:** {one paragraph answering "why did this earn promotion
to the protected list?" — name the specific elevation criteria:
(a) cited by N audit agents across dimensions, (b) load-bearing for
which architectural properties, (c) subtle invariant easy to break.
Be specific about what the codebase would lose if it disappeared.}

**Illustration** (include when the pattern is best shown in code):

```{language}
// {file}:{line}
{minimal code snippet showing the pattern}
```

**Preserve when:** {what kinds of changes put this at risk; e.g., "adding a new state primitive — make sure it still flows through the single setState pathway"}

**Related backlog items:** {if any P0/P1 explicitly preserves this pattern, link it}

---

## 2. {Pattern title}

{same shape}

---

{aim for 5–10 patterns}

---

## How These Were Selected

Patterns that appear in this document met at least one criterion:

- Cited by ≥2 audit agents (out of {n}) as exemplary in their dimension
- Load-bearing: removal would degrade ≥2 rubric dimensions
- Subtle invariant: easy to break in a well-intentioned refactor

Patterns that were noted as good but didn't meet the bar are in the audit working files but not promoted here. Tier-1 is a deliberately small list — too many entries dilute the "preserve at all costs" signal.

The **Why Tier 1** field is the elevation rationale — it answers "what specifically earned this promotion?", not just "why is this good?". A pattern that's good but isolated to one dimension and not load-bearing belongs in the per-dimension audit working files, not here.

````

---

## review/knowledge-foundation/{theme-slug}.md

````markdown
# {Theme title}

> A theme from the repo audit. Read this if you're about to work in
> the area it covers — it explains how this part of the codebase
> thinks, what's load-bearing, and where it tends to drift.

## The Pattern (As Lived)

{2–3 paragraphs: how the codebase actually approaches this concern
today. Cite 3–5 representative files. Be descriptive, not prescriptive.}

## Pattern Illustration (Before/After)

> Include this section when the pattern is best illustrated by code.
> If the pattern is purely structural/organizational (e.g., "auth
> middleware lives at the API boundary"), omit and rely on prose
> + file refs above.

**Before** — {1-line label: anti-pattern from the wild, or hypothetical
counter-example}:

```{language}
// {optional file:line for in-the-wild anti-pattern, or // (hypothetical)}
{actual or representative code showing what to avoid}
```

**Why this hurts:** {1–2 sentences naming the concrete cost}

**After** — {1-line label: the canonical pattern}:

```{language}
// {file:line citing the lived canonical example, OR // (target shape)}
{the pattern as it should be expressed; matches a real file when possible}
```

**Why this works:** {1–2 sentences tied back to the underlying constraint}

## Where It Came From

{1 paragraph: any historical context the engineer mentioned, any ADRs/postmortems that touch this area. If unknown, say so: "No documented origin; inferred from the lived pattern."}

## Where It Drifts

{Findings from the audit that touch this theme. List with file:line citations.}

## The Target Pattern

{1–2 paragraphs: what "fully consistent" would look like, without being prescriptive about HOW to get there. If the Pattern Illustration section already shows the target via code, this can be brief and focus on structural/non-code aspects.}

## Conceptual References

{2–4 external references that ground the theme — published patterns, RFCs, framework docs, design system precedents. Cite URLs or doc names.}

## Related Backlog Items

- [{P-N title}](../refactor-backlog.md#{anchor}) — {one-line connection}
- [{P-N title}](…) — …

## Related Tier-1 Patterns

- [{pattern title}](../tier-1-patterns.md#{anchor}) — {one-line connection}

````

---

## review/before-after/p0-{n}-{slug}.md

````markdown
# P0-{n} Before/After — {title}

> The full intervention proposal for [{P0-n}](../refactor-backlog.md#{anchor}).

## What Changes

{1 paragraph: the user-visible / developer-visible change. State it
plainly without code first.}

## Before

```{language}
// {file}:{line}
{actual current code, copied exactly — not a paraphrase}
```

**Why this hurts:** {2–3 sentences: the concrete cost — name the audience that pays the cost (user, contributor, future-author of adjacent file)}

## After

```{language}
// {file}:{line}
{proposed code, complete enough to compile/run conceptually}
```

**Why this is better:** {2–3 sentences tracing each improvement to the rubric dimension(s) it addresses}

## Migration

Steps to get from before to after:

1. {atomic step with file scope}
2. {atomic step}
3. {atomic step}

**Estimated effort:** {S | M | L | XL} ({n hours / days})

**Blast radius:** {single file | single package | cross-package | public API}

**Risk:** {what could go wrong — race conditions, breaking changes, test gaps; mitigation per risk}

## Verification

How we know the change worked:

- {test added or modified}
- {observable behavior to check}
- {metric or lint rule that catches regression}

## What This Does NOT Solve

{1 paragraph: scope boundaries. This P0 addresses X; it does not address Y or Z (which appear elsewhere in the backlog or as intentionally out of scope).}

## Considered Alternative

{The strongest counter-argument from the adversarial pass — what defenders of the current code would say, and why we're proposing the change anyway.}

````

---

## Standard Finding Format (used inside Wave 3 working files)

```markdown
## Finding — {≤80 char headline}

- **severity:** {blocker | major | minor | nit}
- **evidence:**
  - `{file}:{line}` — {one-line excerpt or description}
  - `{file}:{line}` — {…}
- **observation:** {what the code does, neutrally stated}
- **why-it-matters:** {cost to user, developer, or future change}
- **suggested-direction:** {1–3 sentences; not a full fix}
- **effort-estimate:** {S | M | L | XL}
- **blast-radius:** {single file | single package | cross-package | public API}
```

## Standard Excellence Format (used inside Wave 3 working files)

```markdown
## Excellence — {≤80 char headline}

- **evidence:** `{file}:{line}`
- **why-exemplary:** {one paragraph — what this does well in {dimension}}
- **preserve-when:** {what kinds of changes would put this at risk}
- **cross-dimension-impact:** {does this pattern carry value beyond
  {dimension}? If yes, name the other dimensions it touches. This
  is the signal Wave 6 uses to promote to tier-1.}
```

Note: the Wave 3 field is `why-exemplary` (excellence within the dimension). When Wave 6 promotes a pattern to tier-1, it adds the `Why Tier 1` field which is the _elevation_ rationale (why this earned promotion to the protected list across dimensions). Two fields, two purposes — don't conflate.
