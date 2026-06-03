# Canonical Pattern Index — survey targets for Mode 8 (composite-demo-protocol.md)

**Auto-generated** by `scripts/build-canonical-pattern-index.mjs`. Do not edit by hand — re-run the build script after adding new canonicals to `apps/`, `catalog/`, or `playgrounds/`.

This file is the checked-in snapshot the build script produces; the entries below are **representative** of a typical monorepo state (file lists + line counts will differ on your tree — re-run the build to refresh). The durable content is the **UI-type taxonomy** (the section headers + the lift-guidance under each): that taxonomy is the Phase 2 survey-target schema, and `ui_type` in Phase 1 must resolve to one of these section slugs.

## How to use this index

1. From Phase 1 of [composite-demo-protocol.md](composite-demo-protocol.md), name the UI type.
2. Find the matching section below.
3. Read every `.contents.html` listed (or the closest 2-3 if the section has many).
4. Extract primitive composition per Phase 3 of the protocol.
5. Cite the path in your demo's `<!-- Pattern source: ... -->` comment.

---

## billing

> Billing dashboards (current plan, invoices, payment methods, usage). Lift card-ui + section + col-ui + field-ui chain from billing.contents.html.

- `apps/saas/app/billing/billing.contents.html` (from SaaS app dashboards)
- `apps/user-flow/app/registration/billing/billing.contents.html` (from User-flow templates)

## dashboard

> Admin dashboards (KPI grids, overview cards). Lift grid-ui responsive columns from admin-dashboard.contents.html.

- `apps/saas/app/admin-dashboard/admin-dashboard.contents.html` (from SaaS app dashboards)

## settings

> Settings pages (preferences, security, appearance). Lift card-ui per setting group + col-ui spacing.

- `apps/saas/app/settings-page/settings-page.contents.html` (from SaaS app dashboards)
- `apps/user-flow/app/onboarding/notification-prefs/notification-prefs.contents.html` (from User-flow templates)
- `catalog/ui-patterns/app/settings-appearance/settings-appearance.contents.html` (from UI-pattern atomics)
- `catalog/ui-patterns/app/settings-notifications/settings-notifications.contents.html` (from UI-pattern atomics)
- `catalog/page-shells/app/settings-page/settings-page.contents.html` (from Page-shell templates)

## auth-flow

> Authentication flows (sign-in, MFA, OAuth, password reset). Lift single-column form layout from sign-in.contents.html siblings.

- `apps/user-flow/app/auth/forgot-password/forgot-password.contents.html` (from User-flow templates)
- `apps/user-flow/app/auth/reset-password/reset-password.contents.html` (from User-flow templates)
- `apps/user-flow/app/auth/sign-in/mfa/mfa.contents.html` (from User-flow templates)
- `apps/user-flow/app/auth/sign-in/sign-in.contents.html` (from User-flow templates)
- `apps/user-flow/app/auth/sign-up/mfa-setup/mfa-setup.contents.html` (from User-flow templates)

## onboarding-wizard

> Onboarding multi-step wizards. Lift step-progress + section + cta-row pattern.

- `apps/user-flow/app/onboarding/first-action/first-action.contents.html` (from User-flow templates)
- `apps/user-flow/app/onboarding/welcome/welcome.contents.html` (from User-flow templates)

## registration-wizard

> Registration multi-step flows. Lift wizard step + form composition.

- `apps/saas/app/profile-security/profile-security.contents.html` (from SaaS app dashboards)
- `apps/user-flow/app/auth/sign-up/profile/profile.contents.html` (from User-flow templates)
- `catalog/ui-patterns/app/user-profile-card/user-profile-card.contents.html` (from UI-pattern atomics)

## list-with-detail

> List + detail compositions (entity rows + drawer/modal detail). Lift entity-item + drawer pattern.

- `apps/saas/app/members/members.contents.html` (from SaaS app dashboards)
- `catalog/ui-patterns/app/users-table-badge/users-table-badge.contents.html` (from UI-pattern atomics)

## integrations-list

> Searchable integration/connector grids. Lift grid-ui + card-ui + empty-state-inside-card pattern.

- `apps/saas/app/integrations/integrations.contents.html` (from SaaS app dashboards)
- `apps/user-flow/app/registration/integrations/integrations.contents.html` (from User-flow templates)

## agent-activity

> Agent activity / reasoning feeds. Lift activity-feed scroll + collapsed-reasoning pattern.

- `catalog/ui-patterns/app/agent-activity-feed/agent-activity-feed.contents.html` (from UI-pattern atomics)
- `catalog/ui-patterns/app/agent-reasoning-collapsed/agent-reasoning-collapsed.contents.html` (from UI-pattern atomics)
- `catalog/page-shells/app/agent-canvas/agent-canvas.contents.html` (from Page-shell templates)

## chat

> Chat surfaces (thread, composer, sidebar). Lift chat-streaming-surface composition.

- `apps/genui/app/factory-chat/factory-chat.contents.html` (from GenUI app routes)
- `catalog/ui-patterns/app/chat-streaming-surface/chat-streaming-surface.contents.html` (from UI-pattern atomics)
- `catalog/page-shells/app/chat-page/chat-page.contents.html` (from Page-shell templates)

## editor

> Editor panes (code, preview, toolbar). Lift editor-shell composition.

- `apps/genui/app/a2ui-editor/a2ui-editor.contents.html` (from GenUI app routes)
- `catalog/ui-patterns/app/editor-code-pane/editor-code-pane.contents.html` (from UI-pattern atomics)
- `catalog/page-shells/app/editor-page/editor-page.contents.html` (from Page-shell templates)

## kanban

> Kanban / column-based boards. Lift kanban-board-3col pattern.

- `catalog/ui-patterns/app/kanban-board-3col/kanban-board-3col.contents.html` (from UI-pattern atomics)
- `catalog/page-shells/app/kanban-page/kanban-page.contents.html` (from Page-shell templates)

## data-table

> Data tables with badges/inline actions. Lift users-table-badge composition.

- `apps/user-flow/app/onboarding/import-data/import-data.contents.html` (from User-flow templates)

## command

> Command palette / global search. Lift command-palette overlay pattern.

- `catalog/ui-patterns/app/command-palette/command-palette.contents.html` (from UI-pattern atomics)

## overlay

> Modals, drawers, popovers. Lift destructive-confirm-modal pattern for confirmations.

- `apps/user-flow/app/registration/confirmation/confirmation.contents.html` (from User-flow templates)
- `catalog/ui-patterns/app/destructive-confirm-modal/destructive-confirm-modal.contents.html` (from UI-pattern atomics)

## multi-step-funnel

> Multi-step conversion funnels. Lift conversion-funnel-6step composition.

- `catalog/ui-patterns/app/conversion-funnel-6step/conversion-funnel-6step.contents.html` (from UI-pattern atomics)

## feed

> Activity / event feeds. Lift activity-feed composition.

- `apps/genui/app/gen-ui-feed/gen-ui-feed.contents.html` (from GenUI app routes)

## marketing

> Marketing pages, hero CTAs. Lift marketing-hero-cta composition.

- `catalog/ui-patterns/app/marketing-hero-cta/marketing-hero-cta.contents.html` (from UI-pattern atomics)
- `catalog/page-shells/app/marketing-page/marketing-page.contents.html` (from Page-shell templates)

## error-page

> Error states (404, 500, forbidden, expired). Lift centered single-card error pattern.

- `apps/user-flow/app/auth/account-locked/account-locked.contents.html` (from User-flow templates)
- `apps/user-flow/app/auth/session-expired/session-expired.contents.html` (from User-flow templates)
- `catalog/page-shells/app/error-page/error-page.contents.html` (from Page-shell templates)

## demo-playground

> Internal demo + playground surfaces. Use these as reference for composition style; not always production-grade.

- `apps/genui/app/a2ui/a2ui.contents.html` (from GenUI app routes)
- `apps/genui/app/css-channel-demo/css-channel-demo.contents.html` (from GenUI app routes)

## other

> Misc canonicals. Inspect contents.html to determine UI type.

- Any `.contents.html` whose slug fragment matches none of the heuristics above lands here. Inspect each to determine its UI type, or extend the `inferUiType()` regex (see Maintenance).

---

## Maintenance

Re-build this index:

```bash
node scripts/build-canonical-pattern-index.mjs
```

If a heuristic misclassifies a path (the file lands in `other` or the wrong UI type), update the `inferUiType()` regex in `scripts/build-canonical-pattern-index.mjs`.
