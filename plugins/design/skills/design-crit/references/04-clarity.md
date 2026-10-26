# Stage 4 — Braun-inspired control grammar and controlled-language review

## Own

Honest operation: consistent distinctions among actions, selections, navigation, status and unavailable controls. Language should make the established model understandable, not compensate for a broken model. This lens translates functional product-design principles to software; it is not a demand for decorative austerity.

## Ask after domain, sequence and structure are settled

- Does each control reveal what it will do and what object/scope it affects?
- Are the same tasks, entities, states and results named consistently?
- Do different operations accidentally share one generic label, such as Retry, Done or Clear?
- Is the language familiar to these users, concise without becoming cryptic, and free of unnecessary implementation jargon?
- Do feedback and errors distinguish pending, complete, partial, failed and uncertain outcomes when relevant?
- Does an error offer an available remedy, rather than blame or an action that cannot address its cause?
- Can hierarchy distinguish the primary commitment, ordinary actions/menus, selected navigation, status and disability without relying on color alone?

## Evaluate

| Criterion | Supported when |
| --- | --- |
| Vocabulary consistency | One preferred term per concept; differences in wording reflect real semantic differences. |
| Action honesty | Labels name the operation and enough scope to predict the consequence; controls do not imply unsupported behavior. |
| State/result clarity | Feedback describes what happened and what remains; uncertainty is not mislabeled failure or success. |
| Recovery usefulness | Cause, retained work and viable next action are clear; recovery does not introduce an unacknowledged side effect. |
| Control grammar | Equivalent controls share treatment; destructive, selected, disabled and primary states are distinguishable. |

Produce a small controlled-language table for changed concepts: concept → preferred term → avoid/alias → context. Distinguish task names, action verbs, in-progress states, completed results and recovery actions. Follow domain vocabulary from stage 1 and existing product/localization guidance; do not invent a universal dictionary or claim uncited copy rules are standards.

Examples are semantic, not mandatory strings: regenerating an answer is not resuming it; checking uncertain delivery is not resending; selecting files is not necessarily uploading or attaching them. If the intended operation is unknown, route it upstream rather than guessing a better-sounding label.

Keep user copy separate from authoring annotations. Accessible names should agree with visible labels and add needed context; never hide a confusing visible action behind an explanatory accessible name. Precise technical measurements may belong in interaction feedback or accessibility values rather than permanent everyday chrome.

## Exit

Return specific before/after copy and control-treatment changes with reasons. Reopen upstream design only with evidence. Do not claim the interface is accessible or usable solely because its words and visual hierarchy are consistent.

Seed inside-out validation with concrete action → state/result → recovery traces. Name what actually changes, what remains provisional and what happens next. If the trace does not support the visible promise, identify the responsible upstream layer before proposing a label change.
