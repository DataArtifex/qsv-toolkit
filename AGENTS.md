# 🤖 Agent Intelligence & Project Guidance
Welcome, Agent. This document provides essential context and instructions for working on the **QSV Toolkit** (`dartfx-qsv`) project. Follow these guidelines to ensure consistency and excellence in the codebase.

---

## 🚀 Project Overview and Objectives
- See REQUIREMENTS.md

---

## 🛠 Tech Stack & Tooling

- **Language**: Python 3.12+
- **Build System**: [Hatch](https://hatch.pypa.io/)
- **Package Manager**: **`uv`** (Preferred over `pip`)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Testing**: [pytest](https://docs.pytest.org/)
- **External Dependency**: [QSV CLI](https://github.com/dathere/qsv) (Must be and available in `PATH`)

---

## 📂 Project Structure

- `src/dartfx/qsv/`: Core package directory.
- `tests/`: Project tests (managed by pytest).
- `docs/`: Sphinx based documentation.
- `AGENTS.md`: Agent Intelligence & Project Guidance.
- `REQUIREMENTS.md`: Project requirements.

---

## 📖 Development Workflow

### 📦 Package Management with `uv`
Always use `uv` for managing dependencies and environments.
- **Sync environment**: `uv pip install -e .`
- **Run scripts**: `uv run python verify_wrappers.py`
- **Run Hatch**: `uv run hatch run test`

### 🧪 Testing & Verification
- **Automated Tests**: Run `pytest` or `hatch run test`.

---

## 🧠 Agent Guidelines & Best Practices

1.  **Aesthetics & Quality**: Maintain high standards for code readability and documentation.
2.  **Pydantic Usage**: Use Pydantic v2 features (like `@computed_field` and `Field(alias=...)`) to ensure robust data modeling.
3.  **CLI Interaction**: Always check if `qsv` is available in the environment before execution (use `_run_qsv_command`).
4.  **Error Handling**: Wrap subprocess calls in try-except blocks where appropriate and provide meaningful error messages.
5.  **Schema Alignment**: Ensure that `QsvStatsDataModel` and other models exactly match the latest QSV output formats. Use `qsv <command> --json` or `--stats-jsonl` to verify output structures.

---

## 📜 Repository Rules
- Keep `src` directory structure namespaced under `dartfx`.
- Update `__about__.py` for version changes.
- Ensure all new dependencies are added to `pyproject.toml`.
