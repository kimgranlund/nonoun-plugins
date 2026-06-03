---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Jef Raskin, *The Humane Interface: New Directions for Designing Interactive Systems* (Addison-Wesley, 2000) — commands, noun-verb vs. verb-noun construction, monotony, habituation."
  - "Apple Human Interface Guidelines — “Menus” and “Keyboard shortcuts” (developer.apple.com/design/human-interface-guidelines)."
  - "Nielsen Norman Group — “Command-Line Interfaces & Command Palettes” / accelerators in the 10 Usability Heuristics, Heuristic #7 “Flexibility and Efficiency of Use” (nngroup.com/articles/ten-usability-heuristics)."
  - "WAI-ARIA Authoring Practices — Menu and Menubar pattern (w3.org/WAI/ARIA/apg/patterns/menubar)."
---

# Commands & Actions

This is the working method for the verb layer of an interface: how a user tells the product to _do something_. Beneath every button, menu item, shortcut, and command-palette entry is a small grammar — a vocabulary of actions and the objects they apply to. When that grammar is coherent, the same verb means the same thing everywhere and users can predict commands they've never used; when it's incoherent, every screen is a new language. This file covers the command model (noun-verb vs. verb-noun), action vocabulary, command palettes, keyboard shortcuts, and bulk actions — the machinery that turns intent into a system command.

## The grammar: noun-verb vs. verb-noun

Every command pairs a **verb** (the action) with a **noun** (the object it acts on), and the _order_ in which the user supplies them is a foundational architecture decision Raskin treats at length in _The Humane Interface_. The two constructions:

- **Noun-verb (object-first):** the user selects the object, then chooses the action. Select the file → press Delete. Select the text → click Bold. This is the modeless default of modern GUIs, and Raskin favours it. Its virtue: once an object is selected it stays selected, so the user can fire several verbs at it in a row, and the system is never in a "waiting for the object of this verb" mode.
- **Verb-noun (action-first):** the user invokes the action, then the system asks _what_ to act on. Press Delete → "delete what?" This puts the interface into a mode (it's now waiting for a noun), which Raskin warns against — if the user forgets which verb is pending, the next click does something unexpected.

The working rule: **prefer noun-verb.** Let users select first and then act, so selection persists and actions compose. Reserve verb-noun for genuinely verb-first flows (a search box, a "create new…" that then prompts for type) and make the pending state loudly visible if you must use it. A mixed model where some toolbars are object-first and some action-first is a coherence defect — users can't form one habit.

## Action vocabulary: one verb, one meaning

The single highest-leverage move in command design is a **controlled vocabulary of verbs.** Pick the canonical verb for each operation and use it _everywhere_ that operation appears.

- **One concept, one word.** If you delete in one place, don't "remove" here, "trash" there, and "clear" elsewhere — unless those are genuinely different operations, in which case the difference must be real and explained. Synonym sprawl forces users to relearn the same action per screen.
- **Verbs are actions; nouns are objects.** Label commands with the verb-or verb+object form ("Archive", "Delete project", "Export CSV"), not with vague nouns ("Options", "Actions") that hide what will happen. A menu item should let the user predict the result before clicking.
- **Reserve destructive verbs for destructive acts.** "Delete", "Remove", "Discard" should always be irreversible-or-recoverable in the same way; don't use "Delete" for a reversible hide. Consistency of consequence is part of the vocabulary.
- **Pair every verb with its inverse where one exists.** Cut/Paste, Add/Remove, Show/Hide, Mute/Unmute, Archive/Unarchive. A verb with no visible inverse is a one-way door the user will hesitate at (see `undo-and-recovery.md`).

The audit: list every action label in the product and cluster by operation. If one operation has three labels, or one label covers three operations, the vocabulary is leaking.

## Command palettes: the universal verb-noun surface

A **command palette** (Cmd/Ctrl-K, Cmd/Ctrl-Shift-P in many tools) is a searchable, keyboard-driven list of every command — a single entry point that scales where menus and toolbars run out of room. It is the modern, humane form of a command line: discoverable (you type and it suggests), forgiving (Esc backs out), and fast for experts.

When to add one: the product has **many commands** (more than fit comfortably in menus/toolbars), a **keyboard-centric audience**, or commands that are otherwise buried several clicks deep. It's an accelerator layered _on top of_ direct controls, never a replacement for them — discoverability for new users still lives in visible UI.

Build rules:

- **Index the verb _and_ the object.** "Archive", but also "Archive this project" and the project's name — fuzzy-match against synonyms and recent items so the user's word finds the command.
- **Show the keyboard shortcut next to each command** so the palette teaches its own accelerators; a power user graduates from palette to muscle-memory shortcut over time.
- **Rank by recency/frequency**, and surface context-relevant commands first (what can act on the current selection).
- **Make actions, navigation, and search legible as different kinds of result** if the palette spans all three, so "go to file" isn't confused with "run command".

## Keyboard shortcuts (accelerators)

Shortcuts are Heuristic #7, "Flexibility and efficiency of use": **accelerators — unseen by the novice — speed up interaction for the expert**, letting the product serve both. They're invisible by nature, so the design problem is teaching them.

- **Honour platform conventions first.** Cmd/Ctrl-C/V/X/Z/A/S/F/N/P are sacred — never rebind them, never repurpose them. Violating them is a Jakob's-Law tax paid on every use.
- **Make them learnable in place.** Show the shortcut in the menu item and the tooltip and the command palette, so the user discovers it while doing the slow version of the action.
- **Map mnemonics where you can** (B for Bold, N for New) so the binding is guessable, not arbitrary.
- **Don't trap the user in a chord nobody can find or escape.** Multi-key sequences should be documented and have a discoverable equivalent; a shortcut that's the _only_ way to do something fails the novice.
- **Respect text-entry context** — a single-key shortcut must not fire while the user is typing in a field.

## Bulk actions: verbs over a set

When users routinely operate on many objects, the command model must extend from "verb on one noun" to "verb on a set." This is where noun-verb pays off: select many, act once.

- **Make multi-select obvious and consistent** — checkboxes, shift-click ranges, "select all / select none / select all matching this filter." The selection mechanism should be the same across every list in the product.
- **Surface a contextual action bar** when a selection exists, showing the verbs that apply to the set ("3 selected · Archive · Tag · Delete"), and report the count so the user knows the blast radius.
- **State the scope precisely before a destructive bulk verb.** "Delete 248 items" is honest; "Delete" is not. For large or irreversible sets, prefer undo (a recoverable bulk action with an Undo toast) over a confirmation dialog the user will click past (see `undo-and-recovery.md`).
- **Show progress and partial failure** for bulk operations that aren't instant — "212 of 248 archived, 36 failed (permission)", not a spinner that resolves to silence.

## Accessibility

- **Every command must be keyboard-reachable**, not just the accelerators — the menu/toolbar/palette entry itself must be operable without a pointer (WCAG 2.1.1).
- **Menus and menubars follow the WAI-ARIA pattern** (`role="menu"/"menuitem"/"menubar"`): arrow keys move within, Enter/Space activate, Esc closes and returns focus to the trigger, with a roving tabindex so the menu is a single tab stop.
- **Command palette** is typically a `role="dialog"` containing a `combobox`/`listbox`; arrow keys move the active option, `aria-activedescendant` tracks it, Enter runs it, Esc dismisses and restores focus.
- **Announce the result of an action** via a polite live region ("3 items archived") so non-visual users get the same confirmation a toast gives sighted users.
- **Don't rely on single-character shortcuts without a modifier as the only path**, and provide a way to remap or disable single-key shortcuts (WCAG 2.1.4, Character Key Shortcuts).

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Grammar order** | Mixed object-first/action-first across screens; invisible pending verb | Consistent noun-verb; selection persists; verbs compose on it |
| **Vocabulary** | "Delete/Remove/Trash/Clear" for the same act; vague "Options" labels | One verb per operation, used everywhere; verb(+object) labels that predict the result |
| **Inverses** | One-way verbs with no visible undo/inverse | Every reversible verb paired with its inverse |
| **Palette fit** | A palette bolted on but commands still unfindable; or no fast path in a command-heavy app | Searchable command palette indexing verb+object, showing shortcuts, ranked by context |
| **Shortcuts** | Rebound Cmd-S/Z; undiscoverable chords; fire while typing | Platform conventions honoured, shown in menus/tooltips, mnemonic, text-safe |
| **Bulk actions** | "Delete" with no count; no multi-select consistency; silent partial failure | Scoped count ("Delete 248"), consistent multi-select, progress + partial-failure report |
| **A11y** | Mouse-only menus; no result announcement; mandatory single-key shortcut | ARIA menu/palette patterns, keyboard-complete, live-region result, remappable keys |
