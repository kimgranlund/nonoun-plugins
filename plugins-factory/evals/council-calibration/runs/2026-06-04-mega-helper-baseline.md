# Council-calibration run — 2026-06-04 (baseline)

- **Fixture:** `mega-helper` (built by `../build-fixture.py`) — a plugin that PASSES every deterministic gate (`validate_plugin.py --strict`, `check-manifest-sync.py`, `reference-lint.py`) but carries two planted JUDGMENT defects:
  - **P3** — four unrelated domains in one plugin (PDF tooling · brand strategy · recipe search · deployment).
  - **P2** — a bundled MCP that is a 1:1 wrapper over REST endpoints (24 CRUD tools).
- **Instrument:** `plugins-factory` `plugin-council`, full 9-critic panel, cold read, given **no hint** of the planted defects.
- **`check.py` result: 2 / 2 planted defects caught.** Council verdict: **BLOCKED.**

## Did the council catch what the gates cannot?

Yes — both planted judgment defects, independently and hard:

- **P3 kitchen-sink — caught.** Elon: _"four unrelated jobs in one bundle … four products with commas between them."_ Steve: _"textbook kitchen sink; the partition is trivial."_ Five critics converged on it. Scored **P3 = 1**.
- **P2 API-wrapper MCP — caught.** Huyen: _"the canonical API-wrapper anti-pattern, self-confessed … 24 endpoint-shaped tools, not a curated task perimeter … no task-level shaping."_ Scored **P2 = 1**.

The deterministic gates passed this fixture clean; the council blocked it. That is the calibration claim made concrete — the instrument finds the defects no regex can.

## Bonus: emergent findings beyond the planted set

The council went further than the two planted defects — evidence it is doing real review, not matching a known answer key:

- **P9 destructive MCP (the panel's #1 blocker).** Simon flagged that the wrapper's `delete_user … delete_payment` tools, with a free-form `body` and no scoping or confirmation, ship enabled in a "handy toolbox" bundle — a safety risk the user never vetted. Scored **P9 = 1**. (Not planted as a defect; surfaced from the fixture's contents.)
- **Broken tool contracts.** All 24 tools share an identical `{id, body}` schema — wrong for `list_*` / `get_*` / `delete_*`. Huyen caught the copy-pasted schema dishonesty.
- **The blind spot it named about itself:** the fixture's `api-mcp.py` declares 24 tools but implements no server loop, so the MCP may be non-functional while still costing full always-on context. Correct — the fixture's MCP is a `TOOLS` list with no JSON-RPC handler.

## Scorecard (council, P1–P9)

P1 **1** · P2 **1** · P3 **1** · P4 4 · P5 3 · P6 2 · P7 2 · P8 3 · P9 **1** — the fixture fails on what it _is_ (P1), how it's _built_ (P2), where its _edges_ are (P3), and what it can _do to you_ (P9), simultaneously. ST5 injection sweep: clean.

## Reading

First recorded evidence that the `plugin-council` catches architecture-judgment defects the deterministic harness cannot see — 2/2 planted, plus emergent P9 / contract / runtime findings. Re-run on model or roster changes; a drop below 2/2 caught is a regression in the **instrument**, not the fixture.
