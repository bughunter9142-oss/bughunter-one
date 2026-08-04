# Contributing

Contributions are welcome.

## How to contribute

1. Fork the repository and create a feature branch.
2. Make your changes and add or update tests where possible.
3. Run the relevant test suite.
4. Run `python -m pytest -q --basetemp .pytest-tmp` and update documentation for user-visible changes.
5. Submit a pull request with a clear summary of the change.

## Code style

- Keep the code simple and readable.
- Use descriptive names for functions and variables.
- Prefer small, focused changes.
- Run `python -m compileall -q src` and `ruff check src tests` when the development extras are installed.
- Keep plugins failure-isolated and preserve the existing payload schema.
