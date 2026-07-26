# Conclusion: Evidence Landscape, Methodological Limitations, and Research Agenda {#sec:conclusion}

## Summary

This work demonstrates a first-generation prototype infrastructure for citation-weighted evidence mapping and hypothesis triage across a rapidly growing scientific field. By combining configured multi-source retrieval ($N = {{CORPUS_SIZE}}$ papers, inclusion from {{INCLUSION_YEAR_START}} onward; {{SOURCE_COMPLETION_SUMMARY}}), LLM-based assertion extraction encoded as provenance-bearing nanopublications, and citation-weighted triage scoring, we produce a queryable, RDF-compatible knowledge graph that maps the evolving evidence landscape for eight core Active Inference claims. The system demonstrates the feasibility of automated living reviews, while clearly delineating the boundaries of current model capabilities.

All assertions and hypothesis scores are machine-generated; outputs always report evidence mapping and triage, not scientific confirmation---there is no live gate that suppresses or changes output based on the validation metrics below, which are reported as reproducibility context, not an enforced pass/fail threshold. A stratified rule-based reference-annotator agreement study ($n = {{VAL_N}}$) yields inter-rule $\kappa = {{VAL_KAPPA}}$ and pipeline precision {{VAL_PRECISION}}, recall {{VAL_RECALL}} against a deterministic keyword-rule reference; direction agreement between that reference and the pipeline is only $\kappa = {{VAL_KAPPA_PIPELINE}}$. These are reproducibility signals, not accuracy against human labels—the pre-declared human gold-standard baseline below has not yet been collected.

## Constraints and Methodological Scope

Several conscious design constraints scope these findings.

### Keyword Classifier Resolution

The keyword-based classifier operates over 200+ keyword indicators distributed across 8 domain categories (74 mathematical indicators in A1 alone), using a deterministic priority system that routes papers to specific application domains (C1–C5) before testing tools (B), formal theory (A1), and the qualitative philosophy catch-all (A2). Word-boundary-aware matching reduces partial-match false positives, but keyword-based methods cannot capture semantic nuance: papers using novel terminology or discussing cross-domain topics without standard vocabulary risk misclassification. Residual A2 concentration should be interpreted as a ceiling on broad theoretical generality rather than a literal measure of philosophical focus. An embedding-based classifier trained on a labeled subset would provide a quantitative upper bound on the fraction of A2 papers that merit redistribution.

### Citation Network Coverage Gaps

The {{CITATION_EDGES}} intra-corpus edges spanning {{CITATION_COMPONENTS}} connected components provide a topological skeleton, but three systematic gaps inflate the component count: (1) cross-source identifier mismatches (DOI vs. OpenAlex vs. arXiv ID), (2) papers whose references are not indexed by any source API, and (3) open-access preprints whose DOIs differ from their published versions. Exhaustive DOI-level cross-matching with fuzzy title matching would condense the graph further.

### Corpus Biases, Citation Dynamics, and Linguistic Framing

Citation counts are subject to Matthew effects and cumulative field-size biases. Partial-year indexing for the most recent calendar year undercounts recent publications. The measured {{CAGR_PCT}}\% CAGR is calculated over complete years {{CAGR_PERIOD}}, while {{CURRENT_YEAR_PUBS}} papers from {{CURRENT_YEAR}} are reported as of {{AS_OF_DATE}} and excluded from that endpoint. Additionally, the retrieved corpus itself suffers from selection biases inherent to queried databases, including English-language dominance and the structural over-indexing of preprints relative to peer-reviewed final versions. Finally, positive and negative hypothesis scores alike are affected by publication bias and linguistic asymmetry: declarative scholarly claims are phrased affirmatively more often than negatively. Relative rankings and temporal trajectories are retained for transparent comparison, but their robustness is not established by this abstract-only calibration.

### LLM Extraction Fidelity, Domain Drift, and Robustness

Zero-shot LLM extraction introduces distinct systematic biases: over-extraction (the model hallucinating certainty for claims the paper merely mentions in passing) and direction inversion (misclassifying opposing evidence as supporting). Recent benchmarking confirms that state-of-the-art systems often fall short of production-level precision on tasks requiring exhaustive retrieval and aggregation of directional claims from long documents \citep{liang2024survey}. Furthermore, because our corpus extends to {{YEAR_END}}, LLM extraction is vulnerable to *domain drift*—the base models may lack parametric knowledge of the most recent theoretical developments. As an alternative, fine-tuned models specifically trained on FEP/AIF abstracts could yield higher precision than our zero-shot approach, though at a steeper computational setup cost.

The current validation protocol is a deterministic rule-based reference study, not a human-annotation ground truth. It provides a reproducibility floor through inter-rule agreement and pipeline-versus-reference metrics; a future human-labeled study is required before making accuracy claims.

## Research Agenda: Four Priority Next Steps {#sec:next_steps}

The current prototype establishes a reproducible baseline and surfaces the field's evidence structure at corpus scale. Four concrete next steps, ordered by the dependency chain each one unlocks, define the path from prototype to production-grade living review.

### Next Step 1 — Expand the Scope of Referenced Data

The present corpus of $N = {{CORPUS_SIZE}}$ papers is assembled via keyword queries against the configured APIs (Semantic Scholar, OpenAlex, arXiv); this snapshot records {{SOURCE_COMPLETION_SUMMARY}}. Three expansion axes would materially change the evidence landscape.

**Additional sources.** PubMed, PsycINFO, and IEEE Xplore each index Active Inference literature that the current APIs do not reach: neuroscience clinical trials (PubMed), cognitive-behavioral studies (PsycINFO), and robotics control architectures (IEEE). For each new source, the retrieval layer requires only a source-specific connector implementing the same `fetch_papers(query, max_results)` interface used by existing adapters. Gray literature—technical reports, theses, and institutional preprints not yet indexed by major APIs—represents an additional tier: harvesting from ORCID work records and institutional repositories would capture practitioner findings that never appear in indexed venues.

**Broader query coverage.** The current query set is derived from the eight hypothesis keywords and their immediate synonyms. Expanding to a full ontological synonym set (e.g., mapping "variational inference," "surprise minimization," and "Helmholtz machine" as equivalent retrieval terms for FEP-related claims) would reduce the retrieval false-negative rate for papers that use non-canonical vocabulary. A systematic evaluation of retrieval precision and recall against a hand-curated gold-standard set of 100 known AIF papers would quantify the gap.

**Custom curated bibliographies.** Domain experts can contribute citation lists directly to the corpus without modifying any code: placing a `.bib` or `.ris` file in `data/custom_bibliographies/` triggers the deduplication merge on the next pipeline run. This pathway is the lowest-friction route to extending scope for researchers who maintain personal reference libraries.

### Next Step 2 — Extract and Verify Evidence Supporting Claims in Each Paper

The current extraction pipeline operates exclusively on abstracts. Abstracts contain the claims authors choose to foreground, not necessarily the claims best supported by the paper's data. Three mechanisms bridge this gap.

**Full-text ingestion.** For the subset of papers with open-access PDFs (approximately 60–70\% of recent AIF preprints on arXiv), Stage 3 can be extended to parse full-text sections—specifically Methods, Results, and Discussion—using a structured chunking strategy that splits documents into ~512-token segments aligned to section boundaries. The existing nanopublication schema accommodates a `source_section` field (currently unused) that would record the provenance of each extracted assertion (abstract vs. results vs. discussion), enabling downstream stratification of evidence by rhetorical function.

**Claim-evidence pairing.** The current extraction prompt asks the LLM to classify a paper's stance toward a hypothesis but does not require it to quote the specific sentence or data point that justifies the classification. A revised prompt would require the model to (a) identify the hypothesis-relevant passage verbatim, (b) classify the stance, and (c) rate confidence on the basis of whether the passage reports an empirical measurement, a theoretical derivation, or an assertion without quantitative support. This three-field extraction — \texttt{evidence\_quote}, \texttt{stance}, \texttt{evidence\_type} — upgrades the nanopublication from a classification label to a traceable evidential pointer. For H3 (Markov Blanket Realism), where the {{H3_CONTRADICT}} contradicting assertions drive a contested score, reviewers could then inspect the actual quoted passages rather than trusting the LLM classification in isolation.

**Human spot-check coverage.** The planned 10\% manual-annotation baseline would focus on inter-rater agreement; this manual validation has not yet been performed. Extending spot-checks to verify that the extracted evidence quote actually appears in the source document (a verbatim-match check) adds an additional fidelity gate beyond stance accuracy.

### Next Step 3 — Tie Hypotheses to Real-World Outcomes

The eight tracked hypotheses are formulated at the level of theoretical constructs (e.g., "the FEP provides a universal account of self-organizing systems"). Practical applicability requires mapping from hypothesis support to observable real-world outcomes, distinguishing which claims are actionable from which remain theoretical scaffolding.

**Outcome taxonomy.** Each hypothesis should be annotated with a set of *outcome indicators*: specific, measurable real-world results whose observation would constitute evidence for or against the hypothesis under the closest empirical operationalization. For example:
- H4 (Predictive Coding): outcome indicator = reduction in prediction-error amplitude as measured by ERP N400 or oscillatory gamma-band response in human neuroimaging studies.
- H5 (Scalability): outcome indicator = task performance on standard RL benchmarks (Atari, MuJoCo, ProcGen) at or above the performance of model-free SOTA at matched computational budgets.
- H6 (Clinical Utility): outcome indicator = statistically significant improvement on standardized psychiatric assessment scales (PANSS, BDI-II, PTSD Checklist) in at least one registered clinical trial.
- H7 (Morphogenesis): outcome indicator = quantitative recapitulation of at least one morphogenetic patterning sequence (e.g., digit formation timecourse, limb bud size scaling) in a computational model governed by FEP dynamics rather than reaction-diffusion equations.

For each hypothesis, the extraction pipeline can be extended to tag assertions whose evidence type is `empirical_measurement` and whose outcome aligns with these indicators, producing a filtered score that counts only outcome-linked evidence. This *outcome-filtered score* sits alongside the current citation-weighted score in the hypothesis table, providing a direct answer to "how much of this support is grounded in real-world observations rather than theoretical commentary?"

**Application domain cross-walk.** The subfield classification (A1–C5) already partitions the corpus by application domain. Intersecting hypothesis scores with application domain membership—computing $\text{score}(H_i, D_j)$ for each hypothesis $H_i$ and domain $D_j$—would reveal which domains are generating empirical traction versus theoretical citation counts. H1 (FEP Universality) likely has high A2 (philosophy) support and lower C1–C5 empirical support; quantifying this split would replace qualitative description of the "neutral plurality" with a decomposed evidence profile grounded in domain labels already computed by Stage 2.

### Next Step 4 — Formal Evaluation Rubric for Pipeline Quality

The current validation is primarily structural: do scripts run, do outputs exist, do tests pass, does the PDF render? A formal evaluation rubric answers a different question: *how accurate is the evidence landscape this system produces?* Four rubric dimensions, together with their measurement protocols and target thresholds, define what "good enough for a published living review" means.

\begin{table}[htbp]
\centering
\caption{Proposed evaluation rubric for pipeline quality assessment. Each dimension has a measurement protocol, a current baseline, and a target threshold for a production living review. All metrics are computed on a held-out annotation set of 200 randomly sampled assertions.}
\label{tab:eval_rubric}
\begin{tabular}{llll}
\toprule
\textbf{Dimension} & \textbf{Protocol} & \textbf{Current} & \textbf{Target} \\
\midrule
Extraction direction accuracy & Cohen's $\kappa$ (rule reference vs.\ LLM stance) & $\kappa = {{VAL_KAPPA_PIPELINE}}$ & $\kappa > 0.80$ \\
Evidence-quote fidelity & Verbatim substring match rate & {{VAL_QUOTE_FIDELITY}} (no quotes stored) & $\geq 90\%$ \\
Corpus recall & Precision/recall vs.\ rule reference & $P = {{VAL_PRECISION}}$, $R = {{VAL_RECALL}}$ & recall $\geq 0.85$ \\
Outcome grounding rate & Fraction of supporting assertions citing an outcome indicator & pending & $\geq 30\%$ \\
\bottomrule
\end{tabular}
\end{table}

The four rubric dimensions map directly to the four next steps: corpus recall measures Step 1 progress, evidence-quote fidelity measures Step 2 progress, outcome grounding rate measures Step 3 progress, and extraction direction accuracy is the targeted baseline to be established as the other three improve. Reporting all four numbers alongside hypothesis scores in each pipeline release converts a qualitative description of limitations into a versioned, trackable quality scorecard. This transforms the current "we acknowledge limitations" posture into an audit trail: readers can see whether the rubric scores improved between release v1.0 and v2.0, and reviewers can evaluate pipeline trustworthiness on principled criteria rather than subjective judgement.

---

## Future Directions: Beyond Tally-Based Evidence Aggregation

Beyond the four priority next steps above, the scoring machinery itself can be upgraded. We identify four directions, ordered by expected impact.

### Hierarchical Bayesian Hypothesis Scoring

The most direct extension replaces the additive tally with a **hierarchical Bayesian model** that treats each hypothesis score as a latent variable inferred from noisy assertion observations. Under this formulation, each assertion $a_i$ contributes a likelihood term $P(a_i | \theta_H, \sigma)$ parameterized by the hypothesis-level evidence strength $\theta_H$ and an observation noise term $\sigma$ capturing LLM extraction uncertainty. A hierarchical prior $\theta_H \sim \mathcal{N}(\mu_{\text{field}}, \tau^2)$ pools information across hypotheses, enabling principled shrinkage for hypotheses with sparse evidence (e.g., H6 Clinical Utility, with only {{H6_TOTAL}} assertions). This framework produces posterior credible intervals rather than point estimates, providing uncertainty quantification that the current tally-based scores lack. Temporal dynamics can be modeled through time-varying parameters $\theta_H(t)$ using state-space formulations that re-weight older evidence rather than treating all cumulative assertions equally.

### Causal Evidence Graphs

A second-generation knowledge graph would encode not only assertion-level relationships (paper → supports → hypothesis) but also **causal dependencies among hypotheses** themselves. For example, evidence for predictive coding (H4) often implicitly supports FEP universality (H1), yet the tally-based approach treats them as independent. A causal evidence graph—structured as a directed acyclic graph (DAG) over hypotheses with edge weights learned from co-assertion patterns—would enable cross-hypothesis evidence propagation using belief propagation or variational message passing. This is particularly relevant for the Active Inference literature, where hypotheses are theoretically nested: FEP universality (H1) logically entails predictive coding (H4), and Markov blanket realism (H3) is a prerequisite for certain formulations of H1. Encoding these dependencies would prevent the double-counting of evidence from papers that support multiple related hypotheses and enable identification of which specific claims drive support for downstream hypotheses. The resulting causal structure itself would be a scientific contribution—a formal map of evidential dependencies within the field's theoretical architecture.

### Evidential Diversity and Source Weighting

The current formula weights assertions by $\log(1 + \text{citations}) \cdot \text{confidence}$, treating all assertion sources symmetrically. A more nuanced approach would introduce an **evidential diversity index** that downweights correlated evidence from papers sharing authors, institutions, or methodological approaches. Concretely, assertions could be weighted by the inverse of their similarity to previously counted assertions, measured via cosine similarity of paper embeddings. This would address the observation that H1 (FEP universality) accumulates a large neutral tally partly because many A2 (philosophy) papers invoke the FEP without independently testing it—a form of evidential redundancy that inflates the evidence base without adding independent information. Additionally, assertions could be stratified by evidence type (empirical, theoretical, review) with configurable type-specific weights, enabling users to compute evidence scores that privilege experimental results over theoretical commentary.

### Agentic LLM Extractors and Domain Adaptation

Drawing on recent work extending active inference into artificial reasoning \citep{friston2025active} and proposing AIF as a reward-free alternative for LLM-based agents \citep{wen2025missing}, replacing static prompt templates with goal-directed reasoning architectures could significantly improve confidence calibration. As demonstrated by Friston et al. \citep{friston2025active}, "active reasoning" enables agents to perform structure learning—determining which causal rule governs a situation by seeking observations that explicitly disambiguate competing hypotheses about world models. Applied to literature extraction, analogous uncertainty-aware reasoning could treat each paper as a structured observation to be parsed against hypothesis definitions via an optimal experimental design rubric—directly operationalizing Next Step 2's claim-evidence pairing at scale. The framework is domain-agnostic by design; adaptation to foundation models, quantum computing, or synthetic biology requires only domain-specific hypothesis definitions and keyword lists within the A/B/C taxonomy. The broader convergence between AIF and deep learning demonstrated by AXIOM \citep{heins2025axiom}—which plans in object-centric state-spaces—further validates this trajectory. Systematic cross-referencing with the Energy-Based Model research program \citep{lecun2006tutorial}—including Helmholtz machines \citep{dayan1995helmholtz}, contrastive divergence training \citep{hinton2002training}, and variational autoencoders \citep{kingma2014auto}—would illuminate shared mathematical structures currently obscured by disciplinary siloing.

## Limitations

Three constraints bound the current findings. First, extraction operates on abstracts only: full-text methods, results, and supplementary data—where quantitative effect sizes and experimental controls live—are not yet parsed. The rubric's evidence-quote fidelity dimension (Step 4, Table \ref{tab:eval_rubric}) will quantify exactly how much signal this omission suppresses once a full-text pilot is run. Second, keyword-based retrieval across the configured APIs produces a snapshot with systematic false negatives: papers using non-canonical terminology, gray literature, and domain-adjacent work (EBM, Bayesian brain models) are undercounted. The corpus recall metric provides a principled bound on this gap rather than a vague acknowledgement of it. Third, the citation-weighted tally treats all assertion sources symmetrically; the evidential diversity and outcome-grounding extensions above are the concrete remedies. These are not general disclaimers but tracked deficits against which the Step 1–4 roadmap makes measurable progress.

## Broader Impact

Knight et al. \citep{knight2022fep} identified three capabilities as goals for the field: "encompass increased scope of relevant works," "integrate multiple forms of annotation and participation," and "facilitate integration of manual and artificial contributions." The four-step research agenda in §\ref{sec:next_steps} operationalizes each of these directly: Step 1 addresses scope, Step 2 addresses the quality of extracted contributions, Step 3 addresses empirical grounding, and Step 4 provides the formal rubric that makes "integration of manual and artificial contributions" verifiable rather than aspirational.

By demonstrating that LLM-driven assertion extraction can produce scalable, queryable representations of scientific evidence—processing $N = {{CORPUS_SIZE}}$ papers spanning approximately two and a half decades ({{YEAR_START}}–{{YEAR_END}}), extracting structured assertions, and evaluating 8 core hypotheses—this work provides a reusable architecture for realizing this vision. The corpus window begins in {{YEAR_START}} to capture Energy-Based Model and variational Bayesian antecedents that predate the Free Energy Principle label itself; the formal FEP was introduced in 2006 \citep{friston2006free} and reached its core elaboration by 2010 \citep{friston2010free}. The citation network metrics ({{CITATION_EDGES}} edges, {{CITATION_DENSITY_PCT}}\% density, mean in-degree {{MEAN_IN_DEGREE}}) characterize the field's structure, which has grown at a {{CAGR_PCT}}\% CAGR while diversifying across the 8 configured domains.

The limitations of keyword-based retrieval across disjoint academic repositories mean that any retrieved corpus will contain both false positives and false negatives. There is no single threshold that perfectly defines inclusion or exclusion for a dynamic, interdisciplinary research field. The primary contribution of this work is therefore not a definitive corpus but an open-source, modularly updatable, and versioned software package. This tool is built in reference to custom literature bibliographies that can be iteratively curated for relevance by the community.

The combination of multi-source retrieval, LLM-based extraction, and probabilistic knowledge graph construction provides a reusable template that advances each of these goals. A complementary pathway is emerging through Retrieval-Augmented Generation (RAG) architectures that ground LLMs directly in knowledge graphs, reducing hallucination and enabling real-time, context-aware reasoning over structured evidence \citep{fan2024survey}. Integrating our nanopublication graph into such a RAG system would enable natural-language querying of the evidence base, further lowering the barrier for community engagement. The recent release of nanopub-js v0.1.0 \citep{kuhn2026nanopubjs}—enabling browser-based creation, signing, and querying of nanopublications—lowers the barrier for community-contributed assertions, bringing the participatory evidence curation envisioned by Knight et al. within practical reach. As LLM capabilities improve and standardized metadata adoption grows, the cost of maintaining such systems will decrease while their utility increases. By open-sourcing the pipeline and publishing the schema, we provide both a concrete tool for the Active Inference community and a modular blueprint that other fields can adapt and refine.

**Data and code availability.** The pipeline source code, configuration, and manuscript templates are available in the project repository (see \texttt{metadata.repository} in \texttt{config.yaml} or the manuscript front matter). Nanopublications are persisted as JSON Lines (for incremental runs) and RDF/TriG (nanopub.net-compliant); both can be archived with the code release or on a data repository (e.g., Zenodo) for citation and long-term access.

Community recommendations, actionable implications, and open questions arising from this work are detailed in the \hyperref[sec:discussion]{Discussion}.
