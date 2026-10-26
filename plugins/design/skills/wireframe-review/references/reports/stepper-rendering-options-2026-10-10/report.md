# Stepper rendering options

CSS owns explicit orientation and label placement without changing progress semantics or form behavior. The maintained specimen exposes native Orientation and Label placement selects; they only update presentation attributes.

| Orientation | Default | Alternative | Connector |
| --- | --- | --- | --- |
| Horizontal | Centered labels below dots; equal tracks with space-around distribution | Inline labels right of dots | Center: dot to dot. Inline: after text to next dot. |
| Vertical | Inline labels right of the marker rail | Centered labels below dots, centered in the container | Inline: marker rail. Center: inter-item gaps, clear of labels. |

Use data-step-orientation=horizontal|vertical on the adaptive ordered list; omit or use adaptive to retain the 36rem container switch. Use data-step-label-position=inline|center; omit for orientation defaults. Geometry continues to resolve frame/icon/radius and gap from local roles. No step-jump behavior was added.

Verification: 48 authored layout contexts across Chromium/Firefox/WebKit, narrow/wide and light/dark cover all four combinations, long labels, connector endpoints, value retention and current state. Zero-width connector faults are rejected with the same geometry predicates. Twelve adaptive state/focus/Save contexts and controller remount/isolation/cleanup pass. The bounded-context gate initially rejected the enlarged lookup; compact contract wording restores stepper output to 11,925 bytes under the unchanged 12,000-byte guard. All 24 lookups and seven controls pass. Source-derived sheets pass their existing 20 responsive wiring contexts; exact final source hash parity and published rendering controls are recorded separately.

Prior evidence, accepted limitations, original work/history inputs, generation pipeline and peer-owned live components.html remain unchanged. Actual AT, installed Safari and physical touch remain outside these checks. No fresh generation evaluation or holdout was run. Detailed explanations live in workflow-patterns.md; rendering fields in the family contract remain compact.
