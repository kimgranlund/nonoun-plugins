<!-- role=builder level=L2 model=opus effort=low -->
## Status
inherited red: site-nav.browser.test.ts "renders section context-labels and the wide name|tag row" (chromium + webkit); theme-provider-build-fixture.test.ts; dogfood-assets-freshness.test.ts; site-shard page flows (credentials, otp-signin, swiper-item-demo)

## Changes
- site/public/llms-full.txt: regenerated with `node scripts/generate-llms-full.mjs` so it picks up the command-modal.md footer docs from steps 1 to 3.

## Checks
- `npm run check` at head: exit 0.
- `npm test` at head, before regenerating: exit 1, 3 failures:
  - llms.test.ts (caused by this change)
  - theme-provider-build-fixture.test.ts
  - dogfood-assets-freshness.test.ts
- The same 3 files run with vitest at base 220ae0ac: theme-provider-build-fixture and dogfood-assets-freshness fail there too, so they are inherited. llms.test.ts passes at base.
- `npx vitest run site/lib/llms.test.ts` after regenerating: 7/7 pass. I did not rerun the whole `npm test`. The only remaining reds should be the 2 inherited fixture tests.
- `npm run test:browser:packages:components` at head: exit 1, 2 failures, both site-nav.browser.test.ts (chromium, webkit). At base: exit 1, 5 failures, which include the same 2 site-nav tests plus 3 choice-card tests. Head adds nothing new.
- `npm run test:browser:site` at head: exit 1, 4 failures:
  - otp-signin ×2 (chromium)
  - swiper-item-demo (chromium)
  - credentials (webkit)

  At base: exit 1, 14 failures, including the same files: credentials, otp-signin, swiper-item-demo, magic-link and onboarding. None of them touch command-modal or command-palette.
- `npm run test:browser` at head: exit 1, 2 unique failures (site-nav). At base: exit 1, 5 unique failures. `comm -23 head base` is empty, so head has no new failures.

## Notes
- Both runs of `npm run test:browser` (head and base) stopped at the red packages:components shard. The later shards were covered only by the separate `test:browser:site` runs.
- The site-shard page-flow failures change from run to run and the machine load average was about 55. They look like contention flakes, and they fail at base too.
- No command-modal or command-palette test failed in any gate.
- I symlinked node_modules into the base worktree and removed the worktree when done.
