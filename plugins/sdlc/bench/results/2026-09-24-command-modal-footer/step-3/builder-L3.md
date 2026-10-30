<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
None. No source change was needed. I wrote a throwaway probe, `packages/agent-ui/components/src/controls/command-modal/zz-footer-probe.browser.test.ts`, ran it and deleted it. The working tree still holds only the seven files from steps 1 and 2.

## Checks
- 🟢 `npx vitest run --config vitest.browser.config.ts --project packages packages/agent-ui/components/src/controls/command-modal/command-modal.browser.test.ts`: exit 0. 2 test files passed (chromium + webkit), 30 tests passed, 0 failed.
- 🟢 Throwaway geometry probe, same project: exit 0, 2 files, 4 passed (2 cases × 2 engines).
  - Case 1: palette open with `zzzz-no-match` typed. The probe also asserted that 0 options were left visible.
  - Case 2: the 40-option list. The probe also asserted that the list really overflows.
  - Both cases asserted `footer.height > 0`, `footer.top >= list.bottom - 1` and `footer.bottom <= dialog.bottom + 1`.
  - After deletion, `ls` of the command-modal dir shows no `zz-*` file.
- 🟡 Scoped shard, first run (`... --project packages .../src/controls .../src/dom .../src/traits`): exit 1. 1 failed, 2403 passed, 2 skipped. The failure was `combo-box.browser.test.ts` (webkit), "overflows for real, scrolls, and computes the thin/at-rest-transparent/reveal-on-hover treatment": it ran 25109 ms and a screenshot timed out. Load average was about 78.
- 🟢 `combo-box.browser.test.ts` run alone: exit 0, 112/112 passed. That makes the first-run failure contention, not a regression.
- 🟢 Scoped shard re-run: exit 0. 170/170 files, 2404 passed, 2 skipped (2406 tests, above the 2000 floor). 2406 is the full shard's 2412 minus site-nav's 6 tests.
- 🟢 `find packages/agent-ui/components/src -maxdepth 1 -name '*.browser.test.ts'` printed only `packages/agent-ui/components/src/site-nav.browser.test.ts`.
- 🟢 Sitemap check, `node -e "...filter(e=>e.section==='Components'&&!e.group).length===0..."`: exit 0. All 84 Components entries carry a `group`.
- 🟢 `git status --short -- site/sitemap.json site/pages/_page.ts packages/agent-ui/components/src/site-nav.browser.test.ts`: printed nothing.
- 🟢 `npx vitest run --config vitest.browser.config.ts --project packages packages/agent-ui/components/src/site-nav.browser.test.ts`: exit 1 as expected, 2 failed and 4 passed of 6.
  - Both failures are `renders section context-labels and the wide name|tag row (proper name + trailing data-role="tag")`, one in chromium and one in webkit.
  - Both fail with `expected [ 'Feed & status', …(23) ] to include 'Components'`.
- 🟢 `npm run check`: exit 0.
- 🟢 `git status --short | grep -v '^?? .sdlc'`: lists exactly the seven files named in the handoff, and no `*.test.ts`. So `npm test` and the two regen scripts were not required, and I did not run them.
- 🟢 `git diff` of `command-modal.ts`: no changed line touches `static props` (line 45) or the `const props` object (line 24). The changes are the header comment, the `#footer` field, the footer build, and the `modal.append` call.

## Notes
- Pre-existing red for the filer's follow-up issue:
  - File: `packages/agent-ui/components/src/site-nav.browser.test.ts`
  - Test title: `site nav — ui-nav-rail structure (both engines) > renders section context-labels and the wide name|tag row (proper name + trailing data-role="tag")`
  - It fails in chromium and webkit at the line-92 assertion `expect(labels).toContain('Components')`.
  - Cause: `site/pages/_page.ts` `buildNav()` names each rail group with `entry.group ?? entry.section` (line 1121). Since commit `6ea5c5e3` (GH #1616, the sitemap reorganization), all 84 `Components` entries in `site/sitemap.json` carry a `group`, so no context-label can ever read "Components".
  - It reproduces at HEAD `220ae0ac`, and none of the three involved files are modified in this tree.
- The scoped shard leaves out only `site-nav.browser.test.ts`. That omission is the only reason this step's shard can go green. The full `npm run test:browser:packages:components` stays red until the follow-up lands.
- Host load average ran from about 30 to 110 during the runs.
- `.sdlc/.../step-3/builder-L3.running` was left in place for the runner to handle.
