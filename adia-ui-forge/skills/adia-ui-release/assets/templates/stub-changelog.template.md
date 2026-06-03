<!--
Lockstep stub block — for a ride-along package with no source changes
in this release. The substantive description points at the relevant
@adia-ai/* package whose CHANGELOG carries the headline.

Variables (replace before use):
  $VERSION       — the version being cut (e.g. 0.6.21)
  $DATE          — release date in YYYY-MM-DD
  $SUBSTANTIVE   — one-sentence summary of the substantive work and
                   where it shipped, with the cross-reference path.

Example invocation:
  node scripts/insert-stub.mjs --version 0.6.21 --date 2026-05-21 \
    --substantive "table-ui truncate-default (§403) and FEEDBACK-37 retraction in @adia-ai/web-modules" \
    --xref "packages/web-modules/CHANGELOG.md#0621--2026-05-21"
-->

## [$VERSION] — $DATE

### Maintenance

- **Lockstep version bump only.** No source changes in this package; bumped to maintain the 9-package version coherence enforced by `scripts/release/check-lockstep.mjs`. Substantive v$VERSION work shipped in $SUBSTANTIVE. See `$XREF` for details.
