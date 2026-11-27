# Notation, Abbreviations, and Glossary

This appendix consolidates the mathematical notation, abbreviations, hypothesis identifiers, and key terminology used throughout the manuscript. Each table is self-contained and may be consulted independently. Cross-references in the main text use the labels declared here.

## Mathematical Symbols and Notation

The following symbols appear in the methodology, results, and technical appendices. Where a quantity is defined formally, the relevant equation is referenced inline; otherwise the description here is the canonical definition. All probabilities and confidences are real-valued in $[0, 1]$, and all aggregate scores are in $[-1, 1]$.

\begin{table}[H]
\centering
\caption{Mathematical symbols and notation used throughout the manuscript. Scoring quantities are defined formally in \S\ref{sec:methods_kg} and \S\ref{sec:appendix_scoring}; growth metrics in \S\ref{sec:appendix_growth}; topic-modeling notation in \S\ref{sec:appendix_nmf}.}
\label{tab:notation_symbols}
\begin{tabular}{ll}
\toprule
\textbf{Symbol} & \textbf{Description} \\
\midrule
$N$ & Corpus size after deduplication (total unique papers) \\
$n$ & Subfield paper count (papers within a single domain category) \\
$T = y_T - y_0$ & Time span in years (used for CAGR) \\
$y_0, y_T$ & First and last years in the publication window \\
$n_y$ & Number of publications in year $y$ \\
$w(a)$ & Citation-weighted weight of assertion $a$: $\log(1 + \text{citations}) \cdot c$ \\
$\score(H)$ & Aggregate citation-weighted evidence score for hypothesis $H$, range $[-1, 1]$ \\
$\score(H, t)$ & Cumulative score for $H$ using only assertions from papers published $\leq t$ \\
$S(H), C(H), A(H)$ & Supporting / contradicting / all assertion sets for hypothesis $H$ \\
$c$ & Assertion confidence reported by the LLM, range $[0, 1]$ \\
$d$ & Assertion direction $\in \{\text{supports}, \text{contradicts}, \text{neutral}\}$ \\
$k$ & Number of latent topics in NMF factorization \\
$V \in \mathbb{R}^{n \times m}_{\geq 0}$ & TF-IDF document-term matrix (documents $\times$ terms) \\
$W \in \mathbb{R}^{n \times k}_{\geq 0}$ & NMF document-topic factor \\
$H \in \mathbb{R}^{k \times m}_{\geq 0}$ & NMF topic-term factor (overloaded notation; context disambiguates) \\
$\epsilon$ & Numerical-stability constant ($10^{-\!10}$) \\
$\text{CAGR}$ & Compound annual growth rate (Eq. \ref{eq:cagr}) \\
$t_d$ & Publication doubling time in years (Eq. \ref{eq:doubling_time}) \\
$\bar{g}$ & Mean year-over-year growth rate (Eq. \ref{eq:mean_growth}) \\
$\kappa$ & Cohen's kappa, agreement coefficient (used here for rule-based reference vs.\ pipeline direction agreement, not human annotation) \\
$\text{tf}(t,d)$ & Normalized term frequency of $t$ in document $d$ \\
$\text{df}(t)$ & Document frequency of term $t$ across the corpus \\
$\F$ & Variational free energy \\
$\mathbf{G}$ & Expected free energy (used for policy ranking) \\
$\KL$ & Kullback--Leibler divergence \\
$\E$ & Expectation operator \\
\bottomrule
\end{tabular}
\end{table}

## Abbreviations and Acronyms Used

The acronyms below appear at least once in the main text, methods, results, or appendices. Domain-specific shorthands such as the A/B/C taxonomy categories (e.g., A1, A2, B, C1--C5) are documented inline at first use in the \hyperref[sec:field_overview]{field overview} and the \hyperref[sec:subfield_analyses]{subfield analyses}.

\begin{table}[H]
\centering
\caption{Abbreviations and acronyms used in this manuscript, listed alphabetically. Where an acronym names a software package or organization, the canonical reference appears in the bibliography.}
\label{tab:abbreviations}
\begin{tabular}{ll}
\toprule
\textbf{Abbreviation} & \textbf{Definition} \\
\midrule
AIF & Active Inference \\
API & Application Programming Interface \\
arXiv & Open-access preprint repository (\texttt{arxiv.org}) \\
BTAI & Branching-Time Active Inference \\
CAGR & Compound Annual Growth Rate \\
CC0 & Creative Commons Zero (public-domain dedication) \\
CI & Continuous Integration \\
CNM & Conceptual Nexus Model (ResNei) \\
DCM & Dynamic Causal Modelling \\
DeSci & Decentralized Science \\
DOI & Digital Object Identifier \\
EBM & Energy-Based Model \\
EFE & Expected Free Energy \\
FAIR & Findable, Accessible, Interoperable, Reusable \\
FAIR4RS & FAIR Principles for Research Software \\
FEP & Free Energy Principle \\
FEPS & Free Energy Projective Simulation \\
HITS & Hyperlink-Induced Topic Search (Kleinberg) \\
IaC & Infrastructure as Code \\
JSON & JavaScript Object Notation \\
JSONL & JSON Lines (newline-delimited JSON) \\
KG & Knowledge Graph \\
KL & Kullback--Leibler (divergence) \\
LLM & Large Language Model \\
MBR & Bayesian Model Reduction \\
MCMC & Markov Chain Monte Carlo \\
MIT & Massachusetts Institute of Technology \\
NLP & Natural Language Processing \\
NMF & Non-negative Matrix Factorization \\
ORCID & Open Researcher and Contributor ID \\
PCA & Principal Component Analysis \\
PDF & Portable Document Format \\
POMDP & Partially Observable Markov Decision Process \\
PROV-O & PROV Ontology (W3C provenance data model) \\
RBM & Restricted Boltzmann Machine \\
RDF & Resource Description Framework \\
ResNei & Research Neighbourhood (cognitive-ergonomic platform) \\
RL & Reinforcement Learning \\
SDE & Stochastic Differential Equation \\
SPARQL & SPARQL Protocol and RDF Query Language \\
SPM & Statistical Parametric Mapping \\
TDD & Test-Driven Development \\
TF-IDF & Term Frequency--Inverse Document Frequency \\
TriG & Terse RDF Triple Language with Named Graphs \\
URI & Uniform Resource Identifier \\
VAE & Variational Autoencoder \\
VFE & Variational Free Energy \\
WCAG & Web Content Accessibility Guidelines \\
W3C & World Wide Web Consortium \\
\bottomrule
\end{tabular}
\end{table}

## Standard Hypothesis Definitions and Identifiers

The eight hypotheses below define the evaluation rubric used by the LLM-based assertion extractor (\hyperref[sec:extraction_pipeline]{extraction pipeline}). Each hypothesis is anchored to its primary domain in the A/B/C taxonomy, but assertions are extracted from any paper whose abstract relates substantively to the claim. Quantitative results across these hypotheses are reported in the \hyperref[sec:hypothesis_results]{hypothesis results section}.

\begin{table}[H]
\centering
\caption{Standard hypothesis definitions tracked throughout the meta-analysis. The Scope column records the primary domain in the A/B/C taxonomy; assertions are not restricted to that domain. Wording reflects the prompt presented to the extraction LLM.}
\label{tab:hypothesis_definitions}
\begin{tabular}{cp{8cm}c}
\toprule
\textbf{ID} & \textbf{Hypothesis} & \textbf{Scope} \\
\midrule
H1 & FEP Universality: the Free Energy Principle applies universally to all self-organizing systems, from cells to ecosystems. & A (Core Theory) \\
H2 & AIF Optimality: Active Inference agents achieve principled, near-optimal decision-making under uncertainty by minimizing expected free energy. & B (Tools) \\
H3 & Markov Blanket Realism: Markov blankets correspond to real, physically realizable boundaries between systems and their environments. & A (Core Theory) \\
H4 & Predictive Coding: cortical hierarchies minimize prediction errors via predictive coding, providing a neurobiologically realistic substrate for active inference. & C1 (Neuroscience) \\
H5 & Scalability: Active Inference scales to complex, high-dimensional environments comparable to those addressed by deep reinforcement learning. & B (Tools) \\
H6 & Clinical Utility: Active Inference produces clinically useful computational models of psychiatric and neurological conditions. & C4 (Psychiatry) \\
H7 & Morphogenesis: the FEP explains morphogenetic, developmental, and self-organizing biological processes. & C5 (Biology) \\
H8 & Language AIF: Active Inference provides a viable framework for language comprehension, production, and communication. & C3 (Language) \\
\bottomrule
\end{tabular}
\end{table}

\FloatBarrier

## Glossary of Key Terms

The glossary below defines pipeline-specific concepts, statistical methods, and domain terminology referenced in the main text. Software package names appear in typewriter font; mathematical objects use the notation defined above. Where a term has both a colloquial and a technical sense, the technical reading is given.

\begin{longtable}{p{4cm}p{11cm}}
\caption{Glossary of key terms used in this manuscript, including pipeline-specific concepts, statistical methods, and domain terminology.}
\label{tab:glossary} \\
\toprule
\textbf{Term} & \textbf{Definition} \\
\midrule
\endfirsthead
\toprule
\textbf{Term} & \textbf{Definition} \\
\midrule
\endhead
\midrule
\multicolumn{2}{r}{\textit{Continued on next page}} \\
\endfoot
\bottomrule
\endlastfoot
Active Inference & A framework in which agents minimize expected free energy to select actions, unifying perception, learning, and decision-making under the Free Energy Principle. \\
Assertion & A directed, confidence-scored claim linking a paper to a hypothesis (supports, contradicts, or neutral). The basic unit of evidence in the knowledge graph; a machine-extracted classification, not a human verdict. \\
Bayesian Mechanics & The formal extension of FEP that grounds Markov-blanket dynamics in stochastic physics, casting belief updates as gradient flows on a free-energy potential. \\
Canonical ID & The unique identifier assigned to each paper during deduplication, following DOI $>$ arXiv ID $>$ Semantic Scholar ID $>$ OpenAlex ID $>$ title hash. \\
Checkpoint & A JSON Lines snapshot of LLM extraction progress, recording which papers have been processed and the resulting assertions, enabling incremental resume after interruption. \\
Citation-Weighted Score & The hypothesis-level evidence aggregate combining direction, confidence, and a logarithmic citation weight (Eq. \ref{eq:app_score}). \\
Compound Annual Growth Rate (CAGR) & The constant annual rate that, compounded over the publication window, takes the cumulative count from the first to the last year (Eq. \ref{eq:cagr}). \\
Conceptual Nexus Model (CNM) & The modular knowledge-graph unit used by ResNei; each CNM packages concepts with provenance and supports longitudinal, latitudinal, and relational navigation. \\
Contrastive Divergence & An approximate gradient-based training algorithm for energy-based models \citep{hinton2002training} that truncates the Markov chain used to estimate the gradient of the log-partition function. \\
Domain Timeline & Per-domain yearly publication counts visualizing temporal evolution across the eight tracked categories (A1--A2, B, C1--C5). \\
Doubling Time ($t_d$) & Years required for cumulative output to double under the prevailing growth rate (Eq. \ref{eq:doubling_time}). \\
Energy-Based Model (EBM) & A class of generative models defining $p(x) \propto \exp(-E(x))$ for an unnormalized energy $E$. Includes Boltzmann machines, Helmholtz machines, and VAEs as special or related cases. \\
Expected Free Energy (EFE) & A scalar combining epistemic (uncertainty-reducing) and pragmatic (goal-achieving) value, minimized over policies. Decomposes equivalently into risk + ambiguity or epistemic + instrumental terms \citep{dacosta2020active}. \\
FAIR Principles & Findable, Accessible, Interoperable, Reusable: a set of guiding principles for scientific data infrastructure \citep{wilkinson2016fair}. The pipeline's nanopublications satisfy all four. \\
Free Energy Principle (FEP) & The principle that self-organizing systems minimize variational free energy---an upper bound on surprise---to maintain their structural integrity. \\
Generative Model & A probabilistic model specifying the joint distribution over hidden states and observations, encoding an agent's beliefs about how observations are generated. \\
Greedy Modularity Maximization & The Clauset-Newman-Moore algorithm \citep{clauset2004finding} for community detection. Implemented via NetworkX \texttt{greedy\_modularity\_communities}; applied here to the citation graph to identify clusters of densely interconnected papers. \\
HITS Hub/Authority Scores & Kleinberg's mutually reinforcing centrality metrics \citep{kleinberg1999authoritative}: hubs point to many authorities; authorities are pointed to by many hubs. \\
Helmholtz Machine & A generative model with separate recognition (bottom-up) and generative (top-down) networks trained by the wake-sleep algorithm \citep{dayan1995helmholtz}; a direct precursor to the variational autoencoder and the FEP's recognition--generation duality. \\
Incremental Resume & The pipeline's ability to continue from where a previous run stopped, loading existing corpus and assertion snapshots and processing only new papers; controlled by \texttt{--clear-corpus} and \texttt{--clear-assertions} CLI flags. \\
Knowledge Graph & A directed graph encoding papers, assertions, hypotheses, and their relationships, serialized in an RDF-compatible format. \\
LLM Config & A configuration record specifying the Ollama model name, API URL, sampling temperature, maximum retries, and retry delay used by the assertion extractor. \\
Markov Blanket & A statistical boundary separating internal from external states, defined as the node set that renders a system conditionally independent of its environment. \\
Mean Year-over-Year Growth ($\bar{g}$) & Arithmetic mean of $(n_y - n_{y-1})/n_{y-1}$ across years with non-zero prior-year counts (Eq. \ref{eq:mean_growth}). \\
Named Graph & An RDF graph identified by a URI, enabling multiple graphs to coexist in a single dataset. Nanopublications use four named graphs (Head, Assertion, Provenance, Publication Info). \\
Nanopublication & A minimal, self-contained unit of publishable knowledge consisting of an assertion, provenance metadata, and publication context \citep{groth2010anatomy, kuhn2016decentralized}. \\
NMF (Non-negative Matrix Factorization) & A factorization in which $V$ is approximately $W H$ with all factors non-negative, used here for unsupervised topic discovery (\S\ref{sec:appendix_nmf}). \\
Ollama & A locally hosted LLM server used for assertion extraction; provides reproducibility and avoids external API dependencies \citep{ollama2024}. \\
PageRank & A centrality metric originally designed for web-page ranking. In citation networks, PageRank surfaces influential papers that act as hubs across otherwise disconnected subgraphs. \\
Precision & The inverse variance of a probability distribution; in active inference, precision weighting determines the influence of prediction errors at each level of a hierarchy. \\
Predictive Coding & A scheme in which each cortical level passes prediction errors upward and predictions downward, minimizing local free-energy bounds layer by layer. \\
Progressive Parsing & The pipeline's three-stage JSON recovery strategy for malformed LLM output: (1) direct parse, (2) strip Markdown code fences and retry, (3) extract first \texttt{[\ldots]} substring. Papers failing all three are logged and skipped. \\
Provenance & The recorded lineage of an assertion: source paper, extraction model, timestamp, and confidence; serialized in the Provenance named graph of each nanopublication. \\
Reference Resolution Rate & Fraction of all outgoing references that resolve to another paper inside the corpus; reported as {{CITATION_RESOLUTION_PCT}}\% in the present analysis and used as a lower bound on intra-corpus citation density. \\
Stochastic Differential Equation (SDE) & A differential equation driven by a Wiener (white-noise) process; used in Bayesian-mechanics derivations of Markov-blanket dynamics. \\
Surprise (Self-Information) & The negative log probability of an observation under the agent's generative model; variational free energy is an upper bound on surprise. \\
Term Frequency--Inverse Document Frequency (TF-IDF) & A weighting that combines normalized term frequency with logarithmic inverse document frequency (Eq. \ref{eq:tfidf}); the standard input to NMF in this pipeline. \\
TriG & A serialization format extending Turtle with named-graph support, used to encode nanopublications as RDF datasets. \\
Trusty URI & A URI containing a cryptographic hash of its content \citep{kuhn2014trusty}, providing verifiable immutability and content-addressable identification for nanopublications. \\
Variational Free Energy (VFE) & An upper bound on surprise (negative log evidence) decomposable into complexity (KL from prior) and accuracy (expected log-likelihood). \\
Variational Inference & Approximate posterior inference by optimization, replacing intractable marginalization with optimization of a tractable variational distribution. \\
Ward Linkage & A hierarchical clustering method that minimizes total within-cluster variance at each merge step; used to compute domain-centroid dendrograms from mean TF-IDF vectors. \\
Wong Palette & The colorblind-safe 8-color palette of Wong (2011) \citep{wong2011colorblind}, used as the standard visualization palette throughout all pipeline-generated figures. \\
\end{longtable}

\FloatBarrier
