# Manuscript Module Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/src/manuscript/` directory.

## Overview

The `src/manuscript/` core library dynamically maps metrics, string evaluations, and quantitative pipeline outputs directly into a series of static Markdown files within `projects/act_inf_metaanalysis/manuscript/`. This ensures the final drafted documents never fall out of sync with the underlying codebase constraints or generated data.

## Mechanics

- Calculates variables directly from the raw outputs serialized in `projects/act_inf_metaanalysis/output/`.
- Interfaces with the configurations present in `manuscript/config.yaml`.
- Executes variable substitutions employing custom tag parsing across pre-written natural language templates.

See `README.md` for human-readable integration tips.
