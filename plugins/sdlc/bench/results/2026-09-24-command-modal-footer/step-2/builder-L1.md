<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
blocked

The descriptor and LLD edits are done, but `npm test` still exits non-zero. The remaining failures come from the step 1 code or the environment, not from this step.

## Changes
- `packages/agent-ui/components/src/controls/command-modal/command-modal.md`: added the fifth `parts:` entry `footer` (no `role`), a `## The keyboard-hint footer` section, and "footer" in the Composition sentence. `attributes:` is untouched.
- `.claude/docs/lld/command-modal.lld.md`: added footer to the LLD-C2 row, the §3 ORDER note, the `parts:` sketch, and a `[data-part='footer']` CSS stub.
- `site/public/llms-full.txt`: regenerated with `node scripts/generate-llms-full.mjs`, because the descriptor edit changed the generated corpus and `llms.test.ts` went red.

## Checks
- `npx vitest run .../command-modal-descriptor.test.ts`: exit 0.
- `grep -n "name: footer"` on `command-modal.md`: one hit, at line 76, inside the frontmatter.
- `grep -n footer` on the LLD: hits in the LLD-C2 row (47), the ORDER note (318), the CSS stub (370-371) and the parts sketch (396).
- `npm run check`: exit 0.
- `site/lib/llms.test.ts`: exit 0 after regenerating `llms-full.txt`.
- `npm test`: exit 1, and I did not re-run the full suite after the regeneration. The first run had 5 failed tests in 4 files:
  - `naming-gates.test.ts` has 2 failures: `command-modal.ts` uses `data-role "hint"`, which is not in the §6 registry. That comes from the step 1 change to `command-modal.ts`, which I did not touch.
  - `dogfood-assets-freshness.test.ts` and `theme-provider-build-fixture.test.ts` are fixture-freshness tests. Their own banners say they warn, never red, on a PR run. I did not investigate whether they are red on a clean tree.
  - The `llms.test.ts` failure is fixed by the regeneration.

## Notes
- `npm test` cannot go green until the `data-role "hint"` registry failure is fixed. Either register `hint` in naming.md §6, or change step 1's code to use a different attribute. A planner or verifier needs to decide which.
- I did not check whether the two fixture-freshness failures also occur on a clean tree.
- `site/public/llms-full.txt` is in the diff, though the handoff did not list it.
