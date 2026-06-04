# Creative Collaboration — the Three Seats

Brand work is organized around three seats, defined by _when_ they act and _what they are for_: who **provokes** (before), who **makes** (the convergent middle), and who **reviews** (after). The whole discipline of a studio is keeping these seats distinct and moving the work between them in order. This reference defines the seats, the loop that connects them, and the one invariant that makes the loop work.

The split is not bureaucracy — it is how creative quality is actually produced. The maker+reviewer separation is universal (it shows up as the art-school **crit**, the agency **design review**, and peer code review); the third seat — the **Muse** — is the creative addition, the provocateur who widens the option space so the team converges on a _chosen_ answer instead of the first safe one.

## The three seats

| Seat | Verb | When | Posture | Realized in this plugin as |
| --- | --- | --- | --- | --- |
| **The Muse** | provokes | _before_ | divergent, generative, anti-consensus | the `brand-muse` agent · `/brand-muse` |
| **The Team** | makes | the _middle_ | convergent, decisive, accountable | the methodology's role seats · `/brand-build` |
| **The Council** | reviews | _after_ | adversarial, isolated, exacting | the `critic-*` agents + orchestrator · `/brand-council` · `brand-evaluate` |

The Muse and the Council are easy to confuse because both stand outside the making — but they are opposites in time and intent. **The Muse explores forward** (generates options before anything exists); **the Council attacks backward** (breaks the work after it exists). A provocation is not a critique, and a critique is not a provocation. Convene them at the wrong moment and each becomes noise: a council with nothing built reviews a vacuum; a muse let loose on finished work just relitigates settled decisions.

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

The **Brand Steward** is the seat most teams forget, and its absence is why brands decay: stewardship is not a creative act but a _decision architecture_, and it is owned, not improvised. (The Muse is a seat too, but it sits in its own column above — it feeds the Team, it is not one of the Team's convergent makers. See the `brand-muse` agent for its provocation lenses.)

## The loop: provoke → make → review → remake

```text
   MUSE            TEAM             COUNCIL           TEAM
 provoke    →      make      →      review     →     remake
(diverge)       (converge)        (break it)       (converge)
   │                │                 │                │
 widen the      decide and        name what       address the
 options;       ground the        fails, with     findings; or
 open angles    work on the       cited evidence  defend the line
 to a root      foundation                          on the record
```

This rhythm is not optional ceremony — it is the documented shape of creative process: Jake Knapp's Design Sprint hard-codes **Diverge → Decide** into the calendar; IDEO's brainstorming rules **"defer judgment"** during generation (critique is temporally banned while diverging); and the writer's discipline to **"murder your darlings"** (Quiller-Couch, 1914) is the convergence tax — you generate abundantly _so that_ you can cut ruthlessly. Knapp's own correction matters here: brainstorming _alone_ fails. Divergence only pays off when it is paired with a disciplined convergence and a separate critique.

**The handoffs are where work is won or lost:**

- **Muse → Team** is a _spread of grounded provocations_. Most are discarded; a high discard rate is healthy divergence, not waste.
- **Team → Team (strategy → expression)** is the **creative brief** — the single most load-bearing handoff in the studio. The brief is where the Planner's seat formally hands to the maker's seat. A weak brief poisons everything downstream; score it before passing it (`rubric-brief-quality` in `brand-evaluate`).
- **Team → Council** is _finished work + corpus context_, handed to a cold read. Not a summary, not the author's rationale — the actual artifact.
- **Council → Team** is _severity-classified findings_. The team remakes, or defends the line on the record. The loop repeats until the work survives.

## The one invariant: no seat judges its own work

The owner of the **standard** is never the owner of the **work**. This is the load-bearing rule, and it has a mechanism behind it: self-review grades on a curve. Your attention fills in the gaps because it knows what you _meant_; familiarity bias and ordinary overconfidence make catching your own failures structurally hard. The art-school crit exists for exactly this reason — "fresh eyes," and the rule that **critique serves the work, not the person.**

Three ways the invariant breaks, all common:

- **The lone genius** — one person plays all three seats. They provoke, converge, and approve their own work; the council finding never arrives because the council is the maker. This always grades on a curve.
- **The maker on the council** — the author sits in the review and "explains" the work. The explanation is the tell: if the artifact needed the author present, it failed the cold-read test.
- **The muse that won't let go** — the provocateur falls in love with its own angle and tries to make and defend it. Provocation is cheap precisely because it is not accountable for converging; the moment it converges, it owes the council a cold read like everyone else.

In this plugin the invariant is **structural, not merely advised**: the Muse and every Council critic run as separate, read-only agents in isolated contexts. They cannot make the work, and the makers cannot impersonate them.

**Why the Muse is its own agent, not a skill.** The Council earns its isolation through _diversity_ — fourteen critics must not anchor on each other. A single Muse earns isolation differently, on its own merits: it runs **hot** — deliberately divergent and anti-consensus — and a separate context keeps that wild exploration from polluting the team's convergent thread, while a read-only scope makes it a safe sandbox for provoking _from_ an untrusted brief without being able to act on it. And the Muse is, by design, the **one seat with no mechanical output contract**: a critic's finding cites evidence a reader can verify, but a provocation's only check is that it traces to a real cultural root — a human-judgment substitute for a test, knowingly uncheckable. That is not an oversight; it is the thesis — _structure is mechanized; taste is not_ — and provocation is the purest taste act in the pipeline.

## When to convene which seat

- **Convene the Muse** at the _start_ of a hard creative problem, or whenever the team is converging too fast onto the obvious answer. Symptom: the first idea feels "fine" and no one can name a braver one.
- **Stay in the Team** for the convergent middle — almost all of the work. Diverge deliberately, then decide.
- **Convene the Council** when work _exists_ and you want it broken before it ships — never before there is a grounded foundation to review (a council convened over decoration critiques decoration).

→ For how the seats staff each stage of an engagement, see [`team-operations-by-phase.md`](team-operations-by-phase.md). For the ways-of-working score, see the `rubric-creative-collaboration` rubric in `brand-evaluate`.
