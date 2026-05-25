# Analysis Tests Architecture

**Archived test module** in the `projects_archive/act_inf_metaanalysis/tests/analysis/` directory.

## Overview

Tests within this directory correspond to the data structures and algorithms implemented in `src/analysis/`. They validate the bibliometric logic, TF-IDF vectorization, NMF topic modeling, temporal progression metrics, and subfield keyword classification systems.

## Key Validation Targets

- **`test_citation_network.py`**: Verifies `networkx` DiGraph construction, recursive depth mapping, and community detection outputs against local synthetic citation matrices.
- **`test_subfield_classifier.py`**: Asserts deterministic routing of papers to Domain A, B, and C targets based tightly on standard text token overlap. Validates edge cases concerning word boundaries.
- **`test_temporal_analysis.py`**: Confirms Cumulative Annual Growth Rate (CAGR) calculations, time bucket logic, and grouping.
- **`test_text_processing.py`**: Exhaustively verifies that stopwords are safely evicted and TF-IDF matrices represent correct matrix dimensions without memory leaks.
- **`test_topic_modeling.py`**: Ensures NMF decomposition correctly extracts $k$ distinct topics from synthetically biased feature spaces.

See the directory `README.md` for execution instructions.
