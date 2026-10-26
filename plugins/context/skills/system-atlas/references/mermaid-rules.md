# Mermaid drafting rules

1. Quote every label: `A["text"]`, `G{"text?"}`, `-- "yes" -->`. Unquoted labels break on
   parentheses, colons, slashes and commas, and the break shows up as a blank canvas.
2. Verbs on edges. An edge label says what happens (`"dispatch"`, `"verdict"`, `"changes asked"`),
   never a noun with no action in it.
3. At most 14 nodes per canvas. `atlas_check.py` counts them, best effort, and fails over the
   limit. Split the concept rather than shrink the type.
4. A subgraph means ownership, nothing else. Not grouping by topic, not visual tidiness.
5. Dashed edge `-.->` means dispatch: one party starting another.
6. Thick edge `==>` means result: a verdict, a decision, an outcome travelling back.
7. Show failure paths. Every gate has a no branch and the no branch goes somewhere named.
8. Show human touchpoints. A decision a person makes is its own node, labeled with what they are
   asked.
9. Use `<br/>` for line breaks inside a label. Keep a label under about eight words.
10. Never an `%%{init}%%` directive. The artifact host's native mermaid renderer then fails to
    detect the diagram and prints the source as text. Theming happens in CSS, see
    `mermaid-class-map.md`.
11. State glyphs 🟢 🟡 🔴 ⏳ 🔵 are state only, never decoration.
12. Kinds are told apart by shape and a mono prefix (`skill:`, `cmd:`, `hook:`), never by color.
13. `direction LR` inside a subgraph when the flow inside it reads left to right; otherwise the
    nested layout fights the outer one.
14. Every node and edge label traces to a file. A label you cannot cite is cut, or marked
    intended rather than observed.

## Quick failures to recognise

- Canvas renders the source as text: an init directive, or a syntax error on the first line.
- Black boxes and clipped labels in the viewer: something cloned the SVG instead of moving it.
- A label overflows its box: it is too long, or `--dg-font` drifted from mermaid's default
  metrics. Shorten the label; do not change the font size.
- Edges cross into a mess: too many nodes. Cut to 14 or fewer.
