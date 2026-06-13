/**
 * corpus-reader — component barrel.
 *
 * Importing this module registers every <cr-*> custom element. The page only
 * needs `<cr-shell>` in the body; it boots itself on connect (loads the sitemap,
 * wires the hash router, composes the rest).
 *
 * Architecture:
 *   <cr-shell>                        app root — sitemap + routing
 *     <cr-ui-header>                  sticky [ brand | Menu ]
 *       <cr-ui-nav>                   the menu dropdown
 *     <cr-ui-body>                    the toc | content grid
 *       <cr-ui-toc>                   per-page table of contents
 *       <cr-ui-page>                  home tiles, or a rendered markdown page
 *         <cr-ui-diagram-viewer>      a mermaid diagram
 *
 * Built on the vendored reactive light-DOM base (components/base.js — signals +
 * UIElement, zero dependencies). Presentation lives in corpus-reader.css; only
 * structure + behaviour are here. Order matters only in that the shell is last.
 */
import "./components/cr-ui-diagram-viewer.js";
import "./components/cr-ui-toc.js";
import "./components/cr-ui-page.js";
import "./components/cr-ui-nav.js";
import "./components/cr-ui-header.js";
import "./components/cr-ui-body.js";
import "./components/cr-shell.js";
