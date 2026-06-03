# `recovery-paths.md` — the 5 recovery scenarios

> Loaded by mode 2 (Author from scratch) when `[Unreleased]` promotion requires extension beyond the peer's early release commit; by mode 4 (Batch push); on F-N1 or pre-flight failure in mode 1; and by mode 7 (Post-release recovery — Phase 3 expansion).

Each scenario below has the **shape** ("what does the repo state look like?"), the **canonical example** (the cycle where it happened), the **resolution** (commands + judgment calls), and **what to write in the ledger**.

---

## §Scenario 1 — Version-skip correction

**Shape:** Peer cut a release commit but mislabeled the version. Common form: package.json bumped 0.6.X → 0.6.X+2, skipping 0.6.X+1. The peer's CHANGELOG body may even reference both "the v0.6.X+1 sweep" and "the v0.6.X+2 cut" as if they were two separate releases. Tags don't exist yet; npm latest is still 0.6.X. The commit is unpushed.

**Canonical case:** v0.6.12 correction (2026-05-20).

Peer commit `e8490d96d release(*): v0.6.13 lockstep — admin-shell composition anchors + legacy CSS bridges retired` bumped 0.6.11 → 0.6.13, skipping 0.6.12. The CHANGELOGs referenced "the v0.6.12 dogfooding sweep" and "the v0.6.13 cut" as if both shipped. Operator asked for v0.6.12 release; investigation revealed it was the same body of work, mislabeled.

**Resolution:**

1. Verify the skip — `npm view <pkg> versions --json | tail` confirms no 0.6.X+1 on npm; `git tag --list 'v0.6.X+1*'` confirms no tags. Run pre-flight gates at the peer's commit to confirm content is shippable (no demo-shell fail etc.).
2. **Correct the version in-place via a NEW commit on top of the peer's commit** (NOT amend — the peer's commit stays for history; `b62992aa0` is the repo precedent).
3. Run a script (the v0.6.12 cycle used `/tmp/v0612-correct.mjs`) that rewrites every occurrence of the wrong version. For v0.6.12, 25 files needed edits:
   - 9 × `package.json` (version field)
   - 9 × `CHANGELOG.md` (header + any body refs)
   - 4 × admin-shell CSS files (header comment refs)
   - 1 × ADR-0032 (multiple body refs — be careful to preserve filename references like `v0.6.13-admin-shell-composition-anchors-...md` that intentionally encode the original label)
   - 1 × FEEDBACK ticket (status line)
   - 1 × audit note (factual reference)
   - 1 × `package-lock.json` (regenerate via `npm install --package-lock-only`)
4. Commit the correction with a `fix(release): correct v0.6.X+2 version-skip → v0.6.X+1` message that documents the discovery.
5. **THEN** proceed to the standard cycle from Step 5 onward (`cycle-happy-path.md`). Tag, push, publish at v0.6.X+1.

**What to write in the ledger:**

```json
"version_skip_correction": {
  "issue": "Peer release commit <sha> ('release(*): v0.6.X+2 ...') bumped 0.6.X → 0.6.X+2, skipping 0.6.X+1. 0.6.X+1 was never tagged or published (npm latest was 0.6.X). The commit's CHANGELOG bodies further framed the work as two separate releases though it is a single commit.",
  "root_cause": "<usually: multi-phase plan staged across versions; phases collapsed but the label landed on the higher version>",
  "fix": "Correction commit <new-sha> — 0.6.X+2 → 0.6.X+1 across N files: 9 package.json + 9 CHANGELOG + ..."
}
```

---

## §Scenario 2 — Batch push

**Shape:** Multiple unpushed `release(*): vX.Y.Z` commits sit on `main` since the last published tag. Each one bumps the version, each has its own CHANGELOG block, each has its own substantive content. The operator asks to "initiate the latest version" or "publish what's accumulated."

**Canonical cases:**

- v0.6.1 → v0.6.6 (6-release batch, 2026-05-19)
- v0.6.14 + v0.6.15 (2-release batch, 2026-05-20)

**Resolution:**

1. Re-baseline. Identify the cluster of unpushed `release(*):` commits. Order them oldest-to-newest.
2. For EACH version's release commit:
   - Identify the tag-point SHA. **Tag at each version's release-commit SHA**, not at HEAD. (Exception to the standard "tag at HEAD" rule — batch push tags each version where it was actually cut.) Memory: `feedback_tag_at_head_not_bump_commit`.
   - Run pre-flight gates at that SHA (via detached checkout if you want full rigor; or trust the peer's verification if the commits were verified at cut time).
   - Run F-N1 against the tag candidate — diff-coverage warns may differ per version.
3. Push `main` (sweeps all commits at once).
4. Push the per-version tags + umbrella tags (10 tags per version).
5. **Publish in version order, oldest first**, waiting for each version's 9 workflows to settle before dispatching the next version's 9. This is non-negotiable — `npm dist-tag latest` is set by publish order. If you dispatch v0.6.15 before v0.6.14, you have to manually `npm dist-tag add @adia-ai/<pkg>@0.6.15 latest` after to fix it.
6. GH releases — author one note per version, then `gh release create` each. The notes can be terser since users will read the rollup.
7. Site deploy — once at the END (deploys reflect HEAD).
8. Ledger — write **one batch-push ledger** at `.brain/audit-history/YYYY-MM-DD-batch-push-vA.B.C-vX.Y.Z.json` covering all the versions, instead of N per-version ledgers.

**What to write in the ledger:**

```json
"kind": "batch-push",
"audit_id": "YYYY-MM-DD-batch-push-vA-vZ",
"versions": ["A.B.C", "A.B.D", "A.B.E"],
"tag_commits": {
  "vA.B.C": "<sha>",
  "vA.B.D": "<sha>",
  ...
},
"publish_workflows": {
  "dispatched": "N/N — vA.B.C set dispatched + settled FIRST, then vA.B.D set, then vA.B.E set (ordering ensures npm latest lands on vA.B.E)",
  "conclusions": "N/N success"
}
```

---

## §Scenario 3 — Author from scratch (`[Unreleased]` promotion)

**Shape:** Peer landed source changes + CHANGELOG entries under `## [Unreleased]` but didn't bump versions or cut a release commit. Operator asks to "initiate v0.6.X release."

**Canonical cases:**

- v0.6.19 (claims-ui-v4 FB-22-33 batch — 12 unpushed commits, all under `[Unreleased]`)
- v0.6.20 (claims-ui-v5 FB-34-39 batch — 14 unpushed commits, all under `[Unreleased]`)
- v0.6.21 (table-ui §403 + FB-37 retraction — 23 unpushed commits)

**Resolution:** Standard `cycle-happy-path.md` Variant B (Step 4 inserts `[Unreleased]` → `[vX.Y.Z] — DATE` promotion). The CLI helper `scripts/promote-unreleased.mjs` mechanizes the heading swap. For packages that need fresh blocks (the corpus-regen case), author them per `changelog-discipline.md` § Authoring.

---

## §Scenario 4 — `[Unreleased]` extension (early-cut release commit + post-bump work)

**Shape:** Peer pre-cut a release commit early (e.g. `f167b72bc release(*): v0.6.18 lockstep — loading state + text-ui`) but then landed MORE commits on top that:

- Have CHANGELOG entries under `[Unreleased]` (the peer was building the next release)
- Include a fix that **completes the early release's own scope** (e.g. `d6d980072 fix(demo-shells): import skeleton-ui` — fixes the demo shells that f167b72bc's loading-state feature broke)

The early release commit FAILS a release-blocking gate (`check:demo-shells` in v0.6.18). The completing fix is entangled with unrelated `[Unreleased]` work — can't be cleanly cherry-picked back.

**Canonical case:** v0.6.18 — f167b72bc's stat/table demo shells used `<skeleton-ui>` without importing it; `check:demo-shells` failed at that commit. The fix `d6d980072` landed 10 commits later, interleaved with FB-13/14/15/17 `[Unreleased]` work.

**Resolution:** Two options:

1. **Cherry-pick the fix onto the release commit** to make it shippable in its original scope. Off-mainline tag — messy archaeology.
2. **Extend the release to HEAD** by promoting the `[Unreleased]` content into `[VERSION]`. The release becomes larger but ships everything consistent. ← This is what v0.6.18 did.

**Choose option 2** when the early release commit fails a gate AND the completing fix can't be isolated. Choose option 1 only if the operator explicitly wants the minimal scope.

For option 2:

1. Verify HEAD passes all gates (detached checkout from `f167b72bc` confirms the gate failure there; verify HEAD passes).
2. Promote `[Unreleased]` → `[VERSION]` in the affected CHANGELOGs (`promote-unreleased.mjs`).
3. For packages whose changes have NO `[Unreleased]` entry yet but DID change (corpus catalog regen — same case as `changelog-discipline.md` § Authoring), write a fresh `[VERSION]` block.
4. Commit the CHANGELOG merge with a message that documents the boundary decision (the v0.6.18 cycle's `552bc825f` is the reference).
5. Tag at the new HEAD; proceed.

**What to write in the ledger:**

```json
"boundary_decision": {
  "issue": "Early release commit <sha> failed <gate>. Fix landed in <fix-sha>, entangled with [Unreleased] work that includes <FB list>.",
  "resolution": "v0.6.X absorbed everything through HEAD. <Unreleased> CHANGELOG sections promoted to [v0.6.X] across <pkg list>. v0.6.X tags land at <merge-sha>."
}
```

---

## §Scenario 5 — Stale test detection

**Shape:** A pre-flight test fails. The test asserts a behavior the peer deliberately changed in a `[Unreleased]` / `[VERSION]` entry. The failure isn't a regression — it's a stale test that was never updated to match the deliberate change.

**Canonical case:** v0.6.20 — `admin-shell.test.js` 'contains the vanilla-HTML fallback block' test (a v0.6.17 regression guard) asserted the old blanket `[slot="heading"] { display: none }` shape. The v0.6.20 FEEDBACK-38-addendum fix deliberately narrowed it to `:is(span,p,div,h1-6)[slot="heading"], [slot="heading"]:not(:has(> [slot]))` (composed wrappers survive collapse). The peer shipped the CSS change but did NOT update the test.

**Resolution:**

1. **Read the test's assertion + read the CHANGELOG entry that documents the change.** Both should describe the same behavior. If they disagree → one of them is stale.
2. **Read the actual production code** that the test asserts about. If the code matches the CHANGELOG entry's description → the test is stale. If the code matches the test → the CHANGELOG is wrong (or the change was reverted).
3. For a stale test: update the assertion to match the new, documented behavior. **Add an inline comment** in the test explaining the v0.X.Y change so future operators don't repeat the diagnosis.
4. Consider adding a NEW assertion that pins the v0.X.Y contract explicitly (the v0.6.20 case added the `:not(:has(> [slot]))` guard assertion).
5. Run the test — confirm it passes.
6. Include the test update in the release commit's allowlist (it's part of the release work — the operator authored the fix that the peer's change implied).

**What to write in the ledger:**

```json
"notes": [
  "STALE TEST FIXED: <test path> '<test name>' asserted the old <behavior>. The v0.X.Y <feature> fix deliberately changed it to <new behavior>. The peer shipped the source change but did not update the test. Deploy session updated the assertion to match the new shape + added a guard assertion for the <new contract>. Not a regression — a stale test."
]
```

---

## §Scenario 6 (bonus) — Concurrent peer mid-cycle

**Shape:** A peer agent is actively modifying files while you're running a release. You see the working tree shift between commands. `git stash pop` may report a conflict. New uncommitted files appear that weren't there 30 seconds ago.

**Canonical case:** v0.6.20 post-stash-pop — the peer committed the FEEDBACK-37 revert (`664cb3f55`) RIGHT AFTER my release shipped, making my stashed admin-shell.js delta redundant. The pop reported "kept the stash."

**Resolution:**

1. **Don't fight the peer.** Their working-tree changes are theirs. Confirm v0.6.X is fully shipped (tag pushed + npm published + GH releases + site deployed + ledger committed) — if yes, the release itself is safe regardless of post-release working-tree chaos.
2. If you stashed peer files at Step 2 of the cycle, after the cycle completes:
   - Try `git stash pop`. If clean — great.
   - If "kept the stash" — investigate: is the stash now redundant (peer committed the same content)? Compare via `git stash show -p stash@{0}` vs the relevant `git log -p` for the file.
   - If redundant: `git stash drop` (the work was preserved in the peer's commit).
   - If NOT redundant: leave the stash. It preserves the peer-in-flight change; the peer (or operator) decides next.
3. Note the situation in the ledger so the next cycle has context.

---

## §Decision flowchart — which scenario applies?

```text
Pre-flight or F-N1 gate failed?
├── check:demo-shells fails at the release-commit candidate?
│   └── Look at the post-commit diff: was there a fix-up?
│       ├── Yes, but entangled with [Unreleased] work → Scenario 4
│       └── No → Author the fix in this cycle (Mode 2 from scratch)
├── check:lockstep fails? → typically a peer manually edited an
│   internal range during a PATCH cut → Scenario 4 or fix in place
├── verify:corpus fails? → corpus drift → routes to adia-ui-a2ui skill
├── check:embeddings-fresh fails? → run npm run build:embeddings:chunks;
│   stage chunk-embeddings.json; document in a2ui-corpus CHANGELOG
├── test:unit fails? → Scenario 5 (stale test) OR real regression
│   (read assertion vs CHANGELOG vs source code to tell apart)
└── F-N1 warns (cosmetic)? → enrichment pass (changelog-discipline.md)

Multiple unpushed release commits exist?
└── Scenario 2 (batch push)

Peer commit's CHANGELOG references a different version than its bump?
└── Scenario 1 (version-skip correction)

Working tree has uncommitted source files when you start the cycle?
└── Apply multi-agent-baseline.md § classification taxonomy.
    Stash strays per § Discipline 4 if they're release-relevant +
    undocumented + contradicting.
```

---

## §When this reference is "done v1"

- Each of the 5 (now 6) scenarios has a documented case study in `assets/case-studies/` (Phase 3).
- The decision flowchart correctly routes the next 5 release cycles with no operator override.
- Each scenario's ledger-template fragment is reused verbatim by the `make-ledger.mjs` helper (Phase 3) for that scenario.
