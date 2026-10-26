import {resolve,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const repo=process.argv[2];if(!repo)throw Error('Pass the Ultimate Tokens source directory');
const source=resolve(repo,'src/engine/type.mjs'),{typeScale,typeTokensCSS}=await import(pathToFileURL(source));
const dest=resolve(dirname(fileURLToPath(import.meta.url)),'../assets/foundation/ultimate-tokens');
const css=typeTokensCSS(typeScale());writeFileSync(resolve(dest,'typography.css'),css);
writeFileSync(resolve(dest,'typography.provenance.json'),JSON.stringify({producer:'typeTokensCSS(typeScale())',configuration:'Default exported treatment; font files are not bundled, platform sans/mono fallbacks apply when unavailable',source:'src/engine/type.mjs',sourceHash:createHash('sha256').update(readFileSync(source)).digest('hex'),outputHash:createHash('sha256').update(css).digest('hex')},null,2)+'\n');
