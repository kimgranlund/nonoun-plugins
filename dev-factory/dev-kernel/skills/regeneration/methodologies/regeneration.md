# Regeneration — the loop that converges the definition

`Cell: methodology.system.regeneration · Status: defined · Register: established lineage (event-sourcing / CQRS read-model regeneration, pattern-language distillation, retrospective-to-action loops, self-improving agent loops); the lattice-feedback-to-spec morphism is the substrate-engineering corpus`

## Why this cell exists

Loop engineering reliably converges a single task against a *fixed* verifier — but the spec, rubric, knowledge, and permissions are authored by hand and frozen, so a team accumulates outputs, not a sharpening substrate (TDD §2, Failure 1). The root cause is that the artifacts defining the work are not in the loop. Regeneration puts them in the loop: it reads the ledger — the veridical record of what the factory actually did — and feeds that evidence back up, into reusable patterns and into revision proposals against the definitions themselves. This is the organ that earns the word "self-improving."

## The loop

```
  operate ──▶ ledger ──▶ distill ──▶ patterns ──▶ upstream
     │          │           │            │            │
  cells run  every       compress     reusable    revision
  the engine  event,     signal-      shapes &    PROPOSALS
  & emit      with a     bearing      anti-       against spec/
  signals     rationale  precedent    patterns    rubric cells
     ▲                                                  │
     └──────── ledgered `regenerating` transition ──────┘
              (policy-gated merge; then propagate-staleness)
```

Each arrow is a discipline:

- **operate → ledger.** Every engine pass, signal, block, and incident terminates in an append-only ledger entry carrying a **rationale** — the *why*. A record without a rationale is useless for regeneration, because the next iteration will not have this context window (`ledger.py` enforces the non-empty rationale on append; see `../references/provenance-rules.md`). No silent work: if it happened, it is in the ledger.
- **ledger → distill.** `pattern-distiller` reads a ledger window (`bin/ledger.py read`/`tail`) and compresses recurring signal-bearing precedent into pattern cells. Distillation sits *last in the partial order*: a pattern with no operation behind it is a hypothesis, not a pattern.
- **distill → patterns.** Each pattern names its context, forces, solution shape (or failure mechanism), consequences, and the ledger entries it was distilled from. Indexed on the *problem context* so it is actually retrieved later — a corpus that grows but is never retrieved is pattern hoarding.
- **patterns → upstream.** `spec-regenerator` turns ledger deltas + patterns into revision **proposals** against spec/rubric cells. Proposals only — the merge is policy-gated.
- **upstream → operate (the feedback edge).** A merged revision re-enters the cell at `regenerating` through a *ledgered transition*; `propagate-staleness` flips every dependent to `stale`; the next loop runs against the sharper definition. The cell's identity never changes (renaming on a state change is a drift generator); only its maturity Property and content move.

## The distill step

1. **Read the window.** `bin/ledger.py read --cell C` / `tail -n N` — the recent events, with their results and rationale. The ledger is the source of truth; never re-summarize a run from memory.
2. **Cluster.** Group events by recurring shape — same solution working across contexts (a pattern), same failure signature recurring (`bin/ledger.py no-progress` detects the N-identical case in code, not by counting).
3. **Distill, with provenance.** Write the pattern cell: context, forces, shape, consequences, and the ledger refs it came from. No provenance → do not write it.
4. **Invert.** A recurring failure, captured with its mechanism and corrective, is often higher-leverage than a success — and a failure-mode catalogue *is* a rubric in disguise (each anti-pattern becomes a "does the candidate exhibit X?" dimension). Write the anti-pattern *and* flag the rubric dimension it implies for the rubric-architect.

## The regenerate step

1. **Find the responsible cell.** From a ledger delta (a cluster of runs exposing a definitional weakness) plus the distilled patterns, identify *which* spec or rubric cell was actually wrong — not merely correlated.
2. **Draft the proposal.** A concrete diff against the cell, the `regenerating` transition it requires, and the ledger evidence that motivates it. "The spec was wrong" is not a proposal; the evidence-plus-diff-plus-transition is.
3. **Re-earn validation.** A regenerated spec clears spec-quality again; a regenerated rubric clears rubric-quality *and re-calibrates* (its agreement measurement went stale the moment it changed). Never grandfather a revision to `validated` on prose.
4. **Propose, do not merge.** Hand the proposal to the policy-gated merge (a human or a high-tier policy decides — OD-006). After merge, the cell re-enters `regenerating` and `propagate-staleness` cascades.

## Where computation routes to code

- **Reading the window** — `ledger.py read`/`tail`.
- **No-progress** (the repeated-failure-signature that becomes an anti-pattern and a block) — `ledger.py no-progress`, in code.
- **False-pass** evidence for a rubric revision — `ledger.py false_pass_rate`, which is `unmeasured` until a refuter disagreed. A proposal cannot claim a verifier is unsafe on an unmeasured rate.
- **Staleness propagation** after a merge — `propagate-staleness`, a deterministic hook, never the agent flipping cells.

The judgment — which precedent is a pattern, which delta implies a revision, whether a decomposition was wrong — is the agents'. The bookkeeping is the bins.

## Regeneration failure modes

A pattern with no provenance (untraceable, unfalsifiable — pattern hoarding). Distilling only successes and no anti-patterns (the failure modes are the higher-leverage seam, and the rubric dimensions they imply go un-flagged). A revision proposal motivated by opinion instead of ledger evidence ("the spec feels wrong"). Silently editing a validated spec/rubric instead of proposing a ledgered `regenerating` transition (the canonical drift). Grandfathering a regenerated definition to `validated` on prose without re-grading and re-calibrating. Claiming a verifier is unsafe on a false-pass rate that was never measured (it is `unmeasured`). The regenerator merging its own proposal (the policy gate exists to prevent it).
