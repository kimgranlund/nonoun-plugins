# A2UI integration

Read only when the project uses A2UI. This is optional composition guidance; the plugin does not supply a renderer.

Separate the durable composition contract, versioned composition data, and rendered runtime instance. Pin the renderer/catalog adapter and supported component contracts. Evaluate structure, bindings, rendering, interaction, accessibility, and domain behavior separately. A valid A2UI payload is not proof of a working interface. Adding an unsupported component is renderer work; do not invent catalog entries. Reusable composition data and reusable renderer components have different public interfaces.
