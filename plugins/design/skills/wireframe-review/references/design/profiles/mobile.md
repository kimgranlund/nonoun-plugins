# Mobile apps

## Intent and boundary

Support useful work within constrained, interruptible sessions and device-specific contexts. Mobile is a platform overlay: combine it with the project's domain and purpose. Do not assume a small browser viewport proves a native app experience. Verify current target-platform conventions when the task depends on them.

| Surface / flow family | User intent and content responsibilities | Candidate completion | Candidate success signal |
| --- | --- | --- | --- |
| First use / onboarding | Understand value, prerequisites and the minimum needed to begin | Reach a useful first result | Successful activation with understanding |
| Home / resume | Recognize current state and the most relevant continuation | Resume or start a task | Successful resumption without reconstructing context |
| Core task | Complete the main job with appropriate feedback and input effort | Confirm a meaningful result | Accurate completion, effort and recovery |
| Detail / decision | Understand one object, its status and available actions | Act or return with context | Correct decisions and preserved navigation state |
| Capture / creation | Enter or capture information using appropriate device capabilities | Save, submit or queue | Valid output and preserved work on interruption |
| Permission request | Understand why access is needed and the alternative if declined | Grant, defer or decline | Informed choice and continued usefulness |
| Notifications / inbox | Recognize relevance, urgency and available response | Act, defer or configure | Useful response without avoidable interruption |
| Account / preferences | Control identity, settings, privacy and continuity | Verify a change | Correct configuration and low unintended changes |
| Offline / sync / recovery | Understand local versus committed state | Resume, reconcile or retry | Data continuity and safe recovery |

## Content strategy

Prioritize the current task while keeping secondary routes discoverable. Explain permission and authentication requests at the relevant point. Distinguish an input keyboard obscuring content from a genuinely small viewport. Consider safe areas, orientation, text scaling, long translations, touch reach and external interruptions. Gesture alternatives and accessible controls remain necessary even when a swipe path is efficient.

## Decision space

Possible alternatives include a guided sequence for unfamiliar tasks, a resumable workspace for ongoing work, or direct contextual actions for frequent short sessions. Compare navigation by stable destinations, objects or a dominant task when the domain supports it. Progressive disclosure must preserve discoverability and state; “fewer screens” does not automatically mean less effort.

## Measures and guardrails

Consider meaningful activation, accurate task completion, resumed-task completion and recovery from interruption. Define session boundaries carefully. Pair permission acceptance with informed comprehension and usefulness after denial. Notification opens alone do not establish value; examine relevance, interruption and opt-out behavior.

## Review questions

Can the person stop and resume safely? What happens when the keyboard opens, permission is denied, connectivity drops or another app interrupts? Is the result committed or merely local? Can equivalent tasks be completed without a particular gesture?

Prototype scope: render the required states and navigation; explicitly describe unimplemented native permissions, device APIs, persistence and synchronization.

Related: [lifecycle](../capabilities.md#lifecycle-and-re-entry), [conditions](../conditions.md), [product UI](product.md).

Use [experience reasoning lenses](../experience-lenses.md) to connect surface choices with task continuity, state, recovery and coherent flow alternatives.
