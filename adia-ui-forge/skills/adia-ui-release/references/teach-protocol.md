# Reference: Teach Protocol — Absorbing new knowledge into the adia-ui-release skill

**Ecosystem context:** §Teach is this skill's instantiation of the rollup-family **extensibility** posture. The shared skill-ecosystem conventions live at `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md` (§11 mechanizes the §Teach decision tree); the verify-the-output rationale at `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md`. The posture separates **universal components** (the trigger cluster, the 7 anti-patterns, the 5-step landing procedure, the citation-vs-knowledge principle, the negative case) from **skill-specific components** (the decision tree's branches, the worked examples). When editing this file, preserve the universal sections; replace only the skill-specific decision-tree branches + worked examples.

**Why authored:** As the release skill absorbs new release-engineering patterns (the release trip-wire, diff-coverage enrichment, batch-push npm-latest ordering, embeddings-fresh recovery, version-skip correction, deploy recipes), each absorption was previously a one-off improvisation. This protocol gives every future "make sure `adia-ui-release` knows about [pattern]" request a deterministic landing path.

**Used by:** the `adia-ui-release` skill, when an agent receives one of the trigger phrases below. SKILL.md §Teach is the seed; this file is the binding procedure.

- "make sure `adia-ui-release` knows about [the new gate / recovery path / pattern]"
- "train `adia-ui-release` on [the new ledger field / the new deploy step]"
- "the skill should know about [the F-N1 enrichment]"
- "absorb this release-pattern into adia-ui-release"
- "teach the skill about [the new post-deploy verify]"
- "[recovery-paths case study]: make sure the skill reflects it"

**Companion:** the `§SelfAudit` section + `scripts/audit-gate-roster.mjs` (run after any §Teach landing to verify Axis 9 gate-roster currency holds), and `cycle-happy-path.md` (the 12-step happy path — §Teach landings near it should preserve its structure).

**Anti-companion:** `docs/journal/YYYY/MM/<date>.md` and `.brain/audit-history/YYYY-MM-DD-release-cut-vX.Y.Z.json` (one-off cycle retros + per-cycle ledgers belong there, NOT in the skill — see Branch H below).

---

## When to Use

Trigger phrases (mirrored from the SKILL.md §Teach section):

- "make sure `adia-ui-release` knows about X"
- "train the skill on X"
- "teach the skill about Y"
- "the skill should be aware of Z"
- "absorb [pattern / recovery / gate] into adia-ui-release"
- "update the skill to reflect [the new ADR / the resolved failure mode / the new gate]"

This protocol applies when **another agent** (release operator, peer skill author, dev-ops author) hands the release skill new knowledge to integrate. It does NOT apply when:

- You're cutting a release right now (use mode 1 / `cycle-happy-path.md` instead)
- You're authoring a CHANGELOG entry or release notes (use mode 9 / `notes-authoring.md` instead)
- You're fixing a wrong claim in the skill (the universal "correction" posture)
- You're running cleanup / archive sweeps (use §SelfAudit's hygiene-cut shape)

The procedure below is the binding for skill-teach requests against `adia-ui-release`. Follow it in order. Each step has a stop-condition; do not skip ahead.

---

## Core Principles

1. **The skill is a citation layer, not a knowledge layer.** Release-cycle invariants live in `scripts/release/*` + `package.json` `scripts:` entries + workflows under `.github/workflows/`. The skill cites by gate name, mode, and recovery-path keyword — it does NOT duplicate what the scripts encode. When a §Teach landing's first instinct is "rewrite what `scripts/release/check-lockstep.mjs` says," stop: the substrate is the source of truth.
2. **Reference files are the cold-start budget's safety valve.** New content > ~50 LOC of procedural detail belongs in `references/<topic>.md` and is cited from SKILL.md, not inlined. This keeps the bare-activation surface small (the cold-start menu) and lets modes load only their declared bundles.
3. **Triggers without binding sections are waste.** Adding keywords to `trigger:` without a corresponding section in SKILL.md (or referenced file) consumes activation budget for no payoff. Always pair the two.
4. **Capability menu items must reach an actual mode.** The cold-start `## What this skill can do` table is the agent's mental model on bare activation. Lies in that table cost more than gaps.
5. **Version bumps are PATCH for citations, MINOR for new sections, MAJOR for renames/removals.** Most §Teach landings here are PATCH (a new gate row in `gates-catalog.md`) or MINOR (a new recovery scenario in `recovery-paths.md`). Never bundle MINOR with PATCH polish in one cut.
6. **§SelfAudit is the receipt.** A §Teach landing isn't done until `node "${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/scripts/audit-gate-roster.mjs" --strict` runs clean. If the audit regresses, fix in the same cut.

---

## The Decision Tree — where does new release knowledge land?

Run this **before** any patch. The wrong landing target wastes effort and creates drift.

```text
Is the new fact a SUBSTRATE behavior — a script the skill cites
(e.g. `scripts/release/check-release.mjs`, `scripts/release/check-lockstep.mjs`),
a CI workflow, a package.json script entry?
  → YES: belongs in the SUBSTRATE, not the skill.
         Edit the script / workflow / package.json directly.
         If the change affects what the skill cites, follow up by
         updating the citation paragraph in the appropriate reference
         (usually `gates-catalog.md` Branch B below).
         STOP HERE for the substrate edit.
         (See Worked Example A below.)
  → NO: continue.

Is it a NEW GATE — a `check:*` / `verify:*` / `smoke:*` / `test:*`
script added to `package.json` that the release cycle should run?
  → YES: lands in `gates-catalog.md`. Choose category by
         the gate's role:
           - Category 1-3 — pre-cut quality gates (verify, smoke, test)
           - Category 4-6 — release-time invariants (lockstep, F-N1)
           - Category 7-8 — eval / corpus / embedding floors
           - Category 9 — release-side audit-roster currency itself
         If the new gate doesn't fit, author a new category section.
         Update Axis 9 (gate-roster currency) — the audit script will
         detect the new gate; document it explicitly.
         (See Worked Example B below.)

Is it a NEW RECOVERY PATH — a failure mode in the release cycle
that wasn't previously documented?
  → YES: lands in `recovery-paths.md`. Identify the
         scenario (batch-push npm-latest reversal, version-skip
         correction, stale-test detection, embeddings-fresh recovery,
         F-N1 enrichment pass, corpus drift remediation). Add the
         scenario as a new H2; cross-link from the §Recon table in
         SKILL.md if it's a common-enough symptom that mode-1 needs
         to recognize it.
         (See Worked Example C below.)

Is it a NEW NOTES TEMPLATE VARIANT — a Slack post shape, GH release
body section, or rollup-notes structure?
  → YES: single-version lands in `notes-authoring.md`;
         multi-version retrospectives in `rollup-notes.md`.
         These files are the SoT for what release notes look like;
         update them rather than inlining example notes elsewhere.
         (See Worked Example D below.)

Is it a NEW LEDGER FIELD or audit-history JSON-shape extension?
  → YES: lands in `ledger-discipline.md`. The ledger schema
         is the cross-cycle archaeology layer; new fields should be
         documented before they appear in actual ledgers. Update the
         template at `assets/templates/audit-history.template.json`
         alongside the schema description.
         (See Worked Example E below.)

Is it a NEW EXE DEPLOY RECIPE — a step in the site-build → rsync →
verify chain, or a new probe?
  → YES: lands in `exe-deploy.md`. The deploy recipe is
         a discrete script chain (`npm run build:site` → `rsync` →
         `curl -s -o /dev/null -w`); new steps insert into the chain
         in the documented order. If the recipe gains a new failure
         mode, also add a recovery-paths entry.
         (See Worked Example F below.)

Is it a MULTI-AGENT or PEER-IN-FLIGHT observation — a new pattern
for stash discipline, staging-area defensiveness, or peer-coordination?
  → YES: lands in `multi-agent-baseline.md`. This file
         is the canonical home for the multi-agent baseline assumption
         from AGENTS.md; new patterns build on top.
         (See Worked Example G below.)

Is it a NEW MIGRATION-GUIDE pattern — a breaking-change recipe shape, a
new manual-review class, a version-coverage-table convention, or an
in-repo-sweep verification step (the PRODUCER side of migrations)?
  → YES: lands in `migration-guide-authoring.md`. This is the
         producer counterpart to the consumer/app-author plugin's
         consumer-sweep side. Add the recipe shape or manual-review class
         there; cross-link from §Step 4b (PATCH-vs-MINOR) if it changes
         when a guide section is owed. Do NOT add consumer-sweep recipes
         here — those belong in the separate consumer plugin.
         (Producer side only — the consumer sweep is out of scope.)

Is it a METHODOLOGY / POSTURE shift — a new mode, a new §SelfAudit
axis, a new operator-confirmation checkpoint?
  → YES: lands INLINE in SKILL.md (the procedural spine). These
         shape every mode and belong in the cold-start surface:
         §Mission, §Posture, §ReleaseInvariants, §LoadingProtocol,
         §SelfAudit, §FileMap. They're allowed to grow because they
         shape every other section. Run §SelfAudit immediately to
         confirm the cold-start budget held.
         (See Worked Example H below.)

Is it a one-off RELEASE RETRO, ARC STORY, or HISTORICAL CONTEXT for
a specific cycle (vN.M.X-shaped)?
  → NO landing in the skill. It belongs in:
    - `.brain/audit-history/YYYY-MM-DD-release-cut-vN.M.X.json`
      (per-cycle ledger — already captured by mode 1 step 11)
    - `docs/journal/YYYY/MM/<date>.md` (architectural milestones,
      cross-cycle lessons)
    - `assets/case-studies/<date>-<topic>-vN.M.X.md` (when the cycle
      surfaced a generalizable pattern — but lift the pattern into
      one of the branches above; the case study is the citation,
      not the recipe)
    Skipping the skill is a FEATURE, not a gap.
    (See Worked Example I — the negative case.)
```

---

## The Five-Step Landing Procedure

After the decision tree picks a target, follow these steps in order:

### Step 1 — Audit before patching

Before writing anything:

1. **Read the target file in full.** Don't skim. The release-skill reference files have established voice + section ordering; patches must match.
2. **`git status` + `git log -5`** on the working tree. Confirm no peer activity in this skill’s directory (`${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/`) (peer agents may be authoring sibling skills like `adia-ui-authoring`). If peer is dirty here, halt + coordinate.
3. **Grep for existing coverage.** Run `grep -rn "<keyword>" "${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/"` to confirm the new knowledge isn't already partly covered. If it IS, the landing is a _patch + augment_, not a _new section_.
4. **Confirm the landing-target choice.** Re-read the Decision Tree above against your specific case. Two minutes of "is this really a gate, or is it actually a recovery path?" prevents two hours of misplaced content.

### Step 2 — Author the patch

Two shapes depending on Step 1's grep:

#### Shape A — NEW section / file (no existing coverage)

If the target is a new reference file: create `references/<topic>.md` with the canonical header (provenance, why-authored, used-by, companion, anti-companion), then "## When to Use", "## Core Principles", then content. Reference from SKILL.md `§LoadingProtocol` reference-manifest area with a one-line "when to load" tag.

If the target is a new H2 inside an existing reference (most common for release-skill §Teach): find the semantically correct insertion point (e.g. a new gate row goes in its Category section in `gates-catalog.md`, not at the file's end). Use the established voice — short paragraph framing, table-form details, code blocks for commands.

#### Shape B — AUGMENT existing section (grep found partial coverage)

Read the entire existing section first, including any cross-references to other files. Author the augment as a sub-section or inline paragraph at the _semantically correct place_, not the end. If the augment changes the meaning of nearby paragraphs, edit those too — don't leave stale claims standing.

### Step 3 — Wire the activation surface

For any §Teach landing that should be discoverable:

1. **Add trigger keywords to `trigger:` in the frontmatter** if the new knowledge introduces a vocabulary the cycle's trigger phrases don't cover yet. Pick 1-3 phrases an operator would naturally say (e.g. "embeddings drift", "F-N1 enrichment").
2. **Add a capability menu entry** in `## What this skill can do — pick your mode` ONLY if the new content opens a new mode. Most §Teach landings extend existing modes; they don't create new ones.
3. **Update the §Where are you starting from table** if the new content adds a starting state (e.g. "Embeddings drift caught at pre-flight" → mode 6 / gates-catalog).

If the landing is a new reference file, the SKILL.md edits are minimal — just the manifest line + a triage-table row if it warrants one.

### Step 4 — Version + CHANGELOG

Cut the new content as a release:

- **PATCH (vN.M.x+1)** — citation strengthening, typo fixes, augmenting an existing section with one paragraph, new gate-row in `gates-catalog.md`, new recovery-path scenario.
- **MINOR (vN.M+1.0)** — new reference file, new H2 section in SKILL.md, new capability-menu mode with binding, new §SelfAudit axis.
- **MAJOR (vN+1.0.0)** — renames, removals, restructuring (don't bundle with adds).

Update `skill.json` version + `CHANGELOG.md` entry. The entry must name:

- What was added (one-line summary)
- Where it lives (file path + section anchor)
- What triggers it (1-3 phrases from the trigger keywords or recovery-path keyword)
- What it replaces / supersedes (if anything)

### Step 5 — Verify with §SelfAudit

Run the audit:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/scripts/audit-gate-roster.mjs" --strict
```

Axis 9 (gate-roster currency) is the mechanized check. If a new gate was added in §Teach Branch B but not documented in `gates-catalog.md`, this script catches it. Other axes (the extensibility binding points in `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md`) are manual-review for now.

If the audit regresses, **fix in the same cut**. Don't defer hygiene-debt; it compounds.

---

## Worked Examples

### Example A — Substrate edit (NOT a skill landing)

**Request:** "make sure adia-ui-release knows the new `check:typecheck:strict` script we just added to package.json."

**Decision tree:** It's a substrate behavior — a new script entry. → **substrate edit, NOT skill change.**

**Action:**

```bash
# The package.json edit is the substrate change. Skill cites by gate
# name in gates-catalog.md; the audit will catch the new entry as
# undocumented and surface it as Axis 9 drift.

# Run the audit to surface the gap:
node "${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/scripts/audit-gate-roster.mjs"

# It will report "check:typecheck:strict" as a documented variant of
# the base `check:typecheck` (if that base exists in gates-catalog.md)
# OR as undocumented (if no `:strict` base). Add a one-line entry to
# gates-catalog.md Category 1 or 2 as appropriate — this IS a skill
# edit (Branch B below), but it's downstream of the substrate edit.
```

**Pitfall to avoid:** "While I'm here, let me inline the script's full purpose in SKILL.md." NO. The script's own `--help` flag + the docstring at the top of the `.mjs` file are the SoT. The skill cites; it doesn't duplicate.

### Example B — New gate row

**Request:** "we just added `check:rendered-completeness` — train the skill on it."

**Decision tree:** New gate. → **`gates-catalog.md`**, appropriate category.

**Action:**

1. Read `gates-catalog.md`. Identify the right category (verify-time? smoke-time? Categorized by what fails — content quality? wiring? deployment?).
2. Add a section:

   ```markdown
   #### `npm run check:rendered-completeness`

   - **What it catches:** ...
   - **Failure shape:** ...
   - **Recovery:** ...
   ```

3. PATCH bump (`scripts/audit-gate-roster.mjs` will detect the new gate is documented; Axis 9 stays clean).
4. Run `audit-gate-roster.mjs --strict` — expect 0 drift.

**Real-session reference:** v1.0.1 (2026-05-22) — `audit-gate-roster.mjs` first surfaced 48 undocumented gates; the Category 10 curation pass (variant-aware logic) documented the long tail.

### Example C — New recovery path scenario

**Request:** "make sure the skill knows the v0.6.18 author-from-scratch failure (peer staged source under [Unreleased] but no release commit; we authored it ourselves)."

**Decision tree:** New recovery scenario. → **`recovery-paths.md`**.

**Action:**

1. Open `recovery-paths.md`. Add a new H2 "Scenario N — Author from scratch (peer staged work but no release commit)".
2. Document the diagnosis ("HEAD doesn't show release commit; `[Unreleased]` block has content; no peer prep note"), the fix (mode 2 path), and a cross-reference to the case study (`assets/case-studies/2026-05-21-author-from-scratch-v0.6.18.md`).
3. MINOR bump (new scenario).
4. Cross-link from SKILL.md §Recon table if the symptom is common.

**Real-session reference:** v0.3.0 (2026-05-21) — recovery-paths.md gained the author-from-scratch + version-skip + corpus-drift scenarios as part of the Phase 3 ship.

### Example D — New notes template variant

**Request:** "the rollup-notes shape we used for v0.6.8 → v0.6.16 is the canonical multi-version retrospective — capture it as a template."

**Decision tree:** New notes template variant (multi-version). → **`rollup-notes.md`**.

**Action:**

1. Open `rollup-notes.md`. Add a new H2 documenting the rollup-notes shape: header (arc title + version range + cycle-count), per-version digest table, the-arcs section, headline-event section, net-deltas section, install snippet.
2. Add a worked example (the v0.6.8 → v0.6.16 notes are the prototype).
3. PATCH bump (augmenting existing reference file).
4. Cross-link from §Where are you starting from table if it warrants a triage row ("Want rollup notes across many versions → mode 5").

### Example E — New ledger field

**Request:** "add a `peer_interleave` array to the audit-history JSON when peer commits land mid-cycle."

**Decision tree:** New ledger schema field. → **`ledger-discipline.md`**.

**Action:**

1. Open `ledger-discipline.md`. Add the field to the canonical schema documentation: name, type, when-populated, example value.
2. Update `assets/templates/audit-history.template.json` to include the field with a placeholder.
3. Update `scripts/make-ledger.mjs` to accept the new field via flag if it's mechanically populatable; or document the manual-fill instruction otherwise.
4. PATCH bump if augmenting; MINOR if introducing a new schema version (`schema_version` bump).

**Real-session reference:** v1.0.0 (2026-05-22) — the v0.6.22 ledger captured a peer-amend interleave; future ledgers might benefit from a structured field for that.

### Example F — New EXE deploy recipe step

**Request:** "we added a CDN cache-bust step after rsync — train the skill."

**Decision tree:** New deploy recipe step. → **`exe-deploy.md`**.

**Action:**

1. Open `exe-deploy.md`. Find the recipe section (the `npm run build:site` → `rsync` → `curl` chain).
2. Insert the cache-bust step in the documented order (between `rsync` and `curl -s -o`).
3. Document failure modes (cache-bust API timeout, auth failure).
4. PATCH bump.
5. If the new step has a failure mode that requires recovery, also add a `recovery-paths.md` scenario (Branch C — two landings).

### Example G — Multi-agent / peer-in-flight observation

**Request:** "v0.6.22's mid-cycle peer-amend interaction is a new pattern — when peer commits between `git add` and `git commit`, the staging area absorbs the peer's commit and `--amend` modifies the wrong thing. Make sure the skill knows."

**Decision tree:** Multi-agent baseline observation. → **`multi-agent-baseline.md`**.

**Action:**

1. Open `multi-agent-baseline.md`. Add a new H2 "## §Mid-cycle peer-amend interaction" under the existing peer-coordination sections.
2. Document the failure mode (peer commit between stage + commit), the diagnostic (`git reflog` shows the unexpected commit), the recovery (`git reset HEAD~1` if commit content is fully recoverable; otherwise cherry-pick + re-amend).
3. Cross-link from `cycle-happy-path.md` § Step 5 (Stage and commit) since that's where the interaction manifests.
4. PATCH bump.

**Real-session reference:** v0.6.22 cycle ledger captured this as a note; the pattern graduates from cycle-specific note to canonical guidance via this §Teach landing.

### Example H — Methodology / posture shift (inline)

**Request:** "we should add a 10th §SelfAudit axis — citation-graph integrity (every reference cited in SKILL.md must exist)."

**Decision tree:** Methodology / posture shift (new audit axis). → **INLINE in SKILL.md §SelfAudit**.

**Action:**

1. Open this skill’s `SKILL.md` §SelfAudit (if it exists yet) or §ReleaseInvariants.
2. Add the new axis with: name, what it measures, soft threshold, remediation shape.
3. If the new axis can be mechanized, extend `scripts/audit-gate-roster.mjs` (or author a new audit script).
4. MINOR bump for the new axis (it's a new procedural commitment, not a citation).
5. Run the §SelfAudit immediately — confirm the new axis reports clean against the current state. If it doesn't, fix in the same cut.

**Why inline, not reference file:** §SelfAudit's axes shape every other section. They're the procedural spine; they're allowed to grow. Reference-extracting them would mean agents miss them on cold-start.

### Example I — One-off arc story (the NEGATIVE case)

**Request:** "the skill should remember the v0.6.22 amend interaction — peer's §Teach commit landed on top of the release commit, I amended their commit by mistake, tags ended up on the wrong SHA but it worked out OK."

**Decision tree:** One-off arc story / specific cycle context. → **`.brain/audit-history/2026-05-22-release-cut-v0.6.22.json` + `docs/journal/`, NOT the skill.**

**Action:**

1. The audit-history ledger already captures this (`notes:` field).
2. If the pattern generalizes (peer-amend interaction as a recurring failure mode), lift the generalized version into `multi-agent-baseline.md` via Branch G (Example G above). The CYCLE-SPECIFIC story stays in the ledger; the PATTERN graduates to the skill.
3. **Do nothing else in the skill.** The skill is procedural ("what to do"); the ledger records "what happened in v0.6.22 specifically".

**Pitfall to avoid:** "But the skill should know about every important arc!" NO. The skill teaches the agent **what to do**; the ledger + journal record **what happened**. Conflating them bloats the skill and rots the ledger.

---

## Anti-patterns (the §Teach landing failure modes)

These are universal across extensible skills (per the rollup-family conventions in `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md`). Each one was observed across §Teach rollouts in adjacent release-skill arcs.

### Anti-pattern 1 — "Append-only" landing

Adding new content to the end of an existing reference without integrating it. Symptom: `gates-catalog.md` grows monotonically; new gates pile in Category 10 (stubs) instead of finding the right category.

**Fix:** When augmenting a reference, find the _semantically correct insertion point_, not the end. If the new content doesn't fit any insertion point, you may be in the wrong section.

### Anti-pattern 2 — Duplicating substrate facts

Adding what `scripts/release/check-lockstep.mjs` does as prose in the skill. Symptom: the skill paragraph and the script's `--help` say the same thing in different words; the next time the script changes, drift starts.

**Fix:** When you catch yourself writing "the gate does Y", check — is this really in the script's own `--help` or the docstring at top? If yes, cite by gate name. The skill cites; doesn't describe.

### Anti-pattern 3 — Trigger keywords without binding

Adding phrases to `trigger:` for content that doesn't exist yet, or that exists but has no procedural binding. Symptom: agent activates the skill on the keyword, then has no procedure to follow.

**Fix:** Pair the keyword add with the section authoring in the SAME cut. Never bump the version with orphan triggers.

### Anti-pattern 4 — Capability menu lies

Adding a mode-table row pointing to a section that doesn't exist, or to a stub. Symptom: agent reads the menu, picks the mode, jumps to the section, finds nothing actionable, falls back to general knowledge.

**Fix:** Capability-menu entries are the cold-start surface — load-bearing. Treat each new entry as a contract that the underlying section MUST deliver. If you're not ready to write the section, don't add the menu item yet.

### Anti-pattern 5 — Bundling MINOR + PATCH in one cut

Shipping a new recovery scenario (MINOR) alongside three citation-strengthening edits (PATCH) in a single `vN.M+1.0` cut. Symptom: the CHANGELOG entry is unclear; consumers can't tell what the new behavior is.

**Fix:** Cut the MINOR first (with just the new section). Cut the PATCH after (with the polish). Each cut has a clean intent.

### Anti-pattern 6 — Hygiene-debt deferral

Landing a new section, observing that `audit-gate-roster.mjs --strict` shows a threshold regression, and deferring the fix to "next cut." Symptom: the next cut has a different focus; the hygiene-debt is forgotten; six cuts later the skill's Axis 9 reports 30+ undocumented gates.

**Fix:** Fix axis regressions IN THE SAME CUT as the §Teach landing. Hygiene-debt compounds.

### Anti-pattern 7 — Treating §Teach as one-way

Receiving a §Teach request and landing the content without asking "should this be in `adia-ui-release`, or in `adia-ui-authoring` / a long-running-ops skill / `ops-postmortem` / a different sibling?" Symptom: the release skill absorbs content that semantically belongs in a sibling (e.g. `ops-postmortem` for incident write-ups, `adia-ui-authoring` for authoring-side hygiene).

**Fix:** Before landing here, ask: is there a sibling skill for this domain? Sibling `adia-ui-authoring` owns authoring; the consumer/app-author plugin owns 3rd-party consumption + the **consumer side** of migration; `ops-postmortem` owns incident write-ups; long-running VM ops is a separate concern (not in this plugin). The release skill owns the cycle (and, via §MigrationGuideAuthoring, the **producer side** of migration guides), not adjacent concerns.

---

## Cross-references

- **§Mission** (`SKILL.md`) — defines the autonomous-release-engineer posture. §Teach is a narrower lane.
- **§SelfAudit** (when it lands; tracked by `audit-gate-roster.mjs` Axis 9 today) — the audit gate that catches §Teach landing regressions. Always run after.
- **§LoadingProtocol** (`SKILL.md`) — defines the reference-file extraction discipline. §Teach respects it by routing content > ~50 LOC to `references/`.
- **`scripts/audit-gate-roster.mjs`** — Axis 9 enforcement. Run after every §Teach landing.
- **`${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md`** — the rollup-family skill conventions (§11 mechanizes the §Teach decision tree; §7 the §SelfAudit axes).
- **`${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md`** — the verify-the-output rationale every §Teach landing inherits via §PEV.
- **AGENTS.md** (the target monorepo's root) — defines journal + audit-history disciplines that §Teach defers to for cycle-specific stories.

---

## Worked Decision Examples — Quick-Reference Card

When in doubt, the table below routes by request shape.

| Request shape | Landing target | Version bump | Audit gate |
| --- | --- | --- | --- |
| "new check:_/ verify:_ / smoke:\* gate" | substrate + `gates-catalog.md` | PATCH | `audit-gate-roster.mjs` |
| "new failure mode / recovery path" | `recovery-paths.md` | MINOR if new H2; PATCH if augmenting | manual review |
| "new Slack post / GH release shape" | `notes-authoring.md` | PATCH | manual review |
| "multi-version rollup notes shape" | `rollup-notes.md` | PATCH | manual review |
| "new ledger field / schema bump" | `ledger-discipline.md` + `assets/templates/audit-history.template.json` | PATCH or MINOR | manual review |
| "new EXE deploy step / probe" | `exe-deploy.md` | PATCH | manual review |
| "new peer-coordination pattern" | `multi-agent-baseline.md` | PATCH | manual review |
| "new migration-guide recipe / manual-review class (producer side)" | `migration-guide-authoring.md` | PATCH if augmenting; MINOR if new H2 | manual review |
| "new methodology / §SelfAudit axis" | inline in `SKILL.md` (near §ReleaseInvariants / §SelfAudit) | MINOR | `audit-gate-roster.mjs` after |
| "new CLI helper script" | `scripts/<name>.mjs` + cross-link from §FileMap | MINOR | `audit-gate-roster.mjs` |
| "cycle retro / arc story / vN.M.X-specific lesson" | `.brain/audit-history/` + `docs/journal/` (NOT skill) | n/a | journal-date hook |
| "absorb sibling-skill knowledge" | route to peer skill OR defend inclusion | varies | peer review |

---

**Maintenance:** when new landing-target patterns emerge that don't fit the branches above, augment this file's decision tree + worked examples in the same arc as the landing.
