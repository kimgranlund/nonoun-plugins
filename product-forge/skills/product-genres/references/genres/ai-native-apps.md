---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Andreessen Horowitz, 'Good news: AI Will Eat Application Software'. https://a16z.com/good-news-ai-will-eat-application-software/ — the thin-wrapper-vs-moat / system-of-record argument"
  - "Hamel Husain, 'Your AI Product Needs Evals'. https://hamel.dev/blog/posts/evals/ — eval-driven development and error analysis"
  - "Hamel Husain, 'Creating a LLM-as-a-Judge That Drives Business Results'. https://hamel.dev/blog/posts/llm-judge/"
  - "Andrej Karpathy, 'Vibe coding MenuGen'. https://karpathy.bearblog.dev/vibe-coding-menugen/ — the prototype-to-production gap"
  - "Simon Willison, 'How I use LLMs to help me write code' and prompt-engineering writing. https://simonw.substack.com/p/how-i-use-llms-to-help-me-write-code ; https://simonwillison.net/tags/prompt-engineering/"
  - "Lenny's Newsletter, 'Beyond vibe checks: A PM's complete guide to evals'. https://www.lennysnewsletter.com/p/beyond-vibe-checks-a-pms-complete"
---

# AI-native apps

AI-native apps are products whose **core value depends on a model's capability** — the model is not a feature bolted onto a conventional app but the thing the product is built around. The category is young, moving fast, and short on settled benchmarks, so this file is more observational than the others: where a claim is emerging consensus rather than established fact, or rests on a single source, it is **labeled as such**. The defining property is that the product's quality is **probabilistic and non-deterministic** — the same input can yield different outputs, quality is a distribution rather than a guarantee, and the underlying model can change beneath you. That single fact reshapes how these products are designed, tested, costed, and defended. This reference covers the conventions that follow (capability-led design, eval-driven development, doing the simplest thing that works), the constraints that are unusually hard product limits here (cost and latency), and the question that hangs over the whole category: when is an AI app a real product versus a thin wrapper around someone else's model.

> The one-line frame (emerging consensus): an AI-native product's edge is **not the model** — frontier models are a rented, rapidly-commoditizing input — but the **evals, data, and workflow embedding around it.** "Better models don't make the application layer thinner: they make it more capable, because the hard part was never raw intelligence" (a16z).

## Conventions: what these apps tend to share

These are observed regularities across the current generation of AI-native products, not a settled canon.

- **Model-capability-led design.** What the product can credibly do is bounded by what the model can do _reliably enough_, so design starts from capability and works back to UX — the inverse of conventional design, which starts from the desired UX. New model capabilities open new product surface; model weaknesses (hallucination, brittleness) define the guardrails.
- **Eval-driven development.** Because output quality is a non-deterministic distribution, you cannot verify by example the way deterministic software is verified. The emerging discipline is to build **evals** — systematic, repeatable measurements of output quality — as first-class infrastructure. Hamel Husain's widely-cited claim: unsuccessful LLM products "almost always share a common root cause: a failure to create robust evaluation systems" (Husain). Evals are to AI-native apps what unit tests are to conventional software, and Lenny's guide frames them as the hidden lever behind exceptional AI products (Lenny / evals guide).
- **Human-in-the-loop and graceful degradation.** Mature AI products design for the model being wrong: confidence signals, easy correction, undo, citations/sources, and fallbacks to a deterministic path. The UX assumes a distribution of quality, not a guarantee.
- **Prompt + context as a managed surface.** The prompt, retrieved context, and tool definitions are product artifacts that are versioned, tested against evals, and iterated. Willison's repeated practical advice: examples in the prompt are "the #1 thing" because few-shot examples work so well (Willison, prompt-engineering writing).
- **Cost and latency as visible product constraints.** Unlike conventional software where marginal compute is ~free, every model call has real per-token cost and real latency, and both are felt directly in the product (see Constraints).

## Signature patterns

- **Do the simple thing that works first.** Strong practitioner consensus (not a hard finding): start with the simplest mechanism that clears the bar — a good prompt with examples and retrieval — before reaching for fine-tuning, agents, or bespoke models. Willison's framing is that examples in the prompt outperform most elaboration; the discipline is to add complexity only when an eval shows the simple thing falling short (Willison; widely echoed). The anti-pattern is reaching for the most sophisticated technique before measuring whether the boring one suffices.
- **Error analysis → write an eval.** Husain's core loop: look at real failures, categorize the kinds of error, and for each recurring kind write a test/eval that catches it — turning anecdotes into a regression suite (Husain). "Look at your data" is the recurring refrain.
- **LLM-as-judge, used carefully.** For outputs too open-ended to grade by exact match, use a model to grade against a rubric — but Husain warns against arbitrary 1–5 scales (different judges interpret them differently); prefer concrete binary or criterion-anchored judgments validated against human labels (Husain, LLM-judge).
- **Routing and caching for cost/latency.** Route easy queries to cheaper/faster models, cache repeated calls, and reserve frontier models for the hard cases — an emerging operational pattern (gateways like Helicone/Portkey are commonly cited; single-source / vendor-adjacent, treat as illustrative).
- **The deterministic shell around the probabilistic core.** Wrap the model in conventional, testable software (validation, schemas, retries, guardrails) so the non-deterministic part is contained and the surrounding system stays predictable.

## Key metrics

AI-native metrics layer **quality, cost, and latency** on top of the usual product/retention metrics — because here, quality is measured (not assumed) and unit economics are model-driven.

| Metric | What it measures | Why it matters here |
| --- | --- | --- |
| **Eval pass rate / quality score** | Output quality against a maintained eval set | The closest thing the genre has to a correctness metric; the spine of eval-driven development (Husain). Observe: it is only as good as the eval set behind it |
| **Cost per query / per task / per active user** | Model spend per unit of value delivered | A real, variable COGS that scales with usage — can invert the unit economics of a conventional-looking app (see Constraints) |
| **Latency (p50 / p95 time-to-response)** | How long the user waits for model output | A direct UX and abandonment driver; often the hardest product constraint to hide |
| **Containment / deflection or task-completion rate** | Share of tasks the AI completes without human fallback (support, agents) | The operational value metric for assistant/agent products; high containment with low quality is a trap |
| **Retention / engagement (the usual)** | Whether users come back and the product embeds | Novelty inflates early AI metrics severely; the durable signal is still the flattening cohort curve (see `genre-metrics-map.md`) |

A reusable rule: **if you can't measure output quality with an eval, you are flying blind** — and shipping prompt changes on vibes. Cost and latency must be tracked _per unit of value_, not just in aggregate, because they scale with use in a way conventional software's compute does not.

## Pitfalls

- **The demo-to-production cliff.** The genre's signature failure, documented first-hand by Karpathy on his MenuGen project: vibe-coding the local demo was "an exhilarating and fun escapade," but turning it into a deployed, real app was "a bit of a painful slog" — auth, billing, reliability, edge cases (Karpathy). The polished demo radically understates the distance to a dependable product; non-determinism makes that last mile harder, not optional.
- **Shipping on vibes (no evals).** Iterating prompts by eyeballing a few outputs, with no systematic measurement, so quality silently regresses and nobody can tell whether a change helped — the root cause Husain attributes to most failed LLM products (Husain).
- **Over-engineering past the simple thing.** Reaching for fine-tuning, multi-agent orchestration, or a custom model before an eval shows a good prompt + retrieval falling short — sophistication as procrastination from measuring (practitioner consensus; Willison).
- **Ignoring cost/latency until production.** Designing a flow that is delightful in a demo but, at scale, either too slow to use or too expensive to sustain. These are product constraints, not infra afterthoughts (see Constraints).
- **Mistaking model capability for product.** Building a thin pass-through to a frontier model with no proprietary data, workflow, or eval edge — the wrapper trap below.
- **Novelty mistaken for retention.** Early AI products draw curious one-time users; a signup/usage spike that decays is novelty, not product-market fit (see `genre-metrics-map.md`).
- **Treating model output as trusted/instruction-grade by default.** Feeding untrusted retrieved or user content straight into a privileged action path invites prompt injection; the genre needs the same untrusted-data discipline as any input-handling system (emerging security consensus).

## Cost and latency as product constraints

Conventional software treats marginal compute as effectively free; AI-native apps cannot. **Every model call has a real per-token cost and real latency**, and both are felt directly by the user and the P&L:

- **Cost is a variable COGS that scales with usage.** Heavy users cost real money on every interaction, which can invert the economics of a product that _looks_ like conventional SaaS — a flat subscription over a usage-priced model is a margin trap if a power user's query volume outruns their fee. This pushes AI-native pricing toward usage-based or hybrid models and makes "cost per active user" a first-class metric, not a footnote.
- **Latency is an abandonment driver you often can't hide.** Model inference is slow relative to a database read; a multi-second wait that would be unacceptable in conventional UI is routine here, which is why streaming responses, optimistic UI, smaller/faster models for easy cases, and caching are standard mitigations. Latency frequently constrains _what the product can be_ — some otherwise-good designs are infeasible because they'd be too slow to feel responsive.

The product consequence: cost and latency belong in the design conversation from the start, traded against quality. "Use a bigger model" is not a free quality lever — it spends both budget and milliseconds, and the right design routes the cheapest/fastest mechanism that clears the eval bar to each case (emerging operational consensus).

## The wrapper-vs-product question (the genre's defining debate)

The category's central question: when is an AI-native app a durable **product**, and when is it a **thin wrapper** around a model anyone can call — destined to be eaten when the model provider or a rival ships the same feature? This is genuinely contested and fast-moving; the framing below is a16z's and is widely cited, but is an investment thesis, not a settled law — labeled accordingly.

a16z's position ("Good news: AI Will Eat Application Software"): products that are "thin wrappers around commodity functionality" doing little beyond presenting model output _are_ vulnerable, but durable AI applications build moats that the model layer doesn't erode (a16z):

- **System of record / workflow embedding** — "perhaps the strongest moat." Apps deeply woven into an organization's workflow are nearly impossible to rip out; crucially, "better models don't make the application layer thinner: they make it more capable, because the hard part was never raw intelligence" (a16z).
- **Proprietary data and feedback loops** — exclusive data the model alone can't supply (a16z cites Bloomberg's market data, Abridge's clinical conversations) that compounds: more usage → better product → more usage.
- **Network effects, brand, and switching costs** — the conventional moats, which still apply.

The practical product test (synthesizing a16z + the eval discipline): **strip the frontier model out and ask what's left.** A product is more than a wrapper to the degree it owns (a) a proprietary data / feedback loop, (b) deep workflow embedding / a system of record, and (c) an eval and quality edge competitors can't trivially copy. If the only asset is "we call the model with a nice UI," a better model or the provider itself can replicate it — that's the wrapper trap. The optimistic reading, and a16z's, is that the model is a _rented, commoditizing input_ and the enduring value lives in the workflow, data, and quality discipline built around it (a16z; emerging consensus, not settled).
