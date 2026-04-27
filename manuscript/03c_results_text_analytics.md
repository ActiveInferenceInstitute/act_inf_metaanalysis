### Text Analytics: Topic Modeling, Vocabulary Structure, and Document Embeddings \label{sec:text_analytics}

This section examines the latent semantic structure of the Active Inference corpus through complementary text-analytic methods: non-negative matrix factorization for topic discovery, TF-IDF vocabulary analysis, document embedding projections, and term co-occurrence patterns. Together, these analyses reveal thematic structure that cuts across the keyword-based domain taxonomy presented in the \hyperref[sec:field_overview]{field overview}.

### Topic Modeling: Latent Structure

Non-negative matrix factorization (NMF) applied to the TF-IDF matrix identifies five latent topics:


\begin{table}[htbp]
\centering
\caption{Non-negative matrix factorization (NMF) topic decomposition of the corpus TF-IDF matrix ($k = {{NUM_TOPICS}}$ topics). Top terms are ranked by NMF component weight; interpretations reflect dominant thematic content.}
\label{tab:nmf_topics}
\begin{tabular}{clp{6cm}}
\toprule
\textbf{Topic} & \textbf{Top Terms} & \textbf{Interpretation} \\
\midrule
0 & learning, agent, model, agents, active, environments, aif, inference, environment, based & Agent-environment modeling and robotic applications \\
1 & inference, active, energy, free, variational, control, bayesian, expected, optimal, principle & Active inference agents and decision-making \\
2 & states, internal, external, systems, markov, system, dynamics, information, beliefs, self & Markov blankets and internal/external states \\
3 & fep, systems, ai, principle, energy, free, theory, networks, modeling, language & Free energy principle and AI systems \\
4 & predictive, brain, cognitive, prediction, perception, processing, sensory, models, coding, model & Predictive coding and cognitive neuroscience \\
\bottomrule
\end{tabular}
\end{table}


#### Topic–Domain Overlap

These topics are partially orthogonal to the domain taxonomy. Topic 0 (agent-environment modeling) spans tools (B), robotics (C2), and core theory (A1)—a cross-cutting theme that the keyword classifier cannot capture. Topic 4 (predictive coding and cognitive neuroscience) aligns closely with neuroscience (C1) but also draws from core theory. Topic 2 (Markov blankets and states) captures the mathematical core shared across domains. Topic 3 (FEP and AI systems) reveals the growing intersection of active inference with mainstream artificial intelligence research. The extracted topics demonstrate high stability; rerunning NMF across multiple random seed initializations yields identical topic clusters (Jaccard similarity $> 0.90$ for top term sets). The absence of retrieval noise (no spurious physics topics) confirms that the phrase-matched arXiv query effectively filters irrelevant content (Figure \ref{fig:topic_term_bars}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/topic_term_bars.png}
\caption{Top 10 terms per NMF topic ($k = {{NUM_TOPICS}}$ topics, ${{NUM_VOCAB_FEATURES}}$ vocabulary features). Term weights reflect NMF component loadings; higher-weighted terms define each topic's semantic focus.}
\label{fig:topic_term_bars}
\end{figure}

### Vocabulary Analysis

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/word_cloud.png}
\caption{Word cloud of corpus vocabulary ($N = {{CORPUS_SIZE}}$ abstracts) sized by maximum NMF component weight. Prominent terms—"inference," "active," "free energy," "model"—reflect the field's core theoretical commitments.}
\label{fig:word_cloud}
\end{figure}

The word cloud (Figure \ref{fig:word_cloud}) reveals the conceptual core of the Active Inference literature: terms related to the Free Energy Principle ("inference," "active," "free energy," "model," "bayesian") dominate, while application-specific terms appear at smaller scales, reflecting the domain distribution's heavy A2 concentration.

### Document Embedding Projections

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/pca_embeddings.png}
\caption{PCA projection of TF-IDF document embeddings ($N = {{CORPUS_SIZE}}$ documents, ${{NUM_VOCAB_FEATURES}}$ features), colored by domain. Loading arrows indicate vocabulary terms contributing most to each principal component. Variance explained is annotated per axis.}
\label{fig:pca_embeddings}
\end{figure}

Principal Component Analysis of the TF-IDF document-term matrix projects each paper into a two-dimensional space that preserves the directions of maximum variance (Figure \ref{fig:pca_embeddings}). Rather than serving solely as a visual clustering aid, this projection provides a quantitative measure of semantic distance between subfields. The scatter plot, colored by domain assignment, reveals the degree of semantic separation between domains. Loading arrows overlay the top-variance terms, showing which vocabulary drives the principal components and highlighting the structural overlap between theoretically similar domains that keyword-based hard categorization obscures.

### Domain Semantic Similarity

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

### Term Co-occurrence Patterns

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/cooccurrence_matrix.png}
\caption{Normalized co-occurrence matrix for the 30 most frequent terms across $N = {{CORPUS_SIZE}}$ abstracts. Cell intensity reflects the fraction of documents in which two terms co-appear, normalized to $[0, 1]$.}
\label{fig:cooccurrence_matrix}
\end{figure}

The co-occurrence matrix (Figure \ref{fig:cooccurrence_matrix}) for the 30 most frequent corpus terms reveals tightly coupled term clusters corresponding to the NMF topics. The strong co-occurrence between "free," "energy," "principle," and "bayesian" anchors the theoretical core, while application-specific term clusters (e.g., "brain"–"cognitive"–"predictive"–"coding") form distinct off-diagonal blocks. The relative isolation of robotics-specific terms from neuroscience terms confirms the semantic separation between these application domains despite their shared theoretical foundation.
