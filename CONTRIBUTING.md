# Contributing to Paryavaran

Thank you for your interest in contributing to the Paryavaran Carbon Footprint Tracker! We welcome contributions to make carbon tracking more accessible, performant, and reliable.

## Code of Conduct

By participating, you agree to maintain a respectful, inclusive, and collaborative environment.

## Development Workflow

1. Fork the repository and create your branch from `main`.
2. Setup the virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Implement your changes.
4. Write tests for your features or bug fixes.
5. Ensure all tests pass and coverage is above 90%:
   ```bash
   pytest --cov=src tests/
   ```
6. Follow strict type annotation standards (verify using `mypy`).

## Commit Message Guidelines

We follow a structured commit message format to maintain a clean git history:

- `feat: <description>` for new features (e.g. `feat: implement carbon footprint calculator`)
- `fix: <description>` for bug fixes (e.g. `fix: improve accessibility compliance`)
- `refactor: <description>` for code changes that neither fix bugs nor add features
- `test: <description>` for adding or correcting tests
- `docs: <description>` for documentation adjustments

## Pull Request Process

- Ensure the branch builds successfully and all linting/tests pass.
- Update `README.md` if your change introduces new configurations or endpoints.
- Submit your pull request, linking to the relevant issue.
