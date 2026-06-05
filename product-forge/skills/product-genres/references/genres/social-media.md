---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Jakob N. \"Participation Inequality: The 90-9-1 Rule for Social Features and Online Communities.\" NN/g, 2006. https://www.nngroup.com/articles/participation-inequality/"
  - "Robert E. Kraut & Paul Resnick. *Building Successful Online Communities: Evidence-Based Social Design*. MIT Press, 2012. https://direct.mit.edu/books/monograph/2912/"
  - "Nir Eyal. *Hooked: How to Build Habit-Forming Products*. Portfolio/Penguin, 2014 (Hook Model: trigger → action → variable reward → investment)."
  - "Sarah T. Roberts. *Behind the Screen: Content Moderation in the Shadows of Social Media*. Yale University Press, 2019. https://yalebooks.yale.edu/book/9780300235883/behind-the-screen/"
  - "The Santa Clara Principles on Transparency and Accountability in Content Moderation (2.0, 2021). https://santaclaraprinciples.org/"
---

# Social Media as a Product Genre

A social product's value is almost entirely **other people**. Unlike a tool that's useful to one user alone, a social network is worth nothing to its first user and enormous to its millionth — its utility is a function of who else is there. That single fact drives the whole genre: the central problems are **network effects and the cold-start** (how do you make an empty room worth entering?), **engagement loops** (how do you bring people back without becoming manipulative or toxic?), the **content-creation ladder** (most users only watch — how do you grow the few who make the content everyone else consumes?), and **moderation, safety, and trust at scale** (the same user-generated content that is the product is also, inevitably, where abuse, harassment, and harm arrive). This reference centers consumer social products — networks, feeds, communities, creator platforms, and messaging with a public surface.

> The discipline in one line: a social product is a self-reinforcing loop where users supply the value for other users — so you must seed it past the cold-start, design loops that bring people back without exploiting them, climb the lurker→creator ladder deliberately, and treat trust & safety as core product, not afterthought.

## Conventions: what a competent social product reliably does

- **Solves the empty-room problem at onboarding.** A new user is shown value before they have a network — interest-based suggestions, follow recommendations, seeded/curated content, or a clear first action — so the first session isn't a blank feed. The cold-start is fought per-user, not just at launch.
- **Makes the first contribution trivially low-stakes.** The cheapest possible participation (a like, a vote, a reaction, an emoji) exists as a rung _below_ commenting and posting, because the data (below) says almost everyone starts as a watcher.
- **Has a comprehensible engagement loop.** A trigger (notification, feed update) brings the user back, an easy action and a reward (new content, social response) pays it off, and the user leaves something behind (a post, a follow, a setting) that improves the next visit. This loop is the genre's engine — and its ethical fault line.
- **Surfaces social proof and reciprocity.** Followers/following, likes/reactions, "people you may know," who-responded — the signals that make participation feel seen and reciprocated, which is what actually pulls the next contribution.
- **Ships safety controls _to the user_, not just to moderators.** Block, mute, report, restrict, privacy/audience controls, and comment controls are first-class, discoverable, and on every relevant surface. Self-protection is part of the core loop.
- **Moderates, and is seen to moderate.** There are rules, enforcement, and — per emerging norms like the Santa Clara Principles — notice to affected users and some transparency about what was removed and why. "We have a policy" with invisible, unaccountable enforcement is not credible at scale.

## Signature patterns

The genre-specific moves.

### The engagement / habit loop

Most social products run Nir Eyal's **Hook Model** (from _Hooked_, 2014): **trigger → action → variable reward → investment**. An external trigger (push, email) or internal trigger (boredom, FOMO) prompts an easy **action** (open, scroll); a **variable reward** (you never know what's in the feed/inbox — the unpredictability is the pull) pays it off; and an **investment** (post, follow, customize) loads the next trigger and raises switching cost. The genre-defining tension: this loop is also the mechanism of compulsive use, and the line between "habit-forming" and "manipulative/addictive" is exactly where the ethical and (increasingly) regulatory scrutiny lives. Designing the loop responsibly — honest triggers, no dark-pattern variable rewards aimed at vulnerable users — is part of the craft, not a constraint on it.

### Climbing the content-creation ladder (lurker → contributor → creator)

The genre's most important growth structure. Because participation is radically unequal (see metrics), the product must engineer a **ladder of escalating commitment**: cheap reactions → low-effort contributions (votes, short comments, reshares) → full creation (posts, threads, video). Kraut & Resnick's evidence-based design work frames this as the newcomer/commitment problem — getting people in, giving low-barrier first tasks, and building the reciprocity and identity that motivate deeper contribution. The non-obvious move is that **most design effort should target the rung-to-rung transitions** (lurker→reactor, reactor→commenter), not just the top creators.

```text
Content-creation ladder — design each rung-to-rung transition (illustrative)

  LURKER ───► REACTOR ───► COMMENTER ───► POSTER ───► CREATOR
  (watch)     (like/vote)  (reply)        (original)  (sustained, drives others)

  Roughly tracks the 90-9-1 distribution: the vast base watches, a slim middle
  contributes a little, a tiny top makes most of what everyone consumes.
  Growth = widening the funnel AND nudging users up one rung at a time.
```

### Network seeding and the cold-start

Patterns for making the room worth entering before the crowd arrives: launching in a narrow niche/geography where density is achievable; importing existing graphs (contacts, other platforms); single-player or small-group value that works before the network does; and creator/content seeding so consumers have something to consume on day one. The strategic insight is that liquidity is **local** — a sub-community, topic, or city needs to feel alive even if the global network is small.

### Trust, safety, and moderation at scale

The defensive half of the genre, and inseparable from it. User-facing controls (block/mute/report/restrict, audience and comment controls); the moderation pipeline (community guidelines, automated detection, human review, appeals); and transparency/due-process norms. Sarah T. Roberts' _Behind the Screen_ documents the human and structural reality: moderation is done by **100,000+ commercial moderators worldwide** at real psychological cost, and platforms are structurally **reactive** — the "whack-a-mole" problem means harm is typically addressed only _after_ it scales. The Santa Clara Principles codify the emerging expectation that enforcement come with notice to the user, an appeal, and aggregate transparency — moving moderation from invisible fiat toward accountable process.

## Key metrics

- **Participation inequality (the 90-9-1 distribution).** The genre's foundational metric, named by **Jakob N. (NN/g, 2006)**: in many online communities **~90% lurk (never contribute), ~9% contribute occasionally, and ~1% account for almost all contribution.** Jakob N. is explicit that the exact split varies by platform and that the rule is a heuristic, not a law — but the _shape_ (a vast silent base, a tiny creating top) is the defining reality the content-ladder and growth strategy exist to address. Quote the shape; flag the exact numbers as a heuristic.
- **DAU/MAU (stickiness ratio)** — daily over monthly actives, the standard proxy for habit strength. A high ratio means the engagement loop is genuinely habitual; it's the number the Hook Model is ultimately trying to move. (Industry-standard metric; "good" thresholds vary widely by product and are not a fixed benchmark.)
- **Network-effect / liquidity metrics** — connections per user, time-to-first-follow/friend, share of users who reach an activation threshold (the "magic number" of connections beyond which retention jumps). Specific magic-number figures attributed to particular companies are **widely repeated as folklore and rarely from primary sources — label any such number as anecdotal.**
- **Creation-funnel metrics** — lurker→reactor→creator conversion, % of MAU who post, content produced per active user. These operationalize moving people up the ladder and are the leading indicator of whether the network can sustain its own content.
- **Trust & safety metrics** — report/abuse rates, prevalence of violating content, time-to-action, appeal/overturn rates, and (per Santa Clara) what's disclosed in transparency reporting. Increasingly a board-level and regulatory scoreboard, not just an internal ops number.

## Pitfalls

- **Shipping into the cold-start with no seeding.** Launching a social product that requires a network, to users who have no network, with an empty feed and no first-session value. The most common way social products die before they start.
- **Optimizing engagement into manipulation/toxicity.** Tuning the variable-reward loop and recommendation surface purely for time-on-app — the documented path to compulsive use, outrage amplification, and the harms that draw regulatory and reputational fire. The loop's power is exactly why it needs ethical guardrails.
- **Ignoring the creation ladder.** Building only for posting/creating and assuming users will climb on their own — leaving the 90% with no low-stakes rung, so the content base never grows and the network feels empty even when populated.
- **Treating safety as an afterthought.** Launching without block/mute/report, or with invisible, unaccountable moderation. At any scale, user-generated content _will_ include abuse; a product without safety controls is shipping a harassment tool. Roberts' work shows reactivity is structural — but the absence of any process is a choice.
- **Opaque, due-process-free enforcement.** Removing content or banning users with no notice, no reason, and no appeal. Beyond unfairness, it's now a transparency-norm and regulatory failure (cf. Santa Clara Principles, and emerging platform regulation).
- **Vanity-metric self-deception.** Celebrating raw registered users or total posts while DAU/MAU, creation rate, and liquidity stagnate — mistaking a populated database for a living network.

## Good vs. bad

```text
Cold-start / onboarding
  BAD : New user lands on an empty feed, follows no one, sees nothing, leaves.
  GOOD: Interest pick → seeded/recommended content + suggested follows + one easy first
        action, so the first session is alive before the user has a network.

Engagement loop
  BAD : Maximize time-on-app at any cost: rage-bait ranking, manipulative streaks/badges,
        notifications engineered to exploit FOMO.
  GOOD: A genuine trigger→action→reward→investment loop with honest notifications,
        user-controllable, that brings people back to value rather than compulsion.

Creation ladder
  BAD : The only way to participate is to write a full post; 90% never do; feed stays thin.
  GOOD: A real ladder — react → vote → short reply → post — with design effort on each
        rung-to-rung nudge, widening who contributes.

Trust & safety
  BAD : No block/mute/report; moderation is invisible and unaccountable; bans arrive with
        no reason and no appeal.
  GOOD: Block/mute/report/restrict on every surface; clear guidelines; enforcement with
        notice, an appeal, and aggregate transparency (per Santa Clara Principles).

Metrics
  BAD : "We have 2M registered users!" while DAU/MAU and posts-per-user crater.
  GOOD: Tracks DAU/MAU, lurker→creator conversion, liquidity/activation, and safety
        prevalence — and reads the 90-9-1 shape as a design target, not a surprise.
```

The throughline: social products win by **bootstrapping a self-reinforcing network and then sustaining it humanely** — seeding past the cold-start, building engagement loops that bring people back without exploiting them, deliberately climbing users up the lurker→creator ladder, and treating trust, safety, and accountable moderation as core product surfaces. The genre punishes empty-room launches, manipulation-maximizing loops, creation funnels that ignore the silent 90%, and any product that ships user-generated content without the means to keep its users safe.
