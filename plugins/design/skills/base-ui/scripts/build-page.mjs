// One-time modular consumer scaffold. Existing projects own subsequent edits.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {compileControls, describeKit, readSource, validateUI} from './api.mjs';
import {sources} from './token-index.mjs';
import {bundledFontCSS} from './lib/font-css.mjs';

export function buildPage(source, destination, scriptPath) {
 const output = path.resolve(destination);
 if (fs.existsSync(output)) throw Error('Refusing existing output directory: ' + output);
 const identity = describeKit();
 const fragment = fs.readFileSync(source, 'utf8');
 const missing = validateUI({html: fragment}).unknownTokens;
 if (missing.length) throw Error('Unknown UI tokens: ' + missing.join(', '));
 const runtime = readSource('assets/ui-runtime.js');
 const controller = scriptPath ? fs.readFileSync(scriptPath, 'utf8') : '// Consumer-owned classic controller. Runtime helpers are available here.\n';
 // Parse in their shared classic-script scope, catching collisions before writing.
 new vm.Script(runtime + '\n;\n' + controller);
 const pageStyles = [];
 const markup = compileControls(fragment.replace(/<style\b[^>]*>([\s\S]*?)<\/style\s*>/gi, (_, css) => { pageStyles.push(css); return ''; }));
 const meta = JSON.stringify(identity).replace(/</g, '\\u003c');
 const files = {
  'index.html': `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UI page</title><link rel="stylesheet" href="styles/index.css"></head><body class="product__root">${markup}<script type="application/json" id="base-ui-source">${meta}</script><script src="runtime/kit.js"></script><script src="runtime/controller.js"></script></body></html>\n`,
  'styles/index.css': '@import "./recipes/index.css";\n@import "./pages/page.css";\n',
  'styles/shared/index.css': '@import "../vendor/fonts.css";\n@import "../vendor/tokens.css";\n@import "../vendor/kit.css";\n@import "./tokens.css";\n@import "./recipe-tokens.css";\n@import "./core.css";\n',
  'styles/recipes/index.css': '@import "../shared/index.css";\n@import "./page.css";\n',
  'styles/shared/tokens.css': '/* Authored source colors and semantic mappings. Preserve kit geometry formulas. */\n',
  'styles/shared/recipe-tokens.css': '/* Authored recipe semantic mappings. */\n',
  'styles/shared/core.css': '/* Consumer-owned common layout. */\n',
  'styles/recipes/page.css': '/* Consumer-owned recipe slot, variant and state rules. */\n',
  'styles/pages/page.css': pageStyles.join('\n') || '/* Consumer-owned page arrangement. */\n',
  'styles/vendor/fonts.css': bundledFontCSS(),
  'styles/vendor/tokens.css': [sources.color, sources.typography, sources.geometry, sources.layout].map(readSource).join('\n'),
  // Keep profile then semantic overlays in the same cascade order as getAssetBundle.
  'styles/vendor/kit.css': [sources.profile, sources.palettes].map(readSource).join('\n'),
  'runtime/kit.js': runtime,
  'runtime/controller.js': controller,
  'index.html.review-status.json': JSON.stringify({status:'pending-review', artifact:path.join(output, 'index.html'), next:'review-session.mjs capture ARTIFACT PLAYWRIGHT PLAN.mjs NEW_EVIDENCE_DIR [CHROME]', contract:'references/review/delivery.md'}, null, 2) + '\n'
 };
 // Exclusive directory creation prevents any reseeding/overwrite, including races.
 fs.mkdirSync(path.dirname(output), {recursive:true});
 fs.mkdirSync(output);
 for (const [relative, contents] of Object.entries(files)) {
  const target = path.join(output, relative);
  fs.mkdirSync(path.dirname(target), {recursive:true});
  fs.writeFileSync(target, contents, {flag:'wx'});
 }
 return path.join(output, 'index.html');
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
 const [source, destination, controller, ...extra] = process.argv.slice(2);
 if (!source || !destination || extra.length) throw Error('Usage: build-page.mjs FRAGMENT.html NEW_DIRECTORY [CONTROLLER.js]');
 console.log(buildPage(source, destination, controller));
 console.error('Draft only. Edit consumer CSS/controller in place; this scaffold refuses every existing directory. Run rendered-contract and relevant state checks, then the review delivery gate. Copy the complete asset tree when delivering.');
}
