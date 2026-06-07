/**
 * <cr-ui-nav> — the menu dropdown (sections → pages).
 *
 * Properties: `sitemap` (rendered into links), `active` (current path, for the
 * highlight), `open` (boolean, reflected). Closes on outside-click, Escape, or
 * link activation, and emits `cr:open-change` so <cr-ui-header> can sync the
 * button's aria-expanded. Navigation itself flows through `#/…` hash links.
 */
import { UIElement } from "./base.js";
import { esc, enc } from "./util.js";

export class UINav extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    active: { type: String, default: "" },
    open: { type: Boolean, default: false, reflect: true },
  };

  static template = () => null;

  #panel = null;
  #renderedSitemap = null;
  #lastOpen = false;
  #onDoc = null;
  #onKey = null;

  connected() {
    this.#panel = document.createElement("nav");
    this.#panel.className = "cr-menu-panel";
    this.#panel.setAttribute("aria-label", "All pages");
    this.#panel.hidden = true;
    this.appendChild(this.#panel);

    this.#onDoc = (e) => {
      if (!this.open) return;
      if (
        !this.#panel.contains(e.target) &&
        !(e.target.closest && e.target.closest(".cr-menu-btn"))
      )
        this.open = false;
    };
    this.#onKey = (e) => {
      if (e.key === "Escape") this.open = false;
    };
    document.addEventListener("click", this.#onDoc);
    document.addEventListener("keydown", this.#onKey);
  }

  disconnected() {
    document.removeEventListener("click", this.#onDoc);
    document.removeEventListener("keydown", this.#onKey);
  }

  render() {
    if (!this.#panel) return;
    if (this.sitemap && this.sitemap !== this.#renderedSitemap) {
      this.#renderedSitemap = this.sitemap;
      this.#renderLinks();
    }
    this.#panel.hidden = !this.open;
    this.#markActive();
    if (this.open !== this.#lastOpen) {
      this.#lastOpen = this.open;
      this.dispatchEvent(
        new CustomEvent("cr:open-change", { detail: { open: this.open } }),
      );
    }
  }

  #renderLinks() {
    const sm = this.sitemap || {};
    let html = "";
    (sm.rootPages || []).forEach((p) => {
      html +=
        "<a class='cr-mp-page cr-mp-root' href='#/" +
        enc(p.path) +
        "'>" +
        esc(p.title) +
        "</a>";
    });
    (sm.sections || []).forEach((s) => {
      html +=
        "<div class='cr-mp-sec'><div class='cr-mp-sec-title'>" +
        esc(s.title) +
        "</div>";
      (s.pages || []).forEach((p) => {
        html +=
          "<a class='cr-mp-page' href='#/" +
          enc(p.path) +
          "'>" +
          esc(p.title) +
          "</a>";
      });
      html += "</div>";
    });
    this.#panel.innerHTML = html;
    this.#panel.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        this.open = false;
      }),
    );
  }

  #markActive() {
    const want = this.active ? "#/" + enc(this.active) : null;
    this.#panel.querySelectorAll(".cr-mp-page").forEach((a) => {
      a.classList.toggle(
        "cr-active",
        Boolean(want) && a.getAttribute("href") === want,
      );
    });
  }
}

customElements.define("cr-ui-nav", UINav);
