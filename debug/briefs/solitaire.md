# Solitaire — a playable browser card game

Build a polished, playable **Klondike solitaire** game that runs in the browser with no build step (static
HTML + CSS + vanilla JS, or a tiny Vite app — the factory decides). It is the worked example for proving the
dark factory can take a normal product brief and ship a real app.

## What a good version does

- A standard 52-card Klondike deal: seven tableau piles, four foundations, a stock + waste, draw-one.
- **Intuitive drag-and-drop**: pick up a card (or a valid descending alternating-colour run) and drop it on a
  legal tableau or foundation target; illegal drops snap back. Works with mouse and touch.
- **Score keeping**: a running score (standard Klondike scoring — foundation moves up, waste recycles down),
  a move counter, and an elapsed timer; a win is detected when all four foundations are complete.
- **Leaderboards**: persist best scores/times locally (localStorage) and show a top-10 leaderboard; entries
  survive a reload; a new win is inserted in rank order.
- Clean, legible UI: a new-game button, an undo, and a visible score/timer/moves header.

## What a good version does NOT do (non-goals)

- No backend, accounts, or network leaderboard (local persistence only).
- No multiplayer, no alternate game modes (Spider/FreeCell) in this first cut.
- No card-art licensing — use CSS-drawn or unicode suit glyphs.

## Acceptance signal

The produced app **loads and plays**: a human can deal, drag a legal card to a foundation, see the score and
move counter change, win a trivially-solvable deal, and see that win recorded in the top-10 leaderboard after a
reload. If there is a build step it must `npm install && npm run build` clean; a no-build version must open
`index.html` and run.
