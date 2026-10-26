# Frozen v0.2.2 baseline — Differential Forms

Historical snapshot adopted 2026-10-22 from Differential Forms v0.2.2. For current work, start at the consuming repository’s AGENTS.md and follow its registry to the governing contracts, resolvers and companion CSS. Those repository sources own current formulas, defaults and supported inputs; this baseline must not override them. Keep new project-specific formulas in that repository rather than updating this frozen snapshot. The portable [contracts](../assets/differential-forms/contracts/foundations.json) and [typed resolvers](../assets/differential-forms/geometry/index.ts) are the executable source of detail. The earlier n/tier/percentage rules are superseded, not alternate defaults.

## Inputs and family formulas

All lengths are CSS px. u is 3..6 (default 4); B is 0..u/2 (default 0). Density order is compact/default/loose. Label edge e is 0..3u (default 1.5u), independent of density.

| Family | Slot | Inset I | Gap | Height |
| --- | --- | --- | --- | --- |
| Control | 6u | [0.5,1,2]u | [0,1,2]u | 6u+2I |
| Chip | 4u | control I | control gap | 4u+2I |
| Collection | content-specific | [1,2,3]u | I | content-driven |
| Card | content-specific | [3,4.5,6]u | I | content-driven |

Owner padding is I−B. Never subtract B again from the resolved height. A control's icon artwork is capped at slot−2B; label wrappers do not acquire decorative borders. Control font=2u+6, line height=5u; chip font=2u+4; badge font=2u+2. Icon sizes are 4u/5u/6u before their slot cap.

Badge height/min-width=4u, inline inset=0.5u, width=max(height,contentWidth+2×inset). Multi-digit count overflow remains unspecified. Choice artwork=4u, checkbox radius=u, radio radius=2u; switch frame=9u×5u, inset=0.5u and thumb=4u.

## Label edges

Use `resolveLabelEdges` with exposed edges and the component's explicit compensation policy. At e=6: no slots gives 6/6; leading-only button gives 0/12; trailing-only gives 12/0; both gives 0/0. Inputs disable opposite-edge doubling: leading-only gives 0/6. Chips use e/2. Do not restore the old fixed L=n/2 padding on every side or assume all occupied-slot gaps are zero.

## Curvature

Control requested radii: sharpest=0, sharp=u, default=2u, soft=3u, softest=height/2. Container values are 0/u/2u/3u/4u. `resolveCurvature` caps to height/2 and supplied width/2; CSS also fits radii to actual box dimensions. Width-aware nested resolution is not fully integrated into the specimen. Do not reintroduce the old rule that radii must never clamp.

## Attached composites

Requested inset L=0..1.5u; effective inset A=max(B,L); outer padding=A−B; gap=L. Child inset J=max(B,I−A); child padding=J−B; child height=slot+2J. Single-row outer height=child height+2A, allowing growth.

Child radius is **0 when L=0**, otherwise min(childHeight/2,max(0,parentRadius−A)). Shared parent/child border width and one composite level are verified. Independent border widths or deeper recursive compositions require explicit extensions.

## Composed inputs and multiline

Input adornments use chips. H=max(controlHeight,chipHeight+2I); minimum width=H. Parent radius is resolved using H. Adornment inline radius=max(0,parentRadius−I); block radius=min(chipHeight/2,max(0,parentRadius−(H−chipHeight)/2)). Currency uses a chip trigger with a sibling chip-family listbox. Its popup uses composite geometry; the input wrapper does not.

Multiline rows use collection inset/gap and container curvature; min-height=6u+2I, actual height=auto, no copy-edge margin, no composite subtraction. Collections have row separation=0.5u, block padding=I−B, internal cell inline padding=I/2−B, outer cell inline padding=I−B. Follow the table recipe rather than the old E/m/W table equations.

## Golden checks at u=4, B=0

| Metric | Compact | Default | Loose |
| --- | ---: | ---: | ---: |
| Control height | 28 | 32 | 40 |
| Chip height | 20 | 24 | 32 |
| Composed-input height | 28 | 32 | 48 |
| Collection inset | 4 | 8 | 12 |
| Card inset | 12 | 18 | 24 |

All densities keep control slot=24, chip slot=16, control font=14, control edge=6 and chip edge=3. At u4 compact B2 requested composite inset6: child height28, outer height40. This growth is intentional.
