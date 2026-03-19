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
| **Assertion** | A directed, confidence-scored claim linking a paper to a hypothesis (supports, contradicts, or neutral). The basic unit of evidence in the knowledge graph, representing a machine-extracted classification rather than a definitive human judgment. |
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
