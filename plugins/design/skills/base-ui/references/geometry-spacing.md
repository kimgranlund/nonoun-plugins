# Differential Forms geometry integration

The formula authority is [mathematical-design-system's current contract](../../mathematical-design-system/references/geometry-contract.md). Use its [typed resolvers](../../mathematical-design-system/assets/differential-forms/geometry/index.ts), not base-ui/assets/geometry, which remains historical compatibility code.

Read only the needed family resolver. Component identity is independent of family and parent context. The semantic input uses a neutral wrapper; composed inputs resolve chip adornments with resolveComposedInput. Attached/listbox/segmented groups resolve residual child geometry with resolveComposite. Cards use resolveCard, collections resolveCollection, multiline rows resolveMultiline.

For current components, configure public geometry attributes and resolve lengths in companion CSS. Do not map resolver outputs into inline styles or generate runtime CSS. The bundled v0.2.2 resolver library remains a numerical baseline; consult the current consuming registry and contracts for implemented APIs.

Preserve CSS-pixel values and border-box. Apply owner padding once; do not subtract borders again. Exposed label compensation is density-independent, not the old unconditional L=n/2 rule. Do not propagate collection density into nested controls or apply composite subtraction to ordinary cards. See the shared component/parts/composition contracts for exact anatomy.

At u4, default density and border0: controls are32px with24px slots and6px label edge; chips are24px with16px slots and3px edge; composed inputs are32px. Compact/default/loose control heights are28/32/40 and composed heights28/32/48. Container Softest is16px, while control Softest is a pill. Checkbox radius is4px independently of curvature.

The historical five-density, tier/scale, percentage curvature, fixed L label padding, zero universal slot-gap and E/m/W data-row equations are superseded for new UI. The preserved old integration is in pre-differential/geometry-spacing.md; read it only for explicit legacy maintenance.

Appearance remains separate: keyboard focus3px/offset0px, system-ui text, Plex Mono400 captions, paired subtle surface levels. Use the shared appearance and interaction docs. Numerical passes do not certify browser or assistive-technology behavior.
