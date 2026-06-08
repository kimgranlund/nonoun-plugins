/**
 * <cr-ui-header> — the sticky left sidebar: [ wordmark / nav ].
 *
 * Properties: `sitemap` (wordmark subtitle + passed to the nav) and `route`
 * (passed to the nav for the active highlight). Renders an <aside class="cr-side">
 * rail holding the BZZR wordmark and a persistent <cr-ui-nav> list (no dropdown).
 */
import { UIElement } from "./base.js";

export class UIHeader extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    route: { type: String, default: "" },
  };

  static template = () => null;

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

    const brand = document.createElement("a");
    brand.className = "cr-side-brand";
    brand.href = "#/";
    brand.setAttribute("aria-label", "Home");
    brand.innerHTML =
      "<span class='cr-brand-dot' aria-hidden='true'></span>" +
      "<b>BZZR</b><span class='cr-side-sub'></span>";
    this.#subEl = brand.querySelector(".cr-side-sub");

    this.#nav = document.createElement("cr-ui-nav");

    side.append(brand, this.#nav);
    this.append(side);
  }

  render() {
    this.#build();
    if (this.#subEl) {
      const t = this.sitemap?.title || "Corpus";
      this.#subEl.textContent = t.replace(/^BZZR\s*/i, "") || t;
    }
    if (this.#nav) {
      this.#nav.sitemap = this.sitemap;
      this.#nav.active = this.route;
    }
  }
}

customElements.define("cr-ui-header", UIHeader);
