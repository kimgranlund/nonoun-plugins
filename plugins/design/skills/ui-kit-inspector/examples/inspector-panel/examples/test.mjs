// Exercises every behaviour the inspector-panel contract promises, against demo.html served over http.
// Usage: node test.mjs http://localhost:8000/examples/demo.html ./out   (serve the skill folder over http; needs playwright-core)
import { mkdir } from "node:fs/promises";
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || "playwright-core");
await mkdir(process.argv[3], { recursive: true });
const URL = process.argv[2];
const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
const p = await ctx.newPage();
const errs = []; p.on("pageerror", (e) => errs.push(e.message)); p.on("console", (m) => m.type() === "error" && errs.push(m.text()));
const results = [];
const ok = (name, cond, info = "") => results.push(`${cond ? "PASS" : "FAIL"} ${name}${info ? ` · ${info}` : ""}`);
const cfg = () => p.evaluate(() => window.panel.get());
const text = (s) => p.textContent(s);
const fire = (sel, v) => p.$eval(sel, (el, v) => { el.value = v; el.dispatchEvent(new Event("input", { bubbles: true })); }, v);
const frame = () => p.evaluate(() => new Promise((r) => requestAnimationFrame(() => setTimeout(r, 0))));
const id = (path) => p.evaluate((path) => document.querySelector(`[data-path='${JSON.stringify(path)}']`).id, path);

await p.goto(URL); await p.evaluate(() => localStorage.clear()); await p.reload(); await frame();
ok("loads without errors", errs.length === 0, errs.join(" | "));
ok("one control per leaf (6 matrix cells + 9 params)", (await p.$$eval(".ip [data-path]", (els) => els.length)) === 15);
ok("status shows checks", (await text(".ip-status")) === "contract 3/3 · properties 1/1", await text(".ip-status"));
ok("count says defaults", (await text(".ip-count")) === "defaults");
ok("render ran once", (await p.evaluate(() => window.renders)) === 1);

// number
await p.fill(`#${await id(["spacing", "base"])}`, "8"); await frame();
ok("number input writes its path", (await cfg()).spacing.base === 8);
ok("output follows (padding = base × steps)", (await p.$eval(".card", (e) => e.style.padding)) === "32px");
ok("changed mark + count", (await p.$eval(`#${await id(["spacing", "base"])}`, (e) => e.classList.contains("ip-changed"))) && (await text(".ip-count")) === "1 changed");
// range
await p.focus(`#${await id(["shadow", "alpha"])}`);
await p.keyboard.press("ArrowRight"); await frame();
ok("focused keyboard range readout follows config", Number(await text(`#${await id(["shadow", "alpha"])} + output`)) === (await cfg()).shadow.alpha);
await fire(`#${await id(["shadow", "alpha"])}`, "0.5"); await frame();
ok("range writes a number", (await cfg()).shadow.alpha === 0.5);
ok("range shows its value", (await p.$eval(`#${await id(["shadow", "alpha"])} + output`, (e) => e.textContent)) === "0.5");
ok("property failure doesn't block output", (await text(".ip-status")) === "contract 3/3 · properties 0/1" && (await p.$eval(".card", (e) => e.style.boxShadow)).includes("0.5"));
// select keeps the option's type
await p.selectOption(`#${await id(["look", "ratio"])}`, "2"); await frame();
ok("select writes the option value with its type", (await cfg()).look.ratio === 16 / 9);
// toggle
await p.click(`#${await id(["look", "rounded"])}`); await frame();
ok("toggle writes a boolean", (await cfg()).look.rounded === false);
// matrix cell (array index path)
await p.fill(`#${await id(["grid", "md", 0])}`, "3"); await frame();
ok("matrix cell writes [..prefix, key]", JSON.stringify((await cfg()).grid.md) === "[3,16]");
ok("output follows the matrix", (await p.$eval(".grid", (e) => e.style.gridTemplateColumns)).startsWith("repeat(3"));
// half-typed number is ignored, not written as NaN
await p.fill(`#${await id(["shadow", "y"])}`, ""); await frame();
ok("empty number is not applied", (await cfg()).shadow.y === 4 && (await p.$eval(`#${await id(["shadow", "y"])}`, (e) => e.hasAttribute("aria-invalid"))));
await p.fill(`#${await id(["shadow", "y"])}`, "6"); await frame();

// contract failure keeps the last valid output
const before = await p.evaluate(() => ({ renders: window.renders, html: document.getElementById("out").innerHTML }));
await p.fill(`#${await id(["grid", "lg", 1])}`, "999"); await frame();
const after = await p.evaluate(() => ({ renders: window.renders, html: document.getElementById("out").innerHTML }));
ok("failing contract: render not called, output unchanged", after.renders === before.renders && after.html === before.html);
ok("failing contract: banner + bad status", !(await p.$eval(".ip-banner", (e) => e.hidden)) && (await p.$eval(".ip-status", (e) => e.classList.contains("bad"))), await text(".ip-banner"));
await p.fill(`#${await id(["grid", "lg", 1])}`, "24"); await frame();
ok("fixing it renders again and clears the banner", (await p.evaluate(() => window.renders)) === after.renders + 1 && (await p.$eval(".ip-banner", (e) => e.hidden)));

// render throwing becomes a contract failure; the panel keeps working
await p.fill(`#${await id(["look", "label"])}`, "THROW"); await frame();
ok("render error is caught and reported", (await text(".ip-banner")).includes("render threw") && errs.length === 0, await text(".ip-banner"));
await p.fill(`#${await id(["look", "label"])}`, "Tile"); await frame();
ok("panel recovers after a render error", (await p.$eval(".card p", (e) => e.textContent)).startsWith("Tile"));

// persistence: survives reload; another version is ignored
const before2 = await cfg();
await p.reload(); await frame();
ok("config persists across reload", JSON.stringify(await cfg()) === JSON.stringify(before2));
await p.evaluate(() => localStorage.setItem("ip-demo", JSON.stringify({ v: 0, cfg: { spacing: { base: 99, steps: 1 } } })));
await p.reload(); await frame();
ok("stored config with another version is ignored", (await cfg()).spacing.base === 4);
await p.evaluate(() => localStorage.setItem("ip-demo", JSON.stringify({ v: 1, cfg: { spacing: { base: "9", steps: 2 }, extra: { x: 1 }, grid: { sm: [1, 2, 3] } } })));
await p.reload(); await frame();
const merged = await cfg();
ok("merge keeps only known keys of the same type", merged.spacing.base === 4 && merged.spacing.steps === 2 && !("extra" in merged) && JSON.stringify(merged.grid.sm) === "[1,12]");

// reset
await p.click('[data-act="reset"]'); await frame();
ok("reset returns to defaults", (await text(".ip-count")) === "defaults" && (await cfg()).spacing.steps === 4);

// apply JSON
await p.click(".ip-adv > summary");
await p.fill(".ip-adv textarea", JSON.stringify({ spacing: { base: 6, steps: "x" }, look: { accent: "#ff0000" }, nope: 1 }));
await p.click('[data-act="apply"]'); await frame();
const ap = await cfg();
ok("apply JSON: valid values in, wrong types and unknown keys out", ap.spacing.base === 6 && ap.spacing.steps === 4 && ap.look.accent === "#ff0000" && !("nope" in ap));
await p.fill(".ip-adv textarea", "{ broken"); await p.click('[data-act="apply"]');
ok("apply bad JSON reports, changes nothing", (await text(".ip-msg")).startsWith("Not valid JSON") && (await cfg()).spacing.base === 6);
ok("controls sync after apply", (await p.$eval(`#${await id(["look", "accent"])}`, (e) => e.value)) === "#ff0000");

// inspector
await p.check('[data-act="inspect"]');
await p.hover(".card:nth-child(2) p");
ok("inspect: hover shows the element's spec", (await text(".ip-readout")).startsWith("Card 2 · padding 24") && (await p.$eval(".card:nth-child(2)", (e) => e.classList.contains("ip-hovered"))), await text(".ip-readout"));
await p.hover(".card:nth-child(3) .swatch");
ok("inspect: nearest [data-spec] wins", (await text(".ip-readout")).startsWith("Swatch"));
await p.uncheck('[data-act="inspect"]'); await p.hover(".card:nth-child(1)");
ok("inspect off: no marks, readout hidden", (await p.$$eval(".ip-hovered", (e) => e.length)) === 0 && (await p.$eval(".ip-readout", (e) => e.hidden)));

// copy: in a sandbox without clipboard access it falls back to selecting the JSON
await p.click('[data-act="copy"]'); await p.waitForTimeout(100);
ok("copy reports an outcome", /Copied|Selected/.test(await text(".ip-msg")), await text(".ip-msg"));

// schema errors fail loudly at build time
const thrown = await p.evaluate(async () => {
  const { createInspectorPanel } = await import("../inspector-panel.js");
  const m = document.createElement("div");
  const tryIt = (schema) => { try { createInspectorPanel({ mount: m, outputRoot: document.createElement("main"), schema, defaults: { a: 1, s: "x" }, render() {} }); return "no error"; } catch (e) { return e.message; } };
  return [tryIt([{ group: "g", params: [{ type: "number", path: ["b"], label: "b" }] }]), tryIt([{ group: "g", params: [{ type: "toggle", path: ["a"], label: "a" }] }]),
    tryIt([{ group: "g", params: [{ type: "select", path: ["s"], label: "s", options: [["y", "y"]] }] }]), tryIt([{ group: "g", params: [{ type: "slider", path: ["a"], label: "a" }] }])];
});
ok("schema errors throw with the path", thrown[0].includes('["b"] is missing') && thrown[1].includes("schema says boolean") && thrown[2].includes("isn't one of its options") && thrown[3].includes('unknown param type "slider"'), thrown.join(" | "));

// Regression fixtures use real DOM, events, localStorage and animation frames.
const regressions = await p.evaluate(async () => {
  const { createInspectorPanel } = await import("../inspector-panel.js");
  const results = [];
  const check = (name, pass) => results.push([name, !!pass]);
  const host = document.createElement("div"); document.body.append(host);
  const mount = document.createElement("aside"), outputRoot = document.createElement("main"); host.append(mount, outputRoot);
  const defaults = { n: 1, rows: [{ x: 1, nested: [2, 3] }], matrix: [[4, 5]] };
  const schema = [{ group: "Test", params: [{ type: "number", path: ["n"], label: "N" }] }];
  let renders = 0, oldChanges = 0;
  const options = { mount, outputRoot, schema, defaults, storageKey: "ip-regression",
    validate(c) { if (c.n === 8) throw Error("validation failed"); return []; },
    render(c, { root }) {
      renders++;
      const button = document.createElement("button"); button.textContent = String(c.n);
      button.onclick = () => { button.dataset.clicked = "yes"; }; root.append(button);
      if (c.n === 9) throw Error("failed after drawing");
    }, onChange() { oldChanges++; } };
  const corrupt = { rows: [{ extra: 9, nested: ["bad", 7] }], matrix: [["bad"]] };
  localStorage.setItem("ip-regression", JSON.stringify({ v: 1, cfg: corrupt }));
  let panel = createInspectorPanel(options);
  check("saved nested arrays and objects preserve default shape", JSON.stringify(panel.get()) === JSON.stringify({ n: 1, rows: [{ x: 1, nested: [2, 7] }], matrix: [[4, 5]] }));
  const ta = mount.querySelector("textarea");
  ta.value = JSON.stringify({ rows: [null], matrix: [{ bad: 1 }] }); mount.querySelector('[data-act="apply"]').click();
  check("JSON apply rejects nested null and array/object substitution", JSON.stringify(panel.get()) === JSON.stringify(defaults));
  ta.value = JSON.stringify({ rows: [{ x: 6, nested: [8, "bad"], extra: 1 }], matrix: [[10, 11]] });
  mount.querySelector('[data-act="apply"]').click();
  check("JSON apply keeps valid nested leaves and drops unknown keys", JSON.stringify(panel.get()) === JSON.stringify({ n: 1, rows: [{ x: 6, nested: [8, 3] }], matrix: [[10, 11]] }));
  panel.reset();
  const last = outputRoot.firstChild;
  panel.set(["n"], 9);
  check("partial render failure preserves live node identity", outputRoot.firstChild === last && last.textContent === "1" && mount.querySelector(".ip-banner").textContent.includes("render threw"));
  last.click(); check("preserved output retains event listeners", last.dataset.clicked === "yes");
  panel.set(["n"], 8);
  check("validation exception is reported without replacing output", outputRoot.firstChild === last && mount.querySelector(".ip-banner").textContent.includes("validate threw"));
  panel.set(["n"], 2);
  check("panel recovers after validation and render exceptions", outputRoot.textContent === "2" && mount.querySelector(".ip-banner").hidden);
  const input = mount.querySelector("[data-path]");
  const baseline = { h: getComputedStyle(input).height, font: getComputedStyle(input).fontSize, padding: getComputedStyle(mount.querySelector(".ip")).padding };
  host.style.cssText = "--h:0px;--inset:999px;--type-control:0px;--type-title:0px;--radius:999px;--widget-margin:999px;--widget-gutter:999px;--card-gutter:999px;--type-field-label:0px;--type-group-kicker:0px;--listbox-inset:999px;--corner-shape:scoop";
  check("tuned ancestor tokens cannot alter panel geometry or typography", getComputedStyle(input).height === baseline.h && getComputedStyle(input).fontSize === baseline.font && getComputedStyle(mount.querySelector(".ip")).padding === baseline.padding);
  panel.inspect(true);
  input.value = "3"; input.dispatchEvent(new Event("input", { bubbles: true }));
  const before = renders;
  panel.destroy(); panel.destroy();
  await new Promise(resolve => requestAnimationFrame(resolve));
  check("destroy cancels pending renders and clears inspector state", renders === before && !mount.childNodes.length && !outputRoot.classList.contains("ip-inspecting"));
  const oldCount = oldChanges;
  const next = createInspectorPanel({ ...options, storageKey: undefined, onChange() {} });
  const fresh = mount.querySelector("[data-path]"); fresh.value = "4"; fresh.dispatchEvent(new Event("input", { bubbles: true }));
  await new Promise(resolve => requestAnimationFrame(resolve));
  mount.querySelector('[data-act="reset"]').click();
  check("remount does not invoke old input or action handlers", oldChanges === oldCount && next.get().n === 1);
  next.destroy(); host.remove(); localStorage.removeItem("ip-regression");
  return results;
});
for (const [name, pass] of regressions) ok(name, pass);

// Differential Forms consumer boundaries: independently asserted CSS-pixel goldens.
// The output root is separate; panel geometry must remain independent of the tuned config.
await p.evaluate(async () => {
  const { createInspectorPanel } = await import("../inspector-panel.js");
  window.dfCreateFixture = (geometry) => {
    window.dfFixture?.destroy(); document.getElementById("df-fixture")?.remove();
    const host = document.createElement("section"); host.id = "df-fixture"; host.style.width = "360px";
    const mount = document.createElement("aside"), outputRoot = document.createElement("main");
    host.append(mount, outputRoot); document.body.append(host);
    window.dfFixture = createInspectorPanel({ mount, outputRoot, geometry,
      defaults: { text: "Readable text", number: 12, enabled: true },
      schema: [{ group: "Geometry", params: [
        { type: "text", path: ["text"], label: "Text" },
        { type: "number", path: ["number"], label: "Number" },
        { type: "toggle", path: ["enabled"], label: "Enabled" },
      ] }], render(c, { root }) { root.textContent = c.text; } });
  };
});
const dfMetrics = () => p.evaluate(() => {
  const host = document.getElementById("df-fixture");
  const field = host.querySelector('input[type="text"]'), wrapper = field.closest(".ip-field");
  const button = host.querySelector('[data-act="reset"]'), label = button.querySelector(".ip-label");
  const cs = getComputedStyle(field), bs = getComputedStyle(button), ws = wrapper && getComputedStyle(wrapper);
  const rect = (el) => el ? { width: el.getBoundingClientRect().width, height: el.getBoundingClientRect().height } : null;
  return { field: rect(wrapper), button: rect(button), label: rect(label), font: cs.fontSize, line: cs.lineHeight,
    buttonBorder: parseFloat(bs.borderTopWidth), fieldBorder: ws && parseFloat(ws.borderTopWidth),
    fieldPadding: ws && parseFloat(ws.paddingTop), buttonPadding: parseFloat(bs.paddingTop),
    buttonRadius: parseFloat(bs.borderTopLeftRadius), checkboxRadius: parseFloat(getComputedStyle(host.querySelector('input[type="checkbox"]')).borderTopLeftRadius),
    buttonOutline: [bs.outlineWidth, bs.outlineStyle, bs.outlineOffset, bs.outlineColor],
    fieldOutline: ws && [ws.outlineWidth, ws.outlineStyle, ws.outlineOffset, ws.outlineColor],
    innerOutline: cs.outlineStyle, ink: bs.color, hostWidth: host.scrollWidth,
  };
});
for (const colorScheme of ["light", "dark"]) {
  await p.emulateMedia({ colorScheme });
  for (const [density, height, inset] of [["compact", 28, 2], ["default", 32, 4], ["loose", 40, 8]]) {
    for (const border of [0, 2]) {
      await p.evaluate((geometry) => window.dfCreateFixture(geometry), { unit: 4, border, controlDensity: density, cardDensity: "loose", collectionDensity: "compact" });
      const baseline = await dfMetrics();
      const name = `${colorScheme} ${density} B${border}`;
      ok(`DF ${name}: independent control height and fixed text`, baseline.button.height === height && baseline.field?.height === height && baseline.font === "14px" && baseline.line === "20px", JSON.stringify(baseline));
      ok(`DF ${name}: border deducted once, Soft curve, checkbox1u`, baseline.buttonBorder === border && baseline.fieldBorder === border && baseline.buttonPadding === inset - border && baseline.fieldPadding === inset - border && baseline.buttonRadius === 12 && baseline.checkboxRadius === 4);
      ok(`DF ${name}: preserves label wrapper`, !!baseline.label && baseline.label.height >= 20);
      // Enter keyboard modality through a real Tab event before focusing the field.
      await p.keyboard.press("Tab");
      await p.focus('#df-fixture input[type="text"]');
      const focused = await dfMetrics();
      ok(`DF ${name}: keyboard field focus belongs to wrapper`, focused.fieldOutline?.[0] === "3px" && focused.fieldOutline?.[1] === "solid" && focused.fieldOutline?.[2] === "0px" && focused.fieldOutline?.[3] === focused.ink && focused.innerOutline === "none");
      ok(`DF ${name}: focus changes no geometry`, JSON.stringify(focused.field) === JSON.stringify(baseline.field) && JSON.stringify(focused.button) === JSON.stringify(baseline.button));
      await p.focus('#df-fixture [data-act="reset"]');
      const actionFocused = await dfMetrics();
      ok(`DF ${name}: sibling action owns its focus ring`, actionFocused.buttonOutline[0] === "3px" && actionFocused.buttonOutline[1] === "solid" && actionFocused.buttonOutline[2] === "0px" && actionFocused.buttonOutline[3] === actionFocused.ink && actionFocused.fieldOutline?.[1] === "none");
      await p.click('#df-fixture [data-act="reset"]');
      ok(`DF ${name}: pointer removes keyboard action ring`, (await dfMetrics()).buttonOutline[1] === "none");
      if (density === "compact" && border === 2) {
        await p.keyboard.press("Tab"); await p.focus('#df-fixture input[type="text"]');
        await p.locator("#df-fixture").screenshot({ path: process.argv[3] + `/focus-${colorScheme}-compact-border2.png` });
      }
    }
  }
}
await p.evaluate(() => { window.dfFixture.destroy(); document.getElementById("df-fixture").remove(); delete window.dfFixture; delete window.dfCreateFixture; });
await p.emulateMedia({ colorScheme: "light" });

// timing of one update
const ms = await p.evaluate(async () => { const t = performance.now(); for (let i = 0; i < 20; i++) window.panel.set(["spacing", "steps"], 1 + (i % 8)); return (performance.now() - t) / 20; });
ok("one update under 16ms", ms < 16, `${ms.toFixed(2)} ms`);

// keyboard: every control reachable and labelled
const unlabelled = await p.$$eval(".ip [data-path]", (els) => els.filter((e) => !(e.labels?.length || e.getAttribute("aria-label"))).map((e) => e.id));
ok("every control has a label", unlabelled.length === 0, unlabelled.join(","));

ok("no page errors at the end", errs.length === 0, errs.join(" | "));
await p.evaluate(() => { window.scrollTo(0, 0); document.querySelector(".ip-mount").scrollTop = 0; });
await frame();
await p.screenshot({ path: process.argv[3] + "/desktop.png", fullPage: false });

// Phone width in both color schemes.
for (const colorScheme of ["light", "dark"]) {
  const m = await b.newPage({ viewport: { width: 390, height: 800 }, colorScheme });
  m.on("pageerror", (e) => errs.push(e.message));
  await m.goto(URL); await m.evaluate(() => new Promise(resolve => requestAnimationFrame(resolve)));
  const ov = await m.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
  ok(`390px ${colorScheme}: no horizontal scroll`, ov[0] === ov[1], ov.join(" vs "));
  await m.screenshot({ path: process.argv[3] + `/phone-${colorScheme}.png`, fullPage: false });
  await m.close();
}
ok("no page errors including mobile", errs.length === 0, errs.join(" | "));
console.log(`Chromium ${b.version()}`);

console.log(results.join("\n"));
console.log(`${results.filter((r) => r.startsWith("PASS")).length}/${results.length} pass`);
await b.close();
if (results.some((r) => r.startsWith("FAIL"))) process.exitCode = 1;
