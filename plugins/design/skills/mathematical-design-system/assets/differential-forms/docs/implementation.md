# Implementation guide

The resolvers are pure TypeScript and return CSS-pixel numbers. Pass explicit family inputs. They validate the supported domain and throw RangeError instead of silently clamping invalid inputs. Curvature helper functions are low-level and expect validated values; use the family resolvers as public entry points.

```ts
import { resolveControl, resolveLabelEdges, resolveComposite } from '../geometry/index.ts';
const control = resolveControl({unit:4,border:1,density:'default'});
const edges = resolveLabelEdges(control.labelEdge, true, false);
const group = resolveComposite({unit:4,border:1,insetUnits:.5});
```

Map `height`, `padding`, `gap`, `radius`, `slot` and label edges to scoped CSS variables with px units. For collection or card radius, CSS fits the nominal radius to the actual box; optionally use resolveCurvature with measured dimensions if computing geometry outside CSS. Never add border width to a border-box height that already includes it.

```css
.control { box-sizing:border-box; display:flex; align-items:center;
  height:var(--height); padding:var(--padding); gap:var(--gap);
  border:var(--border) solid transparent; border-radius:var(--radius); }
.slot { box-sizing:border-box; flex:0 0 var(--slot); width:var(--slot);
  height:var(--slot); display:grid; place-items:center; }
.label { min-width:0; display:flex; align-items:center; height:var(--slot); }
```

Framework adapters are intentionally absent. Use CSS custom properties, reactive bindings or Web Components as the host requires; avoid duplicating the formula in each component. Browser-measured text width is needed only for external width calculations; intrinsic CSS layout can size text badges directly.

Node 24 runs these erasable TypeScript files for tests. Running npm test does not type-check. Integrate them with the host repository's TypeScript compiler for static checking. No package downloads or build tools are required for the provided runtime tests.
