# Conclusion: Evidence Landscape, Methodological Limitations, and Research Agenda \label{sec:conclusion}

## Summary

This work demonstrates that the infrastructure for computational meta-analysis of a rapidly growing scientific field is feasible with current technology. By combining multi-source retrieval ($N = 785$ papers from three databases), LLM-based assertion extraction encoded as nanopublications, and citation-weighted hypothesis scoring, we produce a queryable, RDF-compatible knowledge graph that tracks the evolving evidence for eight core Active Inference claims.

## Constraints and Methodological Scope

Several conscious design constraints scope these findings.

### Keyword Classifier Resolution

The keyword-based classifier uses a deterministic priority system that routes papers to specific application domains (C1–C5) before testing tools (B), formal theory (A1), and the qualitative philosophy catch-all (A2). The expanded A1 keyword set (65+ mathematical indicators) and word-boundary-aware matching reduce misclassification of formal papers into A2, but keyword-based methods lack the semantic resolution of embedding-based approaches. Residual A2 concentration should be interpreted as a ceiling on broad theoretical generality rather than a literal measure of philosophical focus.

### Citation Network Coverage Gaps

<<<<<<< HEAD
The 1{,}873 intra-corpus edges spanning 524 distinct connected components provide a meaningful topological skeleton, yet cross-source identifier mismatches inevitably inflate the isolated component count. Exhaustive DOI-level cross-matching would further condense the graph.

### Temporal and Citation-Count Biases

Citation counts remain fundamentally subject to Matthew effects and cumulative field-size biases. Partial-year indexing for the most recent calendar year predictably undercounts concluding publications. Consequently, the measured 5.02\% CAGR explicitly reflects the dilutive effect of the extensive longitudinal span (1977--2026); the localized growth phase from 2010 onward traverses an aggressively steeper trajectory.
=======
The 1{,}873 intra-corpus edges spanning 524 connected components provide a topological skeleton, though cross-source identifier mismatches inflate the isolated component count. Exhaustive DOI-level cross-matching would condense the graph further.

### Temporal and Citation-Count Biases

Citation counts are subject to Matthew effects and cumulative field-size biases. Partial-year indexing for the most recent calendar year undercounts recent publications. The measured 5.02\% CAGR reflects the dilutive effect of the long temporal span (1977–2026); the growth phase from 2010 onward follows a steeper trajectory.
>>>>>>> 042a14f (refine: scholarly prose, fix stale data, remove unused refs)

### LLM Extraction Fidelity

Systematic zero-shot extraction biases include over-extraction (hallucinating claims the paper merely mentions) and direction inversion (misclassifying opposing evidence as supporting). Human review and the explicit "irrelevant" filtering predicate mitigate these errors but do not eliminate them. Zero-shot confidence calibration remains a central open challenge for automated evidence synthesis.

## Future Directions: Beyond Tally-Based Evidence Aggregation

The current scoring formula (Section 5) aggregates LLM-extracted assertions through a simple citation-weighted tally. While this approach provides a transparent and reproducible baseline, it leaves substantial room for methodological sophistication. We identify six directions, ordered by expected impact, with the first three specifically addressing the limitations of tally-based evidence synthesis.

### Hierarchical Bayesian Hypothesis Scoring

The most direct extension replaces the additive tally with a **hierarchical Bayesian model** that treats each hypothesis score as a latent variable inferred from noisy assertion observations. Under this formulation, each assertion $a_i$ contributes a likelihood term $P(a_i | \theta_H, \sigma)$ parameterized by the hypothesis-level evidence strength $\theta_H$ and an observation noise term $\sigma$ capturing LLM extraction uncertainty. A hierarchical prior $\theta_H \sim \mathcal{N}(\mu_{\text{field}}, \tau^2)$ pools information across hypotheses, enabling principled shrinkage for hypotheses with sparse evidence (e.g., H6 Clinical Utility, with only 33 assertions). This framework produces posterior credible intervals rather than point estimates, providing uncertainty quantification that the current tally-based scores lack. Temporal dynamics can be modeled through time-varying parameters $\theta_H(t)$ using state-space formulations that re-weight older evidence rather than treating all cumulative assertions equally.

### Causal Evidence Graphs

A second-generation knowledge graph would encode not only assertion-level relationships (paper → supports → hypothesis) but also **causal dependencies among hypotheses** themselves. For example, evidence for predictive coding (H4) often implicitly supports FEP universality (H1), yet the tally-based approach treats them as independent. A causal evidence graph—structured as a directed acyclic graph (DAG) over hypotheses with edge weights learned from co-assertion patterns—would enable cross-hypothesis evidence propagation using belief propagation or variational message passing. This is particularly relevant for the Active Inference literature, where hypotheses are theoretically nested: FEP universality (H1) logically entails predictive coding (H4), and Markov blanket realism (H3) is a prerequisite for certain formulations of H1. Encoding these dependencies would prevent the double-counting of evidence from papers that support multiple related hypotheses and enable identification of which specific claims drive support for downstream hypotheses. The resulting causal structure itself would be a scientific contribution—a formal map of evidential dependencies within the field's theoretical architecture.

### Evidential Diversity and Source Weighting

The current formula weights assertions by $\log(1 + \text{citations}) \cdot \text{confidence}$, treating all assertion sources symmetrically. A more nuanced approach would introduce an **evidential diversity index** that downweights correlated evidence from papers sharing authors, institutions, or methodological approaches. Concretely, assertions could be weighted by the inverse of their similarity to previously counted assertions, measured via cosine similarity of paper embeddings. This would address the observation that H1 (FEP universality) accumulates a large neutral tally partly because many A2 (philosophy) papers invoke the FEP without independently testing it—a form of evidential redundancy that inflates the evidence base without adding independent information. Additionally, assertions could be stratified by evidence type (empirical, theoretical, review) with configurable type-specific weights, enabling users to compute evidence scores that privilege experimental results over theoretical commentary.

### Additional Directions

1. **Confidence calibration.** A pilot study comparing LLM-generated assertions with domain expert assessments would establish inter-annotator agreement ($\kappa$) and identify systematic biases. This is the prerequisite for all downstream improvements.

2. **Agentic LLM Extractors.** Drawing on recent work connecting active inference to artificial reasoning \citep{friston2025active} and proposing AIF as a reward-free alternative for LLM-based agents \citep{wen2025missing}, replacing static prompt templates with goal-directed, actor-critic LLM architectures could significantly improve confidence calibration. The convergence between AIF and deep learning demonstrated by AXIOM \citep{heins2025axiom}—which outperforms DreamerV3 through principled active inference planning—suggests that the same object-centric, uncertainty-aware reasoning could enhance extraction quality when applied to scientific text comprehension.

3. **Domain adaptation.** The framework is domain-agnostic by design. Adaptation to foundation models, quantum computing, or synthetic biology requires only domain-specific hypothesis definitions and keyword lists within the A/B/C taxonomy.

4. **Energy-Based Model convergence.** Systematic cross-referencing of the Active Inference literature with the broader Energy-Based Model research program \citep{lecun2006tutorial}—including Helmholtz machines \citep{dayan1995helmholtz}, contrastive divergence training \citep{hinton2002training}, and variational autoencoders \citep{kingma2014auto}—would illuminate the mathematical convergence between variational free energy minimization in biological systems and energy-based learning in artificial systems. This analysis could reveal shared mathematical structures that are currently obscured by disciplinary siloing.

## Broader Impact

The vision motivating this work is straightforward: a living literature review—a continuously updated knowledge graph tracking what a field claims, what evidence supports those claims, and where the frontiers of understanding lie. This vision builds on the foundation established by Knight et al. \citep{knight2022fep}, who identified the development of systems that could "encompass increased scope of relevant works," "integrate multiple forms of annotation and participation," and "facilitate integration of manual and artificial contributions" as key goals for the field.

<<<<<<< HEAD
By demonstrating that LLM-driven assertion extraction can produce scalable, queryable representations of scientific evidence—processing $N = 785$ papers spanning nearly five decades (1977--2026), extracting structured semantic assertions, and systematically evaluating 8 core hypotheses—this work provides a robust computational machinery for realizing this vision. The generated citation network metrics (1{,}873 edges, a density of 0.30\%, and an average in-degree of 2.4) quantify the rapid expansion of the active inference ecosystem, which has grown to a 5.02\% CAGR while diversifying across 5 major application domains.
=======
By demonstrating that LLM-driven assertion extraction can produce scalable, queryable representations of scientific evidence—processing $N = 785$ papers spanning nearly five decades (1977–2026), extracting structured assertions, and evaluating 8 core hypotheses—this work provides a reusable architecture for realizing this vision. The citation network metrics (1{,}873 edges, 0.30\% density, mean in-degree 2.4) characterize the field's structure, which has grown at a 5.02\% CAGR while diversifying across 5 application domains.
>>>>>>> 042a14f (refine: scholarly prose, fix stale data, remove unused refs)

The limitations of keyword-based retrieval across disjoint academic repositories mean that any retrieved corpus will contain both false positives and false negatives. There is no single threshold that perfectly defines inclusion or exclusion for a dynamic, interdisciplinary research field. The primary contribution of this work is therefore not a definitive corpus but an open-source, modularly updatable, and versioned software package. This tool is built in reference to custom literature bibliographies that can be iteratively curated for relevance by the community.

The combination of multi-source retrieval, LLM-based extraction, and probabilistic knowledge graph construction provides a reusable template that advances each of these goals. As LLM capabilities improve and standardized metadata adoption grows, the cost of maintaining such systems will decrease while their utility increases. By open-sourcing the pipeline and publishing the schema, we provide both a concrete tool for the Active Inference community and a modular blueprint that other fields can adapt and refine.

**Data and code availability.** The pipeline source code, configuration, and manuscript templates are available in the project repository (see \texttt{metadata.repository} in \texttt{config.yaml} or the manuscript front matter). Nanopublications are persisted as JSON Lines (for incremental runs) and RDF/TriG (nanopub.net-compliant); both can be archived with the code release or on a data repository (e.g., Zenodo) for citation and long-term access.

Community recommendations, actionable implications, and open questions arising from this work are detailed in the Discussion (see \hyperref[sec:discussion]{Section 8a}).
