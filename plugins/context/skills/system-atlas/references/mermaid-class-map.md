# Mermaid class map

Mermaid's own theme variables cannot take `oklch()` or `light-dark()`, so the page paints
mermaid's SVG classes onto the `--dg-*` token tier in CSS. The host injects id-scoped rules of
its own, which is why every declaration here carries `!important`.

Verification state: checked by eye on flowchart only. Sequence and state diagrams use the same
selectors and look right, but no one has walked their class lists against a host render. Take a
look before trusting either, and update this line with what you observed.

| What it paints | Selector | Token |
|---|---|---|
| Canvas background | `svg` | `--none` |
| Node fills and strokes | `.node`, `.statediagram-state`, `.actor-top`, `.actor-bottom`, `rect.actor`, `rect.basic` | `--dg-node-fill`, `--dg-node-stroke` |
| Decision shapes | `.node polygon` | `--dg-decision-fill`, `--dg-decision-stroke` |
| Subgraph and cluster boxes | `.cluster rect`, `.statediagram-cluster rect`, `rect.labelBox` | `--dg-group-fill`, `--dg-group-stroke` |
| Node text | `.nodeLabel`, `.node .label`, `.node text`, `.stateLabel`, `.state-title`, `text.actor` | `--dg-node-text` |
| Group and loop labels | `.cluster-label`, `.labelText`, `.loopText` | `--dg-group-label` |
| Edges and lifelines | `.flowchart-link`, `.edgePath .path`, `.transition`, `.messageLine0/1`, `.actor-line`, `.loopLine`, `.relation` | `--dg-edge` |
| Arrowheads | `.marker`, `.arrowheadPath`, `marker path`, `#arrowhead path`, `#crosshead path` | `--dg-edge` |
| Edge label chips | `.edgeLabel`, `.labelBkg`, `.edgeLabel rect` | `--dg-edge-label-fill`, `--dg-edge-label-text` |
| Notes | `.note`, `.statediagram-note rect`, `.state-note rect` | `--dg-note-fill`, `--dg-note-stroke`, `--dg-note-text` |
| State start and end markers | `.state-start`, `.end-state-inner`, `.end-state-outer` | `--dg-edge`, `--dg-group-fill` |
| All diagram type | every text, tspan and foreignObject element | `--dg-font` |

The block, verbatim from the working page. Paste it whole; partial copies leave one class
unstyled and it shows up as a black box.

```css
/* mermaid paints, overridden onto the diagram tier. The host injects id-scoped rules, so these need !important. */
:is(pre.mermaid,.vstage) svg{background:var(--none)!important;color:var(--dg-node-text)}
:is(pre.mermaid,.vstage) svg :is(.node,.statediagram-state,.actor-top,.actor-bottom) :is(rect,circle,ellipse,path,polygon),
:is(pre.mermaid,.vstage) svg rect.actor,
:is(pre.mermaid,.vstage) svg rect.basic{fill:var(--dg-node-fill)!important;stroke:var(--dg-node-stroke)!important}
:is(pre.mermaid,.vstage) svg .node polygon{fill:var(--dg-decision-fill)!important;stroke:var(--dg-decision-stroke)!important}
:is(pre.mermaid,.vstage) svg :is(.cluster,.statediagram-cluster) rect,
:is(pre.mermaid,.vstage) svg rect.labelBox{fill:var(--dg-group-fill)!important;stroke:var(--dg-group-stroke)!important}
:is(pre.mermaid,.vstage) svg :is(.nodeLabel,.nodeLabel p,.node .label,.node span,.stateLabel,.state-title){color:var(--dg-node-text)!important;fill:var(--dg-node-text)!important}
:is(pre.mermaid,.vstage) svg :is(text.actor,text.actor tspan,.node text,.statediagram-state text){fill:var(--dg-node-text)!important;stroke:var(--none)!important}
:is(pre.mermaid,.vstage) svg :is(.cluster-label,.cluster-label span,.cluster-label p,.cluster .nodeLabel,.cluster text,.labelText,.labelText tspan,.loopText,.loopText tspan){color:var(--dg-group-label)!important;fill:var(--dg-group-label)!important}
:is(pre.mermaid,.vstage) svg :is(.flowchart-link,.edgePath .path,.transition,.messageLine0,.messageLine1,.actor-line,.loopLine,.relation){stroke:var(--dg-edge)!important;fill:var(--none)!important}
:is(pre.mermaid,.vstage) svg :is(.marker,.arrowheadPath,.arrowMarkerPath,marker path,#arrowhead path,#crosshead path){fill:var(--dg-edge)!important;stroke:var(--dg-edge)!important}
:is(pre.mermaid,.vstage) svg :is(.edgeLabel,.edgeLabel p,.edgeLabel span,.labelBkg){background-color:var(--dg-edge-label-fill)!important;color:var(--dg-edge-label-text)!important}
:is(pre.mermaid,.vstage) svg .edgeLabel rect{fill:var(--dg-edge-label-fill)!important;opacity:1!important}
:is(pre.mermaid,.vstage) svg :is(.edgeLabel text,.messageText,.sequenceNumber,.transition-label text){fill:var(--dg-edge-label-text)!important;stroke:var(--none)!important}
:is(pre.mermaid,.vstage) svg :is(.note,.statediagram-note rect,.state-note rect){fill:var(--dg-note-fill)!important;stroke:var(--dg-note-stroke)!important}
:is(pre.mermaid,.vstage) svg :is(.noteText,.noteText tspan,.statediagram-note text,.statediagram-note .nodeLabel,.state-note text){fill:var(--dg-note-text)!important;color:var(--dg-note-text)!important}
:is(pre.mermaid,.vstage) svg :is(.state-start,.start-state,circle.state-start,.end-state-inner){fill:var(--dg-edge)!important;stroke:var(--dg-edge)!important}
:is(pre.mermaid,.vstage) svg .end-state-outer{fill:var(--dg-group-fill)!important;stroke:var(--dg-edge)!important}
:is(pre.mermaid,.vstage) svg,:is(pre.mermaid,.vstage) svg :is(text,tspan,foreignObject div,foreignObject span,foreignObject p,.nodeLabel,.edgeLabel,.cluster-label,.messageText,.noteText,.actor,.stateLabel){font-family:var(--dg-font)!important}
```

## When a diagram kind paints wrong

1. Inspect the offending element in the rendered SVG and read its class list.
2. Add that class to the row it belongs to above, in the same `:is(pre.mermaid,.vstage) svg`
   scope and with `!important`.
3. Never reach for a mermaid theme variable or an init directive. Both lose.
4. Update the verification line at the top with the diagram kind you just checked.
