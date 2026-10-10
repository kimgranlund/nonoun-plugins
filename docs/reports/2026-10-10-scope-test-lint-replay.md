# Scope-versus-tests heuristic replay (T-0416)

Spike for goal G-002, candidate 5 of `docs/specs/sdlc-lite/restart-and-blocked-run-plan.md`. Diagnosis only: no code changed, neither repository edited.

## Heuristic

For each source path a step's scope allow-list names, list the test files in that repository that contain the source file's basename without extension and are not in the allow-list. A test file is a path with a `test/`, `tests/` or `__tests__/` segment, or a `.test.` or `.spec.` name. The repository is read at the step's recorded `base-sha` (the tree the builder saw), so later commits do not leak in. The match is a case-sensitive fixed-string search of file content. Applied literally: the `.spec.` clause also admits `*.spec.md` design documents, which is part of the noise measured below.

## Known misses

Four files a builder had to ask for, none in the original scope list:

- agent-ui T-0060 step 4: `packages/agent-ui/a2ui/src/live-agent/mcp-enablement.test.ts` (builder-L4 blocked on it) and `packages/agent-ui/devtools/src/transports/replay.test.ts` (builder-L4-2 asked for it). Both were then added with `steps.py widen`.
- ultimate-tokens T-0040 step 2 (superseded): `test/engine/semantic.mjs` and `test/engine/exports.mjs` (`builder-L5.md:31-32`, "the scope guard excludes ... and both go red").

## Sources

- agent-ui step folder found at `/Users/kimgranlund/Projects/nonoun/agent-ui/.claude/worktrees/wave-rts/.sdlc/response-type-selection/step-4/` (T-0060 is `response-type-selection`, found by id in `handoff.md`; no `*0060*` folder name exists). Its `builder-L4.md` and `builder-L4-2.md` were read; base sha `0affd8ad09dea44cd9635c25eed2f27bc9bb5739`.
- ultimate-tokens step folder `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc/match-peer-lightness/step-2.superseded-1/`; base sha `2d218bec249c54b82eecd7de6ebca3c5b8f0595d`.

## Plan 1: agent-ui T-0060 step 4

Allow-list (scope guard in the step handoff): `packages/agent-ui/a2ui/src/agent/produce.ts`, `meta-line.ts`, `session.ts`, and the new `packages/agent-ui/a2ui/src/live-agent/produce-response-type.test.ts`. Source paths checked: `produce.ts`, `meta-line.ts`, `session.ts` (basenames `produce`, `meta-line`, `session`). The new test file does not exist at the base sha and is allow-listed, so it never flags.

Test files in the tree at base: 1060. Flagged: 331 (294 code tests, 37 `.spec.md` documents). Known misses flagged: 2 of 2 (mcp-enablement.test.ts, replay.test.ts).

| Flagged test | Matched basename | Known miss |
|---|---|---|
| `.claude/docs/spec/a2a-foundations.spec.md` | produce,session | no |
| `.claude/docs/spec/a2ui-catalog.spec.md` | produce | no |
| `.claude/docs/spec/a2ui-chat.spec.md` | meta-line,produce,session | no |
| `.claude/docs/spec/a2ui-container-vocabulary.spec.md` | produce,session | no |
| `.claude/docs/spec/a2ui-ecosystem-alignment.spec.md` | produce,session | no |
| `.claude/docs/spec/a2ui-expert-harness.spec.md` | produce | no |
| `.claude/docs/spec/a2ui-live-agent.spec.md` | meta-line,produce,session | no |
| `.claude/docs/spec/a2ui-message-lifecycle.spec.md` | meta-line,produce,session | no |
| `.claude/docs/spec/a2ui-runtime.spec.md` | produce,session | no |
| `.claude/docs/spec/a2ui-streaming-pipeline.spec.md` | produce | no |
| `.claude/docs/spec/a2ui-training-corpus.spec.md` | session | no |
| `.claude/docs/spec/agent-model.spec.md` | meta-line,produce,session | no |
| `.claude/docs/spec/app-surfaces-m2.spec.md` | produce | no |
| `.claude/docs/spec/capability-availability-tagging.spec.md` | produce,session | no |
| `.claude/docs/spec/chart-family.spec.md` | produce | no |
| `.claude/docs/spec/code-prose.spec.md` | produce | no |
| `.claude/docs/spec/color-picker.spec.md` | produce | no |
| `.claude/docs/spec/command-modal.spec.md` | produce | no |
| `.claude/docs/spec/content-family.spec.md` | produce,session | no |
| `.claude/docs/spec/devtools-harness.spec.md` | meta-line,produce,session | no |
| `.claude/docs/spec/feed-family.spec.md` | produce | no |
| `.claude/docs/spec/follow-the-change.spec.md` | produce | no |
| `.claude/docs/spec/genui-surface.spec.md` | meta-line,produce,session | no |
| `.claude/docs/spec/identity-mock-transport.spec.md` | produce,session | no |
| `.claude/docs/spec/mcp-agent-config.spec.md` | produce | no |
| `.claude/docs/spec/multi-select-field.spec.md` | session | no |
| `.claude/docs/spec/nav-rail-family.spec.md` | produce | no |
| `.claude/docs/spec/persona-catalog-composition.spec.md` | produce,session | no |
| `.claude/docs/spec/renderer-structural-resend.spec.md` | produce | no |
| `.claude/docs/spec/response-type-selection.spec.md` | meta-line,produce,session | no |
| `.claude/docs/spec/router.spec.md` | produce,session | no |
| `.claude/docs/spec/saas-data-utilities.spec.md` | produce | no |
| `.claude/docs/spec/saas-data-workbench.spec.md` | produce,session | no |
| `.claude/docs/spec/shell-archetypes-m5.spec.md` | produce | no |
| `.claude/docs/spec/site-command-search.spec.md` | produce,session | no |
| `.claude/docs/spec/theme-provider.spec.md` | produce | no |
| `.claude/docs/spec/toolbar.spec.md` | produce | no |
| `packages/agent-ui/a2a/src/arena-agent/match.test.ts` | produce | no |
| `packages/agent-ui/a2a/src/arena-agent/model-seat.test.ts` | session | no |
| `packages/agent-ui/a2a/src/corpus/shard.test.ts` | produce | no |
| `packages/agent-ui/a2a/src/feed/dev-proxy-plugin.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2a/src/feed/feed-session.test.ts` | session | no |
| `packages/agent-ui/a2a/src/rpc/errors.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/agent/agent-assets-freshness.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/agent/gates.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/agent/response-type.test.ts` | meta-line,session | no |
| `packages/agent-ui/a2ui/src/catalog/catalog.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/catalog/default/index.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/catalog/functions.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/catalog/personas/concierge/concierge.browser.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/catalog/personas/concierge/factories.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/catalog/personas/croupier/checks.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/catalog/personas/croupier/recorded-replay.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/catalog/personas/fixture-demo/factories.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/catalog/semantic-check.test.ts` | session | no |
| `packages/agent-ui/a2ui/src/corpus/admission-coverage.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/corpus/admit.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/corpus/corpus-data.test.ts` | session | no |
| `packages/agent-ui/a2ui/src/corpus/index.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/corpus/multi-turn-shard.test.ts` | session | no |
| `packages/agent-ui/a2ui/src/corpus/repair-shard.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/corpus/retrieve.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/corpus/store.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/corpus/verdict-archive.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/layering.test.ts` | meta-line,produce | no |
| `packages/agent-ui/a2ui/src/live-agent/a2ui-surface-toggle.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-tool-loop.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-usage.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/chat-validation.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/dev-proxy-abort.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/dev-proxy-reasoning.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/dogfood-inventory-parity.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/dogfood-inventory.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/feed-catalog.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/genui-exclusive.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/genui-line.test.ts` | meta-line,produce | no |
| `packages/agent-ui/a2ui/src/live-agent/genui-produce.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/genui-surface-prompt.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/mcp-boot.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/mcp-enablement.test.ts` | meta-line,produce,session | yes: mcp-enablement.test.ts |
| `packages/agent-ui/a2ui/src/live-agent/meta-line.test.ts` | meta-line,produce | no |
| `packages/agent-ui/a2ui/src/live-agent/mini-skills.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/produce-budget-usage.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/produce-loop.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/produce-semantic-checks.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/prompt-budget.test.ts` | meta-line,produce | no |
| `packages/agent-ui/a2ui/src/live-agent/round-trip.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/session.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/structural-transcript.test.ts` | meta-line,session | no |
| `packages/agent-ui/a2ui/src/live-agent/system-prompt-grammar.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/turn-deadline.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/validate-authoring-surface.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/validate-builder-mission.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/live-agent/validate-effort.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/validate-mode.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/live-agent/worker-route-guards.test.ts` | session | no |
| `packages/agent-ui/a2ui/src/protocol.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/registry/compose.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/registry/registry-wiring.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/registry/selection.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/binding.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/bound-text.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/checkbox-group-layout.browser.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/date-field-a2ui-mount.browser.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/functions.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/renderer-persona-catalogs.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/renderer.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/renderer/validate.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/renderer/widget.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/testkit/findings.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/testkit/from-conformance.test.ts` | session | no |
| `packages/agent-ui/a2ui/src/testkit/integration.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/testkit/interaction.browser.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/testkit/interaction.test.ts` | meta-line,session | no |
| `packages/agent-ui/a2ui/src/testkit/judge.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/testkit/offline-wiring.test.ts` | meta-line,produce | no |
| `packages/agent-ui/a2ui/src/testkit/producer-leg.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/testkit/scenario.test.ts` | produce,session | no |
| `packages/agent-ui/a2ui/src/testkit/scenarios.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/testkit/scripted-mcp.test.ts` | session | no |
| `packages/agent-ui/a2ui/src/testkit/scripted-transport.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/a2ui/src/testkit/seeded-run.test.ts` | produce | no |
| `packages/agent-ui/a2ui/src/testkit/seeded.test.ts` | produce | no |
| `packages/agent-ui/a2ui/tools/agent-eval/cases.test.ts` | session | no |
| `packages/agent-ui/a2ui/tools/agent-eval/legs.test.ts` | session | no |
| `packages/agent-ui/a2ui/tools/agent/integrations/mcp/client.test.ts` | session | no |
| `packages/agent-ui/a2ui/tools/agent/integrations/mcp/discover.test.ts` | produce | no |
| `packages/agent-ui/a2ui/tools/agent/integrations/tool-dispatch.test.ts` | produce | no |
| `packages/agent-ui/a2ui/tools/agent/worker/route-guards.test.ts` | session | no |
| `packages/agent-ui/a2ui/tools/conformance/suites-driftwire.test.ts` | produce | no |
| `packages/agent-ui/a2ui/tools/corpus-genui/eval-genui-corpus.test.ts` | produce | no |
| `packages/agent-ui/a2ui/tools/corpus-genui/generate.test.ts` | produce | no |
| `packages/agent-ui/a2ui/tools/corpus/import-seeds.test.ts` | produce | no |
| `packages/agent-ui/a2ui/tools/harness/validate-payload.test.ts` | produce | no |
| `packages/agent-ui/app/src/agent-admin-lazy.browser.test.ts` | produce | no |
| `packages/agent-ui/app/src/agent-admin-lazy.test.ts` | produce | no |
| `packages/agent-ui/app/src/catalog-lazy.bundle.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-admin-authoring.test.ts` | produce,session | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-admin-bankroll.test.ts` | session | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-admin-click-turn.browser.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-admin-lazy.bundle.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-admin-transcript-export.test.ts` | session | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-admin.browser.test.ts` | produce,session | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-admin.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/app/src/controls/agent-admin/agent-roster-source.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/agent-admin/dogfood-lazy.bundle.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/agent-admin/entries.test.ts` | session | no |
| `packages/agent-ui/app/src/controls/agent-admin/follow-the-change.browser.test.ts` | session | no |
| `packages/agent-ui/app/src/controls/agent-admin/follow-the-change.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/agent-admin/markdown-lazy.bundle.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/agent-admin/resource-idb-store.test.ts` | session | no |
| `packages/agent-ui/app/src/controls/agent-admin/skill-pack-lazy.bundle.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/conversation/conversation.browser.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/app/src/controls/conversation/conversation.test.ts` | meta-line,produce,session | no |
| `packages/agent-ui/app/src/controls/entry-list/entry-list.browser.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/master-detail/master-detail.browser.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/master-detail/master-detail.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/nav-rail/nav-rail.browser.test.ts` | produce,session | no |
| `packages/agent-ui/app/src/controls/settings/memory-store.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/settings/settings.browser.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/settings/settings.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/super-shell/super-shell-bar-seam.browser.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/super-shell/super-shell-responsive.browser.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/super-shell/super-shell.test.ts` | produce | no |
| `packages/agent-ui/app/src/controls/surface-host/surface-host-working.browser.test.ts` | session | no |
| `packages/agent-ui/app/src/controls/surface-host/surface-host.browser.test.ts` | produce,session | no |
| `packages/agent-ui/app/src/controls/surface-host/surface-host.test.ts` | produce | no |
| `packages/agent-ui/app/src/pdf-identity.bundle.test.ts` | produce | no |
| `packages/agent-ui/app/src/source-bytes.test.ts` | produce | no |
| `packages/agent-ui/code/src/core/project.test.ts` | produce | no |
| `packages/agent-ui/code/src/editor/editor.browser.test.ts` | produce,session | no |
| `packages/agent-ui/code/src/highlight/langs/ts.test.ts` | produce | no |
| `packages/agent-ui/code/src/highlight/scan.test.ts` | produce | no |
| `packages/agent-ui/code/src/markdown/injection.test.ts` | produce | no |
| `packages/agent-ui/code/src/markdown/markdown.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/_surface/container-box.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/_surface/container.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/attachment/attachment.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/avatar/avatar.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/badge/badge.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/bar-chart/bar-chart.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/breadcrumb/breadcrumb.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/button/button-geometry.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/button/button-states.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/calendar/calendar.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/calendar/calendar.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/card/card.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/checkbox/checkbox.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/choice-card/choice-card.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/code/code.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/color-picker/color-picker.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/column-chart/column-chart.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/column/column.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/combo-box/combo-box.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/command-modal/command-modal.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/description-list/description-list.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/disclosure/disclosure.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/drawer/drawer.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/drill/drill.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/drill/drill.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/field/field.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/form-popover/form-popover.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/form-provider/form-e2e.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/gauge/gauge.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/grid/grid-descriptor.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/image/image.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/ladder/ladder.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/line-chart/line-chart.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/menu/menu.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/modal/modal.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/multi-select/multi-select.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/otp-field/otp-field.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/otp-field/otp-field.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/pagination/pagination.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/pie-chart/pie-chart.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/pie-chart/pie-math.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/playing-card/playing-card.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/playing-card/playing-card.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/popover/popover.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/progress/progress.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/radio/radio-group.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/radio/radio-group.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/ramp/ramp.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/rating/rating.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/sandbox-frame/dogfood/dogfood-assets-freshness.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/sandbox-frame/sandbox-frame.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/segmented-control/segmented-control.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/select/select.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/service-card/service-card.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/service-card/service-card.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/slider-multi/slider-multi.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/slider/slider.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/slider/slider.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/source-list/source-list.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/sparkline/sparkline.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/stat/stat.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/status-stream/status-stream.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/suggestions/suggestions.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/suggestions/suggestions.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/swatch/swatch.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/swiper/swiper.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/switch/switch.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/table/table-interactive.browser.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/table/table-model.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/table/table.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/tabs/tabs.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/text-field/text-field-geometry.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/text-field/text-field-states.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/text-field/text-field.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/text/text-href-security.test.ts` | produce | no |
| `packages/agent-ui/components/src/controls/text/text.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/controls/textarea/textarea.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/timeline-item/timeline-item.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/toast/toast.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/toggle/toggle.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/toolbar/toolbar.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/controls/tooltip/tooltip.browser.test.ts` | session | no |
| `packages/agent-ui/components/src/descriptor/component-descriptor-comment.test.ts` | produce | no |
| `packages/agent-ui/components/src/dom/element-upgrade.test.ts` | produce | no |
| `packages/agent-ui/components/src/dom/form.test.ts` | produce | no |
| `packages/agent-ui/components/src/dom/props-reflect.test.ts` | produce | no |
| `packages/agent-ui/components/src/traits/overlay.browser.test.ts` | produce,session | no |
| `packages/agent-ui/components/src/traits/pane-resize.test.ts` | produce | no |
| `packages/agent-ui/components/src/traits/pending-computed.test.ts` | session | no |
| `packages/agent-ui/components/src/traits/scroll-fade.test.ts` | session | no |
| `packages/agent-ui/components/src/traits/tabbable.test.ts` | session | no |
| `packages/agent-ui/data/src/gateway/auth.test.ts` | session | no |
| `packages/agent-ui/data/src/stream/bridge.test.ts` | produce | no |
| `packages/agent-ui/devtools/src/capture/format.test.ts` | session | no |
| `packages/agent-ui/devtools/src/layering.test.ts` | produce | no |
| `packages/agent-ui/devtools/src/server/harness-plugin.test.ts` | session | no |
| `packages/agent-ui/devtools/src/timeline/events.test.ts` | meta-line,session | no |
| `packages/agent-ui/devtools/src/timeline/turn-usage.test.ts` | meta-line,session | no |
| `packages/agent-ui/devtools/src/transports/a2a-peer.test.ts` | session | no |
| `packages/agent-ui/devtools/src/transports/proxy.test.ts` | produce,session | no |
| `packages/agent-ui/devtools/src/transports/replay.test.ts` | meta-line,produce,session | yes: replay.test.ts |
| `packages/agent-ui/router/src/router.browser.test.ts` | produce,session | no |
| `packages/agent-ui/router/src/url-history.test.ts` | produce,session | no |
| `packages/agent-ui/shared/src/tokens/theme-packs.test.ts` | produce | no |
| `packages/agent-ui/shared/src/tokens/wrap-pack.test.ts` | produce | no |
| `scripts/publish/publish-packages.test.mjs` | meta-line,produce | no |
| `site/gallery.browser.test.ts` | produce,session | no |
| `site/lib/a2ui-activity.test.ts` | meta-line,produce | no |
| `site/lib/a2ui-gallery.browser.test.ts` | produce | no |
| `site/lib/admin-live-runner.test.ts` | meta-line,produce,session | no |
| `site/lib/arena-replay.test.ts` | produce | no |
| `site/lib/build-css.test.ts` | produce | no |
| `site/lib/command-palette.browser.test.ts` | session | no |
| `site/lib/command-palette.test.ts` | session | no |
| `site/lib/doc-page.browser.test.ts` | produce | no |
| `site/lib/flow-chrome.test.ts` | meta-line | no |
| `site/lib/genui-line.test.ts` | meta-line | no |
| `site/lib/identity-mock-transport-prod-bundle.test.ts` | produce | no |
| `site/lib/identity-mock-transport.test.ts` | produce,session | no |
| `site/lib/light-dark-minify.test.ts` | produce | no |
| `site/lib/live-proxy-transport.test.ts` | session | no |
| `site/lib/plan-runner.test.ts` | meta-line,session | no |
| `site/lib/sitemap.test.ts` | produce | no |
| `site/lib/team-agent-card.test.ts` | produce | no |
| `site/lib/theme-provider-build-fixture.test.ts` | produce | no |
| `site/lib/zip-writer.test.ts` | produce | no |
| `site/pages/a2a-tic-tac-toe.live.test.ts` | produce | no |
| `site/pages/a2ui-agent.test.ts` | meta-line,produce | no |
| `site/pages/a2ui-chat.effort-wiring.test.ts` | produce | no |
| `site/pages/a2ui-chat.test.ts` | meta-line,produce | no |
| `site/pages/a2ui-live-conversation.browser.test.ts` | produce,session | no |
| `site/pages/a2ui-live.ask-lifecycle.test.ts` | meta-line,produce | no |
| `site/pages/a2ui-live.effort-wiring.test.ts` | produce | no |
| `site/pages/a2ui-live.planner.test.ts` | meta-line | no |
| `site/pages/account-settings.browser.test.ts` | session | no |
| `site/pages/agent-admin-app-team.test.ts` | produce | no |
| `site/pages/agent-admin-app.browser.test.ts` | produce,session | no |
| `site/pages/agent-admin-app.test.ts` | meta-line,produce,session | no |
| `site/pages/agent-admin-debug-export.test.ts` | produce,session | no |
| `site/pages/agent-admin-persona-file.test.ts` | produce | no |
| `site/pages/agent-schema.test.ts` | produce | no |
| `site/pages/breadcrumb-demo.browser.test.ts` | produce | no |
| `site/pages/command-modal-demo.browser.test.ts` | produce | no |
| `site/pages/credentials.browser.test.ts` | produce | no |
| `site/pages/devtools-harness.test.ts` | produce,session | no |
| `site/pages/drill-demo.browser.test.ts` | produce | no |
| `site/pages/gen-ui-live-narrow.browser.test.ts` | produce | no |
| `site/pages/gen-ui-live.browser.test.ts` | produce,session | no |
| `site/pages/gen-ui-live.live-failure.test.ts` | meta-line,produce | no |
| `site/pages/gen-ui-live.test.ts` | produce,session | no |
| `site/pages/onboarding.browser.test.ts` | session | no |
| `site/pages/otp-signin.browser.test.ts` | session | no |
| `site/pages/persona-library-pattern.test.ts` | produce | no |
| `site/pages/service-card-demo.browser.test.ts` | produce | no |
| `site/pages/textarea-demo.browser.test.ts` | produce | no |
| `site/pages/workbench.browser.test.ts` | session | no |

## Plan 2: ultimate-tokens T-0040 step 2

Allow-list: the regex in the step's last (guard) scope criterion. Non-test source paths checked: `src/engine/tonal.js`, `src/engine/layers.mjs`, `src/engine/layer-pins.mjs`, `src/engine/layers/ramp@1.mjs`, `src/engine/layers/FROZEN.json`, `scripts/bundle.mjs`, `scripts/gen-describe-mcp-assets.mjs`, `scripts/lib/envelope-measure.mjs`, `src/ui/describe-mcp-assets.js`, `figma/plugin/ui.html` (basenames `tonal`, `layers`, `layer-pins`, `ramp@1`, `FROZEN`, `bundle`, `gen-describe-mcp-assets`, `envelope-measure`, `describe-mcp-assets`, `ui`). Allow-listed tests (`test/run.mjs`, `test/engine/{layers,layer-pins,anchor,mode-isolation-gate,curated-contrast,tonal,peer-lightness,chroma-envelope-gate}.mjs`, `test/engine/fixtures/tonal-legacy.json`, `test/ui/{model,shell,headless-boot}.mjs`, `test/ui/fixtures/default-doc-ramps.json`) are excluded from flags. `docs/.+\.md` in the regex names no concrete file and was skipped.

Test files in the tree at base: 82. Flagged: 53. Known misses flagged: 2 of 2 (test/engine/semantic.mjs, test/engine/exports.mjs). Both match on the specific basename `tonal` (and `exports.mjs` also on `layers`, `layer-pins`, `bundle`), not only on the generic `ui`.

| Flagged test | Matched basename | Known miss |
|---|---|---|
| `test/engine/adia-derived-exports.mjs` | tonal,ui | no |
| `test/engine/categories.mjs` | tonal,ui | no |
| `test/engine/controls.mjs` | layers,tonal,ui | no |
| `test/engine/corpus-sample.mjs` | ui | no |
| `test/engine/ds-gates.mjs` | bundle,ui | no |
| `test/engine/even-dips-gate.mjs` | tonal,ui | no |
| `test/engine/exports.mjs` | bundle,layer-pins,layers,tonal,ui | yes: test/engine/exports.mjs |
| `test/engine/fixtures/maison-geometry-rows.json` | ui | no |
| `test/engine/fixtures/prime-pre-681.mjs` | FROZEN,tonal,ui | no |
| `test/engine/fixtures/shadcn-baseline.css` | layers,ramp@1,tonal,ui | no |
| `test/engine/geometry.mjs` | ui | no |
| `test/engine/hct.mjs` | tonal,ui | no |
| `test/engine/okhsl.mjs` | tonal | no |
| `test/engine/prime-determinism-worker.mjs` | tonal,ui | no |
| `test/engine/prime.mjs` | FROZEN,tonal,ui | no |
| `test/engine/ramp-identity.mjs` | ui | no |
| `test/engine/semantic.mjs` | tonal,ui | yes: test/engine/semantic.mjs |
| `test/engine/type.mjs` | bundle,ui | no |
| `test/figma/binder.mjs` | bundle,tonal,ui | no |
| `test/figma/migrations.mjs` | FROZEN,ui | no |
| `test/figma/plugin.mjs` | bundle,tonal,ui | no |
| `test/figma/style-plan.mjs` | ui | no |
| `test/gate-report.mjs` | tonal | no |
| `test/mcp/brand-kit-merged-core.mjs` | ui | no |
| `test/mcp/brand-kit-merged.mjs` | ui | no |
| `test/mcp/brand-kit.mjs` | tonal,ui | no |
| `test/mcp/core.mjs` | tonal,ui | no |
| `test/mcp/describe-eval.mjs` | bundle,ui | no |
| `test/mcp/describe-kit-core.mjs` | ui | no |
| `test/mcp/describe-mcp-core.mjs` | ui | no |
| `test/mcp/describe-mcp-package.mjs` | describe-mcp-assets,ui | no |
| `test/mcp/describe-rubric.mjs` | ui | no |
| `test/mcp/png-swatch-board.mjs` | tonal,ui | no |
| `test/plugin/color-tokens.mjs` | ui | no |
| `test/plugin/geometry-tokens.mjs` | ui | no |
| `test/plugin/hosted-pack.mjs` | ui | no |
| `test/plugin/manifest.mjs` | bundle,ui | no |
| `test/plugin/typography-tokens.mjs` | ui | no |
| `test/repo/branding.mjs` | describe-mcp-assets,ui | no |
| `test/repo/citations.mjs` | tonal,ui | no |
| `test/repo/control-text.mjs` | ui | no |
| `test/repo/doc-mutation-lane.mjs` | ui | no |
| `test/repo/dom-charts.mjs` | ui | no |
| `test/repo/em-dash.mjs` | bundle,describe-mcp-assets,ui | no |
| `test/repo/gate-report.mjs` | ui | no |
| `test/repo/ui-polish.mjs` | ui | no |
| `test/smoke/launcher.mjs` | ui | no |
| `test/smoke/smoke.mjs` | bundle,layers,ui | no |
| `test/ui/charts.mjs` | ui | no |
| `test/ui/counts.mjs` | bundle | no |
| `test/ui/persist.mjs` | layer-pins,layers,tonal,ui | no |
| `test/ui/poster-strip.mjs` | ui | no |
| `test/ui/zip.mjs` | ui | no |

## Control: agent-ui T-0060 step 3

Step 3 passed its verifier (`verifier-L2.md`: pass) with its scope list unchanged (no `## Scope widened` section, no blocked builder). Allow-list: `packages/agent-ui/a2ui/src/agent/agent-transport.ts`, `providers/anthropic.ts`, and the new `live-agent/anthropic-terminal-tool.test.ts`. Source paths checked: `agent-transport.ts`, `providers/anthropic.ts` (basenames `agent-transport`, `anthropic`). Base sha `f7ff6c64dc86eedbe864e6eeb9ad5012fbb103ba`.

Test files in the tree at base: 1059. Flagged: 72 (66 code tests, 6 `.spec.md` documents). The same step 4 known misses appear here by coincidence of shared names (2 of 2), which shows how common the basenames are, not a catch. Limit for `build`: 3 or fewer.

| Flagged test | Matched basename | Known miss |
|---|---|---|
| `.claude/docs/spec/a2ui-chat.spec.md` | agent-transport | no |
| `.claude/docs/spec/a2ui-live-agent.spec.md` | anthropic | no |
| `.claude/docs/spec/app-surfaces-m2.spec.md` | agent-transport | no |
| `.claude/docs/spec/capability-availability-tagging.spec.md` | agent-transport | no |
| `.claude/docs/spec/devtools-harness.spec.md` | agent-transport | no |
| `.claude/docs/spec/identity-mock-transport.spec.md` | agent-transport | no |
| `packages/agent-ui/a2a/src/arena-agent/model-seat.test.ts` | agent-transport | no |
| `packages/agent-ui/a2a/src/arena/fixtures.test.ts` | anthropic | no |
| `packages/agent-ui/a2a/src/feed/dev-proxy-plugin.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/a2ui/src/agent/gates.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/agent/response-type.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/catalog/personas/croupier/checks.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/catalog/personas/croupier/recorded-replay.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/catalog/semantic-check.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/corpus-genui/corpus-genui-data.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/layering.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/a2ui-surface-toggle.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/agent-config-schema.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-key-validation.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-request-body.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-retry.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-sse.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-timeouts.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-tool-loop.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/anthropic-usage.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/build-key-safety.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/chat-route.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/dev-proxy-abort.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/dev-proxy-reasoning.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/genui-exclusive.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/genui-produce.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/mcp-enablement.test.ts` | agent-transport,anthropic | yes: mcp-enablement.test.ts |
| `packages/agent-ui/a2ui/src/live-agent/produce-budget-usage.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/produce-loop.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/produce-semantic-checks.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/provider-dispatch.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/providers-config.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/live-agent/round-trip.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/session.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/structural-transcript.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/system-prompt-grammar.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/live-agent/turn-deadline.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/a2ui/src/testkit/offline-wiring.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/src/testkit/producer-leg.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/testkit/scenario.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/testkit/scripted-provider.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/testkit/scripted-tools.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/src/testkit/scripted-transport.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/tools/agent-eval/eval-agent-behavior.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/tools/agent/worker/worker-bundle.test.ts` | anthropic | no |
| `packages/agent-ui/a2ui/tools/corpus-genui/apply.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/tools/corpus-genui/generate.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/a2ui/tools/corpus-genui/judge.test.ts` | agent-transport | no |
| `packages/agent-ui/a2ui/tools/corpus-genui/report.test.ts` | agent-transport | no |
| `packages/agent-ui/app/src/controls/conversation/conversation-composer.test.ts` | anthropic | no |
| `packages/agent-ui/app/src/controls/conversation/conversation.browser.test.ts` | anthropic | no |
| `packages/agent-ui/app/src/controls/conversation/conversation.test.ts` | anthropic | no |
| `packages/agent-ui/devtools/src/capture/format.test.ts` | agent-transport | no |
| `packages/agent-ui/devtools/src/server/harness-plugin.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/devtools/src/timeline/events.test.ts` | agent-transport | no |
| `packages/agent-ui/devtools/src/timeline/turn-usage.test.ts` | agent-transport | no |
| `packages/agent-ui/devtools/src/transports/a2a-peer.test.ts` | agent-transport | no |
| `packages/agent-ui/devtools/src/transports/proxy.test.ts` | agent-transport,anthropic | no |
| `packages/agent-ui/devtools/src/transports/replay.test.ts` | agent-transport | yes: replay.test.ts |
| `site/lib/feed-live-transport.test.ts` | anthropic | no |
| `site/lib/live-proxy-transport.test.ts` | anthropic | no |
| `site/lib/provider-mode-selection.test.ts` | anthropic | no |
| `site/pages/a2a-artifact-feed-live.browser.test.ts` | anthropic | no |
| `site/pages/a2ui-agent.test.ts` | agent-transport | no |
| `site/pages/a2ui-chat.effort-wiring.test.ts` | anthropic | no |
| `site/pages/a2ui-live.effort-wiring.test.ts` | anthropic | no |
| `site/pages/gen-ui-live.live-picker-wiring.test.ts` | anthropic | no |

## Commands run

All read-only; the script lives outside both repositories (`/tmp/t0416/replay.py`, run as `python3 -I`).

```
git -C <repo> ls-tree -r --name-only <base-sha>                       # test-file list per rule above
git -C <repo> grep -lIF <basename> <base-sha> -- <test files>          # one call per source basename
```

- agent-ui step 4: `<repo>` agent-ui, base `0affd8ad`, basenames `produce`, `meta-line`, `session`.
- ultimate-tokens step 2: `<repo>` ultimate-tokens, base `2d218bec`, ten basenames listed above.
- Control, agent-ui step 3: base `f7ff6c64`, basenames `agent-transport`, `anthropic`.
- Locating the evidence: `grep -rl "T-0060" agent-ui/.sdlc --include=handoff.md`, `find` for `builder-L4*.md` under `.sdlc`, `.worktrees`, `.claude/worktrees`.

## Reading

Recall is complete: all four known misses are flagged (2 of 2 on each plan). Precision is not usable. The passing control step flags 72 tests, 66 even with design documents ignored, against a limit of 3. The step 4 plan alone flags 331, so a lint raising this list would bury the two real misses in hundreds of lines. The cause is the basename match: `produce`, `session`, `anthropic` and `ui` are ordinary words that appear in unrelated tests. A tighter rule (import or path references only, not bare basenames) would be a different heuristic and needs its own replay; it is out of scope here and is not filed.

Verdict: do not build
