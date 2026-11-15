# Composition: how the four settings combine

## The fixed order

```
fills → delineation → lighting → transmission → chroma
```

Five passes. Each rewrites only the tokens it owns, reading what the passes before it left (the writers of every token are
in [terms.json](terms.json) › `tokens`):

| Pass | Owns | Reads |
|---|---|---|
| fills | every token's base value ([fills.md](fills.md)) | the palette inputs |
| delineation `line` | neutral faces → the base ground's colour; shadows → line rings | fills |
| lighting `lit` | face shading (fill only), bevels (fill only), casts (both), recess shadows (fill only), lamp glows and holes, the scheme constants | fills; under `line` it adds only the casts |
| transmission | the overlay face, shadow (rim, when lit) and backdrop filter; the pane's lower inner edge appended to the display shadow, and the display cover (lit only); never the recessed or field shadows; `--glass-k` | the face left so far (the ground colour under `line`, `--element` under `fill`) |
| chroma `mono` | the primary solid and `--on-solid`, emissive, data, media, status | everything above |

## Interactions

| Combination | Result |
|---|---|
| none + frosted / clear | glass body without rim or cast; no cover panes |
| lit + line | line rings plus casts; no face shading, bevels or recess shadows |
| line + frosted / clear | translucent body with a strong line instead of a rim |
| mono + lit | lamps keep their inset shading but lose the coloured glow |
| mono + transmission | unchanged: the glass body is neutral already; media under it is greyscaled |
| reduced transparency | transmission forced to `opaque`, whatever the preset says |
| forced colors | delineation forced to `line`, lighting to `none`, transmission to `opaque`, chroma to the system colours |

## CSS layout

One table per setting, keyed by its own attribute. A preset is a shorthand that sets the four attributes.

```css
:root                              { /* fills.md: base block */ }
[data-delineation="line"]          { /* line-and-mono.md */ }
[data-lighting="lit"]              { /* lighting.md (fill) */ }
[data-lighting="lit"][data-delineation="line"] { /* casts only */ }
[data-transmission="frosted"]      { /* transmission.md */ }
[data-transmission="clear"]        { /* … */ }
[data-transmission]:not([data-transmission="opaque"])[data-lighting="lit"] { /* rims and cover panes */ }
[data-lens="on"][data-transmission="clear"] { /* the lens backdrop */ }
[data-chroma="mono"]               { /* line-and-mono.md */ }
```

Selector tables compose only when all four attributes sit on one element. Where a page nests settings (a lit region inside
an Outline page), use inherited toggles: each value a custom property that is empty while it holds and `initial` while
not; each entry `var(<lit toggle>) var(<fill toggle>) <value>`, valid only while every toggle holds; a token the last valid
entry in pass order; the tokens declared again on every element that carries a setting or a scheme. Build the fallback
chain so the last pass is tried first, test the chain by evaluating it, and write an empty toggle as `/**/` where a style
system drops a value that is only a space.

A bare presence selector such as `[data-transmission]` also matches `opaque`, which would give Physical the glass rims;
always exclude the value that must not match.

```js
// a preset expands into the four settings; a page may override any of them afterwards
const PRESETS = {
  flat:     { lighting: 'none', transmission: 'opaque',  delineation: 'fill', chroma: 'colour' },
  physical: { lighting: 'lit',  transmission: 'opaque',  delineation: 'fill', chroma: 'colour' },
  frosted:  { lighting: 'lit',  transmission: 'frosted', delineation: 'fill', chroma: 'colour' },
  glass:    { lighting: 'lit',  transmission: 'clear',   delineation: 'fill', chroma: 'colour' },
  outline:  { lighting: 'none', transmission: 'opaque',  delineation: 'line', chroma: 'mono'   },
};
function applyMaterial(el, name) { for (const [k, v] of Object.entries(PRESETS[name])) el.dataset[k] = v; }
```

When tokens are computed in script (as in a canvas or a design tool), run the same five passes in the same order over one
token object.
