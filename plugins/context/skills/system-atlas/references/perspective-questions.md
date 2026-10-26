# Perspective questions

Use these to decide which perspective a concept belongs to, and to interrogate it once you have
chosen. A concept that answers questions from both lists is two concepts.

## Outside-in: an actor with a goal

Name the actor first. A human operator, a calling service, a CI run, a new contributor on day
one. Then:

- What do they touch? The exact door: a command, an endpoint, a file they edit, a button.
- What do they wait on? Name the thing and who is holding it. Waiting with no named holder is a
  finding.
- What do they decide? Every branch a human owns is a node, not an edge label.
- What can go wrong for them, and how do they learn it went wrong? A failure with no path back
  to the actor is a finding.
- Where does the system refuse them, and does the refusal say why?
- What do they never see that they should? That is the cross-check against the inside-out pass.

## Inside-out: a component and its state

Name the component and the state it owns. Then:

- Who owns it? One owner. Two owners is a finding, not a subgraph.
- Which states exist, and which transitions are legal? Name the transition that is never allowed.
- What crosses the boundary in, and what crosses out? Name the format and the carrier.
- Who writes this record and who reads it? A store with no writer or no reader is a finding.
- What is never allowed, and what enforces that? Carry it to the enforcement ladder.
- Which of these boundaries does an actor ever see? That is the cross-check back.

## The cross-check

Run it after both passes are drafted, before the page is assembled.

1. Take every outside-in step. Point it at an inside-out node. A step with no node means the
   drawing is describing something the components do not do.
2. Take every inside-out boundary. Point it at an outside-in step or an actor-visible signal. A
   boundary nobody sees means a failure will surface as silence.
3. Write each mismatch as a finding with both evidence paths. Do not fix the diagrams to hide it.
