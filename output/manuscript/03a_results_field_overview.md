## Field Overview: Disciplinary Structure and Growth Dynamics {#sec:field_overview}

Annual output in the Active Inference literature rose from 1 papers in 2003, reaching a peak of 134 papers in 2025—a transition from a niche within theoretical neuroscience to a multi-disciplinary research program spanning three primary domains and eight tracked categories. The corpus start of 2003 was chosen to capture Energy-Based Model and variational Bayesian antecedents \citep{dayan1995helmholtz, lecun2006tutorial} that preceded the formal introduction of the Free Energy Principle in 2006 \citep{friston2006free} and its subsequent full elaboration \citep{friston2010free}. The configured corpus sources are arXiv, Semantic Scholar, and OpenAlex; this snapshot records arXiv, OpenAlex completed; Semantic Scholar incomplete and contains $N = 1106$ deduplicated papers (2003--2026). It therefore describes the retained retrieval snapshot rather than an exhaustive census (Figure \ref{fig:field_summary}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/field_summary.png}
\caption{Publication counts by domain ($N = 1106$). Application domains (C1--C5) collectively account for the largest share of the corpus; B tools is the largest single category in this run.}
\label{fig:field_summary}
\end{figure}

### Corpus-Level Summary


\begin{table}[htbp]
\centering
\caption{Corpus-level summary statistics for the Active Inference literature corpus ($N = 1106$), observed over 2003--2026 with the most recent year reported as YTD / partial year.}
\label{tab:corpus_summary}
\begin{tabular}{ll}
\toprule
\textbf{Metric} & \textbf{Value} \\
\midrule
Total papers & 1106 \\
Year range & 2003--2026 (YTD / partial year) \\
Peak year & 2025 \\
CAGR & 24.94\% \\
Active domains & 8 of 8 tracked (A1--A2, B, C1--C5) \\
\bottomrule
\end{tabular}
\end{table}


The CAGR of 24.94\% is measured as the annualised growth rate of yearly publication volume between complete endpoint years 2003 and 2025. The corpus also contains 98 papers from 2026 as of 2026-07-26; this partial-year count is shown separately in the growth figure and is not used as the CAGR endpoint. Citation network metrics are detailed in the dedicated citation network analysis (see \hyperref[sec:citation_network]{the citation network analysis}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/growth_curve.png}
\caption{Annual (bars) and cumulative (line) publication counts, 2003--2026 ($N = 1106$, CAGR = 24.94\% over 2003–2025). The 2026 bar is partial as of 2026-07-26.}
\label{fig:growth_curve}
\end{figure}

### Domain Distribution

Keyword-based classification assigns each paper to one of eight categories across three domains:


\begin{table}[htbp]
\centering
\caption{Domain distribution across three tiers and eight categories ($N = 1106$ papers). Classification uses hierarchical keyword matching with priority-based routing to minimize over-assignment to catch-all categories.}
\label{tab:domain_distribution}
\begin{tabular}{llcc}
\toprule
\textbf{Domain} & \textbf{Category} & \textbf{Papers} & \textbf{Percentage} \\
\midrule
A -- Core Theory & A1: Formal Theory & 86 & 7.8\% \\
 & A2: Qualitative Philosophy & 79 & 7.1\% \\
\midrule
B -- Tools & B: Tools \& Translation & 263 & 23.8\% \\
\midrule
C -- Applications & C1: Neuroscience & 212 & 19.2\% \\
 & C2: Robotics & 159 & 14.4\% \\
 & C3: Language & 75 & 6.8\% \\
 & C4: Psychiatry & 60 & 5.4\% \\
 & C5: Biology & 172 & 15.6\% \\
\bottomrule
\end{tabular}
\end{table}


The largest single category is B tools; the counts should be read as classifier assignments rather than as measures of disciplinary importance (Figure \ref{fig:subfield_distribution}). The priority-based classifier routes papers with mathematical indicators (theorems, proofs, equations, statistical formalism) to A1 before falling back to A2, and prefers specific application domains (C1–C5) and tools (B) over both core-theory categories. Papers that discuss FEP/AIF conceptually without mathematical formalism or domain-specific vocabulary are assigned to A2. Embedding-based classification could redistribute some fraction across categories, so the taxonomy is a reproducible map rather than a literal measure of research focus. All eight categories are populated, indicating diversification beyond the field's neuroscience origins.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/subfield_distribution.png}
\caption{Domain distribution ($N = 1106$). Classification uses hierarchical keyword matching against curated lists applied to titles and abstracts, capturing distinct methodological and domain-specific groupings.}
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
A & A1: Formal & 86 (7.8\%) & Growing & Mature & Math accessibility & \citep{sakthivadivel2023bayesian} \\
A & A2: Philosophy & 79 (7.1\%) & Stable & Mature & Catch-all absorption & \citep{friston2010free} \\
B & B: Tools & 263 (23.8\%) & Rapid & Growing & Deep RL benchmarks & \citep{fountas2020deep} \\
C & C1: Neuroscience & 212 (19.2\%) & Stable & Mature & Theory--neuroimaging gap & \citep{clark2013whatever} \\
C & C2: Robotics & 159 (14.4\%) & Growing & Growing & Embedded real-time & \citep{lanillos2021active} \\
C & C3: Language & 75 (6.8\%) & Emerging & Nascent & NLP model comparison & \citep{friston2020generative} \\
C & C4: Psychiatry & 60 (5.4\%) & Emerging & Nascent & Clinical translation & \citep{smith2021computational} \\
C & C5: Biology & 172 (15.6\%) & Rapid & Nascent & Empirical validation & \citep{kuchling2020morphogenesis} \\
\bottomrule
\end{tabular}
\end{table}


Three structural features emerge from the cross-domain comparison (Figure \ref{fig:subfield_timeline}). Ranked by corpus share, the domains are Domain C (Applications) (61.3\%), Domain B (Tools and Translation) (23.8\%), Domain A (Core Theory) (14.9\%). Domain C is therefore the largest descriptive tier in this snapshot, while Domain A's smaller share does not measure its intellectual influence: the mathematical formalisms developed in A1 shape implementations across all domains. The emergent application frontiers (C3–C5) should be interpreted through their temporal trajectories rather than assumed to be uniformly accelerating.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/subfield_timeline.png}
\caption{Stacked area chart of publications by domain, 2003--2026 ($N = 1106$). The current-year observation is partial as of 2026-07-26; the chart reports classifier-assigned category totals and temporal composition.}
\label{fig:subfield_timeline}
\end{figure}
