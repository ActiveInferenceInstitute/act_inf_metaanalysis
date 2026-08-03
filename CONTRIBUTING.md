# Contributing to act_inf_metaanalysis

Thanks for considering a contribution to the Active Inference Institute's
computational meta-analysis of the Active Inference and Free Energy Principle
literature. This is a **public research repository**: everything you push is
visible, so keep all contributions grounded in the actual repository state and
never include private credentials, internal paths, or personal tooling names.

## Project conventions (read these first)

- [`AGENTS.md`](AGENTS.md) — project overview, architecture, and invariant rules.
- [`doc/README.md`](doc/README.md) — documentation hub index and onboarding order.
- [`doc/architecture.md`](doc/architecture.md) — pipeline design and module map.
- [`doc/scripts.md`](doc/scripts.md) — per-script CLI reference.
- [`TODO.md`](TODO.md) — authoritative forward backlog (Minor / Medium / Major)
  with acceptance gates; check it before starting work.

## How to contribute

1. **Open an issue first** for anything non-trivial (new pipeline stage, changed
   hypothesis set, schema change) so the scope is agreed before code lands.
2. **Branch from `main`** and keep the change focused; one logical change per
   pull request.
3. **Follow the thin-orchestrator pattern.** All computation lives in `src/`;
   scripts in `scripts/` handle only I/O, argument parsing, and logging.
4. **Preserve the documented invariants** — deterministic seeds (`seed=42`),
   the 0.6 `min_confidence` extraction floor, the RDF namespace
   `http://activeinference.institute/ontology/`, and the H1–H8 alias order in
   `src/manuscript/variables.py` (which must match `STANDARD_HYPOTHESES`).
5. **Write tests without mocks.** The suite enforces a zero-mock policy: use
   `pytest-httpserver` for HTTP paths, real `Assertion` objects and real
   computations everywhere else. See `doc/testing.md`.
6. **Keep the documentation dual.** Every module you add needs its `README.md`
   (human-readable) and `AGENTS.md` (agent-facing) entries updated, plus the
   relevant `doc/` page.

## Development setup

```bash
# Python 3.12+ is required (see pyproject.toml)
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90 -q
uv run ruff check src/ scripts/ tests/
uv run mypy src/
```

The CI workflow (`.github/workflows/ci.yml`) runs exactly these three gates on
every push to `main` and on pull requests: `ruff check`, `mypy src/`, and the
pytest suite with the 90% coverage floor.

## Documentation contributions

Documentation changes are welcome and are held to the same accuracy standard as
code: every claim (test counts, corpus size, file paths, flags, schema fields)
must match the current repository state. Run the cheap validations after doc
edits (markdown link checks; `ruff`/`mypy` if Python files were touched), and
keep generated `output/` artifacts out of the diff unless the change
intentionally regenerates them.

## License

By contributing you agree that your contributions are licensed under
[CC-BY-4.0](LICENSE), matching the repository.
