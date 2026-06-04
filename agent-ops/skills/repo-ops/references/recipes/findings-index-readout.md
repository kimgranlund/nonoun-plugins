---
date: 2026-04-29
coverage: canonical
peers:
  - ../audit-patterns/audit-history-ledger.md
  - continuous-learning-loop.md
  - ../doc-types/postmortem-pattern.md
status: practice-verified
---

# Findings index — closing the read side of the audit ledger

> **The premise.** The audit ledger (`.brain/audit-history/*.json`) is _write-rich, read-poor_. Audits accumulate findings with severity codes (F-W1, F-S4, etc.) but nothing surfaces them — there's no list view, no "open findings" surface, no way to ask "what's still on the action surface?" without `cat`-ing every JSON file.
>
> The read-side closure is a single generated Markdown file at `.brain/findings/INDEX.md` that folds every `findings[]` entry across the audit history into one sortable table. Plus a hand-curated `## Graduations` section that tracks finding-to-permanent-infrastructure pairs.

## What this delivers

A repo with a healthy audit-history ledger but no findings index has _capture without action_. Audits keep noting "F-S4 high — render-method drift in stepper.js" — and unless you happen to be reading that specific JSON, you'll never see it again. A future audit re-emits the same finding type from a different commit; the pattern doesn't surface; nothing graduates.

The findings-index closes that loop:

1. **Surface OPEN findings.** Anything `fix_applied: false` rises to the top of the index. The first thing a new agent in the repo can do is grep `OPEN` in `.brain/findings/INDEX.md` and pick from the action surface.
2. **Track graduations.** When a recurring finding-type prompts permanent infrastructure (a trip-wire, a generator, a convention), that pairing is recorded in the `## Graduations` section. The index becomes the institutional memory of _which findings became rules_.
3. **Auto-close findings.** When a later audit emits `F-X-resolved`, the original `F-X` auto-promotes from OPEN to CLOSED-LATER. The ledger stays append-only; the index reflects the latest truth.
4. **Refresh on the harvest cron.** Same cadence as the audit-history workflow. No new infrastructure, no second cron, just one extra script step.

## The minimum viable shape

```text
.brain/
├── audit-history/        # write side (per audit JSON)
│   ├── 2026-04-27.json
│   ├── 2026-04-28.json
│   └── 2026-04-29-002.json
└── findings/
    └── INDEX.md          # read side (regenerated)
```

`INDEX.md` is a single file. It is **not** an index in the README sense (one row per audit) — it's an aggregate of all `findings[]` entries across all audits, sorted by status × severity × id.

## Status taxonomy

Each finding falls into one of six bins. Sort the table by this order — the action surface always sits at the top.

| Status | Rule | Read |
| --- | --- | --- |
| `OPEN` | `fix_applied === false` | Action surface — pick from the top. |
| `DONE-WITH-FOLLOWUP` | `fix_applied === true && follow_up exists` | Fix landed; the audit flagged a follow-up that hasn't been addressed. |
| `DONE` | `fix_applied === true && no follow_up` | Fixed in the same session as the audit; no follow-up flagged. |
| `CLOSED-EARLIER` | `id` ends with `-resolved` | Re-check confirming an earlier OPEN has since been addressed. |
| `CLOSED-LATER` | original was OPEN/DONE-WITH-FOLLOWUP **and** a `<id>-resolved` exists in a later audit | Auto-promoted; original retains its position in the audit JSON, but the index reflects the latest state. |
| `INFO-ONLY` | `fix_applied === null` | Positive observations (trip-wires passing, healthy cadence, etc.). Recorded for ledger continuity. |

Within each status, sort by severity: `high > warn > drift-resolved > info > info-positive > nit`. Then by `id` alphabetical.

## The Graduations section

The hand-curated `## Graduations` table is the load-bearing innovation. It records, in plain text, the pairs:

```markdown
## Graduations

| Finding | Permanent fix |
|---|---|
| [F-N1](../audit-history/2026-04-29-003.json) | Pre-commit Check 3 — journal-date sanity (commit `342ba89c`) |
| [F-W1](../audit-history/2026-04-29-002.json) | `docs/journal/2026/04/INDEX.md` (commit `35146f9d`) |
| [F-A1](../audit-history/2026-04-29.json) | Daily build-log harvest cron firing |
```

This is the read-side answer to _"what do we do with findings beyond fixing them once?"_ When the same finding-type recurs (today's F-S4 echoes last week's F-S2), the graduation table tells you: "we already know this class is recurring — it's earned a trip-wire."

**Pre-seed the table on first generation; preserve it across regenerations.** The table is the memory; the rest of the index is the rendering.

## The generator script (~280 lines)

The reference implementation is a Node script that:

1. Reads every `.brain/audit-history/*.json`.
2. Tracks `audit_id` separately from filename (mismatches happen — one repo had `2026-04-29.json` containing `audit_id: "2026-04-29-001"`).
3. Flattens all `findings[]` entries with their parent audit reference.
4. Auto-promotes OPEN/DONE-WITH-FOLLOWUP to CLOSED-LATER when a `<id>-resolved` exists in a later audit.
5. Sorts by status × severity × id.
6. Preserves the existing `## Graduations` section if it exists; pre-seeds a stub on first run.
7. Writes `.brain/findings/INDEX.md`.

The script is mechanical (no LLM calls). Cheap enough to run on every cron firing.

**Concrete reference**: [`scripts/build/findings-index.mjs`](https://github.com/adiahealth/gen-ui-kit/blob/main/scripts/build/findings-index.mjs) in the chat-ui repo (~280 lines). It's the canonical implementation that the chat-ui repo wires into its daily build-log workflow.

## Wiring into the harvest cron

Add one step to the daily harvest workflow, after the harvester:

```yaml
# After the harvester step:
- name: Refresh findings index
  run: node scripts/build/findings-index.mjs
```

Cheap (just JSON reads + a markdown write); always runs so the index reflects whatever `.brain/audit-history/` currently holds, even on runs where the harvester itself skipped (no material delta).

The PR-creator step that already bundles audit-history changes will pick up `.brain/findings/INDEX.md` automatically.

## When a finding "graduates"

Three signals that a finding-type is ready to graduate from "fixed once" to "permanent infrastructure":

1. **Recurrence.** The same finding-type appears in 2+ audits across different commits. Today's F-S4 echoes a prior F-S2; the pattern is real, not a one-off.
2. **Mechanical verifiability.** The rule the finding implies can be checked by a script (link checker, grep, AST walk) — not "use good judgment."
3. **Clear failure mode.** The cost of _not_ graduating is concrete (a future incident, a daily noise source, a recurring doc-drift class).

Graduations don't require ceremony. When you ship the trip-wire, edit the `## Graduations` table to record the pair: `<finding-id>` → `<permanent fix + commit SHA>`. That's the institutional record.

## Anti-patterns to avoid

1. **Don't make the index `cat`-able from individual audits.** The point is _aggregation_. If the index just lists audits with their findings nested, you've reproduced the read problem.
2. **Don't auto-curate Graduations.** The pairing of "this finding" → "this trip-wire" requires human judgment. Pre-seed and preserve; never overwrite.
3. **Don't drop INFO-ONLY findings.** Positive observations (trip-wires passing, healthy cadence) are the _evidence_ that the system is working. Hiding them makes the index look like a problem list, when much of the value is the green count.
4. **Don't replace the audit JSONs.** The index is a _view_. The JSONs remain the source of truth — append-only, immutable, schema-validated.

## Auto-resolution for Tier 1 findings

Mechanical findings (Tier 1 in the Decompose step — lychee, `wc -l`, hook-presence, `check-skill-frontmatter`) can be automatically verified for resolution in the next audit run without a human manually emitting a `-resolved` marker.

**Procedure after each re-audit:**

1. For each OPEN finding whose underlying check is a Tier 1 command:
   - Re-run that specific command against the current repo state
   - If the check now passes → emit `<id>-resolved` into the audit JSON; the generator script auto-promotes the finding to `CLOSED-LATER` in the index on the next regeneration
   - If the check still fails → leave `OPEN`; update a `last_seen` field so the index shows how long the finding has been active

2. For Tier 2 findings (staleness probe, memory-home completeness, coverage gaps): these require agent judgment to re-evaluate. Surface them in the new gap report with the label `[re-check required — OPEN since <date>]` so a human can confirm resolution before promotion.

**Why this matters.** Without auto-resolution, OPEN findings accumulate indefinitely — a repo that fixed its broken links two months ago still shows them as OPEN in the index. The `-resolved` marker already exists in the schema; this procedure closes the loop without new infrastructure. Tier 1 auto-close; Tier 2 prompt-for-confirmation. Combine with the existing `## Graduations` section to distinguish "fixed once" (CLOSED-LATER) from "graduated to trip-wire" (Graduations table).

## Related

- [`audit-patterns/audit-history-ledger.md`](../audit-patterns/audit-history-ledger.md) — the write-side ledger this recipe reads from.
- [`recipes/continuous-learning-loop.md`](continuous-learning-loop.md) — the broader Promise 5 pattern; this recipe is one specific closure.
- [`doc-types/postmortem-pattern.md`](../doc-types/postmortem-pattern.md) — postmortems are the _narrative_ counterpart; the findings-index is the _structured_ counterpart.
