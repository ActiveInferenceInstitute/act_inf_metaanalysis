## Field Overview: Disciplinary Structure and Growth Dynamics \label{sec:field_overview}

Annual output in the Active Inference literature rose from {{YEAR_START_PUBS}} papers in {{YEAR_START}}, reaching a peak of {{PEAK_YEAR_PUBS}} papers in {{PEAK_YEAR}}—a transition from a niche within theoretical neuroscience to a multi-disciplinary research program spanning three primary domains and eight tracked categories. The corpus start of {{YEAR_START}} was chosen to capture Energy-Based Model and variational Bayesian antecedents \citep{dayan1995helmholtz, lecun2006tutorial} that preceded the formal introduction of the Free Energy Principle in 2006 \citep{friston2006free} and its subsequent full elaboration \citep{friston2010free}. Our corpus, extracted from arXiv, Semantic Scholar, and OpenAlex and deduplicated to $N = {{CORPUS_SIZE}}$ papers ({{YEAR_START}}--{{YEAR_END}}), captures the breadth, tempo, and internal architecture of this expansion (Figure \ref{fig:field_summary}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/field_summary.png}
\caption{Publication counts by domain ($N = {{CORPUS_SIZE}}$). Application domains (C1--C5) collectively account for the largest share of the corpus; Domain A2 (qualitative philosophy) is the largest single category, reflecting the FEP's broad theoretical reach.}
\label{fig:field_summary}
\end{figure}

### Corpus-Level Summary


\begin{table}[htbp]
\centering
\caption{Corpus-level summary statistics for the Active Inference literature corpus ($N = {{CORPUS_SIZE}}$), spanning {{YEAR_START}}--{{YEAR_END}}.}
\label{tab:corpus_summary}
\begin{tabular}{ll}
\toprule
\textbf{Metric} & \textbf{Value} \\
\midrule
Total papers & {{CORPUS_SIZE}} \\
Year range & {{YEAR_START}}--{{YEAR_END}} \\
Peak year & {{PEAK_YEAR}} \\
CAGR & {{CAGR_PCT}}\% \\
Active domains & 8 of 8 tracked (A1--A2, B, C1--C5) \\
\bottomrule
\end{tabular}
\end{table}


The CAGR of {{CAGR_PCT}}\% (measured as the annualised growth rate of yearly publication volume between endpoint years {{YEAR_START}} and {{YEAR_END}}) reflects sustained field expansion; the actual rapid growth phase began around 2013, with annual output accelerating substantially (Figure \ref{fig:growth_curve}). Sustained high output persisting into subsequent years suggests the field has reached a mature production phase rather than experiencing a transient spike. Citation network metrics are detailed in the dedicated citation network analysis (see \hyperref[sec:citation_network]{the citation network analysis}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/growth_curve.png}
\caption{Annual (bars) and cumulative (line) publication counts, {{YEAR_START}}--{{YEAR_END}} ($N = {{CORPUS_SIZE}}$, CAGR = {{CAGR_PCT}}\%). The inflection around 2013 marks the onset of rapid growth. Moving average trendline (dashed), peak year, and median year annotated.}
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


The concentration of papers in A2 (qualitative philosophy and general theory) reflects the broad scope of foundational FEP work (Figure \ref{fig:subfield_distribution}). The priority-based classifier mitigates over-assignment by routing papers with mathematical indicators (theorems, proofs, equations, statistical formalism) to A1 before falling back to A2, and by preferring specific application domains (C1–C5) and tools (B) over both core-theory categories. Papers that discuss FEP/AIF conceptually without mathematical formalism or domain-specific vocabulary are correctly assigned to A2. This figure should be read as a *ceiling* on theoretical generality rather than a literal measure of research focus—embedding-based classification would likely redistribute some fraction into more specific categories. That all eight categories are populated, including computational psychiatry (C4) and formal theory (A1), indicates diversification beyond the field's neuroscience origins.

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


Three structural features emerge from the cross-domain comparison (Figure \ref{fig:subfield_timeline}). First, no single legacy domain dominates: Domain B (Tools \& Translation) accounts for {{B_PCT}}\% of the corpus, followed by C1 (Neuroscience) at {{C1_PCT}}\% and C2 (Robotics) at {{C2_PCT}}\%. Second, Domain A (Core Theory) aggregates {{A_PCT}}\% collectively (A1 + A2), while the emergent application frontiers (C3–C5) exhibit accelerating growth. Third, A1's {{A1_COUNT}} papers understate its intellectual influence—the mathematical formalisms developed in A1 shape implementations across all domains.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/subfield_timeline.png}
\caption{Stacked area chart of publications by domain, {{YEAR_START}}--{{YEAR_END}} ($N = {{CORPUS_SIZE}}$). A2 (qualitative philosophy) provides a large baseline; application domains C1--C5 show accelerating diversification from 2015 onward.}
\label{fig:subfield_timeline}
\end{figure}
