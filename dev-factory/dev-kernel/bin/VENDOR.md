# Vendored kernel — do not edit here

These files are vendored **byte-identical** from `harness-forge/bin/` and kept in sync by
`tools/sync-dev-kernel.py` (CI runs `--check`). Per build-plan decision **D-A**, dev-factory does
**not** re-implement the lattice machine — it vendors harness-forge's proven, selftested, CI-gated
kernel and operates it against `.agents/dev-factory/` via the `--dir` flag. This keeps harness-forge
a single source of truth and an untouched, standalone plugin.

| Vendored file | Source | Role |
|---|---|---|
| `lattice.py` | `harness-forge/bin/lattice.py` | THE lattice kernel — the 8-state maturity machine (`TRANSITIONS`), `scan`/`rank`/`validity`/`advance`, staleness-as-graph, `scaffold`, the run-budget + loop-marker bound machinery. |
| `validate.py` | `harness-forge/bin/validate.py` | the validation path — runs a verifier, mints the Signal from its **exit status**, advances `instantiated → validated` only on pass. Imports `lattice` as a sibling (hence both live in `bin/`, not a subdir). |

**Never edit these here.** Fix upstream in harness-forge, then run `python3 tools/sync-dev-kernel.py`.
A drifted copy fails `sync-dev-kernel.py --check` in CI.

Everything dev-factory-specific — the ticket lifecycle machine, the six gates, the coordination
ledger vocab, dispatch, the server, the autonomy tiers — is **native** dev-kernel code that *calls*
this vendored kernel, never a fork of it. If dev-factory ever needs a kernel behavior the vendored
files don't expose, the fix is an upstream change to harness-forge (a justified cross-over
improvement), re-vendored — not a local edit.
