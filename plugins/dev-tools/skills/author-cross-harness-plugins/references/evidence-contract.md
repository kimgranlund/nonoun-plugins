# Cross-harness evidence contract

Use this contract before claiming that a plugin works in Claude Code and Codex.
Structural validation, a plausible answer, and a generated artifact establish
different facts. Record each stage independently:

1. **Packaged:** the candidate artifact contains the intended surface.
2. **Activated:** the host enabled that exact candidate.
3. **Advertised:** the host exposed the route to the session.
4. **Selected:** the route was chosen for the prompt.
5. **Loaded:** the intended body and required resources were read.
6. **Executed:** the workflow ran with its required tools.
7. **Completed:** the observable result satisfies the contract.
8. **Cleaned up:** owned temporary state was removed without touching peers.

Do not merge stages. Registration is not selection; answer quality is not loading;
an artifact diff does not prove which commands or checks ran. Requested model or
configuration is not observed identity. Use `unverified` when the host exposes no
decisive event.

For main-session instruction wiring, distinguish a valid config read from an
effective startup prompt. Retain the actual prompt/input event or a host diagnostic
that shows the instruction text was injected, and repeat after removal to show it
is absent. A successful agent read of `config.toml`, or a plausible answer, proves
neither injection nor removal. Diagnostic commands such as `codex debug
prompt-input` are version and capability sensitive examples: check availability and
what the target version actually emits. If the effective prompt is not observable,
mark startup injection or removal `unverified`.

## Freeze the candidate

Before each row, record the full commit or artifact digest, wrapper/package version,
configuration identities, working directory, host version, requested model and
available tools. A worktree based on committed history cannot test uncommitted
changes in a primary checkout. If pre-commit evaluation is necessary, copy the
complete candidate to an isolated directory and hash it; do not combine a live
adapter from one checkout with a canonical body from another.

Worktrees isolate Git state and ordinary writes. They are not filesystem sandboxes
and do not prove that discovery, global configuration or caches came from the
worktree. Use fresh top-level processes for acceptance. Child-agent runs are useful
scenario exercises, but their final reports are self-report unless actual call
events are retained.

## Preflight and first launch

Confirm before launch that the session exposes the route-selection mechanism being
tested, candidate resources are readable, required execution tools are available,
and known competing routes are inventoried. A routing-only trial that cannot run a
mandatory helper must say so and cannot establish workflow completion.

A genuinely first session cannot provide prior host-advertisement evidence. Permit
the launch with advertisement explicitly unverified, then classify it from retained
post-launch evidence. Never relabel filesystem inventory or a planned route as host
advertisement. An absent-candidate baseline names the route whose absence will be
checked; an empty unnamed inventory proves nothing.

## Behavioral rows

Use one fresh top-level process per row:

- should-trigger;
- nearest named near miss;
- explicit invocation through the host interface actually being claimed;
- observable completion;
- absent-candidate baseline when discovery behavior matters.

Freeze prompts and expectations outside the tested distribution. Literal
`/skill-name` text passed to a child agent tests that child's interpretation, not
interactive slash-command dispatch. Preserve the first outcome and allow at most
one diagnosed repeat with changed inputs recorded.

## Retention and receipts

Retain raw host events, stdout/stderr, exit status, configuration and artifact
hashes, host/model identity, termination reason and available usage telemetry.
Summaries supplement those files and never replace them. A passed stage cites the
retained evidence that establishes it. Historical receipts that did not represent
a newer stage migrate that stage as `unverified` rather than inventing a result.

Keep temporary runs in exclusively created directories with an ownership manifest.
Cleanup verifies file kind and identity, preserves changed or unlisted files, and
does not infer ownership from a path or signal unrelated processes. Report retained
worktrees and branches for an explicit adopt-or-discard decision.

## Claim language

Use the narrowest supported conclusion:

- “structure validates” for schema/resource checks;
- “artifact confirmed” for filesystem inspection;
- “reported by child agent” for unretained delegated call sequences;
- “host-observed” only for retained host events;
- “cross-host verified” only when the relevant stages pass for frozen candidates
  in both hosts.

Configured CI, an earlier session, or a successful run under a different revision
is not current hosted evidence.
