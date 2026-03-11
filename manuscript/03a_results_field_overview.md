# Field Overview: Disciplinary Structure and Growth Dynamics \label{sec:field_overview}

The Active Inference literature has undergone a phase transition. What originated in the late 2000s as a niche within theoretical neuroscience has expanded rapidly into a multi-disciplinary research program spanning three primary domains and eight tracked categories. Our corpus, extracted from arXiv, Semantic Scholar, and OpenAlex and deduplicated to $N = {{CORPUS_SIZE}}$ papers ({{YEAR_START}}--{{YEAR_END}}), captures the breadth, tempo, and internal architecture of this expansion (Figure \ref{fig:field_summary}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/field_summary.png}
\caption{Publication counts by domain ($N = {{CORPUS_SIZE}}$). Domain A (Core Theory) dominates, with Domains B (Tools) and C (Applications) forming growing tiers.}
\label{fig:field_summary}
\end{figure}

## Corpus-Level Summary

| Metric | Value |
| --- | --- |
| Total papers | {{CORPUS_SIZE}} |
| Year range | {{YEAR_START}}--{{YEAR_END}} |
| Peak year | {{PEAK_YEAR}} |
| CAGR | {{CAGR_PCT}}\% |
| Active domains | 8 of 8 tracked (A1–A2, B, C1–C5) |

The CAGR of {{CAGR_PCT}}\% reflects the corpus's long temporal span from {{YEAR_START}} to {{YEAR_END}}; the field's actual rapid growth phase began around 2013, with annual output accelerating substantially (Figure \ref{fig:growth_curve}). The fact that sustained high output persists into subsequent years suggests the field has reached a mature production phase rather than experiencing a transient spike. Citation network metrics are detailed in the dedicated citation network analysis (see \hyperref[sec:citation_network]{the citation network analysis}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/growth_curve.png}
\caption{Annual (bars) and cumulative (line) publication counts, {{YEAR_START}}--{{YEAR_END}} ($N = {{CORPUS_SIZE}}$, CAGR = {{CAGR_PCT}}\%). The inflection around 2013 marks the onset of rapid growth. Moving average trendline (dashed), peak year, and median year annotated.}
\label{fig:growth_curve}
\end{figure}

## Domain Distribution

Keyword-based classification assigns each paper to one of eight categories across three domains:

| Domain | Category | Papers | Percentage |
| --- | --- | --- | --- |
| **A – Core Theory** | A1: Formal Theory | {{A1_COUNT}} | {{A1_PCT}}\% |
| | A2: Qualitative Philosophy | {{A2_COUNT}} | {{A2_PCT}}\% |
| **B – Tools** | B: Tools \& Translation | {{B_COUNT}} | {{B_PCT}}\% |
| **C – Applications** | C1: Neuroscience | {{C1_COUNT}} | {{C1_PCT}}\% |
| | C2: Robotics | {{C2_COUNT}} | {{C2_PCT}}\% |
| | C3: Language | {{C3_COUNT}} | {{C3_PCT}}\% |
| | C4: Psychiatry | {{C4_COUNT}} | {{C4_PCT}}\% |
| | C5: Biology | {{C5_COUNT}} | {{C5_PCT}}\% |

The concentration of papers in A2 (qualitative philosophy and general theory) reflects the broad scope of foundational FEP work (Figure \ref{fig:subfield_distribution}). The priority-based classifier mitigates over-assignment by routing papers with mathematical indicators (theorems, proofs, equations, statistical formalism) to A1 before falling back to A2, and by preferring specific application domains (C1–C5) and tools (B) over both core-theory categories. Papers that discuss FEP/AIF conceptually without mathematical formalism or domain-specific vocabulary are correctly assigned to A2. This figure should be read as a *ceiling* on theoretical generality rather than a literal measure of research focus—embedding-based classification would likely redistribute some fraction into more specific categories. That all eight categories are populated, including computational psychiatry (C4) and formal theory (A1), indicates diversification beyond the field's neuroscience origins.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/subfield_distribution.png}
\caption{Domain distribution ($N = {{CORPUS_SIZE}}$). Classification uses hierarchical keyword matching against curated lists applied to titles and abstracts, capturing distinct methodological and domain-specific groupings.}
\label{fig:subfield_distribution}
\end{figure}

Detailed characterizations of each domain—including historical context, growth trends, and open problems—are provided in the supplementary domain analyses (see \hyperref[sec:subfield_analyses]{the domain analyses}). Latent topic structure, vocabulary analysis, and document embeddings are presented in the text analytics section (see \hyperref[sec:text_analytics]{the text analytics section}).

## Cross-Domain Comparison

| Domain | Category | Papers | Growth Trend | Key Challenge | Representative Work |
| --- | --- | --- | --- | --- | --- |
| A | A1: Formal | {{A1_COUNT}} ({{A1_PCT}}\%) | Growing | Mathematical accessibility for broader field | \citep{sakthivadivel2023bayesian} |
| A | A2: Philosophy | {{A2_COUNT}} ({{A2_PCT}}\%) | Stable | Residual catch-all; absorbs FEP prose papers | \citep{friston2010free} |
| B | B: Tools | {{B_COUNT}} ({{B_PCT}}\%) | Rapid | Matching deep RL benchmark performance | \citep{fountas2020deep} |
| C | C1: Neuroscience | {{C1_COUNT}} ({{C1_PCT}}\%) | Stable | Bridging theory and empirical neuroimaging | \citep{clark2013whatever} |
| C | C2: Robotics | {{C2_COUNT}} ({{C2_PCT}}\%) | Growing | Real-time feasibility on embedded hardware | \citep{lanillos2021active} |
| C | C3: Language | {{C3_COUNT}} ({{C3_PCT}}\%) | Emerging | Demonstrating gains over existing NLP models | \citep{friston2020generative} |
| C | C4: Psychiatry | {{C4_COUNT}} ({{C4_PCT}}\%) | Emerging | Translating models to clinical practice | \citep{smith2021computational} |
| C | C5: Biology | {{C5_COUNT}} ({{C5_PCT}}\%) | Rapid | Empirical validation of theoretical proposals | \citep{kuchling2020morphogenesis} |

Three structural features emerge from the cross-domain comparison (Figure \ref{fig:subfield_timeline}). First, no single legacy domain dominates: Domain B (Tools \& Translation) accounts for {{B_PCT}}\% of the corpus, followed by C1 (Neuroscience) at {{C1_PCT}}\% and C2 (Robotics) at {{C2_PCT}}\%. Second, Domain A (Core Theory) aggregates {{A_PCT}}\% collectively (A1 + A2), while the emergent application frontiers (C3–C5) exhibit accelerating growth. Third, A1's {{A1_COUNT}} papers understate its intellectual influence—the mathematical formalisms developed in A1 shape implementations across all domains.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/subfield_timeline.png}
\caption{Stacked area chart of publications by domain, {{YEAR_START}}--{{YEAR_END}} ($N = {{CORPUS_SIZE}}$). Domain A (Core Theory) dominates throughout; application domains C1--C5 show accelerating diversification from 2015 onward.}
\label{fig:subfield_timeline}
\end{figure}
