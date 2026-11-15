---
name: ui-interaction-dev
description: Build UI interactions that work for every input - pointer and touch drag and drop (thresholds, touch scrolling, drop indicators, cancel), the single-pointer and keyboard alternatives WCAG 2.5.7 requires, live-region announcements, focus, hover that changes only the face, target sizes (WCAG 2.5.8), shadow DOM traps, dialogs and popups (Escape closes the innermost, where a popup renders), date entry (digits, locale, calendar system, ranges) and custom fields in forms. Keeps a spec of rules, each sourced from a primary reference or validated by a test with a negative control. Use for "add drag and drop", "touch drag scrolls the page", "hover states", "menu ignores Enter in shadow DOM", "Escape closes the dialog under the menu", "the date field rejects typed dates", or before building any pointer interaction. NOT for colours (ui-colors), lengths and radii (ui-geometry), paint and materials (ui-materials), the showcase canvas (ui-showcase-bento), or one system's component recipes (that system's skill).
---

# UI interaction

How a part behaves under a pointer, a finger, a keyboard and a screen reader, as a spec of rules with one reading each. A rule is **sourced** (a primary source states it), **validated** (an implementation's test proved it, with a negative control) or **contested** (the sources disagree, and both are kept). The spec grows only from evidence: a source, or a test that bit. This skill owns behaviour; every length comes from ui-geometry and every paint from ui-materials.

Contents: [Route](#route) · [Rules of the spec](#rules-of-the-spec) · [Procedure](#procedure) · [Core rules](#core-rules) · [Commands](#commands) · [Files](#files)

## Route

Read the row whose question is open. Paths are relative to this file.

| Question | Read | Load when |
|---|---|---|
| What must this interaction do, and how sure are we? | `references/spec.md` at its area, or `node scripts/spec.mjs --area <area>` | Always, before building or reviewing one |
| How do I build a drag (state machine, numbers, indicator, alternative, tests)? | `references/drag-and-drop.md` | Building or fixing a drag, a sortable list or a board |
| What does a word mean here (pending, live, lifted, hit area, validated)? | `references/terms.json` | A term could be read two ways |
| How do I add a rule or record what an implementation proved? | [Rules of the spec](#rules-of-the-spec), then `references/spec.json` | After any implementation whose tests taught something |

## Rules of the spec

These hold for every rule in `references/spec.json`, and `node scripts/spec.mjs --check` enforces each one.

| Rule | Why | Check |
|---|---|---|
| One obligation per rule, in RFC 2119 words (MUST, SHOULD, MAY), with a why | A rule with two readings gives two right-looking answers | `validate`: keyword and why; tests "RFC 2119 obligation" |
| A sourced rule cites a primary https source; a contested rule cites the sources that disagree | A rule nobody can trace is an opinion | `validate`: sources; test "cites an https source" |
| A rule becomes validated only with a record: date, where (generic), finding, and the check that proved it | "It worked" is not evidence; the check is | `validate`: record fields; test "dated record" |
| A finding that contradicts a source is recorded as it was measured, and the rule says which to follow | The spec reports what is true, not what was expected | Judgement, at review |
| No record names a host project; where says what kind of thing was built and on what | The skill serves every project | `validate` with BANNED; test "names a host project" |
| spec.md is generated from spec.json, never edited | One home per fact | `--check` compares; test "drift is caught" |
| After an implementation, its validated insights are written back before the work is called done | Knowledge that stays in one repo's tests is lost to the next | Procedure step 6 |

## Procedure

1. **Read the area.** `node scripts/spec.mjs --area drag` (or `alternative`, `announce`, `focus`, `hover`, `motion`, `target`, `shadow`, `overlay`, `date`, `form`, `mode`, `support`, `testing`). Treat MUST as acceptance criteria and SHOULD as defaults to keep unless a test shows otherwise.
2. **Build** from the guide for the interaction (`references/drag-and-drop.md` for drags), taking lengths from ui-geometry and paint from ui-materials.
3. **Test with real input** (`testing.real-input`): page.mouse, CDP touch events with touch emulation, the browser's hit test, the live region's text.
4. **Run each new check against the old code** and see it fail (`testing.negative-control`). A check that passes there is rewritten.
5. **Report** each MUST as met (with its test), not met, or not applicable, and each SHOULD you departed from, with why.
6. **Write back.** For each rule a test now proves, add a validation record (`on`, `where`, `finding`, `check`) and set status validated; for a new lesson (a bug found, a browser quirk), add a rule with its evidence; for a measured result that contradicts a source, record it and say which to follow. Then run `node scripts/spec.mjs` and `node --test scripts/`.

## Core rules

The rules most often missed; the full set is in `references/spec.md`.

- A press becomes a drag only past a threshold: 4px for a mouse, 250ms at rest for a finger (`drag.activation`).
- The dragged item follows by `translate` and keeps its slot; a line marks the landing (`drag.no-reflow`, `drag.indicator`).
- Escape and pointercancel put it back; the click after a drop is swallowed (`drag.cancel`, `drag.swallow-click`).
- Every drag has a Move menu on the item, named for it, reachable by Tab, returning focus to it (`alternative.*`).
- Hover changes the face only, inside `(hover: hover)`, never on a part that holds state (`hover.*`).
- Every target takes the pointer over 24 CSS px, 44 on a coarse pointer, by box, hit area or a named exception (`target.*`).
- Inside shadow DOM, ask the root for focus and composedPath for the pressed part (`shadow.*`).
- Escape closes only the innermost layer; a popup opened inside a modal renders inside it (`overlay.*`).
- A date field reads bare digits, the locale's digits and four-digit years as typed, in the Gregorian calendar, and keeps invalid text visible while the form holds nothing (`date.*`).
- A custom field resets with its form and points validation at its visible control (`form.*`).

## Commands

- `node scripts/spec.mjs`: validate the spec and write `references/spec.md`.
- `node scripts/spec.mjs --check`: exit 1 on an invalid rule or a stale spec.md.
- `node scripts/spec.mjs --area <area> [--status validated|sourced|contested]`: print the rules that match.
- `node --test scripts/`: the spec's rules, each with a negative control, and this file's routes.

## Files

`references/spec.json` (the rules, the source of truth), `references/spec.md` (generated), `references/drag-and-drop.md` (building a drag), `references/terms.json` (vocabulary), `scripts/spec.mjs` (validate, render, query), `scripts/spec.test.mjs` (checks), `evals/triggers.json` (routing cases for the description; rerun them when the description or scope changes).
