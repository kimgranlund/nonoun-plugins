# Case study — v0.6.18 `[Unreleased]` promotion + demo-shell fix

**Cycle:** 2026-05-21 (v0.6.17 → v0.6.18) **Scenario:** `recovery-paths.md` § Scenario 4 (`[Unreleased]` extension on incomplete release commit) **Source ledger:** `.brain/audit-history/2026-05-21-release-v0.6.18.json` **Outcome:** Peer's early release commit failed a release-blocking gate; cycle extended to HEAD via `[Unreleased]` → `[0.6.18]` promotion.

---

## §The shape

User asked: _"prepare and initiate 0.6.18 release"_.

Operator re-baselined and found 15 unpushed commits since the v0.6.17 ledger. Among them:

- `f167b72bc release(*): v0.6.18 lockstep — loading state (FB-12 P2) + text-ui overlay attrs (FB-10)` — the peer's release commit, **cut early**.
- 14 commits AFTER it, including:
  - `8da3825b7 skill v2.11.0`
  - `dfeb712d4 docs(admin-shell) sidebar gallery`
  - `9207e801e fix(*): resolve outbox tickets FB-14/15/16/17/18`
  - `d6d980072 fix(demo-shells): import skeleton-ui in stat + table demo shells` — ← **completes v0.6.18's own scope**
  - `fec55d82d skill v2.12.0`
  - `5c739a659 fix(check:skills)`
  - (and more)

One of the post-commits had a CHANGELOG fragment naming itself "post-v0.6.18": _"docs(tickets): update TRIAGE-2026-05-21 + file FB-12 followup post-v0.6.18"_. The peer's intent was clear: `f167b72bc` IS v0.6.18; everything after is for a future release, staged under `## [Unreleased]`.

---

## §The diagnosis (the surprising part)

Operator did a detached checkout to f167b72bc and ran the pre-flight gates AT THAT COMMIT:

```text
=== check:demo-shells (at f167b72bc) ===
    demo:     packages/web-components/components/table/table.html
    missing:  skeleton-ui
    declared: check-ui, icon-ui, progress-ui, pagination-ui, skeleton-ui, badge-ui
✗ FAIL
```

**`f167b72bc` failed `check:demo-shells`.** The cycle's own substantive feature (FB-12 `stat-ui loading` + `table-ui loading` shipped via `<skeleton-ui>`) was used in the stat/table demo `.html` shells, but those shells didn't import `<skeleton-ui>`. The demo pages would render `<skeleton-ui>` as `HTMLUnknownElement` — unstyled, unregistered.

The fix existed: `d6d980072 fix(demo-shells): import skeleton-ui in stat + table demo shells` — but it landed **10 commits later**, entangled with FB-13/14/15/17 `[Unreleased]` work.

Two choices:

- **Option A**: Cherry-pick `d6d980072` onto `f167b72bc` to make the release commit shippable in its original scope. Off-mainline tag (the new commit isn't on `main`'s mainline). Messy archaeology.
- **Option B**: Extend v0.6.18 to HEAD by promoting the `[Unreleased]` content into `[0.6.18]`. The release becomes larger but ships everything consistent.

Operator chose **Option B**. Rationale: the peer had clearly intended to ship `f167b72bc` as v0.6.18 + had documented further work as `[Unreleased]` for the next cut — but the demo-shell fix is **part of v0.6.18's own scope** (it completes the feature the cut introduced). Extending v0.6.18 to absorb everything is the honest framing.

---

## §The fix

### 1. Verify HEAD passes all gates

```bash
git checkout main  # return from detached HEAD
npm run check:demo-shells  # PASSES at HEAD
```

### 2. Promote `[Unreleased]` → `[0.6.18]` across affected CHANGELOGs

The `[Unreleased]` blocks on `main` (post-`f167b72bc`) had:

- `packages/web-components/CHANGELOG.md` — FB-14 (toggle-scheme `[data-scheme]`) + FB-15 (button-ui warn)
- `packages/web-modules/CHANGELOG.md` — FB-17 (admin-sidebar resize-handle diagnostic) + sidebar-gallery docs

The `[0.6.18]` block at line ~17 of each was a STUB ("Lockstep version bump only. No source changes in this package") — but the package DID change post-cut. The peer hadn't reconciled the stub.

The merge:

- web-components: delete the `## [Unreleased]` heading; FB-14 + FB-15 sections fall under `[0.6.18]` (with the existing FB-12 + FB-10 entries from the original cut).
- web-modules: delete the `## [Unreleased]` heading AND the stub `## [0.6.18]` block; FB-17 + sidebar-gallery sections become the new `## [0.6.18]` block.
- a2ui-corpus: had no `[Unreleased]` block but the catalog regenerated post-cut. Authored a fresh `## [0.6.18]` entry per `changelog-discipline.md` § Authoring.

### 3. Commit + tag

```bash
git add packages/web-components/CHANGELOG.md \
        packages/web-modules/CHANGELOG.md \
        packages/a2ui/corpus/CHANGELOG.md

git commit -m "$(cat <<'EOF'
chore(release): promote [Unreleased] → [0.6.18] — v0.6.18 = HEAD

The v0.6.18 release commit f167b72bc (loading state FB-12 + text-ui
FB-10) cannot be tagged in isolation: it fails check:demo-shells —
its own skeleton-ui demos (stat.html / table.html) don't import
skeleton-ui. The fix landed 10 commits later in d6d980072,
interleaved with unrelated [Unreleased] feedback work (FB-13/14/15/16/17),
so the demo-shell fix cannot be cleanly cherry-picked onto f167b72bc.

Resolution: v0.6.18 absorbs everything through HEAD. The peer parked
post-f167b72bc work under ## [Unreleased] expecting the next release
cut to promote it — this IS that cut. ...
EOF
)"
```

Then tag v0.6.18 at THIS new commit (the `[Unreleased]` merge), **NOT** at f167b72bc. Per the standard tag-at-HEAD invariant.

```bash
git tag v0.6.18
# + 9 per-package tags
```

### 4. F-N1 + push + publish + GH releases + site + ledger

Standard cycle from here. F-N1 was clean at 9/9 (the CHANGELOG promotion brought all the post-cut work under documented `[0.6.18]` entries).

### 5. Document the boundary decision in the ledger

```json
"boundary_decision": {
  "issue": "Early release commit f167b72bc failed check:demo-shells. Fix landed in d6d980072, entangled with [Unreleased] work that includes FB-13/14/15/17.",
  "resolution": "v0.6.18 absorbs everything through HEAD. [Unreleased] CHANGELOG sections promoted to [0.6.18] across web-components + web-modules + a2ui-corpus. v0.6.18 tags land at the [Unreleased]-merge commit.",
  "verified": "f167b72bc check:demo-shells FAIL confirmed via detached checkout; HEAD check:demo-shells PASS confirmed (124 shells)."
}
```

---

## §The lesson

1. **A release commit can fail its own scope.** When a new feature needs demo-shell updates and the cut happens before those updates land, the release commit is incomplete. Pre-flight the release-commit candidate, not just HEAD.
2. **Detached checkout is the rigorous diagnostic tool.** `git checkout <release-commit-sha>` + `npm run check:demo-shells` tells you the truth — does the tag candidate ship a working demo?
3. **Extending vs cherry-picking.** When the completing fix is ENTANGLED with unrelated `[Unreleased]` work (10 commits later, interleaved with feedback fixes), extension via `[Unreleased]` promotion is the clean path. Cherry-picking off-mainline produces messy archaeology.
4. **The peer's `[Unreleased]` parking IS the next-release signal.** Keep-a-Changelog's `[Unreleased]` block exists precisely so the NEXT release cut can promote it. When the peer cut early and continued building, the operator's job is to read `[Unreleased]` as v0.X.Y intent.
5. **The boundary-decision block in the ledger.** Every cycle that extends a release-commit's scope deserves a documented rationale. Future cycles reading `.brain/audit-history/` can trace what happened.

---

## §Cross-references

- `../../references/recovery-paths.md` § Scenario 4 — the canonical checklist
- `../../references/gates-catalog.md` § Category 3 § `check:demo-shells` — the gate that triggered this scenario; failure is **HIGH severity**
- `../../references/changelog-discipline.md` § Promotion — the heading-swap mechanic that merged `[Unreleased]` into `[0.6.18]`
- `../../references/changelog-discipline.md` § Authoring — the fresh-block authoring path for a2ui-corpus
- `../../references/ledger-discipline.md` — the `boundary_decision` block schema (extended in this case study)
