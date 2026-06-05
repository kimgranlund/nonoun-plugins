---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Kate Moran & Sarah Gibbons, 'Generative UI and Outcome-Oriented Design', NN/g (nngroup.com/articles/generative-ui), 2024-03-22"
  - "Kate Moran & Sarah Gibbons, 'GenUI: AI-Generated Interfaces' (video), NN/g (nngroup.com/videos/genui-ai-generated-interfaces), 2024"
  - "Greg Nudelman, 'Secrets of Agentic UX: Emerging Design Patterns for Human Interaction with AI Agents', UX Magazine (uxmag.com/articles/secrets-of-agentic-ux-emerging-design-patterns-for-human-interaction-with-ai-agents), 2025-04-22"
---

# Generative & Adaptive UI

Beyond chat, AI shows up _inside_ the interface: as a copilot in a side panel, as inline suggestions in the content the user is editing, and — at the frontier — as the interface itself, assembled on the fly. This reference covers that spectrum, from the well-understood (inline AI, side-panel assistants) to the genuinely emerging (UI generated in real time by a model). The common thread is that the AI stops being a separate destination and becomes a layer over the user's real work. The design problem shifts from "design a screen" to "decide how much of the screen the model gets to write, and how the user stays in control of it."

> The framing to hold onto: **generative UI moves the designer's job from drawing elements to setting constraints.** Kate Moran and Sarah Gibbons (NN/g) define generative UI as "a user interface that is dynamically generated in real time by artificial intelligence to provide an experience customized to fit the user's needs and context," and frame the accompanying discipline — outcome-oriented design — as "orchestrating experience design with a greater focus on user goals and final outcomes, while strategically automating aspects of interaction and interface design." You stop designing buttons and start designing the guardrails the AI must generate within.

This is an **emerging area with thin durable literature.** The definitions and the outcome-oriented framing below are well-sourced to NN/g; the placements (inline, side-panel, in-canvas) are conventions consolidated across vendor products and named practitioners, not laws — treat them as a starting taxonomy, and label any claim of "users prefer X" as single-source unless replicated.

---

## The spectrum: four placements

AI assistance sits on a spectrum from a separate destination to a fully generated surface. The four placements below are the load-bearing points on it.

| Placement | Where the AI lives | Best for | Control concern |
| --- | --- | --- | --- |
| **Conversational** | A dedicated chat surface | Open-ended intent (see the chat reference) | Discoverability, steerability of the thread |
| **Side-panel assistant (copilot)** | A persistent panel beside the user's document or app | Acting _on_ the current context without leaving it | Keeping the panel's actions scoped to what the user can see |
| **Inline AI** | Suggestions woven into the content being edited (ghost text, inline rewrites, slash-commands) | Low-friction, in-flow assistance | Not hijacking the cursor; clean accept/reject |
| **AI-in-the-canvas (generative UI)** | The interface itself, assembled by the model per request | The long tail no fixed screen anticipates | Consistency, learnability, and user control of a UI that changes |

Moving down the table trades predictability for adaptivity. Moving up trades adaptivity for the learnability of a stable, designed surface. Most real products mix placements: a fixed shell with inline AI in the editor and a copilot panel for bigger asks.

---

## Side-panel assistants (copilots)

The dominant pattern: a persistent panel that shares the user's context (the open file, record, or selection) and can answer about it or act on it, without making the user leave their work. The copilot wins because **context is free** — it already knows what the user is looking at — and because it keeps the primary surface intact for users who ignore it.

Canonical form:

```text
┌──────────────────────────┬──────────────────────┐
│                          │  Assistant            │
│   User's document /      │  ───────────────────  │
│   primary work surface   │  Working on: <this    │
│   (stays in control)     │   doc / selection>    │
│                          │                       │
│                          │  [ suggested action ] │
│                          │  [ suggested action ] │
│                          │                       │
│                          │  Type a request…      │
└──────────────────────────┴──────────────────────┘
        ↑ primary stays usable      ↑ scoped to visible context
```

The discipline: the panel's powers should be **legible and scoped**. The user should be able to tell what context the copilot can see, and any action it proposes against the document should land as a reviewable change in the document — not as an invisible mutation the user discovers later.

---

## Inline AI

Inline AI puts the model in the flow of the content: ghost-text completions, select-and-rewrite, slash-commands that insert generated blocks. It is the lowest-friction placement and the easiest to get subtly wrong, because it shares the user's most precious real estate — the cursor.

| Lever | Good — assists the flow | Bad — fights the flow |
| --- | --- | --- |
| **Trigger** | Explicit and predictable (a key, a slash, a select-then-act) | Fires on its own and inserts text the user did not ask for |
| **Accept / reject** | A clear, single gesture to take or dismiss a suggestion | Suggestions that are hard to undo or that commit on a stray keystroke |
| **Distinguishability** | Generated text is visually distinct until accepted (e.g. ghosted) | AI text indistinguishable from the user's own, silently mixed in |
| **Cursor ownership** | The user keeps the cursor; AI proposes, never seizes | The cursor jumps, selection is hijacked, focus is stolen |

The rule that generalizes: **inline AI proposes, the user disposes.** A suggestion the user can take or leave with one gesture is an assist; text that appears and stays unless actively removed is an imposition.

---

## AI-in-the-canvas: generative UI

The frontier placement: the model assembles the interface itself, per request and per user. NN/g's outcome-oriented framing is the design stance for it — rather than drawing each control, the designer "establish[es] constraints and guardrails," which NN/g describes as "guard rails that the AI must abide by when generating an interface." You specify what the UI must achieve and must never do; the model composes the rest.

The promise is a UI fitted to each user and each task — the long tail no fixed screen anticipates. The hazards are real and named by the same NN/g source, and they are the reason this placement is still emerging rather than default:

- **Learnability and consistency.** Familiarity is what makes a tool fast: "the more you use a website, the more familiar (and thus efficient) you become." A UI that changes every visit forfeits that. NN/g cautions that "constant relearning of the interface might cause frustration, especially in the beginning." A generated UI must hold _enough_ stable that users build muscle memory.
- **Inherited model failure.** Generative UI inherits the model's "hallucinations and biases" — now expressed as wrong controls and mislabeled actions, not just wrong sentences.
- **Privacy.** Personalizing to the individual requires intent and behavioral data; NN/g flags the "substantial risks to individual privacy and security" this implies.

| Lever | Good — generation in service of outcomes | Bad — generation for its own sake |
| --- | --- | --- |
| **What's designed** | Outcomes + guardrails the model generates within | A free-for-all where the model invents UI unconstrained |
| **Stability** | A stable shell / familiar anchors; only the variable parts regenerate | The entire screen rebuilt every visit; nothing to learn |
| **Correctness** | Generated controls validated against the guardrails before showing | Hallucinated buttons and mislabeled actions shipped raw |
| **Control** | User can fall back to a known, stable view | No escape hatch from a generated layout that missed |

---

## Anti-patterns

- **The bolt-on chatbot as "AI strategy."** A floating chat icon on an app that never uses the model in-context, where a copilot or inline assist would serve the actual task far better.
- **Cursor hijack.** Inline AI that inserts, jumps, or selects without an explicit user trigger — assistance experienced as interference.
- **Indistinguishable generation.** AI-written text or controls the user cannot tell apart from their own work, so they cannot review what the model contributed.
- **The shape-shifting UI.** A fully generated interface with no stable anchors — every visit is a fresh learning task, and efficiency never compounds.
- **Invisible mutation.** A copilot that changes the user's document without surfacing the change as something reviewable.
- **Generation without guardrails.** Treating "let the model build the UI" as the goal rather than the means — outcome-oriented design inverted into output-oriented chaos.

---

## The scoring test: is the AI serving the work, or replacing the interface?

1. **Right placement.** Does the AI sit where the task is (inline / side-panel on the user's real context), or is it a separate destination the user must detour to — and does that match the need?
2. **Propose, don't seize.** For inline AI: does it trigger explicitly and let the user accept or reject with one gesture, keeping the cursor? Or does it insert and hijack?
3. **Legible scope.** For copilots: can the user tell what context the assistant can see, and do its actions land as reviewable changes rather than silent mutations?
4. **Constraints, not just output.** For generative UI: has the team designed the _guardrails the model generates within_ (outcome-oriented), or just turned the model loose on the layout?
5. **Learnability survives.** Does enough of the interface stay stable for the user to build familiarity, with a fall-back to a known view — or does the UI reshuffle so often that efficiency never accrues?

A product passes when the AI lowers the cost of the user's real work while leaving them in control of the surface; it fails when "generative" becomes an end in itself and the user loses either their place or their grip on what changed.
