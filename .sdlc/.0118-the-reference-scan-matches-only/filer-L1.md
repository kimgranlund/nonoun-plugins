<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0118: Reference scan also catches relative and absolute paths to a renamed ticket folder

## PR body
### Summary
In numbered mode, `tickets.py close` and `tickets.py archive` rename `NNNN-<slug>` to `.NNNN-<slug>`. Until now their reference scan matched only the literal toplevel-relative `<rel>/<slug>`. A citation written relative to the citing file, such as `../0003-x/filer-L1.md` or `./0003-x/handoff.md`, was missed and broke silently on rename. The scan now finds these references and, with `--rewrite-refs`, rewrites them. Follow-up from T-0113.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `outside_refs` still runs one `git grep`, now on the folder name `<slug>`. A hit file is kept if it has the literal `<rel>/<slug>` (the old rule, unchanged) or a path token that resolves to the folder. A token can resolve when read relative to the citing file, toplevel-relative, or absolute.
  - A token must contain a `/`, so a bare `0003-x` word is not a reference.
  - New `TOKEN_RE` and `ref_tokens` hold the token matcher and the resolution check.
  - `rewrite_files` does the old byte replace, then rewrites only the `<slug>` component of each resolving token to `.<slug>`. The token keeps its form: relative stays relative, absolute stays absolute. Its signature and both callers are unchanged.
  - Docstrings of `outside_refs`, `rewrite_files` and `cmd_close` are updated.
  - New selftest cases sit after the existing `(u) refs` and `archive refs` blocks. They cover `../` from another ticket folder, `./` from the ticket root, and absolute paths, for both close and archive. Each is refused without `--rewrite-refs`, listed by `--dry-run --rewrite-refs`, and rewritten with it. Negative controls cover a bare `0003-x` word, `other/0003-x/handoff.md`, and `../0003-x/` written from `docs/`.
- Docs describe the widened scan and its limits (no case folding, symlink resolution, `~` expansion or self-reference handling): the `close` and `archive` help text in `tickets.py`, the `tickets.py` Layout entry in `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, and `plugins/sdlc-lite/skills/ticket/SKILL.md`.

Unchanged: refusal text, `rewrite <file>` dry-run lines, the `; rewrote refs in ...` suffix, CLI flags, and "every refusal writes nothing".

### Verification
Both steps have a verifier verdict of pass.
- Step 1 (verifier L2):
  - `tickets.py selftest` prints `tickets selftest: PASS`.
  - The six shell criteria (close refusal, `--rewrite-refs` keeping the relative form, archive dry-run listing, `./` link rewrite, absolute guard, negative-control guard) exit 0.
  - Red before, green after: in a detached worktree at HEAD with the old `outside_refs` and `rewrite_files` swapped back in, the selftest fails on exactly 12 new `../` and `./` cases. No existing case or negative control fails there.
  - The verifier mutated the matcher twice: dropping the `/` requirement, and matching any token whose component equals the slug. Both made the negative controls go red.
  - The diff for the two existing selftest blocks contains only added lines.
  - `check.sh` was run.
- Step 2 (verifier L1):
  - The phrase "relative to the citing file" is present in `CLAUDE.md`, `tickets.py` and `sdlc-lite-author.md`. It is absent at HEAD, so the check bites.
  - `selftest` passes.
  - `check.sh` exits 0.
  - Added lines contain 0 em dashes.

### Notes for reviewers
- The absolute-path cases are guards, not red-first tests. The old literal `<rel>/<slug>` rule already caught absolute paths that contain it, so they pass at HEAD too.
- For absolute tokens the builder added `os.path.realpath`, so a macOS `/var` path matches `/private/var`. The handoff says "no symlink resolution beyond `os.path.normpath`"; the verifier judged this a widening of absolute matching that no criterion forbids. The docs still say symlink resolution is not handled.
- The literal substring rule is kept per the Constraints, so two false positives remain. Another tree's `.../.sdlc/0003-x` still counts, and `.sdlc/0003-xy` still matches `.sdlc/0003-x` as a prefix.
- The `close` and `archive` help lines still say `--rewrite-refs` rewrites `<rel>/<slug>` to `<rel>/.<slug>`, with no "keeping their form" wording. The sentence just before each gives the precise rule.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py close` and `archive` (numbered mode) now detect references to a ticket folder written relative to the citing file (`../0003-x/`, `./0003-x/handoff.md`) as well as absolute and toplevel-relative paths. `--rewrite-refs` rewrites them and keeps each reference's form.

## Follow-ups
- The reference scan still treats another tree's `.sdlc/0003-x` as a reference, and `.sdlc/0003-xy` as a match for `0003-x`. The literal-substring rule was kept per the T-0118 Constraints, which contradicts the Deltas rule that a path resolving elsewhere is not a reference.
