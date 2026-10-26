# Anti-patterns

Each one has been paid for at least once.

## Drawing

- Drawing from memory. The labels look right and cite nothing. Run the source-truth check before
  the page is assembled, not after.
- One giant canvas. Past 14 nodes the edges become a hairball and the reader learns nothing.
  Split the concept.
- A file tree pretending to be an atlas. Directories are not machinery; a diagram of folders
  answers no question an actor has.
- A diagram with no failure path. Every gate has a no branch and the no branch is named.
- Nouns on edges. `"data"` says nothing; `"writes the verdict row"` does.
- A subgraph used for tidiness. A subgraph is an ownership claim and will be read as one.
- Telling kinds apart by color. Color is state. Shape plus a mono prefix tells kinds apart.
- Both perspectives collapsed into one section. An outside-in step and an inside-out boundary in
  the same canvas hides exactly the mismatch the atlas exists to find.

## Reporting

- A finding with no evidence path, or with one path used twice.
- One scout's "none found" written down as a rung 2 rule. Absence from the pass that read the
  prose is not absence from the system. Search the checks inventory for the rule's key terms and
  for the file it governs before the rule drops, or the atlas reports a gap the hook already
  covers.
- Intent reported as observation.
- Smoothing over a mismatch by redrawing until both perspectives agree. The mismatch was the
  product.
- An enforcement matrix with rung 4 as one column. Mechanical and judged are reported apart.
- 🟢 on a check whose red nobody has seen.
- A verifier counted as independent without naming its context, model family and seat.
- Findings buried in prose. They are a list, each line naming what would close it.

## Page and publish

- An `%%{init}%%` directive anywhere: the host prints the diagram source as text.
- A literal color, a per-theme token block, or a `prefers-color-scheme` media query. All three
  fight the `color-scheme` switch.
- A web font. The artifact will render without it and the diagram boxes are measured in the
  fallback anyway.
- A cloned SVG in the viewer: black boxes and clipped labels, because mermaid scopes styles by
  the SVG's id.
- Fitting the viewer to the viewBox instead of the rendered size. It overflows the right edge.
- A joined button strip, which forces a square-cornered middle button.
- Publishing a page `atlas_check.py` fails, or publishing without filling the footer commit.
- Rebuilding the template from scratch. Copy `assets/page-template.html` and change the content.
