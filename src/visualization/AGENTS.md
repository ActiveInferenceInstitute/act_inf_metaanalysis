# Visualization Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/src/visualization/` directory.

## Overview

Generates static, publication-ready imagery tailored for the overarching manuscript.

## Implementation Details

- **Backend**: Configured strictly for `matplotlib` utilizing the generic non-interactive `Agg` backend during tests.
- **Colorblind Safe**: Enforces a strictly-defined set of color palettes (the Okabe-Ito scheme and viridis derivatives) through `VIZ_CONFIG`.
- **Decoupled**: Fully decoupled from all computation modules (`analysis/`, `literature/`). Figure generation relies entirely on deserializing intermediate JSON data outputs.
- **Deterministic Outputs**: Explicit sizing, specific DPIs (default 300), and fixed axis bounds for reproducibility across rendering environments.
