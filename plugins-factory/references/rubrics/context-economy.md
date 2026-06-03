---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Context Economy — Lean Always-On, Rich On-Invoke

The drill-down for holistic **P6**. Every enabled plugin pays a standing context tax on every session. This rubric scores whether that tax is minimal and justified, and whether the plugin's richness lives behind load-on-demand boundaries — so the plugin is worth leaving enabled.

Theory: `../foundations/context-economy-foundations.md`. Primary critic: **Boris Cherny** (vanilla > ceremony) with **Andrej Karpathy** (is the cost buying verifiable capability?) second.

---

## §The Problem

A plugin's cost is not what it does when invoked — it's what it adds to *every* session merely by being enabled. `claude plugin details` splits this into always-on (descriptions + MCP tool defs) and on-invoke (skill bodies, references). A plugin whose standing cost is high enough that users toggle it off between uses has defeated its own purpose. Manifest validation says nothing about this; the cost is real and invisible to it.

---

## §First Principles

1. **Lean always-on, rich on-invoke.** Minimize what's paid every session; let detail be paid only when a component fires.
2. **The MCP is the costliest standing component.** Tool definitions are always-on and can dominate the window — bundle one only when its external-state capability is the point.
3. **Progressive disclosure governs on-invoke richness.** SKILL.md as TOC; references one level deep; scripts cost nothing until they run.
4. **The real test is behavioral.** A plugin cheap enough to leave enabled passes; one users disable to reclaim context fails — a hypothesis to measure, not assert.

---

## §The Rubric

### D1 — Lean Always-On `[review]`

Is the standing context (descriptions + tool defs) minimal and proportional to the capability?

| Score | Evidence |
|---|---|
| **5** | Always-on cost is dominated only by terse, specific component descriptions (the routing surface). No padded descriptions, no needless MCP. `claude plugin details` always-on number is small relative to the capability delivered. |
| **4** | Lean always-on; one description is wordier than needed. |
| **3** | Noticeable standing cost — a couple of verbose descriptions, or an MCP whose tool defs are a meaningful fraction of always-on — but tolerable. |
| **2** | Always-on cost is high: many verbose descriptions, or a bundled MCP's tool defs dominate. Enabling the plugin is felt in unrelated sessions. |
| **1** | Standing context is heavy enough that enabling the plugin measurably degrades every session regardless of use. |

**Go deeper**: `../foundations/context-economy-foundations.md` §"The two costs"; cross-check P2 (MCP fit).
**Test** (always-on audit): from `claude plugin details` (or `context-cost.py`), is the always-on number dominated by anything other than terse descriptions? MCP tool defs or verbose descriptions dominating = D1 ≤ 2.

---

### D2 — On-Invoke Detail Placement `[review]`

Does heavy content load when a component fires, not stand permanently in context?

| Score | Evidence |
|---|---|
| **5** | All substantial content (reference bodies, examples, datasets, agent prompts) is on-invoke — loaded only when its component fires or the model reads it. Nothing heavy is front-loaded into a description or a permanently-loaded surface. |
| **4** | Detail is on-invoke; one reference is loaded a little earlier than needed. |
| **3** | Some detail leaks into always-on surfaces (a long description carrying reference content). |
| **2** | Meaningful reference content front-loaded into descriptions or SKILL.md headers — paid every session. |
| **1** | The plugin's knowledge is front-loaded wholesale; on-invoke vs always-on isn't distinguished. |

**Go deeper**: `../foundations/context-economy-foundations.md` §"Progressive disclosure".
**Test**: is any substantial content in a place paid every session rather than on-invoke? Front-loaded reference text = D2 ≤ 3.

---

### D3 — Progressive Disclosure in Bundled Skills `[gate]`

Do bundled skills follow the disclosure rules (TOC SKILL.md, references one level deep, logic in scripts)?

| Score | Evidence |
|---|---|
| **5** | Every bundled skill: SKILL.md acts as a TOC (≈under 500 lines), references domain-partitioned and one level deep, references >100 lines carry their own TOC, deterministic logic is in scripts (free context until run). |
| **4** | Disclosure followed; one reference is two levels deep or one SKILL.md is heavy. |
| **3** | Partial: one bundled skill front-loads its references or nests them deeply (causing partial reads). |
| **2** | Multiple bundled skills front-load reference content into SKILL.md; little on-demand structure. |
| **1** | Bundled skills dump their whole reference tree up front with no load conditions. |

**Go deeper**: `../foundations/context-economy-foundations.md` §"Progressive disclosure is the on-invoke discipline"; `skills-studio` `context-engineering.md` + `progressive-context-construction.md`.
**Test**: for each bundled skill, is SKILL.md a TOC with references one level deep and logic in scripts? Front-loaded or deeply-nested references = D3 fails.

---

### D4 — MCP Cost Justified `[review]`

If a bundled MCP drives always-on cost, is that cost warranted by a genuine external-state need?

| Score | Evidence |
|---|---|
| **5** | A bundled MCP (if any) exists because the plugin's job genuinely needs external state/actions; its tools are consolidated and bounded (P2), so its always-on cost buys real capability. No MCP bundled "in case." |
| **4** | MCP justified; tool set could be slightly more consolidated. |
| **3** | MCP justified but a couple of tools are endpoint-shaped, inflating always-on cost beyond need. |
| **2** | MCP's standing cost outweighs its centrality — it's adjacent to the plugin's job, not core to it. |
| **1** | A bundled MCP "in case," 1:1-wrapping an API the plugin doesn't centrally need — pure standing tax. |

**Go deeper**: `../foundations/context-economy-foundations.md` §"When always-on cost is justified"; cross-check P2 (D2).
**Test**: is every bundled MCP's external-state capability core to the plugin's one-sentence job? An adjacent/"in case" MCP = D4 ≤ 2. (No MCP = N/A.)

---

### D5 — Toggle-Cost Coherence `[review]`

Does the plugin's standing cost match what enabling it as a unit delivers?

| Score | Evidence |
|---|---|
| **5** | Enabling the plugin is one coherent decision: its standing cost is proportional to the capability the user is choosing to have available. A user can reason about the trade ("I'm doing design work → enable design-system"). |
| **4** | Cost roughly matches capability; one component adds standing cost a user rarely uses. |
| **3** | The toggle bundles some standing cost for capabilities a typical user won't use (mild kitchen-sink coupling). |
| **2** | Enabling the plugin imposes standing cost for several capabilities most installers never touch (P3 kitchen-sink showing up as context tax). |
| **1** | The toggle is all-or-nothing for a grab-bag; standing cost bears no relation to what any given user needs. |

**Go deeper**: `../foundations/context-economy-foundations.md` §"Cohesion and context cost are linked"; cross-check P3.
**Test**: does the standing cost map to one coherent toggled capability, or does it bundle tax for capabilities most installers won't use? Latter = D5 ≤ 2.

---

### D6 — Stays Enabled by Default `[hypothesis]`

Is the plugin cheap enough that users leave it enabled, rather than toggling it off between uses?

| Score | Evidence |
|---|---|
| **5** | Telemetry (or reasoned proxy from `plugin details`) indicates users leave it enabled by default — its standing cost is low enough not to reclaim. |
| **4** | Likely-left-enabled by cost proxy; no telemetry yet. |
| **3** | Borderline — plausibly toggled off by context-sensitive users; unmeasured. |
| **2** | Cost proxy suggests users would disable it between uses to reclaim context. |
| **1** | Clearly a toggle-off-after-use plugin by cost; defeats the always-available premise. |

**Go deeper**: `../foundations/context-economy-foundations.md` §"The empirical signal".
**Test** `[hypothesis]`: this is unverified in v0.1. Track install/disable telemetry and `plugin details` always-on cost across real plugins; do not assert a score above 3 without data. (Default to 3 with a measurement note until telemetry exists.)

---

## §Anti-patterns

### AP-CE1 — The standing-tax MCP
**Symptom**: A bundled MCP's tool defs dominate always-on context (D1 ✗, D4 ✗), often 1:1-wrapping an API (P2 ✗).
**Root cause**: MCP bundled for breadth, not for a core external-state need.
**Correction**: Drop or consolidate the MCP; bundle one only when external state is the plugin's point, with task-level tools.

### AP-CE2 — The front-loaded reference tree
**Symptom**: Bundled skills push reference content into SKILL.md or descriptions (D2 ✗, D3 ✗); everything is paid every session.
**Root cause**: Progressive disclosure not applied — SKILL.md is the content, not a TOC.
**Correction**: SKILL.md as TOC; references one level deep, on-demand; logic in scripts.

### AP-CE3 — The padded description
**Symptom**: Component descriptions are verbose paragraphs (D1 ✗) — standing cost with no routing benefit.
**Root cause**: Confusing "more words" with "better routing."
**Correction**: Terse, specific descriptions (what + when + triggers); detail goes on-invoke.

### AP-CE4 — The plugin-CLAUDE.md that does nothing
**Symptom**: Standing instructions placed in a plugin-root `CLAUDE.md` — which isn't loaded.
**Root cause**: Expecting CLAUDE.md to carry plugin context.
**Correction**: Move instructions into a skill (disclosed on-invoke).

---

## §Hard Tests

1. **The always-on audit** (D1): from `plugin details`, is anything other than terse descriptions dominating always-on cost?
2. **The front-load test** (D2/D3): is substantial reference content paid every session rather than on-invoke?
3. **The MCP-justification test** (D4): is every bundled MCP core to the one-sentence job, or "in case"?
4. **The toggle-map test** (D5): does standing cost map to one coherent toggled capability?
5. **The stays-enabled hypothesis** (D6): by cost proxy/telemetry, would users leave it on? (Unverified in v0.1 — measure, don't assert.)
