# Local Codex project

Unzip the folder, open it as the project root in Codex, and start with AGENTS.md. Node 24 or newer is required. No npm install is needed: all scripts use Node built-ins. External fonts/icons require internet; the UI uses system-ui, captions IBM Plex Mono 400 and Phosphor via pinned CDN.

```sh
cd differential-forms-system
npm test
npm run build
npm run dev
```

Open http://localhost:4173. Stop the server with Ctrl-C. The server binds only to 127.0.0.1. Change PORT if needed. You may also open specimens/index.html directly. No account, deployment credential or Sites dependency is included.

## Suggested first Codex prompt
Read AGENTS.md and system.manifest.json. Run the existing tests and build. Treat this folder as the Differential Forms project. Before modifying a component, identify its semantic role, geometry family and parent context. Keep contracts, resolvers, specimen and verification aligned. Preserve the documented defaults and flag any production accessibility gaps separately.

## Ownership
- contracts/: canonical machine-readable design decisions; descriptive contracts, not formal JSON Schemas.
- geometry/: pure typed formulas; numerical tests exercise these modules.
- specimens/source.html: editable HTML/CSS/JS specimen; retains its own formula implementation.
- specimens/index.html: generated standalone preview, rebuild after source edits.
- scripts/: portable build and local server; no proprietary renderer dependencies.
- docs/ and recipes/: rationale, composition and implementation instructions.
- verification/: automated checks and manual UI cases. Tests do not certify accessibility.

The specimen and resolver library are not wired together at runtime. Formula changes must be reflected in both. The exported source was captured from published commit c703054bb5a20ea963fbf4d4da3cde9fc14149be. The local wrapper is rebuilt portably and is not byte-identical to the hosted wrapper.

Optional: initialize your own Git repository with `git init`, then commit the extracted files. This export does not include Git history, hosting IDs, credentials, personal Codex configuration or deployment automation.

When intentionally updating the source snapshot, refresh source.fragmentSHA256 in system.manifest.json and record the new provenance. The snapshot integrity test detects unrecorded changes.
