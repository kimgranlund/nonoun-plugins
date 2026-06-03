---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Nir Eyal with Ryan Hoover. Hooked: How to Build Habit-Forming Products. Portfolio / Penguin, 2014. ISBN 9781591847786"
  - "Nir Eyal. Want To Hook Your Users? Drive Them Crazy (the three variable rewards). https://www.nirandfar.com/want-to-hook-your-users-drive-them-crazy/"
  - "Nir Eyal. The Manipulation Matrix (Hooked, ch. 8 / nirandfar.com). https://www.nirandfar.com"
  - "B.F. Skinner. Variable-ratio reinforcement schedules — the behaviorist source Eyal cites for variable rewards."
---

# The Hook Model

Nir Eyal's _Hooked_ (2014) is a working model for building products that form habits — behaviors users perform with little or no conscious thought, triggered by internal cues rather than external prompting. The model is a four-phase loop: **Trigger → Action → Variable Reward → Investment.** Run the loop enough times and an external-trigger-driven behavior becomes an internally-cued habit. This reference walks the four phases, the "habit zone" that decides whether a behavior _can_ become a habit at all, and — load-bearing for any responsible use — the ethical line Eyal himself draws with the Manipulation Matrix.

> The model's claim, in one line: habits are built by repeatedly cycling users through trigger, action, variable reward, and investment, until an internal trigger (an emotion, a routine, a context) does the prompting that an external trigger used to do.

## The four phases

### 1. Trigger — what starts the loop

A trigger is the cue that prompts the behavior. Eyal splits them in two, and the whole arc of the model is the migration from the first kind to the second.

- **External triggers** — design artifacts in the user's environment: a push notification, an email, an app icon, a "click here" call to action. They carry information about what to do next. New users run on external triggers.
- **Internal triggers** — emotions, routines, and contexts that have become coupled to the product through repetition. Boredom, loneliness, uncertainty, "I wonder what's happening" — a felt need that the product has been trained to answer. The product becomes habit-forming precisely when an **internal trigger** does the prompting. The strategic goal is to attach the product to a frequently-occurring internal trigger (a negative emotion is the most common and most powerful), so the user reaches for it automatically.

### 2. Action — the simplest behavior in anticipation of reward

The action is the behavior done in expectation of the reward, made as easy as possible. Eyal grounds this in B.J. Fogg's behavior model: a behavior occurs when **motivation, ability, and a trigger** converge at the same moment. The lever the designer pulls hardest is **ability** — reduce the effort the action requires (fewer taps, less thought, less time), because reducing friction reliably increases the behavior more than trying to crank up motivation. Scrolling a feed, hitting search, tapping play: the canonical hooked actions are nearly effortless.

### 3. Variable reward — the engine of craving

This is the phase that distinguishes a hook from a simple feedback loop, and the one with the sharpest ethical weight. A predictable reward satisfies; a **variable** reward _craves_. Eyal draws directly on B.F. Skinner's finding that variable-ratio reinforcement schedules — rewards on an unpredictable schedule — drive far more repetition than fixed ones. The unpredictability of the reward is what keeps the user cycling. Eyal names three types of variable reward:

- **Rewards of the Tribe** — social rewards: validation, connection, status, reciprocity. Likes, comments, replies. (Fueled by connectedness with other people.)
- **Rewards of the Hunt** — the search for material resources or information: the feed that might contain something good, the search result, the deal, the scroll.
- **Rewards of the Self** — intrinsic rewards of mastery, competence, completion, and control: clearing the inbox, finishing the level, the satisfying progress bar.

The discipline: the reward must stay genuinely _variable_ and must satisfy the need the trigger created — a reward that is predictable loses its pull, and a reward that doesn't relieve the internal trigger trains users to stop.

### 4. Investment — loading the next loop

The investment phase is the user putting something _into_ the product, which makes the next pass through the loop more likely. Per Eyal, investment increases the odds of return in two ways:

- **Loading the next trigger.** The user's action sets up a future external trigger that pulls them back — sending a message invites a reply (which arrives as a notification); following accounts populates tomorrow's feed; scheduling something creates a future reminder.
- **Storing value.** Investments accrue **stored value — content, data, followers, reputation, or skill** — that makes the product more valuable the more it is used. Unlike physical goods that depreciate, a hooked product appreciates with use, which raises switching cost and deepens the habit.

Crucially, investment comes _after_ the reward, not before: the user is asked for a bit of work (a "small ask") once they've just been rewarded and are most willing.

## The habit zone: frequency × perceived utility

Not every product can be a habit, and Eyal is explicit about the boundary. He plots a behavior on two axes — **frequency** (how often it occurs) and **perceived utility** (how useful/rewarding it is seen to be) — and locates a **habit zone**. The rule: a behavior becomes a habit only when it occurs **with enough frequency _and_ enough perceived utility.** Both conditions must hold.

- A useful-but-infrequent behavior (filing taxes) is too rare to ever become automatic — high utility, low frequency.
- A frequent-but-low-utility behavior won't stick either.
- High frequency can _compensate_ for lower perceived utility (a behavior done often enough can become a habit even when each instance isn't dramatically useful), which is why low-utility-but-very-frequent products (social feeds) can form strong habits.

The related **vitamin vs. painkiller** distinction: painkillers solve an obvious, often quantifiable pain; vitamins appeal to emotional rather than functional needs and are easy to skip. Eyal's twist is that **habit-forming products often start as vitamins (nice-to-haves) and become painkillers (must-haves) once the habit forms** — the internal trigger turns the optional into the felt-necessary. This is why a product that looks like a mere vitamin can still earn habitual use if it lands in the habit zone.

## The ethical line: the Manipulation Matrix

Eyal devotes a chapter of _Hooked_ to ethics, because the same loop that builds a useful habit builds a harmful compulsion. His tool is the **Manipulation Matrix**, built from two questions the maker must answer honestly:

1. **Does the product materially improve the user's life?**
2. **Does the maker use the product themselves?**

The two yes/no answers produce four quadrants:

|  | Maker uses it | Maker does **not** use it |
| --- | --- | --- |
| **Materially improves life** | **Facilitator** — the goal: you build something you yourself use and that genuinely helps. | **Peddler** — good intentions, but not using it yourself signals you may be missing something; high risk of self-deception. |
| **Does **not** improve life** | **Entertainer** — you use it and find it fun/harmless; fine in moderation, but users churn to the next novelty and it can still drain them. | **Dealer** — you neither use it nor believe it helps. Eyal's name for this is **exploitation.** |

The working rule Eyal draws: aim to be a **Facilitator** — build habit-forming products you use yourself and that materially improve users' lives. The **Dealer** quadrant is unethical by his own definition (exploitation); the **Peddler** is the dangerous one because good intentions mask the fact that you don't actually find the product worth using.

> Honest limitation (and a documented critique): Eyal presents the matrix as a _starting point_ for ethics, not a complete safeguard, and critics have argued it is insufficient — a self-declared "Facilitator" can still ship dark patterns, exploit variable rewards aggressively, and leave users worse off, since both test questions are self-assessed and easy to answer in one's own favor. Use the matrix as a necessary first gate, not a license: pair it with concrete guardrails (clear opt-outs, frequency caps, no manufactured anxiety, honest defaults). This critique is well-represented in commentary on the book and is flagged here as the standard objection, not as Eyal's own position.

## How to use the model responsibly

A short working sequence for applying the Hook model without crossing the line:

1. **Pass the Manipulation Matrix first.** If you are honestly a Peddler or a Dealer, stop — the loop will work and that is the problem. Only Facilitator-grade products earn the right to be habit-forming.
2. **Find the real internal trigger.** Identify the frequent emotion/routine your product genuinely relieves — not one you have to manufacture. A product that invents anxiety to then relieve it is the dark-pattern failure mode.
3. **Reduce friction on the action; don't inflate motivation with pressure.** Make the valuable behavior effortless. Pressure tactics (guilt, FOMO, fake scarcity) are the manipulative substitutes for genuine ability.
4. **Keep the reward variable _and_ satisfying.** It must relieve the internal trigger. A variable reward that doesn't satisfy is a slot machine; one that does is a habit worth forming.
5. **Make investments accrue value for the user, not just lock-in for you.** Stored value should make the product better _for them_ (their data, their content, their skill), not merely raise switching cost.
6. **Check the habit zone before investing.** If the behavior isn't both frequent and perceived-useful, no amount of hook engineering creates a durable habit — you'll be forcing a loop the behavior can't support.
