---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Jon Yablonski. *Laws of UX: Using Psychology to Design Better Products & Services*. O'Reilly Media, 1st ed. 2020 (ISBN 9781492055310); 2nd ed. 2024 (ISBN 9781098146962)."
  - "Jon Yablonski. *Laws of UX* (interactive reference). https://lawsofux.com/ — definitions quoted here track this site."
  - "William E. Hick. \"On the Rate of Gain of Information.\" *Quarterly Journal of Experimental Psychology* 4(1):11-26, 1952. DOI 10.1080/17470215208416600 (Hick's Law)."
  - "Paul M. Fitts. \"The Information Capacity of the Human Motor System in Controlling the Amplitude of Movement.\" *Journal of Experimental Psychology* 47(6):381-391, 1954. DOI 10.1037/h0055392 (Fitts's Law)."
  - "George A. Miller. \"The Magical Number Seven, Plus or Minus Two.\" *Psychological Review* 63(2):81-97, 1956. DOI 10.1037/h0043158 (Miller's Law)."
  - "Walter J. Doherty & Ahrvind J. Thadani. \"The Economic Value of Rapid Response Time.\" IBM, GE20-0752-0, 1982 (the <400ms Doherty Threshold)."
  - "Bluma Zeigarnik. \"Über das Behalten von erledigten und unerledigten Handlungen\" (On finished and unfinished tasks). *Psychologische Forschung* 9:1-85, 1927 (the Zeigarnik effect)."
---

# Laws of UX: cognitive heuristics as design constraints

The "Laws of UX," collected and named by Jon Yablonski (_Laws of UX_, O'Reilly 2020; 2nd ed. 2024; lawsofux.com), are a set of psychology findings reframed as design heuristics — each one a fact about human perception, memory, or motor control, paired with a concrete implication for interface design. They are not rules in the legal sense; they are _constraints the human comes with_, which a design either works with or fights. This reference covers the eight requested for the pattern library, each stated, attributed to its primary research where one exists, and turned into a design implication you can act on. The point of the law is the implication: knowing Hick's Law is useless until it changes how many options you put on a screen.

> How to use a law: it is a _lens for diagnosis and a constraint for design_, not a number to optimize. "This feels slow / overwhelming / forgettable" usually maps onto one of these laws, and the law names both the cause and the move that fixes it.

## Hick's Law — decision time grows with the number and complexity of choices

**Definition (lawsofux.com):** "The time it takes to make a decision increases with the number and complexity of choices." Grounded in W. E. Hick's 1952 work showing reaction time rises logarithmically with the number of equally-probable alternatives (the Hick-Hyman law).

**Design implication.** Reduce the number of options at any single decision point to speed up decisions and lower cognitive load — but do not amputate functionality; _defer_ and _group_ it. Concrete moves: break complex flows into steps (progressive disclosure / wizards), categorize long lists, highlight a recommended default, and hide advanced options until asked. The caution Yablonski adds: minimize choices _without_ hiding things the user actually needs — simplicity that breaks the task is not a win.

## Fitts's Law — acquisition time depends on distance and target size

**Definition (lawsofux.com):** "The time to acquire a target is a function of the distance to and size of the target." From Paul Fitts's 1954 study of the human motor system: movement time increases with distance to the target and decreases with target size, producing a speed-accuracy trade-off — fast moves at small targets cause errors.

**Design implication.** Make important targets **large** and place them **close** to where the pointer or thumb already is. Concrete moves: generous hit areas for primary actions (this is the cognitive root of the 44pt/48dp touch minimums in the responsive-mobile reference); put frequent actions within easy reach (bottom of a phone screen, near the cursor's path); exploit "infinite" edges and corners on desktop (the screen edge stops the pointer, making edge targets effectively huge — the macOS menu bar); and don't strand a critical button far from the content it acts on.

## Jakob's Law — users expect your product to work like the others they know

**Definition (lawsofux.com):** "Users prefer your site to work the same way as all the other sites they already know." Yablonski's own coinage, after Jakob N.'s observation that users spend most of their time on _other_ sites and form expectations there.

**Design implication.** Honour established conventions; users transfer expectations built elsewhere, and meeting them lets people use a new product immediately. Concrete moves: put the logo top-left linking home, the cart top-right, navigation where it's expected; use platform-native patterns on mobile (see responsive-mobile); reserve novelty for where it genuinely pays. When you _must_ break a convention, test it and ease the transition — innovation has a cost measured in relearning, and Jakob's Law prices it.

## Doherty Threshold — keep system response under ~400ms

**Definition (lawsofux.com):** "Productivity soars when a computer and its users interact at a pace (<400ms) that ensures neither has to wait." From Doherty & Thadani's 1982 IBM study on the economic value of rapid response time, which found productivity rising sharply as response time dropped below ~400ms.

**Design implication.** Make the system respond in under ~400ms — and where you can't, _simulate_ responsiveness so the user never feels they're waiting. Concrete moves: optimistic UI (reflect the action immediately, reconcile in the background), skeleton screens and instant acknowledgement of taps, perceived-performance tricks (progress that animates, content that streams in). A fast-_feeling_ interface is judged more usable and keeps the user in flow; latency above the threshold breaks attention and erodes trust.

## Miller's Law — working memory holds about 7 (±2) items

**Definition (lawsofux.com):** "The average person can only keep 7 (plus or minus 2) items in their working memory." From George Miller's 1956 paper on the limits of short-term information processing.

**Design implication.** Don't rely on users holding many discrete items in their heads — and use **chunking** to work within the limit. The frequently-misapplied caveat Yablonski stresses: Miller's number is _not_ a mandate to cap menus or lists at seven; it is about _working memory_, so the real move is to **chunk** information into meaningful groups the mind can hold as units. Concrete moves: group phone numbers, card numbers, and long IDs into chunks; cluster related controls; carry context forward across steps so the user doesn't have to remember it; show, don't make them recall.

## Aesthetic-Usability Effect — attractive design is perceived as more usable

**Definition (lawsofux.com):** "Users often perceive aesthetically pleasing design as design that's more usable." Rooted in Kurosu & Kashimura's 1995 study (and Tractinsky's replication) finding strong correlation between perceived aesthetics and perceived ease of use.

**Design implication.** Visual quality is not decoration — it shapes how usable the product is _judged_ to be, and it buys tolerance for minor usability problems (an attractive interface earns goodwill and gets the benefit of the doubt). Two cautions: it can **mask** real usability issues in testing (users forgive, and evaluators miss, problems hidden behind polish), so don't let beauty substitute for usability testing; and the effect is a reason to invest in craft, not an excuse to skip the fundamentals.

## Von Restorff Effect (Isolation Effect) — the thing that stands out is remembered

**Definition (lawsofux.com):** "When multiple similar objects are present, the one that differs from the rest is most likely to be remembered." Named for Hedwig von Restorff's 1933 finding that a distinctive item in a list is recalled better than its uniform neighbours.

**Design implication.** Make the single most important element _visually distinct_ so it draws attention and is remembered — but spend the contrast budget sparingly, because if everything is emphasized, nothing is. Concrete moves: one primary CTA styled apart from secondary actions; the recommended pricing tier highlighted; the current step marked in a wizard. Two cautions Yablonski raises: don't rely on colour alone to create the distinction (accessibility — ties to WCAG 1.4.1), and avoid making distinctive styling so loud it reads as an ad and gets banner-blindness-ignored.

## Zeigarnik Effect — unfinished tasks stay on the mind

**Definition (lawsofux.com):** "People remember uncompleted or interrupted tasks better than completed tasks." From Bluma Zeigarnik's 1927 research showing interrupted tasks are recalled roughly twice as well as completed ones.

**Design implication.** Surface _incompleteness_ to pull users back toward finishing — the open loop creates a gentle tension that motivates completion. Concrete moves: progress indicators and completion meters (the visible "70% complete" nags pleasantly toward 100%), onboarding checklists with remaining steps shown, "your profile is 3 fields from done." Pairs naturally with the **Goal-Gradient Effect** (motivation increases as the goal nears) — show progress _and_ nearness. The ethical caveat: use this to help users finish _their_ goals; weaponized to manufacture anxiety or trap attention it slides toward the deceptive patterns catalogued elsewhere in this library.

## Applying the laws: a quick diagnostic

These laws are most useful as a fast read on _why_ a screen underperforms. The mapping from symptom to law to move:

```text
SYMPTOM                              LAW                       MOVE
Screen feels overwhelming /          Hick's Law                Fewer choices per step; group,
users stall at a decision                                      default, progressively disclose.
Buttons hard to hit / mis-taps       Fitts's Law               Bigger targets, closer to reach;
                                                               exploit edges (desktop), bottom
                                                               zone (mobile).
Users confused by a novel layout     Jakob's Law               Conform to convention; reserve
                                                               novelty; ease + test any break.
Interface feels sluggish             Doherty Threshold         Respond <400ms or simulate it
                                                               (optimistic UI, skeletons).
Users forget context / fields        Miller's Law              Chunk; carry context forward;
                                                               show don't make them recall.
Polished but problems slip through   Aesthetic-Usability       Invest in craft AND still test;
testing                              Effect                    don't let beauty mask defects.
Key action gets lost on the page     Von Restorff Effect       Make ONE element distinct (not by
                                                               colour alone; not so loud it reads
                                                               as an ad).
Users abandon multi-step flows       Zeigarnik (+ Goal-        Show progress and nearness to
                                     Gradient)                 completion; honestly, not coercively.
```

For the broader catalogue (Gestalt grouping laws, Peak-End Rule, Tesler's Law, Postel's Law, Serial-Position, choice overload, and the rest), see lawsofux.com and the pattern-taxonomy index in this library — this file covers the eight load-bearing heuristics most often invoked when critiquing a product surface.
