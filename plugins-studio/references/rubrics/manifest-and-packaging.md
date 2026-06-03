---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Manifest & Packaging Correctness — Does It Install and Update Cleanly?

The drill-down for holistic **P5**. A plugin is copied into a version-keyed cache and re-resolved through path variables; most packaging rules follow from that. This rubric scores whether the `plugin.json`, layout, path variables, versioning, and marketplace entry are correct — the difference between "validates" and "actually loads, persists, and updates."

Theory: `../foundations/plugin-architecture-foundations.md` (+ field reference `../plugin-architecture.md`). Primary critic: **David F.** (reproducible/idempotent packaging) with **Scott W.** (illegal layout unrepresentable) second.

---

## §The Problem

`claude plugin validate` passing tells you the JSON is well-formed. It does not tell you that a component sits inside `.claude-plugin/` and silently won't load, that state is written to the ephemeral root and vanishes on update, or that `version` is set in two places so users never receive the bump. These are the packaging failures that produce "it validates but it's broken" — and they're all mechanically checkable.

---

## §First Principles

1. **The layout is the contract; the manifest is a thin declaration.** Components auto-discover from fixed root locations — placement, not the manifest, decides what loads.
2. **`${CLAUDE_PLUGIN_ROOT}` is ephemeral; `${CLAUDE_PLUGIN_DATA}` is persistent.** Read-only bundled assets via ROOT; anything written goes to DATA.
3. **The version is the cache key.** Set it in exactly one place; choose semver or SHA mode deliberately.
4. **A malformed `hooks/hooks.json` blocks the whole plugin.** The blast radius of a JSON typo is the entire bundle.

---

## §The Rubric

### D1 — Manifest Validity `[gate]`

Is `plugin.json` valid: parseable, kebab `name`, semver `version`, correct field types?

| Score | Evidence |
|---|---|
| **5** | Valid JSON. `name` present, kebab-case, no spaces. `version` is semver. All recognized fields correctly typed. `description` + `CHANGELOG.md` present. `validate_plugin.py` reports no errors. |
| **4** | Valid + correctly typed; missing a nice-to-have (`keywords`, `author.email`). |
| **3** | Valid but `name` non-kebab (warning + Claude.ai sync rejects it), or `version` non-semver. |
| **2** | A recognized field is wrong-typed (e.g. `keywords` a string) — a hard load error. |
| **1** | Invalid JSON or missing required `name`. The plugin doesn't load. |

**Go deeper**: `../plugin-architecture.md` §1.
**Test**: `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py plugin <path>` — any ERROR on manifest validity = D1 fails.

---

### D2 — Layout Correctness `[gate]`

Are components at the plugin root, with only the manifest in `.claude-plugin/`?

| Score | Evidence |
|---|---|
| **5** | `.claude-plugin/` holds exactly `plugin.json`. All component dirs (`skills/`, `agents/`, `commands/`, `hooks/`, `.mcp.json`) at the plugin root. `hooks/hooks.json` well-formed. No instructions stranded in a root `CLAUDE.md` (which won't load). |
| **4** | Correct layout; a stray non-component file (a `README`) sits in `.claude-plugin/` harmlessly. |
| **3** | Layout correct but a root `CLAUDE.md` carries instructions that silently never load (should be a skill). |
| **2** | A real component (a skill/agent dir) sits inside `.claude-plugin/` and silently won't load — green validate, missing capability. |
| **1** | Most components misplaced; the plugin loads as a near-empty shell. |

**Go deeper**: `../foundations/plugin-architecture-foundations.md` §"Failure mode 1".
**Test**: is any file other than `plugin.json` inside `.claude-plugin/`? Is any component dir not at the root? Either = D2 ≤ 2.

---

### D3 — Path-Field Discipline `[gate]`

Are component paths `./`-relative with no `..`, and is replace-vs-extend handled correctly?

| Score | Evidence |
|---|---|
| **5** | All manifest component paths are `./`-relative with no `..`. Fields that *replace* the default (`commands`/`agents`/`outputStyles`/`themes`/`monitors`) list the default explicitly when extension was intended. |
| **4** | Paths legal; one replace-field used where the default dir is also wanted but happens not to exist yet. |
| **3** | Paths legal but a replace-field silently drops the default dir the author meant to keep. |
| **2** | A component path uses `..` (won't resolve post-install — also a P4 failure). |
| **1** | Multiple `..` paths or absolute machine paths in the manifest. |

**Go deeper**: `../foundations/plugin-architecture-foundations.md` §"Failure mode 4"; cross-check P4 (D1).
**Test**: `validate_plugin.py` flags any `..` in a component/`source` path. Then: does any replace-field unintentionally drop a default dir?

---

### D4 — Path-Variable Use `[gate]`

Are bundled scripts/assets referenced via `${CLAUDE_PLUGIN_ROOT}` (not hard-coded paths)?

| Score | Evidence |
|---|---|
| **5** | Every bundled script/binary/config referenced from a hook, MCP config, or agent uses `${CLAUDE_PLUGIN_ROOT}` (quoted in shell-form). No absolute machine path. No assumption about the install location. |
| **4** | ROOT used throughout; one shell-form reference is unquoted (works until a space in the path). |
| **3** | Mostly ROOT-relative; one hard-coded relative path that happens to work in the cache. |
| **2** | A bundled script is referenced by an absolute path that only resolves on the author's machine. |
| **1** | Hard-coded machine paths throughout; the plugin only runs where it was built. |

**Go deeper**: `../foundations/plugin-architecture-foundations.md` §"The Core Claim"; `../plugin-architecture.md` §3.
**Test**: grep hook/MCP/agent configs for absolute paths or bare relative script paths that should be `${CLAUDE_PLUGIN_ROOT}`-prefixed.

---

### D5 — Persistent-State Placement `[gate]`

Is anything *written* directed to `${CLAUDE_PLUGIN_DATA}`, never the ephemeral root?

| Score | Evidence |
|---|---|
| **5** | All persistent state (caches, venvs, `node_modules`, generated files, logs) is written under `${CLAUDE_PLUGIN_DATA}`. `${CLAUDE_PLUGIN_ROOT}` is treated as read-only. (If the plugin writes no state, N/A — score out.) |
| **4** | State in DATA; one transient temp write to the root that's recreated each run (no data loss, but untidy). |
| **3** | State in DATA but a cache lives in the root — works until the first update reaps it. |
| **2** | Meaningful state (a generated config, a DB) written to `${CLAUDE_PLUGIN_ROOT}`; lost on update. |
| **1** | All state in the root; every update wipes the plugin's memory. |

**Go deeper**: `../foundations/plugin-architecture-foundations.md` §"Failure mode 2".
**Test**: does any write target a path under `${CLAUDE_PLUGIN_ROOT}` (or the install dir)? Any persistent write there = D5 ≤ 2.

---

### D6 — Versioning Correctness `[review]`

Is `version` set in exactly one place, with a deliberate semver-or-SHA strategy and a CHANGELOG?

| Score | Evidence |
|---|---|
| **5** | `version` set in exactly one place (`plugin.json` *or* the marketplace entry, not both). Strategy is deliberate: explicit semver (bumped per release) or omit-for-SHA (every commit updates). `CHANGELOG.md` tracks releases. |
| **4** | Single-source version + changelog; strategy is fine but undocumented. |
| **3** | Version present but no changelog discipline, or the semver/SHA choice is accidental. |
| **2** | `version` set in **both** `plugin.json` and the marketplace entry — one silently wins; `/plugin update` may report "already latest" after a real change. |
| **1** | No version anywhere and no changelog; update behavior is undefined. |

**Go deeper**: `../foundations/plugin-architecture-foundations.md` §"Failure mode 3"; cross-check P8 (Evolution).
**Test**: is `version` set in two places? Is there a `CHANGELOG.md`? Two-place version = D6 ≤ 2.

---

### D7 — Marketplace Entry Validity `[review]`

If distributed via a marketplace, is the `marketplace.json` entry well-formed and legal?

| Score | Evidence |
|---|---|
| **5** | `marketplace.json`: kebab `name` (not reserved), `owner`, `plugins[]` each with `name` + a legal `source` (no `..`). `strict` mode chosen deliberately. Cross-marketplace dependencies whitelisted via `allowCrossMarketplaceDependenciesOn`. |
| **4** | Valid entry; missing an optional (`category`, `tags`, a `description`). |
| **3** | Valid but `strict` semantics misunderstood (relying on supplement behavior that the chosen mode doesn't give). |
| **2** | A `source` path contains `..`, or the marketplace `name` is reserved/non-kebab (sync rejects it). |
| **1** | Duplicate plugin names, invalid `source`, or a missing required marketplace field. |

**Go deeper**: `../foundations/plugin-architecture-foundations.md` §"The marketplace layer"; `../plugin-architecture.md` §4.
**Test**: `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py marketplace <path>` — any ERROR = D7 fails. (No marketplace = N/A.)

---

## §Anti-patterns

### AP-MP1 — The silently-missing component
**Symptom**: A skill/agent dir inside `.claude-plugin/` (D2 ✗). Validate passes; the component never loads. "My skill isn't firing" with a green check.
**Root cause**: Picturing "my files" instead of the auto-discovery-from-root contract.
**Correction**: `.claude-plugin/` holds only `plugin.json`; all components one level up.

### AP-MP2 — State in the ephemeral root
**Symptom**: A cache/config/venv written to `${CLAUDE_PLUGIN_ROOT}` (D5 ✗), lost on the first update.
**Root cause**: Treating the install dir as stable.
**Correction**: Read-only assets via ROOT; all writes to `${CLAUDE_PLUGIN_DATA}`.

### AP-MP3 — The version set twice
**Symptom**: `version` in both `plugin.json` and the marketplace entry (D6 ✗); users don't receive bumps; `/plugin update` says "already latest."
**Root cause**: Not knowing `plugin.json` wins silently.
**Correction**: One source of version truth; document the semver/SHA strategy.

### AP-MP4 — The hooks.json that took down the plugin
**Symptom**: A malformed `hooks/hooks.json` blocks the **entire** plugin from loading (D2 ✗), not just the hook.
**Root cause**: Underestimating the blast radius of a hooks JSON typo.
**Correction**: Validate `hooks/hooks.json` in CI; the whole-plugin blast radius makes it non-optional.

---

## §Hard Tests

1. **The validate test** (D1/D3/D7): `validate_plugin.py plugin <path>` (and `marketplace`) clean?
2. **The `.claude-plugin/` purity test** (D2): is anything but `plugin.json` in there? is any component not at the root?
3. **The root-write test** (D5): does any write target the ephemeral root instead of `${CLAUDE_PLUGIN_DATA}`?
4. **The double-version test** (D6): is `version` set in two places?
5. **The hooks-blast-radius test** (D2): is `hooks/hooks.json` well-formed (a typo blocks the whole plugin)?
