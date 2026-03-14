---
title: Frameworks
description: Framework analyzers supported by Zen of Languages and how they fit into the language-centric architecture.
icon: material/layers
tags:
  - Frameworks
  - Routing
---

# Frameworks

Zen of Languages is still fundamentally organized around **language keys**, but several ecosystems are important enough to expose as first-class framework analyzers.

That means framework support is modeled as dedicated analyzers such as `react`, `fastapi`, or `django`, with their implementation modules now living under `frameworks/<key>/...` while still plugging into the same registry, detector, and documentation pipeline.

## Supported Framework Analyzers

### Frontend

- [React](../languages/react.md)
- [Vue](../languages/vue.md)
- [Angular](../languages/angular.md)
- [Next.js](../languages/nextjs.md)

### Python ecosystem

- [Pydantic](../languages/pydantic.md)
- [FastAPI](../languages/fastapi.md)
- [Django](../languages/django.md)
- [SQLAlchemy](../languages/sqlalchemy.md)

## Detection Model

Framework routing is intentionally conservative:

- high-confidence file extensions like `.vue` route automatically
- strong file-name or project markers can route files such as Next.js pages
- import-based heuristics can elevate Python files into framework analyzers
- ambiguous files can still be analyzed by choosing `--language <framework>` explicitly

## Why frameworks have their own namespace

The repository now distinguishes between core language analyzers and framework analyzers:

- core languages continue to live under `languages/<key>/...`
- framework analyzers live under `frameworks/<key>/...`

Shared loaders, docs generators, and validation scripts understand both namespaces, which keeps framework support explicit without breaking the rest of the product.
