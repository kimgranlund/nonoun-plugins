# Operational roles — the Maker / Critic / Provocateur seats

Some plugins don't just hold knowledge — they **orchestrate work**. For those, there is a reusable pattern older than software: split the work into operational **seats**, defined by _when_ they act and _what they are for_ — who **makes**, who **reviews**, and (sometimes) who **provokes**. This doc is the pattern; `agent-architecture.md` is how to build the agents that realize a seat, and the `agent-fit` rubric scores them.

This is a design-time decision, not a primitive. The seats are realized _through_ the ordinary primitives (skills, agents, commands); naming them is what keeps a plugin's orchestration honest.

## The three seats

| Seat | Verb | When | Realized as | Universality |
| --- | --- | --- | --- | --- |
| **Maker** (the "Team") | makes | the middle | skill modes, or maker agents (`isolation: worktree`) when work mutates files in parallel | always |
| **Critic** (the "Council") | reviews | after | isolated parallel critic agents + an orchestrator + synthesis (the council pattern) | always, the moment you add evaluation |
| **Provocateur** | provokes | before | a generative agent (read-only, trust-bounded) + a thin command | **optional, domain-named** |

The **Maker + Critic** split is universal and non-negotiable: self-review grades on a curve (familiarity bias and ordinary overconfidence make catching your own failures structurally hard — this is why art/design schools run the **crit** and engineering runs peer review). The **Provocateur** is the seat you _add by judgment_, and it is the interesting design decision.

## The one invariant: no seat judges its own work

The owner of the **standard** is never the owner of the **work**. This is the load-bearing rule, and in a plugin you make it **structural, not advisory** (the house rule: harden with structure, not prose). Realize the Critic and Provocateur as separate, isolated, read-only agents — the Maker physically cannot impersonate the critic, and the critic physically cannot rewrite the work. A guard that lives only in a sentence ("remember to review objectively") is not hardened; a separate tool-scoped agent is.

## The loop

```text
 PROVOCATEUR  →   MAKER    →   CRITIC    →   MAKER
  provoke         make         review        remake
 (diverge)      (converge)    (break it)    (converge)
```

This rhythm — **divergence → convergence → critique** — is the documented shape of creative and design work (Knapp's Design Sprint hard-codes _Diverge → Decide_; IDEO's brainstorming rule is **"defer judgment"** during generation; the writer's "murder your darlings" is the convergence tax). The handoffs are where the value moves: the Provocateur hands the Maker a _spread of options_ (most discarded); the Maker hands the Critic _finished work for a cold read_ (not a summary, not the author's rationale); the Critic hands back _severity-classified findings_; the Maker remakes or defends the line. Divergence alone is not the pattern — Knapp's own correction is that brainstorming _without_ a disciplined convergence and a separate critique fails.

## The third seat: name it for the domain, or omit it

The Provocateur's value scales with the **taste-dependence and ambiguity** of the problem. Install it in proportion to the cost of converging too early; name it for the domain.

| Domain | The third seat | Verdict | Why |
| --- | --- | --- | --- |
| **Brand / creative** | the **Muse** | dedicated agent, high value | "who does the customer become?" is irreducibly cultural and taste-laden; provocation supplies stance a brief can't (cf. Rory S.'s psycho-logic). brand-forge ships this. |
| **Product** | a **Visionary / Contrarian** | optional — usually a _ritual_, not a standing role | real ambiguity about the right problem, but bounded by markets and metrics; provocation arrives as mechanisms — Amazon's working-backwards **PR-FAQ**, **"disagree and commit"**, Roger Martin's **"what would have to be true?"**, JTBD reframing — no permanent seat required. |
| **Convergent engineering / agentic systems** | an **Explorer** (a bounded spike) | often unnecessary | once requirements are clear the work is verification-dominated; a standing "what if" seat manufactures divergence where the answer is already constrained. Use a time-boxed **architecture spike** only when the design space is genuinely open. |

If the work is convergent and correctness is testable, **omit the Provocateur** — do not add a council or a muse for symmetry. The Maker + Critic split still applies the instant you add evaluation; the Provocateur only when divergence actually pays.

## The trap: the Provocateur is NOT the red team

This is the distinction this audience most often gets wrong, because this very plugin's council **is** a red team. They are opposite seats:

- **The red team attacks a _converged_ artifact — backward.** It lives in the **Critic** seat (it breaks what already exists). NIST defines a red team as emulating an adversary against a built posture. plugins-factory's `plugin-council` is exactly this.
- **The Provocateur generates options _before anything exists_ — forward.** "The muse explores forward; the red team attacks backward."

Relabeling your review stage as "provocation," or bolting on a second adversarial panel and calling it a muse, does not give you a Provocateur — it gives you two Critic seats. A real third seat is _generative_: its output is divergent options and tensions, not severity-classified findings. If the new seat returns findings, it's a critic.

## Realizing the seats

- **Maker** — usually skill modes behind a `/x-build` command; promote a making role to its own agent only where isolation or parallel file-mutation earns the cost (`isolation: worktree`).
- **Critic** — the **council pattern** in `agent-architecture.md`: isolated parallel `critic-*` agents + an orchestrator with `Task` + a synthesis stage. Read-only (`Read, Grep, Glob`), trust-bounded.
- **Provocateur** — a single generative agent, scoped like a critic (read-only, trust-bounded — it reads input as _data_, never instructions) but generative in output, plus a thin command. A _solo_ provocateur must **earn its isolated context on its own merits** — it runs hot/divergent without polluting the maker's convergent thread, and it is a read-only sandbox for provoking _from_ untrusted input — **not** by symmetry with the council (a council earns isolation through critic _diversity_; one provocateur has no peers to anchor against). Accept, too, that it is the one seat with **no mechanical output contract** — its only check is that each provocation traces to a real root, which is judgment, not a test. The worked example is **brand-forge**: the `brand-muse` agent + `/brand-muse`.

## Embedded rubric — scoring a triad (when a plugin claims one)

Score only if the plugin orchestrates make/review/(provoke) work. Dimensions; `[gate]` fails the pattern outright.

- **R1 — Seat separation `[gate]`.** Maker and Critic are distinct, and the separation is _structural_ (separate tool-scoped agents), not a prose instruction. A maker that reviews its own output fails.
- **R2 — Third-seat justification.** If a Provocateur exists, it is earned by the domain's taste-dependence/ambiguity (and named for the domain); if absent, that omission is correct for convergent work. A muse bolted onto a convergent utility is a finding.
- **R3 — Provocateur ≠ red team `[gate]`.** If a third seat exists, it generates _forward_ (divergent options); it is not the review seat relabeled. A "provocateur" that returns findings fails.
- **R4 — Loop integration.** The handoffs are defined (what passes between seats), and the order is provoke → make → review → remake — not a vague "they collaborate."
- **R5 — Naming fit.** The third seat carries a domain name (Muse / Visionary / Explorer), signalling _what kind_ of divergence it supplies.

**Pass threshold:** R1 and R3 must pass; the rest raise quality. A plugin with no orchestration is exempt — most plugins are.

## When this pattern does NOT apply

Most plugins. A knowledge or utility plugin with a single convergent job needs no seats at all — manufacturing a council or a muse for it is the over-engineering the Elon lens (CF4) flags. Reach for this pattern only when the plugin genuinely runs work through more than one of: generate, make, judge.

## See also

- `agent-architecture.md` — building the Critic and Provocateur agents (the council pattern, tool-scoping, the trust boundary).
- `rubrics/agent-fit.md` — scoring an individual agent.
- **brand-forge** (catalog) — the worked example: the Muse (provoke) · Team (make) · Council (review) triad, with the loop and the one invariant.
