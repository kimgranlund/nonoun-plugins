# `exe-deploy.md` — site build + deploy + version-verify

> Loaded by mode 1 Step 10. Long-running VM ops (provision, restart, key rotation, etc.) are a **separate ops concern** — out of scope for this skill and not shipped in this plugin. This file is the release-cycle's deploy tenant only: site build → rsync → verify.

> **Worked example — the @adia-ai monorepo's demo-site deploy.** The concrete host (`ui-kit.exe.xyz`, a shared Linux VM on exe.dev), the `rsync … :/srv/adia-ui/dist/` target, and the SPA-route trap below are **the worked example** drawn from the @adia-ai monorepo. They are NOT universal. The portable DISCIPLINE is: (1) build the site from the working tree, (2) stash peer-in-flight strays before deploy so the deployed site matches the just-published packages, (3) verify deployed **files** (not SPA routes — see the trap below), (4) restore the stash after. Substitute your monorepo's own demo-site host + transport.

The @adia-ai demo site is served from `ui-kit.exe.xyz` (a shared Linux VM on exe.dev). Every release cycle ends with a site deploy so the live demos reflect the just-shipped npm packages.

The site is a **living HEAD demo**, not version-pinned. It tracks main

- the working tree's demo HTML. This is by design — readers expect the demos to evolve.

---

## §The 3-step deploy

### Step 1 — Build the site locally

```bash
npm run build:site 2>&1 | tail -2
# Expected: "done — NNNNN files, NN.N MB, NNNNms"
```

`scripts/build/site.mjs` is the site builder. It:

- Copies `site/`, `apps/`, `playgrounds/`, `catalog/` into `dist/`
- Generates per-component reference pages from yaml
- Copies the 9 `@adia-ai/*` packages' `dist/` into `dist/packages/`
- Symlinks `node_modules/@adia-ai/*` for bare-specifier resolution
- Copies CodeMirror 6 runtime, 2 third-party root deps + 4 transitive
- Injects importmap into 268+ HTML files

If `build:site` fails, **stop** — don't deploy. Common failure:

- A `<script>` reference to a non-existent file (often a demo .html referencing a primitive whose path moved).
- A symlink resolution failure (run `npm install` in the worktree if this is a fresh checkout — see `feedback_worktree_node_modules_silent_glob`).

### Step 2 — Stash strays before deploy

**Critical**: the site build runs from the WORKING TREE, not from a git tag. If you have stashed peer-in-flight files at Step 2 of the cycle (per `multi-agent-baseline.md` § Discipline 4), KEEP THEM STASHED through the deploy. The deployed site should match v0.X.Y's npm packages exactly — peer-in-flight uncommitted files would leak.

If any uncommitted source files appeared mid-cycle (concurrent peer activity), classify them per `multi-agent-baseline.md` § Discipline 2 BEFORE deploying. Decision:

- **Release-relevant + matches CHANGELOG** — could include (rare; peer finished documenting just-in-time)
- **Release-relevant + contradicts CHANGELOG** — STASH; deploy without
- **Future-release work** — STASH; deploy without
- **Ticket-lane / skill / journal** — they don't affect the site build's output materially, leave or stash per taste

When in doubt, stash. The deploy then reflects pure committed state.

### Step 3 — Rsync to EXE + verify

> **⚠️ curl-200 on a `/site/<route>` path proves NOTHING (v0.7.4 incident).** The docs site is a **client-side-routed SPA**: the server returns the same ~5 KB `index.html` shell (`<title>AdiaUI Docs</title>`) for **every** path with HTTP 200, then `site.js` renders `#router` from `site/sitemap.json`. An **unmatched** route renders **blank** — still 200. In v0.7.4 the deploy-verify (and the release notes) cited `https://ui-kit.exe.xyz/site/gen-ui/` and `/site/components/theme-panel` — **neither is a sitemap route** — got 200, and reported "renders". Both were blank. The real routes are `/site/playground/gen-ui`, `/site/examples/gen-ui-feed`, `/site/components/<slug>`. **Verify deployed FILES, not SPA routes**, per below.

```bash
rsync -az --delete "$REPO/dist/" \
  ui-kit.exe.xyz:/srv/adia-ui/dist/ 2>&1 | tail -1

# (a) Service up + build deployed — curl a CONTENT FILE (returns its OWN
#     bytes, not the SPA shell). A 404 here is a REAL deploy failure.
curl -s -o /dev/null -w "host.css: HTTP %{http_code}\n" \
  https://ui-kit.exe.xyz/packages/web-components/styles/host.css   # expect 200

# (b) A demo/content artifact for THIS cycle — assert REAL content, not the
#     5 KB "AdiaUI Docs" shell. grep a string only the real file contains:
curl -s https://ui-kit.exe.xyz/apps/genui/app/gen-ui/gen-ui.html \
  | grep -q "Gen UI Canvas" && echo "gen-ui content OK" || echo "gen-ui MISSING"
```

**Verify checklist (FILES, not routes):**

- HTTP 200 on a deployed **asset** (`/packages/web-components/styles/host.css`) — confirms the rsync landed + the service serves files.
- The cycle's substantive change has its **content file** deployed with real bytes (grep a unique string; size ≠ ~5 KB shell):
  - Component changed? `…/packages/web-components/components/<name>/<name>.html`
  - Module/shell changed? `…/packages/web-modules/<cluster>/<name>/<name>.html`
  - Standalone docs page? Its `content:` source from sitemap.json, e.g. `…/apps/genui/app/gen-ui/gen-ui.html`
- To cite a **docs route** (in notes or to the operator), it MUST exist in `site/sitemap.json` (`grep '"path": "/site/…"'`) **and** its `content:` / standalone source must be deployed. A route absent from the sitemap renders blank.
- **For true render proof** (not just "file deployed"), run a headless probe — `scripts/qa/*-probe.mjs` — that asserts `#router` has children + 0 console errors. curl can't see client-side render.

If any HTTP returns non-200, **don't panic** — the deploy might be mid-replication. Wait 30 seconds and re-curl. If still failing, check:

1. Did `rsync` actually transfer? Re-run the rsync; look at the transfer count in the output.
2. Is the demo-site service up? `curl -I https://ui-kit.exe.xyz/` should return 200. If not, the VM itself is down — that's a long-running-ops concern (separate from this skill; out of scope).
3. Is the new path missing from `dist/`? `find dist/<path>` should list the file. If not — `build:site` didn't generate it (the gen-UI new-primitive case — site/sitemap.json may need an entry; see `feedback_build_site_dist_gap_after_package_change`).

---

## §Site build invariants

These hold across every cycle:

1. **`dist/site/sitemap.json`** is the live demo manifest. The site home page reads it; entries with missing files render as 404.
2. **`dist/node_modules/@adia-ai/*`** are symlinks to `dist/packages/*`. The importmap depends on them.
3. **HTML files get the importmap injected** at build time (~268 files in the current site). Skipped: files that already have one, or files without `<head>`.
4. **CodeMirror 6 runtime ships with `<code-ui>`** — copied to `dist/packages/web-components/components/code/` (12 files, ~555 KB min).
5. **`dist/` is reproducible** — running `npm run build:site` twice should produce identical output (modulo timestamps).

---

## §EXE deploy invariants

These are EXE-specific concerns:

1. **The remote target is `ui-kit.exe.xyz:/srv/adia-ui/dist/`** for the @adia-ai monorepo — wired into nginx vhost config on the VM, so don't change it for that deploy. The host is the worked-example default; `release-pack.mjs` exposes it as `--host <deploy-host>` (or `$ADIA_DEPLOY_HOST`), defaulting to `ui-kit.exe.xyz`, so a forked lockstep monorepo can point rsync + the curl verify at its own demo host without editing the script.
2. **`rsync -az --delete`** is the canonical command. The `--delete` flag removes files on the remote that aren't in the local `dist/`. This is what keeps stale demos from accumulating.
3. **SSH access** is operator-owned (kimba's SSH key). The skill doesn't manage credentials.
4. **HTTPS termination** is handled by exe.dev; the VM serves HTTP. Trust the cert chain.
5. **For per-package CLI version verification** — the v0.6.7 `bin/` added `adia-ui-doc` CLI; for cycles that touch `packages/<pkg>/bin/`, verify the published CLI works after deploy:

   ```bash
   npx @adia-ai/web-components@X.Y.Z adia-ui-doc <component>
   ```

---

## §When deploy is NOT clean

If `build:site` fails or `rsync` errors or `curl` returns non-200:

1. **Don't immediately re-deploy** — diagnose first.
2. The v0.X.Y release is ALREADY SHIPPED to npm at this point (the deploy runs after publish in Step 10). The site lag is recoverable; the npm publishes aren't.
3. Common recovery paths:
   - **Site build error** — fix the source issue (often a typo in a demo .html or a missing primitive registration), re-build, re-deploy.
   - **rsync hung / SSH refused** — VM rebooting? Check `https://ui-kit.exe.xyz/` directly; if up, retry rsync. If down, the VM is a long-running-ops concern (separate from this skill; out of scope).
   - **HTTP 404 on a new path** — `sitemap.json` may not have the new entry, OR the build's file-copy missed a per-package path (memory: `feedback_build_site_dist_gap_after_package_change`).
4. Log the deploy issue in the ledger's `notes` array even if the release shipped to npm successfully.

---

## §Stash restoration AFTER deploy

If you stashed files at the start of the cycle (Step 2) OR mid-cycle (post-publish, pre-deploy), restore them after the deploy completes:

```bash
git -C $REPO stash pop 2>&1 | tail -3
```

If `pop` reports "Dropped stash@{0}" — clean restore, you're done.

If it reports "kept the stash" — there's a conflict. The working tree moved while you were releasing (typically a concurrent peer made changes). Investigate per `recovery-paths.md` § Scenario 6 (concurrent peer mid-cycle).

---

## §When this reference is "done v1"

- Every cycle's site deploy completes with a single HTTP 200 verify
  - (optional) demo-route verify.
- Stash discipline is followed across cycles — the deployed site matches the v0.X.Y tag's tree, modulo intentional living-HEAD demo updates.
- Deploy failures route through this file's "When deploy is NOT clean" decision tree without operator improvisation.
