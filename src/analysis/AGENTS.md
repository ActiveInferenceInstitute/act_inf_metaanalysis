# Analysis Module Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/src/analysis/` directory.

## Overview

This module is responsible for analyzing the deduplicated paper corpus. It computes all necessary metrics (bibliometrics, network topology, temporal rates) required for the manuscript results.

## Key Capabilities

- **Topic Extraction**: Extracts configurable number of latent topics using Non-negative Matrix Factorization (NMF).
- **Network Metrics**: Uses greedy modularity community detection and computing centrality measures (PageRank, in-degree) on the citation graph.
- **Taxonomy Mapping**: Employs an exact and boundary-aware keyword matching hierarchy to map unstructured papers to the formal 8-domain taxonomy.
- **Growth Modeling**: Computes accurate compound annual growth rate (CAGR) and doubling times ($t_d$).
