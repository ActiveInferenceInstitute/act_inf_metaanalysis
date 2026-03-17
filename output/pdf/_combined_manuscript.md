# Abstract

The Free Energy Principle (FEP) and Active Inference have expanded rapidly across neuroscience, robotics, biology, and formal mathematics—supported by new theoretical foundations in Bayesian mechanics and path-integral formulations. However, the field faces a dual challenge: the sheer volume of publications makes systematic synthesis difficult, while the FEP's theoretical generality has invited falsifiability critiques, since its core claim can be applied to any self-organizing system without clearly distinguishing itself from alternatives. Both challenges point to the same methodological gap: a lack of systematic, hypothesis-specific evidence profiling across the field's core claims. Building on the systematic literature analysis of Knight, Cordes, and Friedman \citep{knight2022fep}—which pioneered manual annotation paired with ontology-based analysis at the scale of hundreds of papers—we present a computational meta-analysis framework that automates and scales this approach. Our pipeline retrieves literature from arXiv, Semantic Scholar, and OpenAlex, deduplicating records via a canonical identifier hierarchy. It classifies papers into a three-tier taxonomy spanning eight categories: A (Core Theory), B (Tools \& Translation), and C (Application Domains). To transcend keyword matching, an LLM-powered extraction system evaluates each abstract against eight core hypotheses, producing structured nanopublications with directionality, confidence scores, and natural-language reasoning. These nanopublications populate an RDF-compatible knowledge graph evaluated by a citation-weighted evidence scoring function.

Applied to a corpus of $N = 849$ papers (spanning 2005–2026), the framework details a field dominated by core theory (Domain A) but actively diversifying into tools development (Domain B)—including pymdp, RxInfer.jl, and interpretable alternatives such as Free Energy Projective Simulation—and specific applications (Domain C), notably neuroscience, robotics, and computational psychiatry. Non-negative matrix factorization identifies five latent topics that cross-cut the keyword domain taxonomy, while citation network analysis reveals a sparse yet structured graph (1,678 intra-corpus edges, 5.5\% reference resolution) anchored by pronounced hub papers. By demonstrating that automated LLM-driven assertion extraction can generate scalable, queryable representations of scientific evidence, this work provides a robust architectural foundation for *living literature reviews*. Such continuously updated knowledge graphs can track the trajectory of theoretical consensus across rapidly evolving fields, within Active Inference and beyond.

**Keywords:** Active Inference, Free Energy Principle, meta-analysis, knowledge graph, nanopublications, bibliometrics, hypothesis scoring, LLM extraction, computational neuroscience



```{=latex}
\newpage
```


# Introduction: Evidence Gaps in a Rapidly Expanding Field

## The Free Energy Principle and Active Inference Framework

The Free Energy Principle (FEP), introduced by Karl Friston, proposes that self-organizing systems maintain their structural and functional integrity by minimizing variational free energy—an upper bound on sensory surprise \citep{friston2006free, friston2010free}. Under this principle, living systems are cast as approximate Bayesian inference engines that build generative models of their environment and act to reduce the discrepancy between predicted and observed states. Active Inference (AIF) extends this picture from passive perception to goal-directed behavior: agents select actions that bring about observations consistent with their preferred states, unifying perception, learning, and decision-making within a single variational framework \citep{parr2022active, friston2017active}. Since its initial formulation for sensorimotor control, AIF has been applied to navigation, visual foraging, language comprehension, social cognition, and multi-agent coordination. Bayesian mechanics \citep{sakthivadivel2023bayesian} has further strengthened the mathematical foundations of the FEP by grounding Markov blanket dynamics in the physics of belief-based systems, placing the principle on a footing commensurate with established physical theories. Importantly, the variational free energy minimization at the core of the FEP shares deep mathematical connections with the broader family of Energy-Based Models (EBMs) \citep{lecun2006tutorial}—including Helmholtz machines \citep{dayan1995helmholtz}, Boltzmann machines \citep{hinton2002training}, and variational autoencoders \citep{kingma2014auto}—all of which parameterize learning and inference through scalar energy functions and variational bounds. This convergence motivates the inclusion of EBM-adjacent literature in our search scope.

## Challenges Posed by Rapid Literature Growth

The active inference literature has grown at a compound annual rate of 16.99\% across 2005--2026, with annual output accelerating sharply after 2013. While early research concentrated on theoretical neuroscience, the field has since diversified across biology (C5), robotics (C2), computational psychiatry (C4), algorithm scaling (B), and formal mathematics (A1). This multi-disciplinary expansion creates three interrelated challenges. First, tracking which core theoretical claims—such as FEP universality or the physical realism of Markov blankets—are well-supported, contested, or merely assumed becomes increasingly difficult as the corpus grows. Second, because the relationship between mathematical formalisms and empirical evidence is frequently implicit, systematic evidence synthesis demands substantial manual effort. Third, new entrants must navigate a literature weighted toward broad qualitative philosophy (A2), interspersed with specialized applied subfields.

Traditional narrative reviews attempt to address these challenges but are static, subjective, and quickly outdated. Systematic reviews from evidence-based medicine offer rigorous aggregation but are structured for clinical trial data with homogeneous outcome measures, making them less suited for the heterogeneous ontological and computational claims in this literature. The expansion of predictive processing \citep{clark2013whatever, hohwy2013predictive} and the emergence of Bayesian mechanics \citep{sakthivadivel2023bayesian} further broaden the scope of assertions that a comprehensive meta-analysis must reconcile. Critically, the falsifiability of the FEP itself remains contested \citep{colombo2021free}: because free energy minimization can be reframed to accommodate any behavior post hoc, distinguishing genuine predictive commitment from tautological redescription requires exactly the hypothesis-specific, evidence-quantified framework we propose here.

## Related Work and Prior Meta-Analyses

Several prior efforts have surveyed aspects of the Active Inference landscape. Sajid et al. \citep{sajid2021active} compare active inference with alternative decision-making frameworks; Da Costa et al. \citep{dacosta2020active} synthesize the discrete-state-space formulation; Lanillos et al. \citep{lanillos2021active} survey robotics applications; Smith et al. \citep{smith2021computational} provide a tutorial bridging theory and empirical data; and Millidge et al. \citep{millidge2021understanding} examine information-theoretic foundations of exploration behavior. Ramstead et al. \citep{ramstead2018answering} extend the FEP to questions of biological self-organization, while Pezzulo et al. \citep{pezzulo2015active} connect active inference to homeostatic regulation. Millidge \citep{millidge2024retrospective} provides a practitioner's retrospective confirming that AIF's strongest demonstrated results arise from novel discrete generative models, while scalability relative to deep reinforcement learning remains the field's central open challenge.

Closest to our work, Knight, Cordes, and Friedman \citep{knight2022fep} conducted a systematic literature analysis of publications using the terms "Free Energy Principle" or "Active Inference," with an emphasis on works by Karl J. Friston. Their analysis—maintained by the Active Inference Institute—combined manual annotation of structural, visual, and mathematical features with automated analyses using the Active Inference Ontology at the scale of thousands of citations and hundreds of annotated papers. That study identified six development directions—including broader scope, richer annotation, and transferable approaches—and represents an important precursor to automated meta-analysis of this field.

These works are primarily narrative reviews: they synthesize qualitative findings but do not strictly quantify the balance of evidence across the field's central claims. The systematic analysis of Knight et al. \citep{knight2022fep} pioneered quantitative literature analysis for this field using manual annotation and ontology-based automated analysis. Our framework advances this line of work by (1) fully automating assertion extraction via LLM-based hypothesis scoring, (2) constructing a structured, RDF-compatible knowledge graph scored by citation-weighted evidence, and (3) tracking how evidence for core claims evolves over time through temporal trend analysis.

## Synergizing Knowledge Graphs and LLMs

Recent systematic literature initiatives underscore a powerful reciprocal synergy between Large Language Models (LLMs) and Knowledge Graphs: LLMs parse unstructured text to rapidly extract semantic claims, efficiently populating the structured, queryable architecture of the graph \citep{quevedo2025combining, li2024unifying}. We adopt the *nanopublication* \citep{groth2010anatomy}—a minimal, machine-readable unit of scientific evidence comprising a core assertion bound to explicit provenance metadata—as the fundamental serialization format for this extracted knowledge.

## This Study: Approach and Overview

This paper presents a computational meta-analysis of the Active Inference literature ($N = 849$). Rather than relying exclusively on bibliometric metadata or slow manual coding, we deploy a Large Language Model (LLM) to "read" each paper's abstract and assess its relationship to eight core hypotheses within the FEP paradigm. We serialize these assessments as nanopublications—each encoding an assertion ("Paper X supports Hypothesis Y") coupled with the LLM's natural-language reasoning and confidence score. The resulting knowledge graph aggregates these nanopublications and links them to paper metadata, citation networks, subfield classifications, and hypothesis definitions. A citation-weighted scoring formula quantifies the net evidence for or against each hypothesis, producing scores in $[-1, 1]$ that reflect both the direction and strength of published evidence.

## Research Questions

This meta-analysis addresses four primary research questions:

1. **RQ1 (Field Structure):** What is the disciplinary structure and growth trajectory of the Active Inference literature, and how are papers distributed across the three domains—Core Theory (A), Tools & Translation (B), and Application Domains (C)?
2. **RQ2 (Growth Dynamics):** What are the temporal growth dynamics of the field, and which subfields are experiencing the most rapid expansion?
3. **RQ3 (Hypothesis Evidence):** What is the current balance of evidence for and against the eight standard hypotheses, and how has this balance evolved over time? (See hypothesis dashboard and assertion figures in the \hyperref[sec:hypothesis_results]{hypothesis results}.)
4. **RQ4 (Tooling Readiness):** What is the state of software tooling and infrastructure for Active Inference research, and what gaps remain?

## Scope and Delimitations

This study focuses on the English-language peer-reviewed and preprint literature retrievable from arXiv, Semantic Scholar, and OpenAlex. Our search scope begins at 2005—chosen to capture Energy-Based Model and variational Bayesian antecedents (Helmholtz machines, VAEs, early Bayesian brain formulations \citep{dayan1995helmholtz, lecun2006tutorial}) that share deep mathematical foundations with variational free energy minimization and predated the Free Energy Principle label introduced in 2006 \citep{friston2006free}. The scope includes both the core Active Inference and Free Energy Principle literature and adjacent Energy-Based Model research where it intersects with variational inference or generative modeling—capturing the growing convergence between these traditions. We do not include book chapters or monographs not indexed by these sources, software documentation, or non-English publications. Domain classification uses keyword matching rather than expert annotation—a deliberate trade-off favoring reproducibility over precision, whose consequences we quantify in the \hyperref[sec:field_overview]{field overview}. Hypothesis scoring relies on LLM-extracted assertions; the fidelity and limitations of this approach are examined in the \hyperref[sec:extraction_pipeline]{extraction pipeline section}. The hypothesis definitions and domain taxonomy are informed by, but not identical to, the Active Inference Ontology used by Knight et al. \citep{knight2022fep}; future alignment would enable direct comparison with that earlier analysis.

## Principal Contributions

This work makes five contributions:

1. **A multi-source retrieval and deduplication pipeline** for Active Inference literature, using a canonical identifier hierarchy across three academic databases.

2. **A nanopublication-based knowledge graph schema** encoding directed, confidence-scored assertions about eight core hypotheses with full provenance tracking.

3. **A quantitative field overview** characterizing the growth, domain distribution (A/B/C taxonomy), citation topology, and latent topic structure of the Active Inference literature. The field's computational maturity is underscored by recent benchmark results: AXIOM \citep{heins2025axiom} demonstrates AIF agents learning Gameworld 10k in minutes using object-centric world models, while Friston et al. \citep{friston2025active} introduce Renormalization Generative Models (RGMs) that achieve 99.8\% MNIST accuracy with 90\% less data, pointing toward scalable multi-agent architectures. Collective AIF has been empirically validated at scale \citep{heins2024collective}.

4. **An LLM-based hypothesis scoring dashboard** that produces differentiated evidence profiles with temporal trend visualization.

5. **A tooling assessment** of the software ecosystem supporting Active Inference research, including the implemented extraction pipeline, existing software (pymdp, SPM, RxInfer.jl), and knowledge graph infrastructure.

The remainder of this paper is organized as follows. \hyperref[sec:methods]{The methodology section} describes the five-stage pipeline—the central contribution enabling reproducible, automated evidence synthesis—with separate treatments of \hyperref[sec:methods_retrieval]{literature retrieval}, \hyperref[sec:extraction_pipeline]{LLM-based assertion extraction}, \hyperref[sec:methods_bibliometrics]{bibliometric analysis}, the \hyperref[sec:methods_kg]{nanopublication-based knowledge graph}, and \hyperref[sec:methods_viz]{visualization and variable injection}. \hyperref[sec:hypothesis_results]{The hypothesis evidence landscape} presents quantitative scoring results (RQ3), followed by \hyperref[sec:field_overview]{the field overview} with domain-level analysis (RQ1, RQ2), \hyperref[sec:subfield_analyses]{detailed domain analyses}, \hyperref[sec:text_analytics]{text analytics}, and \hyperref[sec:citation_network]{citation network topology}. \hyperref[sec:conclusion]{The conclusion} addresses limitations and future directions; the \hyperref[sec:discussion]{discussion} provides community recommendations and open questions. \hyperref[sec:technical_appendix]{Appendix~A} collects mathematical and algorithmic details; \hyperref[sec:tooling]{Appendix~B} surveys the tooling landscape (RQ4).



```{=latex}
\newpage
```


# Methodology: Pipeline Design and Formal Definitions \label{sec:methods}

This section describes the five-stage computational meta-analysis pipeline. Each stage corresponds to a tested, independently executable script that reads upstream outputs and produces structured artifacts. The pipeline extends the systematic literature analysis approach of Knight et al. \citep{knight2022fep}—which combined manual annotation with ontology-based automated analysis—by substituting manual coding with fully automated, LLM-driven assertion extraction and citation-weighted hypothesis scoring.

## Pipeline Overview

| Stage | Script | Primary Input | Primary Output | Section |
| --- | --- | --- | --- | --- |
| 1 | `01_literature_search.py` | API queries | `corpus.jsonl` | \hyperref[sec:methods_retrieval]{Retrieval} |
| 2 | `02_meta_analysis_pipeline.py` | `corpus.jsonl` | Classification, temporal, TF-IDF, NMF, citation network JSONs | \hyperref[sec:methods_bibliometrics]{Bibliometrics} |
| 3 | `03_build_knowledge_graph.py` | `corpus.jsonl` | `nanopublications.jsonl`, `nanopublications.trig`, scores | \hyperref[sec:methods_kg]{Knowledge Graph} |
| 4 | `04_generate_figures.py` | All Stage 2–3 JSONs | 16 publication-ready PNGs | \hyperref[sec:methods_viz]{Visualization} |
| 5 | `05_inject_variables.py` | All output JSONs | Rendered manuscript Markdown | \hyperref[sec:methods_viz]{Injection} |

Scripts act as thin orchestrators that import methods from tested library modules and handle file I/O. All computation resides in the `src/` packages; no analysis logic is embedded in scripts.



```{=latex}
\newpage
```


# Stage 1: Multi-Source Literature Retrieval and Deduplication \label{sec:methods_retrieval}

We retrieve papers from three complementary academic databases to maximize coverage and enable cross-source deduplication. The retrieval window begins at 2005, encompassing the period when Energy-Based Model and variational Bayesian research \citep{dayan1995helmholtz, lecun2006tutorial} provided mathematical precursors to what Friston formalized as the Free Energy Principle in 2006 \citep{friston2006free}; this inclusive start captures historical lineage and cross-disciplinary convergence that a later cutoff would exclude.

**arXiv.** We query the arXiv Atom API using phrase-matched searches including `all:"active inference"`, `all:"free energy principle"`, `all:"expected free energy"`, `all:"variational free energy" AND all:"inference"`, and targeted Energy-Based Model queries (`all:"energy-based model" AND all:"free energy"`, `all:"Helmholtz machine" AND all:"inference"`, `all:"Boltzmann machine" AND all:"free energy"`, `all:"contrastive divergence" AND all:"generative model"`). The `all:` prefix searches titles, abstracts, and full text; phrase matching reduces contamination from unrelated physics papers that mention "free energy" in thermodynamic contexts. The EBM-adjacent queries capture research at the intersection of energy-based generative modeling and variational inference—a growing convergence area \citep{lecun2006tutorial}.

**Semantic Scholar.** We query the Semantic Scholar Graph API \citep{kinney2023semantic} with the same terms. Semantic Scholar provides citation graphs, abstract embeddings, and links to published versions. Retry logic with exponential backoff handles rate limiting.

**OpenAlex.** We query OpenAlex \citep{priem2022openalex} to capture journal-published work that may not appear on arXiv, including clinical studies and neuroscience experiments in domain-specific venues. The `referenced_works` field populates citation links for each paper.

## Canonical Identifier Deduplication

After retrieval, papers are assigned a canonical identifier using the priority scheme: DOI $>$ arXiv ID $>$ Semantic Scholar ID $>$ OpenAlex ID $>$ title hash. When the same paper appears in multiple sources, the record with the highest metadata completeness is retained. For each incoming paper, the two records are compared on metadata completeness—defined as the count of non-empty attributes among \{abstract, DOI, arXiv ID, venue, citation count\}. The pipeline retains the richer record; in the event of a tie, the incumbent is preserved. This "merge-on-add" strategy aggregates the richest available metadata without requiring an expensive downstream reconciliation pass. Deduplication produces $N = 849$ unique papers spanning 2005–2026.

## Relevance Filtering and Curation

After deduplication, a **relevance filter** removes papers whose titles and abstracts lack any core Active Inference terminology (e.g., ``active inference,''``free energy principle,'' ``variational free energy''), eliminating off-topic results introduced by broad keyword overlap across heterogeneous databases.

We emphasize that this process relies on keyword search strategies across divergent APIs. In any complex research field, there is no single optimal word or threshold for definitive inclusion or exclusion. Different information sources and repositories yield differing schemas and representations, introducing both false positives (papers overlapping in terminology, such as unrelated database or biological toolkits) and false negatives (relevant papers using alternative nomenclature without standard keywords).

Consequently, this pipeline is not intended to produce a static, "golden" list of canonical papers. Rather, it is designed as an open-source software package that can be modularly updated and versioned. Researchers can configure the pipeline to operate on custom literature bibliographies curated for specific relevance criteria through time, treating the initial query-based retrieval as a programmatic starting point rather than an absolute boundary.



```{=latex}
\newpage
```


# LLM-Based Assertion Extraction: Prompt Design, Error Taxonomy, and Validation \label{sec:extraction_pipeline}

_This supplementary section documents the implementation specifics of the LLM-based assertion extraction pipeline._

## Relationship to Prior Approaches

The closest prior effort is the systematic literature analysis of Knight, Cordes, and Friedman \citep{knight2022fep}, which used human annotators to manually code structural, visual, and mathematical features of FEP and Active Inference publications. Their work operated at the scale of hundreds of annotated papers and employed terms from the Active Inference Institute's Active Inference Ontology for automated text analysis. Our pipeline replaces the manual coding step with LLM-based assertion extraction, enabling scalable processing of the full corpus ($N = 849$ papers) at the cost of exchanging human-verified precision for machine-generated assessments that require post-hoc validation. This trade-off is characteristic of the broader LLM-based scientific extraction landscape: recent benchmarking confirms that even state-of-the-art modular extraction architectures fall short of production-level precision---particularly on tasks requiring exhaustive retrieval and aggregation of multiple values from long documents---validating our design choice to retain human review pathways alongside automated extraction.

| Dimension | Knight et al. (2022) | This work |
|-----------|---------------------|-----------|
| **Scale** | Hundreds of papers | 849 papers |
| **Annotation** | Manual (structural/visual/math features) | Automated (LLM hypothesis assessment) |
| **Ontology** | Active Inference Ontology terms | 8 standard hypotheses |
| **Output** | Annotated features + term frequencies | Nanopublications + knowledge graph |
| **Reproducibility** | Annotator-dependent | Deterministic (given model + seed) |
| **Precision** | High (human-verified) | Medium (requires validation) |

### Positioning in the LLM-Based Review Landscape

Our pipeline operates within a rapidly maturing ecosystem of LLM-powered literature analysis tools. Multi-agent architectures such as LitLLM decompose the review process into specialized sub-agents (planner, identifier, extractor, compiler), while ensemble approaches aggregate outputs from multiple LLMs via weighted voting to improve reliability. Our work differs from these tools in three respects: (1) we target _hypothesis-level evidence scoring_ rather than inclusion/exclusion screening; (2) we produce structured nanopublications rather than narrative summaries; and (3) we operate on abstracts rather than full texts—a deliberate trade-off that enables corpus-scale processing ($N = 849$) at the cost of missing fine-grained claims embedded in method sections or discussion paragraphs. Full-text processing could improve extraction recall, particularly for hypotheses with small evidence bases (H6 Clinical Utility, H7 Morphogenesis).

## Prompt Engineering and Schema Design

The structured prompt is designed to minimize parsing failures and maximize assessment quality:

1. **Explicit JSON schema.** The prompt specifies the exact output schema—field names, allowed direction values, and the numeric confidence range—reducing the LLM's tendency to generate free-form text or ad hoc structures.

2. **Hypothesis definitions in-context.** All eight definitions are included verbatim, ensuring the LLM assesses relevance from the provided context rather than relying on parametric knowledge that may be stale.

3. **Reasoning field.** Each assessment includes a natural-language reasoning string, providing an audit trail for human reviewers and enabling systematic analysis of error patterns.

4. **Irrelevant filtering.** An explicit "irrelevant" direction allows the LLM to mark hypotheses that a paper does not address, avoiding forced spurious assessments.

### Prompt Template

The extraction prompt follows a two-part structure (system + user):

```text
SYSTEM: You are a scientific literature analyst specializing in the
Free Energy Principle and Active Inference. Assess the relevance of
the given paper to each hypothesis. Return a JSON array.

USER:
Paper: {title}
Abstract: {abstract}

Hypotheses:
H1: FEP Universality — {description}
H2: AIF Optimality — {description}
...
H8: Language AIF — {description}

For each hypothesis, return:
{
  "hypothesis_id": "H1",
  "direction": "supports|contradicts|neutral|irrelevant",
  "confidence": 0.0-1.0,
  "reasoning": "..."
}
```

The extraction module (`src/knowledge_graph/llm_extraction.py`) includes configurable retry logic with exponential backoff, JSON parsing with handling of markdown code fences and extraneous text, confidence clamping, and validation against the hypothesis ID set. The default model is `gemma3:4b` on a local Ollama instance, configurable via `--llm-model` and `--llm-url` flags.

## Failure Modes and Error Recovery

The primary failure modes are documented below.

### Over-Extraction Bias

Approximately 15--20\% of assessments in preliminary experiments exhibit over-extraction: the LLM attributes claims to a paper that merely mentions a hypothesis without taking a position. This is the most common error mode and produces false supporting evidence.

### Direction Misclassification

The LLM misclassifies a contradicting claim as supporting, or vice versa. Rarer but more consequential, as it directly inverts the evidence signal. Most common for papers that discuss limitations while ultimately endorsing a hypothesis.

### Confidence Calibration Constraints

The model occasionally assigns high confidence to assessments where the underlying evidence is ambiguous. Reliable confidence calibration remains an open problem for zero-shot LLM applications, motivating the multi-tiered validation protocols described below.

### Progressive JSON Parsing Recovery

To mitigate formatting inconsistencies, the module implements a progressive parsing pipeline to recover malformed LLM outputs:

1. **Direct parse**: Attempt `json.loads()` on the raw response.
2. **Strip code fences**: Remove Markdown `` ```json ... ``` `` wrappers and retry.
3. **Extract JSON array**: Scan for the first `[...]` substring in the response text.
4. **Individual recovery**: If a valid array contains malformed elements, parse each element independently.

Papers that fail all parsing stages are logged and skipped; their count is reported at pipeline completion.

## Validation Methodology

Validation of LLM-extracted assertions follows a three-tier protocol:

1. **Spot-check validation.** A random sample of 50 papers is reviewed by a domain expert, comparing LLM assessments against human judgments for direction accuracy and confidence appropriateness.

2. **Boundary-case audit.** Papers known to make contested claims (e.g., critiques of FEP universality, Markov blanket realism debates) are specifically checked for correct direction assignment.

3. **Aggregate consistency.** Hypothesis scores are compared against qualitative expectations from the literature: hypotheses known to be well-supported (e.g., H4 Predictive Coding) should score positively; those known to be contested (e.g., H3 Markov Blanket Realism) should show lower or mixed scores.

Preliminary experiments on a sampled subset of Active Inference papers—evaluated across GPT-4 and Claude-family models—suggest that this automated approach reduces human annotation time by approximately 60--70\% compared to purely manual extraction. Both over-extraction biases and direction inversion errors are intercepted by human review at acceptable rates. The pipeline supports model upgrades without code changes: swapping the underlying model requires only adjusting the `--llm-model` flag.

## From Assertions to Nanopublications

Each validated assertion is wrapped in a **nanopublication** \citep{groth2010anatomy, kuhn2016decentralized}—a self-contained, machine-readable knowledge unit packaging the assertion with explicit provenance metadata. The wrapping process assigns:

- A **unique identifier** (`nanopub:<uuid12>`) for graph-level deduplication.
- An **attribution string** recording the pipeline name and LLM model version.
- A **UTC timestamp** in ISO 8601 format, establishing temporal provenance.

Nanopublications are persisted **incrementally** during extraction. Every 50 papers (configurable via `--checkpoint-interval`), the pipeline atomically appends newly extracted nanopublications to `nanopublications.jsonl` using a temporary-file-plus-rename strategy that prevents corruption on interruption. Deduplication operates on the composite key $(paper\_id, hypothesis\_id)$: when a paper is re-processed with an improved model, the newer assertion overwrites the stale entry. This merge-on-add design enables iterative model refinement without costly full-corpus re-extraction.

After extraction completes, the full nanopublication set is additionally serialized to **RDF/TriG** format per the nanopublication standard, producing four named graphs per nanopublication (Head, Assertion, Provenance, Publication Info). The TriG output is suitable for publication to the decentralized nanopublication network and archival on data repositories such as Zenodo. The complete RDF schema is specified in the \hyperref[sec:methods_kg]{knowledge graph methodology} and \hyperref[sec:appendix_rdf]{Appendix~A.5}.



```{=latex}
\newpage
```


# Stage 2: Bibliometric Analysis \label{sec:methods_bibliometrics}

Stage 2 performs four complementary analyses on the deduplicated corpus. All analyses are deterministic given fixed random seeds and operate on the same `corpus.jsonl` input.

## Subfield Classification

Each paper is classified into one of eight categories organized across three domains: **A – Core Theory** (A1: quantitative and formal mathematical theory; A2: qualitative philosophy and general FEP theory), **B – Tools \& Translation** (algorithms, scaling, and software development), and **C – Application Domains** (C1: neuroscience, C2: robotics, C3: language processing, C4: computational psychiatry, C5: biology and morphogenesis). Classification uses word-boundary-aware keyword matching against curated lists applied to titles and abstracts. A priority system ensures that specific application domains (C1–C5, priority 1) take precedence over tools (B, priority 2), formal theory (A1, priority 3), and the broad qualitative philosophy catch-all (A2, priority 4). Within a priority tier, the domain with the most keyword matches wins. A1's keyword set includes mathematical indicators such as *theorem*, *proof*, *convergence*, *posterior*, *equation*, and *Fokker–Planck*, ensuring that papers with mathematical content are classified as formal theory rather than defaulting to the philosophy category.

## Temporal Metrics and Growth-Rate Estimation

We compute temporal publication metrics including year-by-year counts with gap-filling, cumulative totals, 3-year smoothed moving averages, and peak year identification. Field dynamics are estimated via two complementary metrics. The **mean year-over-year growth rate** $\bar{g}$ is the arithmetic mean of annual growth rates for years with non-zero prior-year publications. The **doubling time** $t_d = \ln 2 / \ln(1 + \bar{g})$. The **compound annual growth rate** (CAGR) captures the annualized rate across the full temporal span. Mathematical details are provided in \hyperref[sec:appendix_growth]{Appendix~A.3}.

## Text Analytics

The TF-IDF matrix is constructed manually using tokenization with stopword removal and L2-normalized term-frequency inverse-document-frequency weighting \citep{salton1975vector}, with a configurable vocabulary size (default: 1000 features). Non-negative matrix factorization (NMF) is applied to discover latent topics using multiplicative update rules \citep{lee1999nmf}. Mathematical details are provided in \hyperref[sec:appendix_nmf]{Appendix~A.2}.

## Citation Network Construction

The intra-corpus citation network is constructed as a directed graph where nodes are papers and edges represent citation relationships resolved within the corpus. Network metrics include PageRank centrality, HITS hub and authority scores \citep{kleinberg1999authoritative}, degree distributions, network density, connected components, and community structure via greedy modularity maximization \citep{clauset2004finding}.



```{=latex}
\newpage
```


# Stage 3: Nanopublication-Based Knowledge Graph \label{sec:methods_kg}

Stage 3 is the methodological core of this work: it transforms unstructured abstracts into a structured, RDF-compatible knowledge graph of scientific evidence. The stage encompasses four tightly coupled operations: LLM-based assertion extraction, nanopublication packaging, knowledge graph construction, and citation-weighted hypothesis scoring.

## LLM-Based Assertion Extraction

We extract assertions by prompting a locally hosted LLM (Ollama \citep{ollama2024}) to assess each paper's abstract against eight standard hypotheses. The model receives a structured prompt containing the paper title, abstract, and hypothesis definitions, and returns a JSON array where each element specifies a hypothesis ID, direction (supports, contradicts, neutral, or irrelevant), a confidence score $c \in [0, 1]$, and a reasoning string. Assertions marked "irrelevant" are discarded; confidence values are clamped to $[0, 1]$; and responses are validated against the known hypothesis ID set. Papers lacking abstracts are skipped. Detailed prompt engineering, error taxonomy, and validation methodology are documented in the \hyperref[sec:extraction_pipeline]{extraction pipeline section}.

## Nanopublication Schema and RDF Structure

Each assertion is encoded as a **nanopublication** \citep{groth2010anatomy, kuhn2016decentralized}—a minimal, self-contained, machine-readable unit of scientific evidence. Formally, each nanopublication is a tuple $(p, h, d, c)$ where $p$ is the paper identifier, $h$ the hypothesis identifier, $d \in \{\text{supports}, \text{contradicts}, \text{neutral}\}$ the direction, and $c$ the confidence. Provenance metadata records the LLM model, UTC timestamp, and paper identifier.

The pipeline serializes nanopublications in two complementary formats:

1. **JSON Lines** (one JSON object per line) for efficient incremental checkpointing. Assertions are saved at configurable intervals (default: every 50 papers), enabling the pipeline to resume from where it left off after interruption without re-processing already-analyzed papers. Deduplication uses the composite key $(paper\_id, hypothesis\_id)$; re-runs with improved models overwrite stale results.

2. **RDF/TriG** per the nanopublication standard ([nanopub.net](https://nanopub.net/)), producing four named graphs per nanopublication:

| Named Graph | Content | Key Predicates |
| --- | --- | --- |
| **Head** | Links the nanopub resource to its three component graphs | `np:hasAssertion`, `np:hasProvenance`, `np:hasPublicationInfo` |
| **Assertion** | The core scientific claim | `aif:asserts` (Paper → Assertion), `aif:supports`/`aif:contradicts` (Assertion → Hypothesis), `aif:claim`, `aif:confidence`, `aif:citationCount` |
| **Provenance** | How the assertion was generated | `prov:wasGeneratedBy`, `prov:generatedAtTime`, `prov:wasAttributedTo`, `prov:hadPrimarySource` |
| **Publication Info** | Metadata about the nanopublication itself | `dc:created`, `dc:creator`, `dc:license` |

The namespace `http://activeinference.institute/ontology/` (prefix `aif:`) defines all domain predicates; the nanopublication schema (`http://www.nanopub.org/nschema#`, prefix `np:`) provides structural predicates; provenance uses PROV-O (`http://www.w3.org/ns/prov#`); and Dublin Core (`http://purl.org/dc/terms/`) provides publication metadata. The TriG output is suitable for publication to the decentralized nanopublication network and aligns with FAIR data principles: **F**indable via URI-based identification, **A**ccessible via standard RDF protocols, **I**nteroperable through W3C-standard serialization, and **R**eusable with explicit provenance and CC0 licensing.

## Knowledge Graph Construction

The knowledge graph is an RDF-compatible directed graph with three node types: **paper nodes** (metadata: title, abstract, authors, year, venue, citation count, domain), **assertion nodes** (claim text, direction, hypothesis ID, confidence), and **hypothesis nodes** (the eight standard hypotheses). Edges encode five relations defined in the schema:

- `aif:asserts` — Paper $\to$ Assertion
- `aif:cites` — Paper $\to$ Paper
- `aif:belongsTo` — Paper $\to$ Subfield
- `aif:supports` — Assertion $\to$ Hypothesis
- `aif:contradicts` — Assertion $\to$ Hypothesis

The graph is implemented with a dual backend: `rdflib` \citep{rdflib2023} when available (preferred for semantic web compatibility), with automatic fallback to `networkx.DiGraph` for environments without RDF dependencies. Both backends maintain identical internal indices for efficient paper, assertion, and hypothesis queries.

## Citation-Weighted Hypothesis Scoring

For each hypothesis $H$, we compute a citation-weighted evidence score:

\begin{equation}
\text{score}(H) = \frac{\sum_{a \in S(H)} w(a) - \sum_{a \in C(H)} w(a)}{\sum_{a \in A(H)} w(a)}
\end{equation}

where $S(H)$, $C(H)$, and $A(H)$ are the sets of supporting, contradicting, and all assertions for $H$, and the weight function is:

\begin{equation}
w(a) = \log(1 + \text{citations}(a)) \cdot \text{confidence}(a)
\end{equation}

The logarithmic citation weighting ensures that highly cited papers carry more influence without allowing any single paper to dominate. The score lies in $[-1, 1]$. Temporal trends are computed by evaluating the cumulative score at each year, using only assertions from papers published up to that year. A full derivation appears in \hyperref[sec:appendix_scoring]{Appendix~A.1}.

## Tally-Based Evidence Aggregation

We emphasize that this algorithmic scoring formula constitutes a **tally-based approach** to evidence synthesis: each nanopublication assertion operates as an independent evidential vote, weighted by citation impact and the extraction model's confidence. The aggregation is linear and additive—supporting and contradicting assertions are summed and differenced without modeling dependencies, correlated evidence, or causal structure among claims. This design choice prioritizes transparency, reproducibility, and computational tractability over statistical sophistication.

The tally-based framing introduces three constraints. First, assertions from methodologically related papers (e.g., iterative publications from a single research group testing the same model) are counted independently, amplifying correlated evidence. Second, the scoring metric treats all assertion sources symmetrically: an assertion from a theoretical review and one from an empirical trial carry equal weight at a given confidence level. Third, temporal scoring tracks *cumulative totals* rather than dynamic probabilistic estimates; the score at year $t$ is the sum of all historical evidence, rather than a decaying posterior that downweights early work.

We embrace these constraints intentionally. The tally-based approach provides a stable, interpretable baseline against which more sophisticated scoring methods can be evaluated. The \hyperref[sec:conclusion]{conclusion} describes concrete extensions—including hierarchical Bayesian scoring, causal evidence graphs, and evidential diversity indices that downweight correlated evidence.



```{=latex}
\newpage
```


# Stages 4–5: Visualization, Variable Injection, and Reproducibility \label{sec:methods_viz}

## Stage 4: Visualization

Stage 4 renders 16 publication-ready figures from the analysis outputs of Stages 2 and 3. All figures use the Wong (2011) colorblind-safe palette \citep{wong2011colorblind} and enforce a 16-point minimum font size for accessibility compliance. Figures span six categories: field summary and domain distribution (2 figures), growth and temporal dynamics (2 figures), citation network topology (2 figures), hypothesis evidence dashboard and timeline (2 figures), assertion composition (2 figures), and text analytics—word cloud, PCA embeddings, term heatmap, dendrogram, topic-term bars, and co-occurrence matrix (6 figures). The figure generation script reads only JSON outputs and produces only PNG files, ensuring strict separation between analysis and visualization.

## Stage 5: Manuscript Variable Injection

Stage 5 computes dynamic variables from all pipeline outputs and injects them into manuscript Markdown templates via `{{VAR_NAME}}` placeholder substitution. Variables include corpus-level metrics (size, year range, CAGR), per-domain counts and percentages, citation network statistics (nodes, edges, density, components, resolution rate, mean in-degree), hypothesis scores, and figure counts. All formatting (comma thousand separators, escaping) is applied during variable computation, ensuring the manuscript templates remain human-readable while producing publication-ready output. Unrecognized placeholders are preserved with a warning logged, enabling incremental manuscript development ahead of full pipeline execution.

## Reproducibility and Test-Driven Validation

The pipeline is deterministic given fixed random seeds and API responses. Test-driven development enforces 90\% minimum code coverage on project modules and 60\% on shared infrastructure, with real data and computation (no mocking). The test suite validates boundary conditions for hypothesis scoring (all-support $\to$ +1, all-contradict $\to$ $-1$, balanced $\to$ 0), schema consistency, serialization round-trips, and end-to-end pipeline integrity. Source code, configuration, and outputs are available under CC-BY-4.0.



```{=latex}
\newpage
```


# Hypothesis Evidence Landscape and Temporal Dynamics \label{sec:hypothesis_results}

The LLM-based extraction pipeline produced a total of 2,795 assertions across the eight tracked hypotheses, drawn from the full corpus of $N = 849$ papers. The distribution of assertion types and the resulting citation-weighted scores reveal a differentiated evidence landscape (Figure \ref{fig:hypothesis_dashboard}):

| Hypothesis | Score | Supports | Neutral | Contradicts | Total | Character |
| --- | --- | --- | --- | --- | --- | --- |
| H4: Predictive Coding | $+0.92$ | 677 | 115 | 1 | 793 | Strong consensus |
| H5: Scalability | $+0.68$ | 126 | 95 | 0 | 221 | Strong consensus |
| H8: Language AIF | $+0.48$ | 39 | 70 | 0 | 109 | Moderate, growing |
| H6: Clinical Utility | $+0.42$ | 14 | 21 | 0 | 35 | Moderate, emerging |
| H7: Morphogenesis | $+0.40$ | 16 | 45 | 0 | 61 | Moderate, emerging |
| H1: FEP Universality | $+0.38$ | 250 | 546 | 1 | 797 | Broad but diffuse |
| H2: AIF Optimality | $+0.24$ | 142 | 477 | 15 | 634 | Weakly contested |
| H3: Markov Blanket Realism | $+0.22$ | 11 | 130 | 4 | 145 | Contested |

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/hypothesis_dashboard.png}
\caption{Hypothesis scoring dashboard showing citation-weighted evidence scores ($[-1, +1]$) for the eight tracked hypotheses, sorted descending by consensus strength. Predominantly positive scores reflect both genuine empirical support and systematic positive biases from publication selection and linguistic framing (see \S\ref{sec:pub_bias}).}
\label{fig:hypothesis_dashboard}
\end{figure}

## Interpretation of Evidence Profiles

The eight hypotheses cluster into three distinct tiers. The **consensus tier** (H4, H5) comprises hypotheses with strong positive scores ($> 0.5$) and minimal contradicting assertions. Predictive coding (H4), the most extensively assessed hypothesis with 793 assertions and a score of $+0.92$, has accumulated overwhelmingly supportive evidence since the 1970s, reflecting the deep empirical grounding of hierarchical prediction error models in neuroscience. Scalability (H5) shows a similarly strong positive trajectory ($+0.68$) that accelerated after 2017 as deep active inference architectures emerged.

The **moderate tier** (H6, H7, H8) comprises hypotheses with positive scores in the $0.4$--$0.5$ range. Language AIF (H8) leads this tier with 109 assertions and a score of $+0.48$, reflecting recent breakthroughs coupling active inference to large language models. Clinical utility (H6) has the smallest evidence base (35 assertions) but shows a temporally increasing trend, consistent with the recent growth of computational psychiatry applications. Morphogenesis (H7) shows moderate support ($+0.40$), reflecting its status as an active research frontier where theoretical proposals outpace empirical validation.

The **diffuse or contested tier** (H1, H2, H3) is the most diagnostically informative for understanding the field's intellectual maturation. FEP universality (H1), despite generating one of the largest raw evidence bases (797 assertions), achieves a score of only $+0.38$—the majority of assessments are neutral, indicating that researchers frequently *invoke* the FEP without explicitly testing its universality claim. This finding dovetails with the falsifiability critique leveled by Colombo and Seri\`es \citep{colombo2021free}: if the FEP can be applied to any self-organizing system without generating testable predictions that distinguish it from alternative frameworks, neutral citations (invocations rather than tests) are exactly what one would expect to dominate the literature. AIF optimality (H2) exhibits the largest volume of contradicting evidence (15 assertions), suggesting that as the field has transitioned from theory to empirical application, absolute optimality claims have undergone increasingly stringent critical scrutiny. Markov blanket realism (H3) has the smallest evidence base (145 assertions) with a score of $+0.22$ and 4 contradicting assertions—empirically capturing the ongoing philosophical debate between those who treat Markov blankets as real thermodynamic boundaries (\"Friston blankets\") and those who argue they are purely instrumental statistical tools (\"Pearl blankets\") \citep{bruineberg2022emperor}. The contested score for H3 directly reflects this unresolved ontological tension in the field.

## Temporal Dynamics of Evidence Accumulation

The cumulative evidence timeline (Figure \ref{fig:evidence_timeline}) reveals three temporal patterns. First, **early convergence**: H4 (predictive coding) reached positive territory in the late 1990s following the publication of Rao and Ballard's foundational predictive coding model \citep{rao1999predictive} and has maintained a high score since, reflecting the mature empirical base in cognitive neuroscience. Second, **recent acceleration**: H5 (scalability) and H6 (clinical utility) show steep upward trends after 2017, tracking the emergence of deep active inference tools and computational psychiatry applications. The H5 trajectory is particularly striking: AXIOM \citep{heins2025axiom} demonstrates that principled object-centric world models under the AIF framework can outperform state-of-the-art deep RL agents on standard benchmarks, directly addressing the scalability challenge that has historically been the strongest argument against AIF as a practical framework. Third, **persistent contestation**: H3 (Markov blanket realism) has maintained a lower score since 2018, with supporting papers partially offset by targeted critiques.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/evidence_timeline.png}
\caption{Temporal evolution of cumulative citation-weighted evidence scores by hypothesis (2005--2026). Divergent trajectories around the shaded neutral boundary $(\pm 0.1)$ reveal which hypotheses are gaining or losing support over time. H4 (predictive coding) stabilized early; H5 (scalability) accelerated post-2017.}
\label{fig:evidence_timeline}
\end{figure}

## Assertion Composition and Distribution

The per-hypothesis composition of assertions (Figure \ref{fig:assertion_breakdown}) and the multi-panel summary (Figure \ref{fig:assertion_summary}) provide complementary views of the extraction results.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_breakdown.png}
\caption{Stacked horizontal bars decomposing per-hypothesis assertions into supports (green), contradicts (red-orange), and neutral (blue) categories ($N = 2,795$ total assertions). Labels show total count and support percentage. The high support fractions are partially attributable to publication bias and affirmative linguistic framing.}
\label{fig:assertion_breakdown}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_summary.png}
\caption{Multi-panel assertion summary: (left) pie chart of overall assertion type distribution showing supports/contradicts/neutral proportions, (right) per-hypothesis assertion counts with palette-coded bars. $N = 2,795$ assertions extracted from $849$ papers.}
\label{fig:assertion_summary}
\end{figure}

## Limitations of the Current Scoring Approach

As noted in the \hyperref[sec:methods_kg]{methodology}, these results reflect a **tally-based aggregation** of independent LLM-extracted assertions, weighted by citation count and confidence. This approach does not account for evidential dependencies (e.g., papers from the same group testing the same model), does not distinguish between empirical and theoretical evidence, and treats the LLM's confidence scores as calibrated probabilities. The assertion counts are also sensitive to corpus composition: H1's large neutral tally (546) partially reflects the keyword classifier's tendency to assign papers to the broad A2 (philosophy) category, where FEP universality is implicitly invoked but rarely explicitly tested. The dominant-neutral pattern for H1 is also consistent with the falsifiability critique \citep{colombo2021free}: a principle elastic enough to accommodate any behavior without refutation will naturally accrue neutral rather than positive or negative assessments. More sophisticated approaches—including hierarchical Bayesian models, causal evidence graphs, and evidential diversity weighting—are discussed as future directions in the \hyperref[sec:conclusion]{conclusion}.

### Publication Bias and Linguistic Asymmetry \label{sec:pub_bias}

The predominantly positive scores observed across all eight hypotheses should be interpreted with two systematic caveats.

First, **publication bias** systematically inflates supporting evidence. Academic journals preferentially publish positive and confirmatory results (\citealt{sterling1959publication}), meaning that studies finding null or contradictory outcomes for any hypothesis are less likely to appear in the retrievable literature. This \textit{file-drawer effect} is well-documented across scientific disciplines and is expected to disproportionately suppress contradicting assertions in our extraction pipeline. The Active Inference literature is particularly susceptible: as a theoretical framework with strong foundational proponents, papers are more likely to frame results as consistent with the FEP than as challenges to it.

Second, **linguistic asymmetry** in academic writing further skews extraction toward positive classifications. Declarative scholarly claims are inherently phrased affirmatively—authors write ``our results support,'' ``consistent with,'' or ``extends the prediction of'' far more frequently than ``our results refute'' or ``contradicts the claim that.'' Because the LLM extraction pipeline operates on abstract text, this linguistic imbalance propagates directly into the assertion distribution. Even papers presenting genuinely mixed evidence tend to frame their abstracts in terms of what \textit{was} found rather than what was not, biasing the extracted direction toward ``supports.''

These two effects act in concert: publication bias reduces the number of contradicting papers in the corpus, and linguistic framing reduces the number of contradicting assertions extracted from the papers that do appear. Consequently, the absolute values of hypothesis scores should not be taken as unbiased measures of scientific consensus. The \textit{relative} ordering and temporal \textit{trajectories} of hypothesis scores are more robust indicators, as these biases affect all hypotheses approximately equally.



```{=latex}
\newpage
```


# Field Overview: Disciplinary Structure and Growth Dynamics \label{sec:field_overview}

The Active Inference literature has undergone a phase transition. What originated in the early 2000s—building on predictive coding and Bayesian brain foundations from the late 1990s—as a niche within theoretical neuroscience has expanded rapidly into a multi-disciplinary research program spanning three primary domains and eight tracked categories. The corpus start of 2005 was chosen to capture Energy-Based Model and variational Bayesian antecedents \citep{dayan1995helmholtz, lecun2006tutorial} that preceded the formal introduction of the Free Energy Principle in 2006 \citep{friston2006free} and its subsequent full elaboration \citep{friston2010free}. Our corpus, extracted from arXiv, Semantic Scholar, and OpenAlex and deduplicated to $N = 849$ papers (2005--2026), captures the breadth, tempo, and internal architecture of this expansion (Figure \ref{fig:field_summary}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/field_summary.png}
\caption{Publication counts by domain ($N = 849$). Domain A (Core Theory) dominates, with Domains B (Tools) and C (Applications) forming growing tiers.}
\label{fig:field_summary}
\end{figure}

## Corpus-Level Summary

| Metric | Value |
| --- | --- |
| Total papers | 849 |
| Year range | 2005--2026 |
| Peak year | 2025 |
| CAGR | 16.99\% |
| Active domains | 8 of 8 tracked (A1–A2, B, C1–C5) |

The CAGR of 16.99\% reflects the corpus's long temporal span from 2005 to 2026; the field's actual rapid growth phase began around 2013, with annual output accelerating substantially (Figure \ref{fig:growth_curve}). The fact that sustained high output persists into subsequent years suggests the field has reached a mature production phase rather than experiencing a transient spike. Citation network metrics are detailed in the dedicated citation network analysis (see \hyperref[sec:citation_network]{the citation network analysis}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/growth_curve.png}
\caption{Annual (bars) and cumulative (line) publication counts, 2005--2026 ($N = 849$, CAGR = 16.99\%). The inflection around 2013 marks the onset of rapid growth. Moving average trendline (dashed), peak year, and median year annotated.}
\label{fig:growth_curve}
\end{figure}

## Domain Distribution

Keyword-based classification assigns each paper to one of eight categories across three domains:

| Domain | Category | Papers | Percentage |
| --- | --- | --- | --- |
| **A – Core Theory** | A1: Formal Theory | 67 | 7.9\% |
| | A2: Qualitative Philosophy | 68 | 8.0\% |
| **B – Tools** | B: Tools \& Translation | 182 | 21.5\% |
| **C – Applications** | C1: Neuroscience | 158 | 18.7\% |
| | C2: Robotics | 136 | 16.1\% |
| | C3: Language | 63 | 7.4\% |
| | C4: Psychiatry | 36 | 4.3\% |
| | C5: Biology | 137 | 16.2\% |

The concentration of papers in A2 (qualitative philosophy and general theory) reflects the broad scope of foundational FEP work (Figure \ref{fig:subfield_distribution}). The priority-based classifier mitigates over-assignment by routing papers with mathematical indicators (theorems, proofs, equations, statistical formalism) to A1 before falling back to A2, and by preferring specific application domains (C1–C5) and tools (B) over both core-theory categories. Papers that discuss FEP/AIF conceptually without mathematical formalism or domain-specific vocabulary are correctly assigned to A2. This figure should be read as a *ceiling* on theoretical generality rather than a literal measure of research focus—embedding-based classification would likely redistribute some fraction into more specific categories. That all eight categories are populated, including computational psychiatry (C4) and formal theory (A1), indicates diversification beyond the field's neuroscience origins.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/subfield_distribution.png}
\caption{Domain distribution ($N = 849$). Classification uses hierarchical keyword matching against curated lists applied to titles and abstracts, capturing distinct methodological and domain-specific groupings.}
\label{fig:subfield_distribution}
\end{figure}

Detailed characterizations of each domain—including historical context, growth trends, and open problems—are provided in the supplementary domain analyses (see \hyperref[sec:subfield_analyses]{the domain analyses}). Latent topic structure, vocabulary analysis, and document embeddings are presented in the text analytics section (see \hyperref[sec:text_analytics]{the text analytics section}).

## Cross-Domain Comparison

| Domain | Category | Papers | Growth Trend | Key Challenge | Representative Work |
| --- | --- | --- | --- | --- | --- |
| A | A1: Formal | 67 (7.9\%) | Growing | Mathematical accessibility for broader field | \citep{sakthivadivel2023bayesian} |
| A | A2: Philosophy | 68 (8.0\%) | Stable | Residual catch-all; absorbs FEP prose papers | \citep{friston2010free} |
| B | B: Tools | 182 (21.5\%) | Rapid | Matching deep RL benchmark performance | \citep{fountas2020deep} |
| C | C1: Neuroscience | 158 (18.7\%) | Stable | Bridging theory and empirical neuroimaging | \citep{clark2013whatever} |
| C | C2: Robotics | 136 (16.1\%) | Growing | Real-time feasibility on embedded hardware | \citep{lanillos2021active} |
| C | C3: Language | 63 (7.4\%) | Emerging | Demonstrating gains over existing NLP models | \citep{friston2020generative} |
| C | C4: Psychiatry | 36 (4.3\%) | Emerging | Translating models to clinical practice | \citep{smith2021computational} |
| C | C5: Biology | 137 (16.2\%) | Rapid | Empirical validation of theoretical proposals | \citep{kuchling2020morphogenesis} |

Three structural features emerge from the cross-domain comparison (Figure \ref{fig:subfield_timeline}). First, no single legacy domain dominates: Domain B (Tools \& Translation) accounts for 21.5\% of the corpus, followed by C1 (Neuroscience) at 18.7\% and C2 (Robotics) at 16.1\%. Second, Domain A (Core Theory) aggregates 15.9\% collectively (A1 + A2), while the emergent application frontiers (C3–C5) exhibit accelerating growth. Third, A1's 67 papers understate its intellectual influence—the mathematical formalisms developed in A1 shape implementations across all domains.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/subfield_timeline.png}
\caption{Stacked area chart of publications by domain, 2005--2026 ($N = 849$). Domain A (Core Theory) dominates throughout; application domains C1--C5 show accelerating diversification from 2015 onward.}
\label{fig:subfield_timeline}
\end{figure}



```{=latex}
\newpage
```


# Domain Analyses: Growth Trajectories and Open Problems \label{sec:subfield_analyses}

_This supplementary section provides detailed characterizations of each of the eight tracked Active Inference domains, organized under three tiers: A (Core Theory), B (Tools & Translation), and C (Application Domains)._

## Domain A: Core Theory

### A1 — Quantitative & Formal Theory ($n = 67$, 7.9\%)

The A1 domain develops the mathematical foundations underpinning the Free Energy Principle: information geometry, category-theoretic formulations of Markov blankets, path integral formulations of free energy minimization, and gauge-theoretic perspectives on self-organization. A central debate concerns the ontological status of Markov blankets—whether they correspond to real physical boundaries or are merely useful statistical constructs \citep{bruineberg2022emperor}. Bruineberg et al. draw a critical distinction between _Pearl blankets_ (instrumental, epistemic tools for conditional independence in Bayesian networks) and _Friston blankets_ (ontologically laden physical boundaries between agent and environment), arguing that the scientific credibility of the former should not be extended uncritically to the latter. Friston and collaborators continue to address this critique through the development of Bayesian mechanics \citep{sakthivadivel2023bayesian}, which aims to place the FEP on firmer mathematical footing by grounding Markov blanket dynamics in the physics of belief-based systems. Recent theoretical consolidation has strengthened the formal tools available to A1: variational message passing formulations \citep{champion2021realizing} connect expected free energy decomposition—into risk, ambiguity, epistemic, and instrumental components—to practical planning algorithms, advancing the theoretical justification for EFE-based policy selection. Path integral formulations now connect Markov blanket dynamics to least-action principles, framing free energy minimization as paths of least action for belief updating. With 67 papers (7.9\% of the corpus), A1 captures a meaningful share of formal work, reflecting the improved classifier's ability to route papers with mathematical formalism (theorems, proofs, convergence, posterior distributions, Fokker–Planck equations) into this domain rather than the qualitative philosophy catch-all.

### A2 — Qualitative Philosophy & General Theory ($n = 68$, 8.0\%)

The A2 domain encompasses papers that develop, extend, or review the core Free Energy Principle and Active Inference framework without restricting attention to a specific application domain. This includes Friston's foundational work on variational free energy minimization \citep{friston2010free}, the textbook treatment by Parr, Pezzulo, and Friston \citep{parr2022active}, and numerous tutorial and review papers. The priority-based classifier mitigates over-assignment to A2 by routing papers with mathematical formalism to A1 and papers with domain-specific vocabulary to C1–C5 or B before the A2 catch-all is reached. Nevertheless, the count likely still conceals meaningful internal structure: papers addressing embodied cognition, Bayesian brain theory, and philosophical implications of the FEP are all subsumed under this heading. Key ongoing debates concern the explanatory scope of the FEP—whether it is a principle of physics, biology, or cognition—and the relationship between active inference and competing frameworks such as reinforcement learning and optimal control theory.

## Domain B: Tools & Translation Methods

### B — Algorithms, Scaling, and Software ($n = 182$, 21.5\%)

Domain B addresses the computational challenge of making active inference practical in complex, high-dimensional environments. Early implementations relied on small discrete state spaces amenable to exact message passing. Recent work has introduced deep active inference using neural networks to amortize inference \citep{fountas2020deep}, Monte Carlo tree search for planning \citep{champion2021realizing}, hybrid architectures combining model-based planning with model-free components, and interpretable alternatives such as Free Energy Projective Simulation (FEPS) \citep{pazem2024feps}, which exposes decision logic as human-readable policy graphs. The central open question is whether active inference agents can match deep reinforcement learning performance on standard benchmarks while retaining interpretability and sample efficiency. The availability of the pymdp library \citep{heins2022pymdp} has lowered implementation barriers, contributing to this domain's growth. The recent establishment of the Pymdp Fellowship program in 2025 and the release of real-time stream processing tools like RxInfer.jl v4.0.0 \citep{rxinfer2025} indicate a vibrant and maturing software ecosystem.

## Domain C: Application Domains

### C1 — Neuroscience ($n = 158$, 18.7\%)

Neuroscience represents the historical core of the Active Inference research program. The predictive processing account—in which cortical hierarchies minimize prediction errors through both perceptual inference and active sampling—remains one of the most empirically tested aspects of the framework \citep{friston2010free, clark2013whatever}. The broader neuroscience literature on Dynamic Causal Modeling and predictive coding is extensive; the relatively modest count here likely reflects the keyword classifier's inability to distinguish neuroscience-specific applications from general FEP theory. Bridging the gap between computational models and empirical neuroimaging data remains the domain's primary challenge.

### C2 — Robotics ($n = 136$, 16.1\%)

Robotics applications treat embodied agents as free energy minimizing systems that unify perception and action through proprioceptive and exteroceptive prediction errors \citep{lanillos2021active}. Applications include robotic arm control, mobile navigation, manipulation, and multi-robot coordination. Active inference offers roboticists a principled framework for integrating sensory processing, motor planning, and adaptive behavior without separate perception and control modules. Key challenges include real-time computational feasibility on embedded hardware, continuous high-dimensional action spaces, and sim-to-real transfer.

### C3 — Language Processing ($n = 63$, 7.4\%)

The C3 domain conceptualizes linguistic processes—speech perception, sentence comprehension, dialogue, and reading—as active inference operating over deep hierarchical generative models of linguistic structure \citep{friston2020generative}. Active inference models of reading have reproduced saccadic eye-movement patterns, while models of speech perception capture how listeners integrate prior expectations with acoustic evidence. Recent work couples active inference to large language models, pragmatics, and multi-agent communication. The connection between AIF and LLMs runs in both directions: Wen \citep{wen2025missing} proposes that AIF can replace external reward signals in LLM-based agents, while Friston et al. \citep{friston2025active} demonstrate how active inference enables artificial reasoning through structure learning via Bayesian Model Reduction. The language domain is also where AIF shows strong results through novel discrete generative models for structured sequential tasks \citep{millidge2024retrospective}.

### C4 — Computational Psychiatry ($n = 36$, 4.3\%)

Computational psychiatry leverages active inference to model psychiatric conditions as disruptions in belief updating, precision weighting, or prior rigidity \citep{smith2021computational}. Schizophrenia has been modeled as impaired precision weighting on bottom-up prediction errors; depression as over-precise negative priors; and autism spectrum conditions as atypical precision allocation over sensory channels. Beyond clinical psychopathology, the framework is now being extended to model higher-order cognition: Whyte et al. \citep{whyte2025metacognitive} propose a metacognitive active inference account of imaginative experience, in which "inner screen" representations emerge from EFE-driven attention allocation under FEP constraints—connecting computational psychiatry to consciousness research. The domain continues to expand, with emerging frameworks integrating psychodynamic theory (e.g., self-identity formation via embodied interactions) with predictive processing to unify environmental and biological factors underlying stress disorders. Translating these computational models into diagnostic markers and therapeutic protocols remains an ongoing challenge.

### C5 — Biology & Morphogenesis ($n = 137$, 16.2\%)

The C5 domain applies active inference and the FEP to biological systems beyond the brain: cellular behavior, morphogenesis, evolutionary dynamics, and the origins of life. Morphogenetic processes have been modeled as collective active inference, where groups of cells coordinate to minimize a shared free energy functional \citep{kuchling2020morphogenesis, levin2022technological}. Recent empirical work has validated collective AIF at larger scales: Heins et al. \citep{heins2024collective} demonstrated that surprise minimization alone produces realistic collective motion patterns, providing a principled alternative to ad hoc flocking rules. The FEP's reach now extends beyond biological organisms into engineered systems: Nazemi et al. \citep{nazemi2025energy} apply active inference to smart building energy control under partial observability and privacy constraints, demonstrating that the free energy framework can govern resource allocation in cyber-physical systems. As the second-largest domain, C5 reflects growing interest in extending the FEP to encompass all self-organizing systems—living and artificial—though the ratio of theoretical proposals to empirical validation remains high.

## Comparative Synthesis

Taken together, the three domains reveal a field transitioning from a focused neuroscience program to a broad interdisciplinary framework. The core–periphery structure is clear: Domain A provides the theoretical and mathematical substrate, Domain B pursues engineering viability through scalable algorithms and software, and Domain C tests the framework's generality across neuroscience (C1), robotics (C2), language (C3), psychiatry (C4), and biology (C5). The consistent pattern across applied domains—strong theoretical motivation paired with limited empirical validation—suggests that the field's next growth phase will depend on accumulating experimental evidence.

In direct response to **RQ1** (How is the Active Inference field structured?), the domain taxonomy reveals an asymmetric three-tier architecture: a dominant theoretical core (A), a growing translational layer (B), and an expanding but empirically sparse application periphery (C). The keyword classifier's heavy A2 concentration likely masks genuine diversity within the theoretical core, but the architecture itself—theory → tools → applications—is robust across classification approaches.

### Domain–Hypothesis Cross-Reference

Each domain has a primary hypothesis linkage (see the detailed hypothesis evidence analysis in the \hyperref[sec:hypothesis_results]{hypothesis results}):

| Domain | Category | $n$ | Primary Hypothesis | Evidence Direction |
| --- | --- | --- | --- | --- |
| A1 | Formal | 67 | H3 Markov Blanket Realism | Contested |
| A2 | Philosophy | 68 | H1 FEP Universality | Strongly supporting |
| B | Tools | 182 | H5 Scalability | Mixed |
| C1 | Neuroscience | 158 | H4 Predictive Coding | Supporting |
| C2 | Robotics | 136 | H2 AIF Optimality, H5 Scalability | Mixed |
| C3 | Language | 63 | H8 Language AIF | Emerging |
| C4 | Psychiatry | 36 | H6 Clinical Utility | Supporting |
| C5 | Biology | 137 | H7 Morphogenesis | Supporting |

The evidence directions summarized above are elaborated quantitatively—with citation-weighted scores, temporal trends, and three-tier evidence profiling—in the \hyperref[sec:hypothesis_results]{hypothesis results section}.



```{=latex}
\newpage
```


# Text Analytics: Topic Modeling, Vocabulary Structure, and Document Embeddings \label{sec:text_analytics}

This section examines the latent semantic structure of the Active Inference corpus through complementary text-analytic methods: non-negative matrix factorization for topic discovery, TF-IDF vocabulary analysis, document embedding projections, and term co-occurrence patterns. Together, these analyses reveal thematic structure that cuts across the keyword-based domain taxonomy presented in the \hyperref[sec:field_overview]{field overview}.

## Topic Modeling: Latent Structure

Non-negative matrix factorization (NMF) applied to the TF-IDF matrix identifies five latent topics:

| Topic | Top Terms | Interpretation |
| --- | --- | --- |
| 0 | learning, agent, model, agents, active, environments, aif, inference, environment, based | Agent-environment modeling and robotic applications |
| 1 | inference, active, energy, free, variational, control, bayesian, expected, optimal, principle | Active inference agents and decision-making |
| 2 | states, internal, external, systems, markov, system, dynamics, information, beliefs, self | Markov blankets and internal/external states |
| 3 | fep, systems, ai, principle, energy, free, theory, networks, modeling, language | Free energy principle and AI systems |
| 4 | predictive, brain, cognitive, prediction, perception, processing, sensory, models, coding, model | Predictive coding and cognitive neuroscience |

### Topic–Domain Overlap

These topics are partially orthogonal to the domain taxonomy. Topic 0 (agent-environment modeling) spans tools (B), robotics (C2), and core theory (A1)—a cross-cutting theme that the keyword classifier cannot capture. Topic 4 (predictive coding and cognitive neuroscience) aligns closely with neuroscience (C1) but also draws from core theory. Topic 2 (Markov blankets and states) captures the mathematical core shared across domains. Topic 3 (FEP and AI systems) reveals the growing intersection of active inference with mainstream artificial intelligence research. The absence of retrieval noise (no spurious physics topics) confirms that the phrase-matched arXiv query effectively filters irrelevant content (Figure \ref{fig:topic_term_bars}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/topic_term_bars.png}
\caption{Top 10 terms per NMF topic ($k = 5$ topics, $500$ vocabulary features). Term weights reflect NMF component loadings; higher-weighted terms define each topic's semantic focus.}
\label{fig:topic_term_bars}
\end{figure}

## Vocabulary Analysis

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/word_cloud.png}
\caption{Word cloud of corpus vocabulary ($N = 849$ abstracts) sized by maximum NMF component weight. Prominent terms—``inference,'' ``active,'' ``free energy,'' ``model''—reflect the field's core theoretical commitments.}
\label{fig:word_cloud}
\end{figure}

The word cloud (Figure \ref{fig:word_cloud}) reveals the conceptual core of the Active Inference literature: terms related to the Free Energy Principle ("inference," "active," "free energy," "model," "bayesian") dominate, while application-specific terms appear at smaller scales, reflecting the domain distribution's heavy A2 concentration.

## Document Embedding Projections

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/pca_embeddings.png}
\caption{PCA projection of TF-IDF document embeddings ($N = 849$ documents, $500$ features), colored by domain. Loading arrows indicate vocabulary terms contributing most to each principal component. Variance explained is annotated per axis.}
\label{fig:pca_embeddings}
\end{figure}

Principal Component Analysis of the TF-IDF document-term matrix projects each paper into a two-dimensional space that preserves the directions of maximum variance (Figure \ref{fig:pca_embeddings}). The scatter plot, colored by domain assignment, reveals the degree of semantic separation between domains. Loading arrows overlay the top-variance terms, showing which vocabulary drives the principal components and highlighting the partial overlap between theoretically similar domains.

## Domain Semantic Similarity

To further interrogate the latent semantic structure of the subfields, we extract the top characterizing terms for each domain and compute a hierarchical clustering of domain centroids. The heatmap (Figure \ref{fig:term_heatmap}) reveals distinctive vocabulary patterns beyond mere keyword-level classification, while the dendrogram (Figure \ref{fig:dendrogram}) confirms the tight semantic proximity between Core Theory subfields (A1, A2) and the methodological alignment of Tooling (B) with Robotics (C2).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/term_heatmap.png}
\caption{Mean TF-IDF weight for the top 20 terms across all 8 domains. Darker cells indicate higher usage within a domain, revealing distinctive vocabulary patterns beyond the keyword-level classification used for subfield assignment.}
\label{fig:term_heatmap}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/dendrogram.png}
\caption{Hierarchical clustering of domain centroids (Ward linkage on mean TF-IDF vectors, 8 domains). Cophenetic correlation annotated on figure. A1 (formal theory) and A2 (philosophy) cluster closely, as do C2 (robotics) and B (tools).}
\label{fig:dendrogram}
\end{figure}

## Term Co-occurrence Patterns

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/cooccurrence_matrix.png}
\caption{Normalized co-occurrence matrix for the 30 most frequent terms across $N = 849$ abstracts. Cell intensity reflects the fraction of documents in which two terms co-appear, normalized to $[0, 1]$.}
\label{fig:cooccurrence_matrix}
\end{figure}

The co-occurrence matrix (Figure \ref{fig:cooccurrence_matrix}) for the 30 most frequent corpus terms reveals tightly coupled term clusters corresponding to the NMF topics. The strong co-occurrence between "free," "energy," "principle," and "bayesian" anchors the theoretical core, while application-specific term clusters (e.g., "brain"–"cognitive"–"predictive"–"coding") form distinct off-diagonal blocks. The relative isolation of robotics-specific terms from neuroscience terms confirms the semantic separation between these application domains despite their shared theoretical foundation.



```{=latex}
\newpage
```


# Citation Network Topology \label{sec:citation_network}

The intra-corpus citation network provides a structural view of how Active Inference research is organized, identifying influential hub papers, community structure, and patterns of citation isolation (Figure \ref{fig:citation_network}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/citation_network.png}
\caption{Intra-corpus citation network ($N = 849$ nodes, 1,678 edges). Node size reflects PageRank and HITS centrality scores \citep{kleinberg1999authoritative}; highly cited foundational papers serve as nexus points connecting sub-domains.}
\label{fig:citation_network}
\end{figure}

## Network Density and Degree Distribution

The intra-corpus citation network contains 847 nodes and 1,678 edges, with a density of 0.23\% and 567 connected components. The average in-degree of $\approx 2.0$ indicates that most papers receive few intra-corpus citations, consistent with the field's rapid expansion: the majority of recent papers have not yet accumulated citations within the corpus (Figure \ref{fig:degree_distribution}). Only 5.5\% of all references (1,678 of 30,633) resolve to other papers within the corpus, reflecting cross-source identifier mismatches and the field's engagement with a broad external literature base. Community detection identifies clusters via greedy modularity maximization \citep{clauset2004finding}.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.7\textwidth]{figures/degree_distribution.png}
\caption{In-degree distribution of the citation network. The power-law tail is characteristic of citation networks, with a small number of highly cited hubs.}
\label{fig:degree_distribution}
\end{figure}

## Connected Components and Citation Isolation

The high number of connected components (567 out of 847 nodes) reveals that much of the corpus consists of citation-isolated papers—works that neither cite nor are cited by other papers in the collection. This is partially an artifact of cross-source identifier mismatches, but it also reflects the field's pattern of papers engaging with the FEP literature conceptually without building explicit citation chains. PageRank analysis identifies highly influential papers, predominantly Friston's foundational work \citep{friston2010free} and the AIF textbook \citep{parr2022active}, which serve as nexus points linking otherwise disconnected subgraphs.

## Network Summary

| Metric | Value |
| --- | --- |
| Nodes | 847 |
| Edges | 1,678 |
| Reference resolution rate | 5.5\% (1,678 / 30,633) |
| Connected components | 567 |
| Network density | 0.23\% |
| Mean in-degree | $\approx$ 2.0 |

The citation topology corroborates the field overview findings (RQ1, RQ2): a small number of foundational papers—predominantly Friston's free energy and active inference formulations—anchor a rapidly expanding periphery of increasingly specialized work. The high component count and low density reflect a field in which theoretical influence flows primarily through shared conceptual foundations rather than through dense mutual citation. As metadata standardization improves and DOI adoption becomes universal across preprint and journal ecosystems, re-running this pipeline should yield substantially higher reference resolution rates and a more connected graph, enabling finer-grained community detection and influence tracking.



```{=latex}
\newpage
```


# Conclusion: Evidence Landscape, Methodological Limitations, and Research Agenda \label{sec:conclusion}

## Summary

This work demonstrates that the infrastructure for computational meta-analysis of a rapidly growing scientific field is feasible with current technology. By combining multi-source retrieval ($N = 849$ papers from three databases), LLM-based assertion extraction encoded as nanopublications, and citation-weighted hypothesis scoring, we produce a queryable, RDF-compatible knowledge graph that tracks the evolving evidence for eight core Active Inference claims.

## Constraints and Methodological Scope

Several conscious design constraints scope these findings.

### Keyword Classifier Resolution

The keyword-based classifier operates over 65+ mathematical indicators distributed across 8 domain categories, using a deterministic priority system that routes papers to specific application domains (C1–C5) before testing tools (B), formal theory (A1), and the qualitative philosophy catch-all (A2). Word-boundary-aware matching reduces partial-match false positives, but keyword-based methods cannot capture semantic nuance: papers using novel terminology or discussing cross-domain topics without standard vocabulary risk misclassification. Residual A2 concentration should be interpreted as a ceiling on broad theoretical generality rather than a literal measure of philosophical focus. An embedding-based classifier trained on a labeled subset would provide a quantitative upper bound on the fraction of A2 papers that merit redistribution.

### Citation Network Coverage Gaps

The 1,678 intra-corpus edges spanning 567 connected components provide a topological skeleton, but three systematic gaps inflate the component count: (1) cross-source identifier mismatches (DOI vs. OpenAlex vs. arXiv ID), (2) papers whose references are not indexed by any source API, and (3) open-access preprints whose DOIs differ from their published versions. Exhaustive DOI-level cross-matching with fuzzy title matching would condense the graph further.

### Temporal, Citation-Count, and Assertion-Direction Biases

Citation counts are subject to Matthew effects and cumulative field-size biases. Partial-year indexing for the most recent calendar year undercounts recent publications. The measured 16.99\% CAGR reflects the dilutive effect of the long temporal span (2005–2026); the growth phase from 2010 onward follows a steeper trajectory. Additionally, the predominantly positive hypothesis scores across the board are inflated by two systematic effects: (1) **publication bias**, which causes academic journals to preferentially select positive and confirmatory findings \citep{sterling1959publication}, and (2) **linguistic asymmetry** in scientific writing, where declarative claims are phrased affirmatively far more often than negatively. These effects jointly suppress contradicting assertions in the extracted evidence base. Relative rankings and temporal trajectories are more reliable than absolute score magnitudes.

### LLM Extraction Fidelity

Zero-shot extraction introduces two systematic biases: over-extraction (hallucinating claims the paper merely mentions) and direction inversion (misclassifying opposing evidence as supporting). Recent benchmarking of modular LLM extraction architectures confirms that even state-of-the-art systems fall short of production-level precision—particularly on tasks requiring exhaustive retrieval and aggregation of directional claims from long documents \citep{liang2024survey}. The explicit \"irrelevant\" filtering predicate mitigates over-extraction, but no human-annotated $\kappa$-agreement baseline currently bounds the residual error rate. Hypothesis-level evidence assessment is substantially more demanding than binary inclusion/exclusion screening, suggesting that our pipeline's error rate on directional classification warrants careful calibration. Establishing a human-annotated baseline through a pilot annotation study (Future Direction 1, below) is a prerequisite for calibrating confidence scores and quantifying the gap between automated and expert-level extraction.

## Future Directions: Beyond Tally-Based Evidence Aggregation

The current scoring formula (\hyperref[sec:methods_kg]{described in the methodology}) aggregates LLM-extracted assertions through a simple citation-weighted tally. While this approach provides a transparent and reproducible baseline, it leaves substantial room for methodological sophistication. We identify six directions, ordered by expected impact, with the first three specifically addressing the limitations of tally-based evidence synthesis.

### Hierarchical Bayesian Hypothesis Scoring

The most direct extension replaces the additive tally with a **hierarchical Bayesian model** that treats each hypothesis score as a latent variable inferred from noisy assertion observations. Under this formulation, each assertion $a_i$ contributes a likelihood term $P(a_i | \theta_H, \sigma)$ parameterized by the hypothesis-level evidence strength $\theta_H$ and an observation noise term $\sigma$ capturing LLM extraction uncertainty. A hierarchical prior $\theta_H \sim \mathcal{N}(\mu_{\text{field}}, \tau^2)$ pools information across hypotheses, enabling principled shrinkage for hypotheses with sparse evidence (e.g., H6 Clinical Utility, with only 35 assertions). This framework produces posterior credible intervals rather than point estimates, providing uncertainty quantification that the current tally-based scores lack. Temporal dynamics can be modeled through time-varying parameters $\theta_H(t)$ using state-space formulations that re-weight older evidence rather than treating all cumulative assertions equally.

### Causal Evidence Graphs

A second-generation knowledge graph would encode not only assertion-level relationships (paper → supports → hypothesis) but also **causal dependencies among hypotheses** themselves. For example, evidence for predictive coding (H4) often implicitly supports FEP universality (H1), yet the tally-based approach treats them as independent. A causal evidence graph—structured as a directed acyclic graph (DAG) over hypotheses with edge weights learned from co-assertion patterns—would enable cross-hypothesis evidence propagation using belief propagation or variational message passing. This is particularly relevant for the Active Inference literature, where hypotheses are theoretically nested: FEP universality (H1) logically entails predictive coding (H4), and Markov blanket realism (H3) is a prerequisite for certain formulations of H1. Encoding these dependencies would prevent the double-counting of evidence from papers that support multiple related hypotheses and enable identification of which specific claims drive support for downstream hypotheses. The resulting causal structure itself would be a scientific contribution—a formal map of evidential dependencies within the field's theoretical architecture.

### Evidential Diversity and Source Weighting

The current formula weights assertions by $\log(1 + \text{citations}) \cdot \text{confidence}$, treating all assertion sources symmetrically. A more nuanced approach would introduce an **evidential diversity index** that downweights correlated evidence from papers sharing authors, institutions, or methodological approaches. Concretely, assertions could be weighted by the inverse of their similarity to previously counted assertions, measured via cosine similarity of paper embeddings. This would address the observation that H1 (FEP universality) accumulates a large neutral tally partly because many A2 (philosophy) papers invoke the FEP without independently testing it—a form of evidential redundancy that inflates the evidence base without adding independent information. Additionally, assertions could be stratified by evidence type (empirical, theoretical, review) with configurable type-specific weights, enabling users to compute evidence scores that privilege experimental results over theoretical commentary.

### Additional Directions

1. **Confidence calibration.** A pilot study comparing LLM-generated assertions with domain expert assessments would establish inter-annotator agreement ($\kappa$) and identify systematic biases. This is the prerequisite for all downstream improvements.

2. **Agentic LLM Extractors.** Drawing on recent work connecting active inference to artificial reasoning \citep{friston2025active} and proposing AIF as a reward-free alternative for LLM-based agents \citep{wen2025missing}, replacing static prompt templates with goal-directed, actor-critic LLM architectures could significantly improve confidence calibration. The Renormalization Generative Model (RGM) architecture introduced by Friston et al. \citep{friston2025active}—which achieves 99.8\% MNIST accuracy with 90\% less training data through scale-free hierarchical generative modeling—demonstrates that principled AIF architectures can reach strong sample efficiency. Applied to literature extraction, analogous object-centric, uncertainty-aware reasoning could enhance extraction quality by treating each paper's abstract as a structured observation to be parsed against hypothesis definitions with principled uncertainty quantification. The broader convergence between AIF and deep learning demonstrated by AXIOM \citep{heins2025axiom}—which outperforms DreamerV3 through principled active inference planning—further validates this trajectory.

3. **Domain adaptation.** The framework is domain-agnostic by design. Adaptation to foundation models, quantum computing, or synthetic biology requires only domain-specific hypothesis definitions and keyword lists within the A/B/C taxonomy.

4. **Energy-Based Model convergence.** Systematic cross-referencing of the Active Inference literature with the broader Energy-Based Model research program \citep{lecun2006tutorial}—including Helmholtz machines \citep{dayan1995helmholtz}, contrastive divergence training \citep{hinton2002training}, and variational autoencoders \citep{kingma2014auto}—would illuminate the mathematical convergence between variational free energy minimization in biological systems and energy-based learning in artificial systems. This analysis could reveal shared mathematical structures that are currently obscured by disciplinary siloing.

## Broader Impact

The vision motivating this work is straightforward: a living literature review—a continuously updated knowledge graph tracking what a field claims, what evidence supports those claims, and where the frontiers of understanding lie. This vision builds on the foundation established by Knight et al. \citep{knight2022fep}, who identified the development of systems that could "encompass increased scope of relevant works," "integrate multiple forms of annotation and participation," and "facilitate integration of manual and artificial contributions" as key goals for the field.

By demonstrating that LLM-driven assertion extraction can produce scalable, queryable representations of scientific evidence—processing $N = 849$ papers spanning approximately two and a half decades (2005–2026), extracting structured assertions, and evaluating 8 core hypotheses—this work provides a reusable architecture for realizing this vision. The corpus window begins in 2005 to capture Energy-Based Model and variational Bayesian antecedents that predate the Free Energy Principle label itself; the formal FEP was introduced in 2006 \citep{friston2006free} and reached its core elaboration by 2010 \citep{friston2010free}. The citation network metrics (1,678 edges, 0.23\% density, mean in-degree 2.0) characterize the field's structure, which has grown at a 16.99\% CAGR while diversifying across 5 application domains.

The limitations of keyword-based retrieval across disjoint academic repositories mean that any retrieved corpus will contain both false positives and false negatives. There is no single threshold that perfectly defines inclusion or exclusion for a dynamic, interdisciplinary research field. The primary contribution of this work is therefore not a definitive corpus but an open-source, modularly updatable, and versioned software package. This tool is built in reference to custom literature bibliographies that can be iteratively curated for relevance by the community.

The combination of multi-source retrieval, LLM-based extraction, and probabilistic knowledge graph construction provides a reusable template that advances each of these goals. A complementary pathway is emerging through Retrieval-Augmented Generation (RAG) architectures that ground LLMs directly in knowledge graphs, reducing hallucination and enabling real-time, context-aware reasoning over structured evidence \citep{fan2024survey}. Integrating our nanopublication graph into such a RAG system would enable natural-language querying of the evidence base, further lowering the barrier for community engagement. The recent release of nanopub-js v0.1.0 \citep{kuhn2026nanopubjs}—enabling browser-based creation, signing, and querying of nanopublications—lowers the barrier for community-contributed assertions, bringing the participatory evidence curation envisioned by Knight et al. within practical reach. As LLM capabilities improve and standardized metadata adoption grows, the cost of maintaining such systems will decrease while their utility increases. By open-sourcing the pipeline and publishing the schema, we provide both a concrete tool for the Active Inference community and a modular blueprint that other fields can adapt and refine.

**Data and code availability.** The pipeline source code, configuration, and manuscript templates are available in the project repository (see \texttt{metadata.repository} in \texttt{config.yaml} or the manuscript front matter). Nanopublications are persisted as JSON Lines (for incremental runs) and RDF/TriG (nanopub.net-compliant); both can be archived with the code release or on a data repository (e.g., Zenodo) for citation and long-term access.

Community recommendations, actionable implications, and open questions arising from this work are detailed in the \hyperref[sec:discussion]{Discussion}.



```{=latex}
\newpage
```


# Discussion: Implications and Community Recommendations \label{sec:discussion}

## Relationship to Prior Development Directions

Knight, Cordes, and Friedman \citep{knight2022fep} identified six development directions for systematic Active Inference literature analysis: (1) increased scope of relevant works, (2) richer annotation schemes, (3) integration of manual and artificial contributions, (4) transferable approaches across fields, (5) participation by diverse contributors, and (6) updated analyses tracking the field's evolution. This pipeline directly addresses directions 1, 2, 3, and 6: it scales retrieval to three databases, replaces manual annotation with LLM-driven extraction while preserving human review pathways, and produces a pipeline designed for incremental re-execution as new literature appears. Directions 4 and 5—cross-field transferability and community participation—remain open and are addressed below.

## Tactical and Strategic Priorities

### Demand Rigorous Reporting Metadata

Papers should systematically report DOIs, ORCIDs, and explicit hypothesis commitments. Submitted preprints should forward-link to their published versions to prevent fragmented citation subgraphs. Our extraction pipeline prioritizes the DOI as the canonical identifier; failing that, deduplication cascades to arXiv IDs, Semantic Scholar IDs, and OpenAlex IDs. Broad DOI adoption would resolve the cross-source mismatch problem, enabling higher-resolution evidence mapping.

### Deploy Open Knowledge Graph Infrastructure

We advocate the deployment of a federated nanopublication server architecture to house community-contributed assertions, enabling a continuously updated living literature review that incorporates new findings as they are published. The release of nanopub-js v0.1.0 \citep{kuhn2026nanopubjs} makes browser-based creation and querying of nanopublications practical, enabling researchers to contribute assertions directly from web interfaces without requiring command-line tools or Python environments. Integrating this pipeline with the Active Inference Institute's Knowledge-Engineering infrastructure \citep{knight2022fep} would provide the standardized semantic vocabulary necessary for rigorous cross-study comparison.

### Standardize the Ontological Lexicon

Immediate future extraction cycles should align assertion predicates with the formally curated Active Inference Ontology. Enforcing shared ontological primitives across studies will accelerate the aggregation of evidence from otherwise siloed research communities, advancing the interoperability goal outlined by Knight et al. \citep{knight2022fep}.

## Empirical and Theoretical Imperatives

### Architect Unified Performance Benchmarks

The computational tools domain (B) lacks standardized performance benchmarks for direct comparison against deep reinforcement learning architectures. Establishing baseline metrics analogous to standard RL environments (e.g., OpenAI Gym) is a prerequisite for transitioning theoretical proposals into applied systems.

### Prioritize Empirical Validation

Biology (C5) and Language (C3) have established theoretical frameworks but limited empirical validation. Targeted experiments designed to test specific FEP-derived predictions—such as demonstrating morphogenesis as Bayesian inference or measuring active inference advantages in language tasks—would strengthen the evidence base beyond what further theoretical work alone can achieve.

## Living Review Maintenance

The pipeline is designed for continuous operation rather than one-time analysis. Incremental resume capabilities (checkpoint-based assertion extraction, merge-on-add corpus deduplication) enable periodic re-execution as new papers are indexed. We envision a maintenance cycle in which the pipeline is re-run quarterly, with updated hypothesis scores and field statistics published alongside the pipeline release. Community contributors can extend the framework by adding custom hypothesis definitions, alternative keyword taxonomies, or domain-specific extraction prompts—all configurable via the YAML configuration file without modifying source code. A complementary long-term trajectory is toward RAG-enabled access: integrating the nanopublication knowledge graph into a Retrieval-Augmented Generation architecture \citep{fan2024survey} would enable natural-language querying of the evidence base, making quantitative literature synthesis accessible to researchers without programming expertise.

## Open Questions

This meta-analysis surfaces questions warranting dedicated investigation:

- **Classifier calibration:** What proportion of A1 papers would be reclassified under embedding-based or expert-annotated schemes?
- **Scoring sensitivity:** How sensitive are hypothesis scores to the choice of weighting function? Would square-root or linear weights qualitatively change the evidence landscape?
- **Model sensitivity:** How much do hypothesis scores vary across different LLM models? Are some hypotheses more robust to model choice than others?
- **Domain boundaries:** Do domain boundaries stabilize as the field matures, or continue to shift? Is the 8-category (A/B/C) taxonomy optimal?
- **Cross-hypothesis evidence:** When a neuroscience (C1) paper supports predictive coding, does this constitute evidence for scalability? How should cross-hypothesis evidence be handled?
- **Temporal dynamics:** Do hypotheses follow predictable lifecycles (emergence → rapid support → contestation → resolution), and can these patterns inform research prioritization?
- **Falsifiability operationalization:** H1 (FEP Universality) produces a predominantly neutral evidence profile—consistent with the falsifiability critique that the FEP can accommodate any behavior without generating distinctive predictions \citep{colombo2021free}. Can hypothesis definitions be reformulated to require papers to generate and test a specific empirical prediction before contributing a supporting assertion, thereby distinguishing generative from merely descriptive invocations of the FEP?
- **Scalability gap:** H5 (AIF Scalability) shows a strongly positive trend, yet head-to-head comparisons with deep RL remain limited to a handful of benchmarks. At what state-space dimensionality and reward density does the performance advantage of model-based AIF (via expected free energy exploration) erode relative to model-free RL?
- **EFE decomposition sensitivity:** Variational message passing formulations \citep{champion2021realizing} connect EFE decomposition into risk, ambiguity, epistemic, and instrumental components to practical planning algorithms. When the scoring formula is stratified by decomposition (e.g., risk-driven vs. epistemic-driven papers), do the resulting hypothesis scores differ? This would reveal whether the field's evidence base is driven primarily by curiosity-driven exploration or goal-directed application.
- **Energy-Based Model convergence:** To what extent do the mathematical structures underlying variational free energy minimization in Active Inference and energy function optimization in Energy-Based Models (Helmholtz machines, Boltzmann machines, VAEs) converge? Are there transferable inference algorithms or architectural insights at this intersection?



```{=latex}
\newpage
```


# Appendix B: Tooling and Infrastructure \label{sec:tooling}

The practical utility of a computational meta-analysis depends on robust tooling at each pipeline stage: assertion extraction, modeling and simulation, knowledge graph infrastructure, and quality assurance.

## LLM-Based Assertion Extraction

Extracting structured assertions from unstructured text is the most labor-intensive component of knowledge graph construction. Manual annotation produces high-quality results but does not scale to corpora of thousands of papers—a constraint demonstrated by Knight et al. \citep{knight2022fep}, whose systematic literature analysis of FEP and Active Inference publications required manual coding of structural, visual, and mathematical features for hundreds of annotated papers. We implement a hybrid approach: LLMs perform initial extraction, with human review for validation and correction.

Our extraction pipeline deploys a locally hosted LLM through Ollama \citep{ollama2024}. Each paper's abstract is assessed against the eight hypothesis definitions in a structured prompt requesting a JSON array of assessments. Unlike keyword matching, which detects only topical terms, the LLM evaluates the *semantic relationship* between a paper's claims and each hypothesis. Papers critiquing the FEP correctly receive "contradicts" assessments for FEP Universality (H1), while methodology tutorials receive "neutral" assessments reflecting their pedagogical character. Detailed prompt engineering, schemas, and failure modes are documented in the supplementary extraction pipeline (see the \hyperref[sec:extraction_pipeline]{extraction pipeline section}).

<!-- See 02b_methods_extraction.md for detailed pipeline documentation -->

## Software Ecosystem

The Active Inference community has developed a rapidly growing ecosystem of open-source tools spanning multiple programming languages, inference paradigms, and application domains. This section provides a comprehensive survey of publicly available implementations as of early 2026, organized by functional category. We emphasize tools with accessible source code, as open-source availability is a prerequisite for reproducibility and community-driven validation.

### General-Purpose Frameworks

Four general-purpose frameworks dominate the landscape, collectively covering discrete, continuous, and real-time inference:

**pymdp.** The pymdp library \citep{heins2022pymdp} provides a Python implementation of active inference for discrete state-space POMDPs, supporting message passing on factor graphs, policy inference via expected free energy, and hierarchical generative models. It has become the standard entry point for algorithm development and the most widely forked AIF repository.

**SPM.** The SPM package (Wellcome Centre for Human Neuroimaging) includes MATLAB implementations of Dynamic Causal Modeling and variational Bayesian inference under the FEP. It remains the reference implementation for neuroimaging applications and houses the original Friston-group POMDP scripts.

**RxInfer.jl.** RxInfer is a Julia package for reactive message-passing-based Bayesian inference, supporting real-time and streaming inference suitable for robotics and online learning. Version 4.0.0 (early 2025) \citep{rxinfer2025} introduced projected constraints and adaptive inference optimized for dynamic data streams and autonomous systems. The RxInfer ecosystem includes extensive tutorials covering Bayesian linear regression, hidden Markov models, Kalman filtering, Gaussian process regression, hierarchical Gaussian filters, nonlinear sensor fusion, and active inference mountain car control, available at the [official documentation](https://reactivebayes.github.io/RxInfer.jl/stable/) and the [Learnable Loop](https://learnableloop.com/) tutorial portal.

**Cpp-AIF.** The Cpp-AIF header-only C++ library \citep{gregoretti2023cppaif} implements active inference for discrete POMDPs with multicore parallelization of the most demanding computational kernels—multidimensional inner products for expected free energy computation and state estimation. By abstracting the mathematical details behind a high-level API, Cpp-AIF targets embedded systems and performance-critical applications where Python overhead is prohibitive.

**FEPS.** Free Energy Projective Simulation \citep{pazem2024feps} combines active inference with interpretable graphical policy representations, enabling agents to plan via expected free energy while exposing decision logic as human-readable policy graphs. FEPS targets interpretable reinforcement learning tasks where black-box deep agents are undesirable—behavioral biology, clinical decision support, and safety-critical robotics.

### Deep Active Inference

Scaling active inference beyond tabular POMDPs to high-dimensional observation spaces requires neural network function approximators. A growing body of deep active inference implementations explores this direction:

The foundational deep AIF agent of Fountas et al. \citep{fountas2020deep} introduced Monte-Carlo tree search over learned latent spaces, achieving non-trivial Atari performance. Millidge's DeepActiveInference extended this to continuous control with backpropagation-based world models \citep{millidge2020deep}. Champion's Branching-Time Active Inference (BTAI\_3MF) and its deep variant (Deep\_BTAI\_3MF) implement tree-structured planning under the free energy objective, scaling active inference to partially observable environments with multi-step lookahead \citep{champion2021realizing}. Most recently, AXIOM \citep{heins2025axiom} achieves competitive Gameworld 10k benchmark performance using expanding object-centric world models, learning in minutes rather than hours—a landmark result for scalability.

### Predictive Coding and Neural Generative Coding

Predictive coding provides the core computational mechanism linking active inference to neuroscience. Several implementations offer accessible entry points:

**ngc-learn.** The Neural Generative Coding library (ngc-learn v3.0, JAX-based) provides a framework for simulating neurobiologically-plausible systems using predictive coding circuits, Hebbian learning, and spike-based dynamics. It supports constructing arbitrary neural generative models without backpropagation, directly instantiating the FEP's prediction-error minimization at the circuit level.

**Active Neural Generative Coding (ANGC).** ANGC implements a form of active inference using paired predictive coding circuits—an actor/policy circuit and a world/transition model—that co-evolve across episodes without backpropagation. The agent decomposes behavior into epistemic foraging (uncertainty reduction) and instrumental (reward-seeking) terms, operating with sparse rewards where classical DQN requires dense reward engineering.

**Predictive Coding $\approx$ Backprop.** Millidge et al. demonstrate that predictive coding networks can approximate backpropagation along arbitrary computational graphs \citep{millidge2022predictive}, providing a biologically plausible alternative to gradient descent. The [PredictiveCodingBackprop](https://github.com/BerenMillidge/PredictiveCodingBackprop) repository provides the reference implementation.

### Benchmarking Progress

The scalability gap between AIF and deep reinforcement learning has been a central limitation of the tools domain. Recent work demonstrates significant progress on two fronts. First, AXIOM \citep{heins2025axiom} outperforms state-of-the-art model-based deep RL agents including DreamerV3 on the Gameworld 10k benchmark, while using substantially smaller model sizes; its object-centric scene decomposition enables sample-efficient learning from structured representations rather than raw pixel memorization. Second, variational message passing formulations \citep{champion2021realizing} connect EFE decomposition—into risk, ambiguity, epistemic (information-seeking), and instrumental (goal-reaching) components—to practical planning algorithms, advancing the theoretical justification for EFE-based policy selection (H2). Separately, Friston et al. \citep{friston2025active} introduce structure learning via Bayesian Model Reduction as a principled approach to artificial reasoning under active inference.

### Comprehensive Open-Source Tool Survey

The following table catalogs the principal open-source Active Inference implementations surveyed, organized by functional category. For each tool we list the primary language, the application domain, and the associated publication or repository. This table is intended as a navigational resource for researchers seeking existing implementations relevant to specific hypotheses (H1–H8) or application domains (A1–C5).

\begin{center}
\small
\begin{longtable}{p{3.2cm} p{1.6cm} p{4.4cm} p{2.5cm}}
\hline
\textbf{Tool / Repository} & \textbf{Lang.} & \textbf{Description} & \textbf{Paper / Source} \\
\hline
\endfirsthead
\hline
\textbf{Tool / Repository} & \textbf{Lang.} & \textbf{Description} & \textbf{Paper / Source} \\
\hline
\endhead
\multicolumn{4}{c}{\textit{General-Purpose Frameworks}} \\
\hline
pymdp & Python & Discrete POMDP active inference; factor graphs, hierarchical models & \cite{heins2022pymdp} \\
SPM & MATLAB & DCM, variational Bayes; neuroimaging reference implementation & \cite{friston2017active} \\
RxInfer.jl & Julia & Reactive message passing; real-time streaming Bayesian inference & \cite{rxinfer2025} \\
Cpp-AIF & C++ & Header-only POMDP AIF library with multicore parallelization & \cite{gregoretti2023cppaif} \\
FEPS & Python & EFE on interpretable policy graphs; projective simulation & \cite{pazem2024feps} \\
ActivPynference & Python & Discrete AIF with factor-graph message passing; educational focus & — \\
pypc & Python & Predictive coding inference engine for continuous models & — \\
ActiveInferAnts & Rust & Rust-native AIF framework with WASM compilation target & — \\
\hline
\multicolumn{4}{c}{\textit{Deep Active Inference}} \\
\hline
deep-active-inference-mc & Python & Monte-Carlo tree search in learned latent spaces; Atari & \cite{fountas2020deep} \\
DeepActiveInference & Python & Continuous deep AIF with backprop-based world models & \cite{millidge2020deep} \\
BTAI\_3MF & Python & Branching-time AIF with multi-step tree planning & \cite{champion2021realizing} \\
Deep\_BTAI\_3MF & Python & Deep neural variant of BTAI with learned state spaces & \cite{champion2021realizing} \\
OO-BTAI\_3MF & Python & Object-oriented BTAI variant for structured environments & — \\
AXIOM & Python & Object-centric world models; Gameworld 10k in minutes, beats DreamerV3 & \cite{heins2025axiom} \\
Deep-AIF-POMDPs & Python & Deep AIF for partially observable MDPs & — \\
Homing-Pigeon & Python & Navigation agent using deep active inference & — \\
active-inference (Voostrum) & Python & Continuous deep AIF with learned generative models & arXiv:2406.07726 \\
\hline
\multicolumn{4}{c}{\textit{Predictive Coding \& Neural Generative Coding}} \\
\hline
ngc-learn & Python/JAX & Neurobiological simulation; predictive coding circuits, Hebbian learning & — \\
ANGC & Python & Backprop-free AIF agent with paired PC circuits & AAAI 2022 \\
PredictiveCodingBackprop & Python & Predictive coding approximates backprop on arbitrary graphs & \cite{millidge2022predictive} \\
Supervised-Predictive-Coding & Python & Supervised learning via hierarchical predictive coding & — \\
predcoding & Python & Minimal predictive coding implementation & — \\
pybrid & Python & Hybrid predictive coding and active inference library & — \\
nmpassing & Python & Neural message passing for PC networks & — \\
\hline
\multicolumn{4}{c}{\textit{Neuroscience, Embodied \& Biological}} \\
\hline
allostasis & Python & Allostatic regulation via AIF; interoceptive inference & bioRxiv:2021.02.16 \\
ants & Python & Ant foraging simulation with stigmergic AIF agents & \cite{heins2024collective} \\
Reward\_Bases & Python & Reward-basis function representations under AIF & bioRxiv:2022.04.14 \\
action-oriented & Python & Action-oriented predictive processing models & \cite{tschantz2020action} \\
Biofirm & Python & Bioregional stewardship via organizational AIF & — \\
bayesian-mechanics-sdes & Python & Bayesian mechanics: SDE simulations of Markov blanket dynamics & arXiv:2206.02629 \\
reverse\_engineering & MATLAB & Reverse-engineering neural dynamics under the FEP & — \\
\hline
\multicolumn{4}{c}{\textit{Multi-Agent \& Social Dynamics}} \\
\hline
opinion\_dynamics & Python & Opinion dynamics and belief formation via AIF & — \\
network-actinf & Python & Network-level active inference with coupled agents & — \\
Variational-Capsule-Routing & Python & Capsule networks with variational inference routing & AAAI 2020 \\
Active-Inference-Successor & Python & Successor representations under active inference & — \\
\hline
\multicolumn{4}{c}{\textit{Domain-Specific Applications}} \\
\hline
adaptive\_aif\_agents\_fl & Python & Adaptive AIF agents for federated learning & arXiv:2410.09099 \\
smartville & Python & IoT smart building control via AIF under partial observability & TechRxiv 2025 \\
FEP\_Blorpomon & Python & Game-theoretic AIF agent demonstration & — \\
MountainCarAI & Python & Mountain car control via active inference & — \\
rl-inference & Python & Bridging RL and active inference policy selection & arXiv:2002.12636 \\
EFE-GLean & Python & Expected free energy with generalized learning & Entropy 2025 \\
EFEasVFE & Julia & EFE reformulated as variational free energy & — \\
Robust-FE-Minimization & Python & Robust decision-making via free energy minimization & arXiv:2503.13223 \\
\hline
\multicolumn{4}{c}{\textit{Tutorials \& Educational Resources}} \\
\hline
Active-Inference-from-Scratch & Python & Step-by-step AIF implementation tutorial & — \\
IC2S2-AIF-Tutorial & Python & Computational social science AIF tutorial & — \\
julia4ta tutorials (9x10--12) & Julia & RxInfer-based AIF agent tutorials & — \\
ActInf Textbook Colab & Python & Interactive notebooks for \cite{parr2022active} & — \\
deep\_aif\_workshop & Python & Workshop materials for deep active inference & — \\
AdaptiveResonance.jl & Julia & Adaptive resonance theory models in Julia & — \\
\hline
\end{longtable}
\end{center}

### Comparative Feature Matrix

| Feature | pymdp | SPM | RxInfer.jl | Cpp-AIF | FEPS | ngc-learn |
| --- | --- | --- | --- | --- | --- | --- |
| **Language** | Python | MATLAB | Julia | C++ | Python | Python/JAX |
| **State Spaces** | Discrete | Discrete + Continuous | Continuous (factor graphs) | Discrete | Discrete | Continuous |
| **Inference** | Message passing | Variational Bayes | Reactive message passing | EFE + state estimation | EFE on policy graphs | Predictive coding |
| **Deep AIF** | Partial | No | Via custom factors | No | No (interpretable) | Yes (neural circuits) |
| **Real-time** | No | No | Yes (streaming) | Yes (multicore) | No | No |
| **Hierarchical** | Yes | Yes (DCM) | Yes | Yes | No | Yes |
| **GPU** | No | No | No | CPU (multicore) | No | Yes (JAX) |
| **License** | MIT | GPL | MIT | MIT | MIT | BSD-3 |
| **Primary Use** | Research prototyping | Neuroimaging | Robotics / online learning | Embedded systems | Interpretable RL | NeuroAI simulation |

The complementary strengths across these packages reflect a fragmented but maturing ecosystem. The survey reveals several notable patterns: (1) Python dominates (~75\% of implementations), with Julia emerging as the preferred alternative for performance-critical applications; (2) discrete POMDP implementations outnumber continuous variants by approximately 3:1, reflecting pymdp's community influence; (3) deep active inference implementations are concentrated in a small number of research groups (Champion, Millidge, Fountas, Heins), suggesting high barriers to entry; (4) multi-agent and social AIF implementations remain sparse relative to single-agent tools; and (5) domain-specific applications (IoT, federated learning, smart buildings) represent the newest and fastest-growing category, aligning with the temporal growth patterns observed in the C-domain (applied) subfields. The variational free energy foundations shared by Active Inference and Energy-Based Models (EBMs)—including Helmholtz machines \citep{dayan1995helmholtz}, Boltzmann machines \citep{hinton2002training}, and variational autoencoders \citep{kingma2014auto}—suggest that interoperability with mainstream deep generative modeling frameworks (PyTorch, JAX) could bridge these parallel research programs.

## Knowledge Graph Infrastructure

Our knowledge graph uses an RDF-compatible schema deployable on standard semantic web infrastructure. The nanopublication model \citep{groth2010anatomy, kuhn2016decentralized} provides a principled atomic unit of scientific evidence: each nanopublication packages a single assertion (e.g., "Paper X supports Hypothesis Y") with explicit provenance and publication metadata in four named RDF graphs (Head, Assertion, Provenance, Publication Info). This structure satisfies the FAIR data principles by design: nanopublications are **F**indable via URI-based identification, **A**ccessible through standard RDF protocols, **I**nteroperable via W3C-standard TriG serialization, and **R**eusable with explicit provenance and CC0 licensing. The full RDF schema and a TriG serialization example are presented in the \hyperref[sec:methods_kg]{methodology} and \hyperref[sec:appendix_rdf]{Appendix~A.5}.

The engineering trade-offs among the three deployment options are straightforward:

**Nanopublication servers** provide decentralized, content-addressed storage. The pipeline writes nanopublications in two forms: JSON Lines (for incremental checkpointing and tooling) and RDF/TriG per the [nanopublication standard](https://nanopub.net/) (Assertion, Provenance, Publication Info), suitable for the nanopublication network and FAIR deployment. The recent release of nanopub-js v0.1.0 \citep{kuhn2026nanopubjs}—a JavaScript library enabling browser-based creation, signing, and querying of nanopublications—opens the possibility of community-contributed assertions directly from web interfaces, lowering the barrier to participatory evidence curation. Future integration with Trusty URIs \citep{kuhn2014trusty} would provide cryptographic content verification and persistent identifiers for each nanopublication.

**RDF stores** (e.g., Apache Jena Fuseki, Blazegraph, Oxigraph) enable SPARQL queries such as "find all papers supporting hypothesis H published after 2020 in the neuroscience domain (C1)." The cost is operational overhead and query latency.

**Property graph databases** (e.g., Neo4j) prioritize traversal performance for path queries and community detection, at the expense of semantic web compatibility.

The [Active Inference Ontology namespace](http://activeinference.institute/ontology/) ensures integration with external ontologies and linked data resources.

## Multi-Level Quality Assurance

Quality assurance operates at four levels.

### Assertion-Level Validation

Assertions below a configurable confidence threshold (default 0.5) are flagged for review. Inter-annotator agreement ($\kappa$) is computed when multiple annotators assess the same paper.

### Graph-Level Consistency Checks

Consistency checks verify that all nodes link to valid targets and no orphan nodes exist. Coverage metrics track the proportion of annotated papers.

### Score-Level Unit Testing

Hypothesis scoring is validated through unit tests with synthetic data verifying boundary conditions (all-support → +1, all-contradict → −1, balanced → 0). Sensitivity analysis varies confidence thresholds and citation weighting.

### Pipeline-Level Test Coverage

Test-driven development enforces 90\% minimum code coverage on project modules and 60\% on shared infrastructure, with real data and computation (no mocking).

### Quality Thresholds

| Level | Metric | Threshold | On Failure |
| --- | --- | --- | --- |
| Assertion | Confidence | $\geq 0.5$ | Flag for review |
| Assertion | Inter-annotator $\kappa$ | $\geq 0.6$ | Re-annotate |
| Graph | Orphan node ratio | $= 0$ | Reject build |
| Graph | Corpus coverage | $\geq 80\%$ | Warning |
| Score | Boundary tests | All pass | Block release |
| Pipeline | Code coverage | $\geq 90\%$ | Block merge |
| Pipeline | Test pass rate | $100\%$ | Block release |

The hypothesis evidence results, temporal dynamics of evidence accumulation, and assertion analysis are presented in the dedicated hypothesis results section (see the \hyperref[sec:hypothesis_results]{hypothesis results section}).



```{=latex}
\newpage
```


# Appendix A: Mathematical and Algorithmic Details \label{sec:technical_appendix}

_This appendix collects the formal mathematical definitions, derivations, and algorithmic specifications referenced from the main methodology section._

## A.1 Citation-Weighted Hypothesis Scoring Formula \label{sec:appendix_scoring}

For each hypothesis $H$, we compute a citation-weighted evidence score aggregating all assertions relevant to $H$:

\begin{equation}
\text{score}(H) = \frac{\sum_{a \in S(H)} w(a) - \sum_{a \in C(H)} w(a)}{\sum_{a \in A(H)} w(a)}
\end{equation}

where $S(H)$ is the set of supporting assertions, $C(H)$ is the set of contradicting assertions, $A(H)$ is all assertions for $H$ (including neutral), and the weight function is:

\begin{equation}
w(a) = \log(1 + \text{citations}(a)) \cdot \text{confidence}(a)
\end{equation}

The logarithmic citation weighting ensures that highly cited papers carry more influence while preventing any single blockbuster paper from dominating the score. The score lies in $[-1, 1]$: values near $+1$ indicate strong supporting evidence, values near $-1$ indicate strong contradicting evidence, and values near $0$ indicate balanced or insufficient evidence.

**Temporal aggregation.** We additionally compute temporal trends by evaluating the cumulative score at each year $t$, using only assertions from papers published in year $\leq t$:

\begin{equation}
\text{score}(H, t) = \frac{\sum_{a \in S(H,t)} w(a) - \sum_{a \in C(H,t)} w(a)}{\sum_{a \in A(H,t)} w(a)}
\end{equation}

This reveals whether support for a hypothesis is growing, declining, or plateauing over time.

## A.2 Non-negative Matrix Factorization (NMF) for Topic Modeling \label{sec:appendix_nmf}

We apply NMF to the TF-IDF matrix of the corpus to discover latent topics. Given the document-term matrix $V \in \mathbb{R}^{n \times m}_{\geq 0}$, NMF finds factor matrices $W \in \mathbb{R}^{n \times k}_{\geq 0}$ and $H \in \mathbb{R}^{k \times m}_{\geq 0}$ such that $V \approx WH$, where $k$ is the number of topics.

We use multiplicative update rules \citep{lee1999nmf}:

\begin{equation}
H \leftarrow H \odot \frac{W^T V}{W^T W H + \epsilon}, \quad W \leftarrow W \odot \frac{V H^T}{W H H^T + \epsilon}
\end{equation}

with $\epsilon = 10^{-10}$ for numerical stability and a fixed random seed of 42 for reproducibility.

**Term-Frequency Inverse Document Frequency (TF-IDF).** The document-term matrix is constructed using TF-IDF weighting \citep{salton1975vector}. For term $t$ in document $d$:

\begin{equation}
\text{TF-IDF}(t, d) = \text{tf}(t, d) \cdot \log\!\left(\frac{N}{\text{df}(t)}\right)
\end{equation}

where $\text{tf}(t, d)$ is the term frequency, $N$ is the total number of documents, and $\text{df}(t)$ is the document frequency of term $t$.

## A.3 Field Growth-Rate Estimation \label{sec:appendix_growth}

The **mean year-over-year growth rate** $\bar{g}$ is the arithmetic mean of annual growth rates computed only for years where the prior year had non-zero publications:

\begin{equation}
\bar{g} = \frac{1}{|Y|} \sum_{y \in Y} \frac{n_y - n_{y-1}}{n_{y-1}}
\end{equation}

where $Y = \{y : n_{y-1} > 0\}$ and $n_y$ is the number of publications in year $y$.

The **doubling time** $t_d$ is derived from the mean annual growth rate:

\begin{equation}
t_d = \frac{\ln 2}{\ln(1 + \bar{g})}
\end{equation}

The **compound annual growth rate** (CAGR) over the full span $[y_0, y_T]$ is:

\begin{equation}
\text{CAGR} = \left(\frac{n_{\text{cumulative}}(y_T)}{n_{\text{cumulative}}(y_0)}\right)^{1/(y_T - y_0)} - 1
\end{equation}

For the current corpus, CAGR $= 16.99\%$. The more recent growth phase (2010--2026) exhibits substantially higher annualized growth.

## A.4 Advanced Visualization Methods \label{sec:appendix_viz}

### PCA of TF-IDF Embeddings

Principal Component Analysis (PCA) is applied to the TF-IDF matrix $V$ to project each document into a 2-D space. The projection preserves the directions of maximum variance, enabling visual inspection of document clustering by domain. Loading arrows overlay the top-variance terms onto the scatter plot, showing which vocabulary drives the principal components.

### Hierarchical Clustering Dendrogram

For each domain $s$, we compute the centroid $\bar{v}_s = \frac{1}{|D_s|} \sum_{d \in D_s} v_d$ where $D_s$ is the set of documents in domain $s$ and $v_d$ is the TF-IDF vector of document $d$. Ward linkage is applied to the centroid matrix to produce a hierarchical clustering dendrogram showing semantic proximity between domains.

### Term Heatmap

For each domain $s$ and term $t$, we compute the mean TF-IDF weight $\bar{w}_{s,t} = \frac{1}{|D_s|} \sum_{d \in D_s} \text{TF-IDF}(t, d)$. The heatmap displays $\bar{w}_{s,t}$ for the top-$k$ terms (by global document frequency) across all domains, with cell intensity proportional to mean weight. This reveals distinctive vocabulary patterns that differentiate domains beyond the keyword-level classification used for subfield assignment.

### Term Co-occurrence Matrix

The co-occurrence matrix $C \in \mathbb{R}^{k \times k}$ counts the number of documents in which two terms appear together. For top-$k$ terms by document frequency, $C_{ij} = |\{d : t_i \in d \land t_j \in d\}|$. The matrix is normalized to $[0, 1]$ by dividing by the maximum entry and visualized as a symmetric heatmap.

## A.5 Nanopublication RDF Schema \label{sec:appendix_rdf}

Each nanopublication is serialized to RDF/TriG per the nanopublication standard \citep{groth2010anatomy, kuhn2016decentralized}, producing four named graphs. The following annotated example illustrates the structure for a single assertion:

```trig
@prefix np: <http://www.nanopub.org/nschema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix aif: <http://activeinference.institute/ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# HEAD GRAPH: links nanopub to its three component graphs
<http://activeinference.institute/nanopub/a1b2c3d4e5f6#head> {
  <http://activeinference.institute/nanopub/a1b2c3d4e5f6>
    a np:Nanopublication ;
    np:hasAssertion   <...#assertion> ;
    np:hasProvenance   <...#provenance> ;
    np:hasPublicationInfo <...#pubinfo> .
}

# ASSERTION GRAPH: the core scientific claim
<http://activeinference.institute/nanopub/a1b2c3d4e5f6#assertion> {
  aif:paper/10.1038_nrn2787 aif:asserts aif:assertion/a1b2c3 .
  aif:assertion/a1b2c3
    aif:supports aif:hypothesis/fep_universality ;
    aif:claim "The paper provides foundational support for FEP as a
               unified brain theory."^^xsd:string ;
    aif:confidence "0.85"^^xsd:double ;
    aif:citationCount "5000"^^xsd:integer .
}

# PROVENANCE GRAPH: extraction lineage
<http://activeinference.institute/nanopub/a1b2c3d4e5f6#provenance> {
  aif:assertion/a1b2c3
    prov:wasGeneratedBy  <http://activeinference.institute/nanopub/a1b2c3d4e5f6> ;
    prov:generatedAtTime "2026-01-15T12:00:00+00:00"^^xsd:dateTime ;
    prov:wasAttributedTo "act_inf_metaanalysis/gemma3:4b"^^xsd:string ;
    prov:hadPrimarySource aif:paper/10.1038_nrn2787 .
}

# PUBLICATION INFO GRAPH: nanopublication metadata
<http://activeinference.institute/nanopub/a1b2c3d4e5f6#pubinfo> {
  <http://activeinference.institute/nanopub/a1b2c3d4e5f6>
    dc:created "2026-01-15T12:00:00+00:00"^^xsd:dateTime ;
    dc:creator "act_inf_metaanalysis/gemma3:4b"^^xsd:string ;
    dc:license <https://creativecommons.org/publicdomain/zero/1.0/> .
}
```

### Namespace Definitions

| Prefix | URI | Purpose |
| --- | --- | --- |
| `np:` | `http://www.nanopub.org/nschema#` | Nanopub structural predicates |
| `prov:` | `http://www.w3.org/ns/prov#` | PROV-O provenance model |
| `dc:` | `http://purl.org/dc/terms/` | Dublin Core metadata |
| `aif:` | `http://activeinference.institute/ontology/` | Domain-specific predicates |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` | XML Schema datatypes |

### Core Triple Patterns

The knowledge graph encodes five fundamental relationships:

| Triple Pattern | Meaning |
| --- | --- |
| `Paper  --aif:asserts-->      Assertion` | A paper makes a claim |
| `Paper  --aif:cites-->        Paper` | Intra-corpus citation link |
| `Paper  --aif:belongsTo-->    Subfield` | Domain classification |
| `Assertion --aif:supports-->  Hypothesis` | Supporting evidence |
| `Assertion --aif:contradicts--> Hypothesis` | Contradicting evidence |



```{=latex}
\newpage
```


# Notation, Abbreviations, and Hypothesis Definitions

## Mathematical Symbols and Notation

| Symbol | Description |
| --- | --- |
| $N$ | Corpus size (total deduplicated papers) |
| $n$ | Subfield paper count |
| $T$ | Time span in years (for CAGR computation) |
| $w(a)$ | Citation-weighted assertion score: $\log(1 + \text{citations}) \cdot \text{confidence}$ |
| $\text{score}(H)$ | Aggregate evidence score for hypothesis $H$, range $[-1, 1]$ |
| $S(H)$ | Set of supporting assertions for hypothesis $H$ |
| $C(H)$ | Set of contradicting assertions for hypothesis $H$ |
| $A(H)$ | Set of all assertions for hypothesis $H$ |
| $c$ | Assertion confidence, range $[0, 1]$ |
| $d$ | Assertion direction: supports, contradicts, or neutral |
| $k$ | Number of latent topics |
| $\epsilon$ | Numerical stability constant ($10^{-10}$) |
| $\text{CAGR}$ | Compound annual growth rate |
| $t_d$ | Publication doubling time |
| $\bar{g}$ | Mean annual year-over-year growth rate |
| $\kappa$ | Cohen's kappa (inter-annotator agreement) |

## Abbreviations and Acronyms Used

| Abbreviation | Definition |
| --- | --- |
| AIF | Active Inference |
| API | Application Programming Interface |
| CAGR | Compound Annual Growth Rate |
| DCM | Dynamic Causal Modelling |
| DOI | Digital Object Identifier |
| EBM | Energy-Based Model |
| EFE | Expected Free Energy |
| FAIR | Findable, Accessible, Interoperable, Reusable |
| FEP | Free Energy Principle |
| FEPS | Free Energy Projective Simulation |
| HITS | Hyperlink-Induced Topic Search |
| JSON | JavaScript Object Notation |
| JSONL | JSON Lines (newline-delimited JSON) |
| LLM | Large Language Model |
| NMF | Non-negative Matrix Factorization |
| NLP | Natural Language Processing |
| ORCID | Open Researcher and Contributor ID |
| PCA | Principal Component Analysis |
| POMDP | Partially Observable Markov Decision Process |
| PROV-O | PROV Ontology (W3C provenance data model) |
| RBM | Restricted Boltzmann Machine |
| RDF | Resource Description Framework |
| RL | Reinforcement Learning |
| SPARQL | SPARQL Protocol and RDF Query Language |
| SPM | Statistical Parametric Mapping |
| TF-IDF | Term Frequency--Inverse Document Frequency |
| TriG | Terse RDF Triple Language with Named Graphs |
| URI | Uniform Resource Identifier |
| VAE | Variational Autoencoder |
| VFE | Variational Free Energy |

## Standard Hypothesis Definitions and Identifiers

| ID | Hypothesis | Scope |
| --- | --- | --- |
| H1 | FEP Universality: The Free Energy Principle applies universally to all self-organizing systems | A (Core Theory) |
| H2 | AIF Optimality: Active Inference agents achieve optimal decision-making under uncertainty | B (Tools) |
| H3 | Markov Blanket Realism: Markov blankets correspond to real physical boundaries | A (Core Theory) |
| H4 | Predictive Coding: Cortical hierarchies minimize prediction errors via predictive coding | C1 (Neuroscience) |
| H5 | Scalability: Active Inference scales to complex, high-dimensional environments | B (Tools) |
| H6 | Clinical Utility: Active Inference provides clinically useful models of psychiatric conditions | C4 (Psychiatry) |
| H7 | Morphogenesis: The FEP explains morphogenetic and developmental processes | C5 (Biology) |
| H8 | Language AIF: Active Inference provides a viable framework for language processing | C3 (Language) |

## Glossary of Key Terms

| Term | Definition |
| --- | --- |
| **Active Inference** | A framework in which agents minimize expected free energy to select actions, unifying perception, learning, and decision-making under the Free Energy Principle. |
| **Assertion** | A directed, confidence-scored claim linking a paper to a hypothesis (supports, contradicts, or neutral). The basic unit of evidence in the knowledge graph. |
| **Canonical ID** | The unique identifier assigned to each paper during deduplication, following the priority scheme: DOI > arXiv ID > Semantic Scholar ID > OpenAlex ID > title hash. |
| **Expected Free Energy** | A quantity combining epistemic value (information gain) and pragmatic value (goal achievement) that active inference agents minimize over policies. Decomposes equivalently into risk + ambiguity or epistemic + instrumental terms \citep{dacosta2020active}. |
| **Free Energy Principle** | The principle that self-organizing systems minimize variational free energy, an upper bound on surprise, to maintain their structural integrity. |
| **Generative Model** | A probabilistic model specifying the joint distribution over hidden states and observations, encoding an agent's beliefs about how observations are generated. |
| **Knowledge Graph** | A directed graph encoding papers, assertions, hypotheses, and their relationships, serialized in an RDF-compatible format. |
| **Markov Blanket** | A statistical boundary separating internal states from external states, defined as the set of nodes that renders a system conditionally independent of its environment. |
| **Nanopublication** | A minimal, self-contained unit of publishable knowledge consisting of an assertion, provenance metadata, and publication context. |
| **Precision** | The inverse variance of a probability distribution; in active inference, precision weighting determines the influence of prediction errors at different levels of a hierarchy. |
| **Variational Free Energy** | An upper bound on surprise (negative log-evidence) that can be decomposed into complexity (KL divergence from prior) and accuracy (expected log-likelihood). |
| **Greedy Modularity Maximization** | The Clauset-Newman-Moore greedy modularity-maximization algorithm for community detection in networks (implemented via NetworkX `greedy_modularity_communities`). Applied to the citation graph to identify clusters of densely interconnected papers. |
| **PageRank** | A centrality metric originally designed for web page ranking. In citation networks, PageRank identifies highly influential papers that serve as hubs connecting otherwise disconnected subgraphs. |
| **Ward Linkage** | A hierarchical clustering method that minimizes the total within-cluster variance at each merge step. Used to compute dendrograms of domain centroids from mean TF-IDF vectors. |
| **Checkpoint** | A JSON Lines snapshot of LLM extraction progress, recording which papers have been processed and the resulting assertions, enabling incremental resume after interruption. |
| **Incremental Resume** | The pipeline's ability to continue from where a previous run stopped, loading existing corpus/assertions and processing only new papers, controlled by `--clear-corpus` and `--clear-assertions` CLI flags. |
| **LLM Config** | A configuration object specifying the Ollama model name, API URL, temperature, maximum retries, and retry delay for LLM-based assertion extraction. |
| **Named Graph** | An RDF graph identified by a URI, enabling multiple graphs to coexist in a single dataset. Nanopublications use four named graphs (Head, Assertion, Provenance, Publication Info). |
| **TriG** | A TriG (Terse RDF Triple Language) serialization format that extends Turtle with named graph support, used to encode nanopublications as RDF datasets. |
| **FAIR Principles** | A set of guiding principles to make scientific data Findable, Accessible, Interoperable, and Reusable. The pipeline's nanopublications are designed to satisfy all four principles. |
| **Trusty URI** | A URI that contains a cryptographic hash of its content, providing verifiable immutability and content-addressable identification for nanopublications. |
| **Domain Timeline** | Per-domain yearly publication counts showing temporal evolution of research activity across the eight tracked categories (A1–A2, B, C1–C5). |
| **Progressive Parsing** | The pipeline's multi-stage JSON recovery strategy for handling malformed LLM output: direct parse → strip code fences → extract first JSON array → individual element recovery. |
| **Wong Palette** | The colorblind-safe 8-color palette from Wong (2011), used as the standard visualization palette throughout all pipeline-generated figures. |
| **Energy-Based Model** | A class of generative models that define a probability distribution over data through an un-normalized energy function $E(x)$, where lower energy corresponds to higher probability: $p(x) \propto \exp(-E(x))$. Includes Boltzmann machines, Helmholtz machines, and related architectures sharing the variational free energy minimization foundation with the FEP. |
| **Contrastive Divergence** | An approximate gradient-based training algorithm for energy-based models \citep{hinton2002training} that truncates the Markov chain used to estimate the gradient of the log-partition function, enabling practical training of Restricted Boltzmann Machines. |
| **Helmholtz Machine** | A generative model with separate recognition (bottom-up) and generative (top-down) networks trained by the wake-sleep algorithm \citep{dayan1995helmholtz}. A direct precursor to the variational autoencoder and conceptually related to the FEP's recognition-generative duality. |



```{=latex}
\newpage
```


# Bibliography and Cited Works

\bibliography{references}
\bibliographystyle{plainnat}

<!-- References are managed in references.bib. The bibliography is generated automatically during PDF compilation using BibTeX/natbib. All citation keys used in the manuscript (e.g., \citep{friston2010free}) must have corresponding entries in references.bib. -->
