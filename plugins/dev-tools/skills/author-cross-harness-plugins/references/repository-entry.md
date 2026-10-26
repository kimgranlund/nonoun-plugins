# Repository entry files

Treat repository instructions as a cross-harness surface distinct from a plugin
manifest. They route work inside a checkout; they do not install or activate a
plugin. Inspect the repository's existing convention before changing it.

## Default cross-host pattern

For a new repository that targets both Claude Code and Codex:

1. Put shared project authority in root `AGENTS.md`.
2. Make root `CLAUDE.md` a thin Claude entry that imports the shared authority:

   ```markdown
   @AGENTS.md
   ```

3. Put only genuine Claude-specific additions after the import. Do not restate
   shared build commands, ownership, constraints, architecture, or completion
   rules in both files.
4. Keep repository-local skills canonical in one declared source tree. Generate
   thin host discovery adapters rather than copying workflow bodies.

This is a default, not permission to replace an established repository contract.
If a repository already declares another canonical file or import chain, preserve
that authority unless the maintainer authorizes migration. Record the resulting
precedence and ensure every host reaches the same essential behavior.

## Imports and precedence

- Resolve imports relative to the file containing them.
- Do not create circular imports (`CLAUDE.md` → `AGENTS.md` → `CLAUDE.md`) or
  chains that depend on a user's home directory.
- Prefer one direct shared import over nested mirrors. Markdown links provide
  navigation; do not assume a link loads instructions.
- Read nested instruction files that apply to the edited subtree. A nearer file
  may refine the root contract; it must not silently erase safety or ownership
  boundaries without an explicit repository rule.
- User/global instructions and settings are host configuration, not portable
  repository content. Never copy secrets, personal paths, or permission overrides
  into tracked entry files.
- `.claude/settings.local.json` and similar state remain untracked. Commit portable
  entry files, adapters, manifests, and deterministic generators deliberately.

Host versions change. Verify import syntax and discovery against supported hosts.
When a newer host discovers the shared file natively, a harmless thin entry may
remain for older supported versions; document the compatibility reason.

## Repository skills and packaged plugins

Repository maintenance skills and consumer plugins have different audiences. A
repo-local authoring skill may be discoverable through `.claude/skills` or another
host adapter without becoming a shipped plugin member. Use explicit plugin
membership; do not package every repository skill by directory scan.

An adapter owns discovery metadata and host path mechanics. The canonical skill
owns behavior and references. Adapter generation preserves supported policy fields,
rejects unmapped metadata instead of dropping it, and fails on stale or unowned
adapters.

## Verification

Check the repository view another machine receives:

1. Confirm `CLAUDE.md`, `AGENTS.md`, intended adapters, and generators are tracked.
2. Inspect `git show <candidate>:<path>` or a detached archive/worktree; a dirty
   primary checkout is not evidence of clone contents.
3. Resolve every import and canonical-skill reference inside that frozen candidate.
4. Run deterministic adapter checks and target-host structural validation.
5. Use fresh top-level host sessions for routing/loading evidence when required,
   following [evidence-contract.md](evidence-contract.md).

Do not claim fresh-clone support from a session that loaded untracked adapters from
the primary checkout. A worktree may isolate writes while discovery still consults
the original session root or global catalog.
