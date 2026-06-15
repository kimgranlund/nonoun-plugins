# Drum Sequencer — a step-sequencer drum machine

Build a browser step-sequencer drum machine with real audio, no build step (Web Audio API + vanilla JS, or a
tiny Vite app).

## What a good version does

- A **step grid** (e.g. 16 steps × several instruments: kick, snare, hat, clap) you toggle on/off by clicking.
- A **Web Audio** transport that plays the pattern in a loop with **sample-accurate scheduling** (look-ahead
  scheduler, not setInterval-per-step) so timing doesn't drift; play/stop; an adjustable **tempo (BPM)** and
  swing.
- Synthesized or short built-in sounds per instrument (no external samples needed); a per-track mute + volume.
- **Save/load patterns** to localStorage; a visible playhead stepping across the grid in time.

## Non-goals

- No recording/export to audio file in the first cut; no MIDI.
- No backend.

## Acceptance signal

Toggling steps and pressing play produces an audible, in-time loop; changing BPM changes the tempo without
drift; a pattern round-trips through a reload. **Build the scheduler timing math + the pattern model as pure ES
modules** (`stepTimes(bpm, steps, swing) → number[]`, `togglePattern` / `serializePattern`) a `verify.mjs`
checks headlessly (timing math, swing offsets, pattern round-trip) — the Web Audio playback stays in the shell.
