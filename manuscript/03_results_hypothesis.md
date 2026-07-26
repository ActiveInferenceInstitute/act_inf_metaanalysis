# Results {#sec:results}

## Hypothesis Evidence Landscape and Temporal Dynamics {#sec:hypothesis_results}

The LLM-based extraction pipeline produced a total of {{TOTAL_ASSERTIONS}} assertions across the eight tracked hypotheses, drawn from the retrieved corpus snapshot of $N = {{CORPUS_SIZE}}$ papers. Before presenting the results, we reiterate the interpretive framework established in the \hyperref[sec:methods_kg]{methodology}: hypothesis scores are descriptive comparisons among hypotheses and cumulative trajectories within each hypothesis—they are not absolute probability estimates or validated measures of scientific support. Publication bias and linguistic asymmetry (\S\ref{sec:pub_bias}) inflate all scores toward the positive end, and the tally-based aggregation does not model evidential dependencies. The distribution of assertion types and the resulting citation-weighted scores reveal a differentiated evidence landscape (Figure \ref{fig:hypothesis_dashboard}):


\begin{table}[htbp]
\centering
\caption{Citation-weighted hypothesis evidence landscape ($N = {{CORPUS_SIZE}}$ papers, {{TOTAL_ASSERTIONS}} total assertions). Scores are computed via \eqref{eq:score} and range from $-1$ (unanimous contradiction) to $+1$ (unanimous support). ``Character'' summarizes the qualitative evidence profile for each hypothesis.}
\label{tab:hypothesis_evidence}
\begin{tabular}{lcccccc}
\toprule
\textbf{Hypothesis} & \textbf{Score} & \textbf{Supports} & \textbf{Neutral} & \textbf{Contradicts} & \textbf{Total} & \textbf{Character} \\
\midrule
{{HYPOTHESIS_TABLE_ROWS}}
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

To directly address our core research questions—identifying which claims are robustly supported and which remain contested—we evaluated how the hypothesis-level evidence maps against the critiques introduced in \S\ref{sec:methods}. The score ordering is data-derived and should be read as a relative evidence map, not as a set of absolute scientific-certainty tiers. The highest observed score is {{TOP_HYPOTHESIS_NAME}} ({{TOP_HYPOTHESIS_ID}}) at ${{TOP_HYPOTHESIS_SCORE}}$, while {{POSITIVE_HYPOTHESIS_COUNT}} hypotheses have positive scores and {{NEGATIVE_HYPOTHESIS_COUNT}} have negative scores in this snapshot. FEP Universality (H1), with {{H1_TOTAL}} assertions, has the largest assessed evidence base; assertion volume and score magnitude answer different questions. Across hypotheses, citation-weighting captures which claims the community cites most rather than providing a simple ballot of assertion counts; this can amplify highly cited supportive or critical evidence. The complete score and count table is the authoritative comparison, while the dashboard and timeline provide visual summaries.

Markov blanket realism (H3) has {{H3_TOTAL}} assertions, a score of ${{H3_SCORE}}$, and {{H3_CONTRADICT}} contradicting assertions. Its relatively low positive score is consistent with an active ontological debate between accounts that treat Markov blankets as real thermodynamic boundaries and accounts that treat them as instrumental statistical tools \citep{bruineberg2022emperor}; a positive tally should not be relabeled as consensus.

FEP universality (H1) generates {{H1_TOTAL}} assertions yet achieves a score of ${{H1_SCORE}}$. Neutral assessments account for {{H1_NEUTRAL}} of those tallies, compared with {{H1_SUPPORT}} supporting and {{H1_CONTRADICT}} contradicting assertions. This composition illustrates why a large evidence count does not imply a strongly directional result: many papers invoke the FEP as conceptual scaffolding without explicitly testing universality. The observation is consistent with falsifiability critiques of broad principle-level claims \citep{colombo2021free}, but remains an interpretation of the extracted abstract-level evidence.

### Temporal Dynamics of Evidence Accumulation

The cumulative evidence timeline (Figure \ref{fig:evidence_timeline}) is descriptive and limited to the observed corpus years. Early years can show extreme scores when only a small number of assertions contribute; the updated figure reports cumulative assertion counts alongside the score encoding. Later trajectories should be interpreted as accumulation patterns rather than causal effects of individual papers, especially for H5 and H6, whose evidence base is concentrated in more recent literature. The timeline does not establish that any hypothesis became positive before the first year represented in this corpus.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/evidence_timeline.png}
\caption{Temporal evolution of cumulative citation-weighted evidence scores by hypothesis ({{YEAR_START}}--{{YEAR_END}}). Marker and line encoding includes cumulative assertion counts so sparse early years are not mistaken for stable estimates.}
\label{fig:evidence_timeline}
\end{figure}

### Assertion Composition and Distribution

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

### Limitations of the Current Scoring Approach


#### Publication Bias and Linguistic Asymmetry {#sec:pub_bias}

The mixed scores observed across the eight hypotheses should be interpreted with two systematic caveats.

First, **publication bias** systematically inflates supporting evidence. Academic journals preferentially publish positive and confirmatory results (\citep{sterling1959publication}), meaning that studies finding null or contradictory outcomes for any hypothesis are less likely to appear in the retrievable literature. This \textit{file-drawer effect} is well-documented across scientific disciplines and is expected to disproportionately suppress contradicting assertions in our extraction pipeline. The Active Inference literature is particularly susceptible: as a theoretical framework with strong foundational proponents, papers are more likely to frame results as consistent with the FEP than as challenges to it.

Second, **linguistic asymmetry** in academic writing further skews extraction toward positive classifications. Declarative scholarly claims are inherently phrased affirmatively—authors write "our results support," "consistent with," or "extends the prediction of" far more frequently than "our results refute" or "contradicts the claim that." Because the LLM extraction pipeline operates on abstract text, this linguistic imbalance propagates directly into the assertion distribution. Even papers presenting genuinely mixed evidence tend to frame their abstracts in terms of what \textit{was} found rather than what was not, biasing the extracted direction toward ``supports.''

These two effects act in concert: publication bias reduces the number of contradicting papers in the corpus, and linguistic framing reduces the number of contradicting assertions extracted from the papers that do appear. Consequently, the absolute values of hypothesis scores should not be taken as unbiased measures of scientific consensus. We retain the relative ordering and temporal trajectories as transparent descriptive summaries, but the present study does not establish that they are robust to extraction error, retrieval bias, or correlated evidence.

### Methodological Validation and LLM Calibration

The evidence derives from automated LLM-based assertion extraction operating on abstracts only. A stratified rule-based reference-annotator agreement study ($n = {{VAL_N}}$) provides a first quantitative, fully reproducible calibration: two deterministic keyword-rule protocols agree at $\kappa = {{VAL_KAPPA}}$ (reference stability), while pipeline triage against the primary rule reference yields precision {{VAL_PRECISION}}, recall {{VAL_RECALL}}, and F1 {{VAL_F1}}, with reference--pipeline direction agreement of only $\kappa = {{VAL_KAPPA_PIPELINE}}$. That the LLM and an independent keyword reference diverge this sharply is itself the calibration result: over-extraction (pipeline labels relevant where the keyword reference labels irrelevant) accounts for {{VAL_ERR_OVER_EXTRACTION}} of sampled rows, directly motivating the tempered interpretation of absolute hypothesis scores. Rankings and temporal trajectories are retained for auditability, not treated as validated estimates. These figures are a reproducibility floor, not accuracy against human ground truth, which remains future work. Full metrics and error taxonomy appear in Table \ref{tab:validation_metrics} (\S\ref{sec:extraction_pipeline}).

### Citation-Weighting Sensitivity

Hypothesis ranks under {{SENSITIVITY_ALTERNATIVE_POLICY_COUNT}} alternative weight policies remain stable in this weighting-only sensitivity check: minimum rank-stability Spearman $\rho = {{SENSITIVITY_SPEARMAN}}$ versus the default log-citation policy, with {{SENSITIVITY_RANK_FLIPS}} rank-position changes across all {{SENSITIVITY_POLICY_COUNT}} tested policies. {{SENSITIVITY_SIGN_CHANGE_COUNT}} hypotheses change sign under at least one tested policy, so sign and tier language remain sensitivity-dependent. The largest policy shifts should be read as a weighting diagnostic rather than as evidence of a different scientific conclusion.
