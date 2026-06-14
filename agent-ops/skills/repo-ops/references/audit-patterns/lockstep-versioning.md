---
date: 2026-05-06
---

# Lockstep versioning (Promise-4 trip-wire for monorepos)

**Added:** 2026-05-02 after the AdiaUI repo's caret-on-0.0.x lock-in postmortem (`a2ui-mcp@0.1.3 → corpus@0.0.6` shipped silently for ~4 days).

## The drift class

Monorepos with multiple published packages accumulate one of two versioning failure modes:

1. **Independent versions diverge silently.** Internal-dep ranges like `^0.0.x` lock to exact versions under npm pre-1.0 semver (`^0.0.6 = exactly 0.0.6`). Consumers track stale bundled versions while developers see `main`.
2. **Coordinated cuts have high friction.** Every change to any package requires bumping all packages, regenerating lockfiles, re-tagging, re-publishing. Operators skip the coordination → drift.

Both modes produce shipping bugs that are invisible until a consumer reports it (or, in the AdiaUI case, until a manual code review catches it).

## Detection (Promise-4 trip-wire)

The trip-wire is a CI gate that runs on every PR. Three checks:

1. **Version match:** all published packages share one version.
2. **Caret-trap:** no `@<scope>/*` dep range matches `^0\.0\.\d+`.
3. **Range alignment:** every internal `@<scope>/*` range is `^X.Y.0` matching the lockstep version.

Example implementation (AdiaUI repo, `scripts/release/check-lockstep.mjs`):

```js
const PACKAGES = [
  "packages/a2ui/compose/package.json",
  "packages/a2ui/corpus/package.json",
  // ... 8 total
];
const ADIA_DEP_RE = /^@adia-ai\//;
const CARET_0_0_X_RE = /^\^0\.0\.\d+$/;
const VALID_CARET_RE = /^\^(\d+)\.(\d+)\.0$/;

// Read all 8 package.jsons. Compare versions; flag mismatches.
// For each @adia-ai/* dep across all 8: flag if ^0.0.x; flag if ranges differ.
```

Wire to CI:

```yaml
# .github/workflows/docs-lint.yml (or sibling workflow)
lockstep-versioning:
  name: Lockstep version coherence
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
    - run: node scripts/release/check-lockstep.mjs
```

The `--fix` mode rewrites mismatched ranges to the highest version observed. Used during a coordinated cut to sync the rest of the tree.

## When to install

Install when the monorepo has **2+ published packages** AND at least one package has internal-dep ranges to siblings. The catastrophic failure mode is `^0.0.x` ranges + a popular consumer-facing package; the gate prevents both from coexisting.

The convention to write down (in the project's spec / docs):

- All N published packages share one version `X.Y.0` with Y≥1.
- Every internal dep range is `^X.Y.0` matching the lockstep version.
- Cuts are atomic: bumping one bumps all N.
- The CI gate fails any PR that misaligns.

For AdiaUI's specific implementation, see that repo's `docs/specs/package-architecture.md` § 15 (versioning policy).

## Prevention (post-publish admin)

Once the gate is installed and passing, the post-publish admin:

1. **Flip from `continue-on-error: true` to blocking.** Most cuts are added with the gate advisory (because the cut PR itself can't pass the gate — it's installing the gate against a misaligned repo). After the cut succeeds, flip to blocking.
2. **Add the gate to** `.agents/brain/findings/INDEX.md` Graduations.
3. **Cross-reference the postmortem** if the gate was prompted by an incident.

## Anti-patterns

- **Don't make the gate optional.** A `continue-on-error: true` gate is invisible to operators; the value is in the block.
- **Don't try to make the policy "just for some packages."** The caret-trap is a class — once you have the gate, sweep it across all internal deps. Partial enforcement is worse than no enforcement (operators trust the gate; misalignment in non-gated packages becomes a different shipping bug class).
- **Don't accept `^0.0.x` ranges with comments saying "we know."** Comments don't enforce; the gate does.

## Related

- See [`feedback_npm_caret_on_0_0_x.md`](`~/.claude/projects/<repo>/memory/`) — the user-memory entry (now flagged as superseded by the policy).
- See `.agents/brain/postmortems/2026-05-02-corpus-caret-lock.md` — the postmortem that drove the gate's authoring.
- See `lockstep-release` skill — the procedural counterpart for cuts.
