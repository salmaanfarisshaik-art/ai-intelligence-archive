# ADR 0003: Static Frontend Contract

## Status
Accepted

## Context
The visualization UI needs to be hosted affordably and reliably without maintenance overhead.

## Decision
The Phase 10 frontend must be 100% statically exported (`output: "export"` in Next.js). It consumes generated JSON artifacts exclusively.

## Consequences
- No server-side rendering (SSR) or live APIs are allowed.
- Deploys natively to GitHub Pages.
