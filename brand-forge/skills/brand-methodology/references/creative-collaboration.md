# Creative Collaboration — the Three Seats

Brand work is organized around three seats, defined by _what they are for_: who supplies the **pull** (the aspiration), who **makes** (converges the work), and who **reviews** (judges it after). The discipline of a studio is keeping these seats distinct and moving the work between them. This reference defines the seats, the loop that connects them, and the one invariant that makes the loop work.

The split is how creative quality is actually produced. The maker+reviewer separation is universal (it shows up as the art-school **crit**, the agency **design review**, and peer code review); the third seat — the **Muse** — is the aspirational one: an ideal, principle, or concept that exerts a **gravitational pull**, so the work moves toward something better than the category's center of gravity instead of settling into it.

## The three seats

| Seat | For | When | Posture | Realized in this plugin as |
| --- | --- | --- | --- | --- |
| **The Muse** | the pull — an aspiration to move toward | set early, persists | aspirational, directional | the `brand-muse` agent · `/brand-muse` |
| **The Team** | the making — convergence | the middle | decisive, accountable | the methodology's role seats · `/brand-build` |
| **The Council** | the review — judgment | after | adversarial, isolated, exacting | the `critic-*` agents + orchestrator · `/brand-council` · `brand-evaluate` |

The Muse and the Council both stand outside the making and are easily confused — but they are opposites. **The Muse pulls the work _toward_ an aspiration** (the direction it should reach for); **the Council judges the work _against_ that aspiration** (where it falls short). The Muse sets the standard; the Council enforces it. Neither makes.

**The Muse is many things — whatever best creates pull.** Sometimes the aspiration is a positive ideal ("who the customer becomes at our best"); sometimes it is a **provocation** — when the category's center of gravity is the wrong place to be, the truest aspiration is _away_ from the mainstream, and doing something very different is exactly right; sometimes it is a guiding concept or body of work to emulate, or a small set of principles. All are the same seat: an attractor adding gravitational pull in a direction. (See the `brand-muse` agent for the forms.)

## The Team's making roles

The Team is not one maker — it is a set of on-demand roles. Bernbach's 1949 innovation at Doyle Dane Bernbach was to seat the **copywriter and art director as equals** from the first minute, rather than passing copy to art down a hallway; that pairing is still the atom of creative work. Adopt the seat whose job the current task needs.

| Role | Owns | Asks |
| --- | --- | --- |
| **Strategic Planner** | Research → position → foundation | "What is the real cultural root, and what do we stand against?" |
| **Creative Director** | The idea and its integrity across everything | "Is this one idea, expressed many ways — or many ideas?" |
| **Copywriter** | Voice, naming, the words that carry meaning | "Does this sound like only us, or like the category?" |
| **Art Director** | The visual idea, image, composition | "Does the picture _say_ the strategy, or just decorate it?" |
| **Design Director** | The system — type, color, layout, coherence | "Will this hold across 200 surfaces and three years?" |
| **Product / UX Designer** | The brand as _experienced_ in the product | "Does using the thing feel like the brand claims to?" |
| **Brand Steward** | Coherence over time — guidelines, governance, the decision log | "Will a stranger extend this correctly a year from now, under deadline?" |

The **Brand Steward** is the seat most teams forget, and its absence is why brands decay: stewardship is not a creative act but a _decision architecture_, and it is owned, not improvised. (The Muse sits in its own row above — it supplies the pull the Team converges toward, it is not one of the Team's makers.)

## The loop: aspire → make → review → remake

```text
   MUSE              TEAM              COUNCIL            TEAM
  aspire    →        make      →       review     →      remake
(set the pull)   (converge          (judge against    (close the gap,
                  toward it)         the aspiration)    or defend it)
   │                  │                  │                  │
 name the ideal /  decide + ground   name where the    address the
 provocation /     the work, pulled  work falls short  findings, or
 concept           toward the pull   of the aspiration  defend on record
```

This is the documented shape of creative process, with one correction the attractor framing makes precise: **divergence is not the point — _direction_ is.** Jake Knapp's Design Sprint hard-codes **Diverge → Decide**, and IDEO's rule is to **"defer judgment"** while generating — but Knapp's own lesson is that brainstorming _alone_ fails. Generation pays off only when it is pulled toward an aspiration and then converged. The Muse supplies that pull; when it takes the form of a provocation, you **"murder your darlings"** (Quiller-Couch, 1914) to escape the obvious _toward_ a better direction, not merely away from the safe one.

**The loop has a precondition: aspire comes first.** The Team cannot converge toward nothing — without a named pull, "converge" collapses to "pick the safest option," which is the category average. So the aspiration must be **at least lightly named before the making starts** — a sentence is enough, and it is meant to evolve. This is a **soft gate, not a hard stop**: if no pull is set, name a provisional one (or convene the Muse) and proceed — the gate is cleared by _naming_ a direction. "Lightly declared and developed over time" is the healthy state; "no sense of the pull at all" is the blocker.

**The handoffs are where work is won or lost:**

- **Muse → Team** is _the articulated aspiration and the direction it implies_ — an ideal to reach for, a provocation to commit to, or a concept to emulate, each traced to a real root. The Team converges toward it.
- **Team → Team (strategy → expression)** is the **creative brief** — the single most load-bearing handoff in the studio. The brief is where the Planner's seat formally hands to the maker's seat. A weak brief poisons everything downstream; score it before passing it (`rubric-brief-quality` in `brand-evaluate`).
- **Team → Council** is _finished work + corpus context_, handed to a cold read. Not a summary, not the author's rationale — the actual artifact.
- **Council → Team** is _severity-classified findings_, measured against the aspiration the Muse set. The team remakes, or defends the line on the record. The loop repeats until the work survives.

## The one invariant: no seat judges its own work

The owner of the **standard** is never the owner of the **work**. This is the load-bearing rule, and it has a mechanism behind it: self-review grades on a curve. Your attention fills in the gaps because it knows what you _meant_; familiarity bias and ordinary overconfidence make catching your own failures structurally hard. The art-school crit exists for exactly this reason — "fresh eyes," and the rule that **critique serves the work, not the person.**

Three ways the invariant breaks, all common:

- **The lone genius** — one person plays all three seats. They set the aspiration, converge, and approve their own work; the council finding never arrives because the council is the maker. This always grades on a curve.
- **The maker on the council** — the author sits in the review and "explains" the work. The explanation is the tell: if the artifact needed the author present, it failed the cold-read test.
- **The Muse that won't let go** — the seat holding the aspiration falls in love with it and tries to make and defend the work itself. Holding the pull is a different job from converging the work; the moment the Muse makes, it owes the council a cold read like everyone else.

In this plugin the invariant is **structural, not merely advised**: the Muse and every Council critic run as separate, read-only agents in isolated contexts. They cannot make the work, and the makers cannot impersonate them.

**Why the Muse is its own agent, not a skill.** The Council earns its isolation through _diversity_ — fourteen critics must not anchor on each other. The Muse earns it differently: holding an aspiration is a standing orientation, and a separate context lets it run **hot** — especially when the pull is a provocation, a direction _away_ from the mainstream the convergent team would never reach on its own — without polluting the team's convergent thread, while a read-only scope makes it a safe place to draw an aspiration _from_ an untrusted brief without acting on it. And the Muse is, by design, the **one seat with no mechanical output contract**: a critic's finding cites evidence a reader can verify, but an aspiration's only check is that it traces to a real cultural root and genuinely pulls — judgment, not a test. That is the thesis — _structure is mechanized; taste is not_ — and the aspiration is the purest taste act in the pipeline.

## When to convene which seat

- **Convene the Muse** to set the aspiration at the _start_ of a brand, or to re-assert it whenever the work is drifting toward the category average — settling for the competent and generic. Symptom: the work is "fine" and indistinguishable from three competitors.
- **Stay in the Team** for the convergent middle — almost all of the work, pulled toward the aspiration the Muse set.
- **Convene the Council** when work _exists_ and you want it judged against the aspiration — never before there is a grounded foundation to review (a council convened over decoration critiques decoration).

→ For how the seats staff each stage of an engagement, see [`team-operations-by-phase.md`](team-operations-by-phase.md). For the ways-of-working score, see the `rubric-creative-collaboration` rubric in `brand-evaluate`.
