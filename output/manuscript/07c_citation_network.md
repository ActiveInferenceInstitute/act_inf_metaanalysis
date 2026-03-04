# Citation Network Topology \label{sec:citation_network}

The intra-corpus citation network provides a structural view of how Active Inference research is organized, identifying influential hub papers, community structure, and patterns of citation isolation (Figure \ref{fig:citation_network}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/citation_network.png}
\caption{Intra-corpus citation network ($N = 785$ nodes, 1{,}873 edges). Node size reflects PageRank and HITS centrality scores \citep{kleinberg1999authoritative}; highly cited foundational papers serve as nexus points connecting sub-domains.}
\label{fig:citation_network}
\end{figure}

## Network Density and Degree Distribution

<<<<<<< HEAD
The intra-corpus citation network contains 785 nodes and 1{,}873 edges, with a density of 0.30\% and 524 connected components. The average in-degree of $\approx 2.4$ indicates that most papers receive few intra-corpus citations, consistent with the field's rapid expansion: the majority of recent papers have not yet accumulated citations within the corpus. Only 6.6\% of all references (1{,}873 of 28{,}402) resolve to other papers within the corpus, reflecting cross-source identifier mismatches and the field's engagement with a broad external literature base. Community detection identifies clusters via the Louvain algorithm \citep{blondel2008louvain}.
=======
The intra-corpus citation network contains 785 nodes and 1{,}873 edges, with a density of 0.30\% and 524 connected components. The average in-degree of $\approx 2.4$ indicates that most papers receive few intra-corpus citations, consistent with the field's rapid expansion: the majority of recent papers have not yet accumulated citations within the corpus (Figure \ref{fig:degree_distribution}). Only 6.6\% of all references (1{,}873 of 28{,}402) resolve to other papers within the corpus, reflecting cross-source identifier mismatches and the field's engagement with a broad external literature base. Community detection identifies clusters via the Louvain algorithm \citep{blondel2008louvain}.
>>>>>>> 042a14f (refine: scholarly prose, fix stale data, remove unused refs)

\begin{figure}[htbp]
\centering
\includegraphics[width=0.7\textwidth]{figures/degree_distribution.png}
\caption{In-degree distribution of the citation network. The power-law tail is characteristic of citation networks, with a small number of highly cited hubs.}
\label{fig:degree_distribution}
\end{figure}

## Connected Components and Citation Isolation

The high number of connected components (524 out of 785 nodes) reveals that much of the corpus consists of citation-isolated papers—works that neither cite nor are cited by other papers in the collection. This is partially an artifact of cross-source identifier mismatches, but it also reflects the field's pattern of papers engaging with the FEP literature conceptually without building explicit citation chains. PageRank analysis identifies highly influential papers, predominantly Friston's foundational work \citep{friston2010free} and the AIF textbook \citep{parr2022active}, which serve as nexus points linking otherwise disconnected subgraphs.

## Network Summary

| Metric | Value |
| --- | --- |
| Nodes | 785 |
| Edges | 1{,}873 |
| Reference resolution rate | 6.6\% (1{,}873 / 28{,}402) |
| Connected components | 524 |
| Network density | 0.30\% |
| Mean in-degree | $\approx$ 2.4 |

The citation topology corroborates the field overview findings (RQ1, RQ2): a small number of foundational papers—predominantly Friston's free energy and active inference formulations—anchor a rapidly expanding periphery of increasingly specialized work. The high component count and low density reflect a field in which theoretical influence flows primarily through shared conceptual foundations rather than through dense mutual citation. As metadata standardization improves and DOI adoption becomes universal across preprint and journal ecosystems, re-running this pipeline should yield substantially higher reference resolution rates and a more connected graph, enabling finer-grained community detection and influence tracking.
