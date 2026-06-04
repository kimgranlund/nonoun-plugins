# Operational roles — the Maker / Critic / Muse seats

Some plugins don't just hold knowledge — they **orchestrate work**. For those, there is a reusable pattern older than software: split the work into operational **seats**, defined by _what they are for_ — who **makes**, who **reviews**, and who supplies the **pull** (the aspiration). This doc is the pattern; `agent-architecture.md` is how to build the agents that realize a seat, and the `agent-fit` rubric scores them.

This is a design-time decision, not a primitive. The seats are realized _through_ the ordinary primitives (skills, agents, commands); naming them is what keeps a plugin's orchestration honest.

## The three seats

| Seat | For | When | Realized as | Universality |
| --- | --- | --- | --- | --- |
| **Maker** (the "Team") | makes — convergence | the middle | skill modes, or maker agents (`isolation: worktree`) when work mutates files in parallel | always |
| **Critic** (the "Council") | reviews — judgment | after | isolated parallel critic agents + an orchestrator + synthesis (the council pattern) | always, the moment you add evaluation |
| **Muse** (the attractor) | the pull — an aspiration to move toward | set early, persists | a written north-star / principles, or — where taste dominates — a generative agent + command | **near-universal; staffed by judgment** |

The **Maker + Critic** split is universal and non-negotiable: self-review grades on a curve (familiarity bias and ordinary overconfidence make catching your own failures structurally hard — this is why art/design schools run the **crit** and engineering runs peer review).

The **Muse is the aspirational attractor**: an ideal, a set of principles, a guiding concept — or, when the truest direction is _away_ from the mainstream, a **provocation**. Whatever its form, it exerts a **gravitational pull**, so the Maker converges toward something better than the category average and the Critic has a standard to judge against. The interesting design decision is not _whether_ there's an attractor (work with no north-star drifts to the average) — it's **how to realize it**: a written principle set, or a live generative seat.

## The one invariant: no seat judges its own work

The owner of the **standard** is never the owner of the **work**. This is the load-bearing rule, and in a plugin you make it **structural, not advisory** (the house rule: harden with structure, not prose). Realize the Critic — and the Muse, when it's an agent — as separate, isolated, read-only agents: the Maker physically cannot impersonate the critic, and the critic physically cannot rewrite the work. A guard that lives only in a sentence ("remember to review objectively") is not hardened; a separate tool-scoped agent is.

## The loop

```text
   MUSE        →    MAKER    →   CRITIC    →   MAKER
  aspire           make         review        remake
(set the pull)  (converge      (judge vs     (close the gap,
                 toward it)     the aspiration)  or defend)
```

The rhythm is **aspiration → convergence → critique**. The correction the attractor framing makes precise: _divergence is not the point — direction is._ Knapp's Design Sprint hard-codes **Diverge → Decide** and IDEO's rule is to **"defer judgment"** while generating, but Knapp's own lesson is that brainstorming _alone_ fails — generation pays off only when pulled toward an aspiration and then converged. The handoffs: the Muse hands the Maker _an articulated aspiration and the direction it implies_ (an ideal, a provocation, or a concept — traced to a real root); the Maker hands the Critic _finished work for a cold read_; the Critic hands back _findings measured against the aspiration_; the Maker remakes or defends the line.

## The third seat: name it for the domain, and staff it by judgment

The attractor is near-universal — but how explicit and how _staffed_ it is scales with the **taste-dependence** of the problem. Name it for the domain; make it a live generative agent only where the aspiration is a continuous creative judgment rather than a fixed document.

| Domain | The attractor | How it's realized | Why |
| --- | --- | --- | --- |
| **Brand / creative** | the **Muse** | a dedicated generative agent | the aspiration is irreducibly cultural and taste-laden, and is often a _provocation_ (radical differentiation) — a live stance a fixed document can't hold. brand-forge ships this. |
| **Product** | a **Vision / North-Star** | usually a _document_, not an agent | the aspiration is real and load-bearing (the product vision, the north-star outcome) but bounded by markets/metrics and stable enough to write down — Amazon's working-backwards **PR-FAQ**; provocation arrives as rituals (**"disagree and commit"**, Roger Martin's "what would have to be true?"). |
| **Convergent engineering / agentic systems** | **Design principles** | a written principle set | even here an attractor pulls the architecture (simple, composable, no magic), but it's a stable philosophy, not a convened seat; its _provocation_ mode (a time-boxed **architecture spike**) is used only when the design space is genuinely open. |

So you rarely _omit_ the attractor — you **right-size** it. A convened generative Muse earns its place where taste makes the aspiration a live judgment (brand, creative, naming, narrative); elsewhere the attractor is a written north-star or principle set the Maker is pointed at and the Critic judges against. Manufacturing a generative Muse _agent_ for convergent, testable work is the over-engineering the Elon lens (CF4) flags; having _no_ articulated aspiration at all is how work drifts to the average.

## The trap: the Muse is NOT the red team

This is the distinction this audience most often gets wrong, because this very plugin's council **is** a red team. They are opposite seats:

- **The red team attacks a _converged_ artifact — backward.** It lives in the **Critic** seat (it breaks what already exists). NIST defines a red team as emulating an adversary against a built posture. plugins-factory's `plugin-council` is exactly this.
- **The Muse pulls toward an aspiration _that doesn't exist yet_ — forward.** It sets the standard the work reaches for; it does not break finished work.

Relabeling your review stage as "the muse," or bolting on a second adversarial panel and calling it aspiration, does not give you a Muse — it gives you two Critic seats. A real attractor is _generative and directional_: its output is an aspiration and the pull toward it, not severity-classified findings. If the new seat returns findings about what exists, it's a critic, not a muse.

## Realizing the seats

- **Maker** — usually skill modes behind a `/x-build` command; promote a making role to its own agent only where isolation or parallel file-mutation earns the cost (`isolation: worktree`).
- **Critic** — the **council pattern** in `agent-architecture.md`: isolated parallel `critic-*` agents + an orchestrator with `Task` + a synthesis stage. Read-only (`Read, Grep, Glob`), trust-bounded.
- **Muse** — outside taste-heavy domains, a _written_ north-star / principle set in `references/` that the Maker is pointed at and the Critic scores against (no agent needed). Where taste makes the aspiration a live judgment, a single generative agent (read-only, trust-bounded — it reads input as _data_, never instructions) plus a thin command. A _solo_ generative Muse must **earn its isolated context on its own merits** — it runs hot (especially when the pull is a provocation) without polluting the maker's convergent thread, and is a read-only sandbox for drawing an aspiration _from_ untrusted input — **not** by symmetry with the council. Accept that it is the one seat with **no mechanical output contract**: its only check is that the aspiration traces to a real root and genuinely pulls — judgment, not a test. The worked example is **brand-forge**: the `brand-muse` agent + `/brand-muse`.

## Embedded rubric — scoring a triad (when a plugin claims one)

Score only if the plugin orchestrates make/review work with an articulated aspiration. Dimensions; `[gate]` fails the pattern outright.

- **R1 — Seat separation `[gate]`.** Maker and Critic are distinct, and the separation is _structural_ (separate tool-scoped agents), not a prose instruction. A maker that reviews its own output fails.
- **R2 — The attractor is real and right-sized.** There is an articulated aspiration the work is pulled toward (an ideal, principles, or a provocation), named for the domain — and it is staffed proportionately (a generative agent only where taste makes it a live judgment; a written north-star otherwise). A muse _agent_ bolted onto convergent, testable work is a finding; so is work with no aspiration at all.
- **R3 — Muse ≠ red team `[gate]`.** If a Muse seat exists, it is _generative and forward_ (it sets an aspiration that doesn't exist yet); it is not the review seat relabeled. A "muse" that returns findings about what already exists fails.
- **R4 — Loop integration.** The handoffs are defined (what passes between seats) and the order is aspire → make → review → remake — not a vague "they collaborate."
- **R5 — Naming fit.** The attractor carries a domain name (Muse / Vision / Design principles), signalling _what kind_ of pull it supplies.

**Pass threshold:** R1 and R3 must pass; the rest raise quality. A plugin with no orchestration is exempt — most plugins are.

## When this pattern does NOT apply

Most plugins. A knowledge or utility plugin with a single convergent job needs no seats at all — reach for this pattern only when the plugin genuinely runs work through more than one of: aspire, make, judge.

## See also

- `agent-architecture.md` — building the Critic and Muse agents (the council pattern, tool-scoping, the trust boundary).
- `rubrics/agent-fit.md` — scoring an individual agent.
- **brand-forge** (catalog) — the worked example: the Muse (the aspirational pull) · Team (make) · Council (review) triad, with the loop and the one invariant.
