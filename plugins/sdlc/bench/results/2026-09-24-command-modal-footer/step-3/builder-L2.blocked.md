<!-- role=builder level=L2 model=opus effort=low -->
## Status
blocked

## Changes
None. The step required no source change. I created a throwaway probe `packages/agent-ui/components/src/controls/command-modal/zz-footer-probe.browser.test.ts` and deleted it after the run.

## Checks
- 🟢 `npx vitest run --config vitest.browser.config.ts --project packages .../command-modal.browser.test.ts`: exit 0. 2 files (chromium + webkit), 30/30 passed, including the TKT-0017 fixed-frame test.
- 🟢 Throwaway probe in the same project: exit 0, 4/4 passed (2 cases × chromium + webkit):
  - Case 1: palette open with `zzzz-no-match` typed.
  - Case 2: the 40-option list.
  - Both cases asserted footer `height > 0`, `footer.top >= list.bottom - 1` and `footer.bottom <= dialog.bottom + 1`.
- 🔴 `npm run test:browser:packages:components`: exit 1. 2 failed out of 2412 tests. Both failures are `site-nav.browser.test.ts` > "renders section context-labels and the wide name|tag row", chromium + webkit, with `expected [ 'Feed & status', …(23) ] to include 'Components'`.
  - It also fails when run alone (exit 1).
  - It fails on the base commit 220ae0ac too, with every step 1-3 change stashed out (exit 1), so the failure predates this task and command-modal did not cause it.
- 🟢 `npm test`: exit 0 (617 files passed, 1 skipped).
- 🟢 `npm run check`: exit 0.
- 🟢 `git diff --stat`: no `*.test.ts` changed.

## Notes
- The only unmet acceptance criterion is the components browser shard exiting 0. The cause is a deterministic `site-nav.browser.test.ts` failure that already exists on HEAD 220ae0ac: the site nav has no 'Components' section label.
- It is outside this step's file scope (`command-modal.ts`/`.css` only), so I did not touch it. The planner decides whether to accept the failure as known debt or route it as a separate ticket.
- Every command-modal footer criterion passed in both engines. The footer needed no change, so I did not run the regen steps.
- Host load average was about 130 during the runs, but this failure does not depend on load: it fails the same way run alone.
