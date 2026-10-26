# Cross-cutting foundations and conditions

Use the relevant rows as lenses over a chosen profile, not a requirement to add every state to every project. Explicitly identify consequential omissions. Exact platform and compliance requirements need applicable primary sources; these notes do not certify conformity.

| Lens | Reasoning questions | Content and review implications |
| --- | --- | --- |
| First use / repeated use | What must be learned once? What recurring work should become direct? | Explain unfamiliar concepts without repeatedly obstructing skilled users; compare assistance that can recede. |
| Entry / re-entry | Can people arrive deep-linked, return mid-task or switch devices? | Restore context, progress and meaningful next actions; explain stale or unavailable destinations. |
| Loading / empty / partial | Is there no data, no match, no permission, or unfinished loading? | Distinguish causes; communicate freshness/completeness and a useful next step instead of a generic empty illustration. |
| Success / failure / recovery | Is an action committed, queued, partially complete, reversible or failed? | Confirm consequences and ownership; preserve entered work; identify safe retry, undo or escalation paths. |
| Roles / access | Who can see, act, approve or administer? How does scope change? | Explain boundaries without leaking restricted information; clarify workspace/account context and access requests. |
| Collaboration / concurrency | Can another person change the same object? Who owns the next step? | Surface relevant attribution, conflicts, handoffs and stale state. Do not imply changes are saved when they are not. |
| Responsive / device | What must remain possible at different widths, input methods and orientations? | Reorganize task priority rather than merely shrink desktop chrome. Preserve comparisons and access to secondary actions. |
| Accessibility | Can the experience be understood and operated with keyboard, assistive technology, zoom, reduced motion and varied perception? | Preserve semantics, names, focus order, non-color state cues, feedback and alternatives to gesture-only actions. Geometry tokens alone do not prove accessible target sizes. |
| Localization / language | Do labels expand, formats differ, reading direction change, or concepts need explanation? | Use realistic long strings, date/number/unit formats and names. Avoid baking English word length or left/right assumptions into structure. |
| Connectivity / latency | What works offline, what is queued, and what needs confirmation from a service? | Distinguish local intent from committed state; explain sync status, duplication risk and recovery. |
| Privacy / trust | What information is necessary, sensitive, shared or retained? What does the person understand? | Explain consequential collection and sharing at the decision point. Do not propose instrumentation beyond the task's authorization. |
| Destructive / consequential actions | What harm can an error cause and how reversible is it? | Scale confirmation, preview, recovery and audit detail to consequences, not a blanket modal policy. |
| Data scale / density | What changes with one object, thousands of objects, or long content? | Test representative volumes, filtering, bulk scope and truncation; never hide the only route to critical information. |
| Performance / interruption | What feedback preserves confidence while a task takes time? | Explain progress and cancellability where meaningful; avoid fabricated percentages or instantaneous prototype promises. |

## Navigation and information hierarchy

Organize around recognizable objects, subjects, tasks or questions. Determine which model fits the domain before choosing sidebar, tabs, cards, command entry or bottom navigation. Reveal current location, scope and available next steps. A route can have more than one entry point; navigation labels and content must make sense when encountered independently.

Distinguish global navigation, local navigation, filtering, sorting and record selection. Avoid presenting them as interchangeable tabs simply because they look alike. State persistence should follow user expectations for each control. Explicit Locate actions may move focus and scroll; preference changes should not lose the user's place.

## Interaction and content foundations

Explain why input is needed and what follows. Prefer content close to the decision it informs. Keep status, guidance, validation, confirmation and marketing persuasion distinct. Users should be able to understand whether an action is available, what it affects, and whether it succeeded.

Use stable foundations for controls, spacing, typography and semantic colors; use layout freedom to explore the hypothesis. Motion should explain continuity or feedback. It should not be required to discover essential content, and its performance/accessibility implications need consideration.

## Coverage review

Use [bidirectional reasoning](bidirectional-reasoning.md) at the relevant boundary. One possible view traces outcomes through journeys, surfaces and states to components; the reverse examines how those elements support progress. Move between views as needed rather than treating that decomposition as a mandatory sequence. Find dead ends, duplicate responsibilities, unsupported claims, invisible changes of scope and metrics that reward the wrong behavior.

For each proposed flow, identify what is rendered, what navigation is supported, what behavior is only described, and what remains to validate in a functional prototype. The current static shell cannot establish successful form submission, native device behavior or real service recovery.
