/**
 * <cr-ui-header> — the sticky left sidebar: [ wordmark / nav ].
 *
 * Properties: `sitemap` (wordmark subtitle + passed to the nav) and `route`
 * (passed to the nav for the active highlight). Renders an <aside class="cr-side">
 * rail holding the corpus wordmark (derived from the sitemap title — no hardcoded
 * brand) and a persistent <cr-ui-nav> list (no dropdown).
 */
import { UIElement } from "./base.js";

export class UIHeader extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    route: { type: String, default: "" },
  };

  static template = () => null;

  #leadEl = null;
  #subEl = null;
  #nav = null;
  #built = false;

  connected() {
    this.#build();
  }

  #build() {
    if (this.#built) return;
    this.#built = true;

    const side = document.createElement("aside");
    side.className = "cr-side";
    side.setAttribute("aria-label", "Corpus navigation");

    const header = document.createElement("div");
    header.className = "cr-side-header";

    const brand = document.createElement("a");
    brand.className = "cr-side-brand";
    brand.href = "#/";
    brand.setAttribute("aria-label", "Home");
    brand.innerHTML =
      "<span class='cr-brand-dot' aria-hidden='true'></span>" +
      "<b class='cr-side-lead'></b><span class='cr-side-sub'></span>";
    this.#leadEl = brand.querySelector(".cr-side-lead");
    this.#subEl = brand.querySelector(".cr-side-sub");

    const search = document.createElement("input");
    search.className = "cr-search";
    search.type = "search";
    search.placeholder = "Search documents…";
    search.autocomplete = "off";
    search.setAttribute("aria-label", "Search documents");
    search.addEventListener("input", () => {
      if (this.#nav && this.#nav.filter) this.#nav.filter(search.value);
    });

    header.append(brand, search);
    this.#nav = document.createElement("cr-ui-nav");

    side.append(header, this.#nav);
    this.append(side);
  }

  render() {
    this.#build();
    // Wordmark from the corpus title: bold lead word + muted remainder — generic, no
    // hardcoded brand. "Acme Product Corpus" → "Acme" / "Product Corpus"; a leading
    // separator on the remainder is dropped ("Acme — Docs" → "Acme" / "Docs").
    const title = this.sitemap?.title || "Corpus";
    const sp = title.indexOf(" ");
    if (this.#leadEl) this.#leadEl.textContent = sp > 0 ? title.slice(0, sp) : title;
    if (this.#subEl)
      this.#subEl.textContent = sp > 0 ? title.slice(sp + 1).replace(/^[\s—–|:·-]+/, "") : "";
    if (this.#nav) {
      this.#nav.sitemap = this.sitemap;
      this.#nav.active = this.route;
    }
  }
}

customElements.define("cr-ui-header", UIHeader);
