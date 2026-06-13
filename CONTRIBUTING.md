# Contributing to AI Intelligence Archive

We welcome contributions to the AI Intelligence Archive!

## How to Contribute
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Ensure you follow our pipeline rules:
   - No parallel execution in Phase 1 modules.
   - All modules must inherit `BaseSync`.
   - Idempotency and Determinism are 10/10 requirements.
4. Commit your changes (`git commit -m 'Add some amazing feature'`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request.

## Environment Setup
See the `README.md` for setup instructions. Make sure to run `pytest` before submitting a PR.
