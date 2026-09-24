<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `packages/agent-ui/components/src/controls/command-modal/command-modal.ts`: deleted `hint.setAttribute('data-role', 'hint')` (was line 169). The span/kbd structure, `aria-hidden`, append order and `#footer` guard are unchanged.
- `site/lib/__fixtures__/theme-provider-built.css`: regenerated with `npm run regen:theme-provider-fixture`, run after the `.ts` edit.
- `packages/agent-ui/components/src/controls/sandbox-frame/dogfood/dogfood-assets.ts`: regenerated with `npm run regen:dogfood-assets`, run after the theme fixture.

## Checks
- `npm run regen:theme-provider-fixture`: exit 0
- `npm run regen:dogfood-assets`: exit 0
- The `data-role ... hint` grep on `command-modal.ts`: no output, exit 1 (the expected result)
- `npx vitest run .../naming-gates.test.ts`: exit 0
- `env -u GITHUB_EVENT_NAME npx vitest run site/lib/theme-provider-build-fixture.test.ts .../dogfood-assets-freshness.test.ts`: exit 0
- `npx vitest run packages/agent-ui/components/src/controls/command-modal/`: exit 0
- Throwaway jsdom test (written as `command-modal/zz-throwaway.test.ts`, deleted after the run): exit 0. It checked every item in that acceptance line: exactly one footer, footer is the dialog's `lastElementChild`, `aria-hidden="true"`, 3 spans each with a `kbd`, text contains Navigate, Select and Close, and no descendant has `data-role`.
- `npm test`: exit 0
- `npm run check`: exit 0
- `git status --short` without `.sdlc/`: shows exactly the 7 expected files and no `*.test.ts`.
- `git diff command-modal.ts | grep props`: no match, so no line of `static props` was touched.

## Notes
None
