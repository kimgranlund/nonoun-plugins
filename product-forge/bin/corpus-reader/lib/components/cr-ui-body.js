/**
 * <cr-ui-body> — the `toc | content` grid under the header.
 *
 * Holds <cr-ui-toc> (column 1) and <cr-ui-page> (column 2), forwards
 * `sitemap`/`route` to the page, toggles `.cr-home` (single column) when there
 * is no route, and pipes the page's `cr:page` headings into the toc.
 */
import { UIElement } from "./base.js";

export class UIBody extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    route: { type: String, default: "" },
  };

  static template = () => null;

  #main = null;
  #toc = null;
  #page = null;
  #built = false;

  connected() {
    this.#build();
  }

  #build() {
    if (this.#built) return;
    this.#built = true;

    this.#main = document.createElement("main");
    this.#main.className = "cr-body";
    this.#toc = document.createElement("cr-ui-toc");
    this.#page = document.createElement("cr-ui-page");
    this.#main.append(this.#toc, this.#page);
    this.appendChild(this.#main);

    this.#page.addEventListener("cr:page", (e) => {
      if (this.#toc) this.#toc.headings = e.detail.headings;
    });
  }

  render() {
    this.#build();
    this.#main.classList.toggle("cr-home", !this.route);
    if (this.#page) {
      this.#page.sitemap = this.sitemap;
      this.#page.route = this.route || "";
    }
  }
}

customElements.define("cr-ui-body", UIBody);
