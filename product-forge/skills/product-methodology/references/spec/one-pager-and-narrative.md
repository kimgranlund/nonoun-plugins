---
date: 2026-06-03
coverage: deep
primary_sources:
  - "Colin Bryar and Bill Carr, *Working Backwards: Insights, Stories, and Secrets from Inside Amazon* (St. Martin's Press, 2021). ISBN 978-1-250-26796-3."
  - "Colin Bryar & Bill Carr, *Amazon Narratives — Memos, Working Backwards from Release, More*, a16z podcast (interview). https://a16z.com/podcast/amazon-narratives-memos-working-backwards-from-release-more/"
  - "Jeff Bezos, S-Team email 'No powerpoint presentations from now on at steam' (June 9, 2004), as quoted in contemporary reporting. https://www.inc.com/justin-bariso/amazon-jeff-bezos-powerpoint-meetings-how-to-think.html"
  - "Jeff Bezos, *1997 Letter to Shareholders* (the 'Day 1' letter), Amazon.com, Inc. https://s2.q4cdn.com/299287126/files/doc_financials/2021/ar/Amazon-2020-Shareholder-Letter-and-1997-Shareholder-Letter.pdf"
  - "Marty C., *The Customer Letter*, Silicon Valley Product Group, and *Inspired*, 2nd ed., ch. 36 'Customer Letter Technique' (Wiley, 2018). https://www.svpg.com/the-customer-letter/"
---

# The six-pager, the narrative memo, and the customer letter

This reference is about a deeper claim than "write a PRD": that for the right kind of decision, a **narrative memo beats both a slide deck and a structured PRD** — and that two specific narrative forms (Amazon's six-pager and Marty C.'s customer letter) are spec instruments in their own right. The argument matters because product teams default to slides and to fill-in-the-blank templates precisely when prose would have caught the flaw. The formal authoring engines for finished PRDs/specs are the global `plan-prd` and `plan-spec` skills (peers, not duplicated here); this reference covers the narrative _form_ and when to reach for it instead of a structured document.

## The 2004 decision: narrative over slides

On June 9, 2004, Jeff Bezos sent the S-Team an email titled "No powerpoint presentations from now on at steam." It is the founding artifact of Amazon's writing culture, and its core argument is precise enough to quote:

> "The reason writing a ... memo is harder than 'writing' a ... powerpoint is because the narrative structure of a good memo forces better thought and better understanding of what's more important than what, and how things are related." — Jeff Bezos, 2004 S-Team email

Bezos also closed the obvious loophole: "If someone builds a list of bullet points in word, that would be just as bad as powerpoint." The target was never the software; it was **bulleted thinking**. The switch was influenced by Edward Tufte's critique of presentations, and Bryar (in the a16z interview) recounts the trigger plainly: after "one particularly painful meeting ... Jeff said, 'Let's stop doing PowerPoints at these S-team meetings,'" because "it's the wrong tool for what we're trying to do."

### Why prose catches what slides hide

The deep point is epistemic. A slide of bullets can be internally incoherent and nobody notices — the connective tissue ("therefore," "but," "because," "unless") lives only in the presenter's head and is filled in differently by every viewer. A narrative cannot hide a gap: to write "X, therefore Y" in a sentence, the author must actually believe the inference holds, and a reader can see when it doesn't. Bullets let you _assert_ a structure; prose forces you to _have_ one. That is the entire reason the memo is "harder" — the difficulty is the feature, because the friction is where the muddled thinking gets caught.

Bryar and Carr add the information-density argument, though it is worth labeling as **the authors' own framing rather than an independently measured fact**: in the interview, Carr states a narrative conveys "about 10 times as much information" as a PowerPoint, and Bryar adds "the pixel density is about seven to nine times the pixel density," with the rationale that "people read faster than people talk." These figures are illustrative claims by the practitioners, not peer-reviewed measurements; treat them as the authors' characterization of why the format works, not as data.

## The six-pager: shape and ritual

The Amazon narrative converged on a specific form, and the details are deliberate:

| Property | Detail | Why |
| --- | --- | --- |
| **Length** | Started as four pages; settled on **six** as the cap | Six was "the right length for an hour meeting" — long enough for depth, short enough to force ruthless prioritization. The constraint does the editing. |
| **Form** | Running prose ("narrative"), full sentences — explicitly **not** bullets | Per Bezos: bullets in Word "would be just as bad." |
| **Quality bar** | "Very data-based and fact-based"; "writing them is way harder than making a good PowerPoint" | A narrative that is vague reads as vague; the form exposes hand-waving. |
| **Reading** | Read **silently in the room**, ~3 minutes/page, first ~20 minutes of the meeting | Everyone engages the full argument before anyone speaks — no charismatic presenter steering interpretation, no skimming. |
| **Discussion** | The remaining time is page-by-page Q&A | The document, not the speaker, is on trial. |

The silent-reading ritual is the part teams most often drop and most need. It guarantees the decision is made against the _actual argument as written_, not against a confident verbal performance of it. A memo that falls apart under a careful silent read was always going to fall apart; the ritual just moves the discovery earlier and cheaper.

## When a narrative beats a structured PRD

A structured PRD (problem / user / outcome / non-goals / risks / open questions — see the `prd-modern` reference) is the right instrument for **execution against a settled direction**: the team agrees on the bet and needs an artifact dense enough to build from without re-deriving it. A narrative is the right instrument for the prior question — **should we do this at all, and do we even understand it?** The two are complementary, not competing, and the choice turns on what kind of thinking the document must force.

```text
Reach for a NARRATIVE / six-pager / customer letter when:
  - the DIRECTION is unsettled — you are deciding whether/why, not how
  - the idea is NEW or strategically large — the reasoning, not the spec, is the risk
  - cross-functional leaders must be PERSUADED by an argument, not just informed of a plan
  - the relationships between facts ("X therefore Y unless Z") are the hard part
  - a template would let the author dodge the connective reasoning by filling boxes

Reach for a STRUCTURED PRD when:
  - the direction is SETTLED and the team needs to EXECUTE
  - completeness/coverage matters more than persuasion (scope, metrics, edge cases)
  - a downstream team must act without re-deriving (the "act-without-re-deriving" test)
  - the artifact must be a durable reference, not a one-meeting decision instrument

Rule of thumb: prose forces an ARGUMENT; a template ensures COVERAGE.
Use prose to decide; use the structured doc to build.
```

The failure mode in each direction is symmetric. Forcing a genuinely undecided, strategic question into a PRD template produces a confident-looking document that never had to defend its central inference — the boxes are filled, the logic is untested. Forcing a settled execution plan into free narrative produces a beautiful essay that omits the non-goals, metrics, and edge cases an implementer needs. Match the form to the question: narrative when the thinking is the risk, structure when the coverage is.

## Bezos's shareholder letters as narrative memos

The clearest public specimens of the form are the **Amazon annual shareholder letters**, which read as narrative memos rather than financial boilerplate. The 1997 "Day 1" letter — the first — is effectively a manifesto: it opens the long-term-thinking and customer-obsession argument ("But this is Day 1 for the Internet and, if we execute well, for Amazon.com") in connected prose, not bullets. Bezos considered it foundational enough to **attach the original 1997 letter to every subsequent annual letter for over twenty years**, treating it as Amazon's durable DNA. They are worth reading as the public, polished end of the same discipline the internal six-pager enforces privately: an argument made in sentences, where the reasoning is visible and therefore accountable.

(Single-source caveat: characterizations of the letters' internal _influence_ come substantially from Bryar and Carr, former insiders; the letters themselves are primary and public.)

## The customer letter: Marty C.'s narrative spec

Marty C. adapts the working-backwards instinct into a product-discovery form he calls the **customer letter**, his "variation on the Amazon press release." It is a narrative spec, and its shape is specific:

- **Who writes it**: an imagined, very happy customer — drawn from "a well-defined user or customer persona" — writing **to the CEO**, after using the new product or redesign, to explain why they are grateful and how it changed or improved their life.
- **The second half**: an imagined **congratulatory response from the CEO to the product team**, explaining how this work helped the _business_. This is the bridge from customer value to business value, in one artifact.
- **The driving question**: having written the letter, the team asks "how do we make this letter come true?" — and builds the discovery strategy backwards from it. The output, not the feature list, is the spec.
- **When to use it**: Marty C. reserves it for **larger efforts with multiple, overlapping goals** — typically product redesigns — where "there may in fact be multiple reasons, several customer problems to be solved, or business objectives to be tackled." For a small, single-goal effort it is overkill; its value is in showing how several goals "dovetail into customer satisfaction."

Why a letter and not a requirements list, in Marty C.'s terms: the technique exists "to keep the team focused on the outcome, not the output." A requirements list invites the team to optimize each item in isolation; a single customer's letter forces them to see the _whole experience_ the customer actually has, across all the goals at once — which is exactly the coherence a multi-goal redesign needs and a feature list destroys. It is the same move as the Amazon PR/FAQ (companion `working-backwards-prfaq` reference): start from the delighted customer and reason backwards — but personalized to one named persona's life, and explicitly wired to the business via the CEO's reply.

## The throughline

All three forms — six-pager, shareholder letter, customer letter — encode one belief: **the act of writing connected prose is itself the thinking tool.** Slides let you assert structure you don't have; templates let you achieve coverage without coherence; a narrative makes you build the argument in public, sentence by sentence, where its gaps are visible to a careful reader. Reach for these forms when the reasoning is the risk. Reach for a structured PRD when the direction is settled and a team must build without re-deriving it. The skill is knowing which question you are actually answering.
