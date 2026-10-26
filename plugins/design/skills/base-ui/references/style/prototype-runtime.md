# UI runtime and host adapters

Read [the bounded API](../runtime-api.json) or `node scripts/component-context.mjs --runtime`. The historical filename is retained for local context links. Base UI owns createUIRuntime, mount, reducer/render/bind cleanup and focusWorkflowStep. It has no review unit or variant identity.

## User activation and form defaults

Native form buttons declare type=button unless submitting. Call privileged browser operations from the real activation handler. After committed Next/Back rendering, focusWorkflowStep targets the visible destination heading. Do not steal focus during initial mounting or typing.

## Revision DOM and runtime fidelity

Preserve source hooks and the controller registration strategy of the consuming host. Rendering and validation changes require affected path checks. A valid script or token reference does not prove user outcomes.

## Review integration

wireframe-review is an optional consumer. Its own prototype-runtime.md and component-context.mjs --runtime document registerPrototype and review identity. Do not use those APIs in a standalone base-ui artifact.
