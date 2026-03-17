# Hypothesis Evidence Landscape and Temporal Dynamics \label{sec:hypothesis_results}

The LLM-based extraction pipeline produced a total of {{TOTAL_ASSERTIONS}} assertions across the eight tracked hypotheses, drawn from the full corpus of $N = {{CORPUS_SIZE}}$ papers. The distribution of assertion types and the resulting citation-weighted scores reveal a differentiated evidence landscape (Figure \ref{fig:hypothesis_dashboard}):

| Hypothesis | Score | Supports | Neutral | Contradicts | Total | Character |
| --- | --- | --- | --- | --- | --- | --- |
| H4: Predictive Coding | ${{H4_SCORE}}$ | {{H4_SUPPORT}} | {{H4_NEUTRAL}} | {{H4_CONTRADICT}} | {{H4_TOTAL}} | Strong consensus |
| H5: Scalability | ${{H5_SCORE}}$ | {{H5_SUPPORT}} | {{H5_NEUTRAL}} | {{H5_CONTRADICT}} | {{H5_TOTAL}} | Strong consensus |
| H8: Language AIF | ${{H8_SCORE}}$ | {{H8_SUPPORT}} | {{H8_NEUTRAL}} | {{H8_CONTRADICT}} | {{H8_TOTAL}} | Moderate, growing |
| H6: Clinical Utility | ${{H6_SCORE}}$ | {{H6_SUPPORT}} | {{H6_NEUTRAL}} | {{H6_CONTRADICT}} | {{H6_TOTAL}} | Moderate, emerging |
| H7: Morphogenesis | ${{H7_SCORE}}$ | {{H7_SUPPORT}} | {{H7_NEUTRAL}} | {{H7_CONTRADICT}} | {{H7_TOTAL}} | Moderate, emerging |
| H1: FEP Universality | ${{H1_SCORE}}$ | {{H1_SUPPORT}} | {{H1_NEUTRAL}} | {{H1_CONTRADICT}} | {{H1_TOTAL}} | Broad but diffuse |
| H2: AIF Optimality | ${{H2_SCORE}}$ | {{H2_SUPPORT}} | {{H2_NEUTRAL}} | {{H2_CONTRADICT}} | {{H2_TOTAL}} | Weakly contested |
| H3: Markov Blanket Realism | ${{H3_SCORE}}$ | {{H3_SUPPORT}} | {{H3_NEUTRAL}} | {{H3_CONTRADICT}} | {{H3_TOTAL}} | Contested |

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/hypothesis_dashboard.png}
\caption{Hypothesis scoring dashboard showing citation-weighted evidence scores ($[-1, +1]$) for the eight tracked hypotheses, sorted descending by consensus strength. Predominantly positive scores reflect both genuine empirical support and systematic positive biases from publication selection and linguistic framing (see \S\ref{sec:pub_bias}).}
\label{fig:hypothesis_dashboard}
\end{figure}

## Interpretation of Evidence Profiles

The eight hypotheses cluster into three distinct tiers. The **consensus tier** (H4, H5) comprises hypotheses with strong positive scores ($> 0.5$) and minimal contradicting assertions. Predictive coding (H4), the most extensively assessed hypothesis with {{H4_TOTAL}} assertions and a score of ${{H4_SCORE}}$, has accumulated overwhelmingly supportive evidence since the 1970s, reflecting the deep empirical grounding of hierarchical prediction error models in neuroscience. Scalability (H5) shows a similarly strong positive trajectory (${{H5_SCORE}}$) that accelerated after 2017 as deep active inference architectures emerged.

The **moderate tier** (H6, H7, H8) comprises hypotheses with positive scores in the $0.4$--$0.5$ range. Language AIF (H8) leads this tier with {{H8_TOTAL}} assertions and a score of ${{H8_SCORE}}$, reflecting recent breakthroughs coupling active inference to large language models. Clinical utility (H6) has the smallest evidence base ({{H6_TOTAL}} assertions) but shows a temporally increasing trend, consistent with the recent growth of computational psychiatry applications. Morphogenesis (H7) shows moderate support (${{H7_SCORE}}$), reflecting its status as an active research frontier where theoretical proposals outpace empirical validation.

The **diffuse or contested tier** (H1, H2, H3) is the most diagnostically informative for understanding the field's intellectual maturation. FEP universality (H1), despite generating one of the largest raw evidence bases ({{H1_TOTAL}} assertions), achieves a score of only ${{H1_SCORE}}$—the majority of assessments are neutral, indicating that researchers frequently *invoke* the FEP without explicitly testing its universality claim. This finding dovetails with the falsifiability critique leveled by Colombo and Seri\`es \citep{colombo2021free}: if the FEP can be applied to any self-organizing system without generating testable predictions that distinguish it from alternative frameworks, neutral citations (invocations rather than tests) are exactly what one would expect to dominate the literature. AIF optimality (H2) exhibits the largest volume of contradicting evidence ({{H2_CONTRADICT}} assertions), suggesting that as the field has transitioned from theory to empirical application, absolute optimality claims have undergone increasingly stringent critical scrutiny. Markov blanket realism (H3) has the smallest evidence base ({{H3_TOTAL}} assertions) with a score of ${{H3_SCORE}}$ and {{H3_CONTRADICT}} contradicting assertions—empirically capturing the ongoing philosophical debate between those who treat Markov blankets as real thermodynamic boundaries (\"Friston blankets\") and those who argue they are purely instrumental statistical tools (\"Pearl blankets\") \citep{bruineberg2022emperor}. The contested score for H3 directly reflects this unresolved ontological tension in the field.

## Temporal Dynamics of Evidence Accumulation

The cumulative evidence timeline (Figure \ref{fig:evidence_timeline}) reveals three temporal patterns. First, **early convergence**: H4 (predictive coding) reached positive territory in the late 1990s following the publication of Rao and Ballard's foundational predictive coding model \citep{rao1999predictive} and has maintained a high score since, reflecting the mature empirical base in cognitive neuroscience. Second, **recent acceleration**: H5 (scalability) and H6 (clinical utility) show steep upward trends after 2017, tracking the emergence of deep active inference tools and computational psychiatry applications. The H5 trajectory is particularly striking: AXIOM \citep{heins2025axiom} demonstrates that principled object-centric world models under the AIF framework can outperform state-of-the-art deep RL agents on standard benchmarks, directly addressing the scalability challenge that has historically been the strongest argument against AIF as a practical framework. Third, **persistent contestation**: H3 (Markov blanket realism) has maintained a lower score since 2018, with supporting papers partially offset by targeted critiques.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/evidence_timeline.png}
\caption{Temporal evolution of cumulative citation-weighted evidence scores by hypothesis ({{YEAR_START}}--{{YEAR_END}}). Divergent trajectories around the shaded neutral boundary $(\pm 0.1)$ reveal which hypotheses are gaining or losing support over time. H4 (predictive coding) stabilized early; H5 (scalability) accelerated post-2017.}
\label{fig:evidence_timeline}
\end{figure}

## Assertion Composition and Distribution

The per-hypothesis composition of assertions (Figure \ref{fig:assertion_breakdown}) and the multi-panel summary (Figure \ref{fig:assertion_summary}) provide complementary views of the extraction results.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_breakdown.png}
\caption{Stacked horizontal bars decomposing per-hypothesis assertions into supports (green), contradicts (red-orange), and neutral (blue) categories ($N = {{TOTAL_ASSERTIONS}}$ total assertions). Labels show total count and support percentage. The high support fractions are partially attributable to publication bias and affirmative linguistic framing.}
\label{fig:assertion_breakdown}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_summary.png}
\caption{Multi-panel assertion summary: (left) pie chart of overall assertion type distribution showing supports/contradicts/neutral proportions, (right) per-hypothesis assertion counts with palette-coded bars. $N = {{TOTAL_ASSERTIONS}}$ assertions extracted from ${{CORPUS_SIZE}}$ papers.}
\label{fig:assertion_summary}
\end{figure}

## Limitations of the Current Scoring Approach

As noted in the \hyperref[sec:methods_kg]{methodology}, these results reflect a **tally-based aggregation** of independent LLM-extracted assertions, weighted by citation count and confidence. This approach does not account for evidential dependencies (e.g., papers from the same group testing the same model), does not distinguish between empirical and theoretical evidence, and treats the LLM's confidence scores as calibrated probabilities. The assertion counts are also sensitive to corpus composition: H1's large neutral tally ({{H1_NEUTRAL}}) partially reflects the keyword classifier's tendency to assign papers to the broad A2 (philosophy) category, where FEP universality is implicitly invoked but rarely explicitly tested. The dominant-neutral pattern for H1 is also consistent with the falsifiability critique \citep{colombo2021free}: a principle elastic enough to accommodate any behavior without refutation will naturally accrue neutral rather than positive or negative assessments. More sophisticated approaches—including hierarchical Bayesian models, causal evidence graphs, and evidential diversity weighting—are discussed as future directions in the \hyperref[sec:conclusion]{conclusion}.

### Publication Bias and Linguistic Asymmetry \label{sec:pub_bias}

The predominantly positive scores observed across all eight hypotheses should be interpreted with two systematic caveats.

First, **publication bias** systematically inflates supporting evidence. Academic journals preferentially publish positive and confirmatory results (\citealt{sterling1959publication}), meaning that studies finding null or contradictory outcomes for any hypothesis are less likely to appear in the retrievable literature. This \textit{file-drawer effect} is well-documented across scientific disciplines and is expected to disproportionately suppress contradicting assertions in our extraction pipeline. The Active Inference literature is particularly susceptible: as a theoretical framework with strong foundational proponents, papers are more likely to frame results as consistent with the FEP than as challenges to it.

Second, **linguistic asymmetry** in academic writing further skews extraction toward positive classifications. Declarative scholarly claims are inherently phrased affirmatively—authors write ``our results support,'' ``consistent with,'' or ``extends the prediction of'' far more frequently than ``our results refute'' or ``contradicts the claim that.'' Because the LLM extraction pipeline operates on abstract text, this linguistic imbalance propagates directly into the assertion distribution. Even papers presenting genuinely mixed evidence tend to frame their abstracts in terms of what \textit{was} found rather than what was not, biasing the extracted direction toward ``supports.''

These two effects act in concert: publication bias reduces the number of contradicting papers in the corpus, and linguistic framing reduces the number of contradicting assertions extracted from the papers that do appear. Consequently, the absolute values of hypothesis scores should not be taken as unbiased measures of scientific consensus. The \textit{relative} ordering and temporal \textit{trajectories} of hypothesis scores are more robust indicators, as these biases affect all hypotheses approximately equally.
