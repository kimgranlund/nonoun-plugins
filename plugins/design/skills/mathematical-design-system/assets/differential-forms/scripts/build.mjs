import {readFileSync,writeFileSync} from 'node:fs';
const source=readFileSync(new URL('../specimens/source.html',import.meta.url),'utf8');
const doc=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Differential Forms</title><style>html{color-scheme:light dark}body{margin:0;font-family:system-ui}</style></head><body>${source}</body></html>`;
writeFileSync(new URL('../specimens/index.html',import.meta.url),doc);
console.log('Built specimens/index.html');
