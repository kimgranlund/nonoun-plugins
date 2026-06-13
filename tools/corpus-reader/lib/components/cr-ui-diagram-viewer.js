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
    try {
      window.mermaid
        .render("cr-mmd-" + ++seq, code)
        .then(({ svg }) => {
          host.innerHTML = svg;
        })
        .catch(() => {
          host.textContent = code;
        });
    } catch (e) {
      host.textContent = code;
    }
  }
}

customElements.define("cr-ui-diagram-viewer", UIDiagramViewer);
