/** Pure page-body renderers. Input contract is documented in source-map.json. */
const STAGES = ['seeds', 'raw exports', 'semantic bindings', 'type/geometry', 'components', 'compositions', 'generated interfaces'];
const CLASSES = ['implementation defect', 'missing context', 'ambiguous context', 'retrieval failure', 'generation drift', 'missing coverage', 'stale evidence', 'planning/specification'];
const list = (value, name) => { if (!Array.isArray(value)) throw new TypeError(`${name} must be an array`); return value; };
function unique(rows, name) {
  list(rows, name); const ids = new Set();
  for (const row of rows) { if (!row || typeof row.id !== 'string' || !row.id.trim() || ids.has(row.id)) throw new TypeError(`${name}: missing or duplicate id`); ids.add(row.id); }
  return rows;
}
function presentation(helpers, excerpts = {}) {
  for (const key of ['esc', 'code', 'sourceLink', 'inspector', 'sourceIdentity']) if (typeof helpers?.[key] !== 'function') throw new TypeError(`Missing helper ${key}`);
  const {esc, code, sourceLink, inspector, sourceIdentity} = helpers;
  const text = value => value == null || value === '' ? 'Unavailable' : typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value);
  const wrap = value => `<span class="gap-path">${esc(text(value))}</span>`;
  const gap = value => `<p data-status="unavailable">${esc(value)}: unavailable</p>`;
  const field = (label, value) => `<p><strong>${esc(label)}:</strong> ${wrap(value)}</p>`;
  function source(ref) {
    if (!ref || typeof ref.path !== 'string' || typeof ref.selectionKey !== 'string') return gap('Authoritative source selection');
    const identity = sourceIdentity(ref.path, ref.selectionKey);
    const excerpt = excerpts[ref.path]?.[ref.selectionKey];
    if (typeof excerpt !== 'string' || !excerpt.length || identity?.path !== ref.path || identity?.selectionKey !== ref.selectionKey || !/^[a-f0-9]{64}$/i.test(identity?.sha256 ?? '')) return gap(`Source excerpt/identity ${ref.path} ${ref.selectionKey}`);
    // Link visible text may be long; preserve entities and attributes while adding breaks.
    const link = sourceLink(ref.path);
    return `<div class="flow__root" data-source-path="${esc(ref.path)}"><p>${link}</p><p>Path: ${wrap(identity.path)} · SHA-256: ${wrap(identity.sha256)} · Selection: ${wrap(identity.selectionKey)}</p>${code(excerpt)}</div>`;
  }
  const refs = value => value == null ? gap('Source/context selections') : list(value, 'source selections').map(source).join('') || gap('Source/context selections');
  return {esc, code, inspector, text, gap, field, source, refs};
}
function freshness(report, inventory) {
  if (!report) return 'unavailable';
  if (!inventory?.sourceHash || !inventory?.generatorHash || !report.sourceHash || !report.generatorHash) return 'unverified';
  if (report.sourceHash !== inventory.sourceHash || report.generatorHash !== inventory.generatorHash) return 'stale';
  if (report.outsideSource !== true) return 'unverified';
  return 'compatible';
}
export function renderIndex({inventory, entryContext, routes, seedState, capabilityCoverage, evaluations, evidence, helpers}) {
  const p = presentation(helpers, entryContext?.excerpts); const {esc, code, inspector, gap, field, refs} = p;
  if (!inventory || typeof inventory !== 'object') throw new TypeError('inventory required');
  const declarations = unique(inventory.declarations, 'inventory.declarations');
  const specimens = unique(inventory.specimens, 'inventory.specimens');
  const requirements = unique(inventory.requirements, 'inventory.requirements');
  const sources = unique(inventory.sources, 'inventory.sources');
  const units = unique(inventory.units, 'inventory.units');
  const state = freshness(evidence, inventory);
  const checks = evidence == null ? null : unique(evidence.checks, 'evidence.checks');
  if (checks?.some(c => !['pass','fail','unverified'].includes(c.outcome))) throw new TypeError('Unknown check outcome');
  if (checks?.some(c => !requirements.some(r => r.id === c.id))) throw new TypeError('Check has no declared requirement');
  const checkCounts = {pass:0, fail:0, stale:0, unverified:0};
  for (const requirement of requirements) { const c = checks?.find(c => c.id === requirement.id); checkCounts[state === 'stale' && c ? 'stale' : state === 'compatible' && c ? c.outcome : 'unverified']++; }
  const missingDeclarations = declarations.filter(d => d.available === false).length;
  if (declarations.some(d => typeof d.available !== 'boolean') || specimens.some(s => typeof s.demonstrated !== 'boolean')) throw new TypeError('Explicit declaration availability/specimen demonstration required');
  const chain = STAGES.map(stage => {
    const unit = units.find(u => u.stage === stage);
    if (!unit) return `<section class="section__flow"><h2>${esc(stage)}</h2>${gap('Stage inventory and local context')}</section>`;
    const stageSources = sources.filter(s => s.stage === stage);
    const key = ref => `${ref.path}#${ref.selectionKey}`;
    const expected = stageSources.map(key).sort();
    if (!expected.length || new Set(expected).size !== expected.length) throw new TypeError('Missing or duplicate stage source: ' + stage);
    for (const name of ['manifest', 'context', 'implementation']) {
      const selected = list(unit[name], 'unit.' + name).map(key).sort();
      if (JSON.stringify(selected) !== JSON.stringify(expected)) throw new TypeError('Source-chain selection mismatch: ' + stage + ' ' + name);
    }
    const selections = `<ul>${stageSources.map(ref => `<li>${field('Source', ref.path)}${field('Selection', ref.selectionKey)}</li>`).join('')}</ul>`;
    const markup = `<div class="card__root flow__root" data-chain-stage="${esc(stage)}">${field('Stage', stage)}${field('Source records', stageSources.length)}${unit.description ? field('Description', unit.description) : ''}${selections}</div>`;
    return `<section id="${esc(unit.id)}" class="section__flow"><h2>${esc(stage)}</h2>${markup}${inspector('Implementation', code(markup) + refs(unit.implementation))}${inspector('Manifest', refs(unit.manifest))}${inspector('Context', refs(unit.context))}${inspector('Verification', field('Evidence compatibility', state) + field('Applicable requirement IDs', unit.requirementIds) + '<p>Declarations and this displayed inventory are not passing checks.</p>')}</section>`;
  }).join('');
  if (units.some(u => !STAGES.includes(u.stage)) || new Set(units.map(u => u.stage)).size !== units.length) throw new TypeError('Unknown or duplicate source-chain stage');
  const scopedEvaluations = evaluations == null ? gap('Generated-interface evaluations') : unique(evaluations, 'evaluations').map(e => {
    if (!e.task || !e.model) throw new TypeError('Evaluation task/model scope required');
    if(e.applicability==='historical-cohort'){
      if(!e.reasoningEffort||!Array.isArray(e.cohorts)||!Array.isArray(e.results))throw new TypeError('Historical cohort provenance required');
      return `<article id="generation-${esc(e.id)}" class="card__root flow__root" data-generation-scope="historical-cohort">${field('Task',e.task)}${field('Model',e.model)}${field('Reasoning effort',e.reasoningEffort)}${field('Applicability','Historical cohort; current-source transfer unverified')}${field('Study scope',e.scope)}${field('Frozen cohorts',e.cohorts.map(c=>({id:c.id,files:c.files,sha256:c.manifestSha256})))}${e.cohorts.map(c=>`<p>${helpers.sourceLink(c.manifestPath)}</p>`).join('')}${e.results.map(r=>`<div class="flow__root">${field('Recorded result',r.label)}${code(JSON.stringify(r.value,null,2))}<p>${helpers.sourceLink(r.path)}</p>${field('Selection',r.pointer)}${field('Evidence SHA-256',r.sha256)}</div>`).join('')}${field('Limitations',e.limitations)}</article>`;
    }
    return `<article class="flow__root">${field('Task', e.task)}${field('Model', e.model)}${field('Evidence compatibility', freshness(e, inventory))}${field('Result', freshness(e, inventory) === 'compatible' ? e.result : 'Unverified/stale; recorded result: ' + p.text(e.result))}${field('Environment and evidence', e.evidence)}</article>`;
  }).join('') || gap('Generated-interface evaluations');
  return `<div class="page__flow"><header class="heading-group__root"><h1>System index</h1><p>Source declarations, visible demonstrations and verification are separate records.</p></header><section class="section__flow"><h2>Review domains</h2><div class="grid__root">${[['index','Source chain and entry routes'],['tokens','Typography and geometry'],['colors','Palettes and semantic bindings'],['components','Capabilities and compositions'],['gaps','Actionable findings']].map(([page,label]) => `<a class="card__root flow__root" href="${page}.html"><strong>${esc(label)}</strong></a>`).join('')}</div></section><section class="section__flow"><h2>Inventory and evidence</h2>${field('Declared records', declarations.length)}${field('Missing declarations', missingDeclarations)}${field('Registered specimen records', specimens.length)}<p>Registered specimens, observed source members and tested states are separate evidence. The capability matrix preserves supplied observations; a source plan is not execution.</p>${field('Demonstrated specimens', specimens.filter(s => s.demonstrated).length)}${field('Missing specimens', specimens.filter(s => !s.demonstrated).length)}${field('Checks', checkCounts)}${field('Verification availability', state)}${inspector('Source coverage details', capabilityCoverage == null ? gap('Capability coverage') : code(JSON.stringify(capabilityCoverage,null,2)))}${field('Build timestamp (not verification)', inventory.builtAt)}</section><section class="section__flow"><h2>Entry context and conditional routes</h2><p>The skill entry routes generation tasks to their applicable contracts. Source and agent context is available below.</p>${inspector('Source & agent context', refs(entryContext?.sources) + refs(routes) + (seedState == null ? gap('Seed state') : refs(seedState.sources)))}</section>${chain}<section class="section__flow"><h2>Generated-interface evaluations</h2>${inspector('Historical evaluation records', scopedEvaluations)}</section>${inspector('Provenance', field('Source hash', inventory.sourceHash) + field('Generator hash', inventory.generatorHash) + sources.map(s => p.source(s)).join(''))}</div>`;
}
// Disposition is explicit register data, never inferred from historical prose.
const DISPOSITIONS = {
  'open': 'open',
  'canonical-complete': 'completed',
  'accepted-limitation': 'accepted',
  'canonical-complete-with-accepted-limitations': 'accepted',
};
export function groupWorkItems(items) {
  unique(items, 'workRegister');
  const groups = {open: [], accepted: [], completed: []};
  for (const item of items) {
    const group = DISPOSITIONS[item.normalizedStatus];
    if (!group) throw new TypeError(`Work item ${item.id}: unsupported normalizedStatus ${JSON.stringify(item.normalizedStatus)}; reconcile the register disposition before building`);
    if (typeof item.complete === 'boolean' && item.complete !== (group !== 'open')) throw new TypeError(`Work item ${item.id}: complete contradicts normalizedStatus; reconcile the register`);
    groups[group].push(item);
  }
  // Preserve register order within a priority. Dependencies are displayed, not invented.
  groups.open.sort((a,b) => ({P0:0,P1:1,P2:2,P3:3}[a.priority] ?? 4) - ({P0:0,P1:1,P2:2,P3:3}[b.priority] ?? 4));
  return groups;
}

export function renderGaps({findings, workRegister, rawObservations = [], reviewUnitMap, sharedContext, snapshot, helpers}) {
  const {esc, sourceLink} = helpers;
  unique(findings, 'findings'); unique(rawObservations, 'rawObservations');
  const groups = groupWorkItems(workRegister ?? []);
  const records = new Map(findings.map(f => [f.id,f]));
  for (const w of workRegister ?? []) if (!records.has(w.id)) throw new TypeError(`Missing rendered work item ${w.id}`);
  for (const f of findings) if (!(workRegister ?? []).some(w => w.id === f.id)) throw new TypeError(`Finding ${f.id} has no work record; keep raw source observations separate`);
  const text = value => Array.isArray(value) ? value.join('; ') : typeof value === 'string' ? value : '';
  const field = (label,value) => value ? `<p><strong>${esc(label)}:</strong> ${esc(text(value))}</p>` : '';
  const link = (href,label) => `<a class="gap-path" href="${esc(href)}">${esc(label)}</a>`;
  const fullRecord = () => link('review-inputs/work-register.json','Full record and original history in the register');
  const title = w => w.title?.trim() || `Title missing for ${w.id}`;
  const identity = w => `<span class="gap-record-title">${esc(title(w))}</span><span class="meta gap-record-id">${esc(w.id)}</span>`;
  const alias = w => w.id.startsWith('G-') ? `<span id="${esc(w.id.slice(2))}" aria-hidden="true"></span>` : '';
  const kind = w => ({'missing context':'Missing guidance','missing coverage':'Coverage gap','planning/specification':'Delivery task'}[w.classification] ?? w.classification ?? 'Kind not recorded');
  const evidence = w => {
    const links = w.evidenceLinks ?? [];
    return links.length ? `<p class="gap-evidence">Recorded evidence: ${links.map(r=>link(r.href,r.label)).join(' · ')}</p>` : `<p>Evidence link unavailable; consult the original references in the full register.</p>`;
  };
  const affected = w => (w.affectedUnitIds ?? []).map(id => reviewUnitMap?.[id] ? link(reviewUnitMap[id],id) : `<span>Review link unavailable: ${esc(id)}</span>`).join(' · ');
  const sourceRefs = w => (w.sourceSelections ?? []).map(ref=>`<li>${sourceLink(ref.path)} <span class="meta gap-path">(${esc(ref.selectionKey)})</span></li>`).join('');
  const extras = w => `${w.acceptance ? field('Original closure criterion',w.acceptance) : '<p>Closure criterion missing from the register.</p>'}${affected(w) ? `<p>Affected review units: ${affected(w)}</p>` : ''}${sourceRefs(w) ? `<ul>${sourceRefs(w)}</ul>` : ''}${evidence(w)}<p>${fullRecord()} · ${link('review-inputs/evidence-index.json','Evidence references and identities')}</p>`;
  const decisions = w => [w.resolution, ...(w.acceptedSubpartLimitations ?? [])].filter(r=>r?.kind==='accepted-limitation');
  const limitations = w => decisions(w).map(r=>`<li>${field('Accepted scope',r.scope)}${field('Qualification',r.qualification)}${field('User decision',r.userAnswer)}${r.report ? field('Decision reference',r.report) : ''}</li>`).join('');
  const openRow = w => {
    const condition = w.presentation?.condition ?? w.unresolvedCondition;
    const recordedAction = w.execution?.remainingAction ?? w.correctiveAction;
    const action = ['done','resolved'].includes(w.execution?.phase) ? `Contradiction: the item is open but its execution phase is ${w.execution.phase}. Reconcile the register before acting. Recorded action: ${recordedAction || 'missing'}` : recordedAction;
    // Lengthy logs are kept in the snapshot. Missing concise inputs are explicit.
    const conditionText = condition || (typeof w.status==='string' && w.status.length <= 420 ? w.status : 'Concise unresolved condition is not recorded; inspect the full register before choosing an action.');
    return `<article id="${esc(w.id)}" data-work-id="${esc(w.id)}" data-disposition="open" class="card__root section__flow">${alias(w)}<header class="heading-group__root"><h3>${esc(title(w))}</h3><p class="meta">${esc(w.id)} · ${esc(kind(w))}${w.priority ? ' · '+esc(w.priority) : ''}</p></header>${field('Unresolved condition',conditionText)}${field('Next action',action || 'Missing; reconcile the action in the register.')}${field('Owner',w.owner || 'Missing; assign an owner in the register.')}${field('Blocker or dependency',w.blocker ?? w.dependencies ?? w.dependency)}${field('Closure criterion',w.presentation?.closure ?? (w.acceptance ? (w.acceptance.length<=260?w.acceptance:w.acceptance.slice(0,260).replace(/\s+\S*$/,'')+'… (full criterion below)') : 'Missing from the register.'))}${evidence(w)}<details class="disclosure__root"><summary>Details and evidence</summary>${extras(w)}</details></article>`;
  };
  const acceptedRow = w => `<details id="${esc(w.id)}" data-work-id="${esc(w.id)}" data-disposition="accepted" class="disclosure__root"><summary>${identity(w)}</summary>${alias(w)}<p>${w.normalizedStatus==='canonical-complete-with-accepted-limitations' ? 'Canonical work is recorded as completed with the following accepted limitations.' : 'Resolved for delivery through an accepted limitation.'} Failed or unverified aspects remain so; this is not a verification pass.</p>${limitations(w) ? `<ul class="flow__root">${limitations(w)}</ul>` : '<p>Acceptance scope or decision provenance is missing; reconcile it with the register.</p>'}${w.reopeningCondition ? field('Reopening condition',w.reopeningCondition) : ''}${extras(w)}</details>`;
  const completedRow = w => `<details id="${esc(w.id)}" data-work-id="${esc(w.id)}" data-disposition="completed" class="disclosure__root"><summary>${identity(w)}<span class="meta">Completed work</span></summary>${alias(w)}<p>The register records this work as completed. Its disposition does not certify the current page or a newly generated interface.</p>${typeof w.status==='string' && w.status.length <= 420 ? field('Recorded result',w.status) : '<p>Detailed result and historical failures remain in the linked record and evidence.</p>'}${extras(w)}</details>`;
  const raw = rawObservations.map(f=>{
    const matched = (workRegister ?? []).filter(w=>(w.sourceIds ?? []).includes(f.id));
    if (matched.length>1) throw new TypeError(`Multiple work records match source observation ${f.id}`);
    return `<article id="observation-${esc(f.id)}" data-raw-observation-id="${esc(f.id)}" class="section__flow">${matched.length ? '' : `<span id="${esc(f.id)}" aria-hidden="true"></span>`}<h3>${esc(f.item ?? f.id)}</h3>${field('Observation',f.missing)}${field('Scope or impact',f.impact)}${field('Source owner',f.owner)}<p>${matched.length ? `Mapped work item: ${link('#'+matched[0].id,matched[0].id)}. This observation is not an additional work item.` : 'Unmapped source observation: reconciliation needed; no work requirement has been created or closed.'}</p></article>`;
  }).join('');
  const count = group => groups[group].length;
  return `<div class="page__flow gap-status" data-work-dispositions><header class="heading-group__root"><h1>Gaps and delivery status</h1><p>Remaining work, accepted limitations and completed work are separate register dispositions.</p><p class="meta">Snapshot built ${esc(snapshot?.builtAt ?? 'time unavailable')} · Register ${esc(snapshot?.registerSHA256?.slice(0,12) ?? 'not supplied')} · ${link('#gaps-provenance','Snapshot evidence')}</p></header><div class="cluster__root gap-counts" role="group" aria-label="Filter work dispositions" data-work-filters hidden>${[['all','All'],['open','Open'],['accepted','Accepted limitations'],['completed','Completed']].map(([k,label])=>`<button type="button" class="button__root secondary" aria-pressed="${k==='all'}" data-disposition-count="${k}" data-count="${k==='all'?Object.values(groups).flat().length:count(k)}"><span data-slot="label">${esc(label)} (${k==='all'?Object.values(groups).flat().length:count(k)})</span></button>`).join('')}</div><p data-filter-status role="status" aria-live="polite"></p><section data-work-group="open" id="open-work" class="section__flow"><h2>Open work</h2>${workRegister==null ? '<p>No work register was supplied. These zero counts are not a completeness claim.</p>' : count('open') ? groups.open.map(openRow).join('') : '<p>No open work items in this register snapshot. Accepted limitations and source observations remain separately inspectable below.</p>'}</section><section data-work-group="accepted" class="section__flow"><p>Accepted limitations are delivery decisions, not verification passes.</p><details id="accepted-limitations" class="disclosure__root"><summary>Accepted limitations <span class="meta">${count('accepted')} work items</span></summary><div class="flow__root">${groups.accepted.map(acceptedRow).join('') || '<p>No accepted limitations recorded.</p>'}</div></details></section><section data-work-group="completed" class="section__flow"><details id="completed-work" class="disclosure__root"><summary>Completed work <span class="meta">${count('completed')} work items</span></summary><div class="flow__root">${groups.completed.map(completedRow).join('') || '<p>No completed work recorded.</p>'}</div></details></section><section id="gaps-shared-context" class="section__flow"><details id="gaps-provenance" class="disclosure__root"><summary>Source observations and provenance <span class="meta">${rawObservations.length} source observations</span></summary><p>Raw observations come from the narrow source-coverage check. They are neither the open-work total nor a complete defect inventory. Mapped observations do not add work-item counts.</p>${raw || '<p>No raw source observations in this build.</p>'}<h3>Shared guidance and datasets</h3><p>The register owns work identity and disposition; raw observations report source coverage; evidence records observations under named conditions.</p><p>${workRegister==null ? '<span>Work register not supplied</span>' : link('review-inputs/work-register.json','Full register snapshot')} · ${link('gaps.json','Raw source observations')} · ${link('review-inputs/evidence-index.json','Evidence index')} · ${link('inventory.json','Corpus provenance')}</p>${(sharedContext ?? []).map(ref=>`<p>${sourceLink(ref.path)}</p>`).join('')}${field('Built at',snapshot?.builtAt)}${snapshot?.registerSHA256 ? `<p class="gap-path"><strong>Register SHA-256:</strong> ${esc(snapshot.registerSHA256)}</p>` : '<p>Register identity unavailable.</p>'}<p>This static snapshot does not compare continuously with the canonical register.</p></details></section></div>`;
}
