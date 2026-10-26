import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {root} from './token-index.mjs';
const [pw, output] = process.argv.slice(2);
if (!pw || !output || fs.existsSync(output)) throw Error('Usage: check-compound-save.mjs PLAYWRIGHT NEW_OUTPUT');
const out = path.resolve(output);
fs.mkdirSync(out, {recursive: true});
const action = (selector, action, value) => ({selector, action, value});
const check = (selector, assert, value) => ({selector, assert, value});
const saved = [check('#status', 'textEquals', 'Saved'), check('#confirmation', 'visible', true)];
const stale = [check('#status', 'textEquals', 'Unsaved changes'), check('#confirmation', 'visible', false), check('#confirmations', 'checked', true)];
const save = [action('#save', 'click'), ...saved];
const changes = {
  text: action('#title', 'fill', 'Revised'),
  choice: action('#extended', 'check'),
  capacity: action('#capacity', 'fill', '8'),
  identities: action('#beta', 'check')
};
const acceptance = {version: 2, surface: 'review', cases: [
  {id: 'desktop-light', targetType: 'unit', target: 'compound-save', variant: 'A', viewport: 'desktop', scheme: 'light'},
  {id: 'mobile-dark', targetType: 'unit', target: 'compound-save', variant: 'A', viewport: 'mobile', scheme: 'dark'}
], requirements: [
  ...Object.entries(changes).map(([id, edit]) => ({id: 'invalidate-' + id, type: 'scenario', description: 'Editing saved ' + id + ' invalidates both current-success surfaces without changing the preference.', setup: save, steps: [edit, ...stale]})),
  {id: 'restore-compound', type: 'scenario', description: 'Restore every domain field and synchronized output, retaining independent preferences and filter.', setup: save, steps: [
    ...Object.values(changes), action('#alpha', 'uncheck'), action('#confirmations', 'uncheck'), action('#filter', 'fill', 'beta'), action('#restore', 'click'),
    check('#title', 'value', 'Planning'), check('#basic', 'checked', true), check('#extended', 'checked', false), check('#capacity', 'value', '4'), check('#capacity-summary', 'textEquals', '4 places'),
    check('#alpha', 'checked', true), check('#beta', 'checked', false), check('#participants', 'textEquals', 'alpha'), check('#status', 'textEquals', 'Saved'),
    check('#confirmations', 'checked', false), check('#confirmation', 'visible', false), check('#filter', 'value', 'beta'), check('#filtered-participants', 'textEquals', 'No matches'), action('#confirmations', 'check'), ...saved]},
  {id: 'invalid-preserves-snapshot', type: 'scenario', description: 'Invalid save cannot replace the last valid compound snapshot.', setup: save, steps: [action('#title', 'fill', ''), changes.choice, changes.capacity, changes.identities, action('#save', 'click'), ...stale, action('#restore', 'click'), check('#title', 'value', 'Planning'), check('#basic', 'checked', true), check('#capacity', 'value', '4'), check('#beta', 'checked', false), ...saved]},
  {id: 'manual-return', type: 'scenario', description: 'Returning all saved values restores current success; a partial return remains stale.', setup: save, steps: [changes.text, changes.choice, changes.capacity, changes.identities, action('#title', 'fill', 'Planning'), action('#basic', 'check'), action('#capacity', 'fill', '4'), ...stale, action('#beta', 'uncheck'), ...saved]},
  {id: 'identity-substitution', type: 'scenario', description: 'Replacing a selected identity must dirty the snapshot even when the count is unchanged.', setup: save, steps: [action('#alpha', 'uncheck'), action('#beta', 'check'), ...stale, action('#restore', 'click'), check('#alpha', 'checked', true), check('#beta', 'checked', false), ...saved]},
  {id: 'identity-set-order', type: 'scenario', description: 'Selection identity is a set; toggling order does not change the saved selection.', setup: [action('#beta', 'check'), ...save], steps: [action('#alpha', 'uncheck'), ...stale, action('#alpha', 'check'), ...saved, check('#participants', 'textEquals', 'alpha, beta')]},
  {id: 'view-independence', type: 'scenario', description: 'Confirmation preference and filter never dirty the saved task.', setup: save, steps: [action('#filter', 'fill', 'missing'), check('#filtered-participants', 'textEquals', 'No matches'), ...saved, action('#confirmations', 'uncheck'), check('#status', 'textEquals', 'Saved'), check('#confirmation', 'visible', false), action('#confirmations', 'check'), ...saved]},
  {id: 'keyboard-and-remount', type: 'scenario', description: 'Native keyboard Save commits current state; remount retains draft and saved identity.', steps: [changes.text, action('#save', 'focus'), action('#save', 'press', 'Enter'), ...saved, changes.capacity, ...stale, {action: 'remount', value: 'mobile'}, check('#capacity', 'value', '8'), ...stale, action('#restore', 'click'), check('#title', 'value', 'Revised'), check('#capacity', 'value', '4'), ...saved]}
]};
const ap = path.join(out, 'acceptance.json');
fs.writeFileSync(ap, JSON.stringify(acceptance, null, 2));
fs.chmodSync(ap, 0o444);
const html = fs.readFileSync(path.join(root, 'assets/recipes/compound-save.html'), 'utf8');
const controller = fs.readFileSync(path.join(root, 'assets/recipes/compound-save.js'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'assets/minimal.manifest.json')));
manifest.projectId = 'compound-save-verification'; manifest.title = 'Compound saved-state verification';
manifest.units[0].id = 'compound-save'; manifest.units[0].title = 'Session plan'; manifest.units[0].variants[0].html = html;
const mp = path.join(out, 'manifest.json'); fs.writeFileSync(mp, JSON.stringify(manifest, null, 2));
const results = [];
function invoke(name, script, args) {
  const run = spawnSync(process.execPath, [path.join(root, 'scripts', script), ...args], {encoding: 'utf8', maxBuffer: 16 * 1024 * 1024});
  fs.writeFileSync(path.join(out, name + '.stdout.log'), run.stdout || '');
  fs.writeFileSync(path.join(out, name + '.stderr.log'), run.stderr || '');
  if (run.error) throw run.error;
  return run;
}
function build(name, code) {
  const cp = path.join(out, name + '.js'); fs.writeFileSync(cp, code);
  const dir = path.join(out, name);
  const run = invoke(name, 'generate.mjs', [mp, dir, pw, '--controller', cp, '--mode', 'delivery', '--acceptance', ap]);
  let diagnostic;
  if (run.status !== 0) {try {diagnostic = JSON.parse(run.stderr).diagnostics;} catch {}}
  const reportPath = path.join(diagnostic || dir, 'acceptance-report.json');
  assert(fs.existsSync(reportPath), name + ': acceptance not reached; inspect local logs');
  return {run, dir, reportPath, report: JSON.parse(fs.readFileSync(reportPath))};
}
const baseline = build('verified', controller);
assert.equal(baseline.run.status, 0, 'Baseline generation failed; inspect local logs');
assert.equal(baseline.report.pass, true);
assert.equal(JSON.parse(fs.readFileSync(path.join(baseline.dir, 'generation.json'))).delivery.status, 'delivery-verified');
assert.equal(invoke('report-identity', 'verify-acceptance.mjs', ['--check-report', baseline.reportPath, path.join(baseline.dir, 'artifact.html'), ap]).status, 0);
results.push({name: 'baseline', pass: true, cases: baseline.report.cases.length, requirementsPerCase: acceptance.requirements.length});
const faults = [
  ['stale-secondary', '!(current && state.confirmations)', '!(state.saved && state.confirmations)', ['invalidate-text', 'invalidate-choice', 'invalidate-capacity', 'invalidate-identities']],
  ['omitted-capacity', 'capacity: state.capacity,', "capacity: '4',", ['invalidate-capacity']],
  ['omitted-identities', 'selected: [...new Set(state.selected)].sort()', 'selected: []', ['invalidate-identities']],
  ['count-only-identities', 'selected: [...new Set(state.selected)].sort()', 'selected: [String(state.selected.length)]', ['identity-substitution']],
  ['order-sensitive-identities', 'selected: [...new Set(state.selected)].sort()', 'selected: [...new Set(state.selected)]', ['identity-set-order']]
];
for (const [name, from, to, rejected] of faults) {
  assert.equal(controller.split(from).length, 2, 'Fault must match exactly once: ' + name);
  const result = build(name, controller.replace(from, to));
  assert.notEqual(result.run.status, 0, name + ' incorrectly delivered');
  assert.equal(result.report.pass, false);
  assert(!fs.existsSync(result.dir), name + ' published a failed artifact');
  for (const c of result.report.cases) for (const id of rejected) assert.equal(c.results.find(r => r.id === id)?.status, 'assertion-failure', name + ' must fail ' + id + ' by assertion');
  for (const c of result.report.cases) assert.equal(c.results.find(r => r.id === 'view-independence')?.status, 'pass', name + ' must preserve unrelated view behavior');
  results.push({name, rejected: true, requiredFailures: rejected, report: result.reportPath});
}
fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify({results, scope: 'Authored final generated artifact, Chromium desktop/light and mobile/dark. Not model efficacy, independent evaluation, native Safari, or accessibility certification.'}, null, 2));
console.log('PASS compound snapshot baseline and 5 discriminating controls: ' + out);
