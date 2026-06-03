# Reference: Teach Protocol — Absorbing new knowledge into the adia-ui-authoring skill

**Ecosystem context:** This reference is one instantiation of a generalizable **extensibility** pattern shared across the forge skill family (the consumer-side composition skill in the adia-ui-factory plugin and the sibling **adia-ui-release** skill carry parallel `teach-protocol.md` files). The pattern separates universal components (the trigger cluster, the 7 anti-patterns, the 5-step landing procedure, the citation-vs-knowledge principle, the negative case) from skill-specific components (the decision tree's branches, the worked examples). When editing this file, preserve the universal sections verbatim where possible — they're shared infrastructure. The ecosystem-level rationale lives in `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md` and `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md`.

**Why this exists:** As the authoring skill absorbs new authoring-side patterns (new primitive-audit checklist items, new CSS / token / lifecycle rules, new shell-cluster decompositions, new module-promotion observations, new LLM-bridge defaults, new anti-patterns), each absorption was previously a one-off improvisation. This protocol gives every future "make sure `adia-ui-authoring` knows about [pattern]" request a deterministic landing path.

**Used by:** the `adia-ui-authoring` skill, when an agent receives one of the trigger phrases below. SKILL.md §Teach is the seed; this file is the binding procedure.

- "make sure `adia-ui-authoring` knows about [the new primitive contract / token rule / shell pattern]"
- "train `adia-ui-authoring` on [the new lifecycle rule / module-promotion observation]"
- "the skill should know about [the new CSS pattern from ADR-NNNN]"
- "absorb this authoring-pattern into adia-ui-authoring"
- "teach the skill about [the new LLM-bridge default / the new anti-pattern]"
- "[a FEEDBACK item resolved with this fix] — make sure the skill reflects it"

**Companion:** the `§SelfAudit` section + `scripts/audit-authoring-roster.mjs` (run after any §Teach landing to verify the mechanized axes hold — manifest / reference graph / capability-menu drift / authoring-roster currency), and [authoring-cycle.md](authoring-cycle.md) (the 5-step canonical procedure — §Teach landings near it should preserve its structure).

**Anti-companion:** the repo's dated journal (`docs/journal/YYYY/MM/<date>.md`) — one-off authoring debug stories, "how I caught the lifecycle leak today" arc stories belong there, NOT in the skill (see Branch H below).

---

## When to Use

Trigger phrases (mirrored from the SKILL.md §Teach section):

- "make sure `adia-ui-authoring` knows about X"
- "train the skill on X"
- "teach the skill about Y"
- "the skill should be aware of Z"
- "absorb [pattern / lesson / FEEDBACK resolution] into adia-ui-authoring"
- "update the skill to reflect [the new ADR / the resolved contract bug / the new shell pattern]"

This protocol applies when **another agent in the codebase** (substrate author, kanban worker, peer skill author) hands the authoring skill new knowledge to integrate. It does NOT apply when:

- You're authoring a NEW primitive right now (use mode 1 / [primitive-audit.md](primitive-audit.md) + [authoring-cycle.md](authoring-cycle.md))
- You're modifying an existing primitive (use mode 2 / [authoring-cycle.md](authoring-cycle.md) step 2 onward)
- You're running cleanup / archive sweeps (use §SelfAudit's hygiene-cut shape)

The procedure below is the binding for skill-teach requests against `adia-ui-authoring`. Follow it in order. Each step has a stop-condition; do not skip ahead.

---

## Core Principles

1. **The skill is a citation layer, not a knowledge layer.** Per-component contracts live in `packages/web-components/components/*.yaml` (props, slots, decision rules, keywords, synonyms). ADR rationale lives in the repo's ADR set. The skill cites yaml tags + ADR numbers + contract-spec sections — it does NOT duplicate yaml prose or ADR rationale. When a §Teach landing's first instinct is "rewrite what `docs/specs/component-token-contract.md` says," stop: the substrate is the source of truth.
2. **Reference files are the cold-start budget's safety valve.** New content > ~50 LOC of procedural detail belongs in `references/<topic>.md` and is cited from SKILL.md, not inlined. This keeps the cold-start surface small (the ColdStartTriage menu) and lets modes load only their declared bundles.
3. **Triggers without binding sections are waste.** Adding keywords to `trigger:` without a corresponding section in SKILL.md (or referenced file) consumes activation budget for no payoff. Always pair the two.
4. **Capability menu items must reach an actual mode.** The cold-start `§ColdStartTriage` table is the agent's mental model on bare activation. Lies in that table cost more than gaps.
5. **Version bumps are PATCH for citations, MINOR for new sections, MAJOR for renames/removals.** Most §Teach landings here are PATCH (a new anti-pattern in [anti-patterns.md](anti-patterns.md), a new rule in [api-contract.md](api-contract.md)) or MINOR (a new mode, a new reference file). Never bundle MINOR with PATCH polish in one cut.
6. **§SelfAudit is the receipt.** A §Teach landing isn't done until `node scripts/audit-authoring-roster.mjs --strict` runs clean. If the audit regresses, fix in the same cut.

---

## The Decision Tree — where does new authoring knowledge land?

Run this **before** any patch. The wrong landing target wastes effort and creates drift.

```text
Is the new fact a PER-COMPONENT contract (slot, prop, decision rule,
keyword, synonym, a2ui.rule, default value)?
  → YES: belongs in YAML SoT, not in the skill.
         Open the component's `.yaml` file at
         `packages/web-components/components/<name>/<name>.yaml`
         (or `packages/web-modules/.../<name>.yaml`).
         Add to the appropriate field; run `npm run build:components`
         to regenerate sidecars + catalog. Skill cites by tag — it
         doesn't need to change.
         STOP HERE. Do not edit the skill.
         (See Worked Example A below.)
  → NO: continue.

Is it a NEW AUTHORING RULE that belongs to the four-axis contract
(props/attributes, CSS @scope/tokens, lifecycle, form-association)?
  → YES: route to the appropriate mode-1/2 reference:
           - prop naming / reflection / static properties → references/api-contract.md
           - @scope / variants / modes / L3 tokens → references/css-patterns.md
           - connected/disconnected / observers / listeners → references/lifecycle-patterns.md
           - raw colors / chrome palette / data palette → references/token-contract.md
           - general convention not fitting the above → references/code-style.md
         Add cross-link from authoring-cycle.md Step 3 if the new
         rule extends the non-negotiable list.
         (See Worked Example B below.)

Is it a NEW SHELL PATTERN — a new bespoke child concern, a 5th cluster
candidate, a new state-as-attribute convention, or an ADR-0023 extension?
  → YES: lands in references/shell-patterns.md (mode 3). Add to
         the 4-concern decomposition heuristic if the concern is new;
         add to the pitfall list if it's a failure mode; add to the
         4-canonical-cluster table if it's a 5th instance.
         (See Worked Example C below.)

Is it a NEW MODULE-PROMOTION pattern — a new OD-NNN rule, a new
cluster-placement consideration, a new phase or sweep technique?
  → YES: lands in references/module-promotion.md (mode 4). The
         5-phase arc is the spine; new ODs extend the "Two rules from
         observed bugs" section. Add a worked-example reference if
         the pattern is grounded in a real arc.
         (See Worked Example D below.)

Is it a NEW LLM-BRIDGE DEFAULT or extension procedure step?
  → YES: lands in references/llm-bridge.md (mode 6). The 5 hard
         rules are the spine; new rules extend that list. The
         "add a 4th provider" 8-step procedure extends if a new
         provider class (passthrough proxy, smart proxy, hybrid)
         needs documenting.
         (See Worked Example E below.)

Is it a NEW ANTI-PATTERN or WORKED EXAMPLE?
  → YES: lands in references/anti-patterns.md (failure-mode
         catalogue) OR references/worked-example.md (positive
         example). Anti-patterns get the AP-N## label form
         (AP-N## for new-component AP, AP-T## for token AP, etc.).
         Worked examples mirror the badge-ui / counter-ui shape.
         (See Worked Example F below.)

Is it a METHODOLOGY / POSTURE shift — a new cold-start mode, a new
§SelfAudit axis, a new architectural principle (§FirstPrinciples
extension)?
  → YES: lands INLINE in SKILL.md (the procedural spine). These
         shape every mode: §Mission, §ColdStartTriage, §Posture,
         §LoadingProtocol, §FirstPrinciples, §Plan-Execute-Verify,
         §SelfAudit, §FileMap. They're allowed to grow because they
         shape every other section. Run §SelfAudit immediately to
         confirm the cold-start budget held.
         (See Worked Example G below.)

Is it a one-off AUTHORING ARC STORY, debug session, or LESSON LEARNED
for a specific component (one-off fix, journal-worthy)?
  → NO landing in the skill. It belongs in docs/journal/YYYY/MM/<date>.md
    where future archeology will find it (per the repo's journal
    discipline). The GENERALIZED rule extracted from the arc may
    graduate to the skill via one of the branches above, but the
    cycle-specific story stays in the journal.
    Skipping the skill is a FEATURE, not a gap.
    (See Worked Example H — the negative case.)
```

---

## The Five-Step Landing Procedure

After the decision tree picks a target, follow these steps in order:

### Step 1 — Audit before patching

Before writing anything:

1. **Read the target file in full.** Don't skim. The authoring-skill reference files have established voice + section ordering; patches must match.
2. **`git status` + `git log -5`** on the working tree. Confirm no peer activity in the skill directory (peer agents may be authoring sibling skills like **adia-ui-release** or the consumer-side composition skill). If a peer is dirty here, halt + coordinate.
3. **Grep for existing coverage.** Run `grep -rn "<keyword>" skills/adia-ui-authoring/` to confirm the new knowledge isn't already partly covered. If it IS, the landing is a _patch + augment_, not a _new section_.
4. **Confirm the landing-target choice.** Re-read the Decision Tree above against your specific case. Two minutes of "is this really a CSS pattern, or is it actually a lifecycle rule?" prevents two hours of misplaced content.

### Step 2 — Author the patch

Two shapes depending on Step 1's grep:

#### Shape A — NEW section / file (no existing coverage)

If the target is a new reference file: create `references/<topic>.md` with the canonical header (provenance, why-authored, used-by, companion, anti-companion), then "## When to Use", "## Core Principles", then content. Reference from SKILL.md §FileMap + §ColdStartTriage if it opens a new mode.

If the target is a new H2 inside an existing reference (most common for authoring-skill §Teach): find the semantically correct insertion point. E.g., a new lifecycle rule goes in `lifecycle-patterns.md` near related rules, not at the file's end. A new anti-pattern goes in `anti-patterns.md` under its axis (AP-N## / AP-T## / AP-S## / AP-L##).

#### Shape B — AUGMENT existing section (grep found partial coverage)

Read the entire existing section first, including any cross-references to other files. Author the augment as a sub-section or inline paragraph at the _semantically correct place_, not the end. If the augment changes the meaning of nearby paragraphs, edit those too — don't leave stale claims standing.

### Step 3 — Wire the activation surface

For any §Teach landing that should be discoverable:

1. **Add trigger keywords to `description:` in the frontmatter** if the new knowledge introduces a vocabulary the existing trigger phrases don't cover. Pick 1-3 phrases an operator would naturally say (e.g. "validate primitive contract", "audit token consumption").
2. **Add a capability menu entry** in §ColdStartTriage ONLY if the new content opens a new mode. Most §Teach landings extend existing modes 1-6; they don't create new ones.
3. **Add a binding-procedure line** in §LoadingProtocol or §Plan-Execute-Verify only if the new section must run in a specific phase. Most don't (default LLM behavior is "scan cold-start menu → match → jump").

If the landing is a new reference file, the SKILL.md edits are minimal — just the §FileMap row + a §ColdStartTriage row if it warrants one.

### Step 4 — Version + CHANGELOG

Cut the new content as a release:

- **PATCH (vN.M.x+1)** — citation strengthening, typo fixes, augmenting an existing section with one paragraph, new anti-pattern entry, new rule in api-contract / css-patterns / lifecycle-patterns.
- **MINOR (vN.M+1.0)** — new reference file, new H2 section in SKILL.md, new cold-start mode with binding, new §SelfAudit axis.
- **MAJOR (vN+1.0.0)** — renames, removals, restructuring (don't bundle with adds).

Update `skill.json` version + `CHANGELOG.md` entry. The entry must name:

- What was added (one-line summary)
- Where it lives (file path + section anchor)
- What triggers it (1-3 phrases from the trigger keywords)
- What it replaces / supersedes (if anything)

### Step 5 — Verify with §SelfAudit

Run the audit:

```bash
node scripts/audit-authoring-roster.mjs --strict
```

Mechanized axes are checked: manifest enforcement (skill.json vs on-disk), reference graph (all intra-skill links resolve), capability-menu drift (every mode points to an existing reference), authoring-roster currency (every absorbed-skill has a redirect or correct absence). The manual-review axes (token economy, content currency, cold-start path weight, fence-leak, CLI helper currency) need eyeballing — see `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md`.

If the audit regresses, **fix in the same cut**. Don't defer hygiene-debt; it compounds.

---

## Worked Examples

### Example A — Per-component yaml fact (NOT a skill landing)

**Request:** "make sure adia-ui-authoring knows that `<rating-ui>` defaults to `count=5` and supports half-star precision via `step=0.5`."

**Decision tree:** Per-component contract (default value + prop semantics). → **YAML SoT, not skill.**

**Action:**

```bash
# Open the yaml
$EDITOR packages/web-components/components/rating/rating.yaml

# Update props section with default + step values + a2ui.rule
# Run regen
npm run build:components
npm run verify:components   # "clean — N files up-to-date"
```

**No skill edits required.** The skill cites `<rating-ui>` by tag in `code-style.md`'s primitive examples; the yaml propagates through the catalog automatically.

**Pitfall to avoid:** "While I'm in the skill, let me add a paragraph about rating-ui in `code-style.md`." NO. That paragraph would duplicate the yaml SoT and drift on the next yaml change. Skill cites the tag; doesn't describe its contract.

### Example B — New authoring rule (four-axis contract extension)

**Request:** "train adia-ui-authoring on the new rule: state-bearing Booleans MUST also reflect to attribute via `reflect: true` so CSS `:scope[disabled]` selectors fire."

**Decision tree:** New authoring rule, axis = API contract (reflection). → **references/api-contract.md**.

**Action:**

1. Open `api-contract.md`. Find the section on `static properties` declarations.
2. Add a new rule entry: rule body + rationale + example showing right vs wrong.
3. If the rule replaces a previous looser claim, edit that claim too — don't leave stale guidance standing.
4. Cross-link from `authoring-cycle.md` Step 3 (the non-negotiable rules list) if it's a hard rule.
5. PATCH bump (`vN.M.x+1`) — augmenting existing reference.

### Example C — New shell pattern

**Request:** "absorb the new `<docs-shell>` decomposition pattern (5th cluster after admin/chat/editor/simple)."

**Decision tree:** New shell pattern. → **references/shell-patterns.md** (mode 3).

**Action:**

1. Open `shell-patterns.md`. Find the "Examples — 4 canonical clusters" section.
2. Add a 5th example block: `<docs-shell>` family (JS-bearing + CSS-only children), CSS bridge file, tests, replication notes.
3. Update the compounding-insight table with a 5th row (build time, notes).
4. If the new cluster surfaces a 16th pitfall, append to the pitfall list (numbered, not bullets).
5. PATCH bump (augmenting existing reference).

### Example D — New module-promotion observation

**Request:** "OD-004 — when the promoted module owns a popover, the consumer's existing popover-trigger button must move INTO the module's [data-trigger] slot, not stay outside; otherwise the popover-trigger binding silently breaks."

**Decision tree:** New module-promotion observation. → **references/module-promotion.md** (mode 4), "Two rules from observed bugs" → "Three rules" (now 4).

**Action:**

1. Open `module-promotion.md`. Find the OD-002 + OD-003 section.
2. Add OD-004 as a new H3 with: pattern (the failure mode), recipe (the fix), example (the real arc that surfaced it).
3. Update the section heading from "Two rules" → "Four rules" (or generalize to "rules from observed bugs").
4. PATCH bump.

**Pitfall to avoid:** Authoring OD-004 in `worked-example.md` instead. The OD-NNN labels belong in `module-promotion.md` where the matrix of observation rules lives.

### Example E — New LLM-bridge rule

**Request:** "make sure adia-ui-authoring knows about Rule 6 — providers with native function-calling must not be wrapped with the json-mode fallback; the bridge auto-detects via `MODELS.<provider>.supportsTools`."

**Decision tree:** New LLM-bridge default. → **references/llm-bridge.md** (mode 6), "Hard rules — defaults that bit us" extends.

**Action:**

1. Open `llm-bridge.md`. Find the "Rule 1 / 2 / 3 / 4 / 5" section.
2. Add Rule 6 in the same H3 form: rule body + rationale + example (provider list affected).
3. If the rule affects the 8-step "How to add a 4th provider" procedure, update step 1 (adapter file) and step 4 (models.js) to reference the new constraint.
4. PATCH bump.

### Example F — New anti-pattern

**Request:** "AP-T07 — using `color: var(--a-fg)` inside a `:scope[variant="accent"]` body bypasses the L3 cascade (should be `--a-accent-fg-hover` etc); we saw this in `tag-ui`."

**Decision tree:** New anti-pattern, axis T (token contract). → **references/anti-patterns.md**.

**Action:**

1. Open `anti-patterns.md`. Find the AP-T section (token contract).
2. Add AP-T07 as a new entry: failure mode + symptom + fix + file:line where the bug was found.
3. Cross-link from `token-contract.md` if the rule maps to a documented audit step.
4. Cross-link from `code-style.md` § "Tokens, never raw colors" if it extends that section.
5. PATCH bump.

**Pitfall to avoid:** Authoring AP-T07 only in `token-contract.md`. The canonical home for anti-patterns is `anti-patterns.md` — that's where the catalogue lives. Other references cite the AP-NN label.

### Example G — Methodology / posture (inline)

**Request:** "we should add a §FirstPrinciples #6: 'Light-DOM positioning is by CSS rule, never by slot' — slot= attributes are decorative metadata per ADR-0033. The retraction lesson generalizes."

**Decision tree:** New first-principle. → **INLINE in SKILL.md §FirstPrinciples**.

**Action:**

1. Open `skills/adia-ui-authoring/SKILL.md` §FirstPrinciples.
2. Add the new principle as #6 with: principle body + rationale + ADR cross-reference + cite-by-tag of the retraction.
3. MINOR bump (new first-principle = new procedural commitment).
4. Run §SelfAudit immediately — confirm the cold-start budget held (the new principle adds maybe 50 lines).

**Why inline, not reference file:** §FirstPrinciples is the procedural spine. Reference-extracting it would mean agents miss it on cold-start. It's allowed to grow.

### Example H — One-off arc story (the NEGATIVE case)

**Request:** "the skill should remember the author-from-scratch bug — a peer landed source under [Unreleased] but no release commit; I had to do a mode-2 cycle 'from scratch'. Make sure adia-ui-authoring knows about it."

**Decision tree:** This is a RELEASE-cycle arc, not an AUTHORING-cycle arc. → **wrong skill entirely — should be the adia-ui-release skill's recovery-paths reference, NOT adia-ui-authoring.**

**Action:**

1. Route to the **adia-ui-release** skill's recovery-paths reference instead.
2. **Do nothing in adia-ui-authoring.** This is anti-pattern 7 (one-way thinking) avoided.

**Counter-example** (a genuine NEGATIVE case for authoring):

**Request:** "the skill should remember how I caught the `<rating-ui>` `reflect: true` missing bug today — grep'd for `reflect: true` in `static properties` arrays, found 3 components missing it, fixed all 3 in one PR."

**Decision tree:** One-off authoring arc story / specific debug session. → **`docs/journal/YYYY/MM/<date>.md`, NOT the skill.**

**Action:**

1. Write the journal entry under §N — the arc.
2. The GENERALIZED rule extracted ("state-bearing Booleans need `reflect: true`") may already be in `api-contract.md` (Example B above). If so, no skill change needed. If not, that's a Branch B landing — separate arc.
3. **Do nothing else in the skill.** The skill teaches the agent what to do; the journal records what happened.

**Pitfall to avoid:** "But the skill should know about every important arc!" NO. Conflating procedural ("what to do") with historical ("what happened") bloats the skill and rots the journal.

---

## Anti-patterns (the §Teach landing failure modes)

These are universal across extensible skills. Each one was observed during sibling-skill §Teach rollouts.

### Anti-pattern 1 — "Append-only" landing

Adding new content to the end of an existing reference without integrating it. Symptom: `anti-patterns.md` grows monotonically; new APs pile under no axis header; cross-references go stale.

**Fix:** When augmenting a reference, find the _semantically correct insertion point_. APs go under their axis section. Lifecycle rules go near related rules in `lifecycle-patterns.md`. Don't pile at file ends.

### Anti-pattern 2 — Duplicating substrate facts

Adding what `packages/web-components/components/<name>/<name>.yaml` already says as prose in the skill. Symptom: the skill paragraph and the yaml `description` say the same thing in different words; the next yaml edit drifts the skill.

**Fix:** When you catch yourself writing "the `<X-ui>` component does Y", check — is this really in the yaml? If yes, cite by tag. Skill cites; doesn't describe.

### Anti-pattern 3 — Trigger keywords without binding

Adding phrases to `description:` for content that doesn't exist yet, or that exists but has no procedural binding. Symptom: agent activates the skill on the keyword, then has no procedure to follow.

**Fix:** Pair the keyword add with the section authoring in the SAME cut. Never bump the version with orphan triggers.

### Anti-pattern 4 — Capability menu lies

Adding a §ColdStartTriage row pointing to a section that doesn't exist or to a stub. Symptom: agent reads the menu, picks the row, jumps to the reference, finds nothing actionable.

**Fix:** §ColdStartTriage entries are the cold-start surface — load-bearing. Treat each new row as a contract that the underlying reference MUST deliver. If you're not ready to write the section, don't add the row yet.

### Anti-pattern 5 — Bundling MINOR + PATCH in one cut

Shipping a new §SelfAudit axis (MINOR) alongside three citation-strengthening edits to `anti-patterns.md` (PATCH) in a single `vN.M+1.0` cut. Symptom: the CHANGELOG entry is unclear; consumers can't tell what the new behavior is.

**Fix:** Cut the MINOR first (with just the new axis). Cut the PATCH after (with the polish). Each cut has a clean intent.

### Anti-pattern 6 — Hygiene-debt deferral

Landing a new section, observing that `audit-authoring-roster.mjs --strict` shows axis regression, and deferring the fix. Symptom: the next cut has a different focus; the hygiene-debt is forgotten; six cuts later the skill has 30+ unresolved references in the manifest.

**Fix:** Fix axis regressions IN THE SAME CUT as the §Teach landing. Hygiene-debt compounds.

### Anti-pattern 7 — Treating §Teach as one-way

Receiving a §Teach request and landing the content without asking "should this be in `adia-ui-authoring`, or in the consumer-side composition skill (composition recipes) / **adia-ui-release** (release-cycle patterns) / **adia-ui-a2ui** (generator internals) / an incident-postmortem skill (incident write-ups)?" Symptom: the authoring skill absorbs content that semantically belongs in a sibling, blowing past the cold-start budget while leaving the sibling thin.

**Fix:** Before landing here, ask: is there a sibling skill for this domain? The consumer-side composition skill (in the adia-ui-factory plugin) owns 3rd-party composition; **adia-ui-release** owns the release cycle; **adia-ui-a2ui** owns generator + corpus internals; an incident-postmortem skill owns incident write-ups; a deployment-ops skill owns long-running VM ops. The authoring skill owns the four-axis contract for code inside the monorepo, not adjacent concerns. Example H above demonstrates the routing decision.

---

## Cross-references

- **§Mission** (`SKILL.md`) — defines the authoring-engineer posture. §Teach is a narrower lane.
- **§SelfAudit** (`SKILL.md`) + **`scripts/audit-authoring-roster.mjs`** — the audit gate that catches §Teach landing regressions. Always run after.
- **§LoadingProtocol** (`SKILL.md`) — defines the reference-file extraction discipline. §Teach respects it by routing content > ~50 LOC to `references/`.
- **§ColdStartTriage** (`SKILL.md`) — the mode cold-start menu. §Teach lands in mode 7.
- `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md` + `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md` — the shared infrastructure motivating §Teach and PEV across the forge family.
- the **adia-ui-release** skill's `teach-protocol.md` — a sibling instantiation. Universal sections vendored here.
- the repo's AGENTS.md — defines journal + audit-history disciplines that §Teach defers to for arc stories.

---

## Worked Decision Examples — Quick-Reference Card

When in doubt, the table below routes by request shape.

| Request shape | Landing target | Version bump | Audit gate |
| --- | --- | --- | --- |
| "new primitive contract / yaml fact" | yaml SoT only (no skill change) | yaml change only | `npm run verify:components` |
| "new prop reflection / attribute mapping rule" | references/api-contract.md | PATCH | `audit-authoring-roster.mjs` |
| "new @scope / variant-vs-mode / L3 token rule" | references/css-patterns.md or token-contract.md | PATCH | `audit-authoring-roster.mjs` |
| "new lifecycle rule (observer / listener / cleanup)" | references/lifecycle-patterns.md | PATCH | `audit-authoring-roster.mjs` |
| "new shell pattern / 5th cluster / state-as-attr" | references/shell-patterns.md | PATCH | `audit-authoring-roster.mjs` |
| "new OD-NNN module-promotion rule" | references/module-promotion.md | PATCH | `audit-authoring-roster.mjs` |
| "new LLM-bridge default / Rule N+1" | references/llm-bridge.md | PATCH | `audit-authoring-roster.mjs` |
| "new anti-pattern (AP-N## / AP-T## / AP-S## / AP-L##)" | references/anti-patterns.md | PATCH | `audit-authoring-roster.mjs` |
| "new worked example (badge-ui / counter-ui shape)" | references/worked-example.md | PATCH | `audit-authoring-roster.mjs` |
| "new general convention / code style" | references/code-style.md | PATCH | `audit-authoring-roster.mjs` |
| "new first-principle / cold-start mode / §SelfAudit axis" | inline in SKILL.md | MINOR | `audit-authoring-roster.mjs` after |
| "one-off authoring arc / debug session" | `docs/journal/YYYY/MM/<date>.md` (NOT skill) | n/a | journal-date hook |
| "release-cycle pattern" | route to adia-ui-release (NOT this skill) | varies | peer review |
| "3rd-party composition recipe" | route to the adia-ui-factory plugin (NOT this skill) | varies | peer review |
| "A2UI corpus / generator internals" | route to adia-ui-a2ui (NOT this skill) | varies | peer review |

---

When new landing-target patterns emerge that don't fit the 8 branches above, augment this file's decision tree + worked examples in the same arc as the landing.
