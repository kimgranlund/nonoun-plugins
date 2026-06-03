# `multi-agent-baseline.md` — peer-in-flight classification + stash discipline

> Loaded by every mode when the working tree shows files you didn't author. Companion to `AGENTS.md` § "Multi-agent baseline assumption" — release-side specialization.

The AdiaUI monorepo is **always** worked on by multiple agents concurrently. At any moment a peer agent may be: writing source, drafting tickets, updating skills, regenerating corpus chunks, fixing demo shells, or running an unrelated cycle. Your context is stale at the start of every turn.

Release work is unusually sensitive to peer activity because:

- A release commit's CHANGELOG makes claims (`### Added — X`); peer files in the working tree may **contradict** those claims (the classic v0.6.20 case: peer revert of FEEDBACK-37 while the v0.6.20 CHANGELOG documented FEEDBACK-37 as added).
- A release tarball is built from the tag's tree; peer-in-flight uncommitted files don't ship — but the site build (working-tree driven) DOES include them. This split is silent and easy to miss.
- A `git add -A` on a peer-dirty tree sweeps in peer work without consent. The release commit then makes claims it doesn't authorize.

This reference encodes the four disciplines that prevent these defects.

---

## §Discipline 1 — Re-baseline at every turn

Non-negotiable. The first **four** commands of every release-cycle turn:

```bash
git -C $REPO branch --show-current     # MUST equal main before cutting
git -C $REPO status --short
git -C $REPO log --oneline -8
git -C $REPO fetch && git -C $REPO log HEAD..origin/main --oneline
```

Then read the output BEFORE running anything mutating:

- `branch --show-current` shows the checked-out branch. **It must be `main`.** Peers in this shared clone sometimes work on local feature branches (`fix/*`, `feat/*`) — the AGENTS.md session snapshot saying "Current branch: main" reflects the _prior_ session, not now. Cutting on a feature branch means `git push origin main` pushes the stale `main` ref (not your release commit) while the tags point at the feature tip → tags ahead of main. See the §Wrong-branch recovery below.
- `status` shows working-tree changes. Every modified or untracked file is a classification decision.
- `log -8` shows recent commits. Peer commits since your last turn? New work staged for the release? An unexpected revert?
- `fetch && log HEAD..origin/main` shows remote drift. Did someone else push?

> **§Wrong-branch recovery (v0.7.4 incident, 2026-06-02).** Cut the release on a peer's local-only `fix/font-family-floor-and-css-rollups` instead of main; caught at push (origin/main landed at a mid-window commit, tags pointed at the feature tip). Recovery was clean **because publish is `workflow_dispatch`, not tag-triggered** — npm stayed at the prior version through the whole tangle. If the feature tip's parent is an ancestor of the old main (it was: ff-able), recover with `git branch -f main <release-sha>` → `git checkout main` (no churn since main now == HEAD) → `git push origin main` to fast-forward origin/main to the release commit. Verify `origin/main == vX.Y.Z tag == HEAD` BEFORE dispatching publish. Moving tags while local is free (`tag-lockstep --delete`); moving them after a publish is not.

If anything is unexpected, **diff before deciding**:

```bash
git -C $REPO diff <path>         # working-tree changes
git -C $REPO show <sha> --stat   # peer commits
```

Never proceed past surprising state without classifying it.

---

## §Discipline 2 — Classification taxonomy

Every modified or untracked file falls into one of these buckets:

| Bucket | Definition | Action |
| --- | --- | --- |
| **Mine** | You authored this in the current turn | Stage explicitly |
| **Peer-release-relevant** | Peer authored, part of THIS release's scope (the peer's release-prep work — Variant A) | Stage explicitly |
| **Peer-in-flight, release-relevant, undocumented, contradicts CHANGELOG** | Peer authored, would change the release's behavior but has no CHANGELOG entry and may contradict an existing one | **Stash** — exclude from release; flag to operator |
| **Peer-in-flight, future-release scope** | Peer's working-tree progress destined for a later cut (e.g. `[Unreleased]` block additions, demo-page updates not yet documented) | Leave uncommitted — not yours to commit |
| **Ticket-lane / skill / journal** | `.agents/team/tickets/**`, `.agents/skills/**`, `docs/journal/**` peer work | Leave uncommitted — ticket / skill / docs lane |
| **Generated / regenerable** | `package-lock.json` after a bump, sidecar `.a2ui.json`, `chunk-embeddings.json` after regen | Stage iff you ran the generator this turn |
| **Unknown** | Diff doesn't tell you intent | Ask the operator OR check the most recent commit message for clues OR check `.brain/notes/` for a peer prep note |

The decision is **per-file**, not per-directory. A peer might have modified `admin-shell.js` (release-relevant) AND `SKILL.md` (skill-lane) in the same turn — they get different verdicts.

---

## §Discipline 3 — Explicit allowlist staging

**Never** `git add -A` or `git add .` on a peer-dirty tree. The staging area is opaque without inspection; a peer may have left files staged from a prior partial workflow.

The defensive pattern:

```bash
# 1. Reset the staging area defensively.
git -C $REPO reset HEAD >/dev/null 2>&1

# 2. Stage the explicit allowlist by name.
git -C $REPO add \
  package-lock.json \
  packages/web-components/package.json \
  packages/web-components/CHANGELOG.md \
  packages/web-modules/package.json \
  packages/web-modules/CHANGELOG.md \
  packages/llm/package.json \
  packages/llm/CHANGELOG.md \
  packages/a2ui/compose/package.json \
  packages/a2ui/compose/CHANGELOG.md \
  packages/a2ui/corpus/package.json \
  packages/a2ui/corpus/CHANGELOG.md \
  packages/a2ui/mcp/package.json \
  packages/a2ui/mcp/CHANGELOG.md \
  packages/a2ui/retrieval/package.json \
  packages/a2ui/retrieval/CHANGELOG.md \
  packages/a2ui/runtime/package.json \
  packages/a2ui/runtime/CHANGELOG.md \
  packages/a2ui/validator/package.json \
  packages/a2ui/validator/CHANGELOG.md

# 3. Verify staged count matches the allowlist.
git -C $REPO diff --cached --stat | tail -3
# Expected: "19 files changed" for a pure-stub release; more if you
# also staged source files (test updates, etc.)

# 4. Confirm peer-in-flight files are NOT in the staged set.
git -C $REPO diff --cached --name-only | sort
# Eyeball — no surprises.
```

The memory `feedback_git_commit_targeted` records this rule as a "4th incident" — peer renames absorbed silently 4 times before the `git reset HEAD` defensive prefix became standard.

---

## §Discipline 4 — Stash workflow for strays

A stray = a peer-in-flight file that is:

1. Uncommitted,
2. Undocumented (no CHANGELOG entry covers it, no commit message explains it),
3. Would change behavior visible to consumers, AND
4. Contradicts an existing release-relevant artifact.

The canonical example: `admin-shell.tokens.css` `--page-content-header-bg` changed from `--a-canvas-1` to `--a-canvas-0` uncommitted, with the inline comment still describing `canvas-1`. Sat across v0.6.17/0.6.18/0.6.19 cycles. Resolved when the operator confirmed "keep canvas-0" in the v0.6.19→v0.6.20 boundary.

The stash workflow:

```bash
# 1. Stash the stray file(s) by name. Include a clear message so the
#    next operator (or you next turn) understands why.
git -C $REPO stash push <path1> <path2> \
  -m "vX.Y.Z-cycle: <stray reason> — parked during release"

# 2. Verify the working tree is sane.
git -C $REPO status --short
# Stashed files no longer appear as modified.

# 3. Do the full release (Steps 3–10 of cycle-happy-path.md).

# 4. Restore the stash AFTER the cycle ships.
git -C $REPO stash pop
# If "Dropped stash" prints, it applied cleanly.
# If "kept the stash" prints, there's a conflict — the working tree
# moved while you were releasing. Investigate before dropping.
```

**Always stash, never revert** unless the operator explicitly says "discard." Revert (`git checkout <file>`) destroys peer work; stash preserves it.

**Note the stash in the audit-history ledger** so the next operator can see what was excluded and why.

The 4 case studies in `assets/case-studies/` covering this discipline:

- `2026-05-21-stale-test-detection-v0.6.20.md` — peer changed CSS, didn't update test; deploy session updated the test (NOT stashed — fixed forward because the test was legitimately stale).
- `2026-05-21-feedback37-retraction-v0.6.21.md` — peer staged a revert of FEEDBACK-37 mid-cycle; stashed (would contradict the v0.6.20 CHANGELOG); the peer committed the revert post-publish for v0.6.21.
- `2026-05-20-version-skip-correction-v0.6.12.md` — peer mislabeled the cut v0.6.13; corrected 25 files across the release commit.
- (Phase 3) `2026-05-21-stash-pop-conflict-v0.6.20.md` — concurrent peer activity caused stash pop to keep-the-stash. Resolution: drop if the working tree has caught up (committed the same content); preserve if not. Never blind drop.

---

## §Pre-cut state classification flowchart

When you re-baseline at Step 1 and find a non-clean working tree, walk this in order. The output is "what mode" + "what to stash."

```text
Is there an unpushed release commit (`release(*): vX.Y.Z`)?
├── Yes, exactly one → Mode 3 (Deploy handoff) — peer pre-cut
│   └── Are there commits AFTER it?
│       ├── Yes, with CHANGELOG additions to [Unreleased] → §Boundary check
│       │   (see recovery-paths.md § [Unreleased] promotion, Phase 2 —
│       │    the v0.6.18 case: peer release commit fails check:demo-shells
│       │    because the demo-shell fix landed entangled with future work)
│       └── No → Mode 3 happy path; tag at HEAD
├── Yes, multiple → Mode 4 (Batch push)
│   (see recovery-paths.md § batch-push, Phase 2 — the v0.6.14+v0.6.15
│    case: publish in version order for npm latest)
└── No → Mode 2 (Author from scratch); promote [Unreleased] → [vX.Y.Z]

Is the working tree clean?
├── Yes → proceed with the determined mode.
└── No → classify per the §Discipline 2 taxonomy.
    For every file: Mine? Peer-release-relevant? Stray? Ticket-lane?
    Stash strays, leave ticket-lane alone, stage release-relevant.
```

---

## §The audit-history ledger contract

Every cycle's ledger (Step 11 of `cycle-happy-path.md`) includes a `notes` array. Entries about peer-in-flight handling go there. Standard phrasings:

```json
"notes": [
  "STRAY UNCOMMITTED CHANGE EXCLUDED: <file> — <one-line summary>. git-stashed during the release; restored to the working tree after. Flagged to operator.",
  "PEER-IN-FLIGHT EXCLUDED: <file> — <one-line summary>. v0.X.Y ships the committed state, NOT the peer's uncommitted change. The revert was restored post-release.",
  "Peer cycle activity: skill v2.X.Y / journal §NNN / ticket-lane grooming rode along on main inside the unpushed range — already committed by peers; not npm release artifacts.",
  "Concurrent peer modified <file> mid-cycle; was committed by the peer in <sha> as `<message>`. v0.X.Y absorbed / excluded per <reason>."
]
```

The ledger is the long-term memory of the peer-classification decision. Future cycles read past ledgers (Mode 8 — Phase 3 Investigation).

---

## §When this reference is "done v1"

- Every modified file in a release cycle classifies cleanly into one bucket from §Discipline 2 (zero "unknown" verdicts).
- Every stash command in the release uses the `vX.Y.Z-cycle:` prefix
  - a meaningful reason.
- Every audit-history ledger has at least one `notes` entry per excluded / stashed / peer-in-flight file.
- The §Pre-cut state classification flowchart correctly routes the next 3 cycles without operator override.
