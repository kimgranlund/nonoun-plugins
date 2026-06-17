# Marketplace-DX — the citizen + install experience, as a checked property

A plugin doesn't just have to be *good* (the 9-dimension `plugins-holistic` rubric scores that); it has
to be a **good marketplace citizen** — findable in a browse list, scannable at a glance, honest about its
scope, and obvious to start. That experience is **marketplace-DX**.

The MECE audit (`reviews/2026-06-17-dimension-mece-audit.md`) established that marketplace-DX is **not a
new holistic dimension** — its *judgment* lenses are already owned (Steve Y. → marketplace-as-platform /
namespacing; Boris C. → the post-install "would a user leave it enabled" signal; Charity M. →
observability / state survival; David F. → packaging). That ownership is why a marketplace-DX *critic* was
declined as non-distinct. What was **missing** is the layer below taste: the **mechanizable entry-quality
properties** of the marketplace manifest itself, which no gate checked. This reference records the whole
standard and marks the line — *structure is mechanized; taste is not.*

## The mechanized subset — `bin/check-marketplace-dx.py`

Per marketplace entry (the card a user browses), checked in CI:

| Property | Why it's DX | Rule |
| --- | --- | --- |
| **Scannable card** | A browse list shows the `description` as the card. An essay doesn't get read; a 1-sentence pitch does. | `description` present; **FAIL** if ≥ 800 chars, **WARN** if ≥ 500 (the catalog's good cards sit at ~275–400). |
| **Category present** | Browse/filter by category is the first discovery axis. | `category` present + non-empty. **WARN** if outside the recognized set. |
| **Tag hygiene** | Tags are the second discovery axis; a wall of 17 tags is noise, not signal. | `tags` present (≥1); **WARN** if > 12 (tag-spam) or a tag isn't kebab-case. |
| **Entry exists for every plugin dir** | A plugin not in the marketplace is undiscoverable; an entry with no plugin is a dead card. | every catalog plugin ↔ exactly one entry (already cross-checked by `validate_plugin marketplace`; restated here). |

These are *form*, not taste — an over-long card or a tag-wall is a defect regardless of how good the plugin
is, so they gate.

## The judgment subset — owned elsewhere, named here so the standard is whole

These are real marketplace-DX concerns but they are *taste*, so they live with the critic/dimension that
owns them, not in the gate:

- **The first-five-minutes / clear entry point** — does a newly-installed user know where to start (a
  cold-start/orient command, a README quickstart)? Owned by **P1** (fitness/one-sentence job) + **P7**
  (discoverable entry points) + `cold-start-orientation.md`.
- **"Would a user leave it enabled?"** — the post-install standing-value signal. Owned by **Boris C. / P6**.
- **Namespace + granularity etiquette** — install-id correctness (`<plugin>@<marketplace>`), monolith-vs-
  fragment. Owned by **Steve Y. / P3 / P7** and mechanized for collisions by `validate_plugin marketplace`
  (D-13) + `assemble-marketplace.py`.
- **Scope honesty across surfaces** — the marketplace card must restate the *same scope* as the plugin's
  `plugin.json` / README / CHANGELOG (the four-descriptions rule), mechanized by `check-manifest-sync.py`.

## The standard, in one line

A plugin earns its place in the marketplace when its card is **scannable**, its **category + tags** make it
**findable** without noise, its scope is **honest** across surfaces, and a new user can **start in under a
minute**. The first three are gated; the last is judged.
