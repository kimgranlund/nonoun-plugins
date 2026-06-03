# Case study — v0.6.12 version-skip correction

**Cycle:** 2026-05-20 (v0.6.11 → v0.6.12) **Scenario:** `recovery-paths.md` § Scenario 1 (version-skip) **Source ledger:** `.brain/audit-history/2026-05-20-release-v0.6.12.json` **Outcome:** Peer commit mislabeled v0.6.13; corrected in-place to v0.6.12 across 25 files; shipped cleanly.

---

## §The shape

User asked: _"prepare and initiate 0.6.12 release"_.

Operator re-baselined and found:

- All 9 `package.json` at version `0.6.13` (not `0.6.12`).
- NO `v0.6.12` tags anywhere.
- npm latest: `0.6.11` (operator had shipped it 1 turn earlier).
- The most recent commit: `e8490d96d release(*): v0.6.13 lockstep — admin-shell composition anchors + legacy CSS bridges retired (FB-04 follow-up / FB-05 dogfood / ADR-0032)`. **Unpushed.**

A peer agent had cut a release commit labeled v0.6.13, jumping straight from v0.6.11 → v0.6.13. The CHANGELOG bodies even referenced both _"the v0.6.12 dogfooding sweep"_ AND _"the v0.6.13 cut"_ as if they were separate releases. Inspecting the commit content showed they were the same work.

---

## §The diagnosis

The peer had executed a multi-phase plan (`.brain/notes/2026-05-20-v0.6.13-admin-shell-composition-anchors.md`) that originally staged the work across v0.6.12 + v0.6.13 + v0.7.0, then collapsed all the phases into one commit but kept the v0.6.13 label.

Symptoms confirming "single commit mislabeled" (vs "two separate releases, one missing"):

- One release commit, not two.
- `e8490d96d`'s file footprint matched the cumulative diff for both "phases" the CHANGELOGs described.
- ADR-0032 named `v0.6.13` as the cut version (singular).
- `.brain/notes/2026-05-20-v0.6.12-bespoke-css-coverage-audit.md` (the audit note) line 19 explicitly: _"Scope decision (corrected from plan (then-named v0.7.0, shipped as v0.6.13) §Phase 0 Step 4)"_ — the peer themselves had already flagged the misattribution but hadn't reconciled the version label.

User wanted v0.6.12. The peer's work was v0.6.12-shape. The label was the only thing wrong.

---

## §The fix

**One correction commit on top** of the peer's commit (NOT amending — the peer's commit is preserved for archaeology; `b62992aa0` is the repo precedent for forensic correction-commits).

The correction rewrote every occurrence of the wrong version:

| Category | Files | Touches |
| --- | --- | --- |
| `package.json` version field | 9 | 9 |
| `CHANGELOG.md` headers + body refs | 9 | ~18 |
| admin-shell CSS header comments | 4 | ~8 |
| ADR-0032 (lockstep cut + Decision/Consequences/Verification refs) | 1 | ~6 |
| FEEDBACK-05 ticket draft (status line) | 1 | 1 |
| v0.6.12 audit note (factual ref) | 1 | 1 |
| `package-lock.json` (regenerated via `npm install --package-lock-only`) | 1 | many |
| **Total** | **25 files** | **~50 edits** |

A Node script (`/tmp/v0612-correct.mjs`) handled the mechanical sweep with two regex patterns:

```js
// Most files — replace 0.6.13 → 0.6.12 unconditionally
txt.replace(/v0\.6\.13/g, 'v0.6.12');

// ADR-0032 — preserve the plan-note filename ref while changing
// version claims; negative-lookahead the filename pattern
txt.replace(/v0\.6\.13(?!-admin-shell-composition-anchors)/g, 'v0.6.12');
```

The plan note `.brain/notes/v0.6.13-admin-shell-composition-anchors-*` file was NOT renamed — it's archaeological planning material; renaming would cascade to every reference in ADR-0032 + the audit note. The correction commit kept the original filename and treated it as a plan-history artifact rather than a current-state claim.

Commit message named the problem + the fix + the precedent:

```text
fix(release): correct v0.6.13 version-skip → v0.6.12

The preceding release commit e8490d96d ("release(*): v0.6.13 lockstep")
bumped all 9 packages 0.6.11 → 0.6.13, skipping 0.6.12 entirely.
0.6.12 was never tagged, never published — npm latest is 0.6.11. The
next contiguous version is 0.6.12, not 0.6.13.

Corrected 0.6.13 → 0.6.12 across 25 files: ...
```

Then the standard cycle resumed: tag v0.6.12 at the correction commit HEAD, F-N1, push, publish, GH releases, site deploy, ledger.

---

## §The lesson

1. **Re-baseline catches version-skip BEFORE you tag.** The user asked for v0.6.12; the operator checked package.json + tags + npm latest + git log; the mismatch surfaced in 3 commands.
2. **Correction commit, not amend.** A NEW commit on top preserves the peer's commit (and its message + SHA) as archaeology. The audit-history ledger documents what happened. Future cycles can trace.
3. **Don't rename filenames carrying historical context.** Plan notes with version-prefixed names are archaeological; their reference graph (ADRs, audit notes, ledgers) is brittle. Treat them as immutable once committed. Use the commit message + ledger to reconcile the version-label conflict.
4. **Negative-lookahead regex protects filename references** from a blanket version replace. `/v0\.6\.13(?!-admin-shell-...)/g` is the pattern.

---

## §Ledger fragment

The v0.6.12 audit-history ledger captured this in a dedicated `version_skip_correction` block:

```json
"version_skip_correction": {
  "issue": "Peer release commit e8490d96d ('release(*): v0.6.13 lockstep') bumped all 9 packages 0.6.11 → 0.6.13, skipping 0.6.12 entirely. 0.6.12 was never tagged or published (npm latest was 0.6.11). The commit's CHANGELOG bodies further framed the work as two separate releases ('v0.6.12 dogfooding sweep' + 'v0.6.13 cut') though it is a single commit.",
  "root_cause": "Original multi-phase plan staged work across v0.6.12 / v0.6.13 / v0.7.0; phases collapsed into one commit but the version label landed on 0.6.13 instead of the contiguous-next 0.6.12.",
  "fix": "Correction commit 2ee4a1f18 — 0.6.13 → 0.6.12 across 9 package.json + 9 CHANGELOG (headers/body/anchors) + 4 admin-shell CSS comment refs + ADR-0032 + FEEDBACK-05 + the v0.6.12 audit note + package-lock.json regen. The plan-note filename (v0.6.13-admin-shell-...) was intentionally left as archaeological planning material; authoritative records (CHANGELOG/ADR/package.json) are correct."
}
```

The presence of this block in a ledger is the signal — `grep -l "version_skip_correction" .brain/audit-history/*.json` lists every cycle that needed this scenario applied.

---

## §Cross-references

- `../../references/recovery-paths.md` § Scenario 1 — the canonical resolution checklist
- `../../references/multi-agent-baseline.md` § Re-baseline — the discipline that surfaces this scenario in the first 3 commands
- `../../references/ledger-discipline.md` § What ELSE to capture per kind — the `version_skip_correction` block schema
- Repo precedent: `b62992aa0 chore(forensic): v0.6.10 release-prep misattribution` — the prior cycle that established the forensic-correction-commit pattern.
