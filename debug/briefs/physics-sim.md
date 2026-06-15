# Physics Simulation App — a sandbox of simulations

Build a browser app that runs several interactive 2D physics simulations the user can pick between, tweak, and
watch. Canvas + vanilla JS, no build step (or a tiny Vite app).

## What a good version does

- A menu of **at least three** simulations sharing one engine: **gravity/orbits** (n-body), a **cloth/spring**
  mesh, and a **particle fluid or bouncing-balls** box with collisions + restitution.
- Each sim has live **parameter controls** (gravity, damping, restitution, particle count, timestep) that
  update the running sim; play/pause/step/reset.
- A **fixed-timestep integrator** (semi-implicit Euler or Verlet) so the sim is stable + reproducible, decoupled
  from the render framerate.
- Clear, smooth rendering with a small stats readout (FPS, body count, total energy).

## Non-goals

- No 3D, no GPU compute in the first cut.
- No backend; everything runs client-side.

## Acceptance signal

Each sim runs stably and responds to its controls; pausing freezes it, stepping advances one tick, reset
restores it. **Build the integrator + each sim's step function as pure ES modules** (`step(state, params, dt) →
state`, with energy/invariant helpers) a `verify.mjs` drives headlessly to assert determinism (same seed + dt →
same trajectory), stability (no NaN blow-ups), and a conserved quantity within tolerance — rendering is the shell.
