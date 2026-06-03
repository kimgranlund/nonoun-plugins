---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Nielsen Norman Group — Five Mistakes in Designing Mobile Push Notifications (nngroup.com/articles/push-notification)"
  - "Nielsen Norman Group — Indicators, Validations, and Notifications: Pick the Correct Communication Option (nngroup.com/articles/indicators-validations-notifications)"
  - "Nielsen Norman Group — Visibility of System Status (Usability Heuristic #1) (nngroup.com/articles/visibility-system-status)"
---

# Notifications

A notification is an interruption the product initiates to pull the user's attention to something that happened while they weren't looking — a reply, a status change, a deadline, a system event. NN/g's framing is unsparing: _"Any notification amounts to an interruption: it is meant to grab our attention and direct it to the notification. When the message is irrelevant to us, the interruption is irritating."_ That sentence is the whole discipline. Every notification spends a finite, non-replenishing resource — the user's attention and their willingness to keep notifications on — so the design question is never "can we notify?" but "is this worth an interruption, to this person, right now, on this channel?" Get the budget wrong and the user doesn't tune the volume down; they revoke permission and you lose the channel entirely.

---

## The attention budget (the core model)

Treat the user's tolerance for interruption as a **budget that depletes and does not refill on its own**:

- **Every notification is a withdrawal.** A relevant, well-timed one is a fair price for real value. An irrelevant one is theft — it spends attention and returns nothing, and it lowers the user's trust in the _next_ notification.
- **The budget is shared across all your notifications.** Low-value noise doesn't just annoy in the moment; it desensitizes the user to the high-value alert that comes later, and it pushes them toward the off switch. A pattern library should reason about a product's _total_ notification load, not each message in isolation.
- **When the budget is overspent, the user doesn't negotiate — they cut the cord.** They mute, disable, or uninstall. This makes restraint the highest-leverage notification design decision: **the best notification is often the one you choose not to send.**
- **Relevance is what makes a withdrawal fair.** NN/g's repeated theme: provide "relevant content aimed to inform and engage" rather than notifying about "every minor app occurrence." Relevance, timing, and personalization are how you keep withdrawals worth their cost.

---

## NN/g's five mistakes (the canonical failure list)

NN/g's "Five Mistakes in Designing Mobile Push Notifications" is the load-bearing source; each mistake has a direct fix.

| # | Mistake | Fix |
| --- | --- | --- |
| 1 | **Asking to enable notifications immediately on launch** — before the user knows what the app is. | Let users "experience the app" first; request permission later, once value is felt (reciprocity). This is permission priming. |
| 2 | **Not saying what notifications will contain.** | "Tell people what notifications will be about" — specificity raises opt-in rates and builds credibility. |
| 3 | **Sending notifications in bursts.** | "If you have more than five notifications that you need to send at once, combine them into a single message." Quality over quantity — this is batching. |
| 4 | **Sharing irrelevant content** — notifying about every minor event. | "Provide relevant content aimed to inform and engage"; curate. |
| 5 | **Making it hard to turn notifications off.** | "Allow users to edit their notification preferences within the app," not only at the OS level — granular, in-app control. |

These map cleanly onto the model: #1–#2 govern the **opt-in**, #3–#4 govern **what spends the budget**, and #5 governs **the user's control over the budget**.

---

## Opt-in done right (the permission prompt is a moment, not a formality)

The OS permission prompt is usually one-shot and effectively irreversible in the user's mind — a "No" is hard to reverse and many users never revisit it. So earn it:

- **Prime before you prompt.** Show a soft, in-app pre-permission explanation ("Turn on alerts so you know the moment your order ships?") _before_ triggering the OS dialog. If the user declines the soft ask, you haven't burned the real prompt and can ask again later.
- **Ask in context, after value.** Request permission at the moment notifications obviously help — right after the user does something whose follow-up they'd want pushed — not on first launch (NN/g mistake #1).
- **Name the payload.** Tell them what they'll get (NN/g mistake #2); "we'll let you know when X" beats a blank "Allow notifications?"
- **Make opt-out as easy as opt-in.** In-app, granular preferences (NN/g mistake #5) — per-category toggles, quiet hours — so the user can dial down rather than nuke the channel. A product that makes muting easy keeps more channels alive than one that makes it hard.

---

## Batching (defend the budget at the source)

Batching is the primary defense against burst-fatigue (NN/g mistake #3). Rather than firing one interruption per event, **aggregate** related events into a single, summarized notification:

- **Roll up volume.** "Sarah and 4 others commented on your post" is one interruption for five events; five separate pings is five withdrawals for the same news.
- **NN/g's explicit threshold:** more than five at once → combine into one. Treat that as a ceiling, not a target.
- **Digest the low-priority.** Batch non-urgent items into a periodic digest (daily/weekly) instead of a real-time stream; reserve real-time for the genuinely time-sensitive.
- **Window by relevance.** A reasonable batching policy holds and groups by type and a sending window so the user gets one coherent summary, not a drip. _(How aggressively to batch which categories is a product-specific tuning problem — there's no universal interval; choose by how time-sensitive each category is.)_
- **Respect quiet hours and timezone.** Don't deliver a 3 a.m. interruption; hold non-urgent notifications for waking hours and the user's local time.

---

## Channels (route by urgency and reversibility of attention)

A "notification" is not one thing — it spans channels with very different interruption costs and attention budgets. Route each message to the channel that matches its urgency; over-escalating (paging someone for a digest-worthy event) is itself a budget violation.

| Channel | Interruption cost | Fits | Watch for |
| --- | --- | --- | --- |
| **Push (mobile/desktop)** | High — interrupts outside the app. | Time-sensitive, personally relevant, actionable. | The harshest fatigue and revocation risk; reserve for value. |
| **In-app (inbox, badge, toast)** | Low — only while using the product. | Activity feeds, non-urgent status, contextual updates. | Badges that never clear; toasts used for things needing action (use the right element — see feedback reference). |
| **Email** | Low–medium, asynchronous. | Digests, receipts, things to keep/search later. | Becoming spam; honor unsubscribe; CAN-SPAM/GDPR obligations apply. |
| **SMS** | Very high, intimate, often metered. | OTP/2FA, critical time-sensitive alerts only. | Cost, regulation, deep intrusion — almost never for marketing. |

The cross-channel rule: **don't notify the same thing on every channel.** Hitting push + email + SMS for one event triples the withdrawal and trains the user to ignore — or disable — all three. Pick the lowest-cost channel that achieves the goal, and dedupe across channels.

---

## The notification-fatigue anti-pattern (named)

**Notification fatigue** is the failure mode the whole budget model is built to prevent: when a user receives too many low-value interruptions, they stop attending to _all_ of them — including the important ones — and ultimately mute, disable, or uninstall. It is a tragedy-of-the-commons inside one product: each individual "just one more notification" decision looks locally reasonable, and the aggregate destroys the channel.

Why it is insidious:

- **It's invisible in per-message metrics.** Each notification might show acceptable open rates while the _trend_ — rising mute/disable, falling overall engagement — quietly collapses. Measure the channel's health (opt-out rate, disable rate, per-user volume), not just per-send clicks.
- **It damages the high-value path.** The cost isn't the ignored noise; it's that the noise buried the one alert that mattered (the security warning, the about-to-expire deadline). Fatigue spends the trust the important message depended on.
- **It's usually driven by an engagement metric.** Notifications optimized purely for short-term re-engagement (sending more because more sends → more opens _today_) is the textbook road into fatigue and mass opt-out tomorrow. The honest metric is sustained, _opted-in_ engagement, not send volume.

The antidotes are everything above: ruthless relevance, batching, channel-routing by urgency, and easy granular control — plus the discipline to **not send.**

---

## Variants

- **Transactional vs promotional.** Transactional (receipt, password reset, shipping update — the user expects it) vs promotional (re-engagement, marketing). They carry different consent, regulatory, and tolerance profiles; conflating them, or smuggling marketing into a transactional channel, burns trust.
- **System-status vs activity vs marketing.** "Your export is ready" (status) · "Sarah mentioned you" (activity/social) · "Come back, you've been missed" (marketing) — distinct value to the user and distinct fatigue risk.
- **Notification inbox / center.** A persistent in-app list that lets the user catch up on their own schedule, lowering the need to push everything in real time.
- **Badges and counts.** A low-interruption ambient signal; design clear-on-view rules so a badge that never resets doesn't become learned noise.
- **Actionable / rich notifications.** Reply or approve from the notification itself — high value when the action is genuinely one-step, and worth a higher interruption cost.

---

## Anti-patterns

- **Permission prompt on first launch.** NN/g mistake #1 — asking before value is demonstrated, burning the one-shot OS prompt.
- **Burst firing.** A stream of separate pings for related events instead of one batched summary (NN/g mistake #3).
- **Irrelevant "every event" notifications.** Notifying about minor occurrences nobody asked about (NN/g mistake #4) — the core driver of fatigue.
- **Buried off switch.** Forcing the user to OS settings to mute, with no in-app or granular control (NN/g mistake #5).
- **Cross-channel duplication.** The same event on push + email + SMS.
- **Re-engagement spam.** "We miss you" loops optimized for send volume; the classic fatigue-and-uninstall pipeline.
- **Badge that never clears / count that lies.** Ambient signals that lose meaning and become noise.
- **3 a.m. non-urgent push.** Ignoring quiet hours and timezone.

---

## Accessibility

- **In-app notifications must reach assistive tech.** A toast or banner that appears must be in an ARIA live region — `role="status"` (polite) for routine confirmations, `role="alert"` (assertive) for the rare urgent message that must interrupt — or a screen-reader user never learns it appeared. (Mechanics in the feedback reference.)
- **Don't auto-dismiss faster than people can perceive and act.** A transient in-app notification that vanishes on a timer can be unreadable for users who read slowly, use a screen reader, or have cognitive disabilities; provide a persistent inbox/center as the durable record, and make any action available there too — never _only_ in a fleeting toast (WCAG-aligned: don't make essential info time-limited without an alternative).
- **Color and sound are not the only signal.** Notification importance conveyed solely by a red dot or a chime excludes color-blind and Deaf/hard-of-hearing users; pair with text and an icon shape.
- **Honor OS-level reduced-motion and Do-Not-Disturb / focus modes.** Animated in-app alerts should respect `prefers-reduced-motion`, and the product should defer to the platform's quiet-hours/DND state rather than overriding it.

---

## Good vs bad (for scoring)

```text
BAD                                   GOOD
──────────────────────────────────    ──────────────────────────────────
On first launch:                      After first useful action:
"Allow notifications?"                "Want a heads-up the moment your
(no value yet; one-shot prompt        report finishes? We'll only ping you
 burned)                               for that."  → then OS prompt

5 separate pings:                      1 batched ping:
"Ann liked your post"                 "Ann and 4 others liked your post"
"Bo liked your post" … (×5)
(burst fatigue)

Same event via push + email + SMS     One channel, routed by urgency;
(triple withdrawal)                    in-app inbox holds the rest

Toast "Saved" disappears in 2s,       role="status" toast "Saved" + a
nothing in the AT tree, no inbox      persistent activity inbox as the
(invisible to screen readers)          durable, accessible record
```

A scoring heuristic: for each notification ask (1) is it relevant and worth an interruption _to this user now_; (2) is it batched rather than burst; (3) is it on the lowest-cost channel that works, and not duplicated across channels; (4) can the user opt in with priming and opt out granularly in-app; and (5) does it reach assistive tech and survive in a durable inbox rather than only as a fleeting toast. Track channel health (opt-out/disable rate, per-user volume), not just per-send opens.
