## Field Overview: Disciplinary Structure and Growth Dynamics {#sec:field_overview}

Annual output in the Active Inference literature rose from {{YEAR_START_PUBS}} papers in {{YEAR_START}}, reaching a peak of {{PEAK_YEAR_PUBS}} papers in {{PEAK_YEAR}}—a transition from a niche within theoretical neuroscience to a multi-disciplinary research program spanning three primary domains and eight tracked categories. The corpus start of {{YEAR_START}} was chosen to capture Energy-Based Model and variational Bayesian antecedents \citep{dayan1995helmholtz, lecun2006tutorial} that preceded the formal introduction of the Free Energy Principle in 2006 \citep{friston2006free} and its subsequent full elaboration \citep{friston2010free}. Our corpus, extracted from arXiv, Semantic Scholar, and OpenAlex and deduplicated to $N = {{CORPUS_SIZE}}$ papers ({{YEAR_START}}--{{YEAR_END}}), captures the breadth, tempo, and internal architecture of this expansion (Figure \ref{fig:field_summary}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/field_summary.png}
\caption{Publication counts by domain ($N = {{CORPUS_SIZE}}$). Application domains (C1--C5) collectively account for the largest share of the corpus; {{TOP_SUBFIELD_LABEL}} is the largest single category in this run.}
\label{fig:field_summary}
\end{figure}

### Corpus-Level Summary


\begin{table}[htbp]
\centering
\caption{Corpus-level summary statistics for the Active Inference literature corpus ($N = {{CORPUS_SIZE}}$), observed over {{YEAR_START}}--{{YEAR_END}} with the most recent year reported as {{CURRENT_YEAR_STATUS}}.}
\label{tab:corpus_summary}
\begin{tabular}{ll}
\toprule
\textbf{Metric} & \textbf{Value} \\
\midrule
Total papers & {{CORPUS_SIZE}} \\
Year range & {{YEAR_START}}--{{YEAR_END}} ({{CURRENT_YEAR_STATUS}}) \\
Peak year & {{PEAK_YEAR}} \\
CAGR & {{CAGR_PCT}}\% \\
Active domains & 8 of 8 tracked (A1--A2, B, C1--C5) \\
\bottomrule
\end{tabular}
\end{table}


The CAGR of {{CAGR_PCT}}\% is measured as the annualised growth rate of yearly publication volume between complete endpoint years {{CAGR_START_YEAR}} and {{CAGR_END_YEAR}}. The corpus also contains {{CURRENT_YEAR_PUBS}} papers from {{CURRENT_YEAR}} as of {{AS_OF_DATE}}; this partial-year count is shown separately in the growth figure and is not used as the CAGR endpoint. Citation network metrics are detailed in the dedicated citation network analysis (see \hyperref[sec:citation_network]{the citation network analysis}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/growth_curve.png}
\caption{Annual (bars) and cumulative (line) publication counts, {{YEAR_START}}--{{YEAR_END}} ($N = {{CORPUS_SIZE}}$, CAGR = {{CAGR_PCT}}\% over {{CAGR_PERIOD}}). The {{CURRENT_YEAR}} bar is partial as of {{AS_OF_DATE}}.}
\label{fig:growth_curve}
\end{figure}

### Domain Distribution

Keyword-based classification assigns each paper to one of eight categories across three domains:


\begin{table}[htbp]
\centering
\caption{Domain distribution across three tiers and eight categories ($N = {{CORPUS_SIZE}}$ papers). Classification uses hierarchical keyword matching with priority-based routing to minimize over-assignment to catch-all categories.}
\label{tab:domain_distribution}
\begin{tabular}{llcc}
\toprule
\textbf{Domain} & \textbf{Category} & \textbf{Papers} & \textbf{Percentage} \\
\midrule
A -- Core Theory & A1: Formal Theory & {{A1_COUNT}} & {{A1_PCT}}\% \\
 & A2: Qualitative Philosophy & {{A2_COUNT}} & {{A2_PCT}}\% \\
\midrule
B -- Tools & B: Tools \& Translation & {{B_COUNT}} & {{B_PCT}}\% \\
\midrule
C -- Applications & C1: Neuroscience & {{C1_COUNT}} & {{C1_PCT}}\% \\
 & C2: Robotics & {{C2_COUNT}} & {{C2_PCT}}\% \\
 & C3: Language & {{C3_COUNT}} & {{C3_PCT}}\% \\
 & C4: Psychiatry & {{C4_COUNT}} & {{C4_PCT}}\% \\
 & C5: Biology & {{C5_COUNT}} & {{C5_PCT}}\% \\
\bottomrule
\end{tabular}
\end{table}


The largest single category is {{TOP_SUBFIELD_LABEL}}; the counts should be read as classifier assignments rather than as measures of disciplinary importance (Figure \ref{fig:subfield_distribution}). The priority-based classifier routes papers with mathematical indicators (theorems, proofs, equations, statistical formalism) to A1 before falling back to A2, and prefers specific application domains (C1–C5) and tools (B) over both core-theory categories. Papers that discuss FEP/AIF conceptually without mathematical formalism or domain-specific vocabulary are assigned to A2. Embedding-based classification could redistribute some fraction across categories, so the taxonomy is a reproducible map rather than a literal measure of research focus. All eight categories are populated, indicating diversification beyond the field's neuroscience origins.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/subfield_distribution.png}
\caption{Domain distribution ($N = {{CORPUS_SIZE}}$). Classification uses hierarchical keyword matching against curated lists applied to titles and abstracts, capturing distinct methodological and domain-specific groupings.}
\label{fig:subfield_distribution}
\end{figure}

Detailed characterizations of each domain—including historical context, growth trends, and open problems—are provided in the supplementary domain analyses (see \hyperref[sec:subfield_analyses]{the domain analyses}). Latent topic structure, vocabulary analysis, and document embeddings are presented in the text analytics section (see \hyperref[sec:text_analytics]{the text analytics section}).

### Cross-Domain Comparison


\begin{table}[htbp]
\centering
\caption{Cross-domain comparison showing growth trajectories, maturity levels, key challenges, and representative publications for each of the eight tracked categories. Growth trends and maturity assessments are based on temporal publication patterns and evidence base depth.}
\label{tab:cross_domain_comparison}
\begin{tabular}{llcllll}
\toprule
\textbf{Domain} & \textbf{Category} & \textbf{Papers} & \textbf{Growth} & \textbf{Maturity} & \textbf{Key Challenge} & \textbf{Rep.\ Work} \\
\midrule
A & A1: Formal & {{A1_COUNT}} ({{A1_PCT}}\%) & Growing & Mature & Math accessibility & \citep{sakthivadivel2023bayesian} \\
A & A2: Philosophy & {{A2_COUNT}} ({{A2_PCT}}\%) & Stable & Mature & Catch-all absorption & \citep{friston2010free} \\
B & B: Tools & {{B_COUNT}} ({{B_PCT}}\%) & Rapid & Growing & Deep RL benchmarks & \citep{fountas2020deep} \\
C & C1: Neuroscience & {{C1_COUNT}} ({{C1_PCT}}\%) & Stable & Mature & Theory--neuroimaging gap & \citep{clark2013whatever} \\
C & C2: Robotics & {{C2_COUNT}} ({{C2_PCT}}\%) & Growing & Growing & Embedded real-time & \citep{lanillos2021active} \\
C & C3: Language & {{C3_COUNT}} ({{C3_PCT}}\%) & Emerging & Nascent & NLP model comparison & \citep{friston2020generative} \\
C & C4: Psychiatry & {{C4_COUNT}} ({{C4_PCT}}\%) & Emerging & Nascent & Clinical translation & \citep{smith2021computational} \\
C & C5: Biology & {{C5_COUNT}} ({{C5_PCT}}\%) & Rapid & Nascent & Empirical validation & \citep{kuchling2020morphogenesis} \\
\bottomrule
\end{tabular}
\end{table}


Three structural features emerge from the cross-domain comparison (Figure \ref{fig:subfield_timeline}). Ranked by corpus share, the domains are {{DOMAIN_RANKING}}. Domain C is therefore the largest descriptive tier in this snapshot, while Domain A's smaller share does not measure its intellectual influence: the mathematical formalisms developed in A1 shape implementations across all domains. The emergent application frontiers (C3–C5) should be interpreted through their temporal trajectories rather than assumed to be uniformly accelerating.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/subfield_timeline.png}
\caption{Stacked area chart of publications by domain, {{YEAR_START}}--{{YEAR_END}} ($N = {{CORPUS_SIZE}}$). The current-year observation is partial as of {{AS_OF_DATE}}; the chart reports classifier-assigned category totals and temporal composition.}
\label{fig:subfield_timeline}
\end{figure}
