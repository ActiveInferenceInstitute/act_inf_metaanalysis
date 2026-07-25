# Test Suite Architecture

**Archived test module** in the `projects_archive/act_inf_metaanalysis/tests/` directory.

## Overview

This directory houses the comprehensive test suite for the Active Inference Meta-Analysis project. The suite enforces the **Zero-Mock Testing Philosophy**, relying on actual data transformations, HTTP test servers, and localized fixture generation rather than object mocking. The current verified gate is maintained in `doc/testing.md` rather than duplicated here.

## Architecture

- **`conftest.py`**: Central repository for shared Pytest fixtures. Implements temporary directories, structured test logging, `matplotlib` Agg backend forcing (to prevent window spawning during tests), and provides dummy text corpora for analysis verification.
- **Fixture Strategy**: All module-specific suites request `conftest.py` resources, ensuring side-effect-free execution and rapid teardown.
- **`pytest-httpserver`**: Used extensively in `literature/` tests to proxy remote semantic APIs without making outbound calls or using `MagicMock`.

## Coverage Goals

- Current coverage strictly maintains ≥90% instruction line execution; the latest measured result is recorded in `doc/testing.md`.
- All new features implemented in `src/` MUST be accompanied by equivalent tests in the corresponding `tests/` subdirectory.

## Sub-Modules

- **`test_config_loader.py`** (root): YAML load paths, manuscript default path, ImportError fallback when PyYAML is unavailable.
- **`test_variables.py`**, **`test_scripts.py`**: Manuscript variable injection and script entry-point integration.
