---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Don N., *The Design of Everyday Things*, Revised & Expanded Edition (Basic Books, 2013) — affordances, signifiers, mapping, constraints. Signifier introduced/elaborated in the 2013 edition."
  - "Don N., “Affordances and Design” (jnd.org/affordances-and-design) — the affordance-vs-signifier clarification."
  - "Nielsen Norman Group — “Checkboxes vs. Radio Buttons” (nngroup.com/articles/checkboxes-vs-radio-buttons)."
  - "Nielsen Norman Group — “Toggle-Switch Guidelines” (nngroup.com/articles/toggle-switch-guidelines)."
  - "Nielsen Norman Group — “Slider Design: Rules of Thumb” (nngroup.com/articles/gui-slider-controls)."
---

# Inputs & Controls

This is the working method for the lowest layer of the interaction model: the physical and logical means by which a user acts on the product. Before commands, feedback, or automation exist, the user must be able to point, type, speak, toggle, or drag — and the system must signal what is touchable and what each control will do. Two failures dominate here, and both are diagnosable on sight: choosing a control whose semantics don't match the choice the user is making (a toggle where a radio belongs), and shipping a thing the user can act on but cannot _see_ that they can act on (an affordance with no signifier). This file is about getting both right.

## Norman's vocabulary: affordance, signifier, mapping, constraint

Norman's four terms are the spine of input design, and the affordance/signifier pair is the one product people most often blur. Keep them separate.

- **Affordance** — a relationship between an object and an agent that determines _what action is possible_. A button affords pushing; a list affords scrolling; a draggable card affords moving. Affordances are about capability, not appearance. An affordance can exist and be completely invisible.
- **Signifier** — the perceivable signal that _communicates where and how_ to act. Norman introduced the term in the 2013 edition precisely because the design community had stretched "affordance" to mean "the visual cue," which it never was. His one-line split: **"Affordances determine what actions are possible. Signifiers communicate where the action should take place."** A crosswalk is a signifier; the road's traversability is the affordance.
- **Mapping** — the relationship between controls and their effects. Good mapping exploits spatial and cultural analogies (a volume slider that goes up for louder; stove knobs laid out like the burners). Bad mapping forces the user to memorize an arbitrary lookup.
- **Constraint** — a limit designed into the system that reduces the space of possible actions, so the user can't take a wrong one. Physical (a SIM card fits one way), logical (only one radio in a group can be on), cultural (red means stop), semantic (the situation rules out an action). Constraints prevent errors before they happen — the cheapest error handling there is.

The operational test: for every action you intend the user to take, ask "what is the affordance, and what is its signifier?" If you can name the affordance but not the signifier, users will not discover the action. If the signifier is present but suggests the wrong action (a label-shaped thing that's actually clickable), you have a _false signifier_ — a lie the interface tells.

## Input modalities and their grain

Each modality has a native grain — the kind of input it is good at and the cost it imposes. Match the modality to the task, and never assume the one you designed for is the one the user has.

| Modality | Native strength | Cost / failure mode | Design consequence |
| --- | --- | --- | --- |
| **Pointer (mouse/trackpad)** | Precise targeting, hover-to-preview, fine drag | No hover on touch; small targets punish | Hover can _enhance_ but must never _gate_ — the action must work without it |
| **Touch** | Direct, spatial, two-handed gestures | Fat-finger imprecision; no hover; occlusion by the finger | Targets ≥ ~44px; put controls where fingers don't cover the result |
| **Keyboard** | Speed for experts, text entry, full accessibility path | Discoverability — shortcuts are invisible until learned | Everything operable by pointer must be operable by keyboard (it's also the a11y floor) |
| **Voice** | Hands/eyes-free, fast for known intents | No discoverability of vocabulary; ambiguous; public-space friction | Needs confirmation of interpretation and a visible fallback; never the _only_ path |
| **Camera / sensors** | Capture of the physical world (scan, measure, AR) | Lighting/permission/privacy; high failure rate | Always degrade to manual entry; treat as accelerator, not gate |

The cross-cutting rule: **modalities compose, they don't substitute.** A power user wants the keyboard _and_ the pointer; a touch user who plugs in a keyboard should get both. Designing for a single modality and bolting the others on later is the tell of an input model that will fail an audience you didn't picture.

## Control-type selection: the decision table

The most common, most mechanizable input defect is the wrong control type for the choice being made. NN/g's guidance converges into a clean decision procedure. Run it for every control.

| If the choice is… | Use | Not | Because |
| --- | --- | --- | --- |
| A single independent on/off that takes effect **immediately** | **Toggle switch** | Checkbox | A toggle implies instant system state change; a checkbox implies "stage this, then submit" |
| One on/off that's **submitted with a form** ("I agree") | **Single checkbox** | Toggle | The setting doesn't take effect until the form is sent — toggle would lie about immediacy |
| **One of several** mutually exclusive options, all worth showing | **Radio buttons** | Dropdown | All options visible at once → comparison is free; ~7 or fewer |
| **One of many** mutually exclusive options (long list) | **Select / dropdown** | Radios | Conserves space when the option count would overwhelm a visible list |
| **Zero-to-many** independent options from a set | **Checkbox group** | Multiple toggles | Checkboxes read as a set; a wall of toggles reads as unrelated switches |
| A value on a **continuous or coarse range** where the _approximate_ value matters more than precision | **Slider** | Number field | Direct, playful, shows range; but imprecise — pair with a readout/step |
| A value needing **exact precision** | **Number input** (optionally + stepper) | Slider alone | Sliders can't hit "exactly 250" reliably on touch |

Two tells worth internalizing. First, **toggle-vs-checkbox is decided by immediacy, not by aesthetics** — "does flipping it change the system right now, or only on save?" Second, **radio-vs-select is decided by the value of seeing all options at once**: radios make the full choice set legible (good for comparison, defaults, and a small set); a dropdown hides everything but the current value (good for space, bad for discovery). A dropdown of two options is almost always two radios in disguise.

State and labeling rules that ride along: a slider must always show its current value; a toggle's two states must be unambiguous without color alone (a switch _position_ plus a label, not just green/grey); radio and checkbox groups need a group label and a sane default; never leave a single radio button (a lone radio can't be deselected — that's a checkbox).

## Signifiers in practice: making the affordance perceivable

An affordance the user can't see is dead weight. The job of the signifier layer is to advertise, accurately, what is actionable.

- **Buttons must look pressable; links must look navigable; static text must look static.** When a flat design strips every signifier, users resort to "mystery-meat" hovering and tap-hunting — discoverability collapses. Some perceivable boundary, contrast, or affordance cue is not decoration; it's the signifier doing its job.
- **The signifier must match the affordance.** A pill-shaped, colored label that isn't clickable is a false signifier; a paragraph that _is_ clickable but looks like body text is a missing one. Both raise the gulf of execution (see `feedback-and-confirmation.md`).
- **Use constraints to make wrong inputs impossible, not merely scolded.** Disable submit until required fields are valid (a logical constraint) rather than letting the user submit and then erroring. Mask a phone field to the expected format. A constraint that prevents the error beats any message that explains it.
- **State must be visible at rest.** A control should signal its current value before the user touches it — a toggle reads on/off at a glance, a selected radio is obviously selected, a disabled action looks disabled _and_ ideally says why.

## Accessibility (the input floor, not an add-on)

- **Keyboard operability is non-negotiable.** Every control reachable and operable by pointer must be reachable (Tab/Shift-Tab) and operable (Enter/Space/arrows) by keyboard. This is WCAG 2.1.1 (Keyboard) and it doubles as the power-user path.
- **Use the native control or the right ARIA role.** A native `<input type="checkbox">`, `<input type="radio">`, `<select>`, or `<input type="range">` ships keyboard behavior, state, and screen-reader semantics for free. A custom `<div>` toggle must re-implement `role="switch"`, `aria-checked`, focus, and key handling — usually worse.
- **Target size** ≥ 24×24 CSS px minimum (WCAG 2.5.8), ~44px recommended for touch (2.5.5) — fat-finger error is an accessibility issue, not just a polish one.
- **Don't encode state in color alone** (WCAG 1.4.1). A toggle's on/off, a slider's filled track, a selected radio — each needs a non-color signal (position, fill, checkmark, label).
- **Label every control** with a programmatic name (`<label for>`, `aria-label`, or `aria-labelledby`), and group radios/checkboxes in a `<fieldset>`/`<legend>` so the group's purpose is announced.

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Affordance/signifier split** | Clickable thing with no visible cue; or a label-shaped false signifier | Every action has a perceivable, accurate signifier |
| **Control fit (toggle/checkbox)** | Toggle used for a form field that only applies on save | Toggle = immediate effect; checkbox = staged/submitted |
| **Control fit (radio/select)** | Dropdown hiding 3 options the user should compare | Radios when options are few and worth seeing; select when many |
| **Slider use** | Slider used where an exact value is required | Slider for approximate ranges, with a visible readout/step |
| **Modality assumption** | Hover-only action; works on mouse, dead on touch/keyboard | Modalities compose; no action gated behind one input type |
| **Constraints** | Free-form input, validated only after a failed submit | Wrong input prevented up front (masks, disabled-until-valid) |
| **State visibility** | Control's current value unreadable until you interact | State legible at rest, and not by color alone |
| **A11y** | Custom div-control, no keyboard, color-only state, tiny target | Native/ARIA control, full keyboard, non-color state, ≥24px target |
