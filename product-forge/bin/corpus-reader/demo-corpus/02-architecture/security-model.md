---
title: Security model
status: active
date: 2026-06-10
type: reference
---

# Security model

Corpus markdown is untrusted [KNOWN]. The next line is a live probe — when sanitization works you see **no dialog** (DOMPurify strips the element entirely):

<script>alert("sanitization failed — this dialog should never appear")</script>

The render libraries are pinned with Subresource Integrity, and if marked or DOMPurify fails to load, prose degrades to escaped text rather than injecting raw HTML [KNOWN]. Whether the demo should also probe attribute-based vectors is [OPEN].
