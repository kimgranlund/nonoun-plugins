# Game of Life — an interactive cellular-automaton studio

Build a browser Conway's Game of Life with an editable grid, playback controls, and a pattern library. Canvas
+ vanilla JS, no build step (or a tiny Vite app).

## What a good version does

- An **editable grid**: click/drag to toggle cells; resize the grid; clear/randomize.
- **Playback**: play/pause/step, an adjustable speed (generations per second), and a generation counter.
- Correct Conway rules with a **toggle for edge behavior** (wrap-around torus vs. dead borders); a population
  readout.
- A **pattern library**: stamp classic patterns (glider, blinker, pulsar, glider gun) onto the grid; save/load
  the current board to localStorage; pan/zoom is a plus.

## Non-goals

- No infinite/hashlife grid in the first cut (a bounded grid is fine); no backend.

## Acceptance signal

The simulation evolves by the correct rules, a glider travels, edge-wrap behaves as toggled, play/step/speed
work, and a saved board round-trips. **Build the rules engine + pattern stamping as pure ES modules**
(`nextGeneration(grid, {wrap}) → grid`, `stampPattern`, `serializeBoard`) a `verify.mjs` drives headlessly to
assert known oscillator periods (blinker=2, pulsar=3), glider displacement after N gens, and the wrap toggle —
rendering stays in the shell.
