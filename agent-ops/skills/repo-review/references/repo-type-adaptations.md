---
date: 2026-05-16
---

# Repo-Type Adaptations

The default 11-dimension rubric (`default-rubric.md`) is the starting point. Different repo types require different weights, dropped dimensions, or added dimensions. This file is the matrix.

If the discovery wave classifies the repo as a type listed here, use the adaptation. If it's "other" or "mixed", improvise from the closest match and document the deviation in `rubric.md`.

---

## Type 1 — Component/UI Framework

**Examples:** Web Components framework, React component library intended as a foundation, Vue component kit, a Lit-based primitive set.

**Distinguishing trait:** The repo's value is the API surface consumers build against. Internal cleanliness is secondary to API stability and discoverability.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | **high** | Sibling components must feel like siblings. |
| 2. Naming & Path Consistency | **high** | Discoverable surface. |
| 3. Abstraction Layering | **high** | Primitives → compositions invariant. |
| 4. Dependency Graph Health | medium | Cycles are still bad but less critical than API drift. |
| 5. Public Surface Discipline | **high** | The product IS the surface. |
| 6. DX | **high** | Consumers ARE developers. |
| 7. Framework Idiom Adherence | **high** | Working with Web Components / framework grain. |
| 8. Semantic Correctness | **high** | UI components must produce correct semantics. |
| 9. Accessibility | **high** | Non-negotiable for UI primitives. |
| 10. Performance Posture | medium | Important but consumer-dependent. |
| 11. Test Posture | medium | Critical paths tested; not 100%. |

**Add a dimension:** _Composability_ — do primitives compose, or do they fight each other? Cite the slot/children/prop interactions across sibling primitives.

---

## Type 2 — Application (web/mobile/desktop product)

**Examples:** SaaS web app, mobile client, electron app, shipping product surface.

**Distinguishing trait:** End users are the audience; the codebase serves features, not contracts.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | medium | Internal APIs; less critical than UI symmetry. |
| 2. Naming & Path Consistency | **high** | Onboarding new contributors. |
| 3. Abstraction Layering | medium | Pragmatism over purity. |
| 4. Dependency Graph Health | medium | Bundle size matters; cycles cause bugs. |
| 5. Public Surface Discipline | low | Mostly internal. |
| 6. DX | **high** | Speed-of-feature-delivery depends on it. |
| 7. Framework Idiom Adherence | **high** | Fight the framework, pay forever. |
| 8. Semantic Correctness | **high** | Product UI; matters for users + a11y + SEO. |
| 9. Accessibility | **high** | Real users depend on it. |
| 10. Performance Posture | **high** | Time-to-interactive, render budgets. |
| 11. Test Posture | medium | Critical user paths covered; not 100%. |

**Add a dimension:** _Observability_ — can production issues be diagnosed from logs/metrics, or does every bug require local reproduction? Cite logging conventions and error-reporting integration.

---

## Type 3 — Library (general-purpose, framework-agnostic)

**Examples:** Utility library, parser, validation library, ORM, algorithm package.

**Distinguishing trait:** Consumed by many unknown projects; small surface, deep value.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | **high** | Function signatures across the lib. |
| 2. Naming & Path Consistency | **high** | Reads like one author. |
| 3. Abstraction Layering | **high** | Internal layering for testability. |
| 4. Dependency Graph Health | **high** | Minimal deps is a feature. |
| 5. Public Surface Discipline | **high** | Breaking changes are expensive. |
| 6. DX | **high** | Docs, types, errors are the product. |
| 7. Framework Idiom Adherence | N/A | Often framework-free. |
| 8. Semantic Correctness | **high** | Schema/type correctness. |
| 9. Accessibility | N/A | Usually. |
| 10. Performance Posture | **high** | Consumed in hot paths often. |
| 11. Test Posture | **high** | Library safety net. |

**Add a dimension:** _Compatibility surface_ — what runtimes, languages, framework versions are supported, and is the support tested?

---

## Type 4 — CLI Tool

**Examples:** Build tool, dev utility, scaffolder, code-mod runner.

**Distinguishing trait:** Command-line ergonomics; argument design is the UI.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | medium | Subcommands should feel consistent. |
| 2. Naming & Path Consistency | **high** | Command/flag names. |
| 3. Abstraction Layering | medium |  |
| 4. Dependency Graph Health | medium |  |
| 5. Public Surface Discipline | **high** | CLI surface = public API. |
| 6. DX | **high** | Help text, errors, exit codes. |
| 7. Framework Idiom Adherence | medium | If using a CLI framework. |
| 8. Semantic Correctness | medium | Exit codes, signal handling. |
| 9. Accessibility | N/A | (CLI accessibility = terminal/screen-reader compat — usually N/A.) |
| 10. Performance Posture | medium | Startup time matters. |
| 11. Test Posture | **high** | Subprocess tests, regression suite. |

**Add a dimension:** _Composability_ — does this CLI compose with others (pipes, exit codes, machine-readable output)?

---

## Type 5 — API Service (backend)

**Examples:** REST API, GraphQL service, RPC server, webhook receiver.

**Distinguishing trait:** Network-facing; contracts matter; data integrity matters.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | **high** | Endpoint patterns, response shapes. |
| 2. Naming & Path Consistency | **high** | Route naming, handler naming. |
| 3. Abstraction Layering | **high** | Domain/app/infra separation. |
| 4. Dependency Graph Health | **high** |  |
| 5. Public Surface Discipline | **high** | API versioning, contract stability. |
| 6. DX | medium | Mostly internal devs. |
| 7. Framework Idiom Adherence | **high** |  |
| 8. Semantic Correctness | **high** | Schemas, status codes, idempotency. |
| 9. Accessibility | N/A |  |
| 10. Performance Posture | **high** | p99 latency, throughput. |
| 11. Test Posture | **high** | Contract tests, integration tests. |

**Add a dimension:** _Reliability posture_ — retries, idempotency, timeouts, circuit breakers, observability. _Security posture_ — auth/authz patterns, input validation, secrets handling.

---

## Type 6 — Infrastructure-as-Code

**Examples:** Terraform modules, Pulumi programs, Helm charts, Kubernetes manifests.

**Distinguishing trait:** Declarative; the "code" describes desired state; failures are operational.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | medium | Module input/output shape. |
| 2. Naming & Path Consistency | **high** | Resource naming. |
| 3. Abstraction Layering | medium | Module hierarchy. |
| 4. Dependency Graph Health | **high** | Resource dependencies. |
| 5. Public Surface Discipline | **high** | Module API stability. |
| 6. DX | **high** | Plan output legibility, error messages. |
| 7. Framework Idiom Adherence | **high** | Tool idiom. |
| 8. Semantic Correctness | **high** | Resource semantics. |
| 9. Accessibility | N/A |  |
| 10. Performance Posture | low | Plan/apply time mostly. |
| 11. Test Posture | medium | terratest, kitchen, etc. |

**Add a dimension:** _Blast radius discipline_ — staging vs. production isolation, state file management, destruction safety, drift detection.

---

## Type 7 — Design System (tokens + components + docs)

**Examples:** A multi-package design system: tokens, primitive components, composition recipes, documentation site.

**Distinguishing trait:** Cross-package coherence is the product.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | **high** |  |
| 2. Naming & Path Consistency | **high** | Token names especially. |
| 3. Abstraction Layering | **high** | Primitives → tokens → components → recipes. |
| 4. Dependency Graph Health | **high** | Cross-package deps. |
| 5. Public Surface Discipline | **high** | What's stable, what's experimental. |
| 6. DX | **high** | Adoption by app teams. |
| 7. Framework Idiom Adherence | **high** |  |
| 8. Semantic Correctness | **high** |  |
| 9. Accessibility | **high** |  |
| 10. Performance Posture | medium |  |
| 11. Test Posture | medium | Visual regression. |

**Add a dimension:** _Token discipline_ — primitive vs. semantic layers, alias hygiene, theme/scheme/density wiring (consider referencing a design-token audit's output).

**Note:** This is the area of overlap with a scoped component/design- system coherence audit and a declared-vs-implemented pattern gap analysis. If the engagement is purely design-system, prefer one of those narrower approaches. Use `repo-review` when the design system is one package of a larger repo, or when the review must also cover the docs site, build tooling, etc.

---

## Type 8 — Monorepo (mixed)

**Examples:** Turborepo / Nx / pnpm workspace with apps, libs, infrastructure all in one place.

**Distinguishing trait:** Heterogeneous; each package may be a different "type" above.

**Approach:**

1. In Wave 1, classify **each package** by type.
2. In Wave 2, build a rubric that uses **per-package weights** for each dimension.
3. In Wave 3, dispatch audit agents **per package per dimension** (or group small packages).
4. In Wave 4, the synthesizer must cluster findings across packages, not just within. Themes often emerge at the seams (e.g., "auth inconsistency between web app and API service").
5. Add a dimension: _Cross-package coherence_ — shared types, shared conventions, shared tooling.

**Caveat on scale:** A 100-package monorepo can't be exhaustively audited. Pick 5–10 representative packages with the engineer; sample the rest only for cross-package coherence.

---

## Type 9 — Generative / Agent / Prompt System

**Examples:** Repo containing MCP servers, skills, agent prompts, A2UI flows.

**Distinguishing trait:** Code is prose + schemas; correctness is behavioral, not type-checkable.

| Dimension | Weight | Notes |
| --- | --- | --- |
| 1. API Symmetry | **high** | Skill/tool signatures. |
| 2. Naming & Path Consistency | **high** |  |
| 3. Abstraction Layering | medium |  |
| 4. Dependency Graph Health | low |  |
| 5. Public Surface Discipline | **high** | Skill descriptions = public API. |
| 6. DX | **high** | Agent ergonomics; trigger accuracy. |
| 7. Framework Idiom Adherence | **high** | MCP/A2UI/skill conventions. |
| 8. Semantic Correctness | **high** | Schemas, protocols. |
| 9. Accessibility | N/A |  |
| 10. Performance Posture | low |  |
| 11. Test Posture | medium | Behavioral evals. |

**Add a dimension:** _Trigger discipline_ — skill/tool descriptions, trigger phrases, false-positive rates. _Prompt hygiene_ — versioning, prompt-as-code, evaluation harness presence.

---

## Type 10 — Other / Unknown

If discovery doesn't classify cleanly:

1. **Stop and ask the engineer.** "Here's what I found — does this match the closest type X, or is it a hybrid? I'll specialize the rubric accordingly."
2. **Default fallback:** Run the unweighted 11-dimension rubric. Drop dimensions only with explicit engineer confirmation.

---

## How to Apply These Adaptations

In Wave 2 (Rubric):

1. From Wave 1 discovery, identify the type.
2. Pull the weights and added/dropped dimensions from this file.
3. Generate `review/rubric.md` with the specialized weights.
4. **Present to engineer at HITL #1** with explicit framing: "Because this is a {type}, I've weighted X high and dropped Y. Confirm or adjust."

In Wave 3 (Audit): the dimension agents respect the weights via prioritization in their findings. A `high`-weight dimension's "blocker" finding is treated as more severe than a `medium`-weight dimension's "blocker" by Wave 4's synthesizer.

In Wave 4 (Synthesize): weights affect P0/P1 selection. A blocker in a low-weight dimension might be a P1, not a P0; a major in a high-weight dimension might be a P0.
