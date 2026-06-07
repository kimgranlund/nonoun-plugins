/**
 * <cr-shell> — the app root.
 *
 * Loads lib/sitemap.json, owns the hash route, and composes <cr-ui-header> +
 * <cr-ui-body>, pushing `sitemap` + `route` down to them. Navigation flows
 * through `#/<path>` links anywhere in the tree; the shell listens for
 * `hashchange` and re-routes.
 */
import { UIElement } from "./base.js";
import { esc } from "./util.js";

export class UIShell extends UIElement {
  static template = () => null;

  #header = null;
  #body = null;
  #sitemap = null;
  #onHash = null;

  connected() {
    this.#header = document.createElement("cr-ui-header");
    this.#body = document.createElement("cr-ui-body");
    this.append(this.#header, this.#body);

    this.#onHash = () => {
      if (this.#sitemap) this.#route();
    };
    window.addEventListener("hashchange", this.#onHash);

    fetch("lib/sitemap.json")
      .then((r) => {
        if (!r.ok) throw new Error("lib/sitemap.json — " + r.status);
        return r.json();
      })
      .then((sm) => {
        this.#sitemap = sm;
        document.title = sm.title || "Corpus";
        this.#header.sitemap = sm;
        this.#body.sitemap = sm;
        this.#route();
      })
      .catch((err) => this.#bootError(err));
  }

  disconnected() {
    window.removeEventListener("hashchange", this.#onHash);
  }

  #route() {
    const h = location.hash.replace(/^#\/?/, "").split("::")[0];
    const path = h ? decodeURIComponent(h) : "";
    this.#header.route = path;
    this.#body.route = path;
  }

  #bootError(err) {
    this.innerHTML =
      "<div class='cr-error' style='max-width:40rem;margin:0 auto;padding:2rem'>" +
      "<h1>Could not load the corpus</h1><p>" +
      esc(err.message) +
      "</p><p>The reader uses <code>fetch()</code>, which browsers block on <code>file://</code> — serve the folder over HTTP. From here run:</p>" +
      "<pre>python3 -m http.server</pre><p>then open <code>http://localhost:8000/</code>. If <code>lib/sitemap.json</code> is missing, generate it first: <code>python3 build-sitemap.py</code></p></div>";
  }
}

customElements.define("cr-shell", UIShell);
