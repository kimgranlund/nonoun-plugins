---
date: 2026-05-23
status: draft
version: "0.2.0"
---

# Skills Authoring — Best Practices Rubric

**A skill is a reusable, agent-invocable instruction set for a specific capability.** It is
not documentation. It is not a knowledge dump. It is a contract surface: here is what this
skill can do, when to invoke it, and what "done" looks like.

The measure of a skill is whether it compounds over invocations. The first time a senior skill
is used: 2 hours. The tenth time: 15 minutes. The twentieth time: 5 minutes, mechanical. If
the N+1th invocation takes the same time as the Nth, the skill has stopped compounding — it
is accumulating drift instead of insight.

This rubric is the **universal scoring layer** above the practitioner's checklist in
`SKILLS-best-practices.md` (chat-ui). It is applicable to any agent skill system, not just
Claude Code. The checklist says "here's how to do it"; this rubric says "here's how to measure
whether you did it well."

**Grounding**: Anthropic official guidance at
`platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`; Boris Cherny's
principles from BORIS-feedback.md; production patterns from SKILLS-best-practices.md.

**Companion docs:**
- `harness-design.md` (in `skills-studio` — not bundled here) — where skills surface in the agent ecosystem
- `context-engineering.md` (in `skills-studio` — not bundled here) — progressive loading of skill content
- `agentic-coding.md` (in `skills-studio` — not bundled here) — PEV as the loop skills must close

---

## §The Problem

An unmaintained skill library will develop four failure modes over time:

1. **Drift**: the skill describes a workflow that the substrate no longer supports. The agent
   follows the skill's instructions, hits errors the skill doesn't anticipate, and improvises.
2. **Bloat**: every cycle adds to the skill's SKILL.md. Nothing is removed. The skill becomes
   archaeology — half current knowledge, half arc history from 9 months ago.
3. **Bypass**: the skill isn't discovered (missing from harness), isn't triggered (wrong description),
   or isn't trusted (gave bad results once). The agent improvises the same workflow from scratch
   every session.
4. **Non-compounding**: the skill is invoked regularly but each invocation still takes the same
   time as the first. The procedure is not mechanized; the agent reacts to each step rather than
   anticipating it.

The rubric below scores on these four failure modes plus the foundational design properties
that prevent them.

---

## §First Principles

### 1. WHAT + WHEN + NOT — the description is the routing signal

Per Anthropic's official guidance: the `description:` field is the most important field for
routing accuracy. The model reads it when deciding whether a skill applies. It must contain:
- **WHAT**: what the skill produces (one precise sentence, not a tag cloud)
- **WHEN**: the triggering condition or task shape (specific, not generic)
- **NOT** (for skills with overlapping siblings): what does NOT trigger this skill

A description that's all triggers without WHAT looks like a tag cloud; the model can't tell
what the skill accomplishes. A description that's all WHAT without WHEN looks like documentation;
the model can't tell when to activate it. Both hurt routing accuracy.

### 2. Inversion — the skill is a contract surface, not a script

The skill's job is: tell the agent **which tool**, **which mode**, **when**. Not: tell the
agent the step-by-step procedure the tool executes. Contrast:

- ❌ Un-inverted: "To bump versions, for each package.json, find the version field, change X.Y.Z
  to X.Y.Z+1, save. Repeat for all 9 packages. Then regenerate the lockfile..."
- ✅ Inverted: "Bump 9 package.json versions. Use `scripts/bump.mjs --from 0.X.Y --to 0.X.Z`"

The LLM does NOT reason through what `bump.mjs` does internally. It reads the citation, runs
the command, oversees the result. The script is the source of truth for *how*; the skill is
the source of truth for *when + which*.

### 3. Citation, not knowledge — cite the substrate, don't describe it

Per-substrate facts (component behavior, API signatures, file paths, gate rules) live in the
substrate (YAML, TypeScript, ADRs, specs). The skill cites these by tag or path. When the
skill describes substrate facts in prose, it accumulates drift the next time the substrate changes.

The rule: whenever you write "the X component does Y" in a skill — stop. Is that fact in the
substrate already? If yes, cite the tag, don't describe it.

### 4. Senior skills absorb; standalone skills focus

**Senior skill**: a rollup that absorbs 3+ prior skills, scripts, or ad-hoc procedures into
one coherent folder. Many modes (5-10), many references (8-15), own `scripts/` directory,
§SelfAudit framework, §Teach extensibility required. One customer's complete workflow.

**Standalone skill**: focused, single-purpose. One or two modes, ≤3 references, no scripts
directory, no §SelfAudit required. Small scope means organic content accretion rarely happens.

The discipline is knowing which category a skill belongs in — and NOT adding senior-skill
ceremony to a standalone. If it doesn't absorb scattered concerns, it's standalone. Keep it
light.

### 5. Plan-Execute-Verify is the loop every skill must close

Per Boris: *"Give Claude a way to verify its work. If Claude has that feedback loop, it will
2-3x the quality."* A skill that doesn't define the verify target is a slop generator with extra
ceremony. The verify target must be named in the skill, per the mode that invoked it:

- Release skill: curl registry.npmjs.org → 200
- Authoring skill: build verify passes + demo page renders
- Composition skill: composed output renders correctly + Playwright snapshot
- Pipeline skill: eval thresholds hold

### 6. Build for the model six months from now

Per Boris's manager Ben (Lenny's podcast): *"Build for the model six months from now."*
Don't over-engineer the skill to compensate for current-model limitations that improving
memory/context will obsolete. The right question isn't "how do we compensate for what the
model can't do today" — it's "what will still be needed when context is 2M tokens and the
model rarely forgets?"

Re-examine the ceremony quarterly. Anything still load-bearing earns its keep; anything
obsoleted by improved model capability gets retired.

---

## §The Rubric

### Dimension 1 — Description quality (WHAT + WHEN + NOT) `[gate]`

Is the skill's description sufficient for accurate routing?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Description ≤ 1024 chars. Contains one WHAT sentence, specific WHEN conditions, and (if siblings exist) a NOT clause disambiguating from nearest sibling. Activates on the right phrases in an eval; does not activate on sibling phrases. |
| **4 — Good** | WHAT and WHEN present. NOT omitted but sibling overlap is low enough not to cause misrouting. Description reads as a capability claim, not a tag cloud. |
| **3 — Adequate** | WHAT present. WHEN is generic ("use for coding tasks"). Over-broad; activates on phrases that belong to siblings. |
| **2 — Poor** | Description is only triggers (a list of phrases). Model can route to it but can't tell what shows up. |
| **1 — Failing** | Description is a vague one-liner that describes anything ("helps with development tasks"). Impossible to score routing accuracy against. |

**Test**: run a 20-phrase routing eval against the skill's description. What fraction of correct phrases activate it? What fraction of sibling phrases incorrectly activate it?

---

### Dimension 2 — Cold-start discoverability `[review]`

Can an agent find and activate the skill within 5 actions from cold-start?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Skill surfaced at Tier 1 (AGENTS.md, if cross-cutting senior skill) or Tier 2 (INDEX.md manifest). SKILL.md first screen contains: mode menu, posture, when to use, pointers to references. Agent selects correct mode within 3 actions. |
| **4 — Good** | In AGENTS.md or manifest. Mode menu exists but may take 2-3 reads to find the right mode. Agent navigates correctly within 5 actions. |
| **3 — Adequate** | Skill exists but is not in AGENTS.md or manifest. Agent must browse the skills folder. Discovery depends on file naming and description. |
| **2 — Poor** | Skill exists but is undiscoverable by convention. Agent would bypass it unless explicitly told about it. |
| **1 — Failing** | Skill is not surfaced anywhere. Agent cannot discover it without reading every SKILL.md file. |

**Test**: give an agent a task that the skill is designed for. Does the agent use the skill without being told to? This is the bypass test.

---

### Dimension 3 — Inversion quality (contract surface vs. script) `[review]`

Does the skill tell the agent *which tool* and *when*, rather than *how to manually execute*?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Every repeated procedure is cited as a script command (`scripts/X.mjs --flag`). No step-by-step prose for mechanizable operations. Agent's job is decision-making (which mode? which tool?) and observation (did the gate pass?), not manual execution. |
| **4 — Good** | Most procedures are inverted. 1-2 multi-step prose blocks remain for genuinely judgment-heavy steps that can't be mechanized yet. |
| **3 — Adequate** | Mix of inverted and un-inverted procedures. Some scripts exist; others are still written as step-by-step prose. |
| **2 — Poor** | Most procedures are written as step-by-step manual instructions. Agent is the script. High variance between invocations. |
| **1 — Failing** | No mechanization. Every mode is a list of manual steps. The skill is a tutorial, not a capability contract. |

**Test**: for each mode, count procedural prose steps that could be mechanized. Any step that is (a) repeated across sessions, (b) has clear pass/fail, (c) has silent failure modes, or (d) has destructive blast radius — is mechanize-bait. If > 3 mechanize-bait steps per mode, the inversion discipline is incomplete.

---

### Dimension 4 — PEV binding (verify target per mode) `[review]`

Does the skill define what "done" looks like, per mode, in terms of real-product state?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Every mode has an explicit verify target naming the real-product check (not internal self-checks). `§Plan-Execute-Verify` section or equivalent visible at cold-start. Verify step is mandatory, not optional. |
| **4 — Good** | Verify targets named for high-stakes modes. Low-stakes modes implied. Agent knows when work is done without improvising. |
| **3 — Adequate** | "Verify" mentioned but verify targets are internal (test pass, compile success). Real-product state not explicitly checked. |
| **2 — Poor** | No verify targets. Skill ends at "execute the procedure." Agent declares done when the last step completes. |
| **1 — Failing** | Verify step actively missing or discouraged. Skill says "proceed immediately" without verification language. |

**Test**: for the most-used mode: what is the last thing the agent does before declaring done? If the answer is not the real-product state, the PEV binding is incomplete.

---

### Dimension 5 — Drift resistance (§SelfAudit + citation discipline) `[gate]`

Does the skill maintain accuracy over time, or does it accumulate drift?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Senior skills carry an audit script that bidirectionally checks declared vs. on-disk state. All substrate facts are cited (not described). §SelfAudit runs after every §Teach landing. Audit passes before any commit. |
| **4 — Good** | Some mechanized audit exists. Most substrate facts cited. Manual review catches most drift. |
| **3 — Adequate** | No audit script but drift is caught during skill use (agent hits an inconsistency, corrects it). Reactive rather than proactive. |
| **2 — Poor** | No audit. Substrate changes without skill updates. Drift accumulates across cycles. Agent improvises around stale instructions. |
| **1 — Failing** | Skill describes substrate facts inline. When substrate changes, skill becomes actively misleading rather than just stale. |

**Test**: change one substrate fact (rename a function, update a file path). Does the skill still claim the old name? If yes, drift has already occurred and there's no mechanism to catch it.

---

### Dimension 6 — Compounding (does it get faster?) `[review]` `[hypothesis]`

Is the Nth invocation faster than the 1st, or has the skill plateaued?

> **Note**: The timing figures below (2h → 30m → 15m → 5m) are an unverified hypothesis. They
> represent the intended trajectory, not measured outcomes. Before treating compounding as a
> validated property of any skill, collect timing data from real invocations — controlling for
> model version improvements, harness changes, and operator learning effects. Until then, this
> dimension is observable only as a directional trend, not as a scored fact.
>
> **Measurement plan** (required before promoting from `[hypothesis]` to `[review]`):
> - **Metric**: median wall-clock time-to-complete per mode per invocation (operator-recorded from first tool call to Verify Target confirmation). Track by mode separately — modes with different task sizes are not comparable.
> - **Sample size**: ≥5 real invocations per mode, spread across ≥30 days. Exclude runs where the task type changed materially (a new feature domain vs. the same domain).
> - **Control variables**: record model version and harness version alongside each timing; exclude runs where a model upgrade or harness change occurred mid-sample.
> - **Baseline**: invocation 1 (or first recorded) as the anchor.
> - **Judgment rule**: compounding is confirmed when median time at invocation 5 ≤ 50% of median time at invocation 1. A plateau is defined as < 10% improvement from invocation 5 to invocation 10 — flag the bottleneck (un-inverted procedure? missing script? stale instructions?) rather than continuing to score the hypothesis.

| Score | Evidence |
|---|---|
| **5 — Excellent** | Observed compounding with data: 1st invocation ~2h, 5th ~30m, 10th ~15m, 20th ~5m mechanical. Timing from real invocations, not estimated. Model version and harness state noted alongside timings. §Teach allows new patterns to enter without structural decay. |
| **4 — Good** | Qualitative compounding observed (operators report faster execution across cycles). No quantified timing but pattern is clear. |
| **3 — Adequate** | Some compounding: scripted steps are fast, judgment steps are still slow and variable. Net improvement from the first invocation but plateau has been hit. |
| **2 — Poor** | Each invocation takes roughly the same time. Nothing mechanical has been extracted. |
| **1 — Failing** | Later invocations are slower than the first. Skill has grown bloat (accumulated arc history, stale sections) that costs more time to navigate than it saves. |

**Test**: compare the time for the 1st invocation of a mode vs. the most recent. If no improvement is observed, identify the single bottleneck: un-inverted procedure? Missing script? Stale instructions?

---

### Dimension 7 — Roadmap hygiene (deferred scope declaration) `[gate]`

Does the skill have a canonical home for deferred, excluded, and planned work — separate from the skill body and changelog?

| Score | Evidence |
|---|---|
| **5 — Excellent** | `ROADMAP.md` exists with all three sections (Planned / Deferred / Out of scope). Deferred entries document the reason and a re-evaluation trigger. Out-of-scope entries document *why*, not just *what*. No forward-looking notes found in CHANGELOG.md, SKILL.md comments, or conversation context. |
| **4 — Good** | `ROADMAP.md` exists and is populated or intentionally empty. All three sections present. Minor: one deferred entry missing a reason or trigger. |
| **3 — Adequate** | `ROADMAP.md` exists, sections present, all entries empty. Acceptable for a new skill with no known deferred scope; not acceptable when CHANGELOG.md or SKILL.md contains forward-looking notes that should have migrated here. |
| **2 — Poor** | No `ROADMAP.md`. Deferred or excluded scope is buried in CHANGELOG.md, SKILL.md comments, or conversation context — discoverable by insiders only, invisible to new contributors. |
| **1 — Failing** | No `ROADMAP.md` and known deferred scope exists. New contributors will either add those features into the skill body (bloat) or duplicate work already considered and rejected. |

**Test**: scan CHANGELOG.md and SKILL.md for forward-looking language ("planned", "future work", "out of scope", "considered but rejected", "not yet implemented"). Any match found outside `ROADMAP.md` = convention is not being enforced.

---

## §Anti-patterns

### AP-01 — Append-only SKILL.md
**Symptom**: SKILL.md grows by 50 lines each cycle. Nothing is removed. §SelfAudit shows
stale sections and dead mode entries. The skill is half current knowledge, half historical record.
**Root cause**: Treating SKILL.md as a changelog rather than a living specification.
**Correction**: Prune at every major version. The skill body documents the *current* discipline;
the journal captures *how it got here*; the corrective-feedback chain captures *why we don't
do X anymore*.

### AP-02 — Premature senior-skill ceremony
**Symptom**: A standalone skill with 3 modes has §Teach, §SelfAudit, audit scripts, case studies,
INDEX.md entry, and AGENTS.md surfacing. One author, one use case. The ceremony costs more than
the skill saves.
**Root cause**: Over-generalizing from senior-skill patterns to all skills.
**Correction**: Apply the senior/standalone decision first. If it doesn't absorb scattered concerns
into a coherent folder, it's standalone. Standalone skills get: frontmatter, SKILL.md, references/,
CHANGELOG.md. Nothing more until scale demands it.

### AP-03 — Capability menu lies
**Symptom**: SKILL.md lists a mode ("🔍 Audit the release manifest") that links to a section
that doesn't exist, or exists as a 2-line stub.
**Root cause**: Menu items added aspirationally; sections not yet authored.
**Correction**: Per §8 of SKILLS-best-practices: every menu row is a contract. If you're not
ready to author the section, don't add the row.

### AP-04 — Description stuffing
**Symptom**: A 2000-character description containing 45 trigger phrases and 3 negative clauses.
Token budget wasted on over-specification; routing accuracy doesn't improve past ~15 phrases.
**Root cause**: Confusing "more triggers" with "better routing." The heuristic scorer's
anti-pattern: gaming it by stuffing triggers.
**Correction**: Per Anthropic guidance: ~100 tokens of frontmatter metadata is the right budget.
Every phrase must earn its keep. The discipline is distinctive vocabulary, not volume.

### AP-05 — Spec-before-prototype (ship → measure → write, not write → ship → measure)
**Symptom**: A vision document + best-practices guide authored before any skill evals exist.
The docs explain the pattern; no empirical validation that the pattern actually works.
**Root cause**: Writing the theory first because it feels like progress.
**Correction**: Per Boris B4 and §8 anti-pattern 8 of VISION-extensibility: ship the skill first,
run held-out eval prompts, observe what the model actually does with it, then write the meta-docs
to explain the pattern. Docs authored before evals are educated guesses, not lessons.

### AP-06 — Cross-contamination between arc history and skill body
**Symptom**: SKILL.md contains paragraphs like "in the 2025-Q4 release cycle, we discovered
that..." These are case studies, not procedures.
**Root cause**: §Teach landings that didn't route arc stories to the journal.
**Correction**: The decision tree's terminal branch ("this belongs in the journal, NOT the skill")
with a worked example showing the negative case. Arc stories that generalize become anti-patterns
or case studies. Arc stories that don't generalize live in the project journal, not the skill.

### AP-07 — Roadmap pollution via changelog or skill body
**Symptom**: CHANGELOG.md entries contain "considered but rejected", "out of scope for this release", or "planned for v1.0". SKILL.md has comment blocks like `<!-- TODO: add X -->`. Future contributors have no way to distinguish history from current intent, or current scope from deferred scope.
**Root cause**: No canonical home for forward-looking scope decisions, so they land wherever there is open space.
**Correction**: `ROADMAP.md` is the single, always-present home for planned, deferred, and excluded items. Changelog entries describe what *changed*; ROADMAP.md describes what *comes next* and what is *off the table*. Even an empty ROADMAP.md (sections present, no entries) signals this convention to first-time contributors.

---

## §Hard Tests

1. **The routing test**: run 20 user phrases against the skill's description using a simple
   TF-IDF or token-overlap scorer. What is the routing accuracy? Below 75% on own phrases,
   or above 20% on sibling phrases = failing.

2. **The bypass test**: give an agent the skill's target task without mentioning the skill.
   Does the agent use the skill? If not, the description or harness surfacing is inadequate.

3. **The one-shot test**: for the main mode, give the agent a standard invocation. Does it
   complete without operator intervention? If it requires 3+ mid-course corrections, the
   skill has insufficient specification depth.

4. **The inversion test**: count the mechanizable steps in the most-used mode. If > 3 steps
   are still prose that the agent manually executes, the inversion is incomplete.

5. **The stale-claim test**: pick 3 substrate facts cited in the skill. Verify each against
   current codebase. Any incorrect = drift is active.

6. **The audit test**: run `scripts/audit-<skill>-roster.mjs` (or equivalent). If there is
   no such script, ask: what would it check? The inability to answer suggests the skill doesn't
   have checkable invariants — which means either it's too vague (a problem) or it's genuinely
   standalone (fine, but then why is it treated as senior?).

7. **The Boris test**: read §13.8 of SKILLS-best-practices. Would Boris, with his vanilla-first
   discipline, look at this skill and say "I can see why this level of ceremony is justified"?
   Or would he say "this is a 50-line CLAUDE.md problem that someone turned into a 1500-line
   senior skill"?

8. **The roadmap test**: verify `ROADMAP.md` exists with Planned / Deferred / Out of scope sections.
   Then grep CHANGELOG.md and SKILL.md for: "planned", "future", "out of scope", "not yet", "TODO",
   "considered but". Any match found outside `ROADMAP.md` means the convention is not being enforced
   and that content needs to migrate.
