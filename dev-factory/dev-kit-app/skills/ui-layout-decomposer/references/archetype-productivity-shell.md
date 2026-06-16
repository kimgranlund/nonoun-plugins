# Archetype · productivity-shell

A tool you **work in**: an editor, designer, IDE, cockpit, DAW, CAD, dashboard-you-operate. **One primary artifact**
on a canvas, **framed** by analysis on one side and properties/actions on the other, with thin global chrome top and
bottom. Examples: Figma, VS Code, Linear's command surfaces, a color-palette designer, the dev-factory cockpit.

The defining idea: the **canvas is the subject**; the panes are *about* the canvas (left = what to know, right = what
to change); the headers/footers are *about* the whole session.

## Primary wireframe

```
┌─ app-header ─────────────────────────────────────────────────────────────┐
│ ◆ brand   doc-name        [ ⌘K  command-bar / search ]       ⟲ ⟳   ⇪ ◐    │
├────────────────┬──────────────────────────────────────────┬───────────────┤
│ app-pane-left  │ ┌ app-canvas-header ─────────────────────┐│ app-pane-right│
│  ░ pane-label  │ │ view ▸ [A][B][C]   ÷Fit − 100% +   + new││  ░ pane-label │
│                │ ├ app-canvas ────────────────────────────┤│  [tab|tab|tab]│
│  ┌ card ─────┐ │ │                                        ││  ┌ section ─┐ │
│  │ analysis  │ │ │                                        ││  │ Name  [_]│ │
│  │ data/graph│ │ │            THE ARTIFACT                ││  │ ◉ toggle  │ │
│  └───────────┘ │ │          (select · pan · zoom)         ││  │ ▭▭▭ slider│ │
│  ┌ card ─────┐ │ │                                        ││  │ value  ▸  │ │
│  │ selection │ │ │                                        ││  └──────────┘ │
│  │ detail    │ │ ├ app-canvas-footer ─────────────────────┤│  [ Duplicate ]│
│  └───────────┘ │ │ x:· y:· 100% · drag pan · status·hints ││ ┌ preview ──┐ │
│                │ └────────────────────────────────────────┘│ │ live result│ │
├────────────────┴──────────────────────────────────────────┴─┴────────────┤ │
│ app-footer:  N items · saved/●unsaved · mode          ⚠ warnings · counts  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Named-pattern vocabulary

| Pattern | Job | Outside-in (where) | Inside-out (verbs it hosts) |
|---|---|---|---|
| **app-header** | session identity + global actions | full-width top bar (~48px) | brand/doc identity · **command-bar/search** (⌘K) · undo/redo · export/share · theme toggle |
| **app-pane-left** | *what to know* — selections, data, graphs | fixed-width left column, scrolls | read telemetry · pick/select · drill into the selected object's analysis |
| **app-canvas-header** | view + canvas tools | thin bar atop the canvas | **switch view/mode** · fit · zoom −/+ · add-to-canvas (`+ new`) · filter |
| **app-canvas** | the artifact under work | the elastic primary surface | select · direct-manipulate · pan · zoom · drag |
| **app-canvas-footer** | canvas status + interaction hints | thin bar below the canvas | (read-only) cursor coords · zoom % · pan/zoom hints · live status line |
| **app-pane-right** | *what to change* — actions, properties | fixed-width right column, scrolls; often **segmented tabs** + a pinned **preview** at the bottom | edit/modify the selection · run actions · inspect detail/source/history · a pinned live **preview/result** |
| **app-footer** | global status + warnings | full-width bottom bar (~30px) | (read-only) counts · save state · global warnings/alarms |
| **command-bar / search** | the keyboard verb surface | in the header or a ⌘K overlay | jump-to · run-any-action · search — the power-user spine |

## Variants

- **Single-pane focus:** hide the left rail (or right) for a distraction-free canvas; bring it back on selection.
- **Inspector-as-overlay:** on narrow viewports the right pane becomes a slide-over drawer instead of a column.
- **Multi-canvas / tabs:** the canvas-header carries document tabs; the canvas hosts the active one.
- **Bottom panel:** a console/terminal/timeline docked above the app-footer (collapsible) — common in IDEs/DAWs.

## Outside-in notes (A)
- **A1:** the three-column body (`left · center · right`) between fixed header/footer; **only the panes + canvas
  scroll**, never the page. This is the gate most productivity-shells fail when CSS regresses (everything stacks).
- **A2:** left ~280–320px · right ~300–360px · center elastic; header ~48px · footer ~28–32px.
- **A3:** every region: a small label + a body; the canvas always reads header / area / footer top-to-bottom.
- **A4/A5:** panes are **card stacks**; the right pane's atoms are label-left / control-right property rows.

## Inside-out notes (B)
- **B2 binding:** *know* → left, *change* → right, *switch* → canvas-header, *command* → header/⌘K, *the work* →
  canvas. The classic orphan to catch: an edit verb that exists (keyboard shortcut, drag) but has **no home in the
  right pane** — add the button where its object is inspected.
- **B3 feedback:** the selected artifact element highlights; the right pane **pins a live preview/result** at its
  bottom so the inspector always *shows an outcome*, not just metadata.
- **B5 coherence:** one selection updates the left analysis AND the right inspector AND any canvas highlight — a
  single `select(x)` fanned to every surface.
