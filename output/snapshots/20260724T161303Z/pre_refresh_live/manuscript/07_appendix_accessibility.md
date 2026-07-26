# Appendix: Accessibility, Cognitive Ergonomics, and Participatory Research Infrastructure \label{sec:accessibility}

Automated meta-analysis tools operate at the intersection of computational infrastructure and human sensemaking. The scalability gains demonstrated by the present pipeline are meaningful only if the resulting knowledge artefacts remain cognitively accessible, ethically transparent, and open to diverse forms of participation. This appendix situates our work within the broader landscape of research accessibility, cognitive ergonomics, decentralized science (DeSci), and participatory infrastructure design, and concludes with a WCAG-mapped checklist that summarizes the concrete accessibility practices implemented in the figure pipeline.

## Cognitive Ergonomics of Knowledge Graphs

The knowledge-graph outputs of this pipeline---hypothesis dashboards, citation networks, temporal evidence trajectories---impose nontrivial cognitive demands on users who must interpret multidimensional evidence landscapes. Cognitive Load Theory \citep{sweller2011cognitive} establishes that information system designs which exceed working-memory capacity produce disorientation and interpretive errors. Our visualization pipeline addresses this through progressive disclosure (summarized dashboards linking to detailed per-hypothesis breakdowns), consistent visual grammars (a fixed colour palette for supports/contradicts/neutral across all figures), and a minimum font-size floor of 16\,pt that satisfies low-vision accessibility guidelines. These are not cosmetic choices but functional requirements for trustworthy scientific communication.

The ResNei (Research Neighbourhood) platform \citep{lumiruusu2025resnei} provides a particularly instructive design exemplar for the next generation of cognitive-ergonomic research tools. ResNei is an AI-augmented, neuro-informed research environment that transforms heterogeneous scientific corpora into a living, collaborative knowledge graph structured as modular Conceptual Nexus Models (CNMs). Where our pipeline produces a static (though periodically updated) evidence snapshot, ResNei's architecture foregrounds dynamic, responsive exploration through three cognitive modes: \textit{longitudinal} (tracking a concept's evolution over time), \textit{latitudinal} (surveying related concepts across subfields), and \textit{relational} (mapping connections between concepts). This trimodal navigation directly operationalizes the progressive-disclosure principle, enabling users to manage cognitive complexity by choosing their depth of engagement.

### Action--Intention UX and Active Inference Design Principles

ResNei's most theoretically significant contribution is its action--intention UX model, which replaces the conventional passive, attention-maximizing feed with a framework that interprets user actions (uploading papers, highlighting passages, opening concept maps, initiating discussions) as situated signals of research direction. Rather than deploying opaque recommendation engines, the system uses explicit action trajectories to surface contextually appropriate tools and views---an approach that resonates with the perception--action loop central to Active Inference itself \citep{parr2022active}. The design principle of ``minimal system intervention, maximum research coherence'' ensures that the interface scaffolds orientation and affordances without interruptive prompts or aggressive automation. This ethos directly addresses the risk that AI-augmented sensemaking tools inadvertently narrow epistemic horizons through algorithmic filtering.

### Risk-Aware and Bias-Transparent Design

ResNei's solution-design document is notable for its unusually explicit treatment of harms and ameliorations. It identifies exclusion, algorithmic misrepresentation, overconfidence in AI outputs, hidden inequalities, marginalization of less-cited work, surveillance risks, cognitive overload, false comprehensiveness, and data privacy as first-class design constraints \citep{lumiruusu2025resnei}. Mitigations include deliberately inclusive UX (designing from the standpoint of those usually excluded), systematic provenance and confidence indicators, framing all AI outputs as suggestions with traceable bases, and configurable metrics beyond citation counts (e.g., conceptual novelty, geographic diversity, publication type). This risk model provides a concrete template for future iterations of our own pipeline, which currently presents citation-weighted scores without UI-level confidence calibration or per-assertion provenance indicators.

## FAIR Data and Decentralized Science

The pipeline's outputs---nanopublications, knowledge-graph triples, and structured assertion records---are designed to satisfy the FAIR principles (Findable, Accessible, Interoperable, Reusable) articulated by Wilkinson et al. \citep{wilkinson2016fair}. Each nanopublication carries machine-readable provenance (source paper DOI, extraction model, confidence score, timestamp), enabling downstream consumers to evaluate evidential quality independently of our aggregation choices. The JSON Lines and RDF/TriG serialization formats guarantee interoperability with existing semantic-web infrastructure.

Decentralized Science (DeSci) represents a broader movement to dismantle structural barriers in scientific publishing and funding through blockchain-based governance, tokenized intellectual property, and community-owned research commons \citep{hamburg2021desci}. Our pipeline's open-source, modular, and configuration-driven design aligns with DeSci principles: the entire analytical workflow is reproducible from source code, hypothesis definitions and extraction prompts are version-controlled in YAML rather than embedded in proprietary systems, and the nanopublication output format is natively compatible with federated semantic publishing networks. ResNei's architecture further advances this trajectory by grounding its collaborative features in ``social accountability'' and ``reciprocity, interdependence, and access'' as explicit design values \citep{lumiruusu2025resnei}, directly addressing the power asymmetries that traditional centralized publication systems perpetuate.

## Participatory Research and Universal Access

The aspiration toward participatory research infrastructure---where diverse contributors can meaningfully engage with evidence synthesis regardless of technical expertise---is a recurring theme across the projects discussed here. Bonney et al.'s foundational work on citizen science \citep{bonney2009citizen} demonstrated that non-expert participants can make rigorous contributions to scientific knowledge production when provided with appropriate scaffolding, standardized protocols, and feedback loops. Universal Design for Learning principles \citep{rose2000universal} further emphasize that accessibility is not a specialized accommodation but a design paradigm that improves usability for all users.

Applied to computational meta-analysis, this means designing systems where:

\begin{itemize}
  \item \textbf{Contribution pathways} exist at multiple expertise levels---from correcting individual assertion labels (requiring only domain knowledge) to extending extraction prompts or hypothesis definitions (requiring pipeline familiarity);
  \item \textbf{Transparency mechanisms} make model confidence, extraction provenance, and aggregation logic visible and interrogable by non-technical users;
  \item \textbf{Multimodal access} ensures that knowledge-graph outputs are available not only as programmatic APIs and raw data files but as navigable visual interfaces with WCAG-compliant accessibility standards;
  \item \textbf{Cultural and linguistic inclusivity} is recognized as a structural requirement rather than a desirable addition---our pipeline's current English-language dominance (noted in \S\ref{sec:conclusion} as a corpus bias) is a limitation that future multilingual extraction capabilities must address.
\end{itemize}

The convergence of ResNei's neuro-informed collaborative environment, DeSci's decentralized governance models, FAIR-data interoperability, and citizen-science participation frameworks collectively describes the emerging infrastructure requirements for equitable, cognitively supportive, and community-governed scientific sensemaking. These are not peripheral concerns for computational meta-analysis but architectural prerequisites for systems that aspire to serve as living, trusted evidence ledgers for rapidly evolving scientific fields.

\FloatBarrier

## Pipeline Accessibility Checklist

The following checklist summarizes the concrete accessibility practices implemented in the figure-generation and rendering stages, mapped to the relevant Web Content Accessibility Guidelines (WCAG 2.1, Level AA) success criteria. ``Status'' is recorded as **Implemented**, **Partial**, or **Planned** based on the current state of the pipeline.

\begin{table}[H]
\centering
\caption{Accessibility practices implemented in the figure pipeline, mapped to WCAG 2.1 Level AA success criteria. Status reflects the current pipeline; ``Planned'' items are tracked in the project issue tracker.}
\label{tab:accessibility_checklist}
\small
\begin{tabular}{p{4.5cm} p{1.7cm} p{8.0cm}}
\toprule
\textbf{Practice} & \textbf{WCAG Ref.} & \textbf{Implementation} \\
\midrule
Colorblind-safe palette & 1.4.1 & Wong (2011) 8-colour palette enforced in all figures \citep{wong2011colorblind}; supports/contradicts/neutral encoded by both hue and luminance. \\
Minimum font size & 1.4.4 & 16\,pt floor enforced in figure-generation script; tick labels never fall below this threshold. \\
Sufficient contrast & 1.4.3 & Foreground/background contrast $\geq$ 4.5:1 for all text, $\geq$ 3:1 for large headings, validated programmatically. \\
Non-color encodings & 1.4.1 & Direction encoded by both color and pattern (solid / hatched / outlined) so that grayscale printing remains interpretable. \\
Alt text and figure captions & 1.1.1 & Each \texttt{\textbackslash includegraphics} is paired with a \texttt{\textbackslash caption} that describes the figure content, key axes, and main takeaway. \\
Consistent visual grammar & 3.2.4 & Domain colors, hypothesis ordering, and axis conventions are fixed across all figures by a single style module. \\
Progressive disclosure & 2.4.5 & Summary dashboards link to per-hypothesis and per-domain breakdowns; readers can choose depth of engagement. \\
Machine-readable outputs & 4.1.2 & All analytic results published as JSON / JSONL alongside PNG figures, enabling assistive-technology consumption. \\
Provenance metadata & 1.3.1 & Each nanopublication carries source DOI, extraction model, timestamp, and confidence; programmatically queryable. \\
Multilingual extraction & --- & \textbf{Planned}: current pipeline is English-only; future multilingual prompts and corpus expansion are tracked as a corpus-bias mitigation. \\
Per-assertion confidence UI & --- & \textbf{Planned}: aggregate scores currently dominate the dashboard; future iterations will surface per-assertion confidence and rationale. \\
\bottomrule
\end{tabular}
\end{table}

\FloatBarrier
