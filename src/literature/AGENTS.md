# Literature Retrieval Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/src/literature/` directory.

## Overview

Mines academic papers across arXiv, Semantic Scholar, and OpenAlex. Produces a single, deduplicated canonical corpus stored as a JSONL file.

## Key Technical Decisions

- **Rate-Limit Aware**: Synchronous, carefully staggered requests using `time.sleep` mapped to specific provider policies.
- **Injectable URLs**: Each repository client accepts dependency-injected base URLs specifically to facilitate hermetic testing (e.g. against `pytest-httpserver`).
- **Resumable Downloads**: Allows partial fetches to be saved and later resumed, mitigating data loss from connection interruptions and avoiding redundant downloads.
- **Deterministic Deduplication**: Strict priority order (`DOI` > `arXiv ID` > `S2 ID` > `OpenAlex ID` > `title hash`) for synthesizing an authoritative standard.
