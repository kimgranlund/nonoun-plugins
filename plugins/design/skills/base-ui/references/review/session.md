# Execute a review session

Use this workbench after a runnable draft exists. It supplies the repeated browser matrix and evidence bookkeeping; you supply application state transitions and actual visual judgments. Start capture before spending the review budget hand-writing measurement scripts or JSON. Keep app interaction assertions in your own checks.

Create a short `review-plan.mjs` beside the app:

```js
export default {
 task: 'Complete the primary editing task', reviewer: 'author',
 retrieved: ['actions','fields','disclosure'], // families actually retrieved
 taskAccess: {taskSelector:'#editor',maxScreens:1,rationale:'Editing is the primary task'},
 states: [
  {id:'initial',description:'Initial editor'},
  {id:'expanded',description:'Evidence disclosure expanded',
   setup: async page => { await page.locator('#evidence > summary').click(); }},
  {id:'validation',description:'Required title error',
   setup: async page => {
    await page.locator('#title').fill('');
    await page.locator('[data-action="save"]').click();
   }}
 ]
};
```

Replace the illustrative selectors, budget and states with real app behavior. Include relevant empty, changed selection/filter, expanded, error, stale, focus or overlay states. A scenario may override `taskAccess` and `boundarySelectors`. For arrival checks set `requireFocus:true` and provide `arrive: async page => { /* actual focus/jump action */ }` on the scenario. `setup` prepares the dynamic state; `arrive` runs after final text scaling and layout settlement, so the jump uses the actual doubled-text geometry. Setup receives `(page,{width,scheme,textScale})` and starts from a fresh offline page for each combination. The workbench scales before setup and idempotently after it to include new nodes, then settles fonts and the current finite-animation set (re-sampled until two quiet frames, with a bounded timeout), performs optional arrival and measures. It captures320/390/768/1440px × light/dark × normal/doubled computed text for **each** scenario; no hand-written matrix needed. `widths` can expand the matrix; all four baseline widths are required. Schemes are forced for paint; test application theme switching separately. Full-page screenshots establish composition; the generated detail packets provide readable original-pixel windows for detail judgments.

```sh
python3 scripts/run.py review-session.mjs capture APP.html PLAYWRIGHT_PATH review-plan.mjs NEW_EVIDENCE_DIR CHROME_PATH
```

The output directory must be new. It contains an artifact-bound `review.json`, every captured PNG and measurement JSON. Setup errors remain visible as missing captures, never substituted with an initial screenshot. No rubric is marked passed. Capture is measurement collection, not a design verdict. For an edited draft build to a new name (for example `app-v2.html`) and capture into a new directory: this preserves the draft and its `.review-status.json`, before evidence and prior judgments without orphan-sidecar rebuild errors.

The full machine matrix is not the manual inspection obligation. The generated risk-based visual plan selects320px/light/normal and1440px/dark/doubled for every scenario, plus390px/dark/normal and768px/light/doubled for the first scenario. It adds a representative capture of each distinct machine finding per scenario. Every machine row is still preserved and checked; any machine failure prevents acceptance. Manual conclusions apply only to the selected sample, not all combinations. Missing required samples keep the review incomplete.

Use the compact next-topic packet; it includes rubric questions, findings and absolute image paths, four required captures per page:

```sh
python3 scripts/run.py review-session.mjs packet NEW_EVIDENCE_DIR/review.json
python3 scripts/run.py review-session.mjs packet NEW_EVIDENCE_DIR/review.json layout 2
```

Open each required full image for composition, then follow its `detail.command` through the launcher. The default `sample` returns at most four lossless PNG windows, each at most960×800 physical pixels: the top, focused control, primary task and representative geometry finding, then the bottom if space remains. Paths use content hashes, so repeated unchanged windows share files and observations within this session. Capture records anchor locations after state setup/scaling/arrival; legacy sessions without anchors provide page-edge samples. The packet identifies exact coordinates and unprovided tile count. Open the tiles at original size (for example `view_image` with `detail:"original"`); tool-resized full images alone cannot establish legibility.

```sh
python3 scripts/run.py review-session.mjs detail NEW_EVIDENCE_DIR/review.json initial-320-light-1 PLAYWRIGHT_PATH sample CHROME_PATH
```

This is **overview plus targeted detail sampling**, not exhaustive pixel coverage. Record this limitation in observations, inspect extra regions relevant to a finding, and retain notes across rubric topics instead of reopening every image for every check. To inspect another region, replace `sample` with a numeric page: four tiles per page with40px overlap, explicit coordinates and `nextPage`. Complete numeric coverage is available when needed, not mandatory for every long page. Tiles are generated lazily from the hash-verified original PNG, without replaying the app or changing the review. No tile generation marks anything inspected or passed. A new artifact requires fresh capture and judgments; observations from a previous artifact are not reusable evidence.

Then record judgments one topic at a time. Packet pages do not mark images inspected. Inspect the captures outside-in and inside-out using [principles](principles.md) and the [rubric topics](index.md). Write a small `judgments.json` array, recording only checks actually reviewed. You can submit one topic at a time:

```json
[
 {"id":"layout.rails","status":"pass","states":["initial","expanded","validation"],"note":"The field and disclosure edges share the same rail in the inspected narrow/wide and doubled-text captures."},
 {"id":"image.integrity","status":"na","note":"No generated image assets in this application."}
]
```

`states` accepts exact capture IDs or scenario IDs. A scenario ID selects only that scenario’s **required visual sample**, never its entire machine matrix. Use it only after inspecting all of that sample. Exact IDs can record additional captures you actually inspected; these become declared visual scope. No wildcard or automatic pass is provided. The recorder attaches those existing captures and measurements to the judgment, preserving your observation. Additional interaction/source evidence can be supplied in `evidence`. Failed judgments require `severity` and `diagnosis:{owner,cause,confidence,repair,recheck}` as in the rubric contract. Unknown causes are honest; unfinished inspection remains blocked. Do not relabel an unreviewed required sample as not applicable.

```sh
python3 scripts/run.py review-session.mjs record NEW_EVIDENCE_DIR/review.json judgments.json
python3 scripts/run.py review-session.mjs status NEW_EVIDENCE_DIR/review.json
```

Status returns counts and at most eight outstanding entries per category: rubric IDs, capture errors, unlinked visual states and mechanical findings. Its `fullQueue` file preserves the full queue. Retrieve the next outstanding topic, inspect its evidence, record the judgment and repeat until no outstanding work remains. Complete all19 rubric dispositions, with justified not-applicable items where appropriate; automated passes never supply those judgments. Each record saves a checkpoint. Address review coverage before spending remaining time on optional refinements: a completed review with concrete failures is useful; uninspected states are not completed review. Measurements never substitute for composition judgments. Then [finish the delivery receipt](delivery.md); unresolved failures may yield complete-with-findings, not acceptance. If the artifact changed, a new capture is required; earlier judgments cannot be carried forward by changing a hash.
