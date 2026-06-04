---
date: 2026-04-29
coverage: canonical
peers:
  - harvest-repo-brain.md
  - cold-start-harvest.md
  - continuous-learning-loop.md
status: research-verified
---

# Import repo-ops harvest (consume a portable bundle into this brain)

> **The premise.** Some other repo ran `harvest repo-ops --export` and produced a portable bundle. **`import repo-ops harvest`** ingests that bundle into _this_ repo's `.brain/` tree, then syncs the new content into the agent's memory at `~/.claude/projects/<this-repo>/memory/` so the next session catches everything immediately.

This recipe is invoked by phrases like:

- "import repo-ops harvest"
- "use repo-ops to import"
- "ingest brain bundle"
- "import bundle from `<path>`"
- "merge another repo's brain into this one"

The inverse of [`harvest-repo-brain.md`](./harvest-repo-brain.md). One produces; the other consumes. Together they let institutional memory move between repos without touching source code.

## What gets imported

The bundle's `manifest.json` declares disposition per artifact. The importer respects it:

| Bundle artifact | Target | Collision rule |
| --- | --- | --- |
| `bundle/adrs/NNNN-*.md` | `.brain/adrs/` | Renumber on collision (next free `NNNN`); preserve original number in body as `Originally: 0007 (source-repo)` |
| `bundle/postmortems/YYYY-MM-DD-*.md` | `.brain/postmortems/` | Date prefix is unique enough; on exact-match append `-imported` to filename |
| `bundle/postmortems/_TEMPLATE.md` | `.brain/postmortems/_TEMPLATE.md` | If absent in target, install. If present, diff and prompt — don't auto-overwrite |
| `bundle/runbooks-portable/*.md` | `.brain/runbooks/` | Same diff-and-prompt rule |
| `bundle/conventions-portable/*.md` | `docs/conventions/` | Same — never auto-overwrite |
| `bundle/findings-schema.json` | (use to validate `.brain/findings/INDEX.md`) | If target has no `INDEX.md`, install one with the imported schema |
| `bundle/audit-history-schema.json` | (use to validate `.brain/audit-history/`) | First imported audit lands in the same shape as the source |
| `bundle/config.toml.example` | `.brain/config.toml` | If target has no config, install with imported defaults; otherwise diff-and-prompt |
| `bundle/agents-template.md` | (use to verify target `AGENTS.md` has parallel sections) | Read-only — informs the gap report |

## What does NOT get imported

- Source files, configs, package files (the bundle should never include these; if it does, refuse to import)
- Anything in `bundle/audit-history/` content — only the _schema_. Each repo's audit ledger is its own.
- Anything matching the secret-pattern redactor (defense in depth — the source should have stripped these, but verify)

## Procedure

User-confirmation gates marked **[gate]**.

1. **[gate] Locate the bundle.** Default path: `../brain-export-*-*/`. The user can pass an explicit path. If multiple bundles match, prompt for selection.

2. **Validate the bundle.**
   - `manifest.json` parses
   - Every `disposition: "portable"` claim has a corresponding file
   - Bundle size < 5 MB (refuse to import larger — likely contains junk)
   - No file matches secret patterns (refuse on hit)
   - No absolute user paths in any text file (warn-and-strip)

3. **Detect target's brain layout.**
   - `.brain/` exists? Use it.
   - Only legacy `docs/{adrs,postmortems,...}/` exists? Recommend running base `repo-ops` to migrate to `.brain/` first; abort import unless user forces.
   - Neither exists? Recommend `greenfield-setup.md`; abort.

4. **Plan the merges.** For each bundle artifact, compute:
   - Target path
   - Collision: none / rename / diff-and-prompt
   - Renumber map (for ADRs)

5. **[gate] Show the merge plan.** Render as a table; let the user veto per-row. Default interactive; allow `--yes` for bulk import.

6. **Apply the plan.**
   - Copy ADRs (with renumbering as planned)
   - Copy postmortems (with `-imported` suffix on date collisions)
   - Diff-prompt each runbook and convention; user picks accept / reject / merge-manually
   - Install schemas + config.toml if absent

7. **Update local INDEX files.**
   - `.brain/adrs/README.md` (if present): refresh the index to include imported ADRs with a `(imported from <source-repo>)` annotation
   - `.brain/postmortems/INDEX.md`: same
   - `.brain/findings/INDEX.md`: keep target's findings, but add an `Imported from <source>` section if the source had `## Graduations` content worth preserving

8. **Run a fresh audit.** Invoke the parent `repo-ops` audit on the freshly-imported state. The ledger entry will record the import as the audit's source event.

9. **Sync to agent memory.** Pipeline: the imported ADRs / postmortems / conventions feed the harvest pass from [`harvest-repo-brain.md`](./harvest-repo-brain.md). User can opt out (`--no-memory-sync`) but default is to run it — the import is most useful when it propagates all the way to the agent's working memory.

10. **Sync the harness if recommended.** Re-run the harness audit step from `harvest-repo-brain.md`: any pre-commit hooks the source had that aren't installed locally, propose them; any `permissions.allow` entries the source needed for its runbooks, propose them.

11. **[gate] Approve harness changes.** Settings updates always require explicit confirmation — even with `--yes`.

12. **Report.** Print a summary:

    ```text
    Imported brain-export-source-repo-2026-04-29/ (manifest v1.0, 412 KB):
      ✓ 7 ADRs copied (5 renumbered to 0011-0017; 2 already present, skipped)
      ✓ 1 postmortem copied
      ✓ _TEMPLATE.md updated (your version was older, accepted import)
      ✓ 2 runbooks (1 accepted, 1 rejected — bumped to /tmp/ for review)
      ✓ 3 conventions (3 accepted)
      ✓ Schemas installed (findings-schema, audit-history-schema)

    Memory sync (via harvest-repo-brain pipeline):
      ✓ 7 project_  (from imported ADRs)
      ✓ 4 feedback_ (from imported postmortem + 3 conventions)
      MEMORY.md: 32 → 43 lines.

    Harness recommendations:
      ✓ pre-commit hook for "verify journal-date" (proposed; user approved)
      ✓ permissions.allow += ["Bash(npm run verify:*)"] (proposed; user approved)

    Audit run:
      ✓ Trip-wires green; ledger entry written to .brain/audit-history/2026-04-29-import-source.json
    ```

## Sanity checks

Refuse to import if any of these fail:

- [ ] Bundle's `manifest.json` is missing or invalid
- [ ] Bundle contains files outside the declared dispositions
- [ ] Bundle contains absolute user paths or matches secret patterns (defense in depth)
- [ ] Bundle size > 5 MB
- [ ] Target has uncommitted changes in `.brain/` (require clean tree to make rollback safe)
- [ ] Target's git branch isn't main / a dedicated import branch (refuse to import on a release branch)

Always require **explicit user confirmation** for:

- Overwriting existing ADR / postmortem / convention content (default: skip on collision)
- Settings.json modifications (default: prompt)
- Adding pre-commit hooks (default: prompt — hooks are powerful)
- Auto-syncing to agent memory (default: prompt; opt-out flag)

## Rollback

The import never touches anything outside `.brain/` + `docs/conventions/` + `~/.claude/projects/<repo>/memory/` + `.claude/settings.json`. To roll back:

```bash
git checkout -- .brain/ docs/conventions/ .claude/settings.json
# memory files are user-scope; restore from a backup if needed
```

The audit-history ledger entry that records the import is **not** rolled back — it's append-only. The next audit will show the import was reverted; that's the audit trail working as intended.

## When to NOT import

- Two repos with truly divergent architectures (a Vue 3 SaaS vs an Elixir CLI). The ADRs won't translate; the postmortems won't translate; you'll spend more time triaging than the import saves.
- The source bundle is older than 90 days. Brain matter ages — better to ask the source repo to re-harvest fresh.
- The target repo is mid-incident. Import lands cleanly only against a steady-state target.

## See also

- [`harvest-repo-brain.md`](./harvest-repo-brain.md) — the producing-side recipe; this is its inverse
- [`cold-start-harvest.md`](./cold-start-harvest.md) — different flow (extracts buried learnings from an existing repo's scattered docs into the brain layout for the first time)
- [`continuous-learning-loop.md`](./continuous-learning-loop.md) — the broader iterate pattern import-then-audit instantiates
- [`../audit-patterns/audit-history-ledger.md`](../audit-patterns/audit-history-ledger.md) — privacy redactor reference (defense-in-depth on the import)
