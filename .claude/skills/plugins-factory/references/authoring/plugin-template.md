---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Plugin template — copy-pasteable scaffolds

Copy what you need, delete what you don't. Every component dir is optional except the manifest — a plugin with `name` and one skill is valid. **The non-negotiables**: manifest-only in `.claude-plugin/`, all components at the ROOT, `./`-relative paths with no `..`, state in `${CLAUDE_PLUGIN_DATA}`. The §Layout-rule checklist at the bottom is the fast self-audit.

> Pair this with `creating-plugins.md` (the workflow) and `build-against-the-standard.md` (the gates). Validate with `python3 ${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py plugin <path>`.

---

## (a) Annotated directory layout

A plugin bundling every component type. **Note where the `.claude-plugin/` boundary sits**: only the manifest is inside it; everything the runtime *executes* is at the root.

```
my-plugin/                          # the plugin ROOT (this whole dir is copied into the cache on install)
├── .claude-plugin/
│   └── plugin.json                 # THE MANIFEST — the ONLY thing in here. `name` is the only required field.
│
├── skills/                         # ─┐
│   ├── audit-repo/                 #  │ model-auto-invoked knowledge / workflows
│   │   ├── SKILL.md                #  │ each skill = its own dir with a SKILL.md
│   │   └── references/             #  │ (progressive disclosure: SKILL.md is the TOC, depth here)
│   │       └── method.md           #  │
│   └── cut-release/                #  │
│       └── SKILL.md                # ─┘
│
├── commands/                       # ─┐ user-named explicit actions → /my-plugin:release
│   └── release.md                  # ─┘ (the file's frontmatter/name drives the slash command)
│
├── agents/                         # ─┐ context-isolation / parallel fan-out subagents
│   └── pr-reviewer.md              # ─┘ NOTE: plugin agents may NOT declare hooks/mcpServers/permissionMode
│
├── hooks/
│   └── hooks.json                  # must-run-on-event gates (lint/format/policy). A malformed file blocks the WHOLE plugin.
│
├── .mcp.json                       # external/stateful perimeter — intent-level tools, NOT a 1:1 API wrap
│
├── bin/                            # optional — executables that JOIN THE USER'S PATH on enable (trust surface, P9)
│   └── my-tool
│
├── output-styles/                  # optional — output style presets
├── themes/                         # optional — themes
├── monitors/                       # optional — monitors
├── settings.json                   # optional — plugin-scoped settings
│
├── CHANGELOG.md                    # version history (P8)
└── README.md                       # human-facing description (optional but recommended)

# referenced from a hook/script: ${CLAUDE_PLUGIN_ROOT}/bin/my-tool   (ephemeral cache path — read-only bundled assets)
# persistent state writes to:      ${CLAUDE_PLUGIN_DATA}/...          (survives updates — NEVER write state to the ROOT)
```

**Wrong** (the silent-failure layout): putting a component *inside* `.claude-plugin/`. `.claude-plugin/skills/...` does **not** load — the loader only reads the manifest there. Components live at the root.

---

## (b) `plugin.json` — annotated

Lives at `.claude-plugin/plugin.json`. JSON has no comments — the `//` lines below are annotation; **strip them** in the real file (or the validator rejects it).

```jsonc
{
  // REQUIRED — kebab-case, MUST match the plugin directory name. The only required field.
  "name": "my-plugin",

  // RECOMMENDED — semver. With it: updates trigger on a version bump.
  //               OMIT it entirely → the marketplace pins a new SHA per commit instead.
  //               Set the version in ONE place only — here OR the marketplace entry, never both.
  "version": "1.0.0",

  // RECOMMENDED — always-on routing surface (paid every session). Keep terse (P6/P7).
  "description": "Lint, format, and policy-gate every commit in this repo.",
  "keywords": ["lint", "format", "policy", "git", "ci"],

  "author": { "name": "Your Name", "email": "you@example.com" },
  "homepage": "https://example.com/my-plugin",
  "license": "MIT",

  // CROSS-PLUGIN DEPENDENCIES (P4) — the LEGAL way to share infra across the install boundary.
  // Names another plugin (installed alongside); NEVER a "../path". `~1.0.0` = compatible-with-1.0.
  "dependencies": [
    { "name": "core-types", "version": "~1.0.0" }
  ]

  // Component paths are auto-discovered from the ROOT (skills/, agents/, commands/, hooks/hooks.json, .mcp.json).
  // Only add explicit path fields to REPLACE a default location — rare, and it replaces rather than extends.
}
```

The minimal valid manifest is just:

```json
{ "name": "my-plugin" }
```

---

## (c) `.claude-plugin/marketplace.json` — two entries + a cross-plugin dependency

A marketplace's manifest. `name` (kebab) + `owner{name}` + a `plugins[]` array; each plugin needs `name` + `source`. This example shows a **foundation plugin** (`core-types`) and a **domain plugin** that depends on it.

```jsonc
{
  "name": "acme-tools",                       // REQUIRED — kebab-case marketplace id (not a reserved name)
  "owner": { "name": "Acme Engineering" },    // REQUIRED — owner identity

  "plugins": [
    {
      // FOUNDATION plugin — shared infra others depend on; depends on nothing itself.
      "name": "core-types",
      "source": "./plugins/core-types",       // ./-relative within the marketplace repo (or a git URL)
      "description": "Shared type registry for the Acme tool plugins.",
      "version": "1.0.0"                       // version may live here OR in the plugin's own plugin.json — ONE place.
    },
    {
      // DOMAIN plugin — declares the cross-plugin dependency the LEGAL way.
      "name": "repo-ops",
      "source": "./plugins/repo-ops",
      "description": "Lint, format, and policy-gate every commit in this repo.",
      "dependencies": [
        { "name": "core-types", "version": "~1.0.0" }   // installs core-types alongside — NOT a "../core-types" path
      ]
    }
  ]
}
```

`source` may be a `./`-relative path within the marketplace repo or a git URL. **Same-marketplace file sharing** (a single file across siblings) is done with a symlink inside the source tree — dereferenced/copied at install — never a `../` reference.

---

## (d) `hooks/hooks.json` — minimal, using `${CLAUDE_PLUGIN_ROOT}`

A hook guarantees execution on an event. Reference bundled scripts via `${CLAUDE_PLUGIN_ROOT}` (the ephemeral cache path to *this* plugin) so the path resolves wherever it's installed. **Document every hook's side-effect** (P9): does it mutate? block? on which events/matchers?

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/format.sh"
          }
        ]
      }
    ]
  }
}
```

Side-effect note for the above (keep one per hook in your README/CHANGELOG): *non-blocking; runs the formatter on the edited file after every `Edit`/`Write`; mutates the file in place; no network.* A **blocking** hook (one that can reject the action) is reserved for genuine policy gates — state that explicitly, because a silent blocking hook is a P9 finding. A malformed `hooks.json` blocks the **entire** plugin, so validate it.

---

## (e) §Layout-rule checklist — the fast self-audit

Run this before `validate_plugin.py`; it is the human-readable form of the P4/P5 gates.

- [ ] **Manifest-only in `.claude-plugin/`** — only `plugin.json` (and `marketplace.json` at a marketplace root). No `skills/`, `agents/`, `hooks/`, etc. inside it.
- [ ] **All components at the ROOT** — `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `bin/`, `output-styles/`, `themes/`, `monitors/`, `settings.json` are all root-level.
- [ ] **`./`-relative paths, no `..`** — every path the plugin references stays inside its own root. The install test: *does it resolve when the dir is copied alone into a version-keyed cache?*
- [ ] **No cross-plugin `../` or `$ref`** — shared infra is co-located, declared in `dependencies`, or symlinked within the same marketplace. (P4 — the break-on-install axis.)
- [ ] **State in `${CLAUDE_PLUGIN_DATA}`** — persistent writes go there; the ROOT is the ephemeral cache copy. Bundled read-only assets are referenced via `${CLAUDE_PLUGIN_ROOT}`.
- [ ] **`name` is kebab-case and matches the directory.** It's the only required manifest field.
- [ ] **`version` in exactly one place** — `plugin.json` *or* the marketplace entry, not both (omit both → SHA-per-commit).
- [ ] **No component inside a path that starts `.claude-plugin/`** — the single most common silent-load failure.
- [ ] **Every hook's side-effect documented; bundled agents declare no `hooks`/`mcpServers`/`permissionMode`.** (P9 + loader rule.)
