# Vendored kernel — do not edit here

These files are vendored **byte-identical** from `harness-forge/bin/` and kept in sync by the
repo-root **`tools/sync-dev-kernel.py`** (the catalog convention, alongside `sync-corpus-reader.py` /
`sync-host-detect.py`; CI runs `--check`). Per build-plan decision **D-A**, dev-factory does **not**
re-implement the lattice machine — it vendors harness-forge's proven, selftested kernel and operates
it against `.agents/dev-factory/` via the `--dir` flag. This keeps harness-forge a single source of
truth and an untouched, standalone plugin.

**Pinned source:** harness-forge `0.5.12` (re-vendored 2026-06-15: `validate.py` honest-maturity reporting [DF-6]; 0.5.11 added the **`kernel_version` stamping**
cross-over improvement — `lattice.save()` now stamps the writing version into `lattice.json`, `produced_by`
reads `LATTICE_PRODUCED_BY` so dev-factory labels its own instances, and `lattice.kernel_compat()` gives the
server a boot-time version handshake). `KERNEL_VERSION` stays **0.5.2** — the additions are backward-compatible
(a new optional field + a helper + a defaulted env read), not a contract break. Re-run the sync tool after any
upstream change and update this pin. **Note (own-marketplace scope):** the sync tool lives at the
parent repo's `tools/`; if dev-factory is published as a standalone marketplace, the tool + a CI
workflow that runs `--check` must travel with it (else the drift gate is asserted, not enforced).

| Vendored file | Source | Role |
|---|---|---|
| `lattice.py` | `harness-forge/bin/lattice.py` | THE lattice kernel — the 8-state maturity machine (`TRANSITIONS`), `scan`/`rank`/`validity`/`advance`, staleness-as-graph, `scaffold`, the run-budget + loop-marker bound machinery. |
| `validate.py` | `harness-forge/bin/validate.py` | the validation path — runs a verifier, mints the Signal from its **exit status**, advances `instantiated → validated` only on pass. Imports `lattice` as a sibling (hence both live in `bin/`, not a subdir). |
| `schemas/cell.schema.json` | `harness-forge/schemas/cell.schema.json` | the **cell contract** the vendored `lattice.py check()` validates cell keys/enums against — dev-factory **adopts** harness-forge's cell schema rather than forking it, so the kernel and the reverse-morphism R4 proof stand on the same contract. (Lives under `schemas/`, not `bin/`; the third file the sync tool pins.) |

**Never edit these here.** Fix upstream in harness-forge, then run `python3 tools/sync-dev-kernel.py`.
A drifted copy fails `sync-dev-kernel.py --check` in CI.

Everything dev-factory-specific — the ticket lifecycle machine, the four protective gates + two
lifecycle predicates, the coordination ledger vocab, dispatch, the server, the autonomy tiers — is
**native** dev-kernel code that *calls*
this vendored kernel, never a fork of it. If dev-factory ever needs a kernel behavior the vendored
files don't expose, the fix is an upstream change to harness-forge (a justified cross-over
improvement), re-vendored — not a local edit.
