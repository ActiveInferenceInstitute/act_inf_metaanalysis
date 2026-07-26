## Citation Network Topology {#sec:citation_network}

The intra-corpus citation network provides a structural view of how Active Inference research is organized, identifying influential hub papers, community structure, and patterns of citation isolation (Figure \ref{fig:citation_network}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/citation_network.png}
\caption{Intra-corpus citation network. The figure shows a 100-node view (905 edges) of the full graph (1106 nodes, 4,829 edges); node size reflects in-degree and highly cited foundational papers serve as nexus points connecting sub-domains.}
\label{fig:citation_network}
\end{figure}

### Network Density and Degree Distribution

The intra-corpus citation network contains 1106 nodes and 4,829 edges, with a density of 0.40\% and 645 connected components. The average in-degree of approximately 4.4 indicates that most papers receive few intra-corpus citations, consistent with the field's rapid expansion: the majority of recent papers have not yet accumulated citations within the corpus (Figure \ref{fig:degree_distribution}). Only 10.4\% of all identified references (4,829 intra-corpus matches out of 46,598 total reference entries) resolve to other papers within the corpus, reflecting cross-source identifier mismatches and the field's engagement with a broad external literature base. Community detection identifies clusters via greedy modularity maximization \citep{clauset2004finding}.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.7\textwidth]{figures/degree_distribution.png}
\caption{In-degree distribution of the citation network. The power-law tail is characteristic of citation networks, with a small number of highly cited hubs.}
\label{fig:degree_distribution}
\end{figure}

### Connected Components and Citation Isolation

The high number of connected components (645 out of 1106 nodes) reveals that much of the corpus consists of citation-isolated papers—works that neither cite nor are cited by other papers in the collection. A single Giant Connected Component (GCC) typically dominates mature scientific networks; here, with 645 components across 1106 nodes, the GCC contains a minority of nodes while the remainder form singletons or small clusters of two to three papers. This is partially an artifact of cross-source identifier mismatches, but it also reflects the field's pattern of papers engaging with the FEP literature conceptually without building explicit, graph-tractable citation chains. PageRank analysis identifies highly influential papers, predominantly Friston's foundational work \citep{friston2010free} and the AIF textbook \citep{parr2022active}, which serve as nexus points linking otherwise disconnected subgraphs.

### Network Summary


\begin{table}[htbp]
\centering
\caption{Intra-corpus citation network summary statistics ($N = 1106$ papers, 1106 nodes). The low density and high component count reflect the field's rapid expansion and cross-source identifier mismatches.}
\label{tab:citation_network}
\begin{tabular}{ll}
\toprule
\textbf{Metric} & \textbf{Value} \\
\midrule
Nodes & 1106 \\
Edges & 4,829 \\
Reference resolution rate & 10.4\% (4,829 / 46,598) \\
Connected components & 645 \\
Network density & 0.40\% \\
Mean in-degree & approximately 4.4 \\
\bottomrule
\end{tabular}
\end{table}


The citation topology corroborates the field overview findings (RQ1, RQ2): a small number of foundational papers—predominantly Friston's free energy and active inference formulations—anchor a rapidly expanding periphery of increasingly specialized work. The extremely low density (0.40\%) corresponds to an epistemic stage of high fragmentation, meaning that literature synthesis and cross-pollination between specific sub-domains remain difficult. Theoretical influence flows primarily through shared conceptual foundations (the hub nodes) rather than through dense mutual citation across the periphery. As metadata standardization improves and DOI adoption becomes universal across preprint and journal ecosystems, re-running this pipeline should yield substantially higher reference resolution rates and a more connected graph, enabling finer-grained community detection and tracking.
