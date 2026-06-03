---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Jesse G., *The Elements of User Experience* (New Riders, 2002/2010) — the surface plane and the distinction between structure, skeleton, and surface."
  - "Nielsen Norman Group — Channels, Devices, Touchpoints, and Cross-Channel Experiences (nngroup.com/articles/channels-devices-touchpoints) and Omnichannel UX guidance."
  - "Scott Hurff, *Designing Products People Love* (O'Reilly, 2016) — surface/screen states (the UI Stack), referenced for screen-level inventory."
  - "Jaime Levy, *UX Strategy* (O'Reilly, 2015) — multi-platform / multi-device product surface planning."
---

# Surfaces & Screens

This is the working method for treating the set of **surfaces** a product occupies as an architectural decision rather than an accident of feature growth. A surface is any place the product appears to or acts on the user: a web app, a mobile app, an email, a push notification, an SMS, a widget, a watch complication, a printed receipt, a voice response, a third-party embed. Modern products are almost never one surface — they are a constellation — and the architectural questions are: **which surfaces does this product occupy, what job does each one own, and how do they cohere into one product rather than fragmenting into several disconnected ones?** The tell of unarchitected surfaces is duplication and contradiction: the same job done three ways across three surfaces, or a notification that promises something the destination screen can't deliver. The tell of good surface architecture is that each surface has a clear, distinct job and they hand off cleanly.

## Surface vs. screen vs. channel (precise terms)

These three get used interchangeably and shouldn't be.

| Term | Means | Granularity |
| --- | --- | --- |
| **Channel** | The medium / context of reach (web, mobile, email, in-store, voice) — often org-owned | Coarsest |
| **Surface** | A distinct rendered place the product appears within a channel (the web app, a marketing email, a push notification, a home-screen widget) | Mid |
| **Screen / view** | A single composed view within a surface (the dashboard screen, the settings screen) | Finest |

Garrett's planes apply at the screen level (a screen is structure → skeleton → surface in his sense of "surface" as the sensory layer); _this_ reference uses "surface" in the product-architecture sense — a whole place the product lives. The distinction matters because the decisions differ: which **channels** to be in is strategy; which **surfaces** within them and what each owns is experience architecture; what each **screen** looks like is interaction/visual design.

## The surface inventory

The foundational artifact is a complete inventory of every surface the product touches — including the ones nobody "designed," like transactional emails and system notifications, which are often the most-seen surfaces of all. Build it as a table:

```text
   SURFACE              REACH / CONTEXT          JOB IT OWNS                    ENTRY → EXIT
   ──────────────────── ──────────────────────── ────────────────────────────── ─────────────────
   Web app              desk, focused, long       deep work; full feature set    direct / from email
   Mobile app           on-the-go, glanceable     capture + check; quick actions  app icon / push
   Push notification    interrupt, 1-line         re-engage on time-critical event → deep-links into app
   Transactional email  inbox, durable record     confirm + receipt + recovery    → web app for detail
   Marketing email      inbox, promotional        prompt a return visit           → landing/web
   Home-screen widget   ambient, zero-tap         show status without opening      → opens app to detail
   SMS                  universal, urgent         2FA, critical alerts only        (often terminal)
```

The inventory forces three realizations: how many surfaces actually exist (usually more than the team tracks), which are undesigned (the inherited email templates), and where two surfaces are doing the same job (duplication to consolidate).

## Surface strategy: which job each surface owns

The core discipline is **single ownership of jobs across surfaces.** Each surface should own a job it is _uniquely good at_ given its context — and not redundantly re-implement jobs another surface owns better. The fit is dictated by the surface's intrinsic properties:

- **Context of use:** focused/long (web app on a desk) vs. interrupted/short (mobile, notification). Deep, multi-step work belongs on the surface where the user has attention and screen space; quick capture and status checks belong on the glanceable surface.
- **Interaction budget:** how much the user can realistically do here. A push notification owns _one_ action (the tap); an email owns a read plus maybe one CTA; a full app owns the entire workflow. Asking a low-budget surface to do a high-budget job (a complex form in an SMS) is a category error.
- **Persistence:** ephemeral (notification, gone in seconds) vs. durable (email, kept as a record). Receipts and confirmations belong on durable surfaces; time-critical nudges on ephemeral ones.
- **Reach / universality:** SMS reaches everyone but is expensive and intrusive — reserve it for the critical few (2FA, "your driver is here"). Push requires opt-in and an installed app.

The architectural rule: **assign each job to the surface whose properties fit it, and let other surfaces _point to_ that surface rather than duplicate it.** A notification doesn't contain the workflow — it deep-links to the surface that owns it. An email doesn't reimplement the dashboard — it summarizes and links. This is the surface-level expression of the same DRY discipline that governs good navigation and flows.

## Coherence across surfaces (one product, many places)

The risk of a multi-surface product is fragmentation — it stops feeling like one product. NN/g's omnichannel guidance frames the target: surfaces should be **consistent** (same model, terms, and state) and the experience should be **continuous** across them (a job started on one can be continued on another — see `states-and-continuity.md`). Concretely:

- **Shared mental model and vocabulary.** The same concept is named the same word on every surface. A "project" in the app is not a "workspace" in the email.
- **Shared state.** An action on one surface is reflected on the others without the user re-doing it. Dismiss a notification, mark a task done in the widget — the app knows.
- **Clean hand-offs.** When a surface points to another (notification → app screen), it deep-links to the _exact_ place that fulfills the promise the first surface made. The most common cross-surface defect is the **broken promise**: a notification or email says "your report is ready" and the link dumps the user on a generic home screen, forcing them to hunt. The hand-off must land on the specific destination.
- **Right surface for the moment.** Don't push to every surface at once (notification + email + SMS for the same event is spam); choose the surface that fits the moment's urgency and the user's likely context.

## Procedure

1. **Inventory every surface,** including undesigned/inherited ones (transactional emails, system notifications).
2. **Tag each with its intrinsic properties** (context, interaction budget, persistence, reach).
3. **Assign each job to one owning surface** based on fit; flag any job owned by two surfaces as duplication to resolve.
4. **Define the hand-offs:** for every surface that points to another, specify the exact destination, and verify the promise the source makes is fulfilled there.
5. **Establish the shared model:** one vocabulary, one state, applied across all surfaces.
6. **Prune.** Kill or merge surfaces that own no distinct job; silence channels that fire redundantly.

## What to check (good vs. bad)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Inventory** | Team can't list all surfaces; emails/notifications "just exist" | Complete inventory including inherited surfaces |
| **Job ownership** | Same job done several ways across surfaces | Each job owned by the one surface that fits it best |
| **Fit** | Complex workflow crammed into a low-budget surface (form in SMS) | Job matched to the surface's interaction budget and context |
| **Hand-offs** | Notification/email links to a generic home; user hunts | Deep-link lands on the exact destination that fulfills the promise |
| **Vocabulary** | A concept renamed per surface | One word per concept across every surface |
| **State** | Action on one surface invisible on others | Shared state; an action propagates |
| **Channel discipline** | Push + email + SMS for the same event | One surface per moment, sized to urgency/context |
| **Pruning** | Surfaces that own no distinct job linger | Redundant surfaces merged or removed |

The fastest single test: pick the product's most common real event (a completed task, a received message) and trace which surfaces fire and where each link lands. Redundant fires and links that don't land on the promised destination are the two defects this discipline exists to catch.

## One labeled caveat

The surface/screen/channel distinction and the surface-strategy heuristics (context, interaction budget, persistence, reach) are synthesized from cross-channel/omnichannel UX practice (NN/g) and multi-platform UX-strategy writing (Levy) rather than from a single canonical named framework — they are presented here as working method, well-grounded in the cited sources but not a verbatim model from one author. Garrett's surface plane is cited precisely (the sensory layer of a screen) and should not be confused with this reference's product-level use of "surface." Hurff's UI Stack is referenced only for the screen-state inventory it supplies (covered fully in `states-and-continuity.md`). The "broken promise" hand-off defect is a named-here observation, not a cited term; confirm any specific omnichannel statistic against NN/g's current articles before publication.
