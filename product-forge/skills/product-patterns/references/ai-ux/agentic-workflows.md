---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Erik Schluntz & Barry Zhang, 'Building Effective Agents', Anthropic (anthropic.com/research/building-effective-agents), 2024-12-19"
  - "Greg Nudelman, 'Secrets of Agentic UX: Emerging Design Patterns for Human Interaction with AI Agents', UX Magazine (uxmag.com/articles/secrets-of-agentic-ux-emerging-design-patterns-for-human-interaction-with-ai-agents), 2025-04-22"
  - "Victor Yocco, 'Designing For Agentic AI: Practical UX Patterns For Control, Consent, And Accountability', Smashing Magazine (smashingmagazine.com/2026/02/designing-agentic-ai-practical-ux-patterns), 2026-02-11"
  - "Saranya Gunasekaran, 'Designing for Autonomy: UX Principles for Agentic AI', UXmatters (uxmatters.com/mt/archives/2025/12/designing-for-autonomy-ux-principles-for-agentic-ai.php), 2025-12-15"
---

# Agentic Workflows

An agentic product does not answer a question — it pursues a goal across multiple steps, choosing actions and using tools along the way. That shift breaks the request/response contract chat and forms rely on: the user is no longer issuing one instruction and reading one reply, but **delegating an outcome** and then overseeing a process that runs on its own. This reference covers the UX of that delegation — the autonomy dial, the in-the-loop / on-the-loop distinction, the plan→preview→commit shape, the controls that let a user pause, override, and interrupt, and how to make an agent's progress visible. The companion trust-control-steerability reference covers _how much_ autonomy to grant; this one covers the mechanics of running an agent at any setting.

> The framing to hold onto, from UXmatters: the design shift is "from interaction to delegation," where users "express intentions rather than give instructions." The interface's job is no longer to take a command and return a result, but to let a human **set a goal, watch it being pursued, and step in** — which means an agentic UI lives or dies on visibility and intervention, not on the quality of any single output.

This is an **emerging area.** Anthropic's engineering guidance on agent construction is durable and well-sourced; the named UX patterns below come from a small set of recent named-author posts (Nudelman, Yocco, Gunasekaran) and are consolidating conventions, not settled standards. Pattern _names_ in particular vary by author — treat them as labels for a recognizable shape, not canon.

---

## The autonomy dial

Autonomy is not binary. Yocco's "Autonomy Dial (Progressive Authorization)" pattern makes the point sharply — "trust is not a binary switch; it's a spectrum" — and gives a concrete four-stop scale the user (or admin) sets per task type:

```text
Observe & Suggest  →  Plan & Propose  →  Act with Confirmation  →  Act Autonomously
   (read-only)         (drafts a plan)     (does it, asks first)      (does it, reports after)
   lowest autonomy ─────────────────────────────────────────────► highest autonomy
```

The dial is the central agentic control because it lets one product serve a nervous first-time user and a power user who has earned trust in the same flow, without forking the experience. Gunasekaran frames the same continuum as autonomy "on a spectrum between complete human control and full AI autonomy," with UX safeguards "distributed across this range rather than clustered at either extreme." The design imperative: **expose the dial, default it conservatively, and let trust move it up** — never ship a single fixed autonomy level for tasks of wildly different stakes.

---

## In-the-loop vs on-the-loop

Two oversight postures, often conflated, do different jobs:

| Posture | The human's role | Cadence | Fits |
| --- | --- | --- | --- |
| **Human-in-the-loop** | An approver inside the decision path — the agent _stops_ and waits for a human before a consequential step | Synchronous; the agent blocks on the human | Consequential, hard-to-reverse, or low-confidence actions |
| **Human-on-the-loop** | A supervisor watching a running process, able to intervene but not gating each step | Asynchronous; the agent proceeds, the human can interrupt | High-volume, lower-stakes, or well-trusted tasks |

Nudelman's field observation is that effective agentic UX treats these as a **dynamic** relationship, not a fixed choice: at lower autonomy the human is an operator (in the loop, approving), and "as confidence and system performance increase, the human transitions into a supervisory role" (on the loop, monitoring). The posture should track the autonomy dial — turning the dial up moves the human from in-loop to on-loop. The design failure is picking one posture globally: in-the-loop everywhere produces approval fatigue (see the human-in-the-loop reference); on-the-loop everywhere lets the agent take irreversible actions unwatched.

---

## Plan → preview → commit

The single most important agentic pattern, and the one with the strongest grounding. Yocco names the pre-action half "Intent Preview (Plan Summary)": before acting, the agent shows "sequential steps, clear outcomes in plain language" and offers explicit decision points — "Proceed," "Edit Plan," or "Handle it Myself." Anthropic's "Building Effective Agents" frames the same discipline from the engineering side — "prioritize transparency by explicitly showing the agent's planning steps" — and the production embodiment is Claude Code's plan mode, where the agent drafts the full plan (files it will change, commands it will run), the user reviews, edits, or rejects it, and **only then** does the agent execute. This plan-then-act shape is the repo's own AI-UX stance made concrete, and a good external benchmark for what "showing the plan" looks like in a shipped tool.

```text
   PLAN                    PREVIEW                       COMMIT
   ────                    ───────                       ──────
   agent drafts            human reviews the plan:       agent executes
   the steps it            ┌─────────────────────────┐   the approved plan,
   intends to take    →    │ [ Proceed ]             │   surfacing progress
                           │ [ Edit plan ]           │ → and stopping at
                           │ [ Do it myself ]        │   the next checkpoint
                           │ [ Ask: why this step? ] │
                           └─────────────────────────┘
                           ↑ informed consent BEFORE action
```

Yocco's "Explainable Rationale" pattern handles the questions a preview invites — answering "Why?" with a "'Because you said X, I did Y' structure" that links each step back to the user's stated intent. The preview earns its keep only if the user can _act_ on it: a plan they can read but not edit is a notification, not consent.

---

## Pause, override, interrupt

A running agent the user cannot stop is the canonical agentic nightmare — Nudelman invokes "The Sorcerer's Apprentice." His baseline: "start, stop, and pause buttons are a good starting point for controlling the agentic flow." Gunasekaran makes the deeper, well-stated point about _perceived_ control: "A system that allows intervention even if the user rarely needs it feels trustworthy. A system that the user cannot interrupt, override, or question quickly becomes threatening." Override controls "must be visible, not hidden" — the stop button cannot be three menus deep, because the moment a user needs it is the moment they have no patience to find it.

| Control | What it does | Why it matters |
| --- | --- | --- |
| **Pause** | Suspend a running agent mid-process | Lets the user think without losing the agent's state |
| **Stop / abort** | End the run now | The escape hatch from a wrong or runaway agent |
| **Override** | Correct or replace what the agent is doing | Keeps the human in authority, not just in attendance |
| **Escalation** | The _agent_ stops and asks the human | Yocco: "a smart partner knows when to ask for help instead of guessing" |

Escalation is the underrated one: the best agents route ambiguous or high-stakes decisions back to the human _proactively_, rather than guessing and forcing the human to catch it after.

---

## Showing agent progress

An agent working invisibly creates anxiety, not confidence. Gunasekaran: feedback "transforms invisible processing into a visible, understandable narrative," and autonomous systems operating silently "create anxiety." Nudelman's field note adds a realism check — findings "do not come immediately after the investigation is launched"; the panel starts empty and fills as the agent works, and the UI must communicate that honestly rather than feign instant results.

| Lever | Good — legible progress | Bad — opaque process |
| --- | --- | --- |
| **State** | Current step named ("Searching the codebase…", "Drafting the reply…") | A spinner with no indication of what is happening |
| **Trajectory** | The plan shown with steps checking off as they complete | No relationship between the spinner and the promised plan |
| **Empty start** | Honest "no findings yet — still working" | A blank panel that reads as broken or done |
| **Long runs** | Streamed intermediate results / a running log | Total silence until a final dump |

The standard: a user glancing at a running agent should be able to answer "what is it doing, how far has it got, and is it stuck?" without clicking anything.

---

## Anti-patterns

- **Fixed global autonomy.** One autonomy level for every task — either so timid the agent is useless on trusted work, or so bold it takes irreversible actions on risky work. Ship the dial.
- **Plan-as-notification.** Showing a plan the user can read but not edit or reject before execution. That is informed _notice_, not informed _consent_.
- **The unstoppable agent.** No visible stop/pause, or controls buried where a panicking user cannot reach them — the Sorcerer's Apprentice.
- **Silent running.** An agent that shows a spinner and nothing else, leaving the user unsure whether it is working, stuck, or finished.
- **Guess-don't-ask.** An agent that resolves ambiguity by guessing and acting, instead of escalating to the human — forcing the user to catch errors after the fact.
- **In-the-loop everywhere.** Gating every trivial step behind a human approval, training the user to rubber-stamp (see the human-in-the-loop reference).

---

## The scoring test: can the user delegate _and_ stay in command?

1. **Autonomy is adjustable.** Is there a visible dial (or equivalent) that sets how much the agent does on its own, defaulted conservatively — or one fixed level for all tasks?
2. **Consent before consequence.** For non-trivial actions, does the agent show a plan the user can review, edit, _and_ reject before it acts — or does it act first and report after?
3. **Interruptible.** Can the user pause, stop, and override a running agent through visible, immediate controls? Does the agent itself escalate ambiguous or high-stakes calls rather than guessing?
4. **Posture matches stakes.** Is the human in-the-loop (gating) for consequential steps and on-the-loop (supervising) for routine ones — or one posture forced everywhere?
5. **Progress is legible.** Can a user tell what the agent is doing, how far it has got, and whether it is stuck, at a glance?

An agentic product passes when delegation does not cost the user authority: they hand off the work, watch it happen, and can step in at any moment. It fails when "agentic" means the user has surrendered the wheel and can only watch.
