# CLAUDE.md - Project Context

This file contains project-specific context for Claude Code.

## Project Overview
PDFium build system for multiple platforms (iOS, macOS, Android, WASM) with Python-based build tools.

## Development Commands
- Testing: `poetry run test` or `poetry run tests`
- Linting: `black modules/` (Python code formatter)
- Type checking: Not configured yet
- Install dependencies: `poetry install`

## Testing Infrastructure
- Framework: pytest with coverage reporting
- Test structure: `tests/unit/` and `tests/integration/`
- Coverage threshold: 80% (configurable in pyproject.toml)
- Test markers: @pytest.mark.unit, @pytest.mark.integration, @pytest.mark.slow

## Notes
- Poetry is used for Python dependency management
- Testing infrastructure configured with pytest, pytest-cov, and pytest-mock
- Coverage reports generated in HTML and XML formats

