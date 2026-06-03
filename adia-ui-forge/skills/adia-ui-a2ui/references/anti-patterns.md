# Reference: Anti-pattern catalogue — pipeline-side rules + tuning

**Source:** Absorbed from the former `adia-ui-training` skill (§Anti-pattern catalogue + §Anti-patterns for this skill) — Phase 3 rollup. **Used by:** mode 8 of `adia-ui-a2ui` (tune anti-pattern catalogue). **Companion:** `mcp-pipeline-ops.md`, `eval-diagnostics.md`.

---

## Anti-pattern catalogue

`check_anti_patterns` runs eight checks against rendered HTML:

- `noBareDivs` — use a layout component (`col-ui`, `row-ui`, `grid-ui`, `stack-ui`).
- `noBareInputs` — use `input-ui` / `select-ui` / `check-ui`.
- `cardStructure` — flags incorrect nesting (section > header, etc.).
- `columnWrap` — section content must be wrapped in `col-ui`.
- `noHardcodedColors` — no hex/rgb in inline `style` attributes.
- `noInlineLayout` — no `display: flex` / `grid` in inline styles.
- `noInventedComponents` — every `*-ui` tag must exist in the catalog.
- `slotOnContainer` — `slot` attributes belong on content elements, not containers.

## Anti-patterns for this skill

- **Don't bypass `validate_schema`.** A low structural score usually explains anti-pattern findings; fix the JSON before chasing HTML-level issues.
- **Don't submit feedback on stub outputs.** When the Anthropic key isn't loaded, `thinking` mode silently falls back to `StubLLMAdapter` and returns a canned 6-component card. Feedback on that is noise — check the output shape first.
- **Don't commit intermediate JSON to the repo.** Scratch files go under `/tmp` or `.gitignore`d paths. The repo's training corpus is under `packages/a2ui/corpus/patterns/` and is pipeline-generated from HTML sources via `npm run pipeline`.
