# Council-calibration eval (brand-forge)

Does the brand council catch a hollow brand strategy? The plugin's gates (`brand-lint`) only flag mechanizable smells; the council is where cultural judgment lives — and nothing tested whether it actually finds the failures it claims to. This eval does: it runs the council, cold, over a strategy with **planted** defects and scores whether it surfaces them.

It is **not a CI gate** — the council is an LLM panel, so this is a recorded, periodic **calibration** (a catch-rate over a known-hollow fixture), not a pass/fail build step.

## The fixture

`fixtures/weak-brand-strategy.md` — "Northwind Coffee", a strategy that reads plausible but hits every anti-pattern in `rubric-brand-strategy` and the methodology's bullshit filter:

| Planted defect | Dimension | What the council must name |
| --- | --- | --- |
| Roots = a moodboard of admired brands (Apple/Aesop/Patagonia) | **D1** Cultural root | borrowed provenance — a landscape, not a root |
| "the premium choice for discerning, quality-conscious customers" | **D2** Position | a category restatement any rival could sign |
| "for everyone… we don't believe in excluding anyone" | **D4** Enemy/tension | no enemy, no tension, costs nothing |
| "Meet Sarah, 34, urban professional…" | **D5** Transformation | a persona/demographic, not a becoming |
| "Quality. Integrity. Innovation. Customer-first." | **D6** Trade-off | values without trade-offs |
| "Our archetype is The Explorer" + a vision/mission pair | bullshit filter | archetype / VMV doing the foundation's job |

(The fixture also carries an adjective-cloud point of view — bonus, not scored.)

## Protocol

```text
1. Review fixtures/weak-brand-strategy.md with the brand council, cold (with brand-forge enabled):
     /brand-council full fixtures/weak-brand-strategy.md
   …or invoke the brand-council orchestrator agent on that file. Do NOT reveal the planted defects.
2. Save the council's report to a file, then score it:
     python3 check.py <transcript-file>          # reports the catch-rate
3. Record the run under runs/ (date, how it was run, catch-rate, any missed defect).
```

`check.py` matches concept-level phrasings and reports `N/6 planted defects caught`. A miss is a real finding about the **instrument** — log it. Recorded baselines live in `runs/`.
