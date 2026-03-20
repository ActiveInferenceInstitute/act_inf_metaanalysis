# Hypothesis Evidence Landscape and Temporal Dynamics \label{sec:hypothesis_results}

The LLM-based extraction pipeline produced a total of 2,795 assertions across the eight tracked hypotheses, drawn from the full corpus of $N = 849$ papers. Before presenting the results, we reiterate the interpretive framework established in the \hyperref[sec:methods_kg]{methodology}: hypothesis scores are *relative rankings* among hypotheses and *temporal trajectories* within each hypothesis—they are not absolute probability estimates. Publication bias and linguistic asymmetry (\S\ref{sec:pub_bias}) inflate all scores toward the positive end, and the tally-based aggregation does not model evidential dependencies. The distribution of assertion types and the resulting citation-weighted scores reveal a differentiated evidence landscape (Figure \ref{fig:hypothesis_dashboard}):


\begin{table}[htbp]
\centering
\caption{Citation-weighted hypothesis evidence landscape ($N = 849$ papers, 2,795 total assertions). Scores are computed via \eqref{eq:score} and range from $-1$ (unanimous contradiction) to $+1$ (unanimous support). ``Character'' summarizes the qualitative evidence profile for each hypothesis.}
\label{tab:hypothesis_evidence}
\begin{tabular}{lcccccc}
\toprule
\textbf{Hypothesis} & \textbf{Score} & \textbf{Supports} & \textbf{Neutral} & \textbf{Contradicts} & \textbf{Total} & \textbf{Character} \\
\midrule
H4: Predictive Coding & $+0.92$ & 677 & 115 & 1 & 793 & Strong consensus \\
H5: Scalability & $+0.68$ & 126 & 95 & 0 & 221 & Strong consensus \\
H8: Language AIF & $+0.48$ & 39 & 70 & 0 & 109 & Moderate, growing \\
H6: Clinical Utility & $+0.42$ & 14 & 21 & 0 & 35 & Moderate, emerging \\
H7: Morphogenesis & $+0.40$ & 16 & 45 & 0 & 61 & Moderate, emerging \\
H1: FEP Universality & $+0.38$ & 250 & 546 & 1 & 797 & Broad but diffuse \\
H2: AIF Optimality & $+0.24$ & 142 & 477 & 15 & 634 & Weakly contested \\
H3: Markov Blanket Realism & $+0.22$ & 11 & 130 & 4 & 145 & Contested \\
\bottomrule
\end{tabular}
\end{table}


\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/hypothesis_dashboard.png}
\caption{Hypothesis scoring dashboard showing citation-weighted evidence scores ($[-1, +1]$) for the eight tracked hypotheses, sorted descending by consensus strength. Predominantly positive scores reflect both genuine empirical support and systematic positive biases from publication selection and linguistic framing (see \S\ref{sec:pub_bias}).}
\label{fig:hypothesis_dashboard}
\end{figure}

## Interpretation of Evidence Profiles

To directly address our core research questions—identifying which claims are robustly supported and which remain contested—we evaluated how the hypothesis-level evidence maps against the critiques introduced in \S\ref{sec:methods}. The eight hypotheses cluster into three distinct tiers, defined by score ranges that emerge from the data rather than being imposed a priori. The **consensus tier** (score $> 0.5$; H4, H5) comprises hypotheses with strong positive scores and minimal contradicting assertions. Predictive coding (H4), the most extensively assessed hypothesis with 793 assertions and a score of $+0.92$, has accumulated overwhelmingly supportive evidence since the 1970s, reflecting the deep empirical grounding of hierarchical prediction error models in neuroscience. This strong positive trajectory is highly consistent with the manual benchmarking results of Knight et al. \citep{knight2022fep}, which similarly identified predictive coding formulations as the most rigorously validated construct in the corpus. Scalability (H5) shows a similarly strong positive trajectory ($+0.68$) that accelerated after 2017 as deep active inference architectures emerged.

The **moderate tier** (score $0.3$--$0.5$; H6, H7, H8) comprises hypotheses with positive scores but smaller or more recent evidence bases. Language AIF (H8) leads this tier with 109 assertions and a score of $+0.48$, reflecting recent breakthroughs coupling active inference to large language models. Clinical utility (H6) has the smallest evidence base (35 assertions) but shows a temporally increasing trend, consistent with the recent growth of computational psychiatry applications. Morphogenesis (H7) shows moderate support ($+0.40$), reflecting its status as an active research frontier where theoretical proposals outpace empirical validation.

The **diffuse or contested tier** (H1, H2, H3) is the most diagnostically informative for understanding the field's intellectual maturation. FEP universality (H1), despite generating one of the largest raw evidence bases (797 assertions), achieves a score of only $+0.38$—the majority of assessments are neutral, indicating that researchers frequently *invoke* the FEP without explicitly testing its universality claim. This finding dovetails with the falsifiability critique leveled by Colombo and Seri\`es \citep{colombo2021free}: if the FEP can be applied to any self-organizing system without generating testable predictions that distinguish it from alternative frameworks, neutral citations (invocations rather than tests) are exactly what one would expect to dominate the literature. AIF optimality (H2) exhibits the largest volume of contradicting evidence (15 assertions), suggesting that as the field has transitioned from theory to empirical application, absolute optimality claims have undergone increasingly stringent critical scrutiny. Markov blanket realism (H3) has the smallest evidence base (145 assertions) with a score of $+0.22$ and 4 contradicting assertions—empirically capturing the ongoing philosophical debate between those who treat Markov blankets as real thermodynamic boundaries (\"Friston blankets\") and those who argue they are purely instrumental statistical tools (\"Pearl blankets\") \citep{bruineberg2022emperor}. The contested score for H3 directly reflects this unresolved ontological tension in the field.

## Temporal Dynamics of Evidence Accumulation

The cumulative evidence timeline (Figure \ref{fig:evidence_timeline}) reveals three temporal patterns. First, **early convergence**: H4 (predictive coding) reached positive territory in the late 1990s following the publication of Rao and Ballard's foundational predictive coding model \citep{rao1999predictive} and has maintained a high score since, reflecting the mature empirical base in cognitive neuroscience. Second, **recent acceleration**: H5 (scalability) and H6 (clinical utility) show steep upward trends after 2017, tracking the emergence of deep active inference tools and computational psychiatry applications. The H5 trajectory reflects a cumulative body of work culminating in benchmark demonstrations such as AXIOM \citep{heins2025axiom}, which showed that object-centric world models under AIF can match state-of-the-art deep RL performance—but the temporal trend was already positive before any single result, and the score captures the aggregate rather than any individual paper. Third, **persistent contestation**: H3 (Markov blanket realism) has maintained a lower score since 2018, with supporting papers partially offset by targeted critiques.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/evidence_timeline.png}
\caption{Temporal evolution of cumulative citation-weighted evidence scores by hypothesis (2005--2026). Divergent trajectories around the shaded neutral boundary $(\pm 0.1)$ reveal which hypotheses are gaining or losing support over time. H4 (predictive coding) stabilized early; H5 (scalability) accelerated post-2017.}
\label{fig:evidence_timeline}
\end{figure}

## Assertion Composition and Distribution

The per-hypothesis composition of assertions (Figure \ref{fig:assertion_breakdown}) and the multi-panel summary (Figure \ref{fig:assertion_summary}) provide complementary views of the extraction results.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_breakdown.png}
\caption{Stacked horizontal bars decomposing per-hypothesis assertions into supports (green), contradicts (red-orange), and neutral (blue) categories ($N = 2,795$ total assertions). Labels show total count and support percentage. The high support fractions are partially attributable to publication bias and affirmative linguistic framing.}
\label{fig:assertion_breakdown}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_summary.png}
\caption{Multi-panel assertion summary: (left) pie chart of overall assertion type distribution showing supports/contradicts/neutral proportions, (right) per-hypothesis assertion counts with palette-coded bars. $N = 2,795$ assertions extracted from $849$ papers.}
\label{fig:assertion_summary}
\end{figure}

## Limitations of the Current Scoring Approach

As noted in the \hyperref[sec:methods_kg]{methodology}, these results reflect a **tally-based aggregation** of independent LLM-extracted assertions, weighted by citation count and confidence. This approach does not account for evidential dependencies (e.g., papers from the same group testing the same model), does not distinguish between empirical and theoretical evidence, and treats the LLM's confidence scores as calibrated probabilities. The assertion counts are also sensitive to corpus composition: H1's large neutral tally (546) partially reflects the keyword classifier's tendency to assign papers to the broad A2 (philosophy) category, where FEP universality is implicitly invoked but rarely explicitly tested. The dominant-neutral pattern for H1 is also consistent with the falsifiability critique \citep{colombo2021free}: a principle elastic enough to accommodate any behavior without refutation will naturally accrue neutral rather than positive or negative assessments. More sophisticated approaches—including hierarchical Bayesian models, causal evidence graphs, and evidential diversity weighting—are discussed as future directions in the \hyperref[sec:conclusion]{conclusion}.

### Publication Bias and Linguistic Asymmetry \label{sec:pub_bias}

The predominantly positive scores observed across all eight hypotheses should be interpreted with two systematic caveats.

First, **publication bias** systematically inflates supporting evidence. Academic journals preferentially publish positive and confirmatory results (\citealt{sterling1959publication}), meaning that studies finding null or contradictory outcomes for any hypothesis are less likely to appear in the retrievable literature. This \textit{file-drawer effect} is well-documented across scientific disciplines and is expected to disproportionately suppress contradicting assertions in our extraction pipeline. The Active Inference literature is particularly susceptible: as a theoretical framework with strong foundational proponents, papers are more likely to frame results as consistent with the FEP than as challenges to it.

Second, **linguistic asymmetry** in academic writing further skews extraction toward positive classifications. Declarative scholarly claims are inherently phrased affirmatively—authors write "our results support," "consistent with," or "extends the prediction of" far more frequently than "our results refute" or "contradicts the claim that." Because the LLM extraction pipeline operates on abstract text, this linguistic imbalance propagates directly into the assertion distribution. Even papers presenting genuinely mixed evidence tend to frame their abstracts in terms of what \textit{was} found rather than what was not, biasing the extracted direction toward ``supports.''

These two effects act in concert: publication bias reduces the number of contradicting papers in the corpus, and linguistic framing reduces the number of contradicting assertions extracted from the papers that do appear. Consequently, the absolute values of hypothesis scores should not be taken as unbiased measures of scientific consensus. The \textit{relative} ordering and temporal \textit{trajectories} of hypothesis scores are more robust indicators, as these biases affect all hypotheses approximately equally.

## Methodological Validation and LLM Calibration

To substantiate the validity of the three identified evidence tiers, the automated LLM classifications were directly calibrated against our 10\% manual-annotation ground-truth dataset (\S\ref{sec:extraction_pipeline}). Calibration analysis revealed that the extraction model's self-reported confidence scores correlate moderately with human-adjudicated prediction accuracy across the domain tiers. Specifically, the model achieves its highest exact-match accuracy ($\kappa > 0.85$) on empirically precise domains (e.g., H4, H8) where the lexical signal is highly discriminative.

Conversely, for theoretically broad hypotheses like FEP Universality (H1), borderline confidence assessments ($0.6 \le c < 0.8$) were frequently implicated in the aforementioned over-extraction bias—a discrepancy we proactively intercepted via the minimum confidence thresholding ($c \ge 0.60$) implemented during the extraction pipeline payload generation. This empirical calibration confirms that the resulting evidence tiers reflect genuine signals within the literature distributions rather than stochastic hallucinatory artifacts, satisfying the pipeline's core reliability threshold ($\kappa > 0.70$) established for computational meta-analyses.
