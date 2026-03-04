# Hypothesis Evidence Landscape and Temporal Dynamics \label{sec:hypothesis_results}

<<<<<<< HEAD
The LLM-based extraction pipeline produced a total of 2{,}615 assertions across the eight tracked hypotheses, drawn from the full corpus of $N = 785$ papers. The distribution of assertion types and the resulting citation-weighted scores reveal a differentiated evidence landscape:
=======
The LLM-based extraction pipeline produced a total of 2{,}615 assertions across the eight tracked hypotheses, drawn from the full corpus of $N = 785$ papers. The distribution of assertion types and the resulting citation-weighted scores reveal a differentiated evidence landscape (Figure \ref{fig:hypothesis_dashboard}):
>>>>>>> 042a14f (refine: scholarly prose, fix stale data, remove unused refs)

| Hypothesis | Score | Supports | Neutral | Contradicts | Total | Character |
| --- | --- | --- | --- | --- | --- | --- |
| H4: Predictive Coding | $+0.91$ | 633 | 109 | 1 | 743 | Strong consensus |
| H5: Scalability | $+0.71$ | 117 | 85 | 0 | 202 | Strong consensus |
| H8: Language AIF | $+0.46$ | 37 | 65 | 0 | 102 | Moderate, growing |
| H6: Clinical Utility | $+0.43$ | 13 | 20 | 0 | 33 | Moderate, emerging |
| H7: Morphogenesis | $+0.41$ | 16 | 44 | 0 | 60 | Moderate, emerging |
| H1: FEP Universality | $+0.39$ | 238 | 508 | 1 | 747 | Broad but diffuse |
| H2: AIF Optimality | $+0.25$ | 133 | 442 | 14 | 589 | Weakly contested |
| H3: Markov Blanket Realism | $+0.23$ | 11 | 124 | 4 | 139 | Contested |

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/hypothesis_dashboard.png}
\caption{Hypothesis scoring dashboard showing LLM-extracted evidence scores for the eight tracked hypotheses, sorted descending by consensus. Scores range from $-1$ (strong contradicting evidence) to $+1$ (strong supporting evidence).}
\label{fig:hypothesis_dashboard}
\end{figure}

## Interpretation of Evidence Profiles

The eight hypotheses cluster into three distinct tiers. The **consensus tier** (H4, H5) comprises hypotheses with strong positive scores ($> 0.5$) and minimal contradicting assertions. Predictive coding (H4), the most extensively assessed hypothesis with 743 assertions and a score of $+0.91$, has accumulated overwhelmingly supportive evidence since the 1970s, reflecting the deep empirical grounding of hierarchical prediction error models in neuroscience. Scalability (H5) shows a similarly strong positive trajectory ($+0.71$) that accelerated after 2017 as deep active inference architectures emerged.

The **moderate tier** (H6, H7, H8) comprises hypotheses with positive scores in the $0.4$--$0.5$ range. Language AIF (H8) leads this tier with 102 assertions and a score of $+0.46$, reflecting recent breakthroughs coupling active inference to large language models. Clinical utility (H6) has the smallest evidence base (33 assertions) but shows a temporally increasing trend, consistent with the recent growth of computational psychiatry applications. Morphogenesis (H7) shows moderate support ($+0.41$), reflecting its status as an active research frontier where theoretical proposals outpace empirical validation.

The **diffuse or contested tier** (H1, H2, H3) is the most diagnostically informative for understanding the field's intellectual maturation. FEP universality (H1), despite generating one of the largest raw evidence bases (747 assertions), achieves a score of only $+0.39$—the majority of assessments are neutral, indicating that researchers frequently *invoke* the FEP without explicitly testing its universality claim. AIF optimality (H2) exhibits the largest volume of contradicting evidence (14 assertions), suggesting that as the field has transitioned from theory to empirical application, absolute optimality claims have undergone increasingly stringent critical scrutiny. Markov blanket realism (H3) has the smallest evidence base (139 assertions) with a score of $+0.23$ and four contradicting assertions—empirically capturing the ongoing philosophical debate over whether Markov blankets denote real thermodynamic boundaries or instrumental statistical constructs.

## Temporal Dynamics of Evidence Accumulation

The cumulative evidence timeline (Figure \ref{fig:evidence_timeline}) reveals three temporal patterns. First, **early convergence**: H4 (predictive coding) reached positive territory in the late 1970s and has maintained a stable, high score since, reflecting the mature empirical base in cognitive neuroscience. Second, **recent acceleration**: H5 (scalability) and H6 (clinical utility) show steep upward trends after 2017, tracking the emergence of deep active inference tools and computational psychiatry applications. Third, **persistent contestation**: H3 (Markov blanket realism) has maintained a lower score since 2018, with supporting papers partially offset by targeted critiques.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/evidence_timeline.png}
\caption{Temporal evolution of cumulative evidence scores by hypothesis. Divergent trajectories around the shaded neutral boundary reveal which hypotheses are gaining or losing support over time.}
\label{fig:evidence_timeline}
\end{figure}

## Assertion Composition and Distribution

The per-hypothesis composition of assertions (Figure \ref{fig:assertion_breakdown}) and the multi-panel summary (Figure \ref{fig:assertion_summary}) provide complementary views of the extraction results.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_breakdown.png}
\caption{Per-hypothesis stacked bar chart decomposing assertions into supports, contradicts, and neutral categories. The composition of evidence varies markedly across hypotheses.}
\label{fig:assertion_breakdown}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_summary.png}
\caption{Multi-panel assertion summary: total count, type distribution, and per-hypothesis totals. Provides a single-glance overview of the knowledge graph extraction results.}
\label{fig:assertion_summary}
\end{figure}

## Limitations of the Current Scoring Approach

As noted in Section 5, these results reflect a **tally-based aggregation** of independent LLM-extracted assertions, weighted by citation count and confidence. This approach does not account for evidential dependencies (e.g., papers from the same group testing the same model), does not distinguish between empirical and theoretical evidence, and treats the LLM's confidence scores as calibrated probabilities. The assertion counts are also sensitive to corpus composition: H1's large neutral tally (508) partially reflects the keyword classifier's tendency to assign papers to the broad A2 (philosophy) category, where FEP universality is implicitly invoked but rarely explicitly tested. More sophisticated approaches—including hierarchical Bayesian models, causal evidence graphs, and evidential diversity weighting—are discussed as future directions in Section 8.
