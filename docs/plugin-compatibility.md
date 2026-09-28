# Plugin compatibility and validation

Date: 2026-09-27. Packaging implementation: Progressive Context 0.1.0 and SDLC Lite 0.16.0.

## Shipped scope

Progressive Context is a shared skill for expressing intent, navigating context, evaluating the gap to implementation, and qualifying bounded reuse. Its small reference set covers contracts, evidence, SDLC links, and filesystem/browser/A2UI representations. Browser persistence and A2UI runtime adapters remain proposals.

SDLC Lite now executes roles natively through Codex or Claude. Codex uses generated predefined agent configurations, an explicit model/effort table, and `codex exec`; no Claude installation is required on that path. The shared runner retains result artifacts, base tracking, cleanup and output validation. Project setup additionally installs named in-session agents. See [native execution](codex-role-execution.md) for setup, model choices and live test evidence.

Both repository catalogs point to the same two plugin roots. Both host manifests preserve plugin identity. Every SDLC skill routes Codex through the adapter before Claude-specific tool syntax. Claude's hook configuration is explicitly selected from `adapters/claude/hooks.json`, outside Codex's automatic hook discovery location.

## Validation evidence

- Codex plugin-creator validator: both manifests and their discovered skill metadata pass.
- Claude plugin validator: both plugins and the repository marketplace pass.
- Codex CLI 0.155.0 app-server `plugin/read`, using the repository marketplace path: discovers Progressive Context's one skill and all 24 SDLC Lite skills. Both return zero Codex hooks. No installation or user configuration changes were required.
- New entry-point skills pass `quick_validate.py`. Progressive Context passes the cross-harness validator.
- `scripts/check-packaging.py` checks catalog membership/source paths, manifest identity parity, required entry points, Codex routing, hook separation, and Progressive Context reference links. A copied marketplace with a wrong/missing plugin path was rejected as a negative control.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Role-table checks, decomposition, tickets, board, steps, ordering, fanout, runner, hooks, offline live-probe selftests, shellcheck, and Claude validation all pass. The metadata/role consistency check was rerun after the final skill edits and also passed.

These checks demonstrate packaging, discovery, and the covered script behavior. They do not demonstrate model adherence to every workflow, installed-session implicit routing, browser portability, or comparative effectiveness against ICM Architect.

## Remaining behavioral qualification

Before claiming full end-to-end host parity, run fresh installed sessions in each host: a should-trigger case, a near miss, explicit invocation, and a real completion case. For Progressive Context include an intent-only non-code artifact, failed/stale evidence, and an independent reuse exercise. The original package-discovery checks are supplemented by native Codex runner and agent tests in the execution report. Broader benchmark parity across hosts remains unmeasured.

## Maintenance

Run `python3 scripts/check-packaging.py` and `bash plugins/sdlc-lite/scripts/check.sh`. Repeat Codex native discovery after changing skill paths or hook wiring. The two catalogs use different schemas; do not copy one over the other. The supported compatibility manifest layout is documented in [OpenAI's plugin packaging guide](https://developers.openai.com/plugins/build/plugins).
