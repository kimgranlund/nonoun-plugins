# 2D Car Game — a top-down arcade racer

Build a playable top-down 2D driving game that runs in the browser, no build step (canvas + vanilla JS, or a
tiny Vite app). Drive a car around a track, take laps against the clock, don't spin out.

## What a good version does

- A car with **real-ish 2D vehicle physics**: acceleration, braking, steering that scales with speed, grip vs.
  drift, momentum — keyboard (arrows/WASD) and ideally touch.
- A track with walls/boundaries (collision that stops or bounces the car), a start/finish line, and **lap +
  best-lap timing**.
- A HUD: speed, current lap time, best lap, lap count; a clean restart.
- Smooth animation (requestAnimationFrame), camera follows the car, the track scrolls.

## Non-goals

- No multiplayer, no AI opponents in the first cut.
- No asset pipeline — CSS/canvas-drawn car + track.

## Acceptance signal

A human can drive, the car obeys momentum (can't turn on a dime at speed), collisions are handled, a lap is
timed and the best lap records. **Build the vehicle physics + lap timing as pure ES modules** (`step(state,
input, dt) → state`, `lapTimer`) a `verify.mjs` can drive headlessly with synthetic inputs and assert
determinism, momentum, and lap detection — rendering stays in the shell.
