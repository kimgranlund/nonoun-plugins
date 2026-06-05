---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Ann C. \"Privacy by Design: The 7 Foundational Principles.\" Information & Privacy Commissioner of Ontario, Canada. Originally published August 2009, revised January 2011. https://www.ipc.on.ca/wp-content/uploads/resources/7foundationalprinciples.pdf"
  - "Helen Nissenbaum. *Privacy in Context: Technology, Policy, and the Integrity of Social Life*. Stanford University Press, 2010 (contextual-integrity theory of privacy as appropriate information flow)."
  - "Regulation (EU) 2016/679 (GDPR), Article 25 — 'Data protection by design and by default.' https://gdpr-info.eu/art-25-gdpr/"
---

# Privacy by Design

Privacy by Design (PbD) is the discipline of building privacy into a product as a default architectural property rather than bolting it on after launch or burying it in a settings page. The framework is Ann C.'s, published while she was Information & Privacy Commissioner of Ontario (2009, revised January 2011) and later written into law as GDPR Article 25 ("data protection by design and by default"). This reference turns its seven principles into seven design checks — questions you run against a feature before it ships — and adds the one thing the principles assume but don't operationalize: a way to decide _which_ data flows are appropriate in the first place (Nissenbaum's contextual integrity). The load-bearing move is **privacy as the default state, so that a user who does nothing is already protected** — the opposite of the consent-fatigue model where protection is something the user must hunt for and switch on.

> The framing to hold onto, from Ann C.'s Principle 2: personal data are "automatically protected in any given IT system or business practice, as the default. No action is required on the part of the individual to protect their privacy — it is built into the system, by default." Privacy you have to go and turn on is not privacy by design; it is privacy by homework.

PbD is a **durable, named framework** with a clear primary source, but two honest caveats. First, the seven principles are deliberately high-level — they have been criticized (notably by engineers and by the US FTC's 2012 staff report) as aspirational and hard to operationalize, which is exactly why this file converts each into a concrete check. Second, "positive-sum, not zero-sum" (Principle 4) is Ann C.'s stated ideal, not a law of nature; real designs sometimes _do_ trade functionality against data minimization, and the honest version of this principle is "look hard for the win-win before accepting the trade," not "a win-win always exists." Both are labeled where they bite below.

---

## The seven principles, as design checks

Each principle is quoted in Ann C.'s own titling, then turned into a check you can actually run against a screen or a data flow. The quoted descriptions track the IPC document.

| # | Principle (Ann C.'s title) | The design check |
| --- | --- | --- |
| 1 | **Proactive not reactive; preventative not remedial** | Did privacy risk get raised in the design review, _before_ build — or only after an incident or a regulator forced it? "Privacy by Design comes before-the-fact, not after." |
| 2 | **Privacy as the default setting** | If the user does nothing, are they protected? Are the most privacy-protective options the out-of-the-box state — not opt-in toggles the user must find? |
| 3 | **Privacy embedded into design** | Is privacy a property of the architecture and data model, or a notice/consent layer painted over a system that collects everything anyway? |
| 4 | **Full functionality — positive-sum, not zero-sum** | Did the team genuinely look for the design that delivers the feature _and_ minimizes data — rather than assuming privacy must cost functionality? (Labeled: the win-win is the goal, not a guarantee.) |
| 5 | **End-to-end security — full lifecycle protection** | Is the data protected "cradle to grave" — secured in transit, at rest, and securely destroyed at end of life — not just guarded at the front door? |
| 6 | **Visibility and transparency — keep it open** | Can a user (or an auditor) actually see what is collected, why, and where it goes — and verify the system does what its policy promises? |
| 7 | **Respect for user privacy — keep it user-centric** | Are the individual's interests "uppermost" — strong defaults, clear notice, genuine choice, easy access — or is the design optimized for the business's appetite for data? |

The principles are not independent dials; they reinforce. Principle 2 (default) is the sharpest and most testable — it is the one a reviewer should reach for first, because "is the user protected if they do nothing?" is a yes/no question a feature either passes or fails. Principle 7 is the values backstop the other six serve.

---

## Data minimization: the principle under the principles

The single most actionable consequence of PbD — and the one GDPR Article 5(1)(c) makes a hard legal requirement — is **data minimization**: collect only what the stated purpose actually requires, keep it only as long as needed, and don't retain it "in case it's useful later." Minimization is how Principles 2, 3, and 5 become concrete. The check is purpose-binding: for every field collected, name the specific feature that breaks without it. If you can't, the field is speculative collection and should be cut.

```text
For each piece of data the product collects, answer:
  WHAT      — what exactly is collected (be specific: "precise GPS" not "location")
  WHY       — which user-facing feature requires THIS field to function
  HOW LONG  — the retention period, and what triggers deletion
  WHO       — who/what else receives it (third parties, analytics, the model)

If WHY is "might be useful" or "for analytics generally" → cut the field.
If HOW LONG is "indefinitely" → set a retention limit and a deletion trigger.
If WHO includes parties the user wouldn't expect → that's a contextual-integrity violation (below).
```

The tell of a product that skipped minimization: a sign-up form that asks for phone number, birthday, and gender to read a blog post; an app requesting every permission "to be safe"; a retention policy of "forever." Each is collection unbound from purpose.

---

## Contextual integrity: deciding which flows are appropriate

PbD says protect data and minimize collection, but it doesn't, on its own, tell you _which_ data flows are acceptable. Helen Nissenbaum's **contextual integrity** (Privacy in Context, 2010) fills that gap: privacy is not secrecy and not control — it is "the appropriate flow of information," where appropriateness is set by the norms of the context the data was shared in. The same data point is fine in one flow and a violation in another. Health data shared with a doctor is appropriate; the same data sold to an insurer breaks the norm of the medical context. Nissenbaum's model makes a flow analyzable with five parameters — and a privacy violation is a change to any of them that the user wouldn't expect.

| Parameter | The question | Violation looks like |
| --- | --- | --- |
| **Data subject** | Whose data is it? | Collecting data about non-users (a contact's number from someone's address book) |
| **Sender** | Who is sharing it? | — |
| **Recipient** | Who receives it? | A fitness app sharing heart-rate data with an ad network |
| **Information type** | What kind of data? | Repurposing a phone number given for 2FA into a marketing channel |
| **Transmission principle** | Under what expectation / constraint? | "Shared confidentially with my doctor" → resold; the constraint was broken |

The practical use: when a feature introduces a new data flow, walk the five parameters and ask "would the user, given the context they shared this in, expect _this_ recipient, _this_ type, under _this_ constraint?" If a parameter changed without the user's reasonable expectation, you have a privacy harm even if a consent box was technically checked. This is the analytical engine behind "creepy" — the data flow is technically permitted but contextually wrong.

---

## Anti-patterns

- **Privacy-as-homework.** Protection exists, but only if the user finds and enables it — the inverse of Principle 2. The default leaks; the safe state is opt-in.
- **Notice-and-consent theater.** A privacy policy and a consent banner painted over a system that collects everything regardless — Principle 3 inverted. The notice describes the harm; it doesn't prevent it.
- **Speculative collection.** Gathering data "in case it's useful," with no purpose binding it — the minimization failure. Every un-bound field is future breach surface and future liability.
- **Indefinite retention.** No deletion trigger, no retention limit — Principle 5's lifecycle gap. Data you keep forever is data you will eventually leak.
- **Context collapse / repurposing.** Data collected for one purpose silently reused for another (2FA number → marketing) — a contextual-integrity violation even with a checked box.
- **Privacy as a paid tier.** Charging for the privacy-protective option while the free default surveils — Principle 7 inverted; the individual's interest is subordinated to monetizing their data.
- **Zero-sum surrender.** Declaring "we need all this data to deliver the feature" without seriously looking for the positive-sum design (Principle 4) — sometimes true, but usually an unexamined assumption.

---

## The scoring test: is privacy designed-in, or bolted-on?

1. **Default-protective.** If the user does nothing, are they in the most privacy-protective state — or does protection require them to find and flip switches? (Principle 2, the sharpest test.)
2. **Purpose-bound collection.** Can every collected field be tied to a specific feature that needs it, with a retention limit and deletion trigger — or is there speculative "might be useful" collection and indefinite retention?
3. **Architectural, not cosmetic.** Is privacy a property of the data model and architecture — or a notice/consent layer over a system that hoovers everything? (Principle 3.)
4. **Lifecycle-secure.** Is data protected in transit, at rest, and securely destroyed at end of life — not just guarded at collection? (Principle 5.)
5. **Contextually appropriate flows.** For each data flow, would the user — given the context they shared in — expect this recipient, type, and constraint? (Nissenbaum's five parameters.)
6. **Visible and user-centric.** Can the user see what's collected and why, and is the design optimized for their interest over the business's data appetite? (Principles 6 and 7.)

A product passes when a user who reads nothing and changes no settings is already well-protected, every collected field earns its place against a real purpose, and no data flow would surprise the person it describes. It fails when privacy is a feature you opt into, a policy you're assumed to have read, or a default that quietly leaks.

---

## One labeled caveat

The verbatim principle titles and short quotations ("comes before-the-fact, not after"; "automatically protected... as the default. No action is required"; "positive-sum 'win-win'"; "cradle to grave"; "keep the interests of the individual uppermost") track Ann C.'s "Privacy by Design: The 7 Foundational Principles" (IPC Ontario, 2009 / rev. 2011) as reproduced across multiple authoritative mirrors; cross-checked in this session against the Global Privacy & Security by Design Centre's listing rather than against a single canonical PDF (the IPC original was retrieved but rendered as binary). The principle names and concepts are unambiguous across every source. The critique that the seven principles are "vague and aspirational" is most prominently the US FTC's (2012 privacy staff report) and is widely echoed by engineers; treat it as a real, sourced limitation, not a strawman. Contextual integrity's five parameters and "appropriate information flow" framing are Nissenbaum's (Privacy in Context, 2010). Data minimization as a hard requirement is GDPR Article 5(1)(c).
