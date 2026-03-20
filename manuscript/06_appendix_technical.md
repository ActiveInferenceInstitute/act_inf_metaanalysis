# Appendix: Mathematical and Algorithmic Details \label{sec:technical_appendix}

_This appendix collects the formal mathematical definitions, derivations, and algorithmic specifications referenced from the main methodology section._

## Citation-Weighted Hypothesis Scoring Formula \label{sec:appendix_scoring}

For each hypothesis $H$, we compute a citation-weighted evidence score aggregating all assertions relevant to $H$:

\begin{equation}
\text{score}(H) = \frac{\sum_{a \in S(H)} w(a) - \sum_{a \in C(H)} w(a)}{\sum_{a \in A(H)} w(a)} \label{eq:app_score}
\end{equation}

where $S(H)$ is the set of supporting assertions, $C(H)$ is the set of contradicting assertions, $A(H)$ is all assertions for $H$ (including neutral), and the weight function is:

\begin{equation}
w(a) = \log(1 + \text{citations}(a)) \cdot \text{confidence}(a) \label{eq:app_weight}
\end{equation}

The logarithmic citation weighting ensures that highly cited papers carry more influence while preventing any single blockbuster paper from dominating the score. The score lies in $[-1, 1]$: values near $+1$ indicate strong supporting evidence, values near $-1$ indicate strong contradicting evidence, and values near $0$ indicate balanced or insufficient evidence. Crucially, as discussed in the main text, this score represents a _relative evidentiary ranking_ within the current literature topology, not a calibrated Bayesian probability of the hypothesis actually being true.

**Temporal aggregation.** We additionally compute temporal trends by evaluating the cumulative score at each year $t$, using only assertions from papers published in year $\leq t$:

\begin{equation}
\text{score}(H, t) = \frac{\sum_{a \in S(H,t)} w(a) - \sum_{a \in C(H,t)} w(a)}{\sum_{a \in A(H,t)} w(a)} \label{eq:app_score_t}
\end{equation}

This reveals whether support for a hypothesis is growing, declining, or plateauing over time.

## Non-negative Matrix Factorization (NMF) for Topic Modeling \label{sec:appendix_nmf}

We apply NMF to the TF-IDF matrix of the corpus to discover latent topics. Given the document-term matrix $V \in \mathbb{R}^{n \times m}_{\geq 0}$, NMF finds factor matrices $W \in \mathbb{R}^{n \times k}_{\geq 0}$ and $H \in \mathbb{R}^{k \times m}_{\geq 0}$ such that $V \approx WH$, where $k$ is the number of topics.

We use multiplicative update rules \citep{lee1999nmf}:

\begin{equation}
H \leftarrow H \odot \frac{W^T V}{W^T W H + \epsilon}, \quad W \leftarrow W \odot \frac{V H^T}{W H H^T + \epsilon} \label{eq:nmf_update}
\end{equation}

with $\epsilon = 10^{-10}$ for numerical stability and a fixed random seed of 42 for reproducibility (ensuring deterministic topic alignment across pipeline runs, with empirical stability confirmed via Jaccard similarities $> 0.90$ across alternative seeds).

**Term-Frequency Inverse Document Frequency (TF-IDF).** The document-term matrix is constructed using TF-IDF weighting \citep{salton1975vector}. For term $t$ in document $d$:

\begin{equation}
\text{TF-IDF}(t, d) = \text{tf}(t, d) \cdot \log\!\left(\frac{N}{\text{df}(t)}\right) \label{eq:tfidf}
\end{equation}

where $\text{tf}(t, d)$ is the term frequency, $N$ is the total number of documents, and $\text{df}(t)$ is the document frequency of term $t$.

## Field Growth-Rate Estimation \label{sec:appendix_growth}

The **mean year-over-year growth rate** $\bar{g}$ is the arithmetic mean of annual growth rates computed only for years where the prior year had non-zero publications:

\begin{equation}
\bar{g} = \frac{1}{|Y|} \sum_{y \in Y} \frac{n_y - n_{y-1}}{n_{y-1}} \label{eq:mean_growth}
\end{equation}

where $Y = \{y : n_{y-1} > 0\}$ and $n_y$ is the number of publications in year $y$.

The **doubling time** $t_d$ is derived from the mean annual growth rate:

\begin{equation}
t_d = \frac{\ln 2}{\ln(1 + \bar{g})} \label{eq:doubling_time}
\end{equation}

The **compound annual growth rate** (CAGR) over the full span $[y_0, y_T]$ is:

\begin{equation}
\text{CAGR} = \left(\frac{n_{\text{cumulative}}(y_T)}{n_{\text{cumulative}}(y_0)}\right)^{1/(y_T - y_0)} - 1 \label{eq:cagr}
\end{equation}

For the current corpus, CAGR $= {{CAGR_PCT}}\%$. The more recent growth phase (2010--{{YEAR_END}}) exhibits substantially higher annualized growth.

## Advanced Visualization Methods \label{sec:appendix_viz}

### PCA of TF-IDF Embeddings

Principal Component Analysis (PCA) is applied to the TF-IDF matrix $V$ to project each document into a 2-D space. The projection preserves the directions of maximum variance, enabling visual inspection of document clustering by domain. Loading arrows overlay the top-variance terms onto the scatter plot, showing which vocabulary drives the principal components.

### Hierarchical Clustering Dendrogram

For each domain $s$, we compute the centroid $\bar{v}_s = \frac{1}{|D_s|} \sum_{d \in D_s} v_d$ where $D_s$ is the set of documents in domain $s$ and $v_d$ is the TF-IDF vector of document $d$. Ward linkage is applied to the centroid matrix to produce a hierarchical clustering dendrogram showing semantic proximity between domains.

### Term Heatmap

For each domain $s$ and term $t$, we compute the mean TF-IDF weight $\bar{w}_{s,t} = \frac{1}{|D_s|} \sum_{d \in D_s} \text{TF-IDF}(t, d)$. The heatmap displays $\bar{w}_{s,t}$ for the top-$k$ terms (by global document frequency) across all domains, with cell intensity proportional to mean weight. This reveals distinctive vocabulary patterns that differentiate domains beyond the keyword-level classification used for subfield assignment.

### Term Co-occurrence Matrix

The co-occurrence matrix $C \in \mathbb{R}^{k \times k}$ counts the number of documents in which two terms appear together. For top-$k$ terms by document frequency, $C_{ij} = |\{d : t_i \in d \land t_j \in d\}|$. The matrix is normalized to $[0, 1]$ by dividing by the maximum entry and visualized as a symmetric heatmap.

## Nanopublication RDF Schema \label{sec:appendix_rdf}

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


\begin{table}[htbp]
\centering
\caption{RDF namespace definitions used in the knowledge graph and nanopublication serialization. Each prefix maps to a W3C or domain-specific URI.}
\label{tab:namespace_definitions}
\begin{tabular}{lll}
\toprule
\textbf{Prefix} & \textbf{URI} & \textbf{Purpose} \\
\midrule
\texttt{np:} & \texttt{http://www.nanopub.org/nschema\#} & Nanopub structural predicates \\
\texttt{prov:} & \texttt{http://www.w3.org/ns/prov\#} & PROV-O provenance model \\
\texttt{dc:} & \texttt{http://purl.org/dc/terms/} & Dublin Core metadata \\
\texttt{aif:} & \texttt{http://activeinference.institute/ontology/} & Domain-specific predicates \\
\texttt{xsd:} & \texttt{http://www.w3.org/2001/XMLSchema\#} & XML Schema datatypes \\
\bottomrule
\end{tabular}
\end{table}


### Core Triple Patterns

The knowledge graph encodes five fundamental relationships:


\begin{table}[htbp]
\centering
\caption{Core RDF triple patterns encoding the five fundamental relationships in the knowledge graph. Each pattern links paper, assertion, hypothesis, or subfield nodes.}
\label{tab:core_triple_patterns}
\begin{tabular}{ll}
\toprule
\textbf{Triple Pattern} & \textbf{Meaning} \\
\midrule
\texttt{Paper --aif:asserts--> Assertion} & A paper makes a claim \\
\texttt{Paper --aif:cites--> Paper} & Intra-corpus citation link \\
\texttt{Paper --aif:belongsTo--> Subfield} & Domain classification \\
\texttt{Assertion --aif:supports--> Hypothesis} & Supporting evidence \\
\texttt{Assertion --aif:contradicts--> Hypothesis} & Contradicting evidence \\
\bottomrule
\end{tabular}
\end{table}

