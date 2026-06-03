# Case study — FEEDBACK-37 retraction (v0.6.20 → v0.6.21)

**Cycles:** 2026-05-21 (v0.6.19 → v0.6.20 → v0.6.21) **Scenario:** `recovery-paths.md` § Scenario 6 (concurrent peer mid-cycle) + `../../references/recovery-paths.md` § post-publish revert **Source ledgers:** `2026-05-21-release-v0.6.20.json`, `2026-05-21-release-v0.6.21.json` **Outcome:** Feature shipped in v0.6.20; retracted one cycle later in v0.6.21 after a peer-led re-diagnosis ratified by ADR-0033.

---

## §The shape — v0.6.20 cycle

User asked: _"prepare and initiate 0.6.20 release"_. The cycle was a substantial Mode 2 (author from scratch) with claims-ui-v5 feedback batch FB-34–39 already landed under `[Unreleased]`, plus a new `<admin-entity-item>` shell primitive.

Among the FEEDBACK closures: **FEEDBACK-37** — _"admin-shell warns when `<admin-topbar>` / `<admin-statusbar>` is missing its slot."_ The fix added a `#checkSlotContracts()` method to `admin-shell.js` that emitted a one-shot `console.warn` when an `<admin-topbar>` or `<admin-statusbar>` element was placed inside `<admin-sidebar>` or `<admin-content>` without `slot="header"` / `slot="footer"`.

The web-modules `[0.6.20]` CHANGELOG documented this as:

> `### Added — admin-shell warns when <admin-topbar> / <admin-statusbar> is missing its slot (FEEDBACK-37)`

---

## §The mid-cycle discovery

While operator was staging the v0.6.20 release commit, `git status` showed an UNEXPECTED uncommitted change:

```text
 M packages/web-modules/shell/admin-shell/admin-shell.js
```

Diffing it: a peer had **uncommitted-staged a REVERT** of the FEEDBACK-37 method — `#checkSlotContracts()` was being removed, `static #warnedSlots = new WeakSet()` was being removed, the call site in `connected()` was being removed.

But the v0.6.20 CHANGELOG documented FEEDBACK-37 as **added**. The peer's uncommitted revert directly contradicted the release's own documentation.

Operator applied `multi-agent-baseline.md` § Discipline 4 (stash workflow for strays):

```bash
git stash push packages/web-modules/shell/admin-shell/admin-shell.js \
  .agents/skills/<companion-skill>/SKILL.md \
  -m "v0.6.20-cycle: peer-in-flight FEEDBACK-37 revert in admin-shell.js + SKILL.md — excluded from release"
```

v0.6.20 shipped with FEEDBACK-37 PRESENT (matching the CHANGELOG), the stashed revert preserved for the peer.

---

## §The post-publish discovery

Right after v0.6.20 publishes settled, operator ran `git stash pop` to restore the peer's working state. The pop reported "kept the stash" — a conflict.

Investigation:

```bash
git log d7d44a727..HEAD --oneline
# 664cb3f55 fix(*): 0.6.20 follow-up — revert admin-shell slot warn + toast/input fixes
```

**The peer had committed the revert RIGHT AFTER v0.6.20 publishes settled.** The commit message named the intent: _"0.6.20 follow-up — revert admin-shell slot warn."_

So FEEDBACK-37 shipped in v0.6.20 and the peer immediately reverted it for v0.6.21. The "follow-up" naming implied the peer had already diagnosed this as a misdiagnosis and wanted to retract.

The stash became redundant — the peer committed the same content. Operator dropped the stash:

```bash
git stash drop stash@{0}
```

The v0.6.20 ledger named the situation in `notes`:

> "PEER-IN-FLIGHT EXCLUDED: a concurrent peer had an uncommitted revert of the FEEDBACK-37 slot-contract diagnostic in admin-shell.js (removed #checkSlotContracts() + #warnedSlots). v0.6.20's CHANGELOG documents FEEDBACK-37 as ADDED, and the feature IS committed (d32e34b4f). The uncommitted revert directly contradicts the [0.6.20] CHANGELOG, so it was git-stashed and excluded — v0.6.20 ships the committed state (FEEDBACK-37 present). The revert + SKILL.md edit were restored to the working tree post-release for the peer. FLAGGED to operator: a peer may be reconsidering FEEDBACK-37; if the revert lands, v0.6.21 would remove what v0.6.20 adds."

---

## §The v0.6.21 cycle — retraction

User asked: _"prepare and initiate 0.6.21 release"_.

The v0.6.21 cycle was a normal Mode 2 (author from scratch). The web-modules `[Unreleased]` block now had:

> `### Fixed — admin-shell no longer emits a spurious slot-contract console.warn`

Phrased as a **fix** (a spurious warn was removed), not a **removal** (the feature was rescinded). The peer's framing: the v0.6.20 diagnostic had been **misdiagnosed**, and emitted false positives on legitimate compositions where `<admin-topbar>` / `<admin-statusbar>` landed in the default body slot LEGITIMATELY (per the Light-DOM substrate's `slot=` decorative-not-directive semantics).

The cycle also ratified the framing as **ADR-0033 "Light-DOM substrate"** — making explicit the stance that `slot=` is decorative metadata, not a projection directive; positioning is by CSS rules matching tag + ancestor + DOM order. This is the _zeroth question_ to ask when output looks wrong: "am I treating `slot=` as if it's directive when the substrate is Light-DOM?"

v0.6.21 shipped the retraction + ADR-0033. The release notes carried a **heads-up paragraph** naming the round-trip:

> **Heads-up:** v0.6.20 shipped a FEEDBACK-37 slot-contract `console.warn` that was found to misdiagnose legitimate compositions. v0.6.21 retracts it. If you're on v0.6.20 and saw the warn fire, you can ignore it — upgrade to v0.6.21.

---

## §The lesson

1. **A peer's uncommitted revert is a SIGNAL.** Diff it, classify per `multi-agent-baseline.md` § Discipline 2, decide. Don't silently ship; don't silently revert.
2. **CHANGELOG-contradicting strays MUST be excluded.** v0.6.20's CHANGELOG documented FEEDBACK-37 as ADDED; shipping with the revert applied would have made the CHANGELOG dishonest.
3. **One-version round-trips are recoverable.** A feature shipped in vN.M.X and retracted in vN.M.Y+1 isn't catastrophic — the retraction note explains it. The cost is a one-line "if you saw X, upgrade" in the v0.6.21 release notes.
4. **Ratification via ADR.** When a retraction reveals a deeper framing issue (here, Light-DOM substrate mechanics), write an ADR. ADR-0033 is the durable artifact; the retracted feature becomes the prompt that surfaced the architectural decision.
5. **Stash-then-restore preserves peer work.** The stash workflow meant zero data loss for the peer; the peer committed the same content shortly after; the stash became redundant.
6. **The flagged-to-operator note in the v0.6.20 ledger correctly predicted v0.6.21.** Future cycles reading the ledger can trace "feature shipped + ledger flagged thrash risk + retracted next cycle" as a pattern.

---

## §Ledger fragments

### v0.6.20 ledger (the flag)

```json
"notes": [
  "PEER-IN-FLIGHT EXCLUDED: a concurrent peer had an uncommitted revert of the FEEDBACK-37 slot-contract diagnostic in admin-shell.js. v0.6.20's CHANGELOG documents FEEDBACK-37 as ADDED, and the feature IS committed (d32e34b4f). The uncommitted revert directly contradicts the [0.6.20] CHANGELOG, so it was git-stashed and excluded — v0.6.20 ships the committed state (FEEDBACK-37 present). FLAGGED to operator: a peer may be reconsidering FEEDBACK-37; if the revert lands, v0.6.21 would remove what v0.6.20 adds."
]
```

### v0.6.21 ledger (the retraction)

```json
"feedback_37_round_trip": "FEEDBACK-37 (admin-shell slot-contract diagnostic) shipped in v0.6.20 and is retracted in v0.6.21 — found to misdiagnose legitimate compositions. One-version round-trip. Post-mortem at journal §398; correction-loop discipline captured in a companion skill; Light-DOM substrate stance made explicit at ADR-0033."
```

---

## §Cross-references

- `../../references/recovery-paths.md` § Scenario 6 — concurrent peer mid-cycle
- `../../references/multi-agent-baseline.md` § Discipline 4 — stash workflow
- `../../references/notes-authoring.md` § Cross-references — heads-up paragraph pattern in single-version notes
- `../../references/ledger-discipline.md` § notes (the lesson log) — the PEER-IN-FLIGHT EXCLUDED phrasing
- ADR-0033 — Light-DOM substrate
- a companion consultant skill — the correction-loop discipline that generalizes the lesson (diagnose layer-of-origin before patching)
