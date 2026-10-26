# Evidence rules

An atlas is a claim about a system. Every claim carries its receipts or it does not ship.

## Two paths per claim

Each concept, each inventory item, each finding needs two independent evidence paths. Two paths
that quote the same sentence in two places are one path. Independence means the second path
would still say the same thing if the first were deleted.

Good pairs:

- The rule as written (CLAUDE.md) and the hook that refuses the violation (`githooks/pre-commit`).
- The agent's frontmatter (`agents/verifier.md`) and a dispatch of it in another file.
- The command's definition (`scripts/adapter.py`) and a caller that runs it.

Not a pair:

- A README sentence and the same sentence copied into a skill.
- A file existing and that same file being named in a list of files.

## Intended versus observed

Mark every claim as one of two things and never blur them.

- Intended: the files say this is how it works. Cite the file.
- Observed: it was run, or the artifact of a run was read. Cite the command and the output, or
  the record and its path.

A diagram drawn entirely from intent is legitimate, as long as the page says so. The one thing
that is not allowed is presenting intent as observation. The first atlas was drawn partly from
memory, which is neither, and that is the failure the source-truth check exists to stop.

Where intended and observed disagree, that gap is the finding, and both sides get a path.

## The source-truth check, mechanically

Before assembling the page, list every node label and every edge label from every diagram. For
each one, write the file it came from. Then:

- A label with a file: keep it.
- A label with no file but a plausible source: go find the file, or cut the label.
- A label with no file and no source: cut it. Do not soften it into vaguer wording.
- A label that is true of intent but not of the running system: keep it and mark the section's
  lede as intended.

## Citing a commit

The footer names the commit the atlas was drawn from, and the staleness rule reads off it: the
atlas is stale once any cited path changes past that sha. Use a real sha, never a branch name
alone. `atlas_check.py` fails a footer with no sha in it.
