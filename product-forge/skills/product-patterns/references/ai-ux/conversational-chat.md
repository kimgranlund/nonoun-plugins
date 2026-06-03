---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Georgia Kenderova, Maria Rosala & Tanner Kohler, '10 Guidelines for Designing Your Site's AI Chatbots', Nielsen Norman Group (nngroup.com/articles/ai-chatbots-design-guidelines), 2026-04-24"
  - "Raluca Budiu, Feifei Liu, Emma Cionca & Amy Zhang, 'The 6 Types of Conversations with Generative AI', Nielsen Norman Group (nngroup.com/articles/AI-conversation-types), 2023-11-10"
  - "Megan Chan, 'Explainable AI in Chat Interfaces', Nielsen Norman Group (nngroup.com/articles/explainable-ai), 2025-12-12"
---

# Conversational & Chat UX

The chat surface is the default form of an AI product and the easiest one to ship badly. A text box and a stream of tokens is trivial to stand up; a conversation a user can _steer, read, recover from, and reuse_ is not. This reference covers the durable affordances of a chat interface — prompt entry, streaming output, message history, follow-ups and suggested prompts, and per-message controls — with the canonical form for each and the anti-patterns that NN/g has documented in the wild. The discipline applies whether the chat is the whole product or a panel bolted onto an existing app.

> The framing to hold onto: **a chat box is an unbounded input with no affordances of its own.** A blank prompt field communicates nothing about what the system can do, how to ask well, or what will happen next. Every guideline below exists to put the missing affordances back — discoverability, readability, steerability, and reuse — onto a surface that ships without them by default.

---

## When to use a chat interface

Chat earns its place when the user's need is **open-ended, hard to express as a form, or genuinely conversational** — refining an answer over several turns, exploring a space the user cannot pre-specify, or composing something with the model's help. NN/g's analysis of 425 real interactions with ChatGPT, Bard, and Bing Chat found six distinct conversation shapes (search queries, funneling, exploring, chiseling, pinpointing, expanding), and concluded that "different conversation types serve distinct information needs and demand varied UI designs." The same study found that **conversation length does not indicate success** — both short and long exchanges effectively serve different goals — so do not optimize a chat for turn count in either direction.

Chat is the _wrong_ default when the task is well-structured and repeatable. If the user always supplies the same three parameters, a form is faster, more learnable, and less error-prone than free text; if the output is a known artifact, a generated panel beats a paragraph describing it (see the generative-UI reference). Reach for chat for the long tail of intent, not for tasks a button already handles.

---

## Prompt entry

The input is where steerability is won or lost. The empty state must teach: an opening message should "clearly and concisely indicate what it can do" and name specific topics, because — in NN/g's words — "vague greetings leave users guessing." Replace "Ask me anything" with two or three concrete starting points. NN/g also recommends offering **voice input** where feasible, calling its absence "a dealbreaker" for some users on accessibility grounds.

Canonical form:

```text
┌─────────────────────────────────────────────┐
│  Hi — I can help you:                         │
│   • [ Draft a reply to this thread ]          │  ← suggested prompts as buttons
│   • [ Summarize the last 20 messages ]        │
│   • [ Find the decision we made about X ]     │
├─────────────────────────────────────────────┤
│  Type a message…                        [ ↑ ] │  ← multiline, Enter-to-send,
│                                    [ 🎤 voice ]│     Shift+Enter for newline
└─────────────────────────────────────────────┘
```

The input should grow to multiple lines for longer prompts, make the send affordance obvious, and — for any non-trivial composer — distinguish "send" from "new line" so a user does not fire a half-written prompt by reflex.

---

## Streaming responses

Streaming (rendering tokens as they are generated) is the right default: it lowers perceived latency and signals liveness. But it interacts badly with reading, and NN/g has named the failure precisely. **Do not autoscroll the user to the end of a streaming response.** Users "expect to read from the beginning, not work backwards"; a chat that yanks the viewport to the tail of a long answer forces them to scroll back up and refind their place. NN/g's field example is the Mississippi state chatbot MISSI, which autoscrolled to the end of long streamed answers and made them impossible to read until generation stopped.

| Lever | Good — readable stream | Bad — disorienting stream |
| --- | --- | --- |
| **Scroll behavior** | Pin the viewport to the _start_ of the new message; let the user scroll down as they read | Autoscroll to the bottom on every token, dragging the user past unread text |
| **Stop control** | A visible "Stop generating" while streaming | No way to halt a wrong or runaway answer |
| **Long output** | Progressive disclosure — summarize, then "show more" — to keep the chat short | A wall of streamed text the user must scroll through to find the answer |
| **Completion** | Per-message controls appear once the message finishes | Controls flicker in mid-stream or never appear |

A stopped or completed message should be a stable, addressable unit — not a moving target.

---

## Message history

The transcript is the conversation's working memory and the user's. Keep it scannable: clearly attribute each turn to user or assistant, preserve order, and let long answers collapse via progressive disclosure rather than dominating the scroll. NN/g's chatbot guidelines call for keeping the chat **accessible across pages** (the conversation should not evaporate when the user navigates) and for letting users **resize the chat window** so the history is legible at the size the task needs. When the chat lives inside a larger app, decide deliberately whether history is ephemeral (cleared per session) or persistent (a named, returnable thread) — and tell the user which, so they are not surprised by what survives a reload.

---

## Follow-ups and suggested prompts

Suggested prompts do double duty: they advertise capability and they lower the cost of the next turn. Two NN/g rules govern them. First, **offer suggestions as buttons, not text** — clickable chips "reduce typing burden" and remove the ambiguity of whether a printed example is something to click or merely read. Second, **keep follow-ups relevant and context-aware**: they should "update based on the conversation context," and stale or repetitive suggestions read as "pushy and inattentive." A good follow-up reflects where the conversation actually went; a bad one re-offers the same three openers after ten turns.

| Lever | Good | Bad |
| --- | --- | --- |
| **Affordance** | Clickable buttons / chips | Example prompts printed as plain text |
| **Relevance** | Follow-ups derived from the current thread | Fixed list that never changes turn to turn |
| **Quantity** | A small, curated set (≈3) | A dozen suggestions that bury the input |
| **Tone** | Optional next steps the user can ignore | Repetitive nudges that feel pushy |

---

## Per-message affordances

Once a message is complete, the user needs to _act on it_ — not just read it. The conventional, now near-universal control set: **copy**, **regenerate**, **edit** (re-run a prior user turn with a changed prompt), and **save / share / download** the output. NN/g specifically recommends providing a way to "save, download, or share" when the chat produces "content that users may want to reference later." Two adjacent moves strengthen the set: a **thumbs-up / thumbs-down** feedback control that visibly feeds the system, and — where the answer makes a factual claim — inline sources placed next to the claim they support (the citations reference covers this in depth).

A grounded caution on "regenerate" and "show the reasoning": NN/g's explainable-AI guidance argues that step-by-step "here's how I thought about it" walkthroughs can mislead, because "explanations are often unfaithful to the model's actual computation." Prefer affordances that let the user _verify and redirect_ (sources, edit, regenerate) over ones that perform a possibly-fictional account of the model's internal process.

| Affordance | Job | Anti-pattern it prevents |
| --- | --- | --- |
| **Copy** | Move the output into the user's real workflow | Manual reselection of streamed text |
| **Regenerate** | Get an alternative without re-typing | Re-asking the same question by hand |
| **Edit prompt** | Steer by correcting the input, not arguing with the output | Long corrective sub-threads that drift |
| **Save / share / download** | Preserve reusable output | Losing a good answer to scroll or reload |
| **Feedback (👍/👎)** | A visible channel that shapes the system | Silent dissatisfaction, no signal |

---

## Anti-patterns

- **The blank box.** A naked prompt field with a generic greeting and no suggested prompts — maximum freedom, zero discoverability. Users guess, mis-ask, and conclude the product is weak.
- **Autoscroll-to-bottom on stream.** The single most-cited streaming defect (NN/g): the viewport chases the tail of the answer and the user can never read from the top.
- **No stop control.** A wrong or runaway answer the user must wait out, then scroll past.
- **Static, repetitive suggestions.** Follow-ups that never reflect the conversation — "pushy and inattentive," per NN/g.
- **Ephemeral-by-surprise history.** A conversation the user assumed was saved, gone on reload, with no prior signal.
- **Reasoning-as-theater.** A step-by-step "chain of thought" presented as a faithful explanation when it is a post-hoc narration — overtrust dressed as transparency.

---

## The scoring test: is this a steerable conversation or a token firehose?

1. **Discoverability.** Does the empty state name specific things the system can do, or does it say "ask me anything"? Are suggested prompts clickable buttons, not printed text?
2. **Readability under stream.** When a long answer streams in, does the viewport stay at the _start_ of the message — or does it autoscroll to the bottom and force the user to backtrack? Is there a "Stop generating" control?
3. **Steerability.** Can the user edit a prior prompt and re-run it, regenerate an answer, and follow context-aware suggestions — or is every correction a fresh hand-typed turn?
4. **Reusability.** Can the user copy, save, or share an answer they want to keep? Does anything survive a navigation or reload, and is that behavior signaled?
5. **Honest framing.** Where the answer asserts facts, are sources offered next to the claim? Does the UI avoid presenting a step-by-step "reasoning" trace as if it were a faithful account of the model's computation?

A chat that fails (1) ships without affordances; one that fails (2) is unreadable the moment answers get long; one that fails (3) cannot be steered and degrades into argument. Conversational quality is the sum of these, not the eloquence of any single answer.
