# Example: Generative UI

This example is illustrative only. The skill itself is domain-independent.

## Frame

Intent: generated dashboard should satisfy semantic request, component contracts, responsive layout, interaction, and accessibility requirements.

## Baseline verification

A full run identifies:

- horizontal overflow at medium widths;
- unsupported component variant;
- keyboard navigation failure.

Triage creates three episodes rather than restarting the complete benchmark after each fix.

## Episode: layout overflow

Objective: eliminate overflow at the affected width range without changing semantic component selection.

Budget: four attempts, local layout/style scope, V0–V2 verification.

Attempts may test container constraints, responsive tokens, and layout composition. When local verification passes, the episode stops RESOLVED. The full visual/accessibility/semantic suite waits until integration.

## Outer regression

After validated episode changes are integrated:

1. run representative generated dashboard scenarios;
2. run full regression;
3. perform outside-in browser/task evaluation;
4. produce learning records for causal failures;
5. emit the cycle report and stop.
