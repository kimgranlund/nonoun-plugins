/**
 * <cr-ui-diagram-viewer code="graph TD; A-->B"> — renders one mermaid diagram.
 *
 * Created by <cr-ui-page> in place of each ```mermaid fenced block. mermaid is a
 * global (loaded from CDN); if it's absent, the source is shown verbatim as a
 * fallback so a diagram never becomes a blank gap.
 */
import { UIElement } from "./base.js";

let mermaidReady = false;
let seq = 0;

function ensureMermaid() {
  if (mermaidReady || !window.mermaid) return Boolean(window.mermaid);
  try {
    const dark =
      window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches;
    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: dark ? "dark" : "default",
      // Pin Mermaid's measuring font to the body font so labels are sized against the font
      // that actually renders — otherwise a late web-font swap widens text past the
      // pre-measured node box and clips labels. securityLevel stays "strict" (no htmlLabels).
      fontFamily: getComputedStyle(document.body).fontFamily,
      flowchart: { useMaxWidth: true, padding: 16 },
      sequence: { useMaxWidth: true, wrap: true },
    });
  } catch (e) {
    /* mermaid optional */
  }
  mermaidReady = true;
  return true;
}

export class UIDiagramViewer extends UIElement {
  static properties = {
    code: { type: String, default: "" },
  };

  static template = () => null;

  #rendered = null;

  render() {
    const code = this.code || "";
    if (code === this.#rendered) return;
    this.#rendered = code;
    this.innerHTML = "";
    if (!code.trim()) return;

    const host = document.createElement("div");
    host.className = "mermaid";
    host.textContent = code;
    this.appendChild(host);

    if (!window.mermaid) return; // fallback: the source text stays visible
    ensureMermaid();
    // Render only once web fonts have loaded: Mermaid measures label widths synchronously, so
    // rendering before the body font is ready sizes nodes against fallback metrics and clips
    // labels when the real font swaps in. document.fonts.ready resolves immediately once fonts
    // are loaded (the common case after first paint), so this is a no-op then. The #rendered
    // guard drops a stale async result if the component re-rendered while fonts were loading.
    const draw = () => {
      try {
        window.mermaid
          .render("cr-mmd-" + ++seq, code)
          .then(({ svg }) => {
            if (this.#rendered === code) host.innerHTML = svg;
          })
          .catch(() => {
            if (this.#rendered === code) host.textContent = code;
          });
      } catch (e) {
        host.textContent = code;
      }
    };
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
    else draw();
  }
}

customElements.define("cr-ui-diagram-viewer", UIDiagramViewer);
