#!/usr/bin/env node
// Inline the feedback module into an exploration page.
// Usage: node inline.mjs <page.html>
// Replaces the markers /*@feedback.css*/ (inside a <style>) and /*@feedback.js*/ (inside a <script>) with the files
// in ../assets. If a marker is missing it appends a <style> or <script> block at the end of the page. Running it
// again replaces the previously inlined copy (it is fenced by begin/end comments), so the page can be rebuilt safely.
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const page = process.argv[2]
if (!page) { console.error('usage: node inline.mjs <page.html>'); process.exit(1) }
const assets = join(dirname(fileURLToPath(import.meta.url)), '..', 'assets')
let html = readFileSync(page, 'utf8')
for (const [name, tag] of [['feedback.css', 'style'], ['feedback.js', 'script']]) {
  const body = readFileSync(join(assets, name), 'utf8').trim()
  const fenced = `/*@begin ${name}*/\n${body}\n/*@end ${name}*/`
  const old = new RegExp(`/\\*@begin ${name.replace('.', '\\.')}\\*/[\\s\\S]*?/\\*@end ${name.replace('.', '\\.')}\\*/`)
  const marker = `/*@${name}*/`
  if (old.test(html)) html = html.replace(old, () => fenced)
  else if (html.includes(marker)) html = html.replace(marker, () => fenced)
  else html += `\n<${tag}>\n${fenced}\n</${tag}>\n`
}
if (!/data-explore/.test(html)) console.warn('warning: no [data-explore] container; the feedback module will not start')
if (!/data-variant/.test(html)) console.warn('warning: no section[data-variant]; the feedback module will find nothing')
writeFileSync(page, html)
console.log(`inlined feedback module into ${page}`)
