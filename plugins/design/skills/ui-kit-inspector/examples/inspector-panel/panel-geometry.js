import { resolveControl, resolveCard, resolveCollection, resolveMultiline, resolveChoice, resolveLabelEdges } from './geometry-runtime/index.js';
// Consumer adapter: independent family inputs, CSS pixels mapped exactly once.
export function panelGeometry({ unit=4, border=0, controlDensity='default', collectionDensity='default', cardDensity='default', controlCurvature='soft', containerCurvature='soft', labelEdgeUnits=1.5 } = {}) {
  const common = { unit, border, labelEdgeUnits };
  const control = resolveControl({ ...common, density:controlDensity, curvature:controlCurvature });
  const card = resolveCard({ ...common, density:cardDensity, curvature:containerCurvature });
  const collection = resolveCollection({ ...common, density:collectionDensity, curvature:containerCurvature });
  const multiline = resolveMultiline({ ...common, density:collectionDensity, curvature:containerCurvature });
  const choice = resolveChoice(common);
  const edges = resolveLabelEdges(control.labelEdge, false, false, false);
  return Object.fromEntries(Object.entries({
    unit, border, height:control.height, slot:control.slot, padding:control.padding, gap:control.gap,
    radius:control.radius, font:control.fontSize, line:control.lineHeight, 'edge-start':edges.start, 'edge-end':edges.end,
    'card-padding':card.padding, 'card-gap':card.gap, 'container-radius':card.radius,
    'collection-padding':collection.paddingBlock, 'collection-gap':collection.gap,
    'multiline-height':multiline.minHeight, 'choice-size':choice.artwork, 'choice-radius':choice.checkboxRadius,
    'choice-edge':resolveLabelEdges(control.labelEdge, true, false).end,
  }).map(([key,value]) => [`--ip-${key}`, `${value}px`]));
}
