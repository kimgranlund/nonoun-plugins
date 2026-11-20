# Patterns

Spec 7. Started on 2026-11-13 with wave 1 of the core set. It holds the rules of each pattern that is built after the spike: what the pattern must do, beyond what the [foundation](foundation.md) and the [CSS contract](css-contract.md) already ask of every component. The spike's own patterns keep their rules in the foundation spec (the tabs and the menu button, G7 to G16).

Each pattern's fields are in its manifest. A rule here is an acceptance criterion: whoever builds the pattern, following authoring.md, writes a test for every clause.

The design choices in these rules were made by the session under the author's standing instruction to complete the work without stopping for confirmation.

## Wave 1: activation and form marks

### Switch

One component, a form control like the checkbox.

| # | Rule | Basis | Check |
|---|---|---|---|
| J1 | A switch shall have the switch role and `aria-checked` of `true` or `false`, in step with `checked`. A click, Space and Enter shall toggle it and dispatch `input`, then `change`. While it is disabled none of them shall do anything. | APG switch | Keyboard and pointer test in three engines |
| J2 | A switch shall be a form control as the checkbox is: it submits its name and value while on and nothing while off; a form reset restores its first state; `required` and off is invalid, with `aria-invalid` once the user is due to be told (F5); a label's click toggles it; a disabled fieldset disables it. | F1 to F7, F10 | Form test in three engines |
| J3 | The recipe shall draw a track of ui-geometry's switch width, recessed and neutral when off and solid when on, with a raised neutral thumb at its start when off and at its end when on. The label shall start after the track. Checking shall move no box, and the state shall be painted before the component is defined. | ui-materials: switch; ui-geometry: `switch-track`, `switch-thumb`; U1, U2 | Recipe test in three engines |

### Radio group

Two components: the group, which is the form control and coordinates, and the radio.

| # | Rule | Basis | Check |
|---|---|---|---|
| J4 | The group shall have the radiogroup role and each radio the radio role with `aria-checked`. At most one radio shall be checked: the one whose `value` is the group's. With no value written the group shall take the radio the author marked as checked; a value that names no radio checks none. `value` on the group and `checked` on a radio shall be kept in step both ways. | APG radio group; D67 | Test of each case |
| J5 | The group shall be one stop in the Tab order: Tab enters at the checked radio, or at the first radio that is not disabled when none is checked, and checks nothing. ArrowDown and ArrowRight shall move focus to the next radio and check it; ArrowUp and ArrowLeft the previous; both wrap. Space and a click shall check the radio they land on. A disabled radio shall be passed over, and in a disabled group no radio shall take focus or change. | APG radio group | Keyboard and pointer test in three engines |
| J6 | When the user changes the choice, the group shall write its radios and then dispatch `input` and `change`. It shall dispatch neither when a script changes the value. | G5 | Test that reads the radios inside the listener |
| J7 | The group shall be the form control: it submits its name with the checked radio's value, and nothing when none is checked; a reset restores the first choice; `required` with none checked is invalid, with `aria-required` on the group and `aria-invalid` once the user is due to be told; a disabled fieldset disables it. | F1 to F7 | Form test in three engines |
| J8 | The radio's recipe shall draw a round recessed well with a solid bead while checked, and the label after the well, as the checkbox does its box. The group's recipe shall stack the radios, and put them in a row when `orientation` is `horizontal`. A radio marked `checked` shall be painted before anything is defined, and defining shall move no box. | ui-materials: radio; ui-geometry: `radio-box`, `radio-dot`; U1, U2 | Recipe test in three engines |

### Disclosure and accordion

A disclosure is one component with two things the author writes inside it: a trigger, which is a button, and a panel marked `data-part="panel"`. An accordion stacks disclosures.

| # | Rule | Basis | Check |
|---|---|---|---|
| J9 | A disclosure shall find its panel, the child marked `data-part="panel"`, and its trigger, the first element with the button role or native button that is not inside the panel, wherever the author put it, a heading included. It shall write `aria-expanded` and `aria-controls` on the trigger, and an `id` on the panel only when it has none. | APG disclosure; D66, D79 | Test with the kit's button, a plain element with the button role, and a trigger inside a heading |
| J10 | A click on the trigger, and so Enter and Space, shall show the panel when it is hidden and hide it when it shows, unless the trigger is disabled. The panel shall be displayed exactly while the disclosure has `open`, in the same task as a script's write, and before the component is defined. After the user toggles it the disclosure shall dispatch `toggle`, which bubbles; a script's write dispatches nothing. | APG disclosure; D78; U2 | Pointer, keyboard and recipe test in three engines |
| J11 | An accordion with `single` shall close its other disclosures when one of them opens, whether the user or a script opened it. Without `single` it shall close nothing. Its disclosures are its child elements; one nested deeper belongs to whatever holds it. | APG accordion | Test with a script's write, a click, and a nested accordion |
| J12 | The accordion's recipe shall stack its disclosures with a hairline between them, and defining shall move no box. | ui-geometry: `separator`; U1 | Recipe test |

### Breadcrumb, alert and meter

Three single components with little or no behaviour.

| # | Rule | Basis | Check |
|---|---|---|---|
| J13 | A breadcrumb shall have the navigation role, and the name "Breadcrumb" unless the author named it with `aria-label` or `aria-labelledby`. | APG breadcrumb; A2 | Test with and without an authored name |
| J14 | The breadcrumb's recipe shall lay the author's links in a row that wraps, and draw a separator before each child but the first. The separator shall not be read by assistive technology. The link marked `aria-current="page"` shall be in the ink and the others in the muted ink. | APG breadcrumb | Recipe test in three engines |
| J15 | An alert shall have the alert role unless the author wrote a role, shall take no focus, and shall leave its content as the author wrote it. | APG alert; A1, P1 | Test |
| J16 | The alert's recipe shall lay an optional icon and the message in a row, and paint each variant from the ui-colors roles of that name: the subtle fill as its face, the role's text colour as its ink, the role's border as its line. In forced colours it shall keep a boundary. | ui-colors: `info`, `success`, `warning`, `critical` | Recipe test of every variant in three engines |
| J17 | A meter shall have the meter role and `aria-valuemin`, `aria-valuemax` and `aria-valuenow` in step with `min`, `max` and `value`, with the value held between min and max. | APG meter | Test, with a value outside the range |
| J18 | The meter's recipe shall draw a track of ui-geometry's meter height and a fill whose length is the value's share of the range, following the writing direction. The component shall hand the share to the recipe as a private custom property on the root. Defining shall not change the meter's box. | ui-geometry: `meter-track`; U1 | Recipe test at several values and in a right-to-left scope |

## Wave 2: composite focus

Where a rule is silent on a key, the keyboard table of the pattern's APG page decides.

### Toolbar

| # | Rule | Basis | Check |
|---|---|---|---|
| J19 | A toolbar shall have the toolbar role and be one stop in the Tab order. The arrow keys of its orientation shall move focus among its controls and wrap, Home and End shall go to the first and the last, and Tab shall enter at the control that last had focus. A disabled control shall be passed over. `orientation="vertical"` shall write `aria-orientation` and turn the keys. | APG toolbar | Keyboard test in three engines, with the kit's button and checkbox and a native button |
| J20 | The toolbar's recipe shall lay its controls in a row, or a column when vertical, with ui-geometry's gap for grouped controls, and paint nothing. | ui-geometry: `gap.grouped` | Recipe test |

### Menu: checkable items, groups, submenus and the menubar

These join the menu button's family. The menu and the menu item are built; the menu's class may need to count the new item roles as items, which is the one change to it.

| # | Rule | Basis | Check |
|---|---|---|---|
| J21 | A menu shall treat an element with the menuitemcheckbox or menuitemradio role as an item: roving focus, typeahead and the pointer reach it as they reach a menu item. | APG menu | Keyboard test |
| J22 | A checkbox item shall have `aria-checked` in step with `checked`. Activating it shall turn it on or off and dispatch `change`, which bubbles. A radio item likewise, except that it only turns on, and its group shall then turn off the other radio items that are the group's children. Enter shall close the menu after the change; Space shall leave it open. | APG menu | Keyboard and pointer test in three engines |
| J23 | A menu group shall have the group role, and the name of its label when the author marked one with `data-part="label"`. Its recipe shall separate it from its neighbours with a hairline. | APG menu | Test |
| J24 | A submenu holds one menu item and one menu. ArrowRight, Enter, Space and a click on the item shall open the menu beside the item, with focus on its first item; ArrowLeft and Escape inside it shall close it and return focus to the item, leaving the menu around it open. Activating an item inside it shall close every menu above it and return focus to where it was when the first one opened. The arrows follow the writing direction. | APG menu; ui-interaction-dev `overlay.escape-innermost` | Keyboard test two levels deep, in three engines |
| J25 | A submenu shall write `aria-haspopup`, `aria-controls` and `aria-expanded` on its item, and its menu shall sit beside the item, start edges at the item's end, flipping to the other side where it does not fit. | APG menu; D77 | Test, and a layout test in three engines |
| J26 | A menubar shall have the menubar role and be one stop in the Tab order: the left and right arrows move focus among the buttons of its menus and wrap; ArrowDown, Enter and Space on a button open its menu. While a menu is open, ArrowRight and ArrowLeft shall close it and open the next or the previous menu, unless focus is on an item that opens a submenu in that direction. Escape closes the open menu and returns focus to its button. | APG menubar | Keyboard test in three engines |

### Listbox

A listbox keeps focus on itself and marks one option as highlighted (`aria-activedescendant`), so that the same list can later serve a combobox. That needs a behaviour the kit does not have yet, `activeDescendant`; its rules are B16 to B18 in the foundation spec.

| # | Rule | Basis | Check |
|---|---|---|---|
| J27 | A listbox shall have the listbox role and each option the option role with `aria-selected`. It shall be one stop in the Tab order, keep focus on itself, and name the highlighted option in `aria-activedescendant`. When it takes focus it shall highlight the selected option, or the first that is not disabled. | APG listbox; ui-interaction-dev `focus.cursor` | Keyboard test in three engines |
| J28 | In a single listbox, ArrowDown, ArrowUp, Home, End and a typed letter shall move the highlight and select that option; a click shall select the option it lands on. With `multiple`, the keys only move the highlight, and Space or a click selects the highlighted option or clears it. A disabled option shall be passed over, and a disabled listbox shall take no focus. | APG listbox | Keyboard and pointer test |
| J29 | `value` on the listbox and `selected` on an option shall be kept in step both ways; with `multiple`, the value is the selected values joined by commas. When the user changes the selection the listbox shall write its options and then dispatch `input` and `change`; a script's change dispatches neither. | D67, G5 | Test of each case |
| J30 | The listbox shall be a form control: it submits its name with the selected value, once per selected option with `multiple`, and nothing when none is selected; a reset restores the first selection; `required` with nothing selected is invalid. | F1 to F7 | Form test in three engines |
| J31 | The recipes shall draw a frame padded like a menu with its options as rows. The highlighted option shall have a tint that shows only while the listbox has focus; the selected option a solid face, which differs from the tint and from the pressed paint; a pointer over an option tints it without moving the highlight. A selected option shall be painted before anything is defined. | ui-materials: list; ui-interaction-dev `focus.cursor`, `hover.one-highlight` | Recipe test in three engines |

### Tree

| # | Rule | Basis | Check |
|---|---|---|---|
| J32 | A tree shall have the tree role and each item the treeitem role. An item that has a group, a child marked `data-part="group"`, shall have `aria-expanded`, in step with `expanded`, and its group the group role; its group shall show exactly while the item is expanded, before anything is defined too. The tree shall write `aria-level`, `aria-setsize` and `aria-posinset` on every item. | APG tree view; U2 | Test with three levels |
| J33 | A tree shall be one stop in the Tab order. ArrowDown and ArrowUp shall move focus among the items that show, without wrapping; ArrowRight shall open a closed item, or move to the first child of an open one; ArrowLeft shall close an open item, or move to the parent; Home and End go to the first and last item that shows; a typed letter moves to the next item that shows and starts with it. A click on an item's label shall move focus to it, and on an item with a group also open or close it. | APG tree view | Keyboard and pointer test in three engines |
| J34 | Enter, Space and a click on an item's label shall select that item: it gets `selected` and `aria-selected="true"`, every other item loses them, the tree's `value` follows, and the tree dispatches `change`. `value` and `selected` shall be kept in step both ways. A disabled item shall be passed over. | APG tree view; D67 | Test of each case |
| J35 | The recipes shall indent each group by ui-geometry's tree indent, paint hover, focus and selected on the item's label and not on its group, and draw the focus ring inside the label. | ui-geometry: `tree-indent` | Recipe test |

## Wave 3: overlays

### Tooltip

One component around the element it describes, with the description as a part the author writes.

| # | Rule | Basis | Check |
|---|---|---|---|
| J36 | A tooltip's content, the child marked `data-part="content"`, shall have the tooltip role, and the element it describes, the tooltip's first other child, shall name it in `aria-describedby` unless the author wrote that attribute. The content gets an `id` only when it has none. | APG tooltip; A2 | Test with and without an authored description |
| J37 | The content shall show after the pointer has rested on the described element for a short delay, and at once when that element takes focus from the keyboard. It shall hide when the pointer leaves both the element and the content, when focus leaves, and on Escape, which shall not close a layer around it. The pointer shall be able to move onto the content without hiding it. `open` on the tooltip shall show and hide it from a script. | APG tooltip; WCAG 1.4.13; ui-interaction-dev `overlay.escape-innermost` | Pointer and keyboard test in three engines |
| J38 | The content shall show in the top layer, above the described element and centred on it, below where it does not fit, and take no room while hidden, before the component is defined too. | D77; U2 | Layout test in three engines |

### Dialog and alert dialog

The modal layer is the browser's own `dialog` element, which the author writes inside the component (D91). The component opens it, names it and paints it.

| # | Rule | Basis | Check |
|---|---|---|---|
| J39 | A dialog shall show its `panel` part, the child marked `data-part="panel"`, as a modal exactly while it has `open`: `showModal()` when the attribute is added, in the same task, and `close()` when it is removed. When the browser closes the part, on Escape, through a form with `method="dialog"`, a `command="close"` or the part's own `closedby`, the component shall remove `open`. When the browser opens the part, by a native button's `command="show-modal"` or a script, the component shall set `open`, and shall not close the part before the browser has said that it opened. | D78, D118; the platform's dialog | Keyboard and pointer test in three engines |
| J40 | While it is open the rest of the page shall be inert and Tab shall stay inside; on opening, focus shall go to the element marked `autofocus`, or else to the first control; on closing, it shall return to the element that had focus before. The component shall add no focus handling of its own to what the browser does. | APG modal dialog | Keyboard test in three engines |
| J41 | The component shall name the part after the element marked `data-part="title"` with `aria-labelledby`, and describe it by the one marked `data-part="description"` with `aria-describedby`, unless the author wrote those attributes. With `alert` the part shall have the alertdialog role. | APG modal dialog, alert dialog; A2 | Test of each case |
| J42 | The recipe shall paint the part as an overlay with a backdrop, centred, padded by ui-geometry's dialog depth (`containers.frame.dialog-inset`), no wider than ui-geometry's dialog width and no taller than the viewport, and scroll inside when its content is taller. Nothing of it shall show while it is closed, before the component is defined too. | ui-materials: dialog; ui-geometry: frames | Layout test in three engines |

### Combobox

A combobox is a native input, a popup and, inside the popup, the kit's listbox. Focus stays in the input; the listbox's highlight follows the arrow keys.

| # | Rule | Basis | Check |
|---|---|---|---|
| J43 | The input, the child marked `data-part="input"`, shall have the combobox role with `aria-autocomplete="list"`, `aria-controls` naming the listbox, `aria-expanded` in step with `open`, and `aria-activedescendant` naming the highlighted option while the list is open. Focus shall never leave the input for the list. | APG combobox | Keyboard test in three engines |
| J44 | Typing shall open the list and hide every option whose text does not contain what was typed, whatever its case; when none is left the list shall close. ArrowDown and ArrowUp shall open the list and move the highlight among the options that show, wrapping. Enter, and a click on an option, shall put that option's text in the input, mark it selected, close the list and dispatch `change`. Escape shall close the list, and with the list already closed clear the input. A press outside, and focus leaving, shall close the list. | APG combobox, list autocomplete with manual selection | Keyboard and pointer test in three engines |
| J45 | The popup, the child marked `data-part="popup"`, shall show in the top layer below the field, as wide as the field, above where it does not fit, exactly while the combobox has `open`, and take no room while closed, before the component is defined too. | D77; U2 | Layout test in three engines |
| J46 | The recipe shall paint the root as a field around the input: recessed, a control's height, with the input filling it and drawing nothing of its own, and the focus ring on the root while the input has focus. | ui-materials: field; D14 | Recipe test |
| J80 | While its input carries `readonly`, the combobox shall not open its list, by typing, the arrow keys, a click or a script setting `open`, shall close a list that is open, and shall not change the input's value. Its recipe shall paint the field as J77 says: the etched fill, the etched shadow in place of the ring, no change of face under the pointer, from the first paint, and disabled beats read-only. | ARIA: a read-only combobox's value cannot be changed; ui-materials: review / read-only; D104 | Keyboard and pointer test; recipe test before and after definition, in three engines; forced colours |

## Wave 4: values and text entry

Text entry is always the browser's own input, written by the author inside the component (D14). A value in a range is a custom element that hands its share of the range to its recipe as a private custom property, as the meter does.

### Text field and form field

| # | Rule | Basis | Check |
|---|---|---|---|
| J47 | A text field shall leave its input, the child marked `data-part="input"`, to carry the name, the value, the type and every constraint, and to take part in the form by itself. A click anywhere on the field shall focus the input. `disabled` on the field shall disable the input. | D14 | Form and pointer test in three engines |
| J48 | The text field shall write `aria-invalid="true"` on the input once the input is invalid and the user is due to be told: after the user has changed it and left it, or after a submit attempt. It shall remove it when the input is valid again. It shall mirror that state, and the input's `readonly`, onto its own root as `invalid` and `readonly`, for the recipe. | F5; D33 | Test: untouched, changed and left, submitted, corrected |
| J49 | The text field's recipe shall paint the root as a field: recessed, a control's height, with the input filling it and drawing nothing of its own, text at ui-geometry's text edge, the focus ring on the root while the input has focus, an invalid ring, and fainter ink when disabled. An icon or a button before or after the input shall sit inside the field. | ui-materials: field | Recipe test in three engines |
| J77 | The text field's recipe shall paint a read-only field as ui-materials' etched fill, with the etched shadow in place of the field's ring and no change of face under the pointer, from the first paint: the read-only condition holds for a root whose input carries `readonly` (D104). The ink, the size and the focus ring do not change. Disabled beats read-only: a field that is both paints as a disabled field, with the field's own face and ring, because ui-materials never etches a disabled part. | ui-materials: review / read-only is the etched fill; U2 | Recipe test before and after definition, in three engines; forced colours |
| J50 | A form field shall find its control (the first native input, select or textarea, or element with the checkbox, switch, radiogroup, listbox, combobox, slider or spinbutton role inside it), point its label at the control with `for`, and describe the control by its help text and, while it shows, its error, with `aria-describedby`. It shall give an `id` only where there is none and shall not replace a description the author wrote. | WAI forms; A2 | Test with a text field, a checkbox and a radio group |
| J51 | The form field's error, the child marked `data-part="error"`, shall show exactly while the control is invalid and the user is due to be told, and take no room otherwise, before the component is defined too. A click on the label shall focus or activate the control. | F5; U2 | Test in three engines |
| J52 | The form field's recipe shall stack label, control, help and error with ui-geometry's gap between a label and its control, and paint the error in the critical ink. | ui-geometry: `gap.label-control-control-help` | Recipe test |

### Slider and range slider

| # | Rule | Basis | Check |
|---|---|---|---|
| J53 | A slider shall have the slider role with `aria-valuemin`, `aria-valuemax` and `aria-valuenow` in step with its attributes, and `aria-orientation` when vertical. Its value shall be held between min and max and on a step. | APG slider | Test, with values off the step and outside the range |
| J54 | The arrow keys shall change the value by one step, PageUp and PageDown by ten, and Home and End shall go to the minimum and the maximum; in a right-to-left scope the left and right arrows swap. A press on the track shall move the thumb there, and dragging shall follow the pointer, in a vertical slider too. A disabled slider shall take no key, no pointer and no focus. | APG slider | Keyboard and pointer test in three engines |
| J55 | While the user changes the value the slider shall dispatch `input`, and `change` when they have finished: at pointer release, or after each key. A script's change dispatches neither. The slider shall be a form control: it submits its name and value, and a reset restores its first value. | F1 to F7 | Form test in three engines |
| J56 | The slider's recipe shall draw a track of ui-geometry's height, solid up to the value, and a round raised thumb at the value's share, inside a hit area of ui-geometry's slider hit area, at least 44px on a coarse pointer. Changing the value shall move no box of the root. | ui-geometry: `slider-track`, `slider-thumb`, `slider-hit-area`; U1 | Recipe test in three engines |
| J57 | A range slider shall have two thumbs, each with the slider role, a name, and the limits the other thumb leaves it: the low thumb's maximum is the high value and the high thumb's minimum is the low value. Each thumb shall answer the keys and the pointer as a slider does; a press on the track shall move the nearer thumb. | APG multi-thumb slider | Keyboard and pointer test in three engines |
| J58 | The range slider shall submit its name twice, the low value first, restore both on reset, and dispatch `input` and `change` as the slider does. Its recipe shall fill the track between the thumbs. | F1 to F7 | Form and recipe test |

### Spinbutton and splitter

| # | Rule | Basis | Check |
|---|---|---|---|
| J59 | A spinbutton's input, the child marked `data-part="input"`, shall have the spinbutton role with `aria-valuenow` when its text is a number, and `aria-valuemin` and `aria-valuemax` when the limits are set. ArrowUp and ArrowDown shall step the value, PageUp and PageDown ten steps, Home and End go to a limit that is set; a step from an empty field starts at the minimum, or at 0. Each step shall dispatch `input` and `change` from the input. | APG spinbutton | Keyboard test in three engines |
| J60 | The spinbutton shall create two buttons, named from its messages, that step the value on a click, take no Tab stop and leave focus in the input. A value outside the limits, or text that is not a number, shall make the input invalid in the sense of J48. | APG spinbutton | Pointer test |
| J61 | The spinbutton's recipe shall paint the root as a field, as the text field's does, with the two buttons at its end, each at least 24px in the pointer's direction. | J49; ui-interaction-dev `target.minimum` | Recipe test |
| J81 | While its input carries `readonly`, the spinbutton shall not step, by its buttons, the arrow keys, PageUp, PageDown, Home or End. Its recipe shall paint the field as J77 says, and shall not show the two buttons nor let them take a press, while the field keeps its size, from the first paint. Disabled beats read-only. | ui-materials: in review, controls that only act on the value leave the row and the box keeps its size; D104 | Keyboard and pointer test; recipe test before and after definition, in three engines; forced colours |
| J62 | A splitter shall lay its two panes, the children marked `data-part="start"` and `data-part="end"`, side by side with a bar between them, the first pane taking `value` percent of the room; stacked when vertical. It shall hand the share to its recipe as a private custom property, and the layout shall be right before the component is defined when the author also writes that share as `value`. | APG window splitter; U1 | Layout test in three engines |
| J63 | The bar shall have the separator role, be a Tab stop, carry `aria-valuenow`, `aria-valuemin` and `aria-valuemax`, name the first pane in `aria-controls`, and have `aria-orientation` across the split. The arrow keys along the split shall move it by one step, Home and End to its limits, and Enter shall collapse the first pane and bring it back. Dragging the bar shall follow the pointer. The splitter dispatches `input` while it moves and `change` at the end. | APG window splitter | Keyboard and pointer test in three engines |

## Wave 5: data

A static table is a style-only recipe (J67). The patterns here add behaviour to content the author writes.

### Grid and treegrid

One component around a native table. It needs a behaviour the kit does not have yet, `gridFocus`, which moves focus in two directions; its rules are B19 and B20 in the foundation spec.

| # | Rule | Basis | Check |
|---|---|---|---|
| J68 | A grid shall give its table, the child marked `data-part="table"`, the grid role, and make it one stop in the Tab order: one cell, or the control inside it, is in the Tab order, and the arrow keys move focus cell by cell, stopping at the edges. Home and End go to the ends of the row, with Control to the first and the last cell of the grid, and PageDown and PageUp move by several rows. A click on a cell moves focus to it. | APG grid | Keyboard and pointer test in three engines |
| J69 | A cell that holds exactly one focusable control shall hand focus to that control, so that Enter and Space act on it; any other cell takes focus itself. Header cells are cells. The grid shall write `aria-rowcount` and `aria-colcount` on the table. | APG grid | Keyboard test |
| J70 | With `tree`, the table shall have the treegrid role. A row with `aria-expanded` shows or hides the rows after it whose `data-level` is higher, down to the next row of its own level or lower. Focus can also be on a row: ArrowRight on a closed row opens it, on an open row moves to its first cell; ArrowLeft on an open row closes it, on a closed or leaf row moves to its parent row, and on a first cell moves to the row. The grid shall write `aria-level` on every row from `data-level`. | APG treegrid | Keyboard test in three engines with three levels |
| J71 | The grid's recipe shall paint the table as the table recipe does, draw the focus ring inside the focused cell or row, and tint a row under the pointer. | J67; D74 | Recipe test |
| J79 | A cell that holds more than one focusable control, or one control that takes text or uses the arrow keys itself (an input that is not a checkbox, a radio or a button; a textarea; a select; an element with `contenteditable`; a component with the textbox, combobox, spinbutton, slider or listbox role), shall take focus itself and be the grid's stop. Enter or F2 on it shall move focus to its first control that can take it. While focus is inside the cell the grid shall leave the arrow keys, Home, End, PageUp and PageDown to the control; Tab and Shift+Tab shall move among the cell's controls and wrap; Escape or F2 shall return focus to the cell, and the grid's keys work again. A click on a control inside such a cell focuses that control. The grid shall mark the cell `data-editing` while focus is inside it. The grid shall take the cell's controls out of the Tab order, so the grid stays one stop, and give a control its own `tabindex` back when its cell stops being such a cell. A radio group, a toolbar or any other set of controls in a cell is several controls and follows this rule. | APG grid: editing and navigating inside a cell; D105 | Keyboard test in three engines; mutations |

### Feed

| # | Rule | Basis | Check |
|---|---|---|---|
| J72 | A feed shall have the feed role. Each of its articles shall be focusable, with `aria-posinset` and `aria-setsize` kept right as articles are added and removed. PageDown and PageUp shall move focus to the next and the previous article from anywhere inside one; Control+End and Control+Home shall move focus out of the feed, after and before it. | APG feed | Keyboard test in three engines |
| J73 | `loading` shall write `aria-busy="true"` on the feed. When focus reaches the last article the feed shall dispatch `more`. Its recipe shall stack the articles with a gap and draw the focus ring on the focused article. | APG feed | Test |

### Carousel

| # | Rule | Basis | Check |
|---|---|---|---|
| J74 | A carousel shall have the region role with the role description "carousel", and each slide, a child of the part marked `data-part="slides"`, the group role with the role description "slide" and a name that gives its position, unless the author named it. Only the slide that shows shall be reachable: the others are inert. | APG carousel | Test |
| J75 | The buttons marked `data-part="next"` and `data-part="previous"` shall show the next and the previous slide and be disabled at the ends. `value` shall say which slide shows, follow the user's scrolling, and move the view when a script sets it. The carousel dispatches `change` after the user changes the slide. Nothing shall move by itself. | APG carousel; WCAG 2.2.2 | Pointer, keyboard and scroll test in three engines |
| J76 | The carousel's recipe shall lay the slides in a row that scrolls sideways and snaps to a slide, each slide as wide as the carousel, without a scrollbar showing, and with no animation when the user asks for reduced motion. | U1; reduced motion | Recipe test |
| J78 | The carousel shall write `aria-live="polite"` on the part marked `data-part="slides"`, unless the author wrote `aria-live` there, so that a slide the user brings into view is announced. Nothing in the kit rotates the slides by itself; an author who rotates them writes `aria-live="off"` while they move. | APG carousel: the slide container is a polite live region when rotation is off | Test: written once defined, the author's value kept, a mutation that drops it |

## Style-only recipes

A style-only recipe has no class and no script (D93). Its root is a native element that carries `data-ui="<id>"`, in every target, and a variant is `data-<name>`. Its recipe is scoped to that attribute and otherwise follows the CSS contract.

| # | Rule | Basis | Check |
|---|---|---|---|
| J64 | The link's recipe shall paint an anchor that carries the root attribute in the accent ink, underlined, with a hover and an active ink, a focus ring like the button's, and the plain ink for the link marked `aria-current`. It shall leave an anchor without the attribute alone. | D91 | Recipe test in three engines |
| J65 | The card's recipe shall paint a frame with ui-geometry's card depth as its padding and its radius, its content stacked with the gap between blocks, raised by default and as an outline on the ground with `data-variant="outline"`. | ui-geometry: card frames; ui-materials: card | Recipe test in three engines, at three densities |
| J66 | The badge's recipe shall paint a pill of ui-geometry's badge height with a small label that does not wrap, in the neutral solid by default and in the solid of the ui-colors role named by `data-variant`. | ui-geometry: `mark.badge`; ui-colors roles | Recipe test of every variant |
| J67 | The table's recipe shall lay a native table at full width with rows of ui-geometry's row height, cell padding at the text edge, a hairline under each row, header cells in the muted ink and aligned as their column, and a hover tint on a body row. Numbers shall be alignable to the end with a plain attribute the recipe documents. | ui-geometry: collections rows | Recipe test in three engines |

## Set two: beyond the APG patterns

Nine families a product needs that the APG has no pattern of its own for (D107). Four are components and five are style-only recipes, which follow the paragraph under "Style-only recipes".

### Select

One form control around a popup that holds a listbox, after the APG's select-only combobox.

| # | Rule | Basis | Check |
|---|---|---|---|
| J82 | A select shall have the combobox role, be one Tab stop, and carry `aria-haspopup="listbox"`, `aria-expanded` in step with `open`, and `aria-controls` naming the listbox inside its popup part. The listbox shall take no focus of its own while it is the select's. | APG select-only combobox; A1 | Test, each definition order |
| J83 | The select's value shall be the value of its chosen option. The value part, which the select creates, shall show that option's text, or the placeholder when none is chosen. Setting `value` shall choose the option with that value and mark it `selected`; a value no option has shall choose none. The value shall be submitted under `name`, restored and reset with the form, and `required` shall make an empty select invalid. | D18; APG | Form tests of D18 that apply; test of each clause |
| J84 | A press on the select, Enter, Space, ArrowDown, ArrowUp, Home and End shall open the list, pointing at the chosen option (Home at the first, End at the last). In an open list the arrows, Home and End shall move the pointed-at option without wrapping and without changing the value; Enter, Space, Tab and a press on an option shall choose it, close, and dispatch `input` then `change` when the value changed; Escape and a press outside shall close and keep the value. Focus shall stay on the select throughout, with `aria-activedescendant` naming the pointed-at option. A disabled option shall not be chosen. | APG select-only combobox | Keyboard and pointer test in three engines |
| J85 | Typing characters shall move to the next option whose text starts with them: in an open list it moves the pointed-at option, and on a closed select it opens the list there. | APG; `typeahead` | Test |
| J86 | A disabled select shall not open and shall take no focus. Escape shall close only the list, not a layer around the select. | A4; ui-interaction-dev `overlay.escape-innermost` | Test, inside a dialog |
| J87 | The select's recipe shall paint a control of a control's height with the value at the start and a mark at the end, of one fixed width unless the author sizes it, a value too long for it ending in an ellipsis, with the placeholder in the muted ink. The width does not follow the value, which exists only once the select is defined. The popup shall show in the top layer under the select, at least as wide as it, above where it does not fit, and take no room while closed, before the select is defined too. Defining shall not move the select. | U1, U2; D77 | Recipe test in three engines |

### Popover

One component around the control that opens it, with the panel as a part the author writes.

| # | Rule | Basis | Check |
|---|---|---|---|
| J88 | A popover's content, the child marked `data-part="content"`, shall have the dialog role unless the author wrote a role, and the control, the popover's first other child, shall carry `aria-haspopup="dialog"`, `aria-expanded` in step with `open`, and `aria-controls` naming the content. The content gets an `id` only when it has none, and `tabindex="-1"` unless the author wrote a tabindex, so that it can take focus. | APG dialog (non-modal); A2 | Test with and without authored attributes |
| J89 | A click on the control shall open the popover and, when it is open, close it; Enter and Space do so through the control's own click, as a button's do, so the control is a button of the kit or a native one. A change of `open` to showing shall move focus to the content's first focusable element, or to the content itself; a popover written open in the markup takes no focus when it is defined. Escape, a press outside, and focus leaving the popover shall close it; Escape and a press on the control shall return focus to the control, and Escape shall not close a layer around it. `open` shall show and hide it from a script, and `toggle` shall be dispatched after each change. The page behind stays operable. | APG; ui-interaction-dev `overlay.escape-innermost` | Pointer and keyboard test in three engines |
| J90 | The content shall show in the top layer, below the control and aligned to its start, above where it does not fit, kept inside the window, and take no room while closed, before the component is defined too. | D77; U2 | Layout test in three engines |
| J91 | The popover's recipe shall paint the content as a raised overlay panel with ui-geometry's popover padding and radius and the kit's overlay shadow, with a boundary in forced colours. | ui-materials: overlay; ui-geometry: containers | Recipe test in three engines |

### Toast

A message and the stack that holds it.

| # | Rule | Basis | Check |
|---|---|---|---|
| J92 | A toast shall have the status role, or the alert role when its variant is `critical`, unless the author wrote a role. It shall take no room and not be read while it lacks `open`. | ARIA status and alert; A1 | Test of each variant |
| J93 | An open toast shall close itself `duration` milliseconds after it opened, and never when `duration` is 0. The time shall not run while the pointer is over the toast or focus is inside it, and shall start again from the full duration when both have left. A press on the part marked `data-part="close"`, and Escape while focus is inside, shall close it. Closing, however it came about, shall remove `open` and dispatch `close` once. | WCAG 2.2.1 | Test with a short duration, in three engines |
| J94 | A toaster shall have the region role and the name "Notifications" unless the author named it. It shall show in the top layer while it holds an open toast and leave it when it holds none, sit in the corner of the window `placement` names, stack its toasts with the newest nearest that corner, and let presses through wherever no toast is. | ARIA landmarks; D77 | Layout test in three engines |
| J95 | The toast's recipe shall paint a raised overlay panel no wider than ui-geometry's toast measure, the message and the close control in a row, and each variant from the ui-colors role of that name as the alert does. In forced colours it shall keep a boundary. It shall enter with a transition only when motion is allowed. | ui-colors roles; J16 | Recipe test of every variant in three engines |

### Progress

| # | Rule | Basis | Check |
|---|---|---|---|
| J96 | A progress shall have the progressbar role and `aria-valuemin`, `aria-valuemax` and `aria-valuenow` in step with `min`, `max` and `value`, with the value held between min and max. Without `value` it shall carry no `aria-valuenow`. | ARIA progressbar | Test, with a value outside the range and with none |
| J97 | The progress's recipe shall draw a track of ui-geometry's progress height and a fill whose length is the value's share of the range, following the writing direction, handed to the recipe as a private custom property on the root. With no value the fill shall be a part of the track that moves along it when motion is allowed and rests at the start when it is not. Defining shall not change the progress's box. | ui-geometry: `progress-slider-track`; U1; J18 | Recipe test at several values, with none, right to left, and with reduced motion |

### Pagination, tag, avatar, separator and skeleton

Five style-only recipes.

| # | Rule | Basis | Check |
|---|---|---|---|
| J98 | The pagination's recipe shall lay the links and buttons inside a `nav` that carries the root attribute in a row that wraps, each a box of a control's height at least as wide as it is tall, with no list marks. The one marked `aria-current="page"` shall be painted as selected, each shall have a hover and an active face and a focus ring like the button's, and one that is disabled or marked `aria-disabled="true"` shall be in the disabled ink and show no hover. | APG landmarks: navigation; state matrix | Recipe test in three engines |
| J99 | The tag's recipe shall paint a small rounded box with a label that does not wrap, in the subtle fill, text colour and border of the ui-colors role named by `data-variant`, neutral by default. A native button marked `data-part="remove"` inside shall sit at the end as a square with no face of its own, a hover face, a focus ring, and a hit target of at least 24 by 24 CSS pixels. | ui-colors roles; WCAG 2.5.8 | Recipe test of every variant in three engines |
| J100 | The avatar's recipe shall paint a square of ui-geometry's avatar size and radius for the size `data-size` names, medium by default, that clips an image inside to cover it and centres initials in a type size that follows the avatar's. It shall not shrink in a row. | ui-geometry: `controls.media.avatar-*` | Recipe test of every size, with an image and with initials |
| J101 | The separator's recipe shall paint an `hr` that carries the root attribute as a line of ui-geometry's separator thickness across the inline axis with no margin of its own, and with `data-orientation="vertical"` as a line along the block axis as tall as its row. In forced colours the line shall stay visible. | ui-geometry: `controls.mark.separator` | Recipe test in a block and in a row, in three engines |
| J102 | The skeleton's recipe shall paint a shape in the recessed fill: by default a line as tall as a line of text and as wide as its container, with `data-variant="block"` a box the author sizes, with `data-variant="circle"` a circle of the author's size. It shall pulse only when motion is allowed, and keep a boundary in forced colours. | ui-materials: recessed; WCAG 2.3.3 | Recipe test of every variant, with reduced motion |

## Set three: dates, files and three looks

Five new families and two looks of families that exist (D109). The date rules come from ui-interaction-dev's spec, named in each basis.

### Calendar

| # | Rule | Basis | Check |
|---|---|---|---|
| J103 | A calendar shall have the group role unless the author wrote a role, and shall show one month of the Gregorian calendar as a table with the grid role, named by the month and year, with a row of weekday names and the weeks under it. The first day of the week and every name shall follow the language of the page, the nearest `lang`, with a fallback where the engine has no week information. The month shown is `month`, or the month of the value, or of today. | APG date picker; `date.gregorian`, `date.week-start` | Test in several languages, in three engines |
| J104 | The day that is the value shall carry `aria-selected="true"`, and today `aria-current="date"`. The value shall be a `yyyy-mm-dd` string, submitted under `name`, restored and reset with the form; a value that is not a date, or lies outside `min` and `max`, shall choose nothing. `required` shall make a calendar with no value invalid. | `date.value-format`; D18 | Form tests of D18 that apply; test of each clause, with today injected |
| J105 | The grid shall be one Tab stop: the chosen day, or today, or the first day of the month shown, and the stop returns to that day when focus leaves the grid. The arrows shall move focus by a day or a week, Home and End to the first and last day of the week, PageUp and PageDown by a month and with Shift by a year, keeping the day number or else the last day of the month. Focus that moves out of the month shown shall show the month it lands in. Enter, Space and a press shall choose the focused day and dispatch `input` then `change` when the value changed. | APG date picker; `date.grid-keys` | Keyboard and pointer test in three engines |
| J106 | The controls for the previous and the next month shall be buttons named for what they do, shall change the month shown without changing the value or moving focus off themselves, and the month's name shall be announced politely when it changes. | APG date picker | Test |
| J107 | A day before `min` or after `max` shall be marked `aria-disabled="true"`, take focus, and not be chosen. Navigation shall stop at years 0001 and 9999, with the days past them disabled. A disabled calendar shall take no focus and choose nothing. | `date.bounds`; A4 | Test at both ends |
| J108 | The calendar's recipe shall lay seven columns of equal square day cells of a control's height, the selected day in the accent solid, today marked without colour alone, the days of the neighbouring months in the muted ink, a disabled day in the disabled ink with no hover, and a focus ring inside the focused day. In forced colours the selected day shall be `Highlight`. | state matrix; D15 | Recipe test in three engines |

### Date field

| # | Rule | Basis | Check |
|---|---|---|---|
| J109 | A date field's value shall be a `yyyy-mm-dd` string, submitted under the field's `name` while its input carries none, restored and reset with the form. The input shall show the value formatted for the language of the page with a numeric day, month and four-digit year, in the Gregorian calendar. `required`, `min` and `max` shall make the field invalid when no date, or a date outside them, is held; a date outside them is kept and submitted, as a native date input does. | `date.value-format`, `date.gregorian`; D18 | Form tests of D18 that apply; test in several languages |
| J110 | Text the user types shall be read when focus leaves the input or on Enter, and not on each key. It shall be read in the language's field order, with or without separators: eight digits, or six with a short year; a four-digit year is taken as written; the language's own digits are read. A date that is read replaces the text with its formatted form and dispatches `input` then `change` when the value changed. | `date.commit-on-leave`, `date.digits-only`, `date.year-literal`, `date.locale-digits` | Test of each form, in three engines |
| J111 | Text that is not a whole date shall stay in the input as typed, the input marked `aria-invalid="true"`, and the value emptied. Emptying the input empties the value and is not invalid unless `required`. Escape shall put back the text of the held value while the user has typed and not committed, and shall otherwise be left alone. | `date.invalid-kept`, `date.escape-revert` | Test |
| J112 | The toggle part, a press on it, and Alt+ArrowDown in the input shall open the popup; Alt+ArrowUp, Escape, a press outside and the toggle shall close it. Opening shall hand the calendar inside the popup the field's value, `min` and `max` and move focus to the day held, or else to its grid's Tab stop; choosing a day there, the day already held too, shall set the value, close the popup and return focus to the input. Escape shall close only the popup. The input shall carry the combobox role unless the author wrote a role, with `aria-haspopup="dialog"`, `aria-expanded` and `aria-controls`, and the popup the dialog role. Escape, Alt+ArrowUp and the toggle return focus to the input; a press outside leaves focus where it went. | APG date picker combobox; `date.alt-arrow`; `overlay.escape-innermost` | Keyboard and pointer test in three engines |
| J113 | A read-only input shall keep its text, not open the popup and not change the value; the field paints read-only and disabled as the text field does (J77). | J77, J80 | Test |
| J114 | The date field's recipe shall paint the field as the text field's, with the toggle at the end as a square with a calendar mark, and the popup as a raised overlay panel in the top layer under the field, above where it does not fit, taking no room while closed, before the field is defined too. Defining shall not move the field. | J46; U1, U2; D77 | Recipe test in three engines |

### Tag group

| # | Rule | Basis | Check |
|---|---|---|---|
| J115 | A tag group shall have the group role and be one Tab stop: the remove control of one tag. ArrowRight and ArrowLeft, mirrored right to left, shall move among the remove controls without wrapping, and Home and End to the first and last. A tag with no remove control is passed over. | `focus.one-stop`; `rovingFocus` | Keyboard test in three engines |
| J116 | A press on a remove control, and Delete or Backspace while one has focus, shall dispatch `remove` on the group once, bubbling, with the tag in its detail. The group shall not remove the tag itself. When the tag that held focus leaves the group, focus shall move to the remove control of the tag that followed it, or else the one before it, or else the first remove control left, or else the group. | `focus.after-move-out`; P rules | Test with a page that removes and one that does not |
| J117 | A disabled group shall take no focus and dispatch nothing: it marks itself `aria-disabled="true"` and `inert`, so that a native remove button is no Tab stop, and is painted faded. The group's recipe shall lay its tags in a row that wraps with the gap between controls. | A4 | Test; recipe test |

### File field

| # | Rule | Basis | Check |
|---|---|---|---|
| J118 | A file field shall leave its native file input as the author wrote it, visible and operable with no script: the input carries the files, the name and the validity. | D14; `form.visible-control` | Test before definition |
| J119 | Files dragged over the field shall mark it `data-drag` until they leave or are dropped. A drop shall give the input the files it would take, the first only without `multiple` and only those `accept` names, and dispatch `input` then `change` on the input when it took any. A drop on a disabled field, or of something that is not files, shall do nothing, and the page shall not navigate to a dropped file. | HTML: file upload state | Test with a real drag of a DataTransfer in three engines, as far as each engine allows |
| J120 | `disabled` on the field shall disable its input, and an input disabled by the author shall paint the field disabled once the field is defined. A disabled field shall still take a drop of files and do nothing with it, so that the browser does not open the file. | J46 | Test |
| J121 | The file field's recipe shall paint a frame with a dashed boundary and ui-geometry's panel padding, the input's own button as a neutral button of the kit, a focus ring on the field while its input has focus, the accent boundary while `data-drag` holds, and the invalid and disabled looks of a field. Defining shall move nothing. | U1, U2 | Recipe test in three engines |

### Drawer, segmented control and stepper

A look of the dialog, a look of the radio group, and a style-only recipe.

| # | Rule | Basis | Check |
|---|---|---|---|
| J122 | A dialog with `side` set to `inline-start`, `inline-end` or `block-end` shall be a drawer: its panel sits against that edge of the window and is as long as it, with ui-geometry's panel width across (or its height, at the block end), no margin on that edge, and corners rounded only on the edge that faces the page. Everything else about the dialog holds unchanged (J39 to J42), and right to left mirrors the inline sides. With motion allowed the panel slides in from its edge. | D109 | Recipe test of each side in three engines, right to left too |
| J123 | A radio group with `variant="segmented"` shall paint its radios as the segments of one recessed track in a row: each a label with no mark, of equal height, the chosen one raised, with a hover face, a focus ring inside the segment, and the disabled ink. The group's behaviour is unchanged (J4 to J7). The author writes the variant on the group alone; the radio learns it through one inherited private token (C8, D110). It shall be painted so before anything is defined, and in forced colours the chosen segment shall be `Highlight`. | D109; U2 | Recipe test in three engines |
| J124 | The stepper's recipe shall lay the items of an `ol` that carries the root attribute in a row, each with a mark that holds its number, drawn by a counter, and a line joining it to the next. The item marked `aria-current="step"` and the marks before it shall be solid, the ones after it muted, and the current item's label in the ink. With no current item no step is done. With `data-orientation="vertical"` the items run down with the line between the marks. No list marks of the browser show, and the marks are not read twice. | ARIA `aria-current`; D93 | Recipe test in three engines |

## Not components

- **Link.** The kit's link is the browser's own `a` element. A custom element cannot give what an anchor gives: opening in a new tab, the context menu, the address shown before the click, and a link that works with no script. It has a style-only recipe (J64).
- **Landmarks.** They are the browser's own elements (`main`, `nav`, `header`, `footer`, `aside`, `section` with a name). The kit adds nothing to them.
