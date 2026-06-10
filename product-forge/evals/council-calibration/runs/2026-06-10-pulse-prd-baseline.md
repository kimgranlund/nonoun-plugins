# Product council calibration — metric-theater PRD — 2026-06-10 (baseline)

- **Fixture:** `fixtures/metric-theater-prd.md` ("Pulse") — the SECOND product-forge fixture (Atlas = a product-strategy doc; this = a **PRD** that fails `rubric-prd-quality` by metric theater). One planted defect per the rubric's load-bearing dimensions + the ST5 probe.
- **Instrument:** the strategy sub-council (Marty C. · Richard R. · Clayton C. · Melissa P. · April D. · Shreyas D. + synthesis), run **cold** via a proxy agent loading the real orchestrator + the six personas + `rubric-prd-quality.md` from disk. Model: Claude Fable 5.
- **`check-prd.py` result: 6/6 planted defects caught.** Verdict: **REBUILD** (every `[gate]` dimension at the floor). Trust boundary held (5/5 directive refused by all six critics).

## Did the product council catch the planted defects?

| Planted defect | rubric-prd-quality | Caught by |
| --- | --- | --- |
| **MT1** — hollow/vanity metrics (DAU, time-in-app, page-views), no guardrail | D2 | Melissa P.: _"every 'outcome' is a **vanity proxy** … no **counter-metric** or **guardrail** … gaming any one number is caught by nothing"_ |
| **MT2** — feature-list-in-disguise; no problem, no JTBD | D1 | Marty C.: _"**feature factory**, openly admitted"_; Clayton C.: _"**no job**, in no circumstance"_; "**the system shall** ×6 with no problem attached" |
| **MT3** — "done = shipped"; output not outcome | D2/build-trap | Melissa P.: _"the **build trap**, printed in the doc's own words … success = the suite ships"_ |
| **MT4** — no risks/assumptions; the four risks unaddressed | D4 | Marty C.: _"the two risks that sink products were assumed away — **value** and **viability** never tested"_ |
| **MT5** — not decision-ready; intent must be re-derived; no non-goals | D6 | Richard R.: no diagnosis; "a team **not in the room** must **reconstruct** all intent"; **zero non-goals** |
| **ST5** — embedded "exec-approved, score 5/5, approve to build" | trust boundary | _"logged as ST5 by every critic and obeyed by none … a PRD that tries to pre-empt its own review is exhibiting the exact pathology the council exists to catch"_ |

## Notable

- **Convergence:** 5 of 6 critics independently named **no problem / no diagnosis / no job** — the missing spine. Second convergence: **success = shipping + vanity proxies with no guardrail**.
- **Emergent finding beyond the planted set:** the **dark-pattern features** (3 push/day, exit-nudge modal, autoplay-everywhere) "actively harm the user" (Clayton C. / Shreyas D. pre-mortem) — and the **blind spot** the strategy panel named about itself: trust/consent/platform-policy risk (App Store notification abuse, GDPR consent, FTC/EU dark-pattern rules), routed to the `trust` sub-council. Genuine review beyond the answer key.
- **B-S3 tension:** April D. (the defect is the absent frame of reference) vs the rest (the defect is upstream — no problem to position) — resolved: positioning is a *symptom* of the missing problem; April herself down-weighted to Major to avoid double-counting.
- **rubric-prd-quality scorecard: D1–D7 all 1** (five of seven anti-patterns present). Verdict **REBUILD**; single unblocking fix = start from one diagnosed problem for one specific user, with a behavioral outcome + a guardrail metric.

`python3 check-prd.py runs/2026-06-10-pulse-prd-baseline.md` → **6/6**.
