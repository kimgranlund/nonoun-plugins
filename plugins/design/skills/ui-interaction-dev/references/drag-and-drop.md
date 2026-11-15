# Drag and drop: building one

How to build a pointer drag that meets [spec.md](spec.md) (`drag.*`, `alternative.*`, `announce.*`). The rule ids in
brackets are the obligations; this page is the construction. Framework-neutral: plain DOM, custom elements or any
framework's effect hooks.

Contents: [Choose](#choose) · [The state machine](#the-state-machine) · [Parameters](#parameters) · [During the drag](#during-the-drag) · [The alternative](#the-alternative) · [Announcements](#announcements) · [Tests](#tests) · [Pitfalls](#pitfalls)

## Choose

| Need | Build on | Why |
|---|---|---|
| Reorder or move within the page, mouse and touch | Pointer Events [drag.architecture] | One path for every pointer; full control of preview and indicator |
| Files from the desktop, or dragging to other windows or apps | Native HTML drag and drop, plus a file input | The only way across the window; touch support is weak |
| Both | Native for files only; pointer events for items | Keep the two paths separate |

Library equivalents: dnd-kit (pointer sensors, activation constraints, collision strategies), Pragmatic drag and drop
(native events, design and accessibility guidelines), React Aria (native for pointer, a hand-built keyboard and
screen-reader mode). Borrow their numbers and rules even when the code is your own.

## The state machine

```
idle ──press on a draggable──▶ pending ──constraint met──▶ live ──pointerup──▶ drop ──▶ idle
                                  │                           │
                                  ├─ pointerup: a click ──────┤── Escape / pointercancel / page hidden ──▶ cancel ──▶ idle
                                  └─ touch drifts past tolerance: abort (the page scrolls)
```

- **pending** holds the start point, the pointer id and type, and (touch) a timer. Nothing changes on screen.
- **live** starts once: capture the pointer, listen for Escape and visibilitychange, call `start`, begin the
  autoscroll loop. On touch, also listen for a non-passive `touchmove` and `preventDefault` it [drag.touch-scroll].
- **drop** calls `drop`, then swallows the next click [drag.swallow-click].
- **cancel** calls `cancel`, which puts the item back and announces it [drag.cancel].
- Every exit releases capture, clears the timer and the frame loop, and removes the window listeners.

Listen for move, up and cancel on `window` in the capture phase, filtered by pointer id, so a fast pointer that leaves
the element is not lost before capture is set.

## Parameters

| Parameter | Value | From |
|---|---|---|
| Mouse or pen distance | 4px | [drag.activation]; dnd-kit's distance constraint |
| Touch delay | 250ms | [drag.activation]; dnd-kit's delay constraint |
| Touch tolerance | 5px | dnd-kit's example tolerance |
| Edge band for autoscroll | 40px, 10px a frame | [drag.autoscroll] |
| Drop line | 2px, terminal ring at its start, centred in the gap | Pragmatic drag and drop |
| Target tint | the hover tint over the container's surface, only for a container that is not the item's own | Pragmatic drag and drop |
| Announcement debounce | about 100ms for rapid position updates | Primer |

The numbers are defaults that tests here passed with, not laws: change one only with a test that shows why.

## During the drag

- **The item.** Lift it (raised paint, a small offset up) and follow the pointer with the CSS `translate` property, so it
  composes with any `transform` the lift already uses. Where a scroll box or a stacking context could clip it, the item
  itself may go into the top layer (a manual popover, fixed at its box) while a placeholder of its size keeps the slot;
  the landing leaves the top layer before the item is moved in the DOM, since moving an open popover hides it. Keep its slot, so nothing reflows [drag.no-reflow]. Give it
  `pointer-events: none` while live, so hit tests and autoscroll see what is under it.
- **The target.** Choose the container whose box contains the pointer's x (or the nearest by centre), then the index:
  the number of the container's other items whose vertical centre is above the pointer.
- **The indicator.** Position the line from the neighbours' boxes: above the first item by half the gap, between two
  items at the midpoint, below the last by half the gap. Empty container: no line, tint only [drag.indicator].
- **Layers.** Close any menu or tooltip attached to the item when the drag starts.
- **Hover.** Suspend hover-driven affordances (a Move key that follows the pointer) while live.

## The alternative

Required, not optional [alternative.single-pointer]. The pattern that satisfies 2.5.7 and keyboard users at once:

1. A **Move** control on the item under the pointer or with focus, named "Move <item>" [alternative.trigger], placed
   on the item's first line at its trailing edge, and reachable by Tab from the item (in a one-stop composite it is
   the next stop after the focused item).
2. It opens a **menu** of outcomes: each other container ("Move to Done"), then "Move up" and "Move down" (left out
   when impossible). For outcomes that need input, a menu item opens a dialog.
3. Choosing one moves the item, announces it, fires the same change event as a drop, and **returns focus to the item**.

A keyboard drag mode (Space picks up, arrows carry, Space drops, Escape cancels) may sit beside it
[alternative.keyboard-drag]; it never replaces it.

## Announcements

One polite live region, queued. Name the item, the container and the position [announce.stages]:

| Moment | Example |
|---|---|
| Pick up | "Snare picked up in To do, position 2 of 3" |
| Carried to a new place (keyboard) | "Doing, position 1 of 3" |
| Drop | "Snare dropped in Doing, position 3 of 3" |
| Cancel | "Snare put back in To do" |
| Menu move | "Snare moved in Done, position 1 of 1" |

No `aria-grabbed`, no `aria-dropeffect` [announce.no-grabbed].

## Tests

Real input only [testing.real-input], and each check run once against the code without the change
[testing.negative-control]:

| Check | How |
|---|---|
| A drag carries an item to another container and position | `page.mouse` down, move in steps, up; read the order |
| Nothing reflows mid-drag | container heights before and during |
| One line, in the container under the pointer; empty container tinted, no line | read the indicator and tint mid-drag |
| A click and a sub-threshold move are not drags | click; move 2px; no change event, clicks still arrive |
| Escape mid-drag puts it back and fires nothing | press Escape while live |
| Touch: a swipe moves nothing; a rested press drags | CDP `Emulation.setTouchEmulationEnabled`, `Input.dispatchTouchEvent` |
| Autoscroll | hold near a scroll box's edge; `scrollTop` grows |
| The click after a drop is swallowed | count capturing document clicks |
| The Move key: shown on the pointed or focused item, named, its menu moves the item, focus returns | click and keyboard paths |
| Announcements | wait for the region's text [testing.announcer-queue] |

## Pitfalls

- In shadow DOM, `document.activeElement` is the outer host: a menu rendered there ignores its keys
  [shadow.active-element]. Find the pressed part with `composedPath()[0]` [shadow.composed-target].
- A custom element whose constructor sets attributes cannot be made with `createElement` [shadow.create-element].
- `touch-action` set during a press does nothing [drag.touch-scroll].
- A container's `::slotted()` rules cannot give slotted items a hit area or a pseudo-element [target.slotted].
- Text selection starts on a drag unless the item sets `user-select: none` [drag.text-selection].
- A re-render that replaces the dragged node takes pointer capture with it. `lostpointercapture` then fires at the
  document, not on the node: cancel the drag there [drag.lost-capture].
- Raw CDP mouse moves report `buttons` 0 unless each carries the pressed button [testing.cdp-buttons].

## Tables: reordering columns and rows

A column is reordered by its header and a row by a handle; every `drag.*`, `alternative.*` and `announce.stages` rule tested holds for both unchanged. What a table adds (each rule validated on a table with a sticky header row and a sticky first column, in Chromium and WebKit):

- **The line.** It spans the visible table across the reorder axis, on the shared boundary of two cells, and paints above sticky and lifted cells (`drag.table-line-span`, `drag.table-line-layer`).
- **Sticky cells.** Measure a sticky header from a sticky cell, never from its row; start the autoscroll band at the sticky cells' inner edge; keep the lifted item under the pointer while the box scrolls; give lifted cells a positioned layer, since translate alone leaves them under sticky cells (`drag.sticky-measure`, `drag.autoscroll-sticky-band`, `drag.autoscroll-follow`, `drag.lift-above-sticky`).
- **Commit.** The header cell and the cell in every row move together, focus goes back to the moved item after the nodes are re-inserted, and the release after an Escape cancel does not click (`drag.table-commit`, `focus.after-drop`, `drag.swallow-click-cancel`).
- **The alternative.** The Move control names the thing by its label ("Move Team column", "Move Chen Wei row"), never by an index; a row's handle may double as it; its menu renders outside the scroll box (`alternative.table-names`, `alternative.handle-is-trigger`, `overlay.outside-scroll-box`).

Not proven here: Firefox, touch on real hardware or in WebKit, a screen reader, several pinned columns, right-to-left, spanning cells and virtualised tables.
