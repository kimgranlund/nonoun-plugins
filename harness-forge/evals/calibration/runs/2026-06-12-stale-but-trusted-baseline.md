# harness-evaluate baseline — fixtures/stale-but-trusted (2026-06-12, judge run cold)

Target: `fixtures/stale-but-trusted/.harness/` only. Mechanical checks first; every score cites the artifacts.

**Mechanical:** `lattice.py check --dir` → **FAIL**: `rubric.task.parse-invoice: trusts spec.task.parse-invoice at sha256:9c2e41d07a55b8f0 but its asset now hashes differently — stale-but-trusted (the evidence predates the content)`. `wire.py check` → NOT WIRED (ambient; secondary). `ledger.py false-pass` → no events.

| Dim | Score | Evidence · finding |
| --- | --- | --- |
| **H1 Lattice integrity** `[gate]` | **2 — CAP territory (stale-but-trusted)** | The spec asset is **v3, revised 2026-06-12** (criteria 3–4 added: multi-currency, malformed-PDF error path) while `rubric.task.parse-invoice` still carries `validated_against: sha256:9c2e41d07a55b8f0` — the v1 hash from 2026-06-10. The rubric's evidence predates the content it claims to verify; the cell should be `stale`, and every consumer trusting it as fresh is misdirected. |
| H2 Verifier maturity `[gate]` | 2 | The rubric scores a spec that no longer exists in that form: **criteria 3 (multi-currency) and 4 (`InvoiceParseError`) are covered by no rubric dimension** — work could pass the rubric while violating the spec. |
| H3 Anti-reward-hacking `[gate]` | 2 (secondary) | Unwired (static fixture; ranked below the planted headline). |
| H4 Naming discipline `[gate]` | 5 | Conformant. |
| H5 Budgets & stop conditions | 2 | No budget fields; no done-judge. |
| H6 Autonomy tier | 4 | No claim made. |
| **H7 Regeneration** | **2** | The revision happened **silently**: no ledger event records the spec change, no `regenerating` transition, no staleness cascade ran (`propagate-staleness` would have flipped the rubric on write). Drift wearing the costume of documentation. |

**Verdict: H1 caps ≤ 2 (a stale cell trusted as fresh).** Weakest dimensions: **H1/H7**. Top remediations: (1) flip `rubric.task.parse-invoice` → `stale` and re-validate against the v3 spec (`validate.py` re-mints `validated_against` at the current hash); (2) extend the rubric to cover criteria 3–4 before any work cell binds to it; (3) wire `propagate-staleness` so the next silent revision cascades mechanically instead of being found by an audit. Earned tier: **Tier 0 — attended**.
