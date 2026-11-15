# Icons

Spec 6. Written on 2026-11-13. It is the icon contract the plan asked for: how an icon is drawn, where its glyph comes from, and how a kit uses another icon library. Its decisions, D85 to D88, were made under the author's standing instruction to complete the work without stopping for confirmation.

## The contract

An icon is one element, the icon component, with a `name`. The kit draws it with CSS alone: the element is a square box painted in the ink, seen through the icon as a mask. The mask image for each name is in `kit/styles/icons.css`, which `scripts/icons.mjs` generates from SVG files.

An icon library is a folder of SVG files, one per icon. `kit/styles/kit.config.json` names the folder under `icons.source` and, under `icons.names`, maps each name the kit uses to a file in it. The default is a subset of Phosphor's regular weight in `kit/icons/phosphor`. A kit that uses another library points `source` at its folder and changes the file names; the names the kit uses stay the same, so no component and no page changes.

```html
<ui-button>Actions <ui-icon name="chevron-down"></ui-icon></ui-button>
<ui-button aria-label="Close"><ui-icon name="close"></ui-icon></ui-button>
```

## Rules

| # | Rule | Basis | Check |
|---|---|---|---|
| I1 | An icon shall be painted by CSS alone, as a mask over a box in the ink. No script shall draw it, so it is painted before the component is defined, and defining the component shall change neither its box nor its paint. | D85; U1, U2 | Recipe test before and after the element is defined, in three engines |
| I2 | `kit/styles/icons.css` shall be exactly what `scripts/icons.mjs` generates from the SVG files that `kit.config.json` names: one rule per name, in the `tokens` cascade layer, and no icon the config does not name. | D86, D87; one home per fact | `node scripts/icons.mjs --check`, and a test with a stale copy |
| I3 | The generator shall refuse a name whose file is missing, and a file that is not one `svg` element with a `viewBox`. | A mask needs a box to scale | Generator test with a broken file |
| I4 | An icon shall take the ink of the element it sits in, at rest and in every state of that element, and its ink can be set with `--icon-ink`. | ui-materials: a mark is printed in the ink of its face | Recipe test inside a button, a disabled button and a selected tab |
| I5 | In forced colours an icon shall show in the system colour of the text around it: `CanvasText` on the page, `HighlightText` on a highlighted part, `GrayText` when its control is disabled. | D15; a background colour is forced away in that mode | Recipe test under forced-colours emulation in three engines |
| I6 | An icon shall be a square of one of ui-geometry's four icon sizes, `md` unless the `size` attribute says otherwise, or of `--icon-height`. It shall not shrink or stretch in a flex row. | ui-geometry: icon sizes a.sm, a.md, a.lg, a.full | Layout test at each size and at each density |
| I7 | An icon whose `name` the kit does not have shall paint nothing and keep its box. | A missing icon must not show as a filled square | Recipe test |
| I8 | The icon component shall write `aria-hidden="true"` on an icon the author gave no name, and `role="img"` on one that has `aria-label` or `aria-labelledby`. It shall write neither over what the author wrote. | WAI: a decorative image is hidden; D9 | Test of each case |

## Why a mask

- **It is painted before any script.** The kit's rule for every component (U2) holds for icons with no exception, and an icon never flashes in.
- **It takes the ink for free.** A data-URI image cannot read a CSS variable; a mask in the current colour can. ultimate-tokens ships its select caret once per scheme for that reason.
- **Any library works.** The generator needs an SVG file with a `viewBox`. It needs no shared grid, no weight names and no JavaScript module per icon.
- **Only named icons ship.** agent-ui loads a 41 KB pack whole; here the stylesheet holds the icons the config names and no others.

The cost is one ink per icon. A picture with several colours is not an icon in this sense; the author writes an inline `svg` for it.

## Open

- **The checkbox draws its own check and dash.** Its recipe was written before this contract and holds the two glyphs itself. It could read them from `icons.css`, so that a kit with another library also changes the checkbox's glyphs.
- **A name that changes after connect** repaints through CSS at once. A label that is added after connect is not seen by the component (I8 is applied when it connects).
