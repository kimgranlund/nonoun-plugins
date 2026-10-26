# Viewer: the offline report app

How the reusable shell (`assets/shell.html`) presents a v2 hydrated report. Moved from SKILL.md on 2026-10-16; the analysis path stays in SKILL.md. The skill owns hydration; the shell owns presentation.

## Visual exploration and publication

For visual exploration, produce a v2 hydrated `session.json` and a portable `index.html`, registered in the per-user report library. The reusable shell is `assets/shell.html`; it can open JSON directly using its file picker. Do not rewrite the app per session. The skill owns hydration; the shell owns presentation.

After `library.py publish`, open the published HTML returned by `library.py` (join its `root` and `html` values). Check event selection, scrubbing backward, source history, evidence provenance, JSON loading, and coverage.

Default locations: macOS `~/Library/Application Support/Context Fog of War`, Linux `$XDG_DATA_HOME/context-fog-of-war` (fallback `~/.local/share/context-fog-of-war`), Windows `%LOCALAPPDATA%/Context Fog of War`. Use `library.py path` to resolve it, `library.py list` to inspect metadata, and `library.py --root PATH publish FILE` only for an explicitly selected alternate library or isolated tests. The offline report's “Report library” link opens the saved collection. No browser file-system permissions or server are needed.

The scripts require Python 3.9+ and the standard library. Git is optional. Artifacts require a modern browser, run offline, and have no CDN, server, or package installation requirement.

## Exploring the atlas

The shell opens at the full-session overview. Play restarts from the beginning; scrubbing reveals landmarks at their first recorded exposure without moving their coordinates. Search for a file or skill and select it to highlight an upstream trail and open its exposure history. Earlier/later arrival switches between encounters. Zoom and scroll explore the SVG map. Solid edges represent recorded links or exposure, dashed edges inferred influence, and thin edges observed order only. The trail is a navigational reconstruction, not proof of causation; inspect evidence and routing diagnoses before proposing guidance changes. Event markers display data types. Click any noodle to inspect its rationale, excerpts and trace lines. Evidence-backed guidance sourceIds reveal source-to-destination attribution; missing attribution remains unknown. The existing timeline, parallel call inspection, source inventory and diagnoses remain available below the atlas.

Payload presentation uses the reusable templates in `assets/payloads.js`: message, call, result, compaction, context and unknown. The Readable tab shows decoded fields; Raw JSON preserves the complete hydrated record and parsed original payload, including tool slots. Connection inspection uses the same templates with separate exact excerpts. Never execute or render recorded payloads as HTML.

## Candidate territory in the canvas

Candidate-only paths are grouped by mentioning step and collapsed by default. Expand a group with click, Enter or Space; search opens the matching group. Recorded attempts/reads/edits remain individual landmarks at the current replay position. Group expansion does not move those landmarks and persists while replaying or zooming; loading another report resets expansion.

Selecting a source fits its highlighted upstream route, source landmark and attributed destinations in the canvas. Changing arrival refits the route. Use Fit path to restore framing after manual zoom. Long paths may require small labels; zoom in to inspect individual steps.

## Step-card canvas

The primary canvas nests source occurrences in their recorded step. The same source may appear in multiple cards, with exposure computed at each occurrence (not leaked from later reads). Candidate-only rows collapse under “other paths”. Source-attributed guidance uses row-to-row noodles; unassigned relationships use headers. Selecting a row, header or noodle highlights upstream recorded/inferred links and fills gaps with explicitly non-causal chronological links back to HOME, the first recorded step. Local header-to-row branches mean step membership only. Full-path fitting can shrink long-session labels; zoom controls remain available.

## Evidence indicator strip

Every source occurrence has six independent indicators, in fixed order: Listed, Requested, Returned, Context, Referenced, Edited. They are computed only from records at or before that occurrence. Filled means recorded, half-filled means partial return, diamond means inferred relationship, question mark means unknown, and cross means explicit failure/removal. Unknown never implies false. Context is confirmed only at its assembly event; historical inclusion remains inspectable after the indicator becomes unknown. Failure attribution requires an unambiguous single-source retrieval, never a failed sibling in a batch. Hover or keyboard focus explains an indicator; activation opens its exact citations and full JSON. Step headers show event glyphs and pending/succeeded/failed/mixed/unknown execution; call steps remain pending until their separate result event. Mixed batches retain per-call outcomes.

## Focused inspection

Canvas selections and evidence links inspect historical steps without moving the replay cursor. Only transport/timeline replay controls change time. Source inspection reports exposure at its selected occurrence. Focused route is the default after selection: preserve HOME, the selected source's occurrences and supported ancestor links, and label chronological gaps explicitly. Full session restores every step. Focused cards wrap and maintain a readable minimum scale; long routes may scroll vertically rather than become tiny.

Show evidence badges only when a recorded/partial/inferred/failed/removed state is supported. Do not show unknown question-mark boxes. Unknown remains explicit in source inspection and Raw JSON. Source rows reserve bottom padding beneath badges and step headers share the card frame rather than adding a second bordered card.

## Canvas navigation

Playback is a compact floating bar anchored inside the canvas while the SVG scrolls. Step cards center vertically within each horizontal band. Wrapped routes use rounded, offset connectors. Space + left drag or middle drag pans without selecting a step or changing replay. Ctrl/Cmd-wheel and trackpad pinch zoom around the viewport center; canvas-focused +/− zoom, 0 resets to 100%, F fits the selected route. Blank-canvas double-click zooms in (Shift reverses). Ordinary wheel movement scrolls. Text inputs keep their ordinary keyboard behavior.

The canvas fills the window. Search and zoom float over it; View options contains compact route and exposure choices. Use plain file/source terminology. Evidence opens in a collapsible overlay without seeking replay or resizing the map. Session, timeline, inventory and diagnoses are available in the Session & timeline drawer. Symbols and shortcuts live in expandable help.

Selection highlights the historical route and opens evidence without automatic zoom-to-fit. Only explicit Fit path / F reframes a route; selecting sources, steps, connections, evidence, or arrivals preserves zoom.

Full session is the default layout. Selection only changes highlight/evidence; preserve card coordinates, rows, zoom and replay in both layouts. Snapshot focused geometry when the user explicitly chooses Focused route, and retain it across subsequent selections. Recompute layout for explicit layout/filter/expansion changes, viewport changes, or replay changes. View options uses compact native Layout and Show sources selectors.

Keep the canvas toolbar collapsed by default: only search, zoom and More controls remain visible. Put layout, exposure, fit/clear, session and evidence toggles in a separate collapsible panel. Rebuild the shipped shell from the current authoritative base-ui kit so all shared controls receive its updated styles, fonts and runtime.

Controls and playback have pointer/touch drag handles. Save positions per report in browser localStorage; clamp restored positions on resize. Arrow keys nudge focused handles, Shift increases movement, Home resets. Search, zoom, scrub and playback retain their own gestures. Expanded controls follow the toolbar within window bounds.

Evidence inspector has move and resize handles with per-report local position/size persistence. Keep its header accessible, scroll evidence internally, clamp geometry on window resize; arrow keys adjust and Home resets. Omit header-to-contained-source membership lines; containment conveys membership. Leave viewport-relative trailing space after the timeline for scrolling beyond the final card.

Use base-ui g-height/g-inset/g-text and composed r-control/r-card geometry directly. Do not reintroduce a second local token engine. Nested prose panels use one outer wf-reading-flow to share horizontal text rails. Check expanded controls, inspector and report drawer at narrow, intermediate and wide widths.

Camera framing: initially align the first step 32px from the left edge and center its horizontal band vertically in the viewport. All zoom inputs preserve the current scene point at viewport center, including after horizontal/vertical scrolling. Scene gutters on all sides prevent scroll-boundary clamping from moving the zoom anchor.

Persist camera zoom and scene-space viewport center per report in browser localStorage, restoring on load. Reset view (in More controls) restores default full-session framing and 100% zoom. Double-click zoom anchors to the clicked coordinate; buttons, keyboard and wheel remain viewport-centered. Controls/player drag from their non-interactive backgrounds; inspector moves from its header. Do not show physical move grabbers. Preserve input, button and scrub gestures.

Per-report view persistence includes source/occurrence selection, route mode and frozen focused layout, exposure filter, expanded alternatives, source/timeline/decision search text, replay position and inspector visibility, alongside camera geometry. Validate restored IDs against the report; older camera-only records remain compatible. New reports start with clean defaults.

## Story-first overview
Default to the session story, with the raw event map and recorded timeline available separately. The reusable shell derives bounded chronological episodes from request boundaries and tool activity (roughly 24 events per episode); all events remain inspectable. Titles describe observed dominant activity, not inferred intent. Each episode shows call/return and source exposure/edit counts, affected paths, expandable action/result records and linked existing decision analysis. Never invent a decision explanation where none exists. Following results are chronological, not automatically causal or call-ID matches; exact payloads remain authoritative. Story search, expanded episodes and selected view persist locally per report. Pinch/wheel zoom and double-click anchor to the gesture coordinate; zoom buttons and keyboard remain centered.

Render the session story spatially: connected episode cards left to right on a pannable/zoomable canvas, expanding into horizontal action/result cards. Connections labeled “then” express recorded order, not causation; filtered omissions are labeled. Keep evidence-backed explanations expandable alongside the path. Persist story camera and episode expansion. Raw event cards carry episode number/title context from the same derived episode index.

The primary canvas now unifies episodes and events. Show collapsed episode cards by default; explicit expansion reveals the recorded event cards, source occurrences and existing source-to-source edges inside an episode boundary. Collapse restores the summary. Persist expanded episode IDs with the report view. Folded connections retain their original evidence for inspection. Do not require switching story/raw modes; the recorded timeline remains in the session drawer. Focused-route mode remains an explicit alternative layout.

## Context engineering investigations
Use the Findings panel to review failed discovery, repeated retrieval, truncation, broken references and potentially late guidance. Each candidate links exact trace evidence and a focused canvas path, states uncertainty and alternatives, and proposes a validation experiment. See references/diagnostics.md for detection requirements, exclusions and evaluation limitations. Keep proposals separate from applied changes; causal savings and baseline improvements require comparison runs.

Attach diagnostic candidate badges to their final supporting event and aggregate them once per collapsed episode. Badge activation opens scoped findings without changing camera, replay, or layout. Each finding exposes exact citations, suggested improvements, verification, and expandable uncertainty. Only the explicit Trace evidence on canvas action focuses and fits the evidence path. Use neutral candidate styling, never implied defect severity. Rebuild from the current base-ui kit and inspect expanded findings at narrow and wide widths.

Diagnostic focus (in More map controls) supports Off, All findings, and an individual candidate. Automatically expand episodes containing recorded supporting events and dim unrelated steps and connections without deleting them. Highlight only recorded evidence relationships; chronology is not causal proof. Preserve manual episode expansion separately, respect replay visibility, and persist the diagnostic focus per report. Individual finding details offer Focus this finding on canvas; that explicit action pans to the first visible supporting event without changing zoom. Turning diagnostic focus off restores manual expansion. Reset view clears it.

Canvas finding navigation provides Previous/Next and a clickable current finding title. Traverse findings whose complete supporting evidence has reached the replay position. Disable navigation at either boundary; do not wrap or advance replay. Reuse diagnostic focus and pan to evidence while preserving zoom. The active finding persists through the diagnostic filter state.

Previous/Next finding automatically opens and refreshes the scoped diagnostic inspector, with the active finding expanded. Preserve keyboard focus on navigation (or move to the current title at a disabled boundary), reset detail scrolling for the new finding, and close stale raw-event evidence. Reserve space for the finding navigator when positioning the inspector at narrow and wide widths. Zoom and replay remain unchanged.

When showing a diagnostic inspector for an individual finding, pan the evidence into the unobscured map region without changing zoom. Center all supporting cards when they fit; otherwise expose the first supporting card at readable scale and leave the remainder pannable. Reserve toolbar/player margins. Use a narrower reading column on desktop and a lower inspector on small screens, with repeated scoped filter chrome removed. Re-evaluate placement on window or finding-navigation size changes; keep manual pan available.

## Sunburst and radial exploration
The Charts control opens two full-report views independent of replay. Sunburst groups episode → recorded event kind → tool → directory → file → exposure state. Each unique event/source exposure pair counts once; events without exposures contribute one explicit no-source entry. Angles encode those counts, never importance, retained tokens or causal influence. Episode colors are categorical. Click episodes to drill down and sources to inspect their occurrences. Linked finding counts may overlap episodes and must not be summed as unique findings.
Radial graphs are available for sources and findings from the chooser and their inspectors. Center spokes encode recorded exposures, candidate mentions, context records or finding citations, explicitly labeled without causal claims. Existing report links/guidance edges are retained between visible events; inferred connections are dashed. Paginate 8 related events at a time, with exact totals. Source paths may recur. Allow inspection of exact event payloads, navigation to the corresponding timeline row, and explicit canvas-path exploration. Empty/missing relationships remain explicit. Charts never execute trace contents or require per-session scripts.

Radial nodes show tool/event type, a recorded file basename with additional-file count, and the step number. Full paths remain in the selected detail and accessible label. Selection follows all existing incoming report/guidance edges with cycle protection; finding views also include all finding citations. Highlight those nodes and connections, dim unrelated nodes, and preserve inferred edge styling. Do not fabricate chronological or causal links. Include a complete chronological evidence list across graph pages and an explicit full-path canvas action.

Default report entry opens the sunburst overview. Keep a visible Report library link in the chart header using the publisher-resolved registry URL. Radial overviews remain bounded, but selecting a node shows every event in its full recorded evidence path on one scrollable graph, without pagination. Collapse unrelated members into an explicit counted return-to-overview action. Expand graph radius with path length and retain fixed readable node sizes; do not shrink labels to fit. All recorded path events remain linked to exact evidence and timeline inspection.

Radial navigation uses a scene-space camera: Space + drag or middle drag pans; Ctrl/Cmd-wheel and two-pointer pinch anchor zoom at the gesture coordinate; +/− buttons zoom around the viewport center; Fit path (or F while graph-focused) fits all graph nodes. Persist camera center/scale per report and selected source/finding, preserving it across repaint and inspection. Long selected evidence paths remain unpaginated. The six-ring sunburst supports drilling from every ring, keyboard activation, full-label hover/focus text, clickable breadcrumbs and Back one level. Deep leaves link to original payloads, timeline and source radial view. File and exposure grouping retains the same event-source occurrence denominator; missing metadata is explicit, never guessed.

Persist chart navigation per report (path plus session identity): active view, validated sunburst breadcrumb, source/finding selection, highlighted event, overview page, search and chart-origin inspector event/finding. Keep existing per-selection radial camera storage. Restore valid prefixes/IDs only; missing entries fall back safely. New reports still default to sunburst, while returning reports resume their saved view. Reopening the same radial selection does not clear its highlighted path. Provide Back to charts from chart-origin event inspection. Use stronger strokes for selected-node connections and quiet contextual edges without deleting evidence; distinguish call and response labels.

Radial episode branches replace the flat event ring. Show episode summaries with counts and expandable fixed-size event cards. Preserve selected-node and immediate incoming/outgoing neighbors even inside collapsed episodes; default to keeping their nonessential siblings collapsed. Keep all relevant episode summaries accessible, with explicit expansion instead of pagination. Persist manual episode expansion alongside chart selection. Selected nodes and direct edges have strongest emphasis; grouping branches are quiet and never imply causation. Bundle coincident connections at collapsed endpoints by kind, preserving every underlying edge and endpoint citation for inspection. Expansion and selection never auto-fit or alter zoom; Fit path remains explicit.

Expanding or collapsing a radial episode keeps the selected event at its existing screen coordinate and preserves zoom. Compensate the camera for the selected node’s layout delta; do not automatically fit the graph.

