---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Mailchimp — *Content Style Guide*, 'Voice and Tone.' https://styleguide.mailchimp.com/voice-and-tone/"
  - "Nielsen Norman Group — 'The Four Dimensions of Tone of Voice' (Kate Moran). https://www.nngroup.com/articles/tone-of-voice-dimensions/"
  - "Nielsen Norman Group — 'The Impact of Tone of Voice on Users' Brand Perception' (Kate Moran, Kim Salazar). https://www.nngroup.com/articles/tone-voice-users/"
  - "Sarah Richards, *Content Design* (Content Design London, 2017; 2nd ed. 2023). ISBN 9781527209183."
---

# Voice and Tone (Product-Side UX Writing)

Voice and tone govern _how the interface sounds_ — and the field's foundational move is to split them. **Voice is the product's consistent personality; tone is how that voice flexes to the situation.** MailChimp's public style guide states it plainly: "You have the same voice all the time, but your tone changes... depending on the emotional state of the person you're addressing." A product can be clear, calm, and human everywhere (voice) while turning empathetic in an error, plain on a legal page, and quietly celebratory on success (tone). Confusing the two — using the same chipper tone to confirm a payment and to report a failed one — is the most common voice defect there is.

> **Boundary up front: this is product-side UX writing, not brand voice.** This file covers the voice _of the interface_ — the personality expressed in the words a user reads while completing a task, in service of clarity and task-completion. The brand's distinctive voice as an identity asset — its cultural positioning, how the brand sounds across all media, the voice that differentiates it in its category — is a **brand-strategy** question and lives in **brand-forge**, not here. The two must be consistent (the product should sound like the brand), but they answer different questions. When the request is "define/evaluate our brand voice," route to brand-forge. When it's "how should our error messages and buttons sound so users get through the task," that's this file. Where the two overlap, the brand sets the personality and product content design keeps it from costing comprehension — clarity is the floor the brand voice sits on, never something the brand voice overrides.

## Voice (constant) vs. tone (varies)

The distinction is operational, not academic — it tells you what to fix when copy feels off.

- **Voice = the traits that never change.** A short, named list of personality attributes the product holds everywhere: e.g., _clear, warm, plain-spoken, never condescending._ Voice is what makes two unrelated screens feel like the same product wrote them.
- **Tone = the dial you turn per moment.** The same voice rendered at different emotional registers depending on the user's state and the stakes of the moment. MailChimp: "Our voice doesn't change much from day to day, but our tone changes all the time."
- **Read the user's state first.** Tone is chosen from _the reader's_ emotional state, not the writer's mood: someone hitting an error is frustrated or anxious; someone finishing setup is relieved or proud. Match the tone to where they are.
- **The diagnostic.** If copy feels wrong everywhere, your **voice** is mis-defined or unevenly applied. If copy feels wrong _only in a specific moment_ (a joke in an error, a flat "Success." after a hard task), your **tone** is mismatched to the situation. Fix the right layer.

## Nielsen's four dimensions: making voice/tone concrete

"Be friendly but professional" is unactionable. NN/g (Kate Moran) makes voice and tone measurable with **four dimensions, each a 3-point scale with a neutral midpoint** — so any string, and any product's voice, can be placed precisely:

| Dimension      | One end ↔ Other end           |
| -------------- | ----------------------------- |
| **Humor**      | Funny ↔ Serious               |
| **Formality**  | Formal ↔ Casual               |
| **Respect**    | Respectful ↔ Irreverent       |
| **Enthusiasm** | Enthusiastic ↔ Matter-of-fact |

How to use the four dimensions:

- **Define the product's voice as a default position on each axis.** E.g., "slightly serious, casual, respectful, matter-of-fact." This converts vibes into a spec a writer or reviewer can apply and check.
- **Tone is movement along the axes from that default.** In an error you might dial enthusiasm down to fully matter-of-fact and humor to fully serious; in a celebration you dial enthusiasm up. Voice = your home position; tone = the controlled deviation per moment.
- **Why it matters beyond style:** NN/g's brand-perception research (Moran & Salazar) found tone of voice measurably shapes how users perceive a brand — the _same_ information delivered in different tones changed perceptions of friendliness, trustworthiness, and how desirable the product seemed. Tone is not cosmetic; it moves trust.
- **Watch the irreverence axis especially.** Irreverent/funny copy that delights in a marketing moment reads as flippant or mocking in a failure, a security warning, or a billing error. The cost of misplaced irreverence is highest exactly where stakes are highest.

## The tone-by-situation map

The practical artifact a product needs is a **tone map**: for each kind of moment, the tone the constant voice should take. This is the single most useful thing to produce, and the thing teams most often skip.

| Situation | User's likely state | Tone (same voice, flexed) | Tell of getting it wrong |
| --- | --- | --- | --- |
| **Error / failure** | Frustrated, anxious, possibly blamed | Empathetic, calm, plain; matter-of-fact, fully serious | Jokes, blame, fake-cheery "Oops!" that trivializes |
| **Success / completion** | Relieved, satisfied, sometimes proud | Warm, affirming, brief; enthusiasm dialed _up_ a notch | Flat "Success." that ignores effort, or over-celebrating a trivial action |
| **Onboarding / first run** | Curious but impatient, low context | Encouraging, guiding, confidence-building | Overwhelming, or condescending ("It's easy!") |
| **Empty state** | Mildly uncertain ("is this broken?") | Inviting, lightly encouraging, points to the next step | Apologetic, or so jokey the next action gets lost |
| **Destructive / irreversible action** | Cautious, needs to be sure | Serious, precise, no humor; names the consequence | Breezy tone that undersells the stakes |
| **Legal / privacy / security** | Wants certainty and candor | Neutral, precise, plain; respectful, matter-of-fact | Marketing spin, vagueness, forced friendliness |
| **Waiting / loading** | Slightly impatient | Reassuring, light personality acceptable | Silence on long waits; jokes that stale on repeat |
| **Marketing / upgrade moment** | Open, evaluating | Most expressive end of the voice; enthusiasm allowed | Hype that survives into the post-purchase task surfaces |

The governing rule: **the higher the stakes or the worse the user's state, the more you dial toward serious, plain, and matter-of-fact — and the less room there is for personality.** Personality concentrates in the low-stakes, positive moments; it recedes where a user is stressed, at risk, or must not misread.

## Defining a product voice without straying into brand identity

You can and should define a _product_ voice even when there's no formal brand-voice work — but keep it in the product-UX lane.

- **Anchor it in the task and the user, not the brand mythos.** A product voice is "how we talk to someone using the product to get something done." It expresses traits (clear, human, respectful) in service of completion — it is not a statement of who the company _is_ in the culture (that's brand-forge's brand archaeology and positioning).
- **Write it as 3–5 traits, each with a do/don't pair.** "We're plain-spoken: we say 'we couldn't charge your card,' not 'a billing exception occurred.'" Traits without examples are unenforceable.
- **Place the traits on the four dimensions** so the voice has a measurable home position, then derive the tone map from it.
- **Inherit, don't invent, where brand voice exists.** If brand-forge (or a brand team) has defined brand voice, the product voice is its application to the interface — same personality, made operable at the level of buttons, errors, and labels. Don't create a second, conflicting personality; translate the one that exists into task-level rules. If brand voice does _not_ exist, a product voice scoped to clarity and task-completion is still legitimate and useful on its own — just don't let it quietly become a brand-identity exercise.
- **Clarity is the non-negotiable floor.** However the voice is positioned, it never overrides comprehension at task-critical surfaces. MailChimp's own rule holds: clear beats entertaining wherever a user is trying to act. (Content-design's clarity-over-cleverness principle is in `content-design-principles.md`.)

## Tells of good vs. bad

| Dimension | Good | Bad |
| --- | --- | --- |
| **Voice consistency** | Same personality across every screen | Each screen sounds like a different writer |
| **Tone fit** | Tone flexed to the user's state per moment | One tone everywhere (cheery error, flat success) |
| **Specification** | Voice = named traits placed on the 4 dimensions | "Friendly but professional," undefined |
| **Tone map** | Documented tone per situation, applied | No map; tone decided ad hoc per string |
| **Stakes awareness** | Serious/plain at high-stakes & bad-state moments | Humor/irreverence in errors, security, billing |
| **Brand boundary** | Product voice = brand voice applied to the UI, clarity as floor | Product invents a rival personality, or copy-as-brand-flex breaks the task |
| **Clarity** | Personality never costs comprehension | Cleverness wins over the user finishing the task |

The single test: **read each string as the product speaking to a real person in that exact moment.** Does it sound like the same product everywhere (voice intact), and is it pitched right for how that person feels right now (tone matched)? If a celebration is flat, an error is flippant, or two screens sound like strangers — voice or tone has failed, regardless of how on-brand the words look in isolation.
