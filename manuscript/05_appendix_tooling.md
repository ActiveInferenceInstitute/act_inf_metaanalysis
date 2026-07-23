# Appendix: Tooling and Infrastructure \label{sec:tooling}

The practical utility of a computational meta-analysis depends on robust tooling at each pipeline stage: assertion extraction, modeling and simulation, knowledge-graph infrastructure, and quality assurance. This appendix surveys the open-source ecosystem of Active Inference (AIF) and Free Energy Principle (FEP) implementations as of early 2026, documents the engineering trade-offs behind our knowledge-graph backend, and lists the multi-level quality gates enforced by the pipeline.

## LLM-Based Assertion Extraction

Extracting structured assertions from unstructured text is the most labor-intensive component of knowledge-graph construction. Manual annotation produces high-quality results but does not scale to corpora of thousands of papers---a constraint demonstrated by Knight et al. \citep{knight2022fep}, whose systematic analysis of FEP and Active Inference publications required manual coding of structural, visual, and mathematical features for hundreds of annotated papers. We implement a hybrid approach: an LLM performs initial extraction and human review provides validation pathways.

Our extraction pipeline deploys a locally hosted LLM through Ollama \citep{ollama2024}. Each paper's abstract is assessed against the eight hypothesis definitions in a structured prompt requesting a JSON array of assessments. Unlike keyword matching, which detects only topical terms, the LLM evaluates the *semantic relationship* between a paper's claims and each hypothesis. Papers critiquing the FEP correctly receive "contradicts" assessments for FEP Universality (H1), while methodology tutorials receive "neutral" assessments reflecting their pedagogical character. Detailed prompt engineering, schemas, and failure modes are documented in the \hyperref[sec:extraction_pipeline]{extraction pipeline section}.

<!-- See 02b_methods_extraction.md for detailed pipeline documentation -->

## Software Ecosystem

The Active Inference community has developed a rapidly growing ecosystem of open-source tools spanning multiple programming languages, inference paradigms, and application domains. This section provides a comprehensive survey of publicly available implementations as of early 2026, organized by functional category. We emphasize tools with accessible source code: open-source availability is a prerequisite for reproducibility and community-driven validation.

### General-Purpose Frameworks

Six general-purpose frameworks dominate the landscape, collectively covering discrete, continuous, and real-time inference:

**pymdp.** The pymdp library \citep{heins2022pymdp} provides a Python implementation of active inference for discrete state-space POMDPs, supporting message passing on factor graphs, policy inference via expected free energy, and hierarchical generative models. It has become the standard entry point for algorithm development and the most widely forked AIF repository.

**SPM.** The SPM package (Wellcome Centre for Human Neuroimaging) includes MATLAB implementations of Dynamic Causal Modeling and variational Bayesian inference under the FEP. It remains the reference implementation for neuroimaging applications and houses the original Friston-group POMDP scripts.

**RxInfer.jl.** RxInfer is a Julia package for reactive message-passing-based Bayesian inference, supporting real-time and streaming inference suitable for robotics and online learning. Version 4.0.0 (early 2025) \citep{rxinfer2025} introduced projected constraints and adaptive inference optimized for dynamic data streams and autonomous systems. The RxInfer ecosystem includes extensive tutorials covering Bayesian linear regression, hidden Markov models, Kalman filtering, Gaussian process regression, hierarchical Gaussian filters, nonlinear sensor fusion, and active inference mountain car control, available at the [official documentation](https://reactivebayes.github.io/RxInfer.jl/stable/) and the [Learnable Loop](https://learnableloop.com/) tutorial portal.

**ActiveInference.jl.** In parallel to RxInfer's generalized message-passing focus, ActiveInference.jl provides a Julia-native, near drop-in conceptual analogue to Python's `pymdp` \citep{ActiveInferencejl}. It explicitly targets computational psychiatry and cognitive neuroscience workflows emphasizing standard discrete-state POMDP simulation, parameter estimation, and recovery. The library leverages Julia's array semantics---utilizing vectors of arrays to efficiently encode multimodal factorized models via the canonical $\mathbf{A}, \mathbf{B}, \mathbf{C}, \mathbf{D}, \mathbf{E}$ components---to streamline tasks such as generating synthetic behavioral data, fitting models to subject behavior, and probing internal beliefs via robust simulation loops (`infer_states!`, `infer_policies!`, `sample_action!`).

**Cpp-AIF.** The Cpp-AIF header-only C++ library \citep{gregoretti2023cppaif} implements active inference for discrete POMDPs with multicore parallelization of the most demanding computational kernels---multidimensional inner products for expected free energy computation and state estimation. By abstracting the mathematical details behind a high-level API, Cpp-AIF targets embedded systems and performance-critical applications where Python overhead is prohibitive.

**FEPS.** Free Energy Projective Simulation \citep{pazem2024feps} combines active inference with interpretable graphical policy representations, enabling agents to plan via expected free energy while exposing decision logic as human-readable policy graphs. FEPS targets interpretable reinforcement learning tasks where black-box deep agents are undesirable---behavioral biology, clinical decision support, and safety-critical robotics.

### Deep Active Inference

Scaling active inference beyond tabular POMDPs to high-dimensional observation spaces requires neural-network function approximators. A growing body of deep active inference implementations explores this direction:

The foundational deep AIF agent of Fountas et al. \citep{fountas2020deep} introduced Monte-Carlo tree search over learned latent spaces, achieving non-trivial Atari performance. Millidge's DeepActiveInference extended this to continuous control with backpropagation-based world models \citep{millidge2020deep}. Champion's Branching-Time Active Inference (BTAI\_3MF) and its deep variant (Deep\_BTAI\_3MF) implement tree-structured planning under the free-energy objective, scaling active inference to partially observable environments with multi-step lookahead \citep{champion2021realizing}. Most recently, AXIOM \citep{heins2025axiom} achieves competitive Gameworld-10k benchmark performance using expanding object-centric world models, learning in minutes rather than hours---a landmark result for scalability.

### Predictive Coding and Neural Generative Coding

Predictive coding provides the core computational mechanism linking active inference to neuroscience. Several implementations offer accessible entry points:

**ngc-learn.** The Neural Generative Coding library (ngc-learn v3.0, JAX-based) provides a framework for simulating neurobiologically-plausible systems using predictive-coding circuits, Hebbian learning, and spike-based dynamics. It supports constructing arbitrary neural generative models without backpropagation, directly instantiating the FEP's prediction-error minimization at the circuit level.

**Active Neural Generative Coding (ANGC).** ANGC implements a form of active inference using paired predictive-coding circuits---an actor/policy circuit and a world/transition model---that co-evolve across episodes without backpropagation. The agent decomposes behavior into epistemic foraging (uncertainty reduction) and instrumental (reward-seeking) terms, operating with sparse rewards where classical DQN requires dense reward engineering.

**Predictive Coding $\approx$ Backprop.** Millidge et al. demonstrate that predictive-coding networks can approximate backpropagation along arbitrary computational graphs \citep{millidge2022predictive}, providing a biologically plausible alternative to gradient descent. The [PredictiveCodingBackprop](https://github.com/BerenMillidge/PredictiveCodingBackprop) repository provides the reference implementation.

### Benchmarking Progress

The scalability gap between AIF and deep reinforcement learning has been a central limitation of the tools domain. Recent work demonstrates significant progress on two fronts. First, AXIOM \citep{heins2025axiom} outperforms state-of-the-art model-based deep RL agents including DreamerV3 on the Gameworld-10k benchmark while using substantially smaller model sizes; its object-centric scene decomposition enables sample-efficient learning from structured representations rather than raw-pixel memorization. Second, variational message-passing formulations \citep{champion2021realizing} connect EFE decomposition---into risk, ambiguity, epistemic (information-seeking), and instrumental (goal-reaching) components---to practical planning algorithms, advancing the theoretical justification for EFE-based policy selection (H2). Separately, Friston et al. \citep{friston2025active} introduce structure learning via Bayesian Model Reduction as a principled approach to artificial reasoning under active inference.

\FloatBarrier

### Comprehensive Open-Source Tool Survey

The following table catalogs the principal open-source Active Inference implementations surveyed, organized by functional category. For each tool we list the primary language, application domain, and associated publication or repository. The table is intended as a navigational resource for researchers seeking existing implementations relevant to specific hypotheses (H1--H8) or application domains (A1--C5).

\begin{center}
\small
\begin{longtable}{p{3.2cm} p{1.6cm} p{6.4cm} p{2.5cm}}
\caption{Comprehensive open-source survey of Active Inference and Free Energy Principle software, grouped by functional category. Forty-plus implementations span seven categories.}
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
ActivPynference & Python & Discrete AIF with factor-graph message passing; educational focus & --- \\
pypc & Python & Predictive-coding inference engine for continuous models & --- \\
ActiveInferAnts & Rust & Rust-native AIF framework with WASM compilation target & --- \\
\midrule
\multicolumn{4}{c}{\textit{Deep Active Inference}} \\
\midrule
deep-active-inference-mc & Python & Monte-Carlo tree search in learned latent spaces; Atari & \cite{fountas2020deep} \\
DeepActiveInference & Python & Continuous deep AIF with backprop-based world models & \cite{millidge2020deep} \\
BTAI\_3MF & Python & Branching-time AIF with multi-step tree planning & \cite{champion2021realizing} \\
Deep\_BTAI\_3MF & Python & Deep neural variant of BTAI with learned state spaces & \cite{champion2021realizing} \\
OO-BTAI\_3MF & Python & Object-oriented BTAI variant for structured environments & --- \\
AXIOM & Python & Object-centric world models; Gameworld 10k in minutes; beats DreamerV3 & \cite{heins2025axiom} \\
Deep-AIF-POMDPs & Python & Deep AIF for partially observable MDPs & --- \\
Homing-Pigeon & Python & Navigation agent using deep active inference & --- \\
active-inference (Voostrum) & Python & Continuous deep AIF with learned generative models & arXiv:2406.07726 \\
\midrule
\multicolumn{4}{c}{\textit{Predictive Coding \& Neural Generative Coding}} \\
\midrule
ngc-learn & Python/JAX & Neurobiological simulation; predictive-coding circuits, Hebbian learning & --- \\
ANGC & Python & Backprop-free AIF agent with paired PC circuits & AAAI 2022 \\
PredictiveCodingBackprop & Python & Predictive coding approximates backprop on arbitrary graphs & \cite{millidge2022predictive} \\
Supervised-Predictive-Coding & Python & Supervised learning via hierarchical predictive coding & --- \\
predcoding & Python & Minimal predictive-coding implementation & --- \\
pybrid & Python & Hybrid predictive-coding and active-inference library & --- \\
nmpassing & Python & Neural message passing for PC networks & --- \\
\midrule
\multicolumn{4}{c}{\textit{Neuroscience, Embodied \& Biological}} \\
\midrule
allostasis & Python & Allostatic regulation via AIF; interoceptive inference & bioRxiv:2021.02.16 \\
ants & Python & Ant foraging simulation with stigmergic AIF agents & \cite{heins2024collective} \\
Reward\_Bases & Python & Reward-basis function representations under AIF & bioRxiv:2022.04.14 \\
action-oriented & Python & Action-oriented predictive-processing models & \cite{tschantz2020action} \\
Biofirm & Python & Bioregional stewardship via organizational AIF & --- \\
bayesian-mechanics-sdes & Python & Bayesian mechanics: SDE simulations of Markov-blanket dynamics & arXiv:2206.02629 \\
reverse\_engineering & MATLAB & Reverse-engineering neural dynamics under the FEP & --- \\
\midrule
\multicolumn{4}{c}{\textit{Multi-Agent \& Social Dynamics}} \\
\midrule
opinion\_dynamics & Python & Opinion dynamics and belief formation via AIF & --- \\
network-actinf & Python & Network-level active inference with coupled agents & --- \\
Variational-Capsule-Routing & Python & Capsule networks with variational inference routing & AAAI 2020 \\
Active-Inference-Successor & Python & Successor representations under active inference & --- \\
\midrule
\multicolumn{4}{c}{\textit{Domain-Specific Applications}} \\
\midrule
adaptive\_aif\_agents\_fl & Python & Adaptive AIF agents for federated learning & arXiv:2410.09099 \\
smartville & Python & IoT smart-building control via AIF under partial observability & TechRxiv 2025 \\
FEP\_Blorpomon & Python & Game-theoretic AIF agent demonstration & --- \\
MountainCarAI & Python & Mountain car control via active inference & --- \\
rl-inference & Python & Bridging RL and active inference policy selection & arXiv:2002.12636 \\
EFE-GLean & Python & Expected free energy with generalized learning & Entropy 2025 \\
EFEasVFE & Julia & EFE reformulated as variational free energy & --- \\
Robust-FE-Minimization & Python & Robust decision-making via free-energy minimization & arXiv:2503.13223 \\
\midrule
\multicolumn{4}{c}{\textit{Tutorials \& Educational Resources}} \\
\midrule
Active-Inference-from-Scratch & Python & Step-by-step AIF implementation tutorial & --- \\
IC2S2-AIF-Tutorial & Python & Computational social-science AIF tutorial & --- \\
julia4ta tutorials (9x10--12) & Julia & RxInfer-based AIF agent tutorials & --- \\
ActInf Textbook Colab & Python & Interactive notebooks for \cite{parr2022active} & --- \\
deep\_aif\_workshop & Python & Workshop materials for deep active inference & --- \\
AdaptiveResonance.jl & Julia & Adaptive resonance theory models in Julia & --- \\
\end{longtable}
\end{center}

\FloatBarrier

### Comparative Feature Matrix

\begin{table}[H]
\centering
\caption{Comparative feature matrix of seven representative Active Inference packages. Features span language, state-space type, inference algorithm, hierarchical support, GPU acceleration, license, and primary use case.}
\label{tab:aif_feature_matrix}
\small
\begin{tabular}{llllllll}
\toprule
\textbf{Feature} & \textbf{pymdp} & \textbf{SPM} & \textbf{RxInfer.jl} & \textbf{ActiveInf.jl} & \textbf{Cpp-AIF} & \textbf{FEPS} & \textbf{ngc-learn} \\
\midrule
Language & Python & MATLAB & Julia & Julia & C++ & Python & Python/JAX \\
State Spaces & Discrete & Disc.+Cont. & Continuous & Discrete & Discrete & Discrete & Continuous \\
Inference & Msg.\ pass. & Var.\ Bayes & Reactive msg. & Msg.\ pass. & EFE+state & EFE on graphs & Pred.\ coding \\
Deep AIF & Partial & No & Custom factors & No & No & No & Yes \\
Real-time & No & No & Yes & No & Yes & No & No \\
Hierarchical & Yes & Yes (DCM) & Yes & No & Yes & No & Yes \\
GPU & No & No & No & No & CPU multi & No & Yes (JAX) \\
License & MIT & GPL & MIT & MIT & MIT & MIT & BSD-3 \\
Primary Use & Prototyping & Neuroimaging & Robotics & Comp.\ psych. & Embedded & Interp.\ RL & NeuroAI \\
\bottomrule
\end{tabular}
\end{table}

The complementary strengths across these packages reflect a fragmented but maturing ecosystem. The survey reveals several patterns: (1) Python dominates ($\sim$75\% of implementations), with Julia emerging as the preferred alternative for performance-critical applications; (2) discrete-POMDP implementations outnumber continuous variants by approximately 3:1, reflecting pymdp's community influence; (3) deep active-inference implementations are concentrated in a small number of research groups (Champion, Millidge, Fountas, Heins), suggesting high barriers to entry; (4) multi-agent and social AIF implementations remain sparse relative to single-agent tools; and (5) domain-specific applications (IoT, federated learning, smart buildings) represent the newest and fastest-growing category, aligning with the temporal growth patterns observed in the C-domain (applied) subfields. The variational-free-energy foundations shared by Active Inference and Energy-Based Models---including Helmholtz machines \citep{dayan1995helmholtz}, Boltzmann machines \citep{hinton2002training}, and variational autoencoders \citep{kingma2014auto}---suggest that interoperability with mainstream deep generative-modeling frameworks (PyTorch, JAX) could bridge these parallel research programs.

\FloatBarrier

## Knowledge Graph Infrastructure

Our knowledge graph uses an RDF-compatible schema deployable on standard semantic-web infrastructure. The nanopublication model \citep{groth2010anatomy, kuhn2016decentralized} provides a principled atomic unit of scientific evidence: each nanopublication packages a single assertion (e.g., "Paper X supports Hypothesis Y") with explicit provenance and publication metadata in four named RDF graphs (Head, Assertion, Provenance, Publication Info). This structure satisfies the FAIR data principles by design: nanopublications are **F**indable via URI-based identification, **A**ccessible through standard RDF protocols, **I**nteroperable via W3C-standard TriG serialization, and **R**eusable with explicit provenance and CC0 licensing. The full RDF schema and a TriG serialization example are presented in the \hyperref[sec:methods_kg]{methodology} and Appendix~\ref{sec:appendix_rdf}.

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

Hypothesis scoring is validated through unit tests on synthetic data verifying boundary conditions: all-support fixtures must produce scores at $+1$, all-contradict at $-1$, and balanced inputs at $0$. Sensitivity analysis sweeps over confidence thresholds and citation-weighting schemes to confirm that qualitative rankings are stable.

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
Score & Sensitivity-sweep stability & Top-$k$ ranks unchanged & Warning \\
Pipeline & Project-code coverage & $\geq 90\%$ & Block merge \\
Pipeline & Infrastructure coverage & $\geq 60\%$ & Block merge \\
Pipeline & Test pass rate & $100\%$ & Block release \\
\bottomrule
\end{tabular}
\end{table}

\FloatBarrier

The hypothesis-evidence results, temporal dynamics of evidence accumulation, and assertion analysis are presented in the \hyperref[sec:hypothesis_results]{hypothesis results section}.
