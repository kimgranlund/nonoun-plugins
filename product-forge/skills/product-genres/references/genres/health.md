---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Gunther Eysenbach. \"The Law of Attrition.\" *Journal of Medical Internet Research* 7(1):e11, 2005. DOI 10.2196/jmir.7.1.e11. https://www.jmir.org/2005/1/e11/"
  - "Amy Jo Pratt et al. / JMIR. \"Challenges in Participant Engagement and Retention Using Mobile Health Apps: Literature Review.\" *Journal of Medical Internet Research* 24(4):e35120, 2022. https://www.jmir.org/2022/4/e35120/"
  - "U.S. Federal Trade Commission. \"Complying with the FTC's Health Breach Notification Rule.\" https://www.ftc.gov/business-guidance/resources/complying-ftcs-health-breach-notification-rule-0"
  - "U.S. FTC. \"Collecting, Using, or Sharing Consumer Health Information? Look to HIPAA, the FTC Act, and the Health Breach Notification Rule.\" https://www.ftc.gov/business-guidance/resources/collecting-using-or-sharing-consumer-health-information-look-hipaa-ftc-act-health-breach"
  - "U.S. Food & Drug Administration. \"Software as a Medical Device (SaMD).\" Digital Health Center of Excellence. https://www.fda.gov/medical-devices/digital-health-center-excellence/software-medical-device-samd"
  - "U.S. FDA. \"Clinical Decision Support Software — Guidance for Industry and FDA Staff\" / CDS FAQs. https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs"
---

# Health as a Product Genre

Health products try to change what a person does with their body over time — and they do it while handling data that is among the most sensitive and most regulated a product can touch. Two facts dominate the genre. First, **behavior change is the hard part and attrition is the norm**: people start, lapse, and quit, and the peer-reviewed literature treats high dropout as a structural property of digital health, not a bug to be designed away entirely. Second, **the regulatory floor you stand on depends on what you are**: a wellness tracker, a HIPAA-covered service, an FTC-regulated consumer health app, and FDA-regulated medical-device software are four different legal worlds, and which one you're in changes everything about claims, data handling, and clinical evidence. The single most consequential early decision in a health product is locating yourself on the **clinical-vs-consumer** split, because it sets the rules for all the rest.

> The discipline in one line: design for adherence over time (not first-session delight), handle health data as if a regulator and a frightened user are both watching, and know exactly which regulatory regime you're in before you make a single health claim.

## The clinical-vs-consumer split (decide this first)

Everything downstream — claims you may make, data obligations, evidence you must produce — forks here. This is observable from public regulatory guidance; the four buckets below are a working summary, not legal advice.

- **General wellness / consumer.** "Track your steps, sleep, mood, water." Makes _no_ disease-treatment claims. Lightest regime, but **not unregulated**: the FTC Act bars unfair or deceptive claims, and the FTC's **Health Breach Notification Rule** can apply (see below). Most "health apps" live here and should stay here unless they deliberately step up.
- **HIPAA-covered.** If you are (or are a "business associate" of) a covered entity — a provider, health plan, or clearinghouse — you live under **HIPAA**, administered by HHS, with its own privacy, security, and breach-notification obligations. A direct-to-consumer app is usually _not_ HIPAA-covered unless it operates on a covered entity's behalf.
- **FTC-regulated consumer health app.** Per FTC guidance, many apps that collect health data — fitness trackers, diet apps, a connected BP cuff — **are not covered by HIPAA** but _are_ subject to the FTC's Health Breach Notification Rule as a "vendor of personal health records" (an app that draws health info from multiple sources, managed by/for the individual). The Rule requires notifying users, the FTC, and sometimes the media within **60 days** of a breach of unsecured identifiable health info; the 2024 update expanded what counts.
- **FDA-regulated software (SaMD).** If the software is _intended_ to diagnose, treat, or drive a clinical decision, it may be **Software as a Medical Device** and fall under FDA. FDA's Clinical Decision Support guidance sets exclusion criteria; cross them (e.g. the software analyzes a signal/image, or the clinician can't independently review the basis) and you're a regulated device — with clinical-evaluation and quality-system obligations.

The design implication: **intended use is a regulatory act.** Copy like "detects atrial fibrillation" or "treats your depression" can reclassify a consumer app into a medical device. Claims must match the regime you've actually built and validated for.

## Conventions: what a competent health product reliably does

- **Onboards into a goal and a baseline, not a feature tour.** The first session establishes _what the user is trying to change_ and captures a starting point (current weight, current activity, current mood, current adherence) so progress is later legible.
- **States its regulatory posture honestly.** Wellness apps say what they are _not_ ("not a medical device; not a substitute for professional care"); apps handling data are explicit about what's collected, why, who sees it, and whether it's shared. Vague health data practices are both a trust failure and, increasingly, an enforcement target.
- **Designs for adherence, not just acquisition.** Reminders, streaks, check-ins, and re-engagement are first-class — because the literature is unambiguous that the median trajectory is decline. (See the law of attrition.)
- **Surfaces progress against the baseline.** Trend over time toward the user's goal, with honest framing of plateaus and setbacks — health change is non-linear and a product that only celebrates "up and to the right" will feel like it's lying during a relapse.
- **Treats sensitive data with visible care.** Granular, plain-language consent; the ability to see, export, and delete one's data; conservative defaults on sharing. The user is disclosing things they may not have told their family.
- **Knows when to step back.** Safety-critical content (crisis, severe symptoms, dangerous readings) routes to professional help / emergency services rather than trying to handle it in-app.

## Signature patterns

The genre-specific moves that distinguish health from generic consumer software.

### The behavior-change loop (and its honest version)

Most health products run a variant of the cue → action → feedback → reinforcement loop drawn from behavior-change science. The genre-specific discipline is doing it _without_ becoming coercive: streaks and nudges raise adherence, but a streak that punishes a sick day, or a notification that shames, backfires for exactly the population (chronically ill, struggling) the product claims to help. The strongest implementations pair reminders with **self-monitoring + tailored feedback + some form of human or social support** — the JMIR engagement literature repeatedly finds personalization and a coaching/social element associated with better engagement and adherence (associational, across heterogeneous studies — not a clean causal benchmark).

### Sensitive-data consent and control

Health data gets a heavier consent surface than other genres: what is collected, the purpose, sharing/selling status, retention, and a real delete path. This is both ethical baseline and regulatory hygiene — under the FTC frame, _quietly_ sharing health data (e.g. with ad networks) is a deceptive-practice and breach-rule exposure, not merely bad manners.

### Motivation and adherence scaffolding

Goal-setting, baselines, streaks, reminders, progress visualizations, and re-engagement flows for lapsed users. The non-obvious part is the **relapse path**: a returning user after a two-week gap should be welcomed back to a recoverable state, not greeted with a broken streak and a guilt-trip.

### The clinical bridge (for products that have one)

Connection to a clinician, care team, or the medical record — shared dashboards, clinician-reviewed data, referral/escalation. This is where consumer apps either responsibly hand off, or dangerously pretend to be care.

```text
Safety + escalation routing (illustrative — exact thresholds are clinical)

  Normal self-report ............ in-app tracking + feedback loop
  Concerning trend / reading .... surface guidance; suggest contacting a clinician
  Red-flag symptom / crisis ..... STOP coaching; route to professional help /
                                  emergency services / crisis line — do not
                                  attempt to manage in-product
```

## Key metrics

- **Attrition / dropout.** The defining genre metric, named and theorized by Eysenbach's **"Law of Attrition"** (JMIR, 2005): in essentially any eHealth intervention a substantial share of users stop using it or drop out before completion, and the field needs a "science of attrition" rather than treating it as failure. Eysenbach also describes the typical shape — a steep early drop to a smaller, stable group of "hardcore" users — which is the curve health products are actually managing.
- **Engagement (carefully defined).** The 2022 JMIR literature review on mHealth engagement and retention stresses there is **no agreed definition** — "engagement," "retention," "adherence," "compliance," "completion" are used interchangeably and inconsistently across studies. Practically: pick and _state_ your definition (e.g. active days, completed check-ins, sessions per week) rather than quoting a cross-study "engagement rate" as if it were standardized. Quoting one is a single-study claim, not a benchmark.
- **Adherence to the target behavior** — the metric that actually matters clinically (doses logged, sessions completed, glucose checks done), distinct from app opens. App engagement is a proxy; behavior adherence is the goal.
- **Outcome / clinical efficacy** — change in the health variable the product targets (weight, HbA1c, PHQ-9, blood pressure). For consumer wellness this is aspirational; for SaMD it is a regulatory requirement (FDA clinical evaluation). The literature's standing caution: engagement does not equal efficacy, and many apps show engagement without demonstrated health impact.

## Pitfalls

- **Designing for acquisition, ignoring attrition.** A beautiful onboarding and no re-engagement strategy guarantees the steep-drop curve Eysenbach describes. Adherence scaffolding is the product, not a growth add-on.
- **Coercive engagement mechanics.** Shame-based notifications, punishing streaks, and dark-pattern nudges aimed at a vulnerable population. They lift short-term metrics and erode the trust the genre runs on.
- **Sloppy or covert data handling.** Sharing/selling health data without clear consent, no delete path, vague privacy copy. Under the FTC Act and Health Breach Notification Rule this is a live enforcement exposure — multiple US actions have targeted exactly this.
- **Claims that outrun the regime.** Marketing "detects/diagnoses/treats" while built and validated as a consumer wellness app. Intended-use language can reclassify you as an FDA device; claims must match what you've validated.
- **Faking the clinical bridge.** Implying clinical oversight, accuracy, or "medical-grade" results without the evidence or the regulatory clearance behind them — dangerous to users and to the company.
- **Quoting borrowed benchmarks.** Citing another app's "retention rate" or a cross-study "engagement" number as your target. The literature explicitly warns these aren't comparable; define your own and measure it.

## Good vs. bad

```text
Behavior-change loop
  BAD : Daily push at a fixed time; miss one day → "You broke your 14-day
        streak!" Returning user after illness lands on a reset-to-zero shame screen.
  GOOD: Adaptive reminders + self-monitoring + tailored feedback; a missed day is
        absorbed; a returning user is welcomed to a recoverable state.

Sensitive data
  BAD : One blanket "I agree to the Privacy Policy"; data quietly shared with ad SDKs;
        no export, no delete.
  GOOD: Plain-language, purpose-specific consent; conservative sharing defaults;
        visible view / export / delete; explicit statement of what is NOT shared.

Regulatory posture
  BAD : Consumer mood-tracker whose store listing says "treats anxiety and depression."
  GOOD: "A wellness tool to help you notice patterns — not a medical device and not a
        substitute for professional care," with crisis resources one tap away.

Clinical bridge / safety
  BAD : Symptom checker that returns a confident "diagnosis" and a treatment plan.
  GOOD: Surfaces information, flags red-flag inputs, and routes clearly to a clinician
        or emergency services rather than managing the situation itself.

Metrics
  BAD : Reports "70% engagement" with no definition; benchmarks against a competitor's
        published retention figure.
  GOOD: Defines its metric ("≥3 active check-in days/week"), tracks attrition curve and
        behavior adherence, and separates app engagement from health outcome.
```

The throughline: health products win on **adherence, honesty, and care** — sustained behavior change over time, scrupulous handling of intimate data, claims that match the regulatory regime you actually occupy, and the judgment to hand off when a situation exceeds what software should handle. The genre punishes acquisition-first thinking, coercive mechanics, and any gap between what you claim and what you've validated.
