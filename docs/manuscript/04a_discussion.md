# Discussion: Implications and Community Recommendations {#sec:discussion}

## Relationship to Prior Development Directions

Knight, Cordes, and Friedman \citep{knight2022fep} identified six development directions for systematic Active Inference literature analysis: (1) increased scope of relevant works, (2) richer annotation schemes, (3) integration of manual and artificial contributions, (4) transferable approaches across fields, (5) participation by diverse contributors, and (6) updated analyses tracking the field's evolution. This pipeline directly addresses directions 1, 2, 3, and 6: it configures retrieval across three databases, replaces manual annotation with LLM-driven extraction while preserving human review pathways, and produces a pipeline designed for incremental re-execution as new literature appears. The current snapshot records source completion explicitly; directions 4 and 5—cross-field transferability and community participation—remain open and are addressed below.

## Tactical and Strategic Priorities

### Adopt Rigorous Reporting Metadata

Papers should systematically report DOIs, ORCIDs, and explicit hypothesis commitments. Submitted preprints should forward-link to their published versions to prevent fragmented citation subgraphs. Our extraction pipeline prioritizes the DOI as the canonical identifier; failing that, deduplication cascades to arXiv IDs, Semantic Scholar IDs, and OpenAlex IDs. Broad DOI adoption would resolve the cross-source mismatch problem, enabling higher-resolution evidence mapping.

### Explore Open Knowledge Graph Infrastructure

We encourage the exploration of federated nanopublication server architectures to house community-contributed assertions. This would enable a continuously updated living literature review that incorporates new findings as they are published. The release of nanopub-js v0.1.0 \citep{kuhn2026nanopubjs} makes browser-based creation and querying of nanopublications practical, enabling researchers to contribute assertions directly from web interfaces. Integrating this approach with the Active Inference Institute's Knowledge-Engineering infrastructure \citep{knight2022fep} could provide the standardized semantic vocabulary necessary for rigorous cross-study comparison.

### Standardize the Ontological Lexicon

Immediate future extraction cycles should align assertion predicates with the formally curated Active Inference Ontology. Enforcing shared ontological primitives across studies will accelerate the aggregation of evidence from otherwise siloed research communities, advancing the interoperability goal outlined by Knight et al. \citep{knight2022fep}.

## Empirical and Theoretical Imperatives

### Architect Unified Performance Benchmarks

The computational tools domain (B) lacks standardized performance benchmarks for direct comparison against deep reinforcement learning architectures. Establishing baseline metrics analogous to standard RL environments (e.g., OpenAI Gym) is a prerequisite for transitioning theoretical proposals into applied systems.

### Prioritize Empirical Validation

Biology (C5) and Language (C3) have established theoretical frameworks but limited empirical validation. Targeted experiments designed to test specific FEP-derived predictions—such as demonstrating morphogenesis as Bayesian inference or measuring active inference advantages in language tasks—would strengthen the evidence base beyond what further theoretical work alone can achieve.

## Living Review Maintenance

The pipeline is designed for continuous operation rather than one-time analysis. Incremental resume capabilities (checkpoint-based assertion extraction, merge-on-add corpus deduplication) enable periodic re-execution as new papers are indexed. We envision a maintenance cycle in which the pipeline is re-run quarterly, with updated hypothesis scores and field statistics published alongside the pipeline release. Community contributors can extend the framework by adding custom hypothesis definitions, alternative keyword taxonomies, or domain-specific extraction prompts—all configurable via the YAML configuration file without modifying source code. A complementary long-term trajectory is toward RAG-enabled access: integrating the nanopublication knowledge graph into a Retrieval-Augmented Generation architecture \citep{fan2024survey} would enable natural-language querying of the evidence base, making quantitative literature synthesis accessible to researchers without programming expertise.

### Agentic Workspaces and MCP Integration

Beyond traditional open-source maintenance, the repository is architected as an intrinsically agentic workspace. Every underlying source module (e.g., `src/knowledge_graph/`, `src/visualization/`) is governed by dedicated `SKILL.md` files serving as Model Context Protocol (MCP) prompt-boundaries. These explicitly define the "rules of engagement" for autonomous AI inference agents—such as enforcing the zero-mock testing philosophy via local HTTP proxies, handling specific LLM fallback parsing logic, and respecting headless rendering constraints. This design ensures that future AI orchestrators can natively interface with, scale, and refine the computational meta-analysis pipeline safely and deterministically without structural micromanagement.

### The Discovery Engine and Future Architectures

Broadening our synthesis of knowledge graphs and LLMs, future iterations of this pipeline may interface with architectures like the *Discovery Engine* \citep{baulin2025discovery}. This comprehensive framework is designed to overcome the limitations of the document-centric publishing paradigm by transforming unstructured scientific literature into a machine-operable "world model." Their approach uses systematic, self-consistent LLM distillation to extract typed "knowledge artifacts" from publications, which are sequentially assembled into a hierarchical Conceptual Nexus Model (CNM) graph and encoded as a high-dimensional Conceptual Nexus Tensor. By explicitly modeling experimental variables, causal relations, and evidential contradictions within a FAIR-aligned representation, this architecture enables AI agents to mathematically navigate the knowledge landscape, trace provenance, and generate novel hypotheses through operations akin to tensor factorization and Vector Symbolic Architectures (VSA). This shift from static digital libraries to a computable, relation-rich evidence graph deeply parallels our objective of translating unstructured Active Inference literature into a quantifiable assertion tracking system.

## Open Questions

This meta-analysis surfaces four empirically testable questions whose answers would directly advance the four-step research agenda outlined in \S\ref{sec:next_steps}.


- **Recency bias in citation weighting (Methodological limitation).** The citation-weighting function $w(a) = \log(1+\text{citations}) \cdot \text{confidence}$ systematically underweights recent papers (2024–2026) which have few citations. A 2024 paper with 1 citation is weighted approximately 0.69\times versus a 2015 paper with 100 citations at approximately 4.6\times. Future work may explore time-decay normalization to mitigate this recency penalty.
- **Domain classifier over-assignment to A2 (Philosophy).** The keyword-based domain classifier tends to over-assign papers to the broad A2 (philosophy) category, where FEP universality is implicitly invoked but rarely explicitly tested. This classification bias likely inflates H1's neutral evidence count and should be addressed in future work through embedding-based classification or expert annotation.
- **Classifier calibration (feeds Step 1).** What proportion of A1 (Formal Theory) papers would be reclassified under an embedding-based or expert-annotated scheme, and how does this affect the field's theoretical core? An embedding-classifier trained on a 200-paper labeled set and evaluated on held-out A1 vs. A2 examples would quantify the fraction of "philosophy" papers that carry formal mathematical content, directly sharpening both retrieval scope and outcome-grounding rate.

- **Falsifiability and explicit testing (feeds Step 3).** H1 (FEP Universality) produces a predominantly neutral evidence profile, consistent with the critique that FEP accommodates any behavior without generating distinctive predictions \citep{colombo2021free}. Can hypothesis definitions—and author reporting standards—be reformulated to require a formal, refutable empirical prediction before contributing a supporting assertion? The proposed outcome-indicator taxonomy (§\ref{sec:next_steps}) would operationalize this: only assertions paired with a measurable outcome indicator would count as empirical support, converting the neutral H1 tally into a decomposed "invoked vs. tested" breakdown.

- **The Scalability Gap (feeds Step 3).** H5 (AIF Scalability) shows a strong positive trend, yet head-to-head comparisons with deep RL remain concentrated on a narrow set of benchmarks (predominantly low-dimensional discrete environments). Beyond what state-space dimensionality and reward density does the expected-free-energy exploration advantage of model-based AIF degrade relative to model-free architectures such as SAC or PPO? Answering this requires assembling the outcome-indicator-tagged evidence (Step 3) and identifying which benchmark comparisons are already in the literature versus which are genuinely absent.

- **Evidence Cross-Pollination (feeds Step 1 + Step 4).** To what extent do mathematical structures underlying variational free energy minimization and energy function optimization in Energy-Based Models (VAEs, contrastive divergence) converge? Extending the corpus to include EBM literature (Step 1) and running the assertion extractor on the merged set would produce a cross-domain hypothesis score for the shared-architecture claim—a direct test of convergence rather than a theoretical argument. The rubric's corpus recall metric (Step 4) would validate whether the expanded retrieval actually captures the EBM literature at recall $\geq 0.85$.

## Pipeline as a Community Instrument

The four next steps are not a private development roadmap—they are an invitation. The repository is structured so that each step can be contributed incrementally: a new source connector (Step 1), a revised extraction prompt with evidence-quote fields (Step 2), a YAML file defining outcome indicators per hypothesis (Step 3), and an annotation script that computes rubric scores against a provided gold set (Step 4). None of these require modifying the scoring engine or the knowledge graph schema. By publishing the rubric thresholds alongside the current baseline scores, this work makes explicit what it would take for a community contributor to demonstrably improve the system—and provides the tooling to verify that improvement without relying on subjective assessment.

## Limitations

Recency bias: The citation-weighting function $w(a) = \log(1+\text{citations})\cdot\text{confidence}$ systematically underweights recent papers (2024--2026) which have few citations. A 2024 paper with 1 citation is weighted $\sim0.69\times$ versus a 2015 paper with 100 citations at $\sim4.6\times$. Future work may explore time-decay normalization.

Classifier bias: The assertion counts are also sensitive to corpus composition: H1's large neutral tally ({{H1_NEUTRAL}}) partially reflects the keyword classifier's tendency to assign papers to the broad A2 (philosophy) category, where FEP universality is implicitly invoked but rarely explicitly tested. This classifier bias likely inflates H1's neutral classification count and should be addressed in future work.
