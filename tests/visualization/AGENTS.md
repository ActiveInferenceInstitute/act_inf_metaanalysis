# Visualization Tests Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/tests/visualization/` directory.

## Overview

Tests within this directory target the matplotlib figure generation pipelines housed traversing `src/visualization/`. Verification focuses on ensuring clean termination without segmentation faults, correct execution under headless display backends, and data coherence across pandas DataFrame injections.

## Key Validation Targets

- **Headless Forcing**: The internal operations utilize `matplotlib.use('Agg')` as defined in `tests/conftest.py`. This verifies figures can be produced successfully in headless CI runners without crashing to X11 display expectations.
- **`test_advanced_plots.py`**: Uses synthetically bounded dummy matrices to generate multi-axis subplots (PCA, Heatmap) and ensures the final files are saved cleanly.
- **`test_style.py`**: Confirms that aesthetic variable mappings map string labels securely to HEX constants defined natively inside `VIZ_CONFIG` to protect against missing key exceptions.

All generated PNG files are emitted cleanly to temporary directories managed automatically by the `tmp_path` fixture initialized in `conftest.py`. No files should be written to standard repositories during tests.

See the directory `README.md` for execution instructions.
