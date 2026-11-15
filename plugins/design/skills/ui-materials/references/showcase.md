# Showcases: the material brief

This file is the brief: what a material showcase must show and prove. The canvas, its packing, its switches and its in-page
checks belong to **ui-showcase-bento**, whose `ui-materials` source points here; build there, and use this file for the
content and acceptance.

Two kinds of showcase prove a material system:

1. **A material specimen sheet**: the same component specimens in each material. It proves the components.
2. **A project showcase**: a small, complete demo built only from a component library. It proves the library and the
   materials together in a real composition.

In both, **ui-geometry supplies every length**, and this skill supplies each part's attributes and the paint.

## Controls every showcase has

Three tiers, laid out so the hierarchy shows. A material is a name for one combination of the settings, so the two must
never look like peers, and nothing that only changes the view sits among them.

1. **Material**, the primary control: Flat, Physical, Frosted glass, Glass, Outline, plus a **Custom** state. Picking a material
   sets the four settings. A material shows as selected only while all four match it; otherwise Custom shows as selected.
   Custom is a state that can't be pressed, because a custom mix is reached by changing a setting.
2. **The four settings**, directly under the material, as its expansion ("Glass = lighting lit · transmission clear · …"),
   each editable: lighting, transmission, delineation, chroma. Print their values in their code spelling (lowercase,
   monospace), so the value `frosted` is never mistaken for the material Frosted glass. This tier is what shows the system
   composes.
3. **The view**, set apart (its own group, divided from the material): scheme (light, dark, or the palette's modes when
   ui-colors provides them), size and shape if the system has them, and the anatomy overlay: `off`, `layer`, `relief` or
   `face` ([terms.json](terms.json) › `sets.anatomy`). Each part gets a dashed outline coloured by the chosen attribute, with
   a legend. It is drawn as an `outline` with a negative offset, so it changes no box.

State the settings once per view. The caption a sheet prints ("Glass: lit · clear · fill · colour") is for a sheet without
these controls; a board that has them leaves the caption out. Every showcase keeps **a lens readout** wherever clear
transmission is on: "LENS ON" or "LENS OFF".

Where a showcase must prove the paint itself, it adds **an exploded part**: one real part with an overlay over its corner,
taken apart along the depth axis, each measured piece of paint on a sheet of its own by kind (backdrop filter, cast, face,
line, shading, bevel, recess, cover, rim, glow; construction.md › Enforcing it, item 5), read from the setting tables and
not listed by hand. A sheet the material does not draw stays as an empty outline labelled "not in this material".

## 1. Material specimen sheet

**Content and geometry** come from ui-geometry's default showcase brief (`ui-geometry/references/showcase.md`): 24 ARIA
patterns in eight groups, with its required anatomy, states, geometry table and canvas. Don't re-derive or alter it. The
brief's Type and Space groups are marks and lengths: they take no paint of their own.

This skill adds:
- **One sheet per material preset**, same canvas, layout and content, so they can be compared side by side or by flicking between them.
- **Both schemes.**
- **A backdrop for transmission**: the regions holding overlays (menu, combobox list, tooltip, dialog, alert dialog) get
  coloured, high-contrast content under them in every material: large shapes (frost turns them into a glow) and fine lines
  such as grid paper (clear glass keeps them, and the lens bends them).
- **A material comparison holds the base constant.** One housing in one material and one backdrop in every tile; only
  the floating part (a round overlay body shows the rim best) takes each material, including each transmission value.
  The backdrop has contrast and features coarser than the frost blur.
- **State moves** shown next to rest: pressed beside rest, latched beside off, lamp on beside lamp off.
- **The state table** printed with the state moves: the system's one table (construction.md › The system's state table), each row beside its specimen in the material shown, so a reader checks the table against the render.
- **A caption per sheet** naming its settings, e.g. "Glass: lit · clear · fill · colour", on any sheet without the controls above.

## 2. Project showcase (a playground demo)

An app-like scene someone would open to see what the system can build: a synth, a mixer, a media library, a dashboard,
a chat client, a settings screen, a phone flow.

### Brief template

```
Title          one name, 2–4 words
Demonstrates   which reliefs, faces, layers and settings it exercises, in one sentence
Scene          what the person sees and can do (2–4 sentences); one primary task
Components     the library components used (public exports only)
Overlays       which layers float over content, and what content scrolls under them
Sizes          desktop and/or touch (touch = the system's large size)
Not included   anything explicitly out of scope
```

### Rules

- **Library only.** Import the component library's public entry points as an outside user would: no deep imports, no copied
  internals. Local CSS is for **layout** only. If a demo needs new paint, the library is missing a token or component, so add it there.
- **Every attribute value appears.** The scene has a ground, raised parts, recessed parts, a display, solid faces,
  emissive faces and holes, and at least one overlay over **scrolling, colourful** content.
- **One primary task**, real-looking content, no lorem ipsum, no fake metrics dressed up as real data.
- **Works with every combination of settings.** Nothing in the demo branches on the material.
- **Accessible as shipped**: a keyboard path through the primary task, visible focus, the components' own ARIA.

### Layout

- Page margin, gutter, columns and breakpoints from ui-geometry's layout tier. The scene sits on the base ground.
- Group with ui-geometry's spacing ladder. Use recessed wells to hold groups of values, and panels to hold groups of controls.
- Touch versions use the large size and keep interactive parts out of safe areas. Bars that content scrolls under are overlays.

### Verification matrix

Render every material preset × scheme (× size), plus at least Flat + frosted and Physical + mono, headlessly, and fail on:

- a page error or a failed request
- horizontal overflow, or a part clipped by its container
- any part's box differing between materials at the same scheme and size (script below, or ui-showcase-bento's `uiBentoCheck()`)
- a part whose tokens disagree with its attributes, or an overlay missing one of its three tokens
- text on a transmissive body below its contrast target over the content actually under it

Keep a screenshot per combination.

```js
// rects.js: run in the page once per material, then diff the arrays
(() => [...document.querySelectorAll('[data-relief], [part]')].map((el, i) => {
  const r = el.getBoundingClientRect();
  return [i, el.tagName, el.dataset.layer, el.dataset.relief, el.dataset.face, r.x, r.y, r.width, r.height].join(' ');
}))();
```

Walk `el.shadowRoot` as well for components that keep their parts in shadow roots.

### Gallery entry

One card per showcase: title, the *Demonstrates* line, the components used, and a thumbnail per material preset. The
gallery is a ground holding raised cards. Opening a card can lift it to the overlay layer, which is a small demonstration of
the system in its own right.
