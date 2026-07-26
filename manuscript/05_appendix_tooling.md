# Appendix: Tooling and Infrastructure {#sec:tooling}

The practical utility of a computational meta-analysis depends on robust tooling at each pipeline stage: assertion extraction, modeling and simulation, knowledge-graph infrastructure, and quality assurance. This appendix surveys the source-backed ecosystem of Active Inference (AIF) and Free Energy Principle (FEP) implementations as of {{AS_OF_DATE}}, documents the engineering trade-offs behind our knowledge-graph backend, and lists the multi-level quality gates enforced by the pipeline.

## LLM-Based Assertion Extraction

Extracting structured assertions from unstructured text is the most labor-intensive component of knowledge-graph construction. Manual annotation produces high-quality results but does not scale to corpora of thousands of papers---a constraint demonstrated by Knight et al. \citep{knight2022fep}, whose systematic analysis of FEP and Active Inference publications required manual coding of structural, visual, and mathematical features for hundreds of annotated papers. We implement a hybrid approach: an LLM performs initial extraction and human review provides validation pathways.

Our extraction pipeline deploys a locally hosted LLM through Ollama \citep{ollama2024}. Each paper's abstract is assessed against the eight hypothesis definitions in a structured prompt requesting a JSON array of assessments. Unlike keyword matching, which detects only topical terms, the LLM evaluates the *semantic relationship* between a paper's claims and each hypothesis. Papers critiquing the FEP correctly receive "contradicts" assessments for FEP Universality (H1), while methodology tutorials receive "neutral" assessments reflecting their pedagogical character. Detailed prompt engineering, schemas, and failure modes are documented in the \hyperref[sec:extraction_pipeline]{extraction pipeline section}.

<!-- See 02b_methods_extraction.md for detailed pipeline documentation -->

## Software Ecosystem

The Active Inference community has developed a rapidly growing ecosystem of implementations spanning multiple programming languages, inference paradigms, and application domains. This section provides a dated, source-traceable inventory of implementations and associated paper-only source records. We emphasize entries with traceable papers, preprint identifiers, or official project sources: source traceability is a prerequisite for reproducibility and community-driven validation, but does not by itself establish adoption, comparative performance, or a permissive software license. The registry and exclusion policy are maintained in `doc/tooling_inventory.yaml`; entries without a traceable primary source are not counted in the publication-facing table.
The dated public-source probe for this snapshot is {{TOOLING_VERIFICATION_STATUS}} as of {{TOOLING_LAST_CHECKED}} across {{TOOLING_REGISTRY_COUNT}} retained rows. It records repository reachability, license metadata, release/version information, and recent activity for every retained row; {{TOOLING_SOURCE_ONLY_COUNT}} rows have source-only evidence and {{TOOLING_FLAGGED_COUNT}} rows carry explicit limitations. Row-level flags remain visible for stale repositories, source-only papers/sites, restricted licenses, and missing license files; no such row is presented as a fully verified maintained software distribution.

### General-Purpose Frameworks

The source-backed general-purpose inventory covers discrete, continuous, and real-time inference:

**pymdp.** The pymdp library \citep{heins2022pymdp} provides a Python implementation of active inference for discrete state-space POMDPs, supporting message passing on factor graphs, policy inference via expected free energy, and hierarchical generative models.

**SPM.** The SPM package (Wellcome Centre for Human Neuroimaging) includes MATLAB implementations of Dynamic Causal Modeling and variational Bayesian inference under the FEP. It remains the reference implementation for neuroimaging applications and houses the original Friston-group POMDP scripts.

**RxInfer.jl.** RxInfer is a Julia package for reactive message-passing-based Bayesian inference, supporting real-time and streaming inference suitable for robotics and online learning \citep{rxinfer2025}. The dated source audit records its current release/version and license metadata; the audit report, rather than a hard-coded prose version, is authoritative for this living inventory. The RxInfer ecosystem includes tutorials covering Bayesian linear regression, hidden Markov models, Kalman filtering, Gaussian process regression, hierarchical Gaussian filters, nonlinear sensor fusion, and active inference mountain car control, available at the [official documentation](https://reactivebayes.github.io/RxInfer.jl/stable/) and the [Learnable Loop](https://learnableloop.com/) tutorial portal.

**ActiveInference.jl.** In parallel to RxInfer's generalized message-passing focus, ActiveInference.jl provides a Julia-native, near drop-in conceptual analogue to Python's `pymdp` \citep{ActiveInferencejl}. It explicitly targets computational psychiatry and cognitive neuroscience workflows emphasizing standard discrete-state POMDP simulation, parameter estimation, and recovery. The library leverages Julia's array semantics---utilizing vectors of arrays to efficiently encode multimodal factorized models via the canonical $\mathbf{A}, \mathbf{B}, \mathbf{C}, \mathbf{D}, \mathbf{E}$ components---to streamline tasks such as generating synthetic behavioral data, fitting models to subject behavior, and probing internal beliefs via robust simulation loops (`infer_states!`, `infer_policies!`, `sample_action!`).

**Cpp-AIF.** The Cpp-AIF header-only C++ library \citep{gregoretti2023cppaif} implements active inference for discrete POMDPs with multicore parallelization of the most demanding computational kernels---multidimensional inner products for expected free energy computation and state estimation. By abstracting the mathematical details behind a high-level API, Cpp-AIF targets embedded systems and performance-critical applications where Python overhead is prohibitive.

**FEPS.** Free Energy Projective Simulation \citep{pazem2024feps} combines active inference with interpretable graphical policy representations, enabling agents to plan via expected free energy while exposing decision logic as human-readable policy graphs. FEPS targets interpretable reinforcement learning tasks where black-box deep agents are undesirable---behavioral biology, clinical decision support, and safety-critical robotics.

### Deep Active Inference

Scaling active inference beyond tabular POMDPs to high-dimensional observation spaces requires neural-network function approximators. A growing body of deep active inference implementations explores this direction:

The foundational deep AIF agent of Fountas et al. \citep{fountas2020deep} introduced Monte-Carlo tree search over learned latent spaces, achieving non-trivial Atari performance. Millidge's DeepActiveInference extended this to continuous control with backpropagation-based world models \citep{millidge2020deep}. Champion's Branching-Time Active Inference (BTAI\_3MF) and its deep variant (Deep\_BTAI\_3MF) implement tree-structured planning under the free-energy objective, scaling active inference to partially observable environments with multi-step lookahead \citep{champion2021realizing}. Most recently, AXIOM \citep{heins2025axiom} achieves competitive Gameworld-10k benchmark performance using expanding object-centric world models, learning in minutes rather than hours---a landmark result for scalability.

### Predictive Coding and Neural Generative Coding

Predictive coding provides the core computational mechanism linking active inference to neuroscience. Several implementations offer accessible entry points:

**Predictive Coding and Backpropagation.** Millidge et al. demonstrate that predictive-coding networks can approximately implement backpropagation along arbitrary computational graphs \citep{millidge2022predictive}, providing a biologically plausible alternative to gradient descent. The [PredictiveCodingBackprop](https://github.com/BerenMillidge/PredictiveCodingBackprop) repository provides the reference implementation.

### Benchmarking Progress

The scalability gap between AIF and deep reinforcement learning has been a central limitation of the tools domain. Recent work demonstrates significant progress on two fronts. First, AXIOM \citep{heins2025axiom} outperforms state-of-the-art model-based deep RL agents including DreamerV3 on the Gameworld-10k benchmark while using substantially smaller model sizes; its object-centric scene decomposition enables sample-efficient learning from structured representations rather than raw-pixel memorization. Second, variational message-passing formulations \citep{champion2021realizing} connect EFE decomposition---into risk, ambiguity, epistemic (information-seeking), and instrumental (goal-reaching) components---to practical planning algorithms, advancing the theoretical justification for EFE-based policy selection (H2). Separately, Friston et al. \citep{friston2025active} introduce structure learning via Bayesian Model Reduction as a principled approach to artificial reasoning under active inference.

\FloatBarrier

### Source-backed Tool Survey

The following table catalogs the principal source-backed Active Inference implementations surveyed, organized by functional category. For each entry we list the primary language, application domain, and associated publication or repository. The table is intended as a navigational resource for researchers seeking implementations or traceable source records relevant to specific hypotheses (H1--H8) or application domains (A1--C5). External verification status is reported separately so the table does not convert a citation into a maintenance or license claim.

\begin{center}
\small
\begin{longtable}{p{3.2cm} p{1.6cm} p{6.4cm} p{2.5cm}}
\caption{Source-backed inventory of Active Inference and Free Energy Principle implementations and source records, grouped by functional category. Candidate entries without traceable primary sources are excluded; see the tooling registry and dated verification report.}
\label{tab:tool_survey} \\
\toprule
\textbf{Tool / Repository} & \textbf{Lang.} & \textbf{Description} & \textbf{Paper / Source} \\
\midrule
\endfirsthead
\toprule
\textbf{Tool / Repository} & \textbf{Lang.} & \textbf{Description} & \textbf{Paper / Source} \\
\midrule
\endhead
\midrule
\multicolumn{4}{r}{\textit{Continued on next page}} \\
\endfoot
\bottomrule
\endlastfoot
\multicolumn{4}{c}{\textit{General-Purpose Frameworks}} \\
\midrule
pymdp & Python & Discrete POMDP active inference; factor graphs, hierarchical models & \cite{heins2022pymdp} \\
SPM & MATLAB & DCM, variational Bayes; neuroimaging reference implementation & \cite{friston2017active} \\
RxInfer.jl & Julia & Reactive message passing; real-time streaming Bayesian inference & \cite{rxinfer2025} \\
ActiveInference.jl & Julia & Discrete POMDP AIF; parameter recovery for computational psychiatry & \cite{ActiveInferencejl} \\
Cpp-AIF & C++ & Header-only POMDP AIF library with multicore parallelization & \cite{gregoretti2023cppaif} \\
FEPS & Python & EFE on interpretable policy graphs; projective simulation & \cite{pazem2024feps} \\
\midrule
\multicolumn{4}{c}{\textit{Deep Active Inference}} \\
\midrule
deep-active-inference-mc & Python & Monte-Carlo tree search in learned latent spaces; Atari & \cite{fountas2020deep} \\
DeepActiveInference & Python & Continuous deep AIF with backprop-based world models & \cite{millidge2020deep} \\
BTAI\_3MF & Python & Branching-time AIF with multi-step tree planning & \cite{champion2021realizing} \\
Deep\_BTAI\_3MF & Python & Deep neural variant of BTAI with learned state spaces & \cite{champion2021realizing} \\
AXIOM & Python & Object-centric world models; Gameworld 10k in minutes; beats DreamerV3 & \cite{heins2025axiom} \\
active-inference (Voostrum) & Python & Discrete-time AIF agent with flattened state and observation factors & repository (tooling registry) \\
\midrule
\multicolumn{4}{c}{\textit{Predictive Coding \& Neural Generative Coding}} \\
\midrule
PredictiveCodingBackprop & Python & Predictive coding approximates backprop on arbitrary graphs & \cite{millidge2022predictive} \\
\midrule
\multicolumn{4}{c}{\textit{Neuroscience, Embodied \& Biological}} \\
\midrule
ants & Python & Ant foraging simulation with stigmergic AIF agents & \cite{heins2024collective} \\
action-oriented & Python & Action-oriented predictive-processing models & \cite{tschantz2020action} \\
bayesian-mechanics-sdes & Python & Bayesian mechanics: stationary-process simulations and companion code & \cite{sakthivadivel2023bayesian} \\
\midrule
\multicolumn{4}{c}{\textit{Multi-Agent \& Social Dynamics}} \\
\midrule
\midrule
\multicolumn{4}{c}{\textit{Domain-Specific Applications}} \\
\midrule
rl-inference & Python & Bridging RL and active inference policy selection & arXiv:2002.12636 \\
Robust-FE-Minimization & Python & Robust decision-making via free-energy minimization & source-only preprint record \\
\midrule
\multicolumn{4}{c}{\textit{Tutorials \& Educational Resources}} \\
\midrule
\end{longtable}
\end{center}

\FloatBarrier

### Comparative Feature Matrix

\begin{table}[H]
\centering
\caption{Comparative feature matrix of six source-backed representative Active Inference packages. Features span language, state-space type, inference algorithm, hierarchical support, GPU acceleration, observed license status, and primary use case.}
\label{tab:aif_feature_matrix}
\small
\begin{tabular}{lllllll}
\toprule
\textbf{Feature} & \textbf{pymdp} & \textbf{SPM} & \textbf{RxInfer.jl} & \textbf{ActiveInf.jl} & \textbf{Cpp-AIF} & \textbf{FEPS} \\
\midrule
Language & Python & MATLAB & Julia & Julia & C++ & Python \\
State Spaces & Discrete & Disc.+Cont. & Continuous & Discrete & Discrete & Discrete \\
Inference & Msg.\ pass. & Var.\ Bayes & Reactive msg. & Msg.\ pass. & EFE+state & EFE on graphs \\
Deep AIF & Partial & No & Custom factors & No & No & No \\
Real-time & No & No & Yes & No & Yes & No \\
Hierarchical & Yes & Yes (DCM) & Yes & No & Yes & No \\
GPU & No & No & No & No & CPU multi & No \\
License & MIT & Site-only; not assessed & MIT & MIT & BSD-3-Clause & Source-only; not assessed \\
Primary Use & Prototyping & Neuroimaging & Robotics & Comp.\ psych. & Embedded & Interp.\ RL \\
\bottomrule
\end{tabular}
\end{table}

The complementary strengths across these packages reflect a fragmented ecosystem. The table is descriptive rather than a market-share or adoption estimate: it shows a mixture of Python, Julia, MATLAB, and C++ implementations across discrete, continuous, deep, and domain-specific use cases. The variational-free-energy foundations shared by Active Inference and Energy-Based Models---including Helmholtz machines \citep{dayan1995helmholtz}, Boltzmann machines \citep{hinton2002training}, and variational autoencoders \citep{kingma2014auto}---suggest a potential interoperability pathway with mainstream deep generative-modeling frameworks, but no comparative performance claim is made here.

\FloatBarrier

## Knowledge Graph Infrastructure

Our knowledge graph uses an RDF-compatible schema deployable on standard semantic-web infrastructure. The nanopublication model \citep{groth2010anatomy, kuhn2016decentralized} provides a principled atomic unit of scientific evidence: each nanopublication packages a single assertion (e.g., "Paper X supports Hypothesis Y") with explicit provenance and publication metadata in four named RDF graphs (Head, Assertion, Provenance, Publication Info). This structure satisfies the FAIR data principles by design: nanopublications are **F**indable via URI-based identification, **A**ccessible through standard RDF protocols, **I**nteroperable via W3C-standard TriG serialization, and **R**eusable with explicit provenance and CC0 licensing. The full RDF schema and a TriG serialization example are presented in the \hyperref[sec:methods_kg]{methodology} and Appendix \ref{sec:appendix_rdf}.

The engineering trade-offs among the three deployment options are straightforward:

**Nanopublication servers** provide decentralized, content-addressed storage. The pipeline writes nanopublications in two forms: JSON Lines (for incremental checkpointing and tooling) and RDF/TriG per the [nanopublication standard](https://nanopub.net/) (Assertion, Provenance, Publication Info), suitable for the nanopublication network and FAIR deployment. The recent release of nanopub-js v0.1.0 \citep{kuhn2026nanopubjs}---a JavaScript library enabling browser-based creation, signing, and querying of nanopublications---opens the possibility of community-contributed assertions directly from web interfaces, lowering the barrier to participatory evidence curation. Future integration with Trusty URIs \citep{kuhn2014trusty} would provide cryptographic content verification and persistent identifiers for each nanopublication.

**RDF stores** (e.g., Apache Jena Fuseki, Blazegraph, Oxigraph) enable SPARQL queries such as "find all papers supporting hypothesis $H$ published after 2020 in the neuroscience domain (C1)." The cost is operational overhead and query latency.

**Property-graph databases** (e.g., Neo4j) prioritize traversal performance for path queries and community detection, at the expense of semantic-web compatibility.

While RDF and property graphs excel at structurally organizing assertions, it is crucial to recognize that they inherently compress the rich epistemic context of the original papers (e.g., methodological caveats, sample sizes, scope limitations) into flattened confidence scores---a fundamental limitation of current automated knowledge extraction discussed in the \hyperref[sec:conclusion]{conclusion}.

The [Active Inference Ontology namespace](http://activeinference.institute/ontology/) ensures integration with external ontologies and linked-data resources.

## Multi-Level Quality Assurance

Quality assurance operates at four levels: assertion-level confidence and review, graph-level structural consistency, score-level boundary tests, and pipeline-level continuous-integration coverage.

### Assertion-Level Validation

Assertions below a configurable confidence threshold (default 0.6) are flagged for review. The threshold is chosen to balance recall against the prompt-engineering cost of pushing the LLM to over-commit; lowering it inflates noisy neutral assertions, raising it discards weakly supported but legitimate claims. There is no live per-assertion multi-annotator mechanism; instead, an offline stratified sample is checked against a deterministic rule-based reference (see the extraction-agreement study in the main methods section)---a reproducibility floor, not human inter-annotator agreement.

### Graph-Level Consistency Checks

Consistency checks verify that all nodes link to valid targets and no orphan nodes exist. Coverage metrics track the proportion of annotated papers, the fraction of references that resolve inside the corpus, and the per-domain assertion density.

### Score-Level Unit Testing

Hypothesis scoring is validated through unit tests on synthetic data verifying boundary conditions: all-support fixtures must produce scores at $+1$, all-contradict at $-1$, and balanced inputs at $0$. Sensitivity analysis sweeps over confidence thresholds and citation-weighting schemes to measure, rather than assume, qualitative rank stability; the current weighting-only snapshot shows high but non-perfect agreement and remains a diagnostic rather than validation of the underlying evidence.

### Pipeline-Level Test Coverage

Test-driven development enforces 90\% minimum code coverage on project modules and 60\% on shared infrastructure, with real data and computation (no mocking). All tests run on every push; failures block merges and releases.

### Quality Thresholds

\begin{table}[H]
\centering
\caption{Multi-level quality-assurance thresholds enforced across the pipeline. Each level defines a metric, minimum threshold, and failure action. Pipeline-level thresholds (90\% coverage, 100\% pass rate) are enforced via CI gates; lower-level checks emit warnings or block release as indicated.}
\label{tab:quality_thresholds}
\begin{tabular}{llll}
\toprule
\textbf{Level} & \textbf{Metric} & \textbf{Threshold} & \textbf{On Failure} \\
\midrule
Assertion & Confidence $c$ & $\geq 0.6$ & Flag for review \\
Assertion & Rule-reference $\kappa$ (offline sample) & Reported, not gated & Report only \\
Graph & Orphan-node ratio & $= 0$ & Reject build \\
Graph & Corpus coverage & $\geq 80\%$ & Warning \\
Score & Boundary tests (all-support / all-contradict / balanced) & All pass & Block release \\
Score & Sensitivity-sweep stability & Report rank changes and Spearman $ρ$ & Warning \\
Pipeline & Project-code coverage & $\geq 90\%$ & Block merge \\
Pipeline & Infrastructure coverage & $\geq 60\%$ & Block merge \\
Pipeline & Test pass rate & $100\%$ & Block release \\
\bottomrule
\end{tabular}
\end{table}

\FloatBarrier

The hypothesis-evidence results, temporal dynamics of evidence accumulation, and assertion analysis are presented in the \hyperref[sec:hypothesis_results]{hypothesis results section}.
