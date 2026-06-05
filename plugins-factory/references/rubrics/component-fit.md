---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Component Fit — Is Each Capability the Right Primitive?

The drill-down for holistic **P2**. A plugin bundles five primitives — hook, MCP, agent, skill, command — and the highest-frequency plugin defect is putting a capability in the wrong one. This rubric scores whether each capability's primitive matches the shape of its task.

Theory: `../foundations/component-fit-foundations.md`. Primary critic: **Chip H.** (determinism boundary) with **Elon M.** (delete-first) second.

---

## §The Problem

A `plugin.json` validates whether the JSON is well-formed. It cannot tell you that the "always run our linter" step was shipped as a skill (so it runs _usually_, until the day the model skips it), or that the bundled MCP exposes thirty endpoint-shaped tools that eat 50K of context before the first action. Component fit is invisible to manifest validation because it is a judgment about task-shape, not syntax — and it is the defect that most often makes a structurally-valid plugin behave badly.

---

## §First Principles

1. **A hook guarantees execution; a prompt does not.** Anything that must run on an event is a hook. A skill that "always" runs is a hope, not a guarantee.
2. **MCP is a perimeter, not a wrapper.** External state earns an MCP; an MCP that maps endpoints 1:1 is the most-cited anti-pattern in the field.
3. **"Everything a skill" is the silent default failure.** Skills are the flexible default, which is exactly why required guarantees and external integrations get mis-filed as skills.
4. **Use the fewest primitives the shapes require.** The defect is mismatch, not minimalism — a pure-knowledge plugin is correctly all-skills.
5. **Write the fit table before the manifest.** `capability → primitive → why` is both the evidence this rubric scores and the manifest's skeleton.

---

## §The Rubric

### D1 — Guarantees Are Hooks `[gate]`

Is every capability that _must_ run on an event implemented as a hook, not a hopeful instruction?

| Score | Evidence |
| --- | --- |
| **5** | Every must-run-on-event capability (format, lint, policy gate, secret scan, notify) is a hook in `hooks/hooks.json` with an explicit event + matcher. No "always do X" instruction substitutes for a guarantee. |
| **4** | Guarantees are hooks. One low-stakes "should usually" step left as an instruction, where a miss is harmless. |
| **3** | A capability that should always run is a skill/prose instruction; it runs most of the time. No active incident yet, but the guarantee is probabilistic. |
| **2** | Multiple required guarantees depend on the model remembering to invoke a skill. The enforcement story is "the model is told to." |
| **1** | A safety- or policy-critical step (secret scan, destructive-op guard) is a prose instruction. One skipped invocation = a real failure. |

**Go deeper**: `foundations/component-fit-foundations.md` §"The decision ladder" (rung 1). **Test** (guarantee test): list every capability that must happen regardless of model behavior. Each one not implemented as a hook is a D1 defect; a _safety_-critical one not a hook = D1 fails.

---

### D2 — MCP Is an Intent Perimeter, Not an API Wrapper `[gate]` `[review]`

If the plugin bundles an MCP, are its tools task-level and bounded — or a 1:1 endpoint dump?

| Score | Evidence |
| --- | --- |
| **5** | Bundled MCP (if any) exposes task-level tools (`schedule_event`, not `search` + `create` + `get` chained), ≤~25 tools, prefix-namespaced, high-signal output. The MCP exists because the capability needs _external state/actions_, not as a delivery vehicle for knowledge. |
| **4** | Intent-level tools, reasonable count. One tool is endpoint-shaped, or output is slightly verbose. |
| **3** | A mix: some task-level, some endpoint-level tools. Count creeping toward 25+. The model occasionally chains tools that should be one. |
| **2** | Mostly 1:1 endpoint wraps; the model must orchestrate multi-call chains ("token arson"). Tool defs are a noticeable always-on tax. |
| **1** | An everything-MCP: 30+ endpoint tools, no consolidation. It is an API client wearing a plugin, and its definitions dominate context. |

**Go deeper**: `foundations/component-fit-foundations.md` §"Why the MCP bar is highest"; cross-check P6 (Context Economy). **Test** (wrapper test): count the bundled MCP's tools. >~25, or names that mirror API endpoints 1:1, = a wrapper → D2 ≤ 2. No bundled MCP = N/A (score the dimension out).

---

### D3 — Isolation & Parallelism Are Agents `[review]`

Is context-heavy or parallel work delegated to a subagent rather than run inline?

| Score | Evidence |
| --- | --- |
| **5** | Work that would pollute or blow the main context (large-file sweeps, fan-out research, a parallel review panel) is a bundled agent with its own context + a scoped tool set. Each agent's isolation/parallelism rationale is clear. |
| **4** | Heavy/parallel work is agentized. One borderline task runs inline that would modestly benefit from isolation. |
| **3** | Some context-heavy work runs inline, bloating the main thread; an agent would have helped but isn't fatal. |
| **2** | A clearly context-heavy or fan-out workload is crammed into a single skill/inline flow. |
| **1** | No use of isolation where the plugin's core workflow plainly needs it (e.g. a 50-file audit done inline). |

**Go deeper**: `foundations/component-fit-foundations.md` §"The decision ladder" (rung 3). Note the loader rule (P9): bundled agents cannot declare `hooks`/`mcpServers`/`permissionMode`. **Test**: for each capability, would it consume large context or benefit from parallelism? Any "yes" run inline = a D3 gap.

---

### D4 — Knowledge Is a Progressively-Disclosed Skill `[review]`

Are auto-invoked knowledge workflows skills that load on demand, not front-loaded prose?

| Score | Evidence |
| --- | --- |
| **5** | Repeatable, knowledge-rich, model-auto-invoked workflows are skills with progressive disclosure (SKILL.md as TOC; references on demand). The model reaches for them by description match, not because they're always loaded. |
| **4** | Knowledge is skill-shaped and mostly disclosed. One reference is heavier than needed. |
| **3** | Knowledge is a skill but front-loads its reference content (no progressive disclosure), taxing context when invoked. |
| **2** | Standing knowledge is jammed into always-on surfaces (verbose descriptions, a plugin-root file) instead of an on-demand skill. |
| **1** | The plugin's knowledge is an undifferentiated dump with no skill structure or load conditions. |

**Go deeper**: `foundations/component-fit-foundations.md`; cross-check P6 and `skills-studio` `context-engineering.md`. **Test**: for each bundled skill, does SKILL.md act as a TOC with references loaded on demand? Front-loaded reference trees = a D4 gap.

---

### D5 — User-Named Actions Are Commands `[review]`

Does the plugin offer an explicit, user-typable entry point for its main workflow?

| Score | Evidence |
| --- | --- |
| **5** | The main workflow has an explicit `/command` (or user-invokable skill) the user fires by name. The model-decides vs user-types split is deliberate: rich-description skills for auto-routing, memorable commands for muscle-memory actions. |
| **4** | An explicit entry exists; one action that users would type by name is only model-routed. |
| **3** | Everything is model-invoked; a human who installs the plugin has no obvious typed entry point to start its main flow. |
| **2** | Entry points are unclear; the user must know internal skill names to trigger anything. |
| **1** | No discernible entry point — neither a command nor a discoverable primary skill. |

**Go deeper**: `foundations/component-fit-foundations.md` §"When the choice is genuinely ambiguous"; cross-check P7 (Routing). **Test**: can a fresh installer start the plugin's main workflow by typing something, or only by hoping the router fires a skill? No typed entry = D5 ≤ 3.

---

### D6 — Fit Is Declared & Justified `[gate]`

Is each capability's primitive named and justified — or defaulted?

| Score | Evidence |
| --- | --- |
| **5** | A `capability → primitive → why` table exists (in the plugin's docs or the author's output). Every choice is justified against the ladder. No capability was defaulted to "skill" without considering whether its shape demanded a hook/MCP/agent. |
| **4** | Fit is declared for all but 1–2 capabilities; those are obvious defaults that happen to be correct. |
| **3** | Fit is implicit — the primitives are _mostly_ right but no reasoning is recorded; a reviewer must reverse-engineer the choices. |
| **2** | No fit reasoning; several capabilities are defaulted to one primitive regardless of shape. |
| **1** | Everything is one primitive (all skills / an everything-MCP) with no fit consideration at all. |

**Go deeper**: `authoring/build-against-the-standard.md` §"The component-fit decision is the first move". **Test**: does a `capability → primitive → why` table exist, and does each row's "why" cite the task-shape (must-run / external-state / isolation / knowledge / named-action)? Missing table = D6 fails.

---

## §Anti-patterns

### AP-CF1 — The hopeful guarantee

**Symptom**: A lint/format/policy step is a skill or a prose instruction (D1 ✗). It runs until the model skips it under load, and an unformatted/unsafe change lands. **Root cause**: "Hooks guarantee execution; prompts do not" wasn't applied. **Correction**: Move must-run-on-event capabilities to `hooks/hooks.json`.

### AP-CF2 — The API-wrapper MCP

**Symptom**: A bundled MCP exposes endpoint-shaped tools 1:1 (D2 ✗); their defs dominate always-on context (P6 ✗). **Root cause**: MCP treated as a delivery mechanism for an API instead of a curated intent perimeter. **Correction**: Consolidate to task-level tools; ≤~25; namespace; high-signal output.

### AP-CF3 — The everything-skill plugin

**Symptom**: Every capability is a skill (D6 ✗) regardless of shape — including a required guarantee and an external integration. **Root cause**: The flexible default applied without a fit pass. **Correction**: Write the fit table first; reassign guarantees to hooks and integrations to MCP+skill.

### AP-CF4 — The kitchen-sink primitive set

**Symptom**: The plugin uses all five primitives "because it can" — a hook, an MCP, three agents, ten skills — when two would do. **Root cause**: Over-fitting; mistaking primitive variety for sophistication. **Correction**: Use the fewest primitives the shapes require (Elon M.'s lens). Minimalism is not the defect; mismatch is.

---

## §Hard Tests

1. **The guarantee test** (D1): every must-run-on-event capability not a hook = a defect; a safety-critical one = a fail.
2. **The wrapper test** (D2): a bundled MCP with >~25 tools or 1:1-endpoint names = a wrapper.
3. **The isolation test** (D3): any context-heavy or fan-out workload run inline = a gap.
4. **The disclosure test** (D4): any bundled skill front-loading its references instead of acting as a TOC = a gap.
5. **The entry-point test** (D5): can a fresh installer _type_ something to start the main flow?
6. **The fit-table test** (D6): does `capability → primitive → why` exist with shape-based justifications?
