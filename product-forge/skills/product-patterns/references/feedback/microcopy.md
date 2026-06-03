---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Kinneret Yifrah — *Microcopy: The Complete Guide*, 2nd ed. (Nemala, 2019). ISBN 9789655727944. https://www.microcopybook.com/"
  - "Nielsen Norman Group — 'The 3 I's of Microcopy: Inform, Influence, and Interact' (Maria Rosala). https://www.nngroup.com/articles/3-is-of-microcopy/"
  - "Nielsen Norman Group — 'Error-Message Guidelines' (Page Laubheimer). https://www.nngroup.com/articles/error-message-guidelines/"
  - "Nielsen Norman Group — 'UI Copy: UX Guidelines for Command Names and Keyboard Shortcuts' / 'UX Copy Sizes' (Anna Kaley, Kate Moran). https://www.nngroup.com/articles/ui-copy/ , https://www.nngroup.com/articles/ux-copy-sizes/"
  - "Mailchimp — *Content Style Guide* (voice & tone). https://styleguide.mailchimp.com/voice-and-tone/"
  - "Laws of UX — 'Tesler's Law' (conservation of complexity). https://lawsofux.com/teslers-law/"
---

# UX Writing and Microcopy

Microcopy is the smallest text in the interface — button labels, field hints, error and empty-state messages, confirmations, permission prompts, the words on a toggle. Kinneret Yifrah's working definition: the words that _accompany the user's actions_. These tiny strings carry disproportionate weight: a button verb decides whether a user trusts what's about to happen, an error sentence decides whether they recover or rage-quit, an empty state decides whether a blank screen reads as broken or as an invitation. This reference covers voice and tone, the discipline of honest microcopy, and the canonical forms for buttons, labels, errors, and empty states — with the good-vs-bad contrasts a reviewer needs.

> The framing to hold onto: microcopy is **the interface speaking in the user's moment of doubt.** Every string answers a silent question — "what does this button do?", "what went wrong?", "is it safe to click?", "why is this empty?". Good microcopy answers the actual question, plainly, in the product's voice but the moment's tone. Bad microcopy answers a question nobody asked, or hides the answer behind cleverness.

## Voice vs. tone: one personality, many moments

The foundational distinction, articulated in Mailchimp's style guide and echoed across the field: **voice is the product's consistent personality; tone is how that voice flexes to the situation.** Your voice might be clear, calm, and direct everywhere — but the tone turns empathetic in an error, encouraging in onboarding, neutral on a legal page, and quietly celebratory on success. Voice is fixed; tone is contextual. A product that uses the same chipper tone to confirm a payment and to report a failed one has confused the two.

NN/g frames microcopy's _jobs_ as the **3 I's — Inform, Influence, Interact**: it informs (sets expectations, explains state), influences (motivates the next step, reduces hesitation), and interacts (responds to what the user just did). A given string usually leads with one. A field hint mostly _informs_; a primary CTA mostly _influences_; a success toast mostly _interacts_. Knowing which job a string is doing tells you what "good" looks like for it.

## The honesty principle: microcopy must not lie or manufacture feeling

The line that separates UX writing from manipulation: **microcopy describes what is true and what will happen — it does not invent urgency, shame the user, or disguise the consequence of an action.** This is where microcopy meets deceptive patterns (see `../monetization/social-proof.md` for the full taxonomy). Concretely:

- **Buttons name their real consequence.** "Delete permanently" not "OK"; "Subscribe — $9/mo after trial" not "Continue." Yifrah's rule is that the user should never be surprised by what a click did.
- **No confirmshaming.** A decline option phrased to shame ("No thanks, I hate saving money") is a recognized deceptive pattern, not voice-driven copy.
- **No fabricated urgency or social proof in the copy.** "Only 2 left!" or "12 people are viewing this" must be _true_, or it is a fake-scarcity / fake-social-proof pattern — a copywriting decision that crosses into deception.
- **Honest about errors and limits.** Don't blame the user, don't pretend nothing happened, don't bury the cost. NN/g: never use "invalid"/"illegal"/accusatory phrasing.

Honest microcopy is not the same as blunt or joyless — it is microcopy whose persuasion comes from the genuine value of the action, not from engineered pressure or hidden truth.

## Canonical form: buttons and labels

Buttons are the highest-leverage microcopy in the product. The canon:

- **Lead with a verb that names the outcome.** NN/g: command labels should be verbs or verb phrases that make the result obvious — "Print," "Save changes," "Send invite," "Accept and continue." The user should predict what happens before clicking.
- **Be specific, not generic.** "Create project" beats "OK"; "Discard draft" beats "Cancel." Generic labels force the user to reconstruct meaning from context. The strongest pattern pairs the verb with its object: `verb + noun`.
- **Match the button to the user's goal, not the system's.** Label the action from the user's intent ("Get my report") rather than the system's mechanics ("Execute query").
- **Consistency.** The same action uses the same word everywhere — don't alternate "Delete"/"Remove"/"Trash" for one operation. Inconsistent terminology makes users wonder if they're different actions.
- **Keep it short, front-load meaning.** Buttons are scanned, not read; the meaningful word goes first so it survives truncation.

```text
Field / control labels
- Label what the field is, in the user's words: "Work email" not "Email_Addr_2"
- Required vs. optional made explicit (mark the rarer one; if most are required, mark "(optional)")
- Helper text states the rule before the error: "8+ characters, including a number"
- Toggle/switch labels name the state, not a command: a switch reads "Email notifications", not "Turn on"
```

## Canonical form: error messages

NN/g's error-message guidelines are the field standard. A good error message does three things — **says what happened, why (if known), and what to do next** — and obeys a set of rules on placement, tone, and effort:

- **Placement:** show the message close to its source; associate it with the affected field/element to cut the cognitive load of hunting for it.
- **Visibility:** make it noticeable (bold, high-contrast, conventionally red for errors) — but never rely on color alone (a11y).
- **Tone:** plainspoken, non-judgmental, never blaming. Avoid "invalid," "illegal," "you failed." Avoid humor that goes stale on the third repeat.
- **Content:** constructive — offer the remedy, not just the diagnosis. Where possible, give a short list of fixes the user can pick from.
- **Timing:** don't fire errors prematurely on fields the user hasn't finished (a "hostile pattern"); validate at the right moment, and use real-time guidance for error-prone fields.
- **Effort:** preserve the user's input so they can edit rather than re-enter everything.

```text
Bad   "Error: invalid input."
Good  "That email is missing an @. Check the address and try again."

Bad   "Something went wrong."
Good  "We couldn't save your changes — your connection dropped. Retry?"  [Retry]

Bad   (password rule revealed only on failure)
Good  helper text up front: "8+ characters, 1 number" — error only if violated
```

## Canonical form: empty states

An empty state is the screen before the user has data. NN/g treats it as a **pull-revelation opportunity** — a teachable moment, not a dead end. The canonical empty state: confirms the state is intentional (not broken/loading), explains _why_ it's empty, and offers the single concrete action that fills it.

```text
Bad   (blank screen, no text)                          -> reads as broken
Bad   "No data."                                       -> what do I do?
Good  "No projects yet.
       Create your first project to start tracking work."   [Create project]
Good  (no search results)
      "No results for 'widgit'. Check the spelling or try a broader term."
```

NN/g's anti-patterns here: the _totally_ empty state (ambiguous — broken or empty?), the _misleading_ "no records" that then fills after loading (destroys trust), and the _vague_ instruction that says what to do but not how.

## Variants

- **Confirmation / success messages** — close the loop on an action ("Invite sent to maria@…"). Specific beats generic; name what succeeded and, when useful, offer the next step or an undo.
- **Onboarding / encouraging copy** — tone leans warm and motivating; still honest about effort. Frame the gain ("See your first insight in 2 minutes"), not just the task.
- **Permission / consent prompts** — state plainly what's requested and why the user benefits; the accept/decline must be symmetric and unshamed.
- **Confirmation dialogs for destructive actions** — name the consequence in the body and the button ("Delete 3 files? This can't be undone." / "Delete files"). Never make the safe choice the harder one to find.
- **Inline validation hints** — the helper text that prevents the error (the rule shown _before_ failure), distinct from the error that reports it.
- **Tooltips / microcopy on hover-focus** — secondary clarification; must be reachable by keyboard and not carry essential info alone (a11y).
- **Loading / progress copy** — sets expectations for waits past the Doherty threshold; "Crunching your data…" beats a silent spinner for long operations.

## Anti-patterns

| Anti-pattern | Why it fails | The fix |
| --- | --- | --- |
| **Generic buttons ("OK", "Submit", "Cancel")** | Forces the user to infer the consequence from context | `verb + noun` naming the real outcome |
| **Blame-y / robotic errors ("invalid input")** | Accusatory, jargon-laden, offers no recovery (NN/g) | Plainspoken: what happened + how to fix it |
| **Mismatched tone** | Cheery copy on a failure (or vice versa) feels tone-deaf | Flex tone to the moment; keep voice constant |
| **Cleverness over clarity** | Jokes/puns that obscure the action or stale on repeat | Clear first; personality only where it doesn't cost comprehension |
| **Confirmshaming declines** | Shames the user into the "yes" — a deceptive pattern | Neutral, symmetric decline copy |
| **Fabricated urgency/scarcity in copy** | "Only 2 left!" when untrue is fake scarcity | Say it only if true; otherwise cut it |
| **Hover-only essential microcopy** | Invisible to touch/keyboard/AT users | Persistent inline text for anything essential |
| **Inconsistent terms for one action** | "Delete" vs "Remove" vs "Trash" implies different operations | One action, one word, everywhere |
| **Premature/blocking validation errors** | Flags fields the user hasn't finished — hostile (NN/g) | Validate at the right moment; show rules up front |
| **Empty state that says what, not how** | Strands the user at the blank screen | One concrete next action + the steps |

## Accessibility

- **Errors must not rely on color alone** (WCAG 1.4.1, Use of Color). Pair the red with an icon and text; associate the message with its field via `aria-describedby`, and expose it to assistive tech (e.g. an `aria-live`/`role="alert"` region) so it's announced, not just shown.
- **Link and button text must make sense out of context** (WCAG 2.4.4). Screen-reader users navigate by a list of links/buttons; "Read more" / "Click here" / "Learn more" repeated across a page is unusable. The visible label should carry the meaning; if extra context is unavoidable, add it via accessible name.
- **The accessible name must include the visible label** (WCAG 2.5.3, Label in Name) — voice-control users say what they see, so a button reading "Send" must not have an accessible name of "Submit form 12."
- **Hover/focus microcopy (tooltips) must meet WCAG 1.4.13** — dismissible, hoverable, persistent — and never be the sole carrier of essential information.
- **Plain language aids cognitive accessibility.** Short sentences, common words, one idea per string, and the action stated directly help everyone and are load-bearing for users with cognitive or reading disabilities.
- **Form fields need programmatic labels** (WCAG 1.3.1 / 4.1.2), not placeholder-only labeling — placeholders vanish on input and are low-contrast.

## Good vs. bad (for scoring)

| Dimension | Good — microcopy that works | Bad — microcopy that doesn't |
| --- | --- | --- |
| **Button labels** | `verb + noun`, names the outcome | "OK" / "Submit" / "Continue" |
| **Voice/tone fit** | One voice, tone flexed to the moment | Same tone for success and failure |
| **Errors** | What happened + why + how to fix; non-blaming | "Invalid input" / "Something went wrong" |
| **Empty states** | Explains the blank + one concrete action | Blank screen, or "No data" |
| **Honesty** | Says only what's true; consequence named | Fake urgency, confirmshaming, hidden cost |
| **Clarity vs. cleverness** | Plain first; personality where it's free | Puns that obscure or stale |
| **Consistency** | One action → one term everywhere | "Delete"/"Remove"/"Trash" mixed |
| **Timing** | Validates at the right moment; rules shown up front | Premature/blocking errors |
| **Accessibility** | Not color-alone; labels self-sufficient; name-in-label | Color-only errors; "click here" links; placeholder-as-label |

The single test: **read each string aloud as the answer to the user's silent question in that moment.** If the button doesn't say what it does, the error doesn't say how to recover, the empty state doesn't say what to do next, or the copy says something that isn't true — the microcopy has failed its one job, no matter how on-brand the voice.
