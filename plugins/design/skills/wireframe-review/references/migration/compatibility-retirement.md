# Compatibility retirement plan

Status: scoped, no compatibility paths removed. Base UI is the editable authority; old review paths remain generated views.

The 2026-10-11 current-source scan inventories 117 mirrors; 50 have exact-path references in non-mirror review sources. The other 67 are not proven unused: relative imports, dynamic asset paths, explicit --root consumers and external/frozen callers are outside that search. Evidence: ../../resources/reports/canonical-catalog-publication-2026-10-11/compatibility-inventory.json.

## Ordered checklist

- [x] Move editable UI source, standalone UI checks and catalog extraction to base-ui.
- [x] Make the review catalog consume the locked kit API; preserve canonical publication and source provenance.
- [x] Inventory exact-path consumers without scanning or rewriting historical evidence.
- [ ] Migrate maintained runtime/build readers to the kit API or an explicit owner-aware source resolver. Include snippets, fixtures, source inspectors and asset copying; relative/dynamic imports require review beyond text matches.
- [ ] Replace generation-time full mirror validation with an explicit compatibility-release check only after no live generation reader depends on mirrors. Retain kit integrity and exact lock validation.
- [ ] Run a bounded clean-context consumption test for standalone base-ui and review generation/revision with mirrors absent in a disposable copy. Include missing/incompatible-kit controls; do not alter frozen evaluations or the sealed holdout.
- [ ] Decide the compatibility support window. Forwarding CLI commands, mirrored source files and generated review runtime adapters are different surfaces; do not remove the adapter merely because UI source moves.
- [ ] Remove one proved-unused group from ui-compatibility.json, resync and run its affected readers. Require equivalent output and intentional failure for unsupported legacy calls.
- [ ] Publish a compatible pair with removal notes, exact package parity and rollback archives. Retain historical evidence unchanged.

No new browser certification is implied. Existing component evidence can be reused when specimen/runtime/style bytes are unchanged. Canonical sheet publication and compatibility retirement remain separate operations.
