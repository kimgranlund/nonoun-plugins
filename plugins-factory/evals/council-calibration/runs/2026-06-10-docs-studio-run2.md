# Run 2 — 2026-06-10 — docs-studio (full panel, cold; rate sample)

- **Fixture / instrument / model:** as run 1 (the `build-fixture-hollow.py` fixture; the real `plugin-council` agent reading the updated corpus; cold). Gates re-confirmed PASS.
- **Result:** **BLOCKED** · `check-hollow.py`: **2/2 planted defects caught** · ST5 sweep run — clean (the panel scanned every description, both `SKILL.md` bodies, `doc-fix.md`, the MCP tool descriptions, and the `docs-mcp.py` comment: "None found. The line 53 comment… is a candid self-disclosure, not an injection").

## Planted-defect catches

- **L — dead-but-wired MCP (AP-P7/CF5) — caught, unanimous.** Chip H.: "the MCP tool contract is a fiction: shapes without a server is a contract with no counterparty… no `tools/call` handler, no `tools/list` responder, no stdio loop." Andrej K. supplied the falsifying test verbatim: "`printf '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' | python3 bin/docs-mcp.py` returns nothing — falsifying the plugin's headline capability — and no gate runs it." David F.: "no smoke test would catch the dead server."
- **H — hollow components (AP-P6/PF5) — caught.** Elon M.: "after deleting the dead MCP, what remains is **a skill wearing a manifest**… a scaffold mislabeled `version 1.0.0`." Boris C.: "the expensive always-on bytes promise depth that the body does not contain… progressive disclosure is inverted." Charity M.: "`plugin details` would show capability that doesn't exist; the post-install signal lies." Andrej K.: "the skills' depth claims are unfalsifiable against the bundle — no `references/`, no rule list, no fixtures."

## Emergent findings (genuine review beyond the answer key)

- Run 2 found a **sharper liveness sub-finding than run 1**: the *silent-success* failure class — "a dead server that exits 0 on launch… fails silently and invisibly: `plugin details` shows it green… misattributed by the user to 'the model didn't use the tool.'" Named as the panel's S3 blind spot.
- Simon W. independently flagged the missing `_safe()` traversal guard on `apply_style` (the repo's own MCP convention from CLAUDE.md) — the same unscoped-mutation concern run 1 raised, reached from the security lens.

## Scorecard

P1 **2** · P2 **2** · P3 3 · P4 4 · P5 **2** · P6 **1** · P7 **2** · P8 **2** · P9 3 → **BLOCKED** (3 Critical blocking + Majors well past the floor). P6=1 ("negative economy: the plugin charges every session for capability that cannot fire"). As in run 1, P3 stayed high (3–4) — the coherent-scope isolation held across both runs.

`python3 check-hollow.py runs/2026-06-10-docs-studio-run2.md` → 2/2.
