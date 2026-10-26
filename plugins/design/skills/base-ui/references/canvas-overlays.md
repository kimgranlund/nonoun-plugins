# Compact overlays on a canvas

Use this optional composition for a full-window diagram with search/zoom controls, playback and a nonmodal inspector. Existing `overlay` contracts supply native dialog/popover containment; they do not supply a graph camera or draggable workspace. This pattern composes existing buttons, fields and tokens; it is not a replacement native dialog or an automatic graph-layout engine.

## Maintained implementation

- `assets/recipes/canvas-overlays.html`: scoped composition, one border per floating panel, widget tier and widget surface role: margin2n and adjusted radius k·2n and parent-owned gutter n. Padding is2n minus the border, not2n plus the border. Inspector content scrolls separately; controls wrap. Long headings wrap. Its scene coordinates are example data, not UI spacing tokens.
- `assets/recipes/canvas-overlays.js`: `createCanvasOverlayHost(root,scene)` supplies blank-area pointer dragging, panel Alt+Arrow keyboard movement, viewport/resize clamping, explicit zoom and explicit fit into the largest unobscured rectangle. `select(id)` changes only pressed state. ResizeObserver never modifies the camera or graph coordinates.
- `assets/recipes/canvas-overlays-demo.js`: executable consumer using onAction, compact menu, player, inspector width/height controls and truthful evidence labels. Concatenate helper and demo controller for build.mjs. Below600px the inspector starts closed. `createCanvasOverlayLayout(root,host,{inspector,controls,player})` measures the actual panels: when the inspector overlaps controls or playback, it temporarily replaces both; closing it restores them. This also responds to window, text and panel resizing without changing the camera. Use `layout.update()` after explicit visibility changes and `layout.destroy()` on removal. A width breakpoint alone cannot account for expanded content or enlarged text.

The layout helper reserves the lower player's measured position for the controls, which scroll internally when expanded. The optional data-canvas-reserve-bottom budget remains available for other host policies. This is a three-panel composition policy, not arbitrary collision-free packing: deliberate player placement above controls, touch behavior and additional overlay roles need their own interaction checks. Hidden peers are restored only when this helper suppressed them. A visible inspector needs a reachable Close control.

Call `destroy()` on host removal. Consumers own model state, playback cleanup, persistence, graph layout and selection provenance. `fit(rect)` accepts a scene-space node or path union, returns false when no usable space exists, and never mutates scene coordinates. The host does not infer a selected evidence path. On false, expose a close/move-and-retry action; do not claim unobscured evidence or silently fit behind a panel. Keep reflow a separately named action. Selection, search, expansion, inspector resizing and playback must preserve card positions and camera unless the user explicitly invokes a camera/layout operation.

Dragging starts only in non-interactive, non-text panel areas after a movement threshold. Buttons, inputs, summary, links, contenteditable and data-no-drag descendants keep their gestures. Text hit testing preserves selection; do not add global user-select:none or visible grabbers. Keyboard panel movement is available when the panel itself has focus, not while editing a descendant. Pointer behavior is verified with a mouse; touch scrolling/drag arbitration needs separate device verification.

## Evidence meaning

Use a visible semantic label and actual source support: **signal** means an observation, **problem** identifies something actionable, **verified outcome** names the verified scope. Color supplements those labels and does not upgrade certainty. Unknown retention or provenance belongs in the inspector; do not render a repeated question-mark badge for each absent field. The demo's verified fixture is illustrative data, not a claim about a consumer.

## Verify integration

Run `check-canvas-overlays.mjs PLAYWRIGHT NEW_OUTPUT [CHROME]`. The authored fixture covers small/short/wide windows, both schemes, doubled computed text, long titles, expanded options, oversized resized panels, blank-area dragging, native text/input gestures, keyboard panel movement, window resize, camera preservation, explicit unobscured fit and a negative containment control. PNGs retain expanded/resized states for visual comparison; numerical passes do not establish aesthetic acceptance. No automated pixel-golden equality is claimed.

Inspect the consumer's actual graph and union of selected path bounds too. Finite space can make simultaneous long menus and inspectors impossible: provide a close/collapse path and keep that limitation visible. Avoid stacking a bordered disclosure/card inside the floating frame solely to group controls. Native disclosure retains its own required anatomy; use a plain expanded action group when a second frame is unnecessary. Do not apply doubled text twice or set parent and inherited child font multipliers cumulatively; use the maintained idempotent text-scale helper for synthetic checks.

Containment is not reachability: a panel can be inside the viewport while another panel covers its actions. Verify actual Options → Inspector → Close clicks after text enlargement and resizing, including restoration of controls/player; preserve camera/card coordinates throughout. Inspect expanded and exclusive states separately.

The canvas root uses `overflow:clip`, preventing native focus scrolling from silently shifting the transformed scene and floating chrome. Scroll only inside designated panel bodies. Verify root scroll offsets remain zero when keyboard focus reaches offscreen graph controls.

## Mathematical geometry contract

Floating controls, player and inspector declare `data-tier="widget"`; scene content retains its own purpose tier. Resolve n locally through `--g-margin`, never from a remembered pixel value or a different ancestor. The panel is a widget surface: `--r-widget` (k·2n, with the shared corner policy applied once), border-inclusive margin2n, padding `calc(2*var(--g-margin) - var(--m-border-thin))`, and gutter `--g-gutter`. Viewport clearance and scene camera units remain owned by the canvas root; they need not equal panel-local n.

The inspector body adds no second inline inset: its prose and header share one text rail. Controls retain their own internal label/media margins; do not equate a button border with its text start or add child margins to the parent's gutter. Boxed-child placement must account for the child's own margin (container margin minus child margin); any adaptation mixing prose and boxed children must measure the actual text/box anatomy rather than flattening every inset. The toolbar is a control-only row, not an assertion that differently shaped control labels align.

The maintained check measures local n, all four border-plus-padding distances, widget radius, sibling gutter and inspector header/body text rails across the responsive/text matrix. Negative controls deliberately restore old padding, control radius, doubled body inset and excess gutter and must be rejected. This is geometry evidence, not a substitute for the visual review.

Range controls use `input.range__root` with zero native outer margin. Flexible width belongs only to the player's horizontal row. Never apply a shared `flex-basis` to inspector ranges: their parent labels use a column axis, turning a width budget into excess height. The check rejects this axis leak and verifies inspector ranges retain the local standard frame (H=2n+2d; 4n at Regular).

The controls panel owns vertical overflow. Its direct groups use `flex-shrink:0`: expanded options or search results must not collapse under a short height budget while their children paint over adjacent controls. An independently scrolling results list may have its own bounded maximum height, but must retain a reachable scroll viewport. Verify actual result clicks with options expanded in a short window, not only each panel's outer rectangle.
