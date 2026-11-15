import { PRESETS, crisp, system } from './geometry-runtime/derive.js';
// Consumer adapter: ui-geometry lengths for the panel's own chrome, mapped to CSS pixels exactly once.
// The panel is a card at d = 2I; controls are h = S + 2I tall with text at T = 2I from their edge.
const px = (v) => `${Math.round(v * 1000) / 1000}px`;
export function panelGeometry({ n = 14, border = 0, controlDensity = 'default', collectionDensity = 'default', cardDensity = 'default', controlCurvature, containerCurvature, preset = PRESETS.standard } = {}) {
  const P = crisp(preset, n), X = system(P), q = X.q(n);
  if (!(n >= preset.unit.nMin) || !(q > 0)) throw new RangeError(`panel geometry: n = ${n} is under the preset's ${preset.unit.nMin}px minimum`);
  for (const dn of [controlDensity, collectionDensity, cardDensity]) if (!(dn in P.inset)) throw new RangeError(`panel geometry: density must be one of ${Object.keys(P.inset).join(', ')}, not ${dn}`);
  const kControl = controlCurvature ?? P.softAnchor, kCard = containerCurvature ?? P.dials?.kappa?.card ?? P.softAnchor;
  for (const k of [kControl, kCard]) if (!(k >= 0 && k <= 1)) throw new RangeError(`panel geometry: curvature κ must be in [0, 1], not ${k}`);
  const gc = P.gutter * q;
  if (!(border >= 0 && border <= gc)) throw new RangeError(`panel geometry: border ${border}px must be in [0, g_c = ${gc}px]`);
  const I = X.I(controlDensity) * q, S = P.slot * q, Ic = X.I(collectionDensity) * q, Ik = X.I(cardDensity) * q;
  const d = 2 * Ik, R = d + Math.min(X.radius(kCard, cardDensity), P.soft) * q;
  return Object.fromEntries(Object.entries({
    unit: q, border, height: X.h(controlDensity) * q, slot: S, padding: I - border, gap: I,
    radius: X.radius(kControl, controlDensity) * q, font: n, line: n + (P.type['body-md'][0] + P.type['body-md'][1]) * q,
    'edge-start': I, 'edge-end': I,
    'card-padding': d - border, 'card-gap': d / 2, 'container-radius': R,
    'collection-padding': Ic, 'collection-gap': Ic, 'multiline-height': S + 2 * Ic,
    'choice-size': P.icons.md * q, 'choice-radius': P.marks.checkRadius * q, 'choice-edge': I,
  }).map(([key, value]) => [`--ip-${key}`, px(value)]));
}
