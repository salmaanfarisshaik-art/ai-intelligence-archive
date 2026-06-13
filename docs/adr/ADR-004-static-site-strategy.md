# ADR 004: Static Site Strategy

## Status
Accepted

## Context
We need a web portal to browse the archive, but cannot host a dynamic backend or require a database.

## Decision
We will build a custom, pure Python, deterministic static site generator that outputs raw HTML/JSON directly from our indexes.

## Consequences
- Output is directly hostable on GitHub Pages.
- Free tier hosting forever.
- Deterministic output ensures no git diff noise on unchanged pages.
