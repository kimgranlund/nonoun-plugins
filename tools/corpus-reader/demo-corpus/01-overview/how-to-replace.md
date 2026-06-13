---
title: Replacing this with a real corpus
status: working
date: 2026-06-10
type: guide
---

# Replacing this with a real corpus

Keep the conventions this demo models [INFERRED]: numbered top-level section folders (`01-…`), a root `README.md` whose H1 becomes the site title and wordmark, a frontmatter `title` + `status` per page, and an optional `reader.config.json` for the title and one-line section descriptions. Then build and serve:

```sh
python3 build-sitemap.py demo-corpus   # or your corpus folder
python3 -m http.server                 # open http://localhost:8000/
```
