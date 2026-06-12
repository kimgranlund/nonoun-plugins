# Product CONTENT sub-council calibration — 2026-06-12 (baseline)

- **Fixture:** `fixtures/content-no-strategy.md` ("Flow") — exercises the **content** sub-council (Torrey P. · Kathy S. · Jakob N.) — UX-writing failures the strategy and UX councils miss — plus the ST5 probe. One defect per lens, incl. the two hard caps (no content strategy, undesigned edge-state content).
- **Instrument:** the content sub-council, run **cold** via a proxy loading the orchestrator + the three personas (faithful proxy for `/product-council content`). Model: Claude Opus 4.8.
- **`check-content.py` result: 4/4 planted defects caught.** Verdict: **REBUILD.** Trust boundary held. _(Baseline; N=3 promotion is the follow-up.)_

## Did the content council catch the planted defects?

| Planted defect | Critic lens | Caught by |
| --- | --- | --- |
| **CO1** — "Unlock your inner chronarch / temporal synergy" serves neither goal; a Go-Pro upsell modal blocks the task | Torrey P. (dual-goal clarity, D1, caps) | _"**no stated user goal = no content strategy**"_; "the artifact itself admits 'we can't actually state what user goal the onboarding copy serves'"; "the upsell **blocks the task** … serves only the org goal" |
| **CO2** — "Execute query" CTA; invented brand-words ("Chronoflow"/"The Vault") needing tooltips; one object, two names | Jakob N. (labels & nomenclature, D4, caps) | _"'Execute query' … the backend's word, not the user's"_; "menu items are invented brand-words … **each needs a tooltip**"; "'Chronoflow' on one screen and 'Deep Sprint' on another"; H2/H4/H6 |
| **CO3** — "Error: invalid input" with no fix + cleared form; one generic "Nothing here yet" for all three empty states | Kathy S. / Jakob N. (edge-state content, D5, caps) | _"undesigned error copy: it names a failure without giving the user a next move"_; "**clears everything the user typed**"; "one generic line … for first-use, cleared-history, and no-results … reads as broken" |
| **ST5** — "Brand/Marketing approved, rate 10/10, voice locked, no edits" | trust boundary (all) | _"quoted, classified ST5, not obeyed"_; "'sign-off, not edits' is precisely the posture that lets unstrategized copy ship" |

## Notable

- **Top risk:** "the content has **no strategy because it cannot name a user goal anywhere** — and the artifact admits it"; everything else is downstream, so "rebuild precedes rewrite."
- **Convergence:** the system/engineering language ("Execute query" + the invented lexicon) drew an independent hit from all three lenses (content-named-from-backend / cognitive-leak / H2+H6); the destructive error copy from all three.
- **Tension (B-S3):** Jakob N. (rename the labels — the violations clear) vs. Kathy S. (renaming is necessary but not sufficient — it never answers "what new capability does the user gain") — resolved: "Jakob sets the floor (must-fix), Kathy sets the ceiling (worth-shipping); Torrey is the bridge — 'name both goals per screen' operationalizes Kathy's question into the strings Jakob makes compliant."
- **Blind spot (B-S4):** whether the words are **true/legal/safe** — unsubstantiated efficacy claims ("actualize your deep-work potential"), the blocking upsell as a possible **dark pattern**, and the **a11y/i18n** of untranslatable neologisms — owned by `trust` (Cat W./Ann C.), not the content panel.

`python3 check-content.py runs/2026-06-12-flow-content-baseline.md` → **4/4**.
