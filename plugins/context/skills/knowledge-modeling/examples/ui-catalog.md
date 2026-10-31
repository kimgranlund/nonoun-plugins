# UI catalog: shared behavior, different contracts

This is an authored illustration using synthetic systems, releases and records.
It reports no vendor facts, browser measurements or evaluation results.

## Request and source material

“List components that reveal an associated content section, and determine whether
their published sizes can share a comparison column.” The local catalog defines
`pattern:disclosure` as a control that changes the visibility of its associated
section; it makes no claim about grouping or exclusive expansion.

| Source record | Native assertion |
| --- | --- |
| `iris:r2/fold-doc` | Fold has a trigger and panel; activating the trigger toggles that panel. Its trigger CSS declares `min-height: 2rem`. |
| `sable:r4/section-doc` | Section's trigger toggles its panel; Section operates within an Accordion group that permits only one expanded section. Trigger CSS declares `height: 32px`. |
| `demo:assembly-v1` | The illustrative Fold instance `demo:fold-a` contains trigger `demo:trigger-a` and panel `demo:panel-a`. No rendering evidence or root-font value is supplied. |

## A sufficient model

Keep a small authored registry and a mapping decision table. The generated catalog
page is a projection of those inputs; its text is not a second editing authority.

| Identity | Kind and meaning |
| --- | --- |
| `pattern:disclosure` | Catalog concept, defined above |
| `iris:r2/fold` | Release-specific component type described by `iris:r2/fold-doc` |
| `sable:r4/section` | Release-specific component type described by `sable:r4/section-doc` |
| `demo:fold-a` | Illustrative component instance, `instance_of iris:r2/fold` |
| `demo:trigger-a` | Illustrative trigger instance, `part_of demo:fold-a` according to the assembly record |

`implements_pattern` relates a component type to the behavior it implements.
Both component types implement `pattern:disclosure` under this catalog's definition.
`requires_container` separately records Section's Accordion requirement. Neither
relation means that the two component types are interchangeable implementations.

## Decisions and neighboring failures

| Decision | Outcome and evidence |
| --- | --- |
| Include both types in the disclosure discovery list | Supported by the two behavior descriptions and the catalog definition |
| Substitute Fold for Section in an exclusive group | Unsupported: shared behavior classification does not preserve Section's container contract |
| Treat the trigger as a subtype of its containing Fold | Invalid: the assembly asserts composition between instances, not subclassing |
| Compare both values as measured height | Unsupported: one is a CSS minimum, one a CSS declared height, and neither is a measurement |
| Convert Iris's minimum to pixels | Unknown until the applicable root-font value is evidenced; the declared value remains `2rem` |

If Iris release 3 introduces a fixed height, add that release's assertion and
evidence. Retain the release 2 minimum and its unresolved conversion. A newer
value must not rewrite an older comparison or silently change its property.

A schema can check record shape and units; a semantic check must distinguish
minimum, declared and measured properties. The catalog does not execute the
components or enforce their runtime behavior.

Use [identity](../references/identity.md), [relationships](../references/relationships.md),
[mappings](../references/mappings.md), and [evidence](../references/evidence.md) for the reusable method.
