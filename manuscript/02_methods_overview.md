# Methodology: Pipeline Design and Formal Definitions {#sec:methods}

This section describes the end-to-end computational meta-analysis pipeline. Each stage corresponds to a tested, independently executable script that reads upstream outputs and produces structured artifacts. The pipeline extends the systematic literature analysis approach of Knight et al. \citep{knight2022fep}—which combined manual annotation with ontology-based automated analysis—by substituting manual coding with fully automated, LLM-driven assertion extraction and citation-weighted hypothesis scoring. All code, configuration files, and reproducibility instructions are publicly available in the project repository (`https://github.com/docxology/act_inf_metaanalysis`); dependencies are pinned and managed with `uv` for reproducible local execution.

## Pipeline Overview

The retrieval, analysis, extraction, visualization, validation, hydration, and rendering stages are summarized in \Cref{tab:pipeline_stages}.

\begin{table}[htbp]
\centering
\caption{Nine-stage computational meta-analysis pipeline. Stages 1--5 generate the publication content; stages 6--9 provide full-text QA, deterministic validation, cross-artifact validation, and manifest closure. Each stage is independently executable and reads upstream outputs to produce structured artifacts.}
\label{tab:pipeline_stages}
\begin{tabular}{cllll}
\toprule
\textbf{Stage} & \textbf{Script} & \textbf{Primary Input} & \textbf{Primary Output} & \textbf{Section} \\
\midrule
1 & \texttt{01\_literature\_search.py} & API queries & \texttt{corpus.jsonl} & \hyperref[sec:methods_retrieval]{Retrieval} \\
2 & \texttt{02\_meta\_analysis\_pipeline.py} & \texttt{corpus.jsonl} & Classification, temporal, TF-IDF, NMF, citation network JSONs & \hyperref[sec:methods_bibliometrics]{Bibliometrics} \\
3 & \texttt{03\_build\_knowledge\_graph.py} & \texttt{corpus.jsonl} & \texttt{nanopublications.jsonl}, \texttt{nanopublications.trig}, scores & \hyperref[sec:methods_kg]{Knowledge Graph} \\
4 & \texttt{04\_generate\_figures.py} & All Stage 2--3 JSONs & {{NUM_FIGURES}} publication-ready PNGs & \hyperref[sec:methods_viz]{Visualization} \\
5 & \texttt{z\_generate\_manuscript\_variables.py} & All output JSONs & Rendered manuscript Markdown & \hyperref[sec:methods_viz]{Injection} \\
6 & \texttt{06\_fulltext\_assessment.py} & \texttt{corpus.jsonl} & Full-text availability report & QA \\
7 & \texttt{07\_run\_validation\_study.py} & Nanopubs + corpus & Rule-reference agreement metrics & Validation \\
8 & \texttt{08\_validate\_artifacts.py} & All current artifacts & Cross-artifact contract report & Validation \\
9 & \texttt{09\_write\_pipeline\_manifest.py} & Inputs + gate reports & Hashes, counts, versions, gate results & Provenance \\
\bottomrule
\end{tabular}
\end{table}

Scripts act as thin orchestrators that import methods from tested library modules and handle file I/O. All computation resides in the `src/` packages; no analysis logic is embedded in scripts. End-to-end pipeline execution completes in under one hour on commodity hardware (excluding LLM extraction, which depends on model size and inference backend); all stochastic components use fixed random seeds for deterministic reproduction.

## Reproducible Build Infrastructure

The analysis pipeline described above is embedded within `template/` \citep{Friedman2026TemplateReproducibleGenerative, FriedmanTemplateSoftware}, an open-source Infrastructure-as-Code system for computational research that turns a full research compendium—code, data, tests, manuscript, and provenance—into a single, version-controlled, deterministically buildable repository with an enforced, test-gated publication pipeline. `template/` applies the principle of Infrastructure as Code to the research lifecycle, making the manuscript, test suite, and provenance chain independently verifiable. The system operationalizes FAIR4RS principles \citep{wilkinson2016fair} and supply-chain-style provenance for manuscripts, targeting structural causes of the reproducibility crisis: fragmented workflows across LaTeX, notebooks, and ad-hoc scripts, lack of end-to-end testing, and no binding between code, data, figures, and the final PDF.

The system employs a Two-Layer Architecture: a globally shared *infrastructure layer* provides generic services—logging, rendering, validation, reporting, and LLM integration—while self-contained *project workspaces* carry their own `manuscript/`, `scripts/`, `src/`, `tests/`, `data/`, and `output/` directories. The tested build runs analysis, deterministic validation, PDF/HTML rendering, and output validation. A Zero-Mock testing policy requires tests to exercise real filesystem operations, real subprocess calls, and real computation. Cryptographic provenance is recorded in generated artifacts, and the `template/` framework supplies the shared rendering and validation methods. The project is available under the MIT License at `https://github.com/docxology/act_inf_metaanalysis`.
