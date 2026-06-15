# Breakout — a brick-breaking arcade game

Build a polished Breakout/Arkanoid clone in the browser, no build step (canvas + vanilla JS, or a tiny Vite app).

## What a good version does

- A paddle (mouse/keyboard/touch), a ball with **proper reflection physics** (angle off the paddle depends on
  where it hits), and a grid of destructible bricks.
- **Collision detection** ball↔walls / paddle / bricks; bricks break and the ball deflects correctly; the ball
  speeds up over time.
- **Lives, score, levels** — clearing all bricks advances to the next layout; losing the ball costs a life;
  game over + restart. A few power-ups (wider paddle, multi-ball) are a plus.
- Smooth requestAnimationFrame animation + a clean HUD (score, lives, level).

## Non-goals

- No backend leaderboard; local high score only.
- No asset pipeline — canvas-drawn shapes.

## Acceptance signal

A human can play: the ball reflects believably, bricks break and score, a level clears and advances, a lost
ball costs a life. **Build the ball/paddle/brick collision + the game-state reducer as pure ES modules**
(`step(state, input, dt) → state`, `reflect(ball, surface)`) a `verify.mjs` drives headlessly to assert
reflection correctness, brick-collision resolution, and level/lives transitions — rendering stays in the shell.
