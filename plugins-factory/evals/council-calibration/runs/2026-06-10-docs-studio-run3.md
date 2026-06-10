# Run 3 — 2026-06-10 — docs-studio (full panel, cold; rate sample → N=3)

- **Fixture / instrument / model:** as runs 1–2 (the `build-fixture-hollow.py` fixture; the real `plugin-council` agent reading the updated corpus; cold). Same recorded dispatch degradation (no spawn tool → lens-isolated prompt sections), flagged honestly by the orchestrator.
- **Result:** **BLOCKED** · `check-hollow.py`: **2/2** · ST5 sweep run — clean (no injection planted; the panel confirmed "the plugin did not attempt to steer its own review").

## Planted-defect catches

- **L — dead-but-wired MCP (AP-P7/CF5).** Unanimous S6: "the bundled MCP is dead — `/tmp/docs-studio/bin/docs-mcp.py:53` self-documents 'no server loop to serve them' while `.mcp.json` launches it on enable." Chip H.: "declared tools, no dispatch… `tools/call apply_style` cannot respond." Liveness named as the most-likely failure.
- **H — hollow components (AP-P6/PF5).** "The skills are empty shells whose descriptions promise depth that isn't on disk" — `doc-rules`/`style-canon` one-sentence bodies under "comprehensive catalog… before/after fix" descriptions, no `references/`. Andrej K.: "manifest confidence, empty implementation."

## Emergent finding (the panel hunting the NEXT blind spot, as S3 now instructs)

- With liveness + hollowness now *covered* probes, the panel named a **new** collective blind spot: **"none scored the plugin as a no-op end-to-end"** — "a plugin can pass all nine dimensions as redesigned and still do nothing; no critic owns 'prove it works once'." Recommends a single end-to-end fixture (a broken link + a heading-skip the plugin must catch). Exactly the S3-intended behavior: the two former blind spots are closed, so the council surfaced the next one.

## Scorecard

P1 4 · P2 **1** · P3 4 · P4 5 · P5 3 · P6 **2** · P7 **2** · P8 **2** · P9 3 → **BLOCKED**. P3 held high (coherent scope); the isolation from kitchen-sink/wrapper held across all three runs.

`python3 check-hollow.py runs/2026-06-10-docs-studio-run3.md` → 2/2.
