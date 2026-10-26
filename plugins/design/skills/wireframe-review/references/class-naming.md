# Recipe class names

Version 4 uses recipe__slot classes exclusively for shared recipe anatomy.
Names are kebab-case on both sides of the double underscore. Examples:
button__root, input-group__body, select__root, menu__trigger, menu__content.

There is no compatibility alias table and no selector rewriting in getAssetBundle.
compileControls normalizes duplicate classes but never adds another naming system.
Native/ARIA attributes own state. Use finite data attributes for appearance and
context, data-action for action dispatch, and --ui-* for shared semantic variables.
Derived geometry remains in --g-*; geometry formulas are not duplicated per recipe.

Site slot inventory and enforcement live in
../../../../Projects/ui-kit/apps/site/checks/recipe-naming.json and
../../../../Projects/ui-kit/apps/site/checks/check-recipe-naming.mjs.
The site architecture policy is documented in its docs/recipe-naming.md.

This is a breaking styling/action-hook API change. Historical review artifacts
remain evidence of their captured version and are not migrated or current proof.
