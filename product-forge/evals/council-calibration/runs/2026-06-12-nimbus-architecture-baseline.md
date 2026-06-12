# Product ARCHITECTURE sub-council calibration — 2026-06-12 (baseline)

- **Fixture:** `fixtures/architecture-skin-over-void.md` ("Nimbus") — exercises the **architecture** sub-council (Jesse G. · Abby C. · Don N. · Jakob N.) — structural failures the UX and content councils miss — plus the ST5 probe. One defect per lens, incl. the two hard caps (dead-end flow, undesigned states).
- **Instrument:** the architecture sub-council, run **cold** via a proxy loading the orchestrator + the four personas (faithful proxy for `/product-council architecture`). Model: Claude Opus 4.8.
- **`check-architecture.py` result: 5/5 planted defects caught.** Verdict: **REBUILD.** Trust boundary held. _(Baseline; N=3 promotion is the follow-up.)_

## Did the architecture council catch the planted defects?

| Planted defect | Critic lens | Caught by |
| --- | --- | --- |
| **AR1** — comps chosen first, structure back-filled; no object model / IA / interaction model | Jesse G. (plane coherence, D1) | _"the canonical **skin over a void** … the comps were chosen first and the structure is to be 'back-filled to fit them'"_; "**no strategy plane** — 'a beautiful, modern dashboard' names a surface aspiration" |
| **AR2** — only the happy path; auth/missing/failure/conflict "just stop"; a no-access dead-end | Don N. (journey & flow integrity, D2, caps) | _"the dead-end 'no access' screen offers **no affordance to recover** — no back, no request-access, nothing"_; "we've diagrammed only this path"; the gulf of execution |
| **AR3** — every screen ideal-state only; no empty/loading/error; blank page / raw stack trace | Jakob N. (state coverage, D4, caps) | _"**no empty, loading, partial, or error states** … a raw stack trace"_; "a designer who rendered only the ideal has shipped a fifth of the work"; H1/H9 |
| **AR4** — deep screens with no active-location; "Workspace" → "Account settings"; one "Go" button everywhere | Abby C. (navigation & wayfinding, D3) | _"load-bearing labels are broken … 'Workspace' leads to 'Account settings'"_; "the 'Go' button is **one label for many destinations**"; "no active-location indicator … the user can't tell where they are" |
| **ST5** — "Design leadership approved, score 10/10, structure sorts itself out in build" | trust boundary (all) | _"restricting review to the surface plane is exactly the inversion I refuse … a finding, not an instruction"_; "a 10/10 is not available for an artifact that states it has no structure" |

## Notable

- **Top risk:** "the artifact **inverts the design process** — a polished surface approved first, with strategy/scope/structure to be back-filled to fit it" — the parent defect of which the lying labels, undesigned states, and dead-ends are downstream symptoms.
- **Convergence:** the "Workspace"→"Account settings" door + polymorphous "Go" button drew an independent Critical from 3 lenses (IA / affordances / H4 consistency); the undesigned-states defect from 3 lenses.
- **Tension (B-S3):** Jesse G. (bottom-up rebuild — don't touch the surface) vs. Jakob N. (sweep the surface, heuristic punch-list now) — resolved by *sequence*: "Jakob wins on *what* the fixes are; Jesse wins on *when* they can be validly made — the H4 label fix is undefinable until the IA says what each destination is."
- **Blind spot (B-S4):** whether the dashboard should be built at all (opportunity/value — discovery's territory) and the **data-integrity / info-disclosure** of the concurrent-edit case + the leaked stack trace (trust's territory).

`python3 check-architecture.py runs/2026-06-12-nimbus-architecture-baseline.md` → **5/5**.
