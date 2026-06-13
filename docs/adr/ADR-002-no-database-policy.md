# ADR 002: No Database Policy

## Status
Accepted

## Context
Adding external databases (e.g., Postgres, Redis) complicates setup, increases costs, and hinders easy cloning of the repository.

## Decision
The project will remain completely file-based. All data is stored in static JSON/YAML files. 

## Consequences
- Zero infrastructure cost.
- Anyone can clone and run the project locally immediately.
- Scalability is bounded by file system limits and GitHub's repository limits, which is acceptable for the current scope.
