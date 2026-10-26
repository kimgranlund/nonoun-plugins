# Interaction state punch list

Implemented in the maintained stylesheet; the mathematical-design-system reference site supplies an interactive state lab. This list declares styling, not universal browser or assistive-technology certification.

| Complete | Owner | Declared states and treatment |
|---|---|---|
| Yes | Filled buttons, icon buttons, chips | Rest paired fill/text; hover reverses the pair with a visible boundary; active retains the paired fill without an inset stroke; keyboard focus uses the shared ring. |
| Yes | Secondary/outline buttons | Transparent or surface rest; hover/active uses action fill and its paired text. |
| Yes | Ghost buttons, toolbar triggers | Transparent rest and border; hover uses action fill/paired text with transparent border; active retains the paired fill without an inset stroke. |
| Yes | Expanded/pressed triggers | Persistent action fill; semantics remain aria-expanded/aria-pressed; pointer hover does not mutate state. |
| Yes | Disabled/busy actions | Disabled dims and suppresses hover/active paint; busy uses progress cursor and dashed boundary. Controller owns activation suppression and actual work. |
| Yes | Listbox options | Transparent rest; hover/active-descendant fill; persistent selected fill/check; focus ring; disabled suppression. Both backgrounds subtract only unprotected border overlap. |
| Yes | Segments | Independent selected and hover shapes, hover below selection; focus ring; disabled; conditional border inset shared by both shapes. |
| Yes | Checkbox, radio, switch | Existing off/on/mixed (checkbox only), focus, disabled and invalid paint; enabled hover strengthens the mark/track boundary without changing checked state. |
| Yes | Editable fields | Enabled hover strengthens boundary; focus ring; invalid dashed boundary and associated error; readonly dashed boundary; disabled dims. No color reversal during text editing. |
| Yes | Native selects, disclosure summaries | Hover/active action pair; visible focus; open disclosure weight/caret and native select open caret; disabled select remains unchanged. Platform popup paint remains browser-owned. |
| Yes | Navigation, tabs, menus, record choices | Hover/active action pair; persistent current/selected styling and keyboard focus. Links have no invented disabled behavior. |
| Yes | Table sorting | Hover/active action pair on the sort button, visible focus; sorted caret and aria-sort remain persistent. Static rows/data lists have no misleading hover affordance. |
| Yes | Motion and accessibility | Shared Apple Smooth for non-reversing paint; reduced motion/forced colors disable transitions. Reverse foreground/background pairs change together immediately to avoid an unreadable midpoint. |

## Border-protected listbox paint

Container margin remains its existing geometry. Each option retains its entire hit area. The decorative background uses `I = max(0, B − P)` where B is the border thickness and P is existing container padding. Position is inset I on each side, dimensions lose 2I, and radius is `max(0, option radius − I)`. Standard margins protect the border (I=0); compact zero padding uses I=B. Both selected and hover use the same layer and calculation, so selected hover never overwrites selection.

The default CSS derives P from maintained listbox margin. For custom padding/radii, bind `assets/recipes/listbox-backgrounds.js` and call refresh after a theme/profile change. It reads actual per-edge padding and resolved option radius. Native selection and keyboard behavior remain the consumer's responsibility. Do not attach listbox roles to static specimen divs.

Explicit semantic-intent buttons retain their tested palette pairs rather than inheriting neutral reversal. Always test the foreground and background together, including custom page schemes.

## Color roles and conditions

Scope: neutral controls and the geometry reference page. Explicit semantic intents keep their own tested pairs.

Rule COLOR-01. The page defines a background, foreground and paired action foreground. A filled action uses the page foreground as its background. A charcoal page with off-white text therefore uses off-white actions; a charcoal page with red text uses red actions.

Rule COLOR-02. Pair dark or red action fills with off-white text only when contrast passes. Pair off-white action fills with charcoal text. The screen reference red is #f9423a; small red annotation text on off-white uses its darker companion #bd381c. The red is a screen approximation, not a claim about print-ink equivalence.

Rule COLOR-03. On neutral filled-action hover, reverse the foreground/background pair together. On ghost hover, use action fill and its paired foreground; keep the border transparent. Do not interpolate through a low-contrast midpoint.

Rule COLOR-04. Keep editing surfaces transparent. Strengthen field boundaries on hover; do not reverse text while editing. Keep selected states persistent while another option is hovered.

Rule STATE-01. Use native or ARIA state as the styling source. Disabled and busy actions suppress activation and enabled hover paint. A controller owns asynchronous work; CSS does not simulate completion.

Rule SORT-01. A sortable header shows both arrows when unsorted, up when ascending, and down when descending. Use a 2n slot with a 2n−2c mark. Update aria-sort and row order together. An icon control does not reduce the table cell margin.

Verification: check foreground/background contrast in every supported page scheme; check native keyboard focus, selected plus hover, disabled hover, reduced motion, and actual row order after sorting.

## Focus modality and boundary ownership

Call bindFocusModality(document) once for strict keyboard-only focus indication, including editable inputs that browsers otherwise match as focus-visible after a click. Pointerdown clears focus paint; unmodified keyboard input restores it. Without the binding, retain native focus-visible as the accessible fallback. Never remove focusability or editing behavior. Shared ring width/offset/color tokens own focus paint; use a 3px ring with zero offset and make the focus owner’s border transparent only while the ring is visible. Composite fields show one ring on the wrapper when the input has visible focus; internal actions retain their own focus target. OTP uses a rounded outer boundary; invalid cell borders remain distinct from focus. Selected/current state must not depend on focus modality. Verify pointer, Tab, keyboard-after-pointer, keyboard focus return, forced colors and reduced motion.

## Button boundary paint

Current Control buttons have no default or active inset stroke when filled. Secondary/outline controls use the explicit `--ui-control-border` token (default `--ui-border`; semantic intent outlines use `--ui-intent-border`) for their layout-neutral inset boundary. Text color does not choose the stroke. The existing focus ring and hover/active paired fills remain. Border width, frame height, padding, slots and radius formulas are unchanged.
