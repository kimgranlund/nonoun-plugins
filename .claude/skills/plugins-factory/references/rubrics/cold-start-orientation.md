---
date: 2026-05-31
status: draft
version: "0.1.0"
---

# Cold-Start Orientation — Best Practices Rubric

**A skill that requires 200 lines of reading before a user can take their first step has failed orientation.** The cold-start surface is the first screen — everything before the user must scroll. If a user invoking "use [skill]" or "how should I use [skill]?" cannot get a helpful, actionable response from that surface alone, the skill has a discoverability failure that no amount of internal quality makes up for.

**Grounding:** The CS evaluator topical section (CS1–CS5 in `eval-prompts.md`) operationalizes this rubric as adversarial prompts. The CS2 gate ("Quick Start present with all three elements") is the mechanically-checkable floor; the dimensions below score the quality above that floor. The fresh-context test (V2 in `eval-prompts.md`) and the bypass test (D2 in `skills-authoring.md`) address related but distinct properties.

**Companion docs:**
- `rubric-foundations.md` (in `skills-studio` — not bundled here) — what rubrics are and why they structure judgment
- `skills-authoring.md` (in `skills-studio` — not bundled here) — D1 description quality, D2 discoverability
- `harness-design.md` (in `skills-studio` — not bundled here) — D1 structural clarity, D4 skill surfacing

---

## §The Problem

A skill with excellent internal quality — precise modes, thorough reference files, well-typed rubrics — still fails if a user invoking it cannot orient themselves in under 60 seconds. The failure manifests in three patterns:

1. **Front-loaded detail.** The SKILL.md opens with First Principles, Decomposition steps, or a Reference table — all valuable but none answering "what do I provide and what do I get back?" A user reads 150 lines and still doesn't know whether their problem is in scope.

2. **Delegated examples.** Worked examples live in `references/examples/` — correct for load-on-demand architecture, but invisible at cold start. The user cannot visualize the output before committing.

3. **Vocabulary barriers.** Key concepts ("blueprint," "selection eval," "rubric," "trifecta") appear in the first screen but are defined only in reference files. The user encounters terms they cannot look up without leaving the skill.

The rubric below scores orientation quality on six dimensions. D1 and D5 are `[gate]` — mechanically checkable. D2, D3, D4, and D6 are `[review]` — require reading the skill and judging quality.

---

## §First Principles

### 1. The cold-start surface is the first 40–50 lines after frontmatter

Everything before the first scroll is the surface a user sees when invoking the skill. The skill cannot control how much context the user has; it can control what they see first. The Quick Start section exists to answer the two most common orientation questions ("use [skill]" and "how should I use [skill]?") within that surface.

### 2. One worked example is worth five descriptions

A user who can see a concrete prompt → output pair understands the skill's scope, specificity, and output shape in seconds. A user who reads "this skill produces a structured scorecard with dimension scores, evidence, top issues by severity, and recommended next actions" still doesn't know what to type. The example anchors the abstraction.

### 3. Concepts must be defined where they first appear

A skill may use specialized vocabulary ("inversion," "selection eval," "[gate]/[review]") that is precise and correct. If that vocabulary first appears in the Quick Start or first screen, it must be defined there — a one-sentence inline definition. External reference files are not findable at cold start.

### 4. Mode selection is the first decision — make it trivial

Most skills have 3–5 modes. A user who has to read the full Modes section to know which one applies has failed cold start. The Quick Start mode table gives each mode a one-clause trigger condition: "You have a goal and want the right topology → PLAN." That one line is the orientation.

### 5. The orientation question is "what do I bring and what do I get back?" not "how does the skill work?"

Users invoking a skill do not need to understand its internals. They need to know: what should I provide? what will I receive? Cold-start orientation answers these two questions before explaining anything else. Architecture, reference structure, and §SelfAudit are load-on-demand, not cold-start.

---

## §The Rubric

### Dimension 1 — Quick Start presence `[gate]`

Does a `## Quick Start` section (or equivalent orientation block by any name) exist within the first 50 lines of SKILL.md after the frontmatter?

The section must contain all three: (a) at least one worked example prompt showing what a user would actually type, (b) what to provide/bring (2–4 bullet points), and (c) a mode table or equivalent path-selection guide.

| Score | Evidence |
|---|---|
| **5 — Excellent** | Quick Start present within 50 lines. All three elements present. Example is specific and realistic (not a placeholder like "use [skill] for your goal"). Mode table maps user situations to mode names in one clause per row. |
| **4 — Good** | Quick Start present. All three elements present but one is thin (e.g., mode table has vague trigger conditions, or example uses a generic scenario). |
| **3 — Adequate** | Quick Start present but missing one of the three elements (example, bring list, or mode table). |
| **2 — Poor** | An orientation block exists but is beyond line 50, or lacks two of the three elements. |
| **1 — Failing** | No Quick Start or orientation block. User must read the full SKILL.md to orient. |

**Test:** grep SKILL.md for `## Quick Start` or equivalent. If found, check line number and verify all three elements. If any element is absent or the section is beyond line 50: FAIL.

---

### Dimension 2 — First-screen coverage `[review]`

Can a user answer "use [skill-name]" helpfully from the first visible screen (lines 1–40 after frontmatter) without scrolling?

"Helpfully" means: the agent responding can name what to provide, offer a first clarifying question or first step, and set expectations for the output shape.

| Score | Evidence |
|---|---|
| **5 — Excellent** | Lines 1–40 contain enough to respond to "use [skill]" without scrolling: the Quick Start example anchors the task, the bring list names inputs, the mode table routes the user. An agent reading only the first screen responds usefully. |
| **4 — Good** | First screen enables a useful but incomplete response — the agent can explain what the skill does and ask a clarifying question but cannot set full output expectations. |
| **3 — Adequate** | First screen enables the agent to confirm the skill is the right one but not to specify what the user should provide or what they'll receive. |
| **2 — Poor** | First screen contains only the frontmatter description (triggers, boundaries) but no orientation content. Agent must scroll to answer "use [skill]." |
| **1 — Failing** | First screen is opaque to a first-time user. The agent reading only lines 1–40 cannot produce a useful response. |

**Test:** Read only lines 1–40 of SKILL.md. Simulate responding to "use [skill-name]." Rate the quality of the response achievable from that context alone.

---

### Dimension 3 — Worked example embedded `[gate]`

Is at least one worked example embedded in SKILL.md itself — not delegated to `references/examples/` or another file?

An embedded example shows: a specific user prompt (what they typed), the topology/mode selected, and the output shape (what they received). A reference to a worked example ("see `references/examples/example-a.md` for a worked example") does not pass this gate.

| Score | Evidence |
|---|---|
| **5 — Excellent** | At least one fully worked example embedded in SKILL.md. The example is specific: a real user prompt (not "example goal"), a selected mode/topology, and a description of the output received. |
| **4 — Good** | An embedded example exists but is partial — the prompt is specific but the output is described abstractly, or the example lacks the mode/topology selection. |
| **3 — Adequate** | A brief inline example exists (a one-line prompt with no output description) or a partial walkthrough. |
| **2 — Poor** | SKILL.md only references external examples ("see `references/examples/`") without embedding any content. |
| **1 — Failing** | No examples anywhere in SKILL.md — examples are fully external or absent. |

**Test:** Search SKILL.md for a realistic user prompt followed by a description of the response it would generate. If only a cross-reference to external files: FAIL.

---

### Dimension 4 — Example specificity `[review]`

Is the worked example realistic and specific enough to work with — or is it a generic placeholder?

A specific example names a real domain, a real constraint, and a real success criterion. A generic example ("use [skill] to achieve [goal]") teaches nothing about what the skill handles.

| Score | Evidence |
|---|---|
| **5 — Excellent** | Example prompt names a real domain ("our OAuth auth migration," "a read-only document search MCP"), real constraints ("all existing tests must stay green," "agent must never write"), and a clear success criterion. Output description matches the skill's actual artifact shape. |
| **4 — Good** | Example has a specific domain but a generic constraint or success criterion. Output description is accurate but not tied to the specific example. |
| **3 — Adequate** | Example has a real domain but uses placeholder language for constraints ("some task," "relevant criteria"). Output description is abstract. |
| **2 — Poor** | Example is a template: "use [skill] to [verb] [noun]." It demonstrates format but not content. |
| **1 — Failing** | No example, or example is so generic it provides no signal about the skill's scope or output shape. |

**Test:** Read the example prompt. Could a user copy-paste it and get a useful response? If not — if it requires filling in blanks — it's a template, not an example.

---

### Dimension 5 — Key concept inline definition `[gate]`

For each key concept that appears in the Quick Start or first screen (e.g., "blueprint," "selection eval," "rubric," "inversion," "[gate]/[review]"): is it defined inline (a one-sentence definition at first appearance), or does it first appear undefined?

Count the undefined concepts in the first screen.

| Score | Evidence |
|---|---|
| **5 — Excellent** | Every concept introduced in the Quick Start or first screen has an inline definition at its first appearance. No concept is used before it is defined. |
| **4 — Good** | 0–1 undefined concepts in the first screen. The undefined concept is a general term a technically literate reader would know. |
| **3 — Adequate** | 2–3 undefined concepts — the user encounters specialized vocabulary they cannot look up without loading a reference file. |
| **2 — Poor** | 4+ undefined concepts in the first screen. The Quick Start is only navigable by someone who already knows the skill. |
| **1 — Failing** | The Quick Start uses 5+ undefined skill-specific terms. A first-time user cannot read it without external reference. |

**Test:** List every noun or labeled concept in the first 50 lines. For each: is it defined at or before its first use in those 50 lines? Count undefined = FAIL count.

---

### Dimension 6 — Mode clarity `[review]`

Can a user identify which mode applies to their situation after one read of the mode table — without reading the full Modes section?

Each mode table row should have: the mode name, a one-clause trigger condition, and (optionally) what it produces. "PLAN — select and wire a loop" is a name and a verb phrase; it's adequate. "PLAN — you have a goal and want the right topology selected and a blueprint emitted" is a trigger condition; it's excellent.

| Score | Evidence |
|---|---|
| **5 — Excellent** | Mode table maps user situations to modes in one clause per row (e.g., "You have a goal; want the topology selected → PLAN"). A user can self-classify without reading further. Mode names are distinctive — no two are synonymous. |
| **4 — Good** | Mode table exists. Most rows have clear trigger conditions. 1 row uses abstract language ("advanced use") that requires reading further. |
| **3 — Adequate** | Mode table exists but trigger conditions are verb-only ("select," "compose," "evaluate") — the user knows what the mode does but not when to use it. |
| **2 — Poor** | Modes are listed in the Modes section (not the Quick Start) and require reading 100+ lines to find. No mode table in the first screen. |
| **1 — Failing** | No mode table or mode classification guide. User cannot determine which mode applies without reading the full SKILL.md. |

**Test:** Read only the mode table. Without reading the Modes section, classify: which mode would you use if your situation is [concrete scenario]? If you cannot answer: D6 fails.

---

## §Anti-Patterns

### AP-CO-1 — The reference-delegated example
**Symptom:** SKILL.md references a worked example in `references/examples/` or a link to another file. The agent following the skill loads it on demand — but a first-time user arriving at the skill for orientation cannot see it.
**Root cause:** The SKILL.md was written for load-on-demand reference use, not cold-start orientation.
**Correction:** Embed a brief but complete example directly in the Quick Start (3–5 lines showing prompt → selected path → output shape). The external worked example can stay; the Quick Start example is additional, not a replacement.

### AP-CO-2 — The mode menu without trigger conditions
**Symptom:** The mode table lists mode names with action verbs ("Select," "Compose," "Evaluate") but no user-situation trigger conditions. The user knows what each mode does but not which one applies.
**Root cause:** Mode descriptions were written from the agent's perspective ("this mode selects") rather than the user's ("use this mode when you have X").
**Correction:** Rewrite each mode table row as a trigger condition: "You have [situation] → [Mode]."

### AP-CO-3 — The vocabulary barrier at entry
**Symptom:** The Quick Start introduces specialized terms ("blueprint," "selection eval," "[gate]/[review]") without definition. These terms are defined in reference files the user hasn't loaded yet.
**Root cause:** Authors write for readers who already know the skill; the Quick Start inherits that vocabulary.
**Correction:** Add a one-sentence inline definition at each term's first appearance in the first 50 lines: "`[gate]` = mechanically checkable (pass/fail by inspection); `[review]` = requires expert judgment (scored 1–5 with evidence)."

### AP-CO-4 — The generic worked example
**Symptom:** The worked example uses placeholder language: "use [skill] to achieve [goal]." It demonstrates format but not substance.
**Root cause:** Authors template-out the example to keep it broadly applicable, producing something that is technically correct but operationally useless.
**Correction:** Replace with a real domain, real constraint, and real success criterion. The example should be narrow enough to be specific and broad enough to generalize.

---

## §Hard Tests

1. **The 40-line test:** Read lines 1–40 of SKILL.md (after frontmatter). Respond to "use [skill-name]." If the response requires scrolling past line 40 to be useful: D2 fails.

2. **The Quick Start gate:** Find the `## Quick Start` section. Verify: (a) within 50 lines, (b) worked example present and specific, (c) bring list present, (d) mode table with trigger conditions. Any missing: D1 fails.

3. **The copy-paste test:** Copy the worked example prompt exactly as written. Would submitting it to the skill generate a useful, non-generic response? If it contains placeholders like "[goal]" or "[topic]": D4 fails.

4. **The undefined vocabulary test:** List every concept in the first 50 lines. Count how many have no inline definition. Count > 2: D5 fails.

5. **The self-classify test:** Read only the mode table row trigger conditions. Given a concrete scenario (pick one relevant to the skill's domain), can you identify the correct mode without reading the Modes section? If no: D6 fails.

6. **The bypass test** (from `skills-authoring.md`): Give a fresh agent the skill's target task without mentioning the skill by name. Does the agent route to it? If not — and if the cold-start surface isn't the cause — the discoverability failure is in the description, not here.
