# Content and task pattern registry

Read this when choosing or generating page modules and task surfaces. The machine-readable [registry](registry.json) contains intent, content shape, selection and rejection conditions, required content, variant directions, tradeoffs, evaluation questions and alternative patterns. Its top-level principles distinguish marketing, content publishing, product work and analytical/agent experiences.

## Choose by fit

Start with what the reader or user must understand or accomplish at this point. Examine the content relationship: sequence, dependency, comparable alternatives, one object, a set of actionable objects, evidence, or a consequential decision. Consider cardinality, user expertise, frequency, device constraints and the cost of error. Prefer the pattern that represents that relationship with the least unnecessary interpretation.

“Best” is conditional on those facts. A matrix often fits comparison, a queue actionable work and a workbench creation; none is universally optimal. Treat the choice as a testable hypothesis rather than an aesthetic preference. Adapt the pattern or propose another when the registry does not fit. No mandatory rubric score, fixed pass count or transcript of model reasoning is required.

Do not fill a pattern by inventing proof, statistics, quotations or capabilities. If its required content is absent, choose a simpler representation or make the gap explicit. `demoRenderer` means the suite includes a rendered marketing specimen for that family; false means selection guidance, not an unimplemented promise of an automatic renderer. Variant directions describe possibilities, not an obligation to render all of them.

## Website rhythm and fatigue

A marketing page develops an argument: establish relevance, explain a mechanism, make evidence assessable, resolve fit and offer an appropriate commitment. These responsibilities need not follow one universal order. Content for an expert evaluator may begin with the result or constraint that changes their decision.

Review the sequence at two scales. Within a module, inspect the relationship between content and its presentation. Across the page, look for duplicate meaning, repeated silhouettes, uniformly high density, repeated reading effort and conversion asks that arrive without new grounds for action.

Use variety to signal a meaningful change. An editorial interlude can mark the central question; a sequence can explain the mechanism; a working specimen can make the output tangible; an evidence story can establish limits; a compact fit band can prepare the next decision. Moving the same picture from left to right is rarely a new content strategy.

Avoid a mechanical alternation or diversity quota. Repetition can support comparison, familiarity and navigation. Break a pattern when it helps the reader notice a new responsibility or renew attention, while keeping typography, spacing, interaction and state semantics coherent. Fatigue reduction is a design hypothesis to evaluate, not a promised conversion gain.

Place an action after the reader has gained grounds for taking it. A mid-page route to inspect an example and an end-of-page pilot request serve different levels of commitment. Repeating the same CTA after every module adds pressure and visual noise without necessarily helping.

## Product consistency

Repeated work benefits from stable object structure, control placement, state vocabulary and recovery paths. Do not rotate templates for novelty. Change the arrangement when the task or information relationship changes: queue to record, record to editor, editor to review. Within equivalent tasks, consistency supports transfer of learning.

A dashboard should preserve measure definitions and scope. An agent console should distinguish judgment, policy, authority and execution. A content publication can vary discovery pages while retaining consistent article and reference anatomy. An experience can combine these modes; choose principles locally rather than label the entire project once.

## Width contract

Content section surfaces fill the available wrapper width, including mobile. Internal grids divide that width intentionally. Text measure is an explicit inner-block decision through `.prose__root`; it must not accidentally cap a section, reading layout or briefing surface. Insets and gaps continue to use foundation roles. Width is independent of typography and of the logical preview viewport.

## Example implementation

`assets/demos/marketing-patterns.mjs` assigns patterns explicitly by each chapter’s content responsibility. It resolves names, purpose and tradeoffs from the registry so the review shell exposes why each alternative was chosen. Its assignments are authored examples, not a universal algorithm or positional rotation rule.

Build the demo suite to inspect `pattern-registry.html` and `pattern-registry.json` alongside the revised marketing pages. The marketing revision is advanced and the builder preserves its preceding HTML and manifest under `revisions/marketing/`.

## Reason before selecting

For narrative experiences, use [page and module reasoning](../narrative-reasoning.md). The registry exposes the same prompts under `reasoningGuidance`: page purpose and story shape module responsibilities; module evidence and representation can reshape the page. Scale includes emphasis, density, depth and interaction as well as physical footprint. Capture the consequential conclusions in existing intent and variant rationale fields.

Full-width sections may contain a centered `.content__root` wrapper (`--ui-content-width`) or `.prose__root` block (`--ui-prose-width`). Max-width and automatic inline margins belong to these inner containers, not the section surface. Desktop previews grow beyond their 1200px baseline to fill a wider wrapper; narrower wrappers scale the baseline down. Mobile retains its 390px logical viewport scaled to the wrapper.

## Navigation

Read the separate [navigation registry](navigation.md) for experience shells, destination hierarchy, local orientation and task movement. It includes 17 patterns and four family defaults with meaningful variants.
