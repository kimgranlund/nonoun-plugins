# `cycle-happy-path.md` — the standard 12-step release cycle

> Loaded by **mode 1 (Cut & ship)** and **mode 3 (Deploy handoff)**. Cross-references: `multi-agent-baseline.md` (peer-in-flight classification), `gates-catalog.md` (pre-flight gate roster), `changelog-discipline.md` (F-N1 enrichment), `exe-deploy.md` (site deploy).

> **Worked example — the @adia-ai monorepo's 9-package lockstep.** The concrete gate names, the 9 package paths, the `ui-kit.exe.xyz` deploy, and the npm-workflow specifics below are **the worked example** of the portable release discipline, drawn from the @adia-ai (`@adia-ai/*`) lockstep monorepo. The DISCIPLINE generalizes to any @adia-ai-style lockstep monorepo (re-baseline → classify peer-in-flight → pre-flight gates → changelog promotion → bump → cut → tag → release trip-wire → push → publish → notes → ledger). When you cut a _different_ lockstep monorepo, keep the step skeleton and substitute its own package set, gate roster, and deploy target. `$REPO` below = the monorepo root.

This is the canonical 12-step happy-path cycle. It applies to any PATCH cut in a lockstep line, with two entry-point variants:

- **§Variant A — Deploy handoff** (mode 3): peer pre-cut the release commit + CHANGELOG + bump + lockfile. You re-baseline, verify, tag, push, publish.
- **§Variant B — Author from scratch** (mode 2): peer landed source changes under `## [Unreleased]` but did not bump or cut. You do the promotion, bump, lockfile, then re-enter the standard cycle.

Both variants converge at **Step 5 (Tag at HEAD)**.

---

## §The 12 steps

| Step | Action | Mutates? |
| --- | --- | --- |
| 1 | Re-baseline (git status + log + fetch + check for peer notes) | No |
| 2 | Classify peer-in-flight files; stash strays if needed | Yes (stash) |
| 3 | Run pre-flight gates | No |
| 4 | (Variant B only) Promote `[Unreleased]` → `[vX.Y.Z] — DATE`; bump; lockfile | Yes |
| 5 | Stage release allowlist; create release commit | Yes |
| 5.5 | Pre-commit verification trip-wire (re-verify staged state) | No |
| 6 | Tag umbrella `vX.Y.Z` + per-package tags at HEAD | Yes |
| 7 | Run the release trip-wire (F-N1, `check:release --all-pending`); enrich CHANGELOGs if warns | Yes if warns |
| 8 | Push `main` + all tags | Yes (push) |
| 9 | Dispatch the publish workflows; wait for completion | Yes (publish) |
| 10 | Create the GH releases; build + deploy site | Yes (deploy) |
| 11 | Write the audit-history ledger; commit + push | Yes |
| 12 | **Author release notes** (single-version via `notes-authoring.md`, or rollup if recent gap) and surface to operator for copy-paste | No |

---

## §Step 1 — Re-baseline (every turn)

The multi-agent baseline assumption is non-negotiable. Your context is stale at the start of every turn. Run these unconditionally:

```bash
git -C "$REPO" branch --show-current   # MUST be main
git -C "$REPO" status --short
git -C "$REPO" log --oneline -8
git -C "$REPO" fetch && git -C "$REPO" log HEAD..origin/main --oneline
```

> **`branch --show-current` MUST be `main` before cutting.** Peers in a shared clone sometimes check out local feature branches; the session "Current branch: main" snapshot is from the _prior_ session. Cutting on a feature branch silently breaks the push (stale `main` ref pushed, tags ahead of main). Full recovery: `multi-agent-baseline.md` § Wrong-branch recovery.

Also check:

```bash
# Current package versions (all should match — confirms lockstep state)
grep -h '"version"' packages/web-components/package.json \
  packages/web-modules/package.json packages/a2ui/validator/package.json

# Existing tags for this version (must NOT exist before this cycle)
git tag --list 'v0.X.Y' '*-v0.X.Y'

# Peer prep note?
ls -la .brain/notes/ | grep "v0.X.Y-release-prep"
```

Classify the situation. The triage table in `SKILL.md` § Where are you starting from is the routing input. If multiple unpushed `release(*): vN.M.X` commits exist, this is a **batch push** — bail out to mode 4 (`recovery-paths.md` § Scenario 2 — batch push).

---

## §Step 2 — Classify peer-in-flight files

`git status --short` will likely show files you didn't author. Apply the discipline in `multi-agent-baseline.md`:

- **Identify** every modified / untracked file.
- **Diff** any file whose intent you can't tell from filename.
- **Classify** each as: yours · peer-in-flight (release-relevant) · peer-in-flight (ticket lane / journal / skill — exclude) · unknown.
- **Stash** any file that's release-relevant but uncommitted + undocumented + contradicts the release CHANGELOG. (See the `admin-shell.tokens.css` saga in `multi-agent-baseline.md` § Discipline 4 as the canonical example.) The stash preserves the work for the peer; staging it silently is destructive.

The stash command pattern:

```bash
git -C "$REPO" stash push <file1> <file2> -m "vX.Y.Z-cycle: <reason> — parked"
```

Confirm working tree is now sane:

```bash
git -C "$REPO" status --short
```

After the cycle completes (Step 11+), `git stash pop` to restore the peer files. Note the stash in the audit-history ledger.

---

## §Step 3 — Pre-flight gates

### §Step 3.0 — Harvest preamble (when source content changed)

**Before running the gates,** check whether source content changed in the release window. If yes, regenerate downstream artifacts proactively — otherwise the freshness gates will catch the drift reactively (and force a tag-move recovery, see `../assets/case-studies/2026-05-23-freshness-gate-recovery-v0.6.32.md`).

Source-content signals that warrant a harvest preamble:

- `git diff <prev-tag>..HEAD --name-only` shows changes to:
  - `packages/web-components/components/**/*.yaml` or `*.a2ui.json`
  - `apps/**/*.contents.html` or `playgrounds/**/*.contents.html`
  - `catalog/**/*.contents.html` or `catalog/**/index.html`
  - `site/pages/**/*.html` with `data-chunk-*` annotations
- The release window contains a "status:stable sweep" / "anatomy sweep" / "data-property sweep" / "data-chunk-\* sweep" — all are yaml/HTML touches that propagate to the chunk corpus.

If any of those land, run the **four-deliverable preamble** — every output below must land in the release commit even when the same file paths are peer-in-flight in the working tree:

```bash
node scripts/build/components.mjs             # → catalog-a2ui_0_9.{json,_rules.txt} + per-component .a2ui.json sidecars
npm run harvest                               # full harvest (yaml + composition + chunks)
# or for chunk-only changes:
npm run harvest:chunks                        # site/pages + apps + playgrounds + catalog → chunk corpus
npm run build:embeddings:chunks               # embedding index (e.g. OpenAI text-embedding-3-small)
npm run build:bundles                         # dist/*.min.{css,js} (web-components + shells + everything)
```

Then stage the regenerated artifacts (full list — `packages/a2ui/corpus/chunks/`, `packages/a2ui/corpus/chunk-embeddings.json`, `packages/a2ui/corpus/catalog-a2ui_0_9.json`, `packages/a2ui/corpus/catalog-a2ui_0_9_rules.txt`, `packages/web-components/dist/`, `packages/web-modules/dist/`) into the release commit. Add a CHANGELOG note to `@adia-ai/a2ui-corpus [vX.Y.Z]` describing the regen.

**⚠️ Regen-output supersedes-WT contract** — the regen output **always** lands in the release commit, even when the same file paths are also peer-in-flight in the working tree. Peer's uncommitted catalog / chunk / bundle modifications are SUPERSEDED by the fresh regen. Stage the regenerated paths into the release-commit allowlist UNCONDITIONALLY (see §Step 5 allowlist convention below + §Step 5.5 verification trip-wire). Peer can rebase any divergent work on top of the release commit after the cycle. Canonical incident: `../assets/case-studies/2026-05-26-catalog-drift-recurring-v0.6.40.md`.

The preamble is OPTIONAL when the release window is purely docs/skills/CHANGELOG. Run the preamble freshness checks anyway — they're cheap and confirm nothing drifted.

### §Step 3.1 — The full gate roster

**Every gate in the roster MUST run. A selective subset = pre-flight failure.** This is a hard rule. A commit message claiming "verification: green" without enumerating the full roster is incomplete. The canonical failure: a release commit that ran 7 of the documented gates — `check:embeddings-fresh` failure surfaced 1d post-cut and required a tag-move recovery (see `../assets/case-studies/2026-05-23-freshness-gate-recovery-v0.6.32.md`).

The @adia-ai monorepo's roster (the worked example) is:

```bash
node scripts/build/components.mjs --verify    #  1. yaml ↔ .a2ui.json ↔ .d.ts coherence
npm run verify:traits                          #  2. trait coverage
npm run check:lockstep                         #  3. all packages at same version
npm run test:unit                              #  4. full vitest suite
npm run typecheck                              #  5. tsc --noEmit
npm run check:demo-shells                      #  6. demo .html imports cover composes:
npm run check:lightningcss-build               #  7. CSS files minify
npm run check:css-bundles-fresh                #  8. dist CSS bundles match source
npm run check:js-bundles-fresh                 #  9. dist JS bundles match source
npm run smoke:engines                          # 10. gen-UI engine smoke
npm run smoke:register-engine                  # 11. register-engine
npm run verify:corpus                          # 12. 0 errors (warnings carried forward)
npm run check:chunks-fresh                     # 13. corpus captured_at vs source fragments
npm run check:embeddings-fresh                 # 14. chunk-embeddings.json mtime vs chunks/_index.json
npm run check:links                            # 15. intra-repo link integrity
npm run eval:diff -- --engine zettel           # 16. cov ≥ 5%, avg ≥ 85 (floors)
npm run dogfood:status                         # 17. aggregate dogfood audits — exit-1 on P0/P1
```

Full gate roster + failure recovery: `gates-catalog.md`.

The dogfood-status gate is a thin aggregator over the component-authoring dogfood audits (itself composed into `npm run check`). The release-cut signal it gates is specifically the P0/P1 floor — P2/P3 findings are advisory and don't block the cut.

If `check:embeddings-fresh` FAILS — the corpus chunks changed but the embedding index didn't regenerate. **Run** `npm run build:embeddings:chunks`. Then add a note to the a2ui-corpus CHANGELOG `[vX.Y.Z]` entry about the regen. Canonical example: `../assets/case-studies/2026-05-20-corpus-drift-remediation-v0.6.15.md`.

If `check:css-bundles-fresh` FAILS — the source CSS changed but the rolled-up CDN bundles weren't regenerated. **Run** `npm run build:bundle-css`. Then re-stage `packages/web-components/dist/` + `packages/web-modules/dist/` into the release commit. The bundles ship as part of the tarball + serve via the CDN automatically. Consumers reach them via `@adia-ai/web-components/css/bundled` and `@adia-ai/web-modules/shell/admin-shell/bundled` (plus `chat/` / `editor/` / `simple/` variants).

If `check:js-bundles-fresh` FAILS — the source JS changed but the rolled-up CDN JS bundles weren't regenerated. **Run** `npm run build:bundle-js`. Then re-stage `packages/web-components/dist/` + `packages/web-modules/dist/` into the release commit. The bundler emits the JS entry points (web-components/index.js, the shells, and web-modules/index.js → everything.min.js). CDN consumers reach them via `@adia-ai/web-modules/everything` (kitchen-sink) or `@adia-ai/web-components/js/bundled` (primitives only). One bundle path per page — mixing causes `customElements.define` dup-name errors.

Shorthand: `npm run build:bundles` runs both CSS + JS together.

If `check:demo-shells` FAILS at a release-commit candidate — the new primitive's demos may not import a newly-added composes-dep. **Do not tag at that commit.** Either fix the demo .html files (Mode 2 path) or extend the release window to include the fix commit. Canonical example: `../assets/case-studies/2026-05-21-author-from-scratch-v0.6.18.md`.

---

## §Step 4 — (Variant B only) Promote, bump, lockfile

Skip if peer pre-cut the release commit (Variant A).

For **Variant B (author from scratch)**:

**4a. Promote `[Unreleased]` blocks to `[vX.Y.Z] — YYYY-MM-DD`.**

The Keep-a-Changelog discipline: every CHANGELOG that has `## [Unreleased]` content gets its heading renamed to `## [vX.Y.Z] — YYYY-MM-DD`. The content under it stays.

Across the packages, typically:

- 2–3 have substantive `[Unreleased]` content (web-components, web-modules, sometimes a2ui-corpus).
- The rest have nothing — author a stub block (see `../assets/templates/stub-changelog.template.md`).

For substantive packages with `[Unreleased]`: the heading swap is the simplest case (`## [Unreleased]` → `## [vX.Y.Z] — YYYY-MM-DD`); see `changelog-discipline.md` § Promotion for the exact text-edit pattern.

For packages with NO `[Unreleased]` block but with source changes (e.g. a2ui-corpus when only the catalog regenerated): **add a fresh `## [vX.Y.Z]` block** describing what generated content changed. Stale "no source changes" stubs on packages that DID change are an F-N1 diff-coverage warn waiting to happen.

For packages with NO source changes: insert the lockstep stub (`promote-unreleased.mjs` and `insert-stub.mjs` automate this).

**4b. Bump package versions.**

> **PATCH vs MINOR — operator convention.** MINOR (`0.X.0`) is reserved for **API-surface breaks ONLY**: a removed or renamed prop, attribute, slot, or component (cf. `stat-ui`→`stat` rename; avatar `name` + chart `aspect`/`heading` removed). **Everything else stays PATCH** — including _visible behavior changes_: default spacing/radius re-scaling, register changes, token-shadowing reverts with no public-API change, new opt-in features. A CHANGELOG bullet annotated `(MINOR behavior change)` is **descriptive prose, not a semver directive** — do NOT stop to surface it or bump MINOR for it. Only stop for an actual removed/renamed API symbol. Range bump (`^0.X.0`→`^0.Y.0`) happens on MINOR only — see §ReleaseInvariant 2 (PATCH-cut asymmetry).

Use `bump.mjs --from 0.X.Y --to 0.X.Z`. Note: `bump.mjs` bumps `"version"` fields only; on a **MINOR** cut the internal `@adia-ai/*` `^ranges` must be bumped separately (text-preserving regex on the `@adia-ai/*` dependency lines).

**4c. Regenerate the lockfile.**

```bash
npm install --package-lock-only --no-audit --no-fund
```

**4d. Confirm lockstep.**

```bash
npm run check:lockstep
# Expected: [lockstep] OK — all packages at 0.X.Z, all internal ranges at ^0.X.0
```

---

## §Step 5 — Stage and commit

**Defensive `git reset HEAD` before staging.** Per the multi-agent baseline (`multi-agent-baseline.md` § Discipline 3), the staging area may contain peer-staged files you don't know about.

```bash
git -C "$REPO" reset HEAD >/dev/null 2>&1
```

Then stage the **explicit allowlist** for the release commit:

- `package-lock.json`
- each `packages/*/package.json` (or `packages/a2ui/*/package.json`)
- each `packages/*/CHANGELOG.md` (or `packages/a2ui/*/CHANGELOG.md`)
- Any additional source files in scope (e.g. a test update that's part of the cycle's work)

**Allowlist convention — regen-deterministic outputs.** When source content changed in the release window (yaml / examples.html / contents.html with `data-chunk-*` / status:stable sweeps / Wave commits / anatomy sweeps) — i.e. any time §Step 3.0 ran — the allowlist MUST also include the following regen-deterministic outputs **UNCONDITIONALLY**, even when they're also peer-in-flight in WT:

- `packages/a2ui/corpus/catalog-a2ui_0_9.json`
- `packages/a2ui/corpus/catalog-a2ui_0_9_rules.txt`
- `packages/a2ui/corpus/chunk-embeddings.json`
- `packages/a2ui/corpus/chunks/` (if chunk content drifted)
- `packages/web-components/dist/web-components.min.{css,js}`
- `packages/web-components/dist/icons-manifest.js`
- `packages/web-modules/dist/everything.min.js`
- `packages/web-modules/dist/shell/admin-shell.min.js`
- `packages/web-modules/dist/icons-manifest.js`

These are regen-deterministic — your §Step 3.0 output is the authoritative state. Peer's WT pre-state on the same paths is SUPERSEDED. This is **not** "stage WT changes" (would violate multi-agent baseline). This is "stage the regen outputs you just produced in §Step 3.0 — they supersede any peer WT pre-state on the same paths." Canonical incident: `../assets/case-studies/2026-05-26-catalog-drift-recurring-v0.6.40.md`.

**Never `git add -A`.** Stage by name. Confirm the staged diff:

```bash
git -C "$REPO" diff --cached --stat | tail -3
# Expect: "N files changed, M insertions(+), L deletions(-)"
```

Commit (HEREDOC for multi-line):

```bash
git -C "$REPO" commit -m "$(cat <<'EOF'
chore(release): vX.Y.Z lockstep — <one-line summary>

N-package lockstep PATCH cut to X.Y.Z. Internal dep ranges hold at
^X.Y.0 (PATCH-cut asymmetry).

Substantive scope:
- @adia-ai/web-components: <bullet list>
- @adia-ai/web-modules: <bullet list>
- @adia-ai/a2ui-corpus: <bullet list>

Ride-along stubs (lockstep bump only): <package list>

Excluded — peer-agent in-flight (if any):
- <file path> (<reason>)

Verification:
- check:lockstep OK at X.Y.Z / ^X.Y.0
- NNNN/NNNN vitest across NN files
- ... (paste the gate summary)
EOF
)"
```

---

## §Step 5.5 — Pre-commit verification trip-wire

After `git add` (§Step 5) but **BEFORE** `git commit`, re-run the freshness gates one final time against the staged state. This catches the case where a regen-deterministic output was excluded from the allowlist (same-paths-as-peer-WT exclusion conflict — see §Step 3.0 supersedes-WT contract).

```bash
node scripts/build/components.mjs --verify    # catalog + sidecar drift?
npm run check:chunks-fresh                     # chunks/_index vs source fragments
npm run check:embeddings-fresh                 # chunk-embeddings.json vs chunks/_index
```

**Any DRIFT here means a regen output was excluded from staging.** Recovery is in-cycle (no force-push, no tag-move):

```bash
git -C "$REPO" add <drift-paths>               # stage the missing regen output
# Re-run §Step 5.5 → expect clean
# Then re-create the commit (HEREDOC again — same body works).
```

The trip-wire runs in <2 seconds locally vs ~5 minutes to recover from a CI failure (regen + commit follow-up + force-move tags + re-dispatch). Pure win. Canonical incident: `../assets/case-studies/2026-05-26-catalog-drift-recurring-v0.6.40.md`.

If §Step 5.5 fails: rewind to a pre-commit state, re-stage, re-commit. Do **not** proceed to §Step 6 (tag) with drift — the tag-at-HEAD invariant means CI will hit the drift after publish, not before.

---

## §Step 6 — Tag

One umbrella tag + one per-package tag at the release-commit HEAD:

```bash
git -C "$REPO" tag vX.Y.Z
for pkg in web-components web-modules llm a2ui-runtime a2ui-compose \
           a2ui-corpus a2ui-mcp a2ui-retrieval a2ui-validator; do
  git -C "$REPO" tag "$pkg-vX.Y.Z"
done
```

(`tag-lockstep.mjs --version X.Y.Z` mechanizes this loop.)

**Tag-at-HEAD invariant** (`SKILL.md` § ReleaseInvariants #3): post-bump fixes, tests, README updates belong in the tarball. The release window's last commit is the tag point.

Exception: **batch push** (mode 4). Each version tags at its own release-commit SHA. See `recovery-paths.md` § Scenario 2 — batch push.

---

## §Step 7 — The release trip-wire (F-N1)

```bash
node scripts/release/check-release.mjs --all-pending
```

Expected for a clean cycle:

```text
│  ✓ clean  (× the per-package tags)
│  ✗ [error] tag 'vX.Y.Z' doesn't match <pkg>-v<version>  (umbrella — EXPECTED, ignore)
```

If you see **warns** of the form:

```text
⚠ [warn] diff 'packages/web-components/components/' touched between
  web-components-v0.X.Y-1 → web-components-v0.X.Y but CHANGELOG [0.X.Y]
  doesn't mention 'components'
```

This is the **F-N1 diff-coverage enrichment pass**. The change is documented but the CHANGELOG entry didn't use the literal path keyword the regex expects. Fix: add the path keyword naturally to a relevant entry (e.g., change "`table.yaml`" → "`components/table/table.yaml`"). Then **amend the release commit** (it's yours, unpushed, and the enrichment belongs in the same commit conceptually):

```bash
git -C "$REPO" add packages/<pkg>/CHANGELOG.md
git -C "$REPO" commit --amend --no-edit

# Re-tag (the SHA moved): delete all tags, then re-create them.
node scripts/release/check-release.mjs --all-pending   # re-run; expect per-package clean
```

See `changelog-discipline.md` § F-N1 enrichment for the full discipline + the worked example (`../assets/case-studies/2026-05-21-fn1-enrichment-pass-v0.6.19.md`).

---

## §Step 8 — Push

```bash
echo "commits to push: $(git -C "$REPO" rev-list --count origin/main..HEAD)"
git -C "$REPO" push origin main 2>&1 | tail -3
```

Then the tags:

```bash
git -C "$REPO" push origin vX.Y.Z \
  web-components-vX.Y.Z web-modules-vX.Y.Z llm-vX.Y.Z \
  a2ui-runtime-vX.Y.Z a2ui-compose-vX.Y.Z a2ui-corpus-vX.Y.Z \
  a2ui-mcp-vX.Y.Z a2ui-retrieval-vX.Y.Z a2ui-validator-vX.Y.Z \
  2>&1 | grep -c 'new tag'
```

---

## §Step 9 — Publish

The repo's `publish-<pkg>.yml` workflows only auto-trigger on per-package tag push sometimes. **Always dispatch manually** to be safe:

```bash
sleep 4  # let the CI host index the new tags
for pkg in web-components web-modules llm a2ui-runtime a2ui-compose \
           a2ui-corpus a2ui-mcp a2ui-retrieval a2ui-validator; do
  gh workflow run "publish-$pkg.yml" --ref "$pkg-vX.Y.Z" 2>&1 | head -1
  echo "  dispatched: $pkg"
done
```

(`dispatch-publish.mjs --version X.Y.Z` mechanizes this loop, and its `--after <prev-version>` flag enforces the batch-push ordering rule. The npm scope it checks defaults to `@adia-ai`; a fork overrides it with `--scope <@org>` or `$ADIA_NPM_SCOPE`.)

Wait for completion (use `run_in_background`):

```bash
until [ "$(gh run list --workflow=publish-a2ui-validator.yml \
  --limit 1 --json status -q '.[0].status')" = "completed" ]; do
  sleep 5
done
echo "vX.Y.Z publishes settled"
```

Verify all succeeded, then confirm npm:

```bash
for pkg in web-components web-modules llm a2ui-runtime a2ui-compose \
           a2ui-corpus a2ui-mcp a2ui-retrieval a2ui-validator; do
  echo -n "$pkg: "; npm view "@adia-ai/$pkg" version 2>/dev/null
done
echo -n "latest: "; npm view @adia-ai/web-components dist-tags.latest 2>/dev/null
```

All should print `X.Y.Z`. `latest` should be `X.Y.Z`.

**Batch-push exception**: dispatch the older version's workflows + WAIT for completion + verify, THEN dispatch the newer version's. Otherwise `npm dist-tag latest` lands on the older version. See `recovery-paths.md` § Scenario 2 — batch push.

---

## §Step 10 — GH releases + site deploy

GH releases (use the `.brain/release-notes/{version}-release-notes.md` body — see `notes-authoring.md` for the template; strip the YAML frontmatter before passing as the GH-release body):

```bash
# Frontmatter-stripped body for the GH release:
sed '1{/^---$/!q;};1,/^---$/d' .brain/release-notes/X.Y.Z-release-notes.md > /tmp/gh-body-X.Y.Z.md
for pkg in web-components web-modules llm a2ui-runtime a2ui-compose \
           a2ui-corpus a2ui-mcp a2ui-retrieval a2ui-validator; do
  gh release create "$pkg-vX.Y.Z" \
    --title "@adia-ai/$pkg vX.Y.Z" \
    --notes-file /tmp/gh-body-X.Y.Z.md \
    2>&1 | tail -1
done
```

Then site build + deploy (see `exe-deploy.md` for the @adia-ai monorepo's deploy specifics — the `ui-kit.exe.xyz` host is the worked example; a different lockstep monorepo substitutes its own demo-site host):

```bash
npm run build:site 2>&1 | tail -2
# rsync to the demo host + verify; see exe-deploy.md for the FILES-not-routes
# verification discipline (an SPA returns 200 for unmatched routes).
```

If any peer-in-flight file was stashed in Step 2, **keep it stashed** through this step. The site build runs from the working tree; the deployed site should match this version's npm packages exactly.

---

## §Step 11 — Audit-history ledger

Write `.brain/audit-history/YYYY-MM-DD-release-vX.Y.Z.json` (`make-ledger.mjs` scaffolds it from git state; see `ledger-discipline.md` for the canonical schema). Minimum fields:

```json
{
  "kind": "release-cut",
  "audit_id": "YYYY-MM-DD-release-vX.Y.Z",
  "released_at": "YYYY-MM-DD",
  "version": "X.Y.Z",
  "release_type": "PATCH",
  "summary": "<one-paragraph>",
  "release_commit": "<sha>",
  "tag_commit": "<sha>",
  "tags": ["vX.Y.Z", "web-components-vX.Y.Z", "..."],
  "verification": { "...": "gate-by-gate summary" },
  "publish_workflows": { "dispatched": "N/N", "conclusions": "N/N success" },
  "notes": ["<lesson>", "<excluded peer file>", "<F-N1 enrichment if any>"]
}
```

Commit + push the ledger:

```bash
git -C "$REPO" add .brain/audit-history/YYYY-MM-DD-release-vX.Y.Z.json
git -C "$REPO" commit -m "chore(audit-history): vX.Y.Z release ledger ..."
git -C "$REPO" push origin main
```

If anything was stashed in Step 2, `git stash pop` now and **flag any that returned with conflicts** to the operator.

---

## §Step 12 — Author release notes (default, not optional)

After the cycle ships clean (npm publish + site deploy + ledger committed), **always** author release notes for the operator. The operator does not need to ask. This is the default end-of-cycle behavior.

**Single-version cut** (most cycles) → load `notes-authoring.md`:

- One body covering this version's substantive packages, FEEDBACK closures, behavior changes, and verification baseline.
- **Save to `.brain/release-notes/{version}-release-notes.md`** (durable repo artifact, committed with the ledger) — NOT `/tmp`, and NOT `.brain/notes/` (that's working notes; `release-notes/` is the ship record). Open with YAML frontmatter (see `notes-authoring.md` § Where to put the notes). The Slack/GH-release body is derived from this file, not the reverse.
- Surface inline in the operator's terminal as well — they may want to paste without opening the file.

**Rollup** (when ≥2 versions have shipped since the last operator- acknowledged notes broadcast, or when the operator says "rollup notes" / "v0.6.X → v0.6.Y notes") → load `rollup-notes.md`:

- One body using the 5-section skeleton + framing option A/B/C.
- **Save to `.brain/release-notes/{lo}-to-{hi}-rollup-notes.md`** with the same frontmatter convention.

**Surfacing convention**: present the notes inline at the end of the cycle report ("the cycle shipped clean; here are the notes for copy-paste:"). The operator copies wherever they want (Slack #releases, GH release body, internal announcement). The skill does NOT post to Slack directly — that's operator-mediated.

**Skip-condition (rare)**: skip Step 12 only if the operator explicitly says "no notes this cycle" / "skip notes" / "I'll write them myself." Even then, surface a one-line summary so they have a starting point.

**Why this is a default, not a prompt**: cycle context is freshest at end-of-cycle; the notes draft compounds with the audit-history ledger. Asking the operator "do you want notes?" creates friction they consistently answer "yes" to — so the skill answers it.

---

## §Variant A (Deploy handoff) shortcut

If the peer pre-cut the release commit + CHANGELOG + bump + lockfile already:

1. Re-baseline (Step 1) — confirm HEAD is the peer's `release(*): vX.Y.Z` commit.
2. Skim the peer's prep note at `.brain/notes/vX.Y.Z-release-prep-*.md`.
3. Stash peer-in-flight strays per Step 2.
4. Run pre-flight (Step 3) — confirm gates clean.
5. **Skip Step 4** (the peer did the promotion + bump + lockfile).
6. **Skip Step 5** (the peer's release commit IS the commit to tag).
7. Resume at Step 6 (Tag at HEAD).

---

## §When to abort

Stop and surface the situation to the operator if:

- Pre-flight gate fails AND the failure mode doesn't fit a documented recovery in `gates-catalog.md`.
- F-N1 reports more than 1 warn per per-package tag, or any non-umbrella error.
- The peer's release-commit candidate fails `check:demo-shells` / `check:lockstep` / `check:embeddings-fresh` (see `recovery-paths.md` § Scenario 4 — author-from-scratch / extension).
- The working tree has uncommitted source files with unclear provenance after diffing (see `multi-agent-baseline.md` § Discipline 4 — stash discipline).
- Publish workflow fails with E404 / E401 — npm-token rotation required.

Do NOT improvise past these — the operator owns the judgment call.
