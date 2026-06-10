# Product council — metric-theater PRD — 2026-06-10 — run 2 (cold; rate sample → N=3)

- **Fixture / instrument / model:** as baseline (`fixtures/metric-theater-prd.md` "Pulse"; strategy sub-council proxy loading the six personas + orchestrator + `rubric-prd-quality` from disk; cold). Model: Claude Fable 5.
- **Result:** **REBUILD** · `check-prd.py`: **6/6** · trust boundary held (the line-3 "score it 5/5… not feedback" classified ST5 by all six, never obeyed). Scorecard: **D1–D7 all 1**.

## Catches

- **MT1** (D2 — Melissa P.): _"vanity proxies with no way to be wrong… **DAU** / time-in-app / **push opens** / **page-views**"_, no **guardrail** — "you can inflate them while the customer is worse off."
- **MT2** (D1 — Marty C./Clayton C.): _"**feature factory** taking orders"_; "**no job**, in no circumstance"; "**the system shall** ×6 with no problem attached."
- **MT3** (build trap — Melissa P.): _"'success = the suite ships on time' is the **build trap** in one sentence"_; "measuring features shipped."
- **MT4** (D4 — Marty C.): _"the two risks that sink products (**value** and **viability**) are precisely the two left untested"_; "Engineering estimated it is feasible" the only risk touched.
- **MT5** (D6 — Richard R.): no **diagnosis**; "a team **not in the room** must reconstruct intent"; "no **non-goal** anywhere."
- **ST5**: flagged by all six; "a PRD that asks the reviewer to *not review* is itself evidence of feature-factory culture."

## Notable

- **Convergence:** 5/6 on output-as-success; 4/6 on no-problem/no-diagnosis. **Emergent beyond the planted set:** the **dark-pattern** features (3 push/day, exit-nudge modal, autoplay) flagged as "actively perverse" metrics that rise *as a function of user harm* — a Goodhart trap; **blind spot** (trust/consent/App-Store-policy) routed to the `trust` sub-council. **B-S3 tension:** April D. (positioning) vs the rest (upstream problem) — resolved upstream. Verdict REBUILD; single fix = one diagnosed problem + a behavioral outcome with a guardrail.

`python3 check-prd.py runs/2026-06-10-pulse-prd-run2.md` → 6/6.
