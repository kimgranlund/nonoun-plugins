---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Sarah Tavel, 'The Hierarchy of Engagement', Greylock / Medium. https://sarahtavel.medium.com/the-hierarchy-of-engagement-expanded-648329d60804"
  - "OpenView Partners, 'Product-Led Growth'. https://openviewpartners.com/product-led-growth/ — origin of the PLG term and the land-and-expand seat-expansion motion"
  - "Pocus, 'Running a Seat Expansion Playbook'. https://www.pocus.com/playbook/running-a-seat-expansion-playbook"
  - "Sujeet Jaiswal, 'Figma: Building Multiplayer Infrastructure for Real-Time Design Collaboration'. https://sujeet.pro/articles/figma-multiplayer-infrastructure"
  - "Slack, 'An introduction to Slack Enterprise Grid' and 'Manage members with SCIM provisioning'. https://slack.com/resources/why-use-slack/slack-enterprise-grid"
  - "Jay Kapoor, 'Consumerization of Enterprise Software — Part I', Medium. https://medium.com/jaykapoornyc/consumerization-of-enterprise-software-part-i-7b48274889f6 — the buyer-vs-user split"
---

# Workplace collaboration

Workplace-collaboration apps — Figma, Notion, Slack, Linear, Miro, Google Docs — are tools whose value comes from being used _together_. The defining property is that a single user gets little value; a team gets compounding value. This reverses the design center of gravity of single-player software: the unit that retains is not the user but the **workspace**, and the growth loop is not acquisition but **invitation**. This reference covers the conventions that follow from multiplayer value (presence, permissions, notifications), the metrics that actually track health (seat expansion and net dollar retention, not raw signups), and the structural tension every one of these products must resolve — that the person who pays is rarely the person who uses.

> The one-line frame: in collaboration software, **the workspace is the retaining unit and the invite is the growth loop.** Optimize the team's value-per-collaborator, and seats, retention, and revenue follow. Optimize signups, and you fill a leaky bucket.

## Conventions: what these apps have in common

A handful of capabilities recur across the genre because they are load-bearing for _multiplayer_ value, not because they are fashionable. Treat their absence as a smell, not their presence as a feature.

- **Multiplayer-by-default editing.** Two or more people can act in the same artifact at once. The hard engineering problem is conflict resolution: when two people change the same thing, whose change wins? Figma's published architecture keeps authoritative document state on a central server as a map of object → property → value, resolves conflicts **last-write-wins at the property level**, and only uses CRDT-like structures where the domain needs them — a deliberately _simpler_ choice than full operational transform, justified by Figma's having both a central server and natural property-level granularity (Jaiswal, Figma multiplayer infrastructure). The lesson is architectural humility: pick the weakest consistency model the domain tolerates.
- **Presence.** Who else is here, where are they, what are they doing. Figma coalesces cursor movements and ships them at roughly 33 ms intervals to keep presence frames small and avoid head-of-line blocking on the document socket, then interpolates client-side inside `requestAnimationFrame` for smooth ~60 Hz cursors over a ~30 Hz wire rate (Jaiswal). Presence is cheap to underbuild and expensive to retrofit: it is the signal that makes a space feel _inhabited_.
- **Permissions and roles (RBAC).** Who can view, comment, edit, share, administer. Role-based access control groups permissions into roles (viewer / commenter / editor / admin / owner) rather than assigning them per-user, which is what makes permissioning tractable as a workspace grows. Sharing scope (private → team → org → public-link) is the other half and is a frequent source of security incidents when defaults are too open.
- **Comments, mentions, and async threads.** Collaboration is mostly asynchronous; synchronous co-editing is the exception. The comment-and-`@mention` surface is where most collaboration actually happens, and the `@mention` is also a growth lever — it pulls a not-yet-active colleague into the artifact.
- **Notifications.** The nervous system connecting async work — and the most over-used surface in the genre (see Pitfalls).
- **An admin/governance plane.** Distinct from the user plane: SSO, SCIM provisioning, audit logs, retention policies, role administration. This is what an org buys; it is invisible to the daily user (see the admin-vs-user split).

## Signature patterns

- **Invite-as-growth-loop.** The product's primary acquisition channel is its own users inviting collaborators; the `@mention`, the "share" button, and "X is waiting for you to respond" are the loop's triggers. This is the engine behind PLG land-and-expand: products win expansion by making it _frictionless and natural_ to invite teammates (the pattern OpenView and Pocus document across Figma, Notion, Miro). Reported anecdote: Miro teams growing from roughly 3 → 10 seats within ~45 days on the strength of invite-driven collaboration (Pocus; single-source, treat as illustrative not benchmark).
- **Land small, expand by seats.** The PLG motion lands a single team or even a single user on a free or cheap tier, then expands seat-by-seat as collaboration spreads — ideally without a salesperson touching the account. OpenView frames "land and expand" as the defining PLG revenue shape; the land deal is typically a fraction of the account's eventual potential.
- **Free-tier / freemium as distribution.** A generous individual or small-team free tier is a distribution channel, not charity: it seeds the workspace so the invite loop can run. The monetization line is usually drawn at _team scale_, _admin/governance features_, or _usage limits_, not at core single-player function.
- **The consumerized enterprise tool.** These apps look and feel like consumer software (instant, beautiful, no training) precisely because they enter the org bottom-up through end users, not top-down through a CIO purchase (Kapoor). The polish is a go-to-market strategy.

## Key metrics

The metric that matters is **value-per-workspace over time**, proxied by retention and expansion of _teams_, not counts of _individuals_.

| Metric | What it measures | Why it matters here |
| --- | --- | --- |
| **Net dollar retention (NDR / NRR)** | Revenue retained + expanded from existing accounts, net of churn and contraction | The genre's headline metric: it captures seat expansion, the whole point of land-and-expand. Best-in-class PLG companies are widely reported at ~120–150% NDR (Pocus; varies by source and cohort) |
| **Seats per account / seat expansion rate** | How a workspace grows in collaborators over time | The leading indicator of NDR; a flat seat count is a stalled land-and-expand |
| **Weekly active workspaces / collaborating teams** | Workspaces with ≥2 active collaborators in the period | Closer to real value than user MAU — a workspace of one is not collaborating |
| **Invite acceptance / activation-to-collaboration** | Share of invites that convert to active collaborators | The health of the growth loop itself |
| **Workspace (team-level) retention** | Whether a _team_ is still active months later | The retaining unit is the workspace; individual churn within a healthy workspace is normal |

A reusable rule: **measure the team, not the seat.** A product can show flat or growing individual MAU while every _workspace_ slowly dies (members leave faster than they are replaced). Cohort the retention curve by workspace.

## Pitfalls

- **The single-player trap.** Shipping a great solo experience and assuming collaboration will follow. The genre's value is multiplayer; if a second user adds no value to the first, there is no invite loop and no expansion — it is a productivity tool wearing a collaboration label (see `productivity.md`).
- **Notification fatigue.** The fastest way to kill engagement while believing you are driving it. Over-notification trains users to ignore, mute, or disable alerts; opt-out / unsubscribe rate is the canary, and it moves _after_ the damage is done (Courier; MagicBell). Digesting and batching notifications is widely reported to lift engagement while cutting opt-outs (single-source figures circulate — e.g. "+35% engagement / −28% opt-out" from Courier — treat as illustrative, not a benchmark). The dark-pattern version — vague "you have a message waiting" bait, buried unsubscribe — buys short-term clicks and burns long-term trust.
- **Permissions too open by default.** Convenient sharing defaults (anyone-with-the-link-can-edit, org-wide visibility) are a recurring security-incident source; the safe default is least-privilege, with widening as an explicit act.
- **Building admin features the buyer wants but no user will ever see, while the daily experience rots** — or the inverse, a beloved tool that no enterprise will buy because it has no governance plane. Both are failures of the buyer-vs-user split below.
- **Vanity DAU.** Counting individuals who opened the app rather than teams who collaborated. A login is not collaboration (see `genre-metrics-map.md`).

## The admin-vs-user split (the genre's defining tension)

Collaboration software almost always has **two distinct constituencies whose interests diverge**, and resolving that divergence _is_ the product design problem.

- **The end user** wants speed, beauty, zero friction, and to invite whomever they need. They adopt bottom-up, often on a free tier, and they are the engine of the invite loop. Their experience must feel like consumer software.
- **The admin / economic buyer** wants control, security, compliance, and predictable cost: SSO and SCIM provisioning, audit logs, data-retention and DLP policy, role administration, and a single bill. They frequently **never use the core product** — Slack's Enterprise Grid, SSO, and SCIM surfaces exist almost entirely for this constituency (Slack). As Kapoor puts it, the long-standing enterprise-SaaS problem is that "the buyer persona and user persona are actually different people" — it is hard to sell value to someone who will never touch the product.

The structural consequence: these are effectively **two products sharing a database** — a delightful user plane and a trustworthy admin plane — and the go-to-market is a relay. Bottom-up adoption by users (the consumerized tool, the free tier, the invite loop) creates internal demand; that demand is then _converted_ to a contract by giving the admin/buyer the governance plane that lets them say yes to what their users already chose (Kapoor; Slack Enterprise Grid). A product that serves only one constituency stalls: all-user-no-admin can't close enterprise deals; all-admin-no-user gets bought, ignored, and churned.

## Good vs. bad

| Dimension | Good | Bad |
| --- | --- | --- |
| **Unit of value** | The workspace; a second collaborator makes the first more productive | The individual; collaboration is a bolt-on nobody uses |
| **Growth** | Invite loop runs on its own (`@mentions`, shares, "waiting on you") | Paid acquisition into a free tier with no invite loop — a leaky bucket |
| **Retention measured as** | Team / workspace cohort retention + seat expansion (NDR) | Individual MAU / total registered users |
| **Notifications** | Batched, relevant, opt-out respected; opt-out rate watched as a canary | Maximized for clicks; vague bait; opt-out treated as a loss to prevent |
| **Permissions** | RBAC roles, least-privilege defaults, sharing widened explicitly | Anyone-with-link-can-edit by default; org-wide visibility on by default |
| **Two constituencies** | Delightful user plane _and_ a real admin/governance plane (SSO, SCIM, audit) | One served, the other ignored — can't sell, or gets bought and churned |
| **Consistency model** | Weakest the domain tolerates (Figma's property-level LWW), presence built early | Over-engineered CRDTs where LWW would do; presence retrofitted late |
