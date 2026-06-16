# Archetype · marketing-site

A site you **read to convert**: a stack of full-bleed **sections** between a global nav and a sitemap footer, each
page a curated narrative toward one call-to-action. Examples: a SaaS homepage, a feature page, pricing, a campaign
landing page, a blog. The defining idea: **vertical section stacking inside a centered content measure**; the verbs
are *read · compare · sign-up/contact*. Layout is governed by **section order** (the narrative), not a fixed frame.

## Global chrome (every page)

```
┌─ global-nav ────────────────────────────────────────────────────────────┐
│ ◆ logo    Product ▾  Solutions ▾  Pricing  Docs  Blog      [Login][Sign up]│ ← sticky, mega-menu on ▾
└───────────────────────────────────────────────────────────────────────────┘
                              … page sections …
┌─ footer-sitemap ──────────────────────────────────────────────────────────┐
│ Product   Solutions   Resources   Company   Legal      ◆ social  ☐ newsletter│
│ • links   • links      • links     • links   • links                         │
│ ─────────────────────────────────────────────────────────────────────────── │
│ © brand  ·  status · privacy · terms                                  ◐ lang │
└───────────────────────────────────────────────────────────────────────────┘
```

## Homepage section stack

```
┌ HERO ─────────────────────────────────────────┐  headline · subhead · [Primary CTA][Secondary]
│  Big promise.            ┌───────────────┐     │  · hero visual / product shot · trust line
│  One-line subhead.      │  product shot │     │
│  [Get started] [Demo]    └───────────────┘     │
├ SOCIAL PROOF / CREDIBILITY ────────────────────┤  logo wall · "trusted by" · rating · metric bar
│   ▭ logo  ▭ logo  ▭ logo  ▭ logo  ▭ logo        │
├ FEATURES GRID ─────────────────────────────────┤  2–4 col cards: icon · title · blurb · link
│  ┌ feat ┐ ┌ feat ┐ ┌ feat ┐                     │
│  │ ◇    │ │ ◇    │ │ ◇    │                     │
│  └──────┘ └──────┘ └──────┘                     │
├ DEEP-DIVE / ALTERNATING ───────────────────────┤  alternating media-left / media-right "unpacking" rows
│  [ visual ]  text  │  text  [ visual ]          │
├ PRICING (teaser) ──────────────────────────────┤  tier cards → link to /pricing
├ NEWS / RESOURCES ──────────────────────────────┤  latest posts / changelog / press cards
├ TESTIMONIAL / CASE STUDY ──────────────────────┤  quote · portrait · metric · "read story"
├ FINAL CTA ─────────────────────────────────────┤  repeat the hero CTA, conversion-focused band
└────────────────────────────────────────────────┘
```

**Homepage section vocabulary:** `hero` · `social-proof / credibility` (logo wall, metrics, ratings) ·
`features-grid` · `deep-dive / unpacking` (alternating rows) · `pricing-teaser` · `news / resources` ·
`testimonial / case-study` · `final-cta` · `global-nav` · `footer-sitemap`.

## Other page templates

```
FEATURE PAGE                    ABOUT PAGE                    PRICING PAGE
┌ hero (one feature) ─────┐     ┌ mission (hero) ────────┐    ┌ hero: "simple pricing" ──┐
│ promise · [CTA]         │     │ "why we exist"          │    │  [ monthly | annual ]    │
├ solution / promises ────┤     ├ vision / purpose ───────┤    ├ tier cards ──────────────┤
│ 3 promise blocks        │     │ beliefs · principles    │    │ ┌Free┐ ┌Pro★┐ ┌Scale┐    │
├ unpacking (how) ────────┤     ├ brand / story ──────────┤    │ │ $0 │ │ $X │ │ Call │    │
│ alternating media rows  │     ├ investors / backers ────┤    │ │ ✓✓ │ │ ✓✓✓│ │ ✓✓✓✓│    │
├ proof (case study) ─────┤     ├ team / values ──────────┤    │ └CTA─┘ └CTA─┘ └CTA──┘    │
├ FAQ ────────────────────┤     ├ jobs / careers (CTA) ───┤    ├ feature-comparison table┤
└ final CTA ──────────────┘     └ contact / CTA ──────────┘    │  feature · ✓/—/value/tier │
                                                               ├ FAQ · final CTA ─────────┘
LEAD-GEN LANDING                 BLOG — HOME / INDEX            BLOG — ARTICLE
┌ focused hero + form ────┐     ┌ featured post ──────────┐    ┌ title · byline · date ───┐
│ promise   ┌ capture ──┐ │     ├ [ All | Tag | Tag ▾ ] ──┤    │ ┌ hero image ─────────┐  │
│ benefits  │ name      │ │     │ ┌card┐ ┌card┐ ┌card┐    │    │ prose · h2 · code · img  │
│ • • •     │ email     │ │     │ │img │ │img │ │img │    │    │ ── pull quote ──         │
│ proof     │ [Submit]  │ │     │ │ttl │ │ttl │ │ttl │    │    │ TOC ▸ (aside)  · share   │
│ (no nav!) └───────────┘ │     │ └tag┘ └tag┘ └tag┘       │    │ author bio · related ·CTA│
└─────────────────────────┘     │ ‹ pagination ›          │    └──────────────────────────┘
 stripped nav, one CTA, form     tag filter · search · grid    reading column + TOC + share
```

## Named-pattern vocabulary (cross-page)
`global-nav` (sticky, mega-menu) · `hero` (headline · subhead · CTA · visual) · `cta-band` ·
`features-grid` · `feature-deep-dive` (alternating media rows) · `pricing-cards` + `comparison-table` ·
`social-proof` (logos/metrics/ratings) · `testimonial` / `case-study` · `faq` · `lead-capture-form` ·
`blog-index` (featured + grid + tags) · `article` (reading column + TOC + share + related) · `footer-sitemap`.

## Outside-in notes (A)
- **A1:** unlike the app shells, the marketing page **DOES page-scroll** — the "frame" is the *centered content
  measure* (a max-width container, ~1100–1280px) the sticky nav sits over. The gate becomes: *is every section on
  the same measure + vertical rhythm*, and *is the nav the only fixed chrome*.
- **A2/A3:** sections are full-bleed bands; content lives on the measure; consistent section padding (the vertical
  rhythm) is the spatial discipline.

## Inside-out notes (B)
- **B1/B2:** the only real verbs are *read · navigate · compare · convert*. The conversion verb (sign-up / demo /
  contact / submit) must appear **in the hero AND in a final CTA band**, and on lead-gen pages it is the *only*
  verb (strip the nav so nothing competes with the form).
- **B3/B5:** sticky-nav active state, form validation + success state, and a single consistent primary-CTA style so
  the convert action is unmistakable on every page.
