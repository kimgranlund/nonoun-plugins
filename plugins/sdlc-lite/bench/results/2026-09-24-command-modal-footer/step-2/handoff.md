## Task goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

## Step 2: Clear the naming-gate red and refresh the derived fixtures
level: L2
### Do
The working tree already carries the verified step-1 footer (`command-modal.ts` + `command-modal.css`) and the verified descriptor/LLD/`llms-full.txt` edits. Do not redo them. Only this remains:

- `packages/agent-ui/components/src/controls/command-modal/command-modal.ts`, line 169: delete `hint.setAttribute('data-role', 'hint')`. `hint` is not in the naming.md §6 `data-role` registry (`naming-gates.test.ts` Gate 3, `ALLOWED_ROLES`), and the footer needs no content-model role: `command-modal.css` targets only `[data-part='footer']` and its `kbd`, never `[data-role='hint']`. Keep the `<span>` + `<kbd>` structure, the `aria-hidden="true"`, the append order and the `#footer` guard as they are. Do not register `hint` in `naming.md` (a new role needs a descriptor `contentModel` entry plus the registry line; this footer is control-created anatomy, not an author hook).
- Then, in this order, regenerate the two byte-identical build fixtures that now drift because the site bundle embeds `command-modal.css`/`.ts` (their banners say a local `npm test` keeps the strict byte check; only a `pull_request` CI run warns):
  - `npm run regen:theme-provider-fixture` (rewrites `site/lib/__fixtures__/theme-provider-built.css`)
  - `npm run regen:dogfood-assets` (rewrites `packages/agent-ui/components/src/controls/sandbox-frame/dogfood/dogfood-assets.ts`)
  Run both AFTER the `.ts` edit, never before, or the dogfood module drifts again. Do not hand-edit either output.
- Run `npm test` and `npm run check`; judge by exit code only.
### Acceptance criteria
- `grep -nE "data-role['\"]?\s*,\s*['\"]hint|data-role=['\"]?hint" packages/agent-ui/components/src/controls/command-modal/command-modal.ts` prints nothing (exit 1).
- `npx vitest run packages/agent-ui/components/src/controls/naming-gates.test.ts` exits 0.
- `npx vitest run site/lib/theme-provider-build-fixture.test.ts packages/agent-ui/components/src/controls/sandbox-frame/dogfood/dogfood-assets-freshness.test.ts` exits 0 with `GITHUB_EVENT_NAME` unset.
- `npx vitest run packages/agent-ui/components/src/controls/command-modal/` exits 0.
- In jsdom (throwaway check, deleted afterwards): a connected `<ui-command-modal>` has exactly one `[data-part="footer"]`, it is `[data-part="dialog"]`'s `lastElementChild`, has `aria-hidden="true"`, three `span` children each containing a `kbd`, text containing "Navigate", "Select", "Close", and no descendant carries a `data-role` attribute.
- `npm test` exits 0.
- `npm run check` exits 0.
- `git status --short` (ignoring `.sdlc/`) lists exactly: `command-modal.ts`, `command-modal.css`, `command-modal.md`, `.claude/docs/lld/command-modal.lld.md`, `site/public/llms-full.txt`, `site/lib/__fixtures__/theme-provider-built.css`, `packages/agent-ui/components/src/controls/sandbox-frame/dogfood/dogfood-assets.ts`; no `*.test.ts` appears.
- `git diff packages/agent-ui/components/src/controls/command-modal/command-modal.ts` still touches no line of `static props`.
