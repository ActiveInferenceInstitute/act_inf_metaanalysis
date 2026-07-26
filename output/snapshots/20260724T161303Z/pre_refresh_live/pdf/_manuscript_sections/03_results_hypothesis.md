# Results \label{sec:results}

## Hypothesis Evidence Landscape and Temporal Dynamics \label{sec:hypothesis_results}

The LLM-based extraction pipeline produced a total of 1,671 assertions across the eight tracked hypotheses, drawn from the full corpus of $N = 817$ papers. Before presenting the results, we reiterate the interpretive framework established in the \hyperref[sec:methods_kg]{methodology}: hypothesis scores are *relative rankings* among hypotheses and *temporal trajectories* within each hypothesis—they are not absolute probability estimates. Publication bias and linguistic asymmetry (\S\ref{sec:pub_bias}) inflate all scores toward the positive end, and the tally-based aggregation does not model evidential dependencies. The distribution of assertion types and the resulting citation-weighted scores reveal a differentiated evidence landscape (Figure \ref{fig:hypothesis_dashboard}):


\begin{table}[htbp]
\centering
\caption{Citation-weighted hypothesis evidence landscape ($N = 817$ papers, 1,671 total assertions). Scores are computed via \eqref{eq:score} and range from $-1$ (unanimous contradiction) to $+1$ (unanimous support). ``Character'' summarizes the qualitative evidence profile for each hypothesis.}
\label{tab:hypothesis_evidence}
\begin{tabular}{lcccccc}
\toprule
\textbf{Hypothesis} & \textbf{Score} & \textbf{Supports} & \textbf{Neutral} & \textbf{Contradicts} & \textbf{Total} & \textbf{Character} \\
\midrule
H7: Morphogenesis & $+0.55$ & 17 & 2 & 4 & 23 & Strong consensus \\
H2: AIF Optimality & $+0.68$ & 351 & 44 & 32 & 427 & Strong consensus \\
H4: Predictive Coding & $+0.91$ & 132 & 14 & 2 & 148 & Strong consensus \\
H6: Clinical Utility & $+0.84$ & 29 & 7 & 2 & 38 & Strong consensus \\
H5: Scalability & $+0.73$ & 99 & 8 & 2 & 109 & Strong consensus \\
H8: Language AIF & $+0.81$ & 28 & 2 & 2 & 32 & Strong support \\
H3: Markov Blanket Realism & $-0.82$ & 5 & 8 & 108 & 121 & Moderate, active debate \\
H1: FEP Universality & $+0.13$ & 67 & 703 & 3 & 773 & Broad but diffuse \\
\bottomrule
\end{tabular}
\end{table}


\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/hypothesis_dashboard.png}
\caption{Hypothesis scoring dashboard showing citation-weighted evidence scores ($[-1, +1]$) for the eight tracked hypotheses, sorted descending by consensus strength. Predominantly positive scores reflect both genuine empirical support and systematic positive biases from publication selection and linguistic framing (see \S\ref{sec:pub_bias}).}
\label{fig:hypothesis_dashboard}
\end{figure}

### Interpretation of Evidence Profiles

To directly address our core research questions—identifying which claims are robustly supported and which remain contested—we evaluated how the hypothesis-level evidence maps against the critiques introduced in \S\ref{sec:methods}. The eight hypotheses cluster into three tiers, defined by score ranges that emerge from the data rather than being imposed a priori. The **consensus tier** (score $> 0.83$; H7, H2, H4, H6, H5) spans five of the eight hypotheses, revealing a predominantly supportive evidence landscape across domains. H8 (Language AIF) sits at the **boundary of consensus** at score $+0.81$ — above 0.8 but below the more stringent 0.83 line that separates the densely populated upper tier from the rest. Morphogenesis (H7) achieves the maximum score ($+0.55$), though its small evidence base (23 assertions) means unanimity reflects limited assessment scope rather than mature empirical closure. AIF Optimality (H2) holds the second highest score ($+0.68$) despite carrying the largest raw count of contradicting assertions (32): supporting assertions are substantially more highly cited than critical ones, so citation-weighting amplifies the supportive signal—underscoring that citation-weighted scores capture \textit{which} claims the community cites most, not a simple ballot of assertion counts. Predictive coding (H4), the most extensively assessed hypothesis with 148 assertions and a score of $+0.91$, has accumulated overwhelmingly supportive evidence since the 1970s, reflecting the deep empirical grounding of hierarchical prediction error models in neuroscience. This trajectory is consistent with the manual benchmarking results of Knight et al. \citep{knight2022fep}, which similarly identified predictive coding as the most rigorously validated construct in the corpus. Clinical Utility (H6, $+0.84$) and Scalability (H5, $+0.73$) complete the upper consensus tier; H5's trajectory accelerated sharply after 2017 as deep active inference architectures emerged. The H8 (Language AIF) boundary placement noted above reflects recent breakthroughs coupling active inference to large language models within a still-maturing evidence base.

The **moderate tier** (score $0.5$--$0.8$; H3) contains a single hypothesis. Markov blanket realism (H3) has the smallest overall evidence base (121 assertions) with a score of $-0.82$ and 108 contradicting assertions—empirically capturing the ongoing philosophical debate between those who treat Markov blankets as real thermodynamic boundaries (``Friston blankets'') and those who argue they are purely instrumental statistical tools (``Pearl blankets'') \citep{bruineberg2022emperor}. The moderate score for H3 reflects this active ontological debate: the supporting literature is more highly cited but not by a large margin, and the small total evidence base limits inferential confidence.

The **diffuse tier** (score $< 0.5$; H1) is the most diagnostically informative for understanding the field's intellectual maturation. FEP universality (H1) generates one of the largest raw evidence bases (773 assertions) yet achieves a score of only $+0.13$—a striking gap explained by assertion composition: neutral assessments account for 703 of those 773 tallies, while supporting assertions number 67 and contradicting assertions just 3. This neutral plurality—more than either supporting or contradicting tallies—reveals that researchers routinely \textit{invoke} the FEP as conceptual scaffolding without subjecting its universality claim to explicit empirical test. This composition is the quantitative fingerprint of the falsifiability critique leveled by Colombo and Seri\`es \citep{colombo2021free}: a principle elastic enough to accommodate any self-organizing system without generating predictions that distinguish it from alternatives will naturally accumulate invocations rather than tests, and invocations register as neutral in the extraction pipeline.

### Temporal Dynamics of Evidence Accumulation

The cumulative evidence timeline (Figure \ref{fig:evidence_timeline}) reveals three temporal patterns. First, **early convergence**: H4 (predictive coding) reached positive territory in the late 1990s following the publication of Rao and Ballard's foundational predictive coding model \citep{rao1999predictive} and has maintained a high score since, reflecting the mature empirical base in cognitive neuroscience. Second, **recent acceleration**: H5 (scalability) and H6 (clinical utility) show steep upward trends after 2017, tracking the emergence of deep active inference tools and computational psychiatry applications. The H5 trajectory reflects a cumulative body of work culminating in benchmark demonstrations such as AXIOM \citep{heins2025axiom}, which showed that object-centric world models under AIF can match state-of-the-art deep RL performance—but the temporal trend was already positive before any single result, and the score captures the aggregate rather than any individual paper. Third, **moderate and stable**: H3 (Markov blanket realism) has maintained a score in the moderate range since 2018, with supporting papers partially offset by targeted philosophical critiques—a pattern consistent with ongoing debate rather than either clear consensus or rejection.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/evidence_timeline.png}
\caption{Temporal evolution of cumulative citation-weighted evidence scores by hypothesis (2005--2026). Divergent trajectories around the shaded neutral boundary $(\pm 0.1)$ reveal which hypotheses are gaining or losing support over time. H4 (predictive coding) stabilized early; H5 (scalability) accelerated post-2017.}
\label{fig:evidence_timeline}
\end{figure}

### Assertion Composition and Distribution

The per-hypothesis composition of assertions (Figure \ref{fig:assertion_breakdown}) and the multi-panel summary (Figure \ref{fig:assertion_summary}) provide complementary views of the extraction results.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_breakdown.png}
\caption{Stacked horizontal bars decomposing per-hypothesis assertions into supports (green), contradicts (red-orange), and neutral (blue) categories ($N = 1,671$ total assertions). Labels show total count and support percentage. The high support fractions are partially attributable to publication bias and affirmative linguistic framing.}
\label{fig:assertion_breakdown}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/assertion_summary.png}
\caption{Multi-panel assertion summary: (left) pie chart of overall assertion type distribution showing supports/contradicts/neutral proportions, (right) per-hypothesis assertion counts with palette-coded bars. $N = 1,671$ assertions extracted from $817$ papers.}
\label{fig:assertion_summary}
\end{figure}

### Limitations of the Current Scoring Approach


#### Publication Bias and Linguistic Asymmetry \label{sec:pub_bias}

The predominantly positive scores observed across all eight hypotheses should be interpreted with two systematic caveats.

First, **publication bias** systematically inflates supporting evidence. Academic journals preferentially publish positive and confirmatory results (\citealt{sterling1959publication}), meaning that studies finding null or contradictory outcomes for any hypothesis are less likely to appear in the retrievable literature. This \textit{file-drawer effect} is well-documented across scientific disciplines and is expected to disproportionately suppress contradicting assertions in our extraction pipeline. The Active Inference literature is particularly susceptible: as a theoretical framework with strong foundational proponents, papers are more likely to frame results as consistent with the FEP than as challenges to it.

Second, **linguistic asymmetry** in academic writing further skews extraction toward positive classifications. Declarative scholarly claims are inherently phrased affirmatively—authors write "our results support," "consistent with," or "extends the prediction of" far more frequently than "our results refute" or "contradicts the claim that." Because the LLM extraction pipeline operates on abstract text, this linguistic imbalance propagates directly into the assertion distribution. Even papers presenting genuinely mixed evidence tend to frame their abstracts in terms of what \textit{was} found rather than what was not, biasing the extracted direction toward ``supports.''

These two effects act in concert: publication bias reduces the number of contradicting papers in the corpus, and linguistic framing reduces the number of contradicting assertions extracted from the papers that do appear. Consequently, the absolute values of hypothesis scores should not be taken as unbiased measures of scientific consensus. The \textit{relative} ordering and temporal \textit{trajectories} of hypothesis scores are more robust indicators, as these biases affect all hypotheses approximately equally.

### Methodological Validation and LLM Calibration

The evidence derives from automated LLM-based assertion extraction operating on abstracts only. A stratified rule-based reference-annotator agreement study ($n = 200$) provides a first quantitative, fully reproducible calibration: two deterministic keyword-rule protocols agree at $\kappa = 0.554$ (reference stability), while pipeline triage against the primary rule reference yields precision 0.000, recall 0.000, and F1 0.000, with reference--pipeline direction agreement of only $\kappa = -0.055$. That the LLM and an independent keyword reference diverge this sharply is itself the calibration result: over-extraction (pipeline labels relevant where the keyword reference labels irrelevant) accounts for 0.765 of sampled rows, directly motivating the tempered interpretation of absolute hypothesis scores. Relative rankings and temporal trajectories remain more robust than point estimates. These figures are a reproducibility floor, not accuracy against human ground truth, which remains future work. Full metrics and error taxonomy appear in Table~\ref{tab:validation_metrics} (\S\ref{sec:extraction_pipeline}).

### Citation-Weighting Sensitivity

Hypothesis ranks under six alternative weight policies remain stable: minimum rank-stability Spearman $\rho = 0.762$ versus the default log-citation policy, with 18 rank inversions across all policies. No hypothesis changes sign under any tested policy; the largest score shifts occur under raw-citation weighting (popularity stress test) for H5 (Scalability) and H8 (Language AIF), reflecting Matthew-effect sensitivity without altering qualitative tier ordering.
