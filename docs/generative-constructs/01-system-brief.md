# System brief

Status: proposed v0.1. Related: [model](02-construct-model.md), [prototype](06-prototype-and-validation.md).


> Shipped status: the Progressive Context skill implements a smaller subset of this proposal under different words. This document's terms (construct, revision, instance) map to the skill's capability, contract and assessment as listed in the [vocabulary table](README.md#vocabulary-proposal-and-shipped-skill). The skill specification and the shipped skill record later refinements; reconcile any difference before implementing from this document.

## Purpose

Build a generative system that accumulates usable capabilities as it produces artifacts. Each construct carries intent, domain meaning, a public contract, a realization, and evidence. An agent discovers existing constructs, reads relevant context, composes a new construct, evaluates it, and qualifies a revision for subsequent reuse.

The intended benefit is less repeated interpretation and reconstruction in later tasks, while retaining the ability to inspect and revise the basis for reuse.

## Problem

A generated result often loses the reasoning needed to use it again: its scope, assumptions, dependencies, and evidence remain in a conversation. A library of outputs alone does not tell a later agent whether something fits a new purpose. A library of intentions alone does not tell it what works.

The system keeps intended behavior and observed behavior separately addressable, linked through evaluation criteria. It must make missing evidence visible rather than treating documentation as proof.

## Research hypothesis

Compared with ordinary artifact storage or stage-scoped context alone, storing qualified, discoverable constructs will improve successful reuse and reduce human correction effort on related tasks without unacceptable context or maintenance costs.

This is a testable hypothesis. No quality or efficiency gain is assumed. [The prototype brief](06-prototype-and-validation.md) defines the first test.

## Relationship to ICM

ICM organizes agent work using folder structure, stage contracts, and scoped loading of reference and working material. This proposal retains scoped navigation and inspectable work while adding persistent construct identity, revision-specific qualification, and recursive composition. A browser implementation represents those concepts through records and APIs. It is an adaptation of the architecture, not a literal filesystem implementation. [Source: ICM paper](https://arxiv.org/html/2603.16021v2).

## Intended users and jobs

| User | Job |
| --- | --- |
| Requester | Express an outcome, inspect a result, correct assumptions, and decide whether it fits the intended use |
| Builder, human or agent | Discover capabilities, inspect contracts, compose and revise a realization |
| Evaluator | Assess a specific revision using explicit criteria and record findings |
| Maintainer | Manage shared definitions, dependencies, published releases, and obsolete evidence |

One person can occupy several roles. Role separation is about responsibility and evidence, not a requirement for multiple agents or people.

## Worked example

Request: “Create a workspace for reviewing overdue invoices and preparing follow-up.”

The system discovers a table, customer summary, and action panel. It resolves the meaning of overdue and the supported input fields, creates a workspace construct, and renders an A2UI realization. A fixture exposes a defect: a cancelled invoice appears as overdue. The realization is corrected and reevaluated. The accepted workspace is then tested with another supported dataset and published with a reusable input and action contract.

A later task asks for the same workflow grouped by customer. A fresh agent starts from the published construct, creates a derived construct, and evaluates the new composition.

## Scope

The conceptual model supports different artifact types. The first implementation supports A2UI compositions in a browser-based JS harness, with synthetic invoice data, a small seeded library, durable construct records, and local interactions.

The prototype excludes live financial integrations, outbound messages, arbitrary generated code execution, concurrent editing, automatic renderer-component authoring, and an unrestricted marketplace. These are scope boundaries for a measurable first experiment.

## Design principles

1. **Meaning precedes composition.** Resolve relevant domain definitions and outcome criteria before choosing the interface.
2. **Claims retain their evidence.** Status always points to the revision and conditions assessed.
3. **Context follows the operation.** Discovery, use, modification, and evaluation disclose different resources.
4. **Composition creates new obligations.** Valid parts do not establish the fitness of the whole.
5. **Changes remain inspectable.** Preserve prior revisions, observations, and transition decisions.
6. **Reuse has boundaries.** Contracts expose required inputs, supported actions, limitations, and dependencies.

## Success and failure

Success means a fresh agent can use a qualified construct for a new supported scenario without hidden access to its creation conversation, and the resulting outcome satisfies the new criteria.

Failure includes a polished UI with incorrect domain behavior, stale evidence presented as current, weakened criteria presented as progress, or a library whose documentation costs exceed the reuse benefit.

## Open questions

- How broad should an applicability claim become before several reuse exercises are required?
- Which contextual decisions generalize enough to become shared ontology or reusable guidance?
- How much qualification effort is appropriate for different consequence levels?

The initial answers are deliberately narrow and specified in the lifecycle and prototype documents.
