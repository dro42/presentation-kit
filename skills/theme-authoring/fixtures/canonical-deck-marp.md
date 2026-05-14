---
marp: true
theme: hcw
paginate: true
footer: '© 2026 brand-spec test deck'
---

<!-- _class: lead -->
<!-- _paginate: false -->

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

<!-- _class: invert -->

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

<!-- _class: invert -->

# Thank you.

Generated from `hcw-brand.yaml` via `/new-theme`.
