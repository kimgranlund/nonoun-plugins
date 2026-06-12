# harness-forge — plugin-council red-team (2026-06-12, v0.1.0)

The 9-critic plugins-factory council (Boris C. · Steve Y. · Elon M. · Charity M. · Andrej K. · Simon W. · Scott W. · Chip H. · David F.), run cold in parallel isolated contexts against v0.1.0. The panel's headline: **the kernel is genuinely well-built (real deterministic machinery, every `bin/` script selftested, the trust boundary disciplined) — but v0.1 systematically OVER-CLAIMS.** Several "mechanical" guarantees are, as shipped, prose. The council did its job; the converged findings are folded into 0.1.1.

## Verdict: REBUILD the claims, not the kernel.

### Converged Critical (folded into 0.1.1)

- **CC1 — The scaffold is a hopeful instruction** (David F., Charity M.). `lattice.py init` wrote only `lattice.json`, not the nine layer dirs / `signals/` / `ledger/` / the schema copy that four surfaces promised; the CI "smoke" could only read `lattice.json`, so it was green on the path that hid the gap; the MCP reported the hole as "empty" not "missing." → **Fixed:** `init` now scaffolds the full tree + copies `naming.schema.json` + stamps `created`/`produced_by`, refuses to clobber existing state (idempotent unless `--force`); `lattice.py selftest` and CI assert the tree exists.
- **CC2 — "Mechanically deny-on-write" was prose** (Boris C., Simon W., Chip H.). `gate-signal` was wired nowhere (only the advisory hook); "the gate is the contract" was false in the shipped roster; the worker carried `Bash` (defeats a path glob); no executable validate path existed (the worker self-graded). → **Fixed:** every "deny-on-write / the validation path writes the signal" claim is scoped to *"when you wire `gate-signal` into your worker loop"* and named as the headline Honest-scope limitation; `Bash` dropped from the worker; `harness-builder`'s `Write` dropped; a real `bin/validate.py` ships — it runs a verifier command and writes the typed signal from the command's exit status (the missing executable), worker-deny-on-write.
- **CC3 — `false-pass` 0.0% read as earned** (Andrej K.). The rate defaulted to 0.0% when no `refute` event existed, indistinguishable from a measured 0.0%. → **Fixed:** `ledger.py false-pass` returns **`unmeasured`** with a loud notice when no refute source is registered; the rubric's H6 autonomy claim is gated on a registered refuter.

### Converged Major (folded into 0.1.1)

- **CM1 — The plugin's own name failed its own grammar** (Steve Y., Chip H., Scott W.). `harness-forge` — `forge ∉ tier{kernel,kit}`. → **Fixed:** `naming.schema.json` admits the catalog family axis (`forge`/`factory`/`ops`) as a deliberate ontology revision; `naming.py selftest` now runs the grammar over the *real* `agents/*.md` + the plugin name, so dogfooding is mechanically checked, not coincidental.
- **CM2 — Un-namespaced agents + a dead regenerator** (Steve Y., Elon M., Andrej K.). → **Fixed:** agents renamed `harness-advancer · harness-auditor · harness-distiller · harness-builder` (namespaced, collision-safe); `cell-regenerator` deleted (unreachable, duplicated the advancer, and stranded cells) — its one rule ("a validated cell changes only through a deliberate, ledgered transition") folded into the advancer's hard rules.

### Deferred (tracked in ROADMAP, scoped/acknowledged in 0.1.1)

- **D1 — Schemas not enforced + the "state machine" has no transition relation** (Scott W.). 0.1.1 ships a lightweight `lattice.py check` (stdlib enum/required/pattern validation of `lattice.json` against the cell schema) + the legal-transition relation; the full JSON-Schema gate is ROADMAP. The "typed data" claim is scoped accordingly.
- **D2 — MCP `scan_frontier` over-promises / `_OPEN` duplicates `lattice.py`** (Chip H.); **read_ledger truncates rationale silently** (Chip H., Charity M.); **gate-signal globs are over-broad** (David F., Andrej K.). 0.1.1 fixes the cheap ones (the `scan_frontier` description, the truncation marker); the import-dedup + glob anchoring are ROADMAP.
- **D3 — harness-builder is premature** (Elon M., Andrej K.) — kept (the requested orchestrator) but reachability via a `/harness-run` auto-loop is ROADMAP; for v0.1 the commands + the human are the controller.
- **D4 — H2 verifier calibration is prose** (Andrej K.) — labeled honestly; the calibration mechanism is ROADMAP.

### What the panel explicitly PASSED (no finding)

The trust boundary (every reviewer carries the untrusted-DATA guard, content-specific, per-isolated-context — no injection found in the plugin's own files); the advisory-vs-blocking hook species split (advisory always exits 0, blocking correctly NOT session-wired); the MCP read perimeter (`_safe()` against traversal/absolute/symlink/prefix-sibling, selftested; read-only, no exfil); copy-alone path legality (zero `../`, zero absolute paths); the deterministic kernel itself (selection/ranking/staleness/naming are real, selftested code).
