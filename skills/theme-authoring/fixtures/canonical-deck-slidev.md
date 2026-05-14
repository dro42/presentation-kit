---
# Canonical 6-slide Slidev fixture for the theme-authoring smoke test.
#
# Mirrors fixtures/canonical-deck-marp.md — same six slides exercise the
# same brand surfaces (h1/h2, bullets, section divider, code block, table,
# inverted closing). The theme: directive points at a generated directory
# placed alongside this file:
#
#   cp -R <generated>/slidev/slidev-theme-hcw <here>/
#   npx slidev fixtures/canonical-deck-slidev.md
#
theme: ./slidev-theme-hcw
title: Generated theme test
info: Verifying brand projection — generated from hcw-brand.yaml
author: Andreas Drozd
date: 2026-05-14
---

# Generated theme test

## Verifying brand projection

Andreas Drozd · 14 May 2026

---

# Bullets and emphasis

The 6-slide canonical deck exercises every variant the generator emits:

- Title slide (lead variant)
- Section divider (invert variant)
- Bullet body
- Code block
- Table
- Inverted closing slide

Use *italic* for emphasis, **bold** for terms, and `inline code` for identifiers.

---
layout: section
---

# Section: Visual surface

## Inverted slides for section dividers

---

# Code block

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: theme-authoring-test
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test
```

Note the brand-color inline `code` and the brand-color left rule on the block.

---

# Tables

| Token        | Value      | Where it lives                |
|--------------|------------|-------------------------------|
| primary      | `#36566D`  | h1, brand surfaces, code rule |
| secondary    | `#4B5059`  | h2, body emphasis             |
| primary_soft | `#7897AC`  | h3, subtitles                 |

Header rows carry the brand-primary underline.

---
layout: section
---

# Thank you.

Generated from `hcw-brand.yaml` via `/new-theme`.
