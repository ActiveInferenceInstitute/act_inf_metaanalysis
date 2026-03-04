# Discussion: Implications and Community Recommendations \label{sec:discussion}

## Relationship to Prior Development Directions

Knight, Cordes, and Friedman \citep{knight2022fep} identified six development directions for systematic Active Inference literature analysis: (1) increased scope of relevant works, (2) richer annotation schemes, (3) integration of manual and artificial contributions, (4) transferable approaches across fields, (5) participation by diverse contributors, and (6) updated analyses tracking the field's evolution. This pipeline directly addresses directions 1, 2, 3, and 6: it scales retrieval to three databases, replaces manual annotation with LLM-driven extraction while preserving human review pathways, and produces a pipeline designed for incremental re-execution as new literature appears. Directions 4 and 5—cross-field transferability and community participation—remain open and are addressed below.

## Tactical and Strategic Priorities

### Demand Rigorous Reporting Metadata

Papers must systematically report DOIs, ORCIDs, and explicit hypothesis commitments. To prevent fragmented citation subgraphs, submitted preprints must rigorously forward-link to their definitive published versions. Our extraction pipeline prioritizes the DOI as the apex canonical identifier; failing that, deduplication cascades to arXiv IDs, Semantic Scholar IDs, and OpenAlex IDs. Systemic DOI adoption fundamentally solves the cross-source mismatch barrier, enabling high-resolution evidence mapping.

### Deploy Open Knowledge Graph Infrastructure

We advocate the deployment of a federated nanopublication server architecture to house community-contributed assertions, birthing an uninterrupted, living literature review that seamlessly updates as adjacent work publishes. Interlocking this pipeline with the Active Inference Institute's operational Knowledge-Engineering infrastructure \citep{knight2022fep} would furnish the standardized semantic vocabulary necessary for flawless cross-study comparison.

### Standardize the Ontological Lexicon

Immediate future extraction cycles must structurally align assertion predicates against the formally curated Active Inference Ontology. Enforcing shared ontological primitives across disparate studies will dramatically accelerate the direct mathematical aggregation of evidence spanning siloed research enclaves, actualizing the ultimate interoperability goal mapped by Knight et al. \citep{knight2022fep}.

## Empirical and Theoretical Imperatives

### Architect Unified Performance Benchmarks

The computational tools domain (B) suffers from a critical absence of standardized performance benchmarks preventing raw comparative evaluation against deep reinforcement learning architectures. Formalizing baseline metrics analogous to standard RL environments (e.g., OpenAI Gym) is the mandatory prerequisite catalyst for transitioning theoretical propositions into hardened applied systems.

### Prioritize Empirical Validation

Biology (C5) and Language (C3) possess substantial theoretical foundations but comparatively limited empirical support. Targeted investment in experiments designed to validate specific FEP-derived predictions—such as isolating morphogenesis as Bayesian inference or demonstrating active inference advantages in language tasks—would substantially strengthen the evidence base beyond what further theoretical elaboration alone can achieve.

## Living Review Maintenance

The pipeline is designed for continuous operation rather than one-time analysis. Incremental resume capabilities (checkpoint-based assertion extraction, merge-on-add corpus deduplication) enable periodic re-execution as new papers are indexed. We envision a maintenance cycle in which the pipeline is re-run quarterly, with updated hypothesis scores and field statistics published alongside the pipeline release. Community contributors can extend the framework by adding custom hypothesis definitions, alternative keyword taxonomies, or domain-specific extraction prompts—all configurable via the YAML configuration file without modifying source code.

## Open Questions

This meta-analysis surfaces questions warranting dedicated investigation:

- **Classifier calibration:** What proportion of A1 papers would be reclassified under embedding-based or expert-annotated schemes?
- **Scoring sensitivity:** How sensitive are hypothesis scores to the choice of weighting function? Would square-root or linear weights qualitatively change the evidence landscape?
- **Model sensitivity:** How much do hypothesis scores vary across different LLM models? Are some hypotheses more robust to model choice than others?
- **Domain boundaries:** Do domain boundaries stabilize as the field matures, or continue to shift? Is the 8-category (A/B/C) taxonomy optimal?
- **Cross-hypothesis evidence:** When a neuroscience (C1) paper supports predictive coding, does this constitute evidence for scalability? How should cross-hypothesis evidence be handled?
- **Temporal dynamics:** Do hypotheses follow predictable lifecycles (emergence → rapid support → contestation → resolution), and can these patterns inform research prioritization?
- **Energy-Based Model convergence:** To what extent do the mathematical structures underlying variational free energy minimization in Active Inference and energy function optimization in Energy-Based Models (Helmholtz machines, Boltzmann machines, VAEs) converge? Are there transferable inference algorithms or architectural insights at this intersection?
