/**
 * <cr-ui-nav> — the persistent sidebar nav (sections → pages).
 *
 * Properties: `sitemap` (rendered into links) and `active` (current path, for the
 * highlight). Renders an always-visible <nav class="cr-side-nav"> list inside the
 * sidebar rail — no dropdown, no toggle. Navigation flows through `#/…` hash links.
 */
import { UIElement } from "./base.js";
import { esc, enc } from "./util.js";

export class UINav extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    active: { type: String, default: "" },
  };

  static template = () => null;

  #nav = null;
  #renderedSitemap = null;

  connected() {
    this.#nav = document.createElement("nav");
    this.#nav.className = "cr-side-nav";
    this.#nav.setAttribute("aria-label", "All pages");
    this.appendChild(this.#nav);
  }

  render() {
    if (!this.#nav) return;
    if (this.sitemap && this.sitemap !== this.#renderedSitemap) {
      this.#renderedSitemap = this.sitemap;
      this.#renderLinks();
    }
    this.#markActive();
  }

  #renderLinks() {
    const sm = this.sitemap || {};
    let html = "";
    (sm.rootPages || []).forEach((p) => {
      html +=
        "<a class='cr-nav-link cr-nav-root' href='#/" +
        enc(p.path) +
        "'>" +
        esc(p.title) +
        "</a>";
    });
    (sm.sections || []).forEach((s) => {
      html +=
        "<div class='cr-nav-group'><div class='cr-nav-group-title'>" +
        esc(s.title) +
        "</div>";
      (s.pages || []).forEach((p) => {
        html +=
          "<a class='cr-nav-link' href='#/" +
          enc(p.path) +
          "'>" +
          esc(p.title) +
          "</a>";
      });
      html += "</div>";
    });
    this.#nav.innerHTML = html;
  }

  #markActive() {
    const want = this.active ? "#/" + enc(this.active) : null;
    this.#nav.querySelectorAll(".cr-nav-link").forEach((a) => {
      a.classList.toggle(
        "cr-active",
        Boolean(want) && a.getAttribute("href") === want,
      );
    });
  }
}

customElements.define("cr-ui-nav", UINav);
