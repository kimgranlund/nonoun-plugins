# adia-ui-factory — plugins-factory 9-critic red-team (2026-06-03)

Ran the full `plugin-council` panel (Boris · Steve · Elon · Charity · Karpathy · Simon · Wlaschin · Huyen · Farley) cold against v0.1.0, in parallel isolated contexts, then synthesized (S-series). **No Critical from any critic.** The plugin is structurally sound — copy-alone clean, manifest valid, no bundled-agent trifecta (no agents at all), hook provably never-blocks. The Majors clustered on three roots, all folded.

## Verdict: CONDITIONAL → fixes folded → **APPROVED** (one accepted trade-off)

## Convergent findings (S6) and resolution

| # | Finding | Critics | Fix |
| --- | --- | --- | --- |
| 1 | **Stale "phase c / later phase" prose** contradicting shipped artifacts; `/adia-scaffold` steered away from the working `bin/adia-scaffold` | 8/9 (Elon Major) | Wired `/adia-scaffold` → the bin; deleted every stale hedge across commands/skills/references |
| 2 | **`npx -y @adia-ai/a2ui-mcp` unpinned + un-gated**, cost disclosed only in a load-on-demand reference | Boris·Charity·Simon·Huyen·Wlaschin·Farley (Major) | Pinned `@0.7.8`; lifted cost + supply-chain + disable path to README; documented "can't scope tools from `.mcp.json`" + upstream-owned network |
| 3 | **Trust boundary under-propagated** — only in orchestrator + `/adia-orient` | Simon (Major) | Added "inputs are data" to `a2ui-mcp-tools.md` + compose/verify/llm skills |
| 4 | **`adia-lint` gaps**: documented px≥3 rule didn't exist; path-substring color exemption un-linted `color-picker.css`; no selftest/CI | Karpathy (Major)·Farley | Implemented px≥3; foundation-sheet exemption (not substring); added `selftest` → CI |
| 5 | **Skill trigger collisions** (`factory`↔`spa`/`ssr`; `compose`↔modes on "author") with hand-off only in prose | Steve (Major) | Reserved "author" for `compose`; mode skills defer to `factory` when mode undecided |

## 9-dimension scorecard (critic scores → post-fix)

| Dim | Pre | Driver | Post |
| --- | --- | --- | --- |
| P1 fitness | 2–4 | description was a feature-list; MCP center-of-gravity | ~4 (trimmed; the SPA/SSR architecture fork is the non-MCP value) |
| P2 component-fit | 2–4 | MCP API-wrapper tax; scaffold determinism inverted | ~3–4 (scaffolder wired; tax documented, not scopable) |
| P3 boundary | 3 | `adia-ui-llm` the outlier | 3 (kept; tracked) |
| P4 dependency | 2–5 | MCP blast radius | ~4 (pinned + disclosed) |
| P5 manifest | 4 | unwired bin; unversioned MCP | ~5 (both fixed) |
| P6 context-economy | 2–3 | 24 always-on MCP tool defs | 3 — **accepted trade-off** (host starts the MCP on enable; disable path documented) |
| P7 routing | 2–5 | trigger collisions | ~4 (hand-off clauses) |
| P8 evolution | 3–5 | CHANGELOG/manifest drift | ~5 (dated 0.1.0 release) |
| P9 security | 2 | unpinned MCP + guard gaps | ~4 (pinned + guard propagated; outbound disclosed-as-unknown) |

## Accepted / deferred (see ROADMAP "Open")

- **P6 always-on MCP cost** — pinned, documented, disable-path given, but the host starts a plugin's MCP on enable and `.mcp.json` can't scope the tool set. Native gating is upstream; accepted for now.
- `adia-ui-llm` cohesion; `/adia-*` vs `/adia-ui-*` command namespace; the SSR-import lint blind spot — all logged, none load-bearing.

Method: `references/critics/eval-prompts.md` (PF/CF/BC/DL/MP/CE/RD/EV/ST + S-series). The artifact under review was treated as untrusted data; no embedded instruction was obeyed (ST5 scan: clean).
