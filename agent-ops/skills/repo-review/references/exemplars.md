---
date: 2026-05-16
---

# Exemplars — Calibration Anchors per Dimension

Audit agents need calibration. "Score this repo's API symmetry 1–5" without a reference point produces wildly inconsistent results across agents. This file gives each dimension 1–2 publicly known anchors at the **5/5 end** and a brief description of what the anchor does that makes it exemplary.

These anchors are **descriptive shapes**, not file:line citations. External repos change over time; cite the _pattern shape_ and the _project that exhibits it_, not specific code that may have moved.

When auditing, the agent asks: **"Is this repo closer to the exemplar shape or to the negative-signal end of the scale?"**

A team's fork of this skill (see `forking-for-your-repo.md`) should replace these with **repo-specific exemplars** — the team's own file:line references to what 5/5 looks like in their codebase.

---

## 1. API Symmetry — 5/5 anchor shapes

**Anchor: Stripe SDK method shape.** Every resource has the same verb set (`create`, `retrieve`, `update`, `list`, `del`) with consistent parameter conventions. A consumer who learns one resource can predict the next without reading docs.

**Anchor: TanStack Query / TanStack Router hook signatures.** Hook options across the library share a stable shape — `{ queryKey, queryFn, enabled, staleTime, … }` for queries; route definitions share `{ component, loader, validateSearch, … }`. When new hooks are added, they extend the shape rather than inventing a new one.

**What to look for in the audited repo:**

- Can you predict the signature of an unread sibling from a read one?
- Do new additions extend the convention or break it?
- Same-named props (`disabled`, `loading`, `onChange`) mean the same thing across every component?

---

## 2. Naming & Path Consistency — 5/5 anchor shapes

**Anchor: Next.js app router conventions.** `app/page.tsx`, `app/layout.tsx`, `app/loading.tsx`, `app/error.tsx` — the filesystem itself is the convention; an experienced contributor can locate anything from the path alone. The convention is also lint-enforced by the framework.

**Anchor: Go standard library file naming.** One concern per file, filename is the concern (`reader.go`, `writer.go`); `*_test.go` for tests, `doc.go` for package docs. The whole stdlib reads as if one author wrote it.

**What to look for:**

- File casing invariant within a directory
- Single test-file convention (not `.test.ts` + `.spec.ts` + `__tests__/`)
- Directory depth bounded; no rogue 6-level paths
- Exported names match filename or follow a documented rule

---

## 3. Abstraction Layering — 5/5 anchor shapes

**Anchor: htmx.** Has one primary primitive (HTML attributes), one behavior layer (the htmx runtime), and the layers don't leak across each other. Documentation makes the layering explicit; the codebase enforces it.

**Anchor: Hexagonal-architecture exemplars (e.g., Hexagonal Java templates).** Domain / application / adapters — imports flow inward only. Enforced by package boundaries and (ideally) by a build-time check.

**What to look for:**

- A primitive never imports from a composition
- Layer boundary is enforceable (lint rule, fs check, package boundary)
- Cross-layer imports, where they exist, are justified by an ADR or marker

---

## 4. Dependency Graph Health — 5/5 anchor shapes

**Anchor: Preact / Mithril.** Minimal external deps (often zero runtime). Internal deps are acyclic and shallow. Bundle size disclosed prominently. New deps require justification.

**Anchor: Deno standard library.** No external deps in core modules; bundle composition is auditable; every import is an explicit URL with a version.

**What to look for:**

- `madge --circular` (or equivalent) reports zero cycles
- No "god module" imported by half the codebase
- External deps are listed with rationale or a CONTRIBUTING rule
- Bundle-size impact of each external dep is known

---

## 5. Public Surface Discipline — 5/5 anchor shapes

**Anchor: Zod's package.json `exports` field.** The public surface is explicitly enumerated; internals are unreachable from consumer code. Type-level public surface mirrors the runtime surface.

**Anchor: React's documented `* / unstable_* / __NON_OFFICIAL` prefix taxonomy.** Stability is visible at the import site; consumers know what they're opting into.

**What to look for:**

- `exports` field (or equivalent) limits the surface
- Internal modules marked with `_` prefix, `internal/`, or `@internal` JSDoc
- Public-surface breaking changes appear in CHANGELOG with migration notes
- Deprecation cycle exists (warning before removal)

---

## 6. Developer Experience (DX) — 5/5 anchor shapes

**Anchor: tRPC error messages.** Type errors describe the problem in domain terms, not in TypeScript-compiler terms. The compiler becomes a teacher, not a barrier.

**Anchor: Vite startup output.** Time-to-dev-server is sub-second in normal cases; the output tells you the URL, the deps that loaded, and any warnings that need attention — nothing more.

**Anchor: Stripe's docs-as-product approach.** Docs are versioned with the code; every API has a live example; error responses link to the docs for that error.

**What to look for:**

- Error messages include what went wrong, where, and what to do
- Types precise (no `any` proliferation; `unknown` only at boundaries)
- README answers: what is this, who is it for, how to run, how to test
- Clone → install → run < 5 minutes for a new contributor

---

## 7. Framework Idiom Adherence — 5/5 anchor shapes

**Anchor: Lit's example components.** Every component is built **with** Web Components, not on top of them. Uses native ElementInternals, native FACE for form-associated, native Popover API where available — doesn't reinvent.

**Anchor: SolidJS sample apps.** Signals used as intended; no attempts to layer React's reactivity model on top. The framework's grain is followed.

**What to look for:**

- Uses framework state primitives instead of rolling its own
- Uses framework lifecycle correctly (mount/unmount, connected/ disconnected, hydration)
- No workarounds for behaviors the framework supports natively
- No "we did it this way before X was available" without follow-up

---

## 8. Semantic Correctness — 5/5 anchor shapes

**Anchor: GOV.UK Design System.** Every component produces correct HTML semantics; ARIA is used only where native semantics fall short. Form components are labeled and associated.

**Anchor: USWDS (US Web Design System).** Landmark structure on every page; heading levels respected; modal/dialog uses native `<dialog>` or proper ARIA modal pattern.

**Non-UI anchor: JSON Schema's own schemas** — schemas that describe data accurately and stay aligned with the implementation.

**What to look for:**

- Buttons are `<button>`, links are `<a>`, headings leveled correctly
- Form labels associated with inputs
- ARIA used to enhance, not patch
- Schemas/types match the runtime data shape

---

## 9. Accessibility — 5/5 anchor shapes

**Anchor: Radix Primitives.** Keyboard model exhaustive for every component; focus management on overlays correct; reduced-motion respected; screen-reader testing happens.

**Anchor: Reach UI (historical).** Made the case that accessibility is a _design constraint_, not a feature; every component shipped with documented keyboard model and ARIA contract.

**What to look for:**

- Every interactive element keyboard-reachable
- Focus order matches visual order
- Focus indicator visible and meets WCAG SC 2.4.11
- Color not the only signal for meaning
- `prefers-reduced-motion` respected
- Tests exercise keyboard paths

---

## 10. Performance Posture — 5/5 anchor shapes

**Anchor: Astro / Qwik.** Bundle size is a first-class concern; the framework choice itself reflects a performance budget. Bundle analysis runs in CI; regressions are caught at PR time.

**Anchor: PostgreSQL query planning.** Every hot path is profiled; query plans are stable; performance changes appear in release notes.

**What to look for:**

- Bundle size monitored (CI gate or routine check)
- Hot paths benchmarked or noted
- Async code uses cancellation/debouncing/batching where needed
- Memoization where measured to help, not speculatively
- Database queries reviewed for N+1

---

## 11. Test Posture — 5/5 anchor shapes

**Anchor: TanStack Router test suite.** Tests target behavior, not implementation; the suite catches real regressions without breaking on refactors. Tests run fast enough that developers actually run them.

**Anchor: SQLite's testing approach.** The test suite is the product; 99%+ branch coverage on the engine, with a stated rationale for what's not tested and why.

**What to look for:**

- Test pyramid is intentional (unit, integration, e2e in some ratio)
- Tests fail for the right reasons (refactor-friendly)
- Critical paths covered; trivial paths not over-covered
- What's NOT tested has a stated reason
- Tests run fast enough to actually be run (CI < 10 min, local < 1 min)

---

## How to Use This File During an Audit

In Wave 3 (Audit), each dimension's sub-agent prompt should include the relevant exemplar shapes from this file. The agent's framing becomes:

> "Compared to the {dimension} exemplar shape ({anchor}), the audited repo exhibits {observation}. This puts it at {n}/5 on the dimension because {gap or alignment with the exemplar's signals}."

This grounds scoring in shared anchors instead of agent-to-agent calibration drift.

## Limitations

- **Anchors evolve.** The exemplars named here are accurate as of this skill's authoring (2026-05-16). External projects change; before citing a specific behavior, verify the exemplar still exhibits the cited shape.
- **Anchors aren't universal.** A great Stripe-style API for a payments SDK isn't the right model for a state-management library. When the audited repo's type doesn't map to an anchor's domain, describe the underlying _property_ (predictable verb set, extensible signature) rather than the specific exemplar.
- **Team-specific anchors beat industry anchors.** A repo-specific fork of this skill (see `forking-for-your-repo.md`) should add in-repo exemplars — the team's own internal "this is what 5/5 looks like here" references with file:line citations. Industry anchors are the fallback when team anchors don't exist.
