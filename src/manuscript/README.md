# Manuscript Template Engine (`src/manuscript/`)

Logic mapping computationally derived pipeline outputs (such as JSON arrays and CSV totals) cleanly into Markdown evaluation tags.

## Usage

This module is called exclusively through `scripts/05_inject_variables.py`. It is responsible for filling the variable tags (e.g. `{{CORPUS_SIZE}}`) found inside `manuscript/` documentation files with the accurate parameters gathered dynamically.

## Structure

- **`variables.py`**: The mapping lookup table logic calculating pipeline metrics into strings ready for manuscript injection.

Refer to **[AGENTS.md](AGENTS.md)** for data flow architectural context.
