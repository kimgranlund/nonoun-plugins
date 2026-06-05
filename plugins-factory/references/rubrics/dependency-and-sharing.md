---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Dependency & Shared-Infra Legality — Does It Resolve After Install?

The drill-down for holistic **P4** — the library make-or-break. An installed plugin is copied into a version-keyed cache and cannot reach outside its own directory, so every shared resource must be resolved legally or the plugin ships dangling references on first install. This rubric scores whether sharing is legal and whether anything dead is bundled.

Theory: `../foundations/dependency-and-sharing-foundations.md`. Primary critic: **Scott W.** (make the illegal layout unrepresentable) with **Simon W.** (cross-boundary references are attack surface) second.

---

## §The Problem

A plugin can be perfect on disk and broken on install. `claude plugin validate` checks the JSON; it does not check that a `$ref`, an include, or a script path resolves _after the directory is copied, alone, into the cache_. The author who develops against a monorepo — where `../core-types/schemas/foo.json` resolves locally — ships a plugin that dangles for every user. This rubric exists because the most dangerous path is the one that works in development and fails in production.

---

## §First Principles

1. **The install test is the only test that matters here.** For every referenced path: does it resolve after copy-into-cache, alone? If no → illegal.
2. **There are exactly three legal sharing mechanisms**: co-locate, declare a `dependencies` edge, symlink within the marketplace. The raw `../` path is the illegal fourth that tempts because it works locally.
3. **Dead weight is a dependency defect too.** A pointer to a retired/renamed/never-read component is a dangling reference of the opposite kind — to a corpse inside the plugin.
4. **Share what changes in lockstep; duplicate the rest.** Coupling cost can exceed duplication cost (ESLint's lesson).

---

## §The Rubric

### D1 — Install-Path Legality `[gate]`

Does every referenced path resolve after the plugin is copied alone into a version-keyed cache?

| Score | Evidence |
| --- | --- |
| **5** | Zero `../`-traversal paths outside the plugin root. Zero cross-plugin `$ref`s. Every script path, include, and reference resolves within the plugin's own directory (or via a legal mechanism below). The install test passes for every path. |
| **4** | All component paths legal; one reference uses an absolute path that happens to resolve but should be `${CLAUDE_PLUGIN_ROOT}`-relative. |
| **3** | Paths resolve, but one leans on a co-located copy that should be a declared dependency — fragile, not yet broken. |
| **2** | A `$ref`, include, or script path reaches a sibling plugin via `../` — resolves in the repo, **breaks in the cache**. |
| **1** | Multiple `../` cross-plugin paths; shared infra assumed to "just be there." Dangling references on first install. |

**Go deeper**: `foundations/dependency-and-sharing-foundations.md` §"The Core Claim"; `manifest-and-packaging.md` (path-field rules). **Test** (install test): for every path the plugin references, ask "does this resolve after the directory is copied alone into a version-keyed cache?" Any `../` outside the root or cross-plugin `$ref` = D1 fails.

---

### D2 — Shared-Infra Resolution Mechanism `[gate]` `[review]`

Is each shared resource resolved by co-location, a `dependencies` edge, or a same-marketplace symlink — appropriately?

| Score | Evidence |
| --- | --- |
| **5** | Every shared resource (types, knowledge, a sibling skill, a template) is resolved by exactly one of the three legal mechanisms, and the mechanism fits the resource shape (small/coupled → co-locate; whole-plugin → `dependencies`; file-bytes → symlink). |
| **4** | All sharing is legal; one item uses a heavier mechanism than ideal (a `dependencies` edge where co-location would be simpler). |
| **3** | Sharing is legal but the mechanism is mismatched (co-locating a large corpus that three plugins need, causing triple duplication). |
| **2** | One shared resource has no legal mechanism — it relies on filesystem adjacency that won't survive install. |
| **1** | Sharing is ad-hoc filesystem reach-across throughout; no mechanism declared. |

**Go deeper**: `foundations/dependency-and-sharing-foundations.md` §"The three legal mechanisms" + §"The decision among the three". **Test**: for each shared item, name its mechanism (co-locate / `dependencies` / symlink). Any item whose answer is "it's just in a sibling dir" = D2 ≤ 2.

---

### D3 — Co-location Discipline `[review]`

Is co-located shared infra placed at its tightest consumer, without needless duplication?

| Score | Evidence |
| --- | --- |
| **5** | Co-located resources sit with their dominant consumer (the tightest/hottest coupling). Duplication is deliberate and bounded; nothing is co-located in three places that should be one declared dependency. |
| **4** | Sensible co-location; one resource duplicated across two plugins where a shared edge would be marginally cleaner. |
| **3** | Co-location works but placement is arbitrary (the registry lives with a light consumer, not the hot one), or duplication is creeping. |
| **2** | The same large resource is co-located (copied) into several plugins, each now drifting independently. |
| **1** | No placement logic; shared resources scattered and duplicated with no owner. |

**Go deeper**: `foundations/dependency-and-sharing-foundations.md` §"Co-location" + §"When not to share at all". **Test**: for each co-located shared resource, is it placed at its dominant consumer, and is it duplicated more than twice? >2 copies of a lockstep-changing resource = D3 ≤ 2.

---

### D4 — `dependencies` Completeness & Versioning `[review]`

Are declared dependencies real, version-constrained, and (cross-marketplace) whitelisted?

| Score | Evidence |
| --- | --- |
| **5** | Every `dependencies` entry names a real plugin with a semver constraint where stability matters. Cross-marketplace deps are covered by `allowCrossMarketplaceDependenciesOn`. An undeclared "always co-installed" assumption does not exist — if the plugin needs a sibling, it says so. |
| **4** | Dependencies declared and real; one missing a version constraint where it would help. |
| **3** | Dependencies mostly declared; one "assumed present" sibling is undeclared (a fragment dependency hiding as an assumption). |
| **2** | A cross-marketplace dependency without the whitelist (install-time failure waiting), or a declared dep naming a plugin that doesn't exist. |
| **1** | The plugin silently requires other plugins with nothing declared. |

**Go deeper**: `foundations/dependency-and-sharing-foundations.md` §"Marketplace-level cross-dependencies"; cross-check P3 (a hidden dependency is also a fragmentation smell). **Test**: does the plugin function standalone? If not, is every required sibling in `dependencies` (with a version where it matters)? Any undeclared requirement = D4 ≤ 3.

---

### D5 — No Dead Weight Bundled `[gate]`

Is every bundled component and internal pointer live and correct — nothing retired, renamed, or never-read?

| Score | Evidence |
| --- | --- |
| **5** | Every bundled component is live and used. No retired/renamed component shipped. No internal pointer (`peer_skills`, a reference path, a `files[]` entry) names a corpse. No reference file Claude never reads. |
| **4** | All components live; one reference file is rarely accessed but not wrong. |
| **3** | A bundled component is stale/duplicative (an old + new version of the same thing), or a `files[]` entry lags disk. |
| **2** | A retired/renamed component is bundled, or an internal pointer names something that no longer exists. |
| **1** | Multiple dead components + dangling internal pointers shipped — the bundle is partly archaeology. |

**Go deeper**: `foundations/dependency-and-sharing-foundations.md` §"Dead weight is a dependency problem too". **Test** (dead-weight grep): grep the bundle for retired/renamed component names; verify every internal pointer (`peer_skills`, reference paths, `files[]`) resolves to a live file. Any corpse = D5 fails.

---

### D6 — Symlink Hygiene `[review]`

Do symlinks (if any) stay within the marketplace so they're dereferenced at install?

| Score | Evidence |
| --- | --- |
| **5** | Any symlink used for sharing targets a file _within the same marketplace_ (so it is dereferenced/copied at install). No symlink points outside the marketplace (which would be skipped for security, leaving a broken link). |
| **4** | Symlinks are in-marketplace and resolve; one is to a path that's valid but fragile (deep into another plugin's internals). |
| **3** | Symlinks work but the sharing they enable would be cleaner as a `dependencies` edge. |
| **2** | A symlink targets outside the marketplace — skipped at install, leaving a dangling link. |
| **1** | Symlinks point at absolute machine paths or outside the marketplace throughout. |

**Go deeper**: `foundations/dependency-and-sharing-foundations.md` §"Same-marketplace symlinks". **Test**: for each symlink, is its target inside the same marketplace? Any outside-target symlink = D6 ≤ 2. (No symlinks = N/A.)

---

## §Anti-patterns

### AP-DL1 — The broken-on-install shared dep

**Symptom**: Clean in the repo, broken after `/plugin install` — a `../shared-types` path or cross-plugin `$ref` doesn't resolve in the cache (D1 ✗). **Root cause**: Designing against the monorepo layout, not the installed-cache layout. **Correction**: Co-locate, declare in `dependencies`, or symlink within the marketplace. Run the install test on every path.

### AP-DL2 — The hidden sibling requirement

**Symptom**: The plugin only works when a specific sibling is also enabled, but nothing is declared (D4 ✗) — also a fragmentation smell (P3). **Root cause**: A fragment shipped as if standalone. **Correction**: Declare the `dependencies` edge, or merge the fragment back into one coherent plugin.

### AP-DL3 — The corpse in the bundle

**Symptom**: A retired/renamed component or a dangling `peer_skills`/reference pointer ships inside the plugin (D5 ✗). **Root cause**: No dead-weight pass before packaging. **Correction**: Grep for retired names; verify every internal pointer resolves to a live file.

### AP-DL4 — The triplicated registry

**Symptom**: The same large shared resource is co-located (copied) into three plugins, now drifting independently (D3 ✗). **Root cause**: Co-location used where a single `dependencies` edge or marketplace symlink belonged. **Correction**: Promote lockstep-changing shared infra to one declared edge; keep co-location for small, single-consumer resources.

---

## §Hard Tests

1. **The install test** (D1): every referenced path resolves after copy-alone-into-cache? Any `../` outside root or cross-plugin `$ref` = a break.
2. **The mechanism test** (D2): every shared item names co-locate / `dependencies` / symlink? "It's just in a sibling dir" = illegal.
3. **The standalone test** (D4): does the plugin function alone? If not, is every required sibling declared?
4. **The dead-weight grep** (D5): any retired/renamed component bundled? any internal pointer to a corpse?
5. **The symlink-target test** (D6): every symlink target inside the same marketplace?
