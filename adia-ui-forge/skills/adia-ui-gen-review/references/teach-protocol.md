---
name: teach-protocol
description: >
  §Teach invocation protocol for adia-ui-gen-review. 8-branch decision tree
  routing new evidence to the correct file. Invoked via Mode 5 of
  ColdStartTriage when the operator says "make sure gen-review knows about X"
  or "train gen-review on Y".
---

# §Teach Protocol — adia-ui-gen-review

**Invoked from**: SKILL.md §ColdStartTriage Mode 5 **Trigger phrases**: "make sure gen-review knows about X", "train gen-review on Y", "absorb this into gen-review", "update gen-review with the new primitive"

This is a standalone skill. §Teach here covers the 8 evidence types that arise from running review cycles, not a full extensibility harness.

---

## §WhenToInvoke

Invoke when evidence arrives from:

- A new AdiaUI primitive shipped to the monorepo's `packages/web-components/components/`
- A cycle reveals a new failure pattern not covered by the 9 existing cause codes
- Human QA consistently disagrees with mechanical scores (threshold drift)
- A native HTML element appears in canvas output that isn't yet tracked
- A new DOM attribute needs to pass the allowlist to the decomposed file
- A new cosmetic anti-pattern keeps appearing that the rubric doesn't name
- The loop protocol needs a new phase or conditional guard
- A cycle output field needs to be formally tracked in scores.schema.json

Do NOT invoke §Teach for:

- Fixing a bug in the loop protocol execution — that's an edit task, not a teach
- Re-running coverage audit after adding entries — that's verify, not teach
- Any change to the canvas or Gen UI pipeline itself — route to `adia-ui-a2ui`

---

## §DecisionTree

### Branch 1 — New AdiaUI primitive shipped

Evidence: a new `-ui` tag appears in the monorepo's `packages/web-components/components/` that is missing from `TAG_TO_COMPONENT` in `gen-review-decompose.mjs`.

Detection (run from the monorepo root):

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-coverage-audit.mjs
```

Action:

1. Find the component's display name in its `.yaml` `name:` field.
2. Add to `TAG_TO_COMPONENT` in `gen-review-decompose.mjs`:

   ```js
   'new-primitive-ui': 'NewPrimitive',
   ```

3. If it's a slotted container (card-like, drawer-like), also update `rubric-decompose.md` slot-vocabulary section.

Verify: `node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-coverage-audit.mjs --strict` exits 0.

---

### Branch 2 — New native element appearing in canvas

Evidence: a cycle decomposition shows a native HTML element (e.g. `<details>`, `<dl>`, `<blockquote>`) in canvas output that should be tracked as a quality signal.

Action:

1. Add to `TAG_TO_COMPONENT` in `gen-review-decompose.mjs`:

   ```js
   'details': 'NativeDetails',
   ```

   Use the `Native` prefix to distinguish from AdiaUI primitives.

2. Add a note to `rubric-decompose.md` in the native-element quality-signal section explaining what this element's presence indicates.

Verify: re-run decompose on a prompt that uses the element; confirm it appears in `decomposed.components[]` with the `Native*` name.

---

### Branch 3 — New allowlisted attribute

Evidence: a cycle reveals that a semantically useful attribute is being stripped from the decomposed file by the allowlist (e.g., a new `columns=` equivalent attr added to a grid primitive).

Action:

1. Add the attribute name to `ATTR_ALLOWLIST` in `gen-review-decompose.mjs`:

   ```js
   const ATTR_ALLOWLIST = new Set([
     ..., 'new-attr',
   ]);
   ```

2. Confirm the attribute carries no user-controlled content that could be adversarial (strings typed by a user into the canvas). Static enum values (variant, size, gap) are safe; freeform text should stay blocked.

Verify: re-run decompose on the affected prompt; confirm the attribute appears in `decomposed.attrs{}`.

---

### Branch 4 — New root-cause code

Evidence: a recurring failure pattern across 2+ cycles that doesn't fit any of the 9 existing codes (WRONG_CHUNK, EMPTY_CHUNK, WRONG_COMPONENT, MISSING_PROPS, WRONG_NESTING, TRANSPILER_GAP, RETRIEVAL_SCORE, FREE_FORM_HALLUC, COSMETIC_ONLY).

Action:

1. Add a new row to `rubric-score.md` §Root-Cause Classification.
2. Add the new code to the `rootCauses[].code` enum in `scores.schema.json`.
3. Bump `schemaVersion` in `scores.schema.json` (patch bump: `"2.0.1"` → `"2.0.2"`).
4. Update CHANGELOG.md.

Verify: the schema file parses as JSON; confirm the new code appears in the enum array.

---

### Branch 5 — Threshold recalibration

Evidence: human QA gate results consistently contradict the mechanical score (e.g., QA passes 4/5 prompts but rubric-score marks them Failing), sustained across 2+ cycles.

Action:

1. Edit `rubric-score.md` §Thresholds — adjust the Excellence/Acceptable/Failing boundary numbers.
2. Update the `scores.schema.json` thresholds comment (if any) to match.
3. Update SKILL.md §ExitCondition if the Excellence number changes (it is the exit gate).
4. Note the calibration in CHANGELOG.md with the cycle numbers that motivated it.

Verify: re-score the 5 QA prompts from that cycle against the new thresholds; confirm they now agree with human QA judgement.

---

### Branch 6 — New rubric dimension

Evidence: a structural quality axis that cycles consistently expose but that D1–D6 don't capture (e.g., a new "Responsive breakpoint fidelity" dimension).

Action:

1. Add a `D7+` section to `rubric-score.md` §Dimensions.
2. Update the max-score note (e.g., D7 at 0–15 = max 120).
3. Update `rubric-score.md` §Thresholds to reflect the new max.
4. Add `d7` (or whatever the dimension key is) to the `rubricScore` object in `scores.schema.json`.
5. Bump `schemaVersion` (minor bump: `"2.0.1"` → `"2.1.0"` for schema shape change).
6. Update SKILL.md §ExitCondition if the Excellence threshold number changes.
7. Update CHANGELOG.md.

Verify: the schema parses; loop-protocol.md §Phase 3 names the new dimension; rubric-decompose.md is updated if Phase 2 must produce new data the dimension consumes.

---

### Branch 7 — New cosmetic pattern

Evidence: a visual anti-pattern that recurs across prompts and isn't covered by COS-1 through COS-6 in `rubric-cosmetic.md`.

Action:

1. If the pattern fits within an existing COS-N's scope, add it as a sub-item.
2. If it's a distinct axis, add `COS-7+` as a new section.
3. Assign severity (P1/P2/P3) using the existing rubric criteria:
   - P1: blocks task completion or signals wrong primitive
   - P2: visually broken but navigable
   - P3: polish only

Verify: run Phase 4 on a prompt that exhibits the pattern; confirm the scoring rubric now names it and assigns the right severity.

---

### Branch 8 — New phase or phase-conditional logic

Evidence: the loop protocol needs a new phase (e.g., a "Phase 0 — prerequisite check" step), or an existing phase needs a new conditional guard.

Action:

1. Edit `loop-protocol.md` — add or update the affected §Phase section.
2. If the change adds new artifacts to the cycle output, update §DataModel in SKILL.md and the `files:` structure listed there.
3. If Phase 5 routing changes (new peer skill invoked), update §SkillDelegation in SKILL.md.
4. Update SKILL.md §SelfAudit if the check list needs updating.
5. Update CHANGELOG.md.

Verify: trace through the full loop-protocol.md from §Setup through §Cycle Close to confirm the new logic is coherent with all phase transitions.

---

## §VerifyAfterAnyBranch

After ANY branch completes, run SelfAudit checks:

```bash
# Check 1: skill.json files: list matches disk
node -e "
const root = process.env.CLAUDE_PLUGIN_ROOT + '/skills/adia-ui-gen-review';
const fs = require('fs');
const s = JSON.parse(fs.readFileSync(root + '/skill.json','utf8'));
const missing = s.files.filter(f => !fs.existsSync(root + '/' + f));
if (missing.length) { console.error('MISSING:', missing); process.exit(1); }
console.log('OK — all', s.files.length, 'files present');
"

# Check 5: TAG_TO_COMPONENT coverage (run from the monorepo root)
node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-coverage-audit.mjs --strict
```

---

## §AntiPatterns

- ✗ Adding new knowledge directly to SKILL.md prose — SKILL.md is cold-start weight only; it should cite file destinations, not duplicate content
- ✗ Updating a rubric threshold without also updating SKILL.md §ExitCondition — the exit gate and the threshold must agree
- ✗ Adding a TAG_TO_COMPONENT entry using a display name that doesn't match the component's `name:` field in its yaml
- ✗ Adding a new root-cause code without bumping `schemaVersion` — downstream tools validate against the schema
- ✗ Updating rubric-score.md §Dimensions without checking if rubric-decompose.md Phase 2 produces the data the new dimension consumes
