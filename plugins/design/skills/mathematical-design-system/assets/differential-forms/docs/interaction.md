# Semantics and interaction

Confirmed intent: focus indication only for keyboard interaction; preserve native focus and keyboard operation. A production implementation must show which input or action has focus. Text fields suppress inner focus rectangles and paint a 3px ink outline with a 0px offset on their neutral input wrapper when the field is focus-visible in keyboard mode. All focusable components use the same 3px ink outline and 0px offset. Composite containers allow focused children’s outlines to paint beyond their edges; focused children paint above adjacent siblings. This paint-only indicator preserves geometry. Focus on a sibling selector, clear action or stepper uses that action’s own outline, not the wrapper. Pointer interaction clears keyboard mode; subsequent unmodified keyboard interaction restores it.

Buttons use native button with type=button unless submitting. Disabled buttons use disabled. Filter chips and segmented controls use aria-pressed. Native checkbox/radio semantics retain Space and group behavior; labels are clickable. Select-all uses a real indeterminate property. Custom artwork must preserve forced-colors usability.

Listbox trigger has aria-expanded and aria-controls. Options expose aria-selected, with one selected tab stop. Arrow keys move through options, Home/End move to extremes, Escape closes and returns focus, activation commits selection, Tab leaves normally. Keep options free of interactive descendants. The specimen's option implementation is a reference, not a full assistive-technology audit.

Segmented controls are exclusive pressed buttons in a named group. If used as tabs controlling panels, implement the complete tablist/tab/tabpanel relationship and keyboard model instead. Do not mix the two semantics.

Inputs have names independent of placeholders. Currency selector has its own name. Units and prefixes must be included in accessible naming/description when meaningful. Steppers have distinct increase/decrease names and respect native bounds. Search clear action disables when empty and returns focus to input.

Tables retain native table/header semantics and meaningful checkbox/action names. Scrollable regions have names and keyboard access when necessary. Added content, selected counts and removal/restore actions need predictable focus and status announcements in production.

Unspecified: touch target expansion, validation message associations, disabled chips, asynchronous loading, error recovery, and all assistive-technology combinations. Resolve these explicitly when implementing an application; the small visual slot is not automatically a sufficient interaction target.
