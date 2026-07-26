## Domain Analyses: Growth Trajectories and Open Problems \label{sec:subfield_analyses}

_This supplementary section provides detailed characterizations of each of the eight tracked Active Inference domains, organized under three tiers: A (Core Theory), B (Tools & Translation), and C (Application Domains)._

### Domain A: Core Theory

#### A1 — Quantitative & Formal Theory ($n = 64$, 7.8\%)

The A1 domain develops the mathematical foundations underpinning the Free Energy Principle: information geometry, category-theoretic formulations of Markov blankets, path integral formulations of free energy minimization, and gauge-theoretic perspectives on self-organization. A central debate concerns the ontological status of Markov blankets—whether they correspond to real physical boundaries or are merely useful statistical constructs \citep{bruineberg2022emperor}. Bruineberg et al. draw a critical distinction between _Pearl blankets_ (instrumental, epistemic tools for conditional independence in Bayesian networks) and _Friston blankets_ (ontologically laden physical boundaries between agent and environment), arguing that the scientific credibility of the former should not be extended uncritically to the latter. Friston and collaborators continue to address this critique through the development of Bayesian mechanics \citep{sakthivadivel2023bayesian}, which aims to place the FEP on firmer mathematical footing by grounding Markov blanket dynamics in the physics of belief-based systems. Our hypothesis scoring quantifies this debate: the Markov blanket realism hypothesis (H3) achieves a score of $-0.82$ with 108 contradicting assertions, making it the most heavily contested hypothesis in the corpus. Recent theoretical consolidation has strengthened the formal tools available to A1: variational message passing formulations \citep{champion2021realizing} connect expected free energy decomposition—into risk, ambiguity, epistemic, and instrumental components—to practical planning algorithms, advancing the theoretical justification for EFE-based policy selection. Path integral formulations now connect Markov blanket dynamics to least-action principles, framing free energy minimization as paths of least action for belief updating. With 64 papers (7.8\% of the corpus), A1 captures a meaningful share of formal work, reflecting the improved classifier's ability to route papers with mathematical formalism (theorems, proofs, convergence, posterior distributions, Fokker–Planck equations) into this domain rather than the qualitative philosophy catch-all. **Key evidence gap:** A mathematically formal distinction yielding testable predictions that differentiate systems actively minimizing an internal free energy functional from systems that merely possess a Markov blanket.

#### A2 — Qualitative Philosophy & General Theory ($n = 60$, 7.3\%)

The A2 domain encompasses papers that develop, extend, or review the core Free Energy Principle and Active Inference framework without restricting attention to a specific application domain. This includes Friston's foundational work on variational free energy minimization \citep{friston2010free}, the textbook treatment by Parr, Pezzulo, and Friston \citep{parr2022active}, and numerous tutorial and review papers. The priority-based classifier mitigates over-assignment to A2 by routing papers with mathematical formalism to A1 and papers with domain-specific vocabulary to C1–C5 or B before the A2 catch-all is reached. Nevertheless, the count likely still conceals meaningful internal structure: papers addressing embodied cognition, Bayesian brain theory, and philosophical implications of the FEP are all subsumed under this heading.

Three unresolved debates drive the most contested A2 literature. First, the **explanatory scope** question: is the FEP a principle of physics (applying to any system at non-equilibrium steady state \citep{friston2010free}), a principle of biology (restricted to organisms that actively maintain their boundaries against entropy), or a computational-level description of cognition \citep{clark2013whatever}? The answer determines whether evidence from robotics, synthetic biology, or cellular dynamics counts as genuine support for the FEP or merely analogical illustration. Second, the **relationship to reinforcement learning**: active inference and deep RL both minimize expected future cost, but differ in whether the objective is expected free energy (AIF) or expected cumulative reward (RL). Establishing formal equivalence or principled divergence between these frameworks is prerequisite for the benchmark comparisons domain B requires. Third, **eliminativist vs. instrumentalist interpretations** of free energy itself—whether variational free energy is a latent quantity the brain actually tracks or a mathematical convenience for describing inference—remain open, with consequences for the empirical status of A1 formalisms. **Key evidence gap:** A head-to-head theoretical comparison showing conditions under which active inference makes predictions that differ from reinforcement learning, optimal control, or Bayesian brain models, together with experimental designs capable of adjudicating among them.

### Domain B: Tools & Translation Methods

#### B — Algorithms, Scaling, and Software ($n = 170$, 20.8\%)

Domain B addresses the computational challenge of making active inference practical in complex, high-dimensional environments. Early implementations relied on small discrete state spaces amenable to exact message passing. Recent work has introduced deep active inference using neural networks to amortize inference \citep{fountas2020deep}, Monte Carlo tree search for planning \citep{champion2021realizing}, hybrid architectures combining model-based planning with model-free components, and interpretable alternatives such as Free Energy Projective Simulation (FEPS) \citep{pazem2024feps}, which exposes decision logic as human-readable policy graphs. The central open question is whether active inference agents can match deep reinforcement learning performance on standard benchmarks while retaining interpretability and sample efficiency. The availability of the pymdp library \citep{heins2022pymdp} has lowered implementation barriers, contributing to this domain's growth. The recent establishment of the Pymdp Fellowship program (funding 8 open-source developers in 2025) and the release of real-time stream processing tools like RxInfer.jl v4.0.0 \citep{rxinfer2025} indicate a vibrant and maturing software ecosystem. **Key evidence gap:** Head-to-head benchmarking of AIF agents against state-of-the-art deep RL baselines on standardized, continuous-control or long-horizon environments.

### Domain C: Application Domains

#### C1 — Neuroscience ($n = 161$, 19.7\%)

Neuroscience represents the historical core of the Active Inference research program. The predictive processing account—in which cortical hierarchies minimize prediction errors through both perceptual inference and active sampling—remains one of the most empirically tested aspects of the framework \citep{friston2010free, clark2013whatever}. The broader neuroscience literature on Dynamic Causal Modeling and predictive coding is extensive; the relatively modest count here likely reflects the keyword classifier's inability to distinguish neuroscience-specific applications from general FEP theory. Bridging the gap between computational models and empirical neuroimaging data remains the domain's primary challenge.

#### C2 — Robotics ($n = 136$, 16.6\%)

Robotics applications treat embodied agents as free energy minimizing systems that unify perception and action through proprioceptive and exteroceptive prediction errors \citep{lanillos2021active}. Applications include robotic arm control, mobile navigation, manipulation, and multi-robot coordination. Active inference offers roboticists a principled framework for integrating sensory processing, motor planning, and adaptive behavior without separate perception and control modules. Key challenges include real-time computational feasibility on embedded hardware, continuous high-dimensional action spaces, and sim-to-real transfer.

#### C3 — Language Processing ($n = 58$, 7.1\%)

The C3 domain conceptualizes linguistic processes—speech perception, sentence comprehension, dialogue, and reading—as active inference operating over deep hierarchical generative models of linguistic structure \citep{friston2020generative}. Active inference models of reading have reproduced saccadic eye-movement patterns, while models of speech perception capture how listeners integrate prior expectations with acoustic evidence. Recent work couples active inference to large language models, pragmatics, and multi-agent communication. The connection between AIF and LLMs runs in both directions: Wen \citep{wen2025missing} proposes that AIF can replace external reward signals in LLM-based agents, while Friston et al. \citep{friston2025active} demonstrate how active inference enables artificial reasoning through structure learning via Bayesian Model Reduction. The language domain is also where AIF shows strong results through novel discrete generative models for structured sequential tasks \citep{millidge2024retrospective}.

#### C4 — Computational Psychiatry ($n = 33$, 4.0\%)

Computational psychiatry leverages active inference to model psychiatric conditions as disruptions in belief updating, precision weighting, or prior rigidity \citep{smith2021computational}. Schizophrenia has been modeled as impaired precision weighting on bottom-up prediction errors; depression as over-precise negative priors; and autism spectrum conditions as atypical precision allocation over sensory channels. Beyond clinical psychopathology, the framework is now being extended to model higher-order cognition: Whyte et al. \citep{whyte2025metacognitive} propose a metacognitive active inference account of imaginative experience, in which "inner screen" representations emerge from EFE-driven attention allocation under FEP constraints—connecting computational psychiatry to consciousness research. The domain continues to expand, with emerging frameworks integrating psychodynamic theory (e.g., self-identity formation via embodied interactions) with predictive processing to unify environmental and biological factors underlying stress disorders. Translating these computational models into diagnostic markers and therapeutic protocols remains an ongoing challenge. **Key evidence gap:** Translating retrodictive computational phenotyping models into prospective clinical predictions that demonstrably outperform standard diagnostic criteria in clinical trials.

#### C5 — Biology & Morphogenesis ($n = 135$, 16.5\%)

The C5 domain applies active inference and the FEP to biological systems beyond the brain: cellular behavior, morphogenesis, evolutionary dynamics, and the origins of life. Morphogenetic processes have been modeled as collective active inference, where groups of cells coordinate to minimize a shared free energy functional \citep{kuchling2020morphogenesis, levin2022technological}. Recent empirical work has validated collective AIF at larger scales: Heins et al. \citep{heins2024collective} demonstrated that surprise minimization alone produces realistic collective motion patterns, providing a principled alternative to ad hoc flocking rules. The FEP's reach now extends beyond biological organisms into engineered systems: Nazemi et al. \citep{nazemi2025energy} apply active inference to smart building energy control under partial observability and privacy constraints, demonstrating that the free energy framework can govern resource allocation in cyber-physical systems. As the second-largest domain, C5 reflects growing interest in extending the FEP to encompass all self-organizing systems—living and artificial—though the ratio of theoretical proposals to empirical validation remains high.

### Comparative Synthesis

Taken together, the three domains reveal a field transitioning from a focused neuroscience program to a broad interdisciplinary framework. The core–periphery structure is clear: Domain A provides the theoretical and mathematical substrate, Domain B pursues engineering viability through scalable algorithms and software, and Domain C tests the framework's generality across neuroscience (C1), robotics (C2), language (C3), psychiatry (C4), and biology (C5). The consistent pattern across applied domains—strong theoretical motivation paired with limited empirical validation—suggests that the field's next growth phase will depend on accumulating experimental evidence.

In direct response to **RQ1** (How is the Active Inference field structured?), the domain taxonomy reveals an asymmetric three-tier architecture: a dominant theoretical core (A), a growing translational layer (B), and an expanding but empirically sparse application periphery (C). The keyword classifier's heavy A2 concentration likely masks genuine diversity within the theoretical core, but the architecture itself—theory → tools → applications—is robust across classification approaches.

#### Domain–Hypothesis Cross-Reference

Each domain has a primary hypothesis linkage (see the detailed hypothesis evidence analysis in the \hyperref[sec:hypothesis_results]{hypothesis results}):


\begin{table}[htbp]
\centering
\caption[Domain--hypothesis cross-reference]{Domain--hypothesis cross-reference linking each of the eight tracked categories to its primary hypothesis and the direction of the current evidence base. See the \hyperref[sec:hypothesis_results]{hypothesis results} for quantitative scores and temporal trends. Table values are regenerated automatically from \texttt{hypothesis\_scores.json}; the most recent verified pipeline run is dated 2026-04-28.}
\label{tab:domain_hypothesis_crossref}
\begin{tabular}{llcll}
\toprule
\textbf{Domain} & \textbf{Category} & $n$ & \textbf{Primary Hypothesis} & \textbf{Evidence Direction} \\
\midrule
A1 & Formal & 64 & H3 Markov Blanket Realism & Contested \\
A2 & Philosophy & 60 & H1 FEP Universality & Strongly supporting \\
B & Tools & 170 & H5 Scalability & Mixed \\
C1 & Neuroscience & 161 & H4 Predictive Coding & Supporting \\
C2 & Robotics & 136 & H2 AIF Optimality, H5 Scalability & Mixed \\
C3 & Language & 58 & H8 Language AIF & Emerging \\
C4 & Psychiatry & 33 & H6 Clinical Utility & Supporting \\
C5 & Biology & 135 & H7 Morphogenesis & Supporting \\
\bottomrule
\end{tabular}
\end{table}


The evidence directions summarized above are elaborated quantitatively—with citation-weighted scores, temporal trends, and three-tier evidence profiling—in the \hyperref[sec:hypothesis_results]{hypothesis results section}.
