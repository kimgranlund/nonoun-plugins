<!-- role=builder level=L1 model=sonnet effort=low -->
All acceptance criteria pass.

## Status
done

## Changes
- packages/agent-ui/components/src/controls/command-modal/command-modal.md: added `footer` part entry (no role) under `parts:`, mentioned footer in the Composition bullet, added a new "The keyboard-hint footer" prose section
- packages/agent-ui/components/src/controls/command-modal/command-modal-descriptor.test.ts: extended parts `arrayContaining` list with `'footer'`
- .claude/docs/lld/command-modal.lld.md: updated LLD-C2 row and LLD-C11 row to mention the footer, updated the `modal.append(...)` snippet, added `footer` to the abbreviated `parts:` list, added a new `## 9 · Amendments` section recording the 2026-09-27 footer amendment

## Checks
- `awk '/^parts:/,/^customStates:/' .../command-modal.md | grep -q -- '- name: footer'` → pass
- `grep -q "'footer'" .../command-modal-descriptor.test.ts` → pass
- `grep -q footer .claude/docs/lld/command-modal.lld.md` → pass
- `npx vitest run .../command-modal-descriptor.test.ts .../naming-gates.test.ts` → 2 files, 99 tests passed, exit 0

## Notes
None
