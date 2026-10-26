# Product UI

## Intent

Help people create, understand and manage domain objects through repeatable work. Identify objects, their states, owners, relationships and permissible actions before choosing an application shell. Separate end-user tasks from administration and governance when their intents differ.

| Surface / flow family | User intent and content responsibilities | Candidate completion | Candidate success signal |
| --- | --- | --- | --- |
| Workspace home | Understand relevant work, scope and continuation | Start or resume a useful task | Successful orientation and resumption |
| List / collection | Find, assess and organize objects at realistic scale | Select, compare or act on a suitable set | Retrieval accuracy and safe bulk scope |
| Detail / record | Understand an object's state, history and relationships | Make an informed next action | Correct interpretation and action |
| Editor / creation | Produce a valid object while retaining context and work | Save, publish or hand off | Valid completion, quality and correction effort |
| Workflow / review | Understand sequence, dependencies and who acts next | Advance or resolve a blocked step | Completed handoff and reduced rework |
| Search / command | Reach known work or invoke a suitable action | Find or execute with scope clear | Successful retrieval/action without wrong-scope changes |
| Activity / collaboration | Understand relevant change, responsibility and feedback | Respond or coordinate | Shared understanding and resolved work |
| Administration / access | Configure people, roles, policies and workspace boundaries | Verify intended access/configuration | Accurate changes and auditability |
| Billing / preferences | Control entitlements, commitments and personal behavior | Verify the chosen setting or plan | Correct understanding and low surprise |

## Content strategy

Use the domain's object vocabulary consistently. Explain state, scope and consequences where they affect decisions. Distinguish draft, saved, submitted, approved and published only when those states actually exist. Provide context for bulk actions and inherited settings. Settings should describe the resulting behavior rather than expose internal variable names.

## Decision space

Explore object-first workspaces when entities organize the work, task-first queues when throughput matters, or guided flows when prerequisites and consequences need attention. Editing alternatives might integrate preview, separate focused stages or start from reusable templates. Match information density to frequency and expertise, then test first-use comprehension and repeated-use efficiency separately.

## Measures and guardrails

Candidate measures include valid task completion, work quality, rework, recovery effort, successful handoffs and appropriate feature adoption. Pair speed with correctness and reversibility. Activity counts may reward unnecessary steps. Separate organization-wide outcomes from an individual's behavior and avoid proposing intrusive monitoring as a default.

## Review questions

Does every action have clear object and workspace scope? What happens to unfinished edits during navigation or concurrent changes? Can people understand validation and recover? Are administrative powers and end-user capabilities visibly different?

Related: [operations](../capabilities.md#operational-and-administrative-systems), [collaboration](../capabilities.md#collaboration-and-community), [AI assistance](../capabilities.md#ai-assisted-experiences).

Use [experience reasoning lenses](../experience-lenses.md) to connect surface choices with task continuity, state, recovery and coherent flow alternatives.

## Default application navigation

Use a sidebar with a context-switching head, search in the body, links and accordion groups with optional dividers, and a user-menu footer. Align the main workspace beside it. Preserve active location, return context and accessible labels. Vary grouping and disclosure according to work frequency and hierarchy. The product demo renders three examples. Registration and other focused flows may omit workspace navigation in a real application when the task requires it; the demo retains it for cross-specimen navigation. Reference: [shadcn sidebar anatomy](https://ui.shadcn.com/docs/components/base/sidebar).
