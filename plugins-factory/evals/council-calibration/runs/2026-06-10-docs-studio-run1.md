# Run 1 — 2026-06-10 — docs-studio (full panel, cold; new-fixture baseline)

- **Fixture:** `docs-studio` (built by `build-fixture-hollow.py`) — the SECOND fixture shape, built to prove the two probes added to the corpus this session (PF5/AP-P6 hollowness · CF5/AP-P7 liveness). Deterministic gates re-confirmed **PASS** (`validate_plugin.py --strict`, `check-manifest-sync.py`); it is a **coherent single job** with a **task-shaped 3-tool MCP**, so it does NOT trip the kitchen-sink (P3) or API-wrapper (P2/AP-P4) findings — isolating the new probes. Defects not revealed.
- **Instrument:** the real `plugins-factory:plugin-council` agent, cold, reading the updated `references/critics/eval-prompts.md` (now carrying PF5 + CF5). Model: Claude Fable 5.
- **Result:** **BLOCKED** · `check-hollow.py`: **2/2 planted defects caught** · ST5 sweep run — clean (no injection planted in this fixture; the panel correctly classified `docs-mcp.py`'s self-disclosure as candor, "not a security finding").

## Planted-defect catches

- **L — dead-but-wired MCP (AP-P7/CF5) — caught, the panel's #1 blocker.** Chip H.: "a contract with no implementation — the inverse of the API-wrapper anti-pattern, and worse… no `stdio` read loop, no `initialize`/`tools/list`/`tools/call` dispatch (confirmed by grep)." Elon M.: "delete the MCP server: it cannot run, so it is pure mass." David F. named the missing gate: "a liveness check that the declared MCP server actually completes a JSON-RPC handshake" — exactly the CF5 smoke-gate recommendation. **Six of nine lenses converged**, and crucially the panel credited the tool *shapes* as correctly task-level (3 tools, not a wrapper) — proving the fixture isolated liveness from the wrapper anti-pattern as designed.
- **H — hollow components (AP-P6/PF5) — caught.** Boris C.: "the `description` is the entire knowledge, the body is empty… every session pays for two verbose descriptions that route to nothing." Charity M.: "the post-install surface over-promises and a user can't tell from `plugin details` that the bodies are empty stubs." Andrej K.: "the descriptions are at the 90th percentile of specificity, the bodies at the 1st… legal-but-dead." Elon M.: "what remains is a manifest plus four descriptions."

## Emergent finding beyond the planted set (real review, not answer-key matching)

- **The unscoped `apply_style` repo-wide rewrite** — the panel's named S3 blind spot: "the stated job is unattended multi-file mutation with no dry-run, no diff-gate, no scope limit, and no undo." Not planted as a defect (the MCP is dead) — surfaced from the fixture's *intended* behavior. This is the council doing genuine architecture review beyond the two planted seams.

## Scorecard

P1 3 · P2 **2** · P3 4 · P4 4 · P5 **2** · P6 **2** · P7 **2** · P8 **2** · P9 3 → **BLOCKED** (5 Critical + 9 Major across the panel; "the plugin's *concept* is sound — blocked on being non-functional and unsafe-by-intent, not mis-conceived"). Note P3=4: the coherent-scope isolation held — the panel did **not** misread it as a kitchen sink.

`python3 check-hollow.py runs/2026-06-10-docs-studio-run1.md` → 2/2.
