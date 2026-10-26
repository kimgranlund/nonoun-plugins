# Minimal host

A stand-in for a real project: the smallest UI system a jig can be pointed at. The jig one folder up (`../jig.html`) tunes it and never edits it.

- `tokens.css`: five constants, and four values derived from them.
- `components.css`: a card, a text field and a button. Every size reads a token.
- `index.html`: the one screen the host ships.

## Rules

The host states two rules. A jig reports them under `checks.contract`.

1. A control is at least 24px tall.
2. The radius is at most half the control height.
