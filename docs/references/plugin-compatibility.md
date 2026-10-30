# Plugin compatibility and validation

Updated: 2026-10-30. Marketplace `nonoun` ships four plugins: `sdlc` 1.0.0, `context` 0.3.0, `design` 0.1.0, and `dev-tools` 0.1.0. The standard these follow is [the plugin card](../specs/doc-standards/plugins.md).

## Shipped scope

- `sdlc` executes roles natively through Codex or Claude. Codex uses generated agent configurations in `plugins/sdlc/adapters/codex/agents/`, the model and effort table in `adapters/codex/models.json`, and `codex exec`; no Claude installation is needed on that path. Claude agents are generated from `adapters/claude/levels.json`. See [native execution](codex-role-execution.md).
- `context` (formerly Progressive Context) is a skill set for intent, context navigation, routing, evidence, and qualified reuse.
- `design` holds UI construction, geometry, palette, inspector, wireframe, and critique skills.
- `dev-tools` holds machine, repo, and harness care skills, including `author-cross-harness-plugins`.

Both catalogs point to the same four roots under `./plugins/`. Every plugin has two manifests with the same identity, and each Codex manifest reads `./skills/`. Every SDLC skill routes Codex through the adapter before Claude-specific tool syntax. Claude hooks are selected from `plugins/sdlc/adapters/claude/hooks.json`, outside Codex's hook discovery location. Host-only gaps are in `plugins/sdlc/HARNESS-NOTES.md` and `plugins/context/HARNESS-NOTES.md`.

## Validation evidence (2026-10-30)

- [V] `python3 scripts/check-packaging.py`: exit 0, PASS on catalog parity, identity, skill routes and sizes, hook isolation, links, and CI triggers.
- [V] `validate_cross_harness.py` per plugin: `context` and `dev-tools` clean. `sdlc` fails on `${CLAUDE_PLUGIN_ROOT}` in shared skills, the pattern its Codex adapter translates. `design` fails on `$ARGUMENTS` in `make-figma-agent-connector`.
- [U] Live discovery in a fresh Codex or Claude session was not rerun for the 1.0.0 layout.

## Validation evidence (2026-09-27)

Packaging then: Progressive Context 0.1.0 and SDLC 0.16.0, two plugin roots.

- Codex plugin-creator validator: both manifests and their discovered skill metadata pass.
- Claude plugin validator: both plugins and the repository marketplace pass.
- Codex CLI 0.155.0 app-server `plugin/read`, using the repository marketplace path: discovers Progressive Context's one skill and all 24 SDLC skills. Both return zero Codex hooks. No installation or user configuration changes were required.
- New entry-point skills pass `quick_validate.py`. Progressive Context passes the cross-harness validator.
- `scripts/check-packaging.py` checks catalog membership/source paths, manifest identity parity, required entry points, Codex routing, hook separation, and Progressive Context reference links. A copied marketplace with a wrong/missing plugin path was rejected as a negative control.
- `bash plugins/sdlc/scripts/check.sh`: exit 0. Role-table checks, decomposition, tickets, board, steps, ordering, fanout, runner, hooks, offline live-probe selftests, shellcheck, and Claude validation all pass. The metadata/role consistency check was rerun after the final skill edits and also passed.

These checks demonstrate packaging, discovery, and the covered script behavior. They do not demonstrate model adherence to every workflow, installed-session implicit routing, browser portability, or comparative effectiveness against ICM Architect.

## Retired skill names (T-0467, T-0468, T-0665)

Changelog: `plan-goal`, `plan-campaign`, `plan-doc`, and `plan-fanout` are merged into `/sdlc:plan <kind>` (kinds `steps`, `doc`, `goal`, `campaign`, `fanout`). For one release each old name stayed as a redirect stub; T-0665 deleted the stubs and `scripts/check.py` item 58, so a typed old name no longer resolves and the old trigger phrases route to `plan`. `plan-loop`, `plan-verification`, and `run-plan` keep their names. Codex reads the same skill folders (`skills: ./skills/`), so no Codex manifest change is needed.

## Remaining behavioral qualification

Before claiming full end-to-end host parity, run fresh installed sessions in each host: a should-trigger case, a near miss, explicit invocation, and a real completion case. For Progressive Context include an intent-only non-code artifact, failed/stale evidence, and an independent reuse exercise. The original package-discovery checks are supplemented by native Codex runner and agent tests in the execution report. Broader benchmark parity across hosts remains unmeasured.

## Maintenance

Run `python3 scripts/check-packaging.py` and `bash plugins/sdlc/scripts/check.sh`. Repeat Codex native discovery after changing skill paths or hook wiring. Regenerate agents with `claude_roles.py generate` and `codex_roles.py generate` after a role or level change. The two catalogs use different schemas; do not copy one over the other. The supported compatibility manifest layout is documented in [OpenAI's plugin packaging guide](https://developers.openai.com/plugins/build/plugins).
