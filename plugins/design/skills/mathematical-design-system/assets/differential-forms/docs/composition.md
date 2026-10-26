# Composition and inheritance

Read contracts/composition.json before composing new families. One base unit and border setting are shared in this version. Control, collection and card densities are separate inputs; control and container curvature are separate selections.

A slot defines alignment. Artwork defines visible size. A badge is a compact content box, not an icon slot. A label wrapper defines text alignment and exposed edge compensation. Preserve these identities when the DOM implementation changes.

## Input grammar
Neutral wrapper → optional leading prefix/selector/icon slot → input label wrapper → optional suffix/action/stepper pair. A recipe may contain both prefix and suffix. Every interactive child receives its own accessible name. Fixed adornments do not become part of the editable value; accessible names or descriptions include units where necessary. Placeholder is a hint, never the sole name.

## Control grammar
Button → optional leading slot → optional label → optional trailing slot. At least visible text or an accessible name is required. Do not insert a selector, remove button or stepper inside a button. Removable chip: span → label + remove button. Filter chip: button with noninteractive icon and label.

## Composite grammar
Parent owns background, outer border, requested inset, gap, clipping and outer curvature. Direct children use resolved residual geometry. Do not pass residual inset through grandchildren repeatedly. Each internal slot still owns its declared border budget. Parent border is deducted only through D, not from the same slot a second time.

For listbox and attached groups use direct children without independent outer margins. For cards, normal document layout remains appropriate. An attached group is not a free-floating group of independently rounded buttons.

## Layout grammar
Table uses shared columns. Collection record uses flexible copy and fixed leading/trailing parts. Row wrapping must retain readable content and permit height growth. The specimen switches input grids to one column and allows collections to wrap; breakpoints are specimen implementation details, not universal viewport contracts.

Page and section layout are responsible for independent component gutters. A component must not include external margin in its reusable size calculation. Layout defaults are starting values, not constraints on application architecture.

## Composed input boundary
Use resolveComposedInput for chip-adorned inputs. Prefix/suffix spans and selector buttons all contain real chip label wrappers. An interactive selector owns its label and caret only; its popup is a sibling, never inside the trigger button. Resolve that popup with resolveComposite({childFamily:'chip'}). This popup is one composite level; the neutral input wrapper is not an attached composite.

Multiline content rows use resolveMultiline with collection density/container curvature. They do not inherit composite inset or control density. Collection copy is not an exposed single-line label and has zero label edge compensation.
