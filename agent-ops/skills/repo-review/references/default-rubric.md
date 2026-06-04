---
date: 2026-05-16
---

# Default Rubric — 11 Dimensions

The default audit rubric. Each dimension has a definition, a list of **positive signals** (what excellence looks like), a list of **negative signals** (what drift looks like), and **scoring guidance** (1–5).

The rubric is **specialized per repo type** in `repo-type-adaptations.md` — weights and dropped dimensions vary. Read that file before assigning weights.

---

## How to Use This Rubric

Each dimension produces:

- **A score** (1–5) for the rubric.md document
- **An audit log** (findings) for the refactor-backlog.md
- **Excellence cites** for the tier-1-patterns.md candidates

The score is summarized; the findings and excellence cites are the substance. A repo can score well overall and still have specific P0 findings — and vice versa.

Scoring scale (applies to every dimension):

- **5 — Exemplary.** Could be cited as a tier-1 reference for other repos.
- **4 — Strong.** Solid foundation with isolated drift.
- **3 — Mixed.** Conventions exist but are inconsistently applied.
- **2 — Weak.** Conventions absent or routinely violated.
- **1 — Broken.** Active harm to the codebase.

If a dimension is N/A for the repo type, mark it `—` and explain in the rubric document; don't score it.

---

## 1. API Symmetry

**Definition:** Sibling functions, components, classes, and modules expose comparable surfaces for comparable concerns. Same-named props mean the same thing. Same shape of input/output across peer abstractions.

**Positive signals:**

- Boolean state props share a naming pattern (e.g., `disabled`, `loading`, `readonly` across all form participants)
- Pagination, filtering, sorting expressed the same way across list components
- Error shapes are uniform across API client functions
- Naming reuses verbs/nouns consistently (`create*`, `fetch*`, `*Item`)

**Negative signals:**

- One component uses `isOpen`, another uses `expanded`, another uses `visible` — for the same concept
- One module returns `{ data, error }`, the sibling returns `[data, error]`
- Required vs. optional props differ across siblings without justification
- Event handler prop names drift (`onChange` vs. `onValueChange` vs. `onUpdate`)

**Scoring guidance:**

- **5** — Symmetry is enforced by lint or types; no drift observable
- **4** — Symmetry is the lived convention; <5% drift
- **3** — Mixed: ~20% drift; clear inconsistency areas
- **2** — No discoverable convention; every author rolls their own
- **1** — Active harm: same name used for different concepts in neighboring files

---

## 2. Naming & Path Consistency

**Definition:** Filenames, directory names, identifier casing, and exported names follow a discoverable, consistent system.

**Positive signals:**

- File-name casing is invariant within a directory (all kebab-case or all PascalCase, not mixed)
- Test files follow a single convention (`*.test.ts`, `*.spec.ts` — pick one)
- Index/barrel files used consistently or consistently avoided
- Exported names match the file name (or follow a documented rule)
- Directory depth is bounded (no rogue 6-level-deep paths)

**Negative signals:**

- `userProfile.tsx` next to `user-settings.tsx` next to `User_Avatar.tsx`
- Mixed `.test.ts` / `.spec.ts` / `__tests__/` patterns
- Casing-only differences across imports (`Button` vs. `button`)
- Directory names contradict the package's stated taxonomy (e.g., a "primitives" folder containing app-level features)

**Scoring guidance:**

- **5** — Single, declared convention; lint-enforced
- **4** — Single lived convention, <10 violations corpus-wide
- **3** — Multiple competing conventions, each well-represented
- **2** — No convention; reads like several authors who never met
- **1** — Naming actively misleads (e.g., `utils.ts` containing business logic)

---

## 3. Abstraction Layering

**Definition:** Code is organized into layers (primitives → compositions → applications, or domain → application → infrastructure, etc.) and imports flow in one direction across layer boundaries.

**Positive signals:**

- A primitive never imports from a composition
- Application code imports from compositions, not from primitives directly (unless explicitly allowed)
- The layer boundary is enforceable (ESLint rules, fs-based check, package boundary)
- Cross-layer imports, when they exist, are justified by an ADR or comment

**Negative signals:**

- Primitives import from app-level files (inverted dependency)
- App code reaches into primitive internals
- "Utils" or "helpers" folders that have grown to contain everything
- Circular imports across layers
- A layer's responsibilities are unstated, so anything goes

**Scoring guidance:**

- **5** — Layers are mechanically enforced; violations are impossible without an exception annotation
- **4** — Layers are the lived convention; <5% violations
- **3** — Layers exist nominally but are routinely crossed
- **2** — No discoverable layering; flat mess
- **1** — Inverted layering: primitives depend on apps

---

## 4. Dependency Graph Health

**Definition:** Internal dependency graph is acyclic, has bounded fan-out per node, and external dependencies are minimal and justified.

**Positive signals:**

- No internal cycles (verify with `madge --circular` or equivalent)
- Most modules have <10 internal imports
- External dependencies are listed with rationale (or there's a CONTRIBUTING rule for adding new ones)
- Bundle-size impact of each external dep is known
- Dev vs. production deps are correctly separated

**Negative signals:**

- Circular import warnings ignored
- A "god module" imported by half the codebase
- Lodash + Underscore + Ramda all in the deps (overlap unaudited)
- Dependencies pinned to ranges that produce non-reproducible installs
- Production code uses deps that are in devDependencies (works by accident)

**Scoring guidance:**

- **5** — Acyclic, bounded, fully justified deps
- **4** — Acyclic, mostly bounded, deps lightly audited
- **3** — One or two cycles, fan-out unbounded in some places
- **2** — Many cycles, large hub modules, deps proliferating
- **1** — Dependency hell: cycles, redundancy, version chaos

---

## 5. Public Surface Discipline

**Definition:** What's exported vs. internal is intentional and stable. Breaking changes to the public surface are tracked.

**Positive signals:**

- `exports` field in package.json (or equivalent) limits surface
- Internal modules marked with `_` prefix, `internal/`, or `@internal` JSDoc
- Public types are documented; internal types are not (or vice versa, but consistently)
- Breaking changes appear in CHANGELOG with migration notes
- Deprecation cycle exists (warnings before removal)

**Negative signals:**

- Everything is exported from a single barrel; nothing is private
- Internal helpers leak through because they're transitively reachable
- No `exports` field; consumers can reach into anything
- Type breaking changes ship without notice
- "Public" API surface drifts every release

**Scoring guidance:**

- **5** — Public surface is declared, enforced, and tracked across releases
- **4** — Public surface is intentional but enforcement is partial
- **3** — Public/internal is a convention; routinely violated
- **2** — No public/internal distinction; everything is reachable
- **1** — Consumers can break with patch upgrades; no surface contract

---

## 6. Developer Experience (DX)

**Definition:** The codebase is friendly to a contributor who has never seen it. Errors are legible, types are useful, docs answer first questions, onboarding is < 1 day.

**Positive signals:**

- Error messages include what went wrong, where, and what to do
- Types are precise (no `any`, no over-broad `unknown`); type errors describe the problem
- README answers: what is this, who is it for, how to run, how to test
- AGENTS.md / CLAUDE.md exists and is current (see `repo-ops`)
- Local dev: clone → install → run < 5 minutes
- Common tasks have one obvious command

**Negative signals:**

- Errors are `Error: undefined` or stack-trace-only
- README is stale; commands no longer work
- `any` proliferation; type system is decorative
- Hidden setup requirements (env vars, system deps) not documented
- Multiple ways to do the same thing with no guidance on which is right

**Scoring guidance:**

- **5** — A new contributor lands a useful PR in < 1 day
- **4** — Onboarding is documented and works for most cases
- **3** — Possible but requires asking questions
- **2** — Tribal knowledge required for most tasks
- **1** — Hostile codebase; setup itself is an ordeal

---

## 7. Framework Idiom Adherence

**Definition:** The code works **with** its framework's grain, not against it. Uses framework primitives correctly; doesn't reinvent.

**Positive signals:**

- Uses framework's state primitives instead of rolling its own
- Uses framework's lifecycle correctly (mount/unmount, connected/disconnected, hydration)
- Doesn't fight the framework's rendering model
- Updates as the framework evolves (no 2-major-versions-behind stragglers)

**Negative signals:**

- Custom state system layered over framework state
- Workarounds for behaviors the framework supports natively
- "We did it this way before X was available" comments without follow-up
- Direct DOM manipulation in a virtual-DOM framework (or vice versa for Web Components: virtual-DOM-style diffing in a light-DOM component)
- Use of deprecated APIs

**Scoring guidance:**

- **5** — Idiomatic; could be a reference implementation
- **4** — Mostly idiomatic; isolated workarounds documented
- **3** — Mix of idiomatic and ad-hoc; framework not fully exploited
- **2** — Fighting the framework; many workarounds
- **1** — The framework is mostly an accident; could be ripped out

---

## 8. Semantic Correctness

**Definition:** HTML semantics, ARIA, schema definitions, type definitions, and protocol implementations are correct — not just "works visually" or "passes tests."

**Positive signals (UI):**

- Buttons are `<button>`, links are `<a>`, headings are leveled correctly
- Form labels are associated with their inputs
- Landmark roles used appropriately (`<main>`, `<nav>`, `<aside>`)
- ARIA used only where native semantics fall short
- Modal/dialog primitives use `<dialog>` or proper ARIA modal pattern

**Positive signals (non-UI):**

- JSON Schema or Zod schemas describe data accurately
- API responses match their documented contracts
- Protocol implementations follow the spec (MCP, A2UI, OpenAPI, etc.)

**Negative signals:**

- `<div onClick>` for buttons; `<span>` for headings
- ARIA used to "fix" what wrong elements broke
- Schemas that don't match the data shape
- Protocol "implementations" that diverge silently from the spec

**Scoring guidance:**

- **5** — Semantically correct; could be a teaching example
- **4** — Mostly correct; isolated issues
- **3** — Mix of correct and lazy
- **2** — Semantics ignored; visual/behavioral correctness only
- **1** — Actively misleading semantics

If this dimension is N/A (e.g., backend service with no schemas or protocols), mark `—`.

---

## 9. Accessibility

**Definition:** Keyboard navigation, focus management, color contrast, reduced-motion support, screen-reader operability.

**Positive signals:**

- Every interactive element is keyboard-reachable
- Focus order matches visual order
- Focus indicator is visible and meets WCAG SC 2.4.11
- Color contrast meets WCAG AA (or AAA when stated)
- Motion respects `prefers-reduced-motion`
- Screen-reader testing happens (manually or via tests)

**Negative signals:**

- Tab order skips elements
- Focus disappears (e.g., into a hidden modal background)
- Color is the only signal for meaning
- Animations can't be disabled
- ARIA labels missing or wrong
- Tests don't exercise keyboard paths

**Scoring guidance:**

- **5** — Accessibility is a graded gate; meets AA across the surface
- **4** — Strong baseline; isolated issues
- **3** — Mixed; the obvious paths work, edges don't
- **2** — Accessibility is incidental; not designed for
- **1** — Inaccessible in core paths

If non-UI repo, mark `—`.

---

## 10. Performance Posture

**Definition:** The repo is aware of its performance budget — bundle size, render cost, async hygiene, query cost. Aware doesn't mean optimized; it means measured.

**Positive signals:**

- Bundle size is monitored (CI gate or routine check)
- Hot paths have benchmarks or notes
- Async code uses cancellation, debouncing, batching where needed
- Database queries are reviewed for N+1
- Memoization used where measured to help, not speculatively

**Negative signals:**

- No bundle-size awareness; sudden 2× growth nobody noticed
- N+1 queries in hot paths
- Speculative memoization (memoizing things that aren't slow)
- Async-without-cancellation (memory leaks, race conditions)
- Synchronous I/O in hot paths

**Scoring guidance:**

- **5** — Performance is measured, budgeted, and gated
- **4** — Performance is observed; problems are caught reactively
- **3** — Performance happens by luck; no systematic measurement
- **2** — Performance ignored; routine regressions
- **1** — Active performance harm in core paths

---

## 11. Test Posture

**Definition:** Tests exist where they create value; they're not brittle; what's not tested is intentionally not tested.

**Positive signals:**

- Test pyramid is intentional (unit, integration, e2e in some ratio)
- Tests fail for the right reasons (refactor-friendly, not snapshot-spam)
- Critical paths covered; trivial paths not over-covered
- What's not tested has a stated reason (manual QA, type-system-enforced, etc.)
- Tests run fast enough to actually be run (CI < 10 min, local < 1 min)

**Negative signals:**

- Big balls of snapshots that fail on every refactor
- Tests that test the implementation, not the behavior
- 100% coverage badge with zero meaningful assertions
- Flaky tests left to retry
- Critical paths uncovered while trivial ones are tested to the bone

**Scoring guidance:**

- **5** — Test posture is a graded design; pyramid is intentional and works
- **4** — Tests provide real safety; isolated brittleness
- **3** — Mix of useful and ceremonial tests
- **2** — Tests exist but offer little safety
- **1** — Tests actively harm refactoring; refactors require rewriting tests

---

## Adding a Dimension

If the repo has a concern not covered above (e.g., **i18n**, **security posture**, **observability**, **data migration discipline**), add it during the rubric specialization step. Use the same format: definition, signals (+/-), scoring guidance.

When adding, ask: **does this dimension produce different findings than the existing 11?** If it overlaps significantly with one, fold it in. New dimensions only when they map to a distinct audit lens.

---

## Dropping a Dimension

If a dimension is N/A for the repo type, mark `—` and explain in `rubric.md`. Common drops:

- Backend service → drop **9. Accessibility**, often **8. Semantic Correctness** (unless API schemas)
- CLI tool → drop **9. Accessibility**, **10. Performance Posture** (usually), **8. Semantic Correctness**
- Throwaway prototype → drop **5. Public Surface Discipline**, **11. Test Posture**

See `repo-type-adaptations.md` for the full matrix.
