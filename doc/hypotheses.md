# Standard Hypotheses

**Repository:** [github.com/ActiveInferenceInstitute/act_inf_metaanalysis](https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis)

The meta-analysis tracks evidence for and against eight standard hypotheses drawn from the Active Inference literature. Each hypothesis represents a major claim that the field collectively evaluates through ongoing research. The current corpus size, paper-level coverage, and per-hypothesis assertion counts are reported in `output/data/assertion_summary.json` and the rendered manuscript; this document defines the hypotheses themselves rather than fixing a particular run's numbers.

## Identifier Cross-Reference

The eight hypotheses have three identifier forms used across different layers of the system:

| config.yaml key | Code identifier | RDF URI | Short name |
| --- | --- | --- | --- |
| `H1` | `FEP_UNIVERSALITY` | `http://activeinference.institute/ontology/H1_FEP_UNIVERSALITY` | FEP Universality |
| `H2` | `AIF_OPTIMALITY` | `http://activeinference.institute/ontology/H2_AIF_OPTIMALITY` | AIF Optimality |
| `H3` | `MARKOV_BLANKET_REALISM` | `http://activeinference.institute/ontology/H3_MARKOV_BLANKET_REALISM` | Markov Blanket Realism |
| `H4` | `PREDICTIVE_CODING` | `http://activeinference.institute/ontology/H4_PREDICTIVE_CODING` | Predictive Coding |
| `H5` | `SCALABILITY` | `http://activeinference.institute/ontology/H5_SCALABILITY` | Scalability |
| `H6` | `CLINICAL_UTILITY` | `http://activeinference.institute/ontology/H6_CLINICAL_UTILITY` | Clinical Utility |
| `H7` | `MORPHOGENESIS` | `http://activeinference.institute/ontology/H7_MORPHOGENESIS` | Morphogenesis |
| `H8` | `LANGUAGE_AIF` | `http://activeinference.institute/ontology/H8_LANGUAGE_AIF` | Language AIF |

- **config.yaml key** (H1–H8): used in `manuscript/config.yaml` `hypothesis_definitions` section and in manuscript text
- **Code identifier**: used in `src/knowledge_graph/hypothesis.py` (`STANDARD_HYPOTHESES`), `src/knowledge_graph/schema.py` (`DEFAULT_HYPOTHESIS_CATEGORIES`), and LLM prompt output
- **RDF URI**: used in `nanopublications.trig` RDF export and semantic web queries

## The Eight Hypotheses

### 1. FEP_UNIVERSALITY

**The Free Energy Principle applies universally to all self-organizing systems.**

The claim that the FEP is not merely a model of brain function but a fundamental principle governing any system that maintains its integrity against environmental perturbation. Supporting evidence comes from applications to biological, social, and physical systems. Contradicting evidence arises from arguments that the FEP is unfalsifiable or tautological.

### 2. AIF_OPTIMALITY

**Active inference is optimal for planning and decision-making.**

The claim that active inference agents, which select actions by minimizing expected free energy, perform at least as well as reinforcement learning agents on planning tasks while additionally providing uncertainty-aware exploration. Supporting evidence comes from benchmark comparisons. Contradicting evidence comes from tasks where RL methods significantly outperform AIF.

### 3. MARKOV_BLANKET_REALISM

**Markov blankets correspond to real physical boundaries in nature.**

The claim that the statistical construct of a Markov blanket maps onto actual physical boundaries separating systems from their environments (e.g., cell membranes, skin). Supporting evidence comes from biophysical modeling. Contradicting evidence comes from arguments that Markov blankets are inference artifacts with no necessary physical correlate. Bruineberg et al. (2022) formalize this critique by distinguishing *Pearl blankets* (epistemic tools in Bayesian networks) from *Friston blankets* (ontological boundaries in the FEP), while Sakthivadivel (2023) develops Bayesian mechanics to ground the latter on firmer mathematical footing.

### 4. PREDICTIVE_CODING

**The brain implements predictive coding as described by the FEP.**

The claim that cortical hierarchies operate by passing prediction errors upward and predictions downward, as formalized by the predictive processing framework. Supporting evidence comes from neuroimaging studies (fMRI, EEG) showing prediction error signals. Contradicting evidence comes from alternative explanations of the same neural data.

### 5. SCALABILITY

**Active inference scales to complex, high-dimensional tasks.**

The claim that AIF agents can handle real-world complexity comparable to state-of-the-art deep RL, including continuous control, high-dimensional observations, and long planning horizons. Supporting evidence comes from deep active inference implementations. Contradicting evidence comes from scalability limitations observed in practice. A landmark 2025 result — AXIOM (Heins et al.) — demonstrates that active inference with expanding object-centric world models outperforms DreamerV3 on the Gameworld 10k benchmark while using substantially smaller models, significantly narrowing the perceived scalability gap.

### 6. CLINICAL_UTILITY

**Active inference models have genuine clinical utility in psychiatry.**

The claim that computational psychiatry models based on active inference can inform diagnosis, prognosis, or treatment selection beyond their explanatory value. Supporting evidence comes from clinical studies using AIF-derived biomarkers. Contradicting evidence comes from the persistent gap between computational models and clinical practice.

### 7. MORPHOGENESIS

**The FEP explains morphogenesis and biological self-organization.**

The claim that developmental biology and morphogenetic processes can be modeled as collective free energy minimization. Supporting evidence comes from computational simulations of cell behavior. Contradicting evidence comes from the empirical sparsity of the biology domain (C5) and the speculative nature of current proposals. Heins et al. (2024, PNAS) extend the connection between surprise minimization and collective behavior, demonstrating that cohesion, milling, and directed motion emerge naturally from individual active inference agents — a result with implications for both biological self-organization and artificial swarm design.

### 8. LANGUAGE_AIF

**Language processing is best understood as active inference.**

The claim that language comprehension and production are predictive inference over hierarchical generative models of linguistic structure, and that this framing offers advantages over existing computational linguistics models (surprisal theory, noisy-channel models). Supporting evidence comes from eye-tracking and reading-time studies. Contradicting evidence comes from arguments that AIF provides no explanatory gain over existing models.

## Scoring Formula

For each hypothesis $H$, the citation-weighted evidence score is:

$$
\text{score}(H) = \frac{\sum_{a \in S(H)} w(a) - \sum_{a \in C(H)} w(a)}{\sum_{a \in A(H)} w(a)}
$$

where:

- $S(H)$ = set of supporting assertions for $H$
- $C(H)$ = set of contradicting assertions for $H$
- $A(H)$ = all assertions for $H$ (supporting + contradicting + neutral)
- $w(a) = \log(1 + \text{citations}(a)) \cdot \text{confidence}(a)$

### Score Range

| Score | Interpretation |
| --- | --- |
| +0.7 to +1.0 | Strong supporting evidence |
| +0.3 to +0.7 | Moderate supporting evidence |
| -0.3 to +0.3 | Balanced, insufficient, or contested evidence |
| -0.7 to -0.3 | Moderate contradicting evidence |
| -1.0 to -0.7 | Strong contradicting evidence |

### Design Rationale

**Logarithmic citation weighting** ensures that highly cited papers carry more influence while preventing any single paper from dominating the score. A paper with 1000 citations gets ~3x the weight of a paper with 10 citations, not 100x.

**Confidence weighting** allows assertions with higher extraction confidence to contribute more to the score. The validated extraction floor is `min_confidence: 0.6` — assertions below it are discarded during extraction (see `LLMConfig.min_confidence` and `manuscript/config.yaml`).

**Neutral assertions** appear in the denominator but not the numerator, acting as a dampening factor. A hypothesis with many neutral assertions and few directional ones will have a score closer to zero, reflecting evidential ambiguity rather than absence. In practice, a "neutral" assertion signifies that the NLP model successfully extracted an assertion related to the domain space, but mathematically determined it neither provided supporting momentum nor explicit denouncement. This serves to penalize highly-debated or poorly-formed hypotheses.

## Temporal Trends

The `temporal_trend` function computes the cumulative score at each year by including only assertions from papers published in that year or earlier. This reveals whether support for a hypothesis is:

- **Growing** --- score increases monotonically (e.g., PREDICTIVE_CODING as neuroimaging evidence accumulates)
- **Declining** --- score decreases as contradicting evidence mounts
- **Plateauing** --- score stabilizes as the community reaches informal consensus
- **Oscillating** --- score fluctuates as debates produce alternating waves of supporting and contradicting work

## Implementation

The scoring functions are in `src/knowledge_graph/hypothesis.py`:

```python
from knowledge_graph.hypothesis import (
    STANDARD_HYPOTHESES,   # Default 8 hypotheses (hardcoded fallback)
    HYPOTHESES,            # Active hypothesis set (config-driven)
    configure_hypotheses,  # Load from config.yaml
    score_hypothesis,
    score_all_hypotheses,
    temporal_trend,
)

# Optional: load hypotheses from config.yaml (otherwise defaults are used)
configure_hypotheses(Path("manuscript/config.yaml"))

# Score a single hypothesis — returns a float in [-1, 1]
score = score_hypothesis(assertions, "FEP_UNIVERSALITY")
print(f"Score: {score:+.3f}")

# Score all configured hypotheses — returns dict[str, float]
all_scores = score_all_hypotheses(assertions)
for h_id, score in all_scores.items():
    print(f"{h_id}: {score:+.3f}")

# Temporal trend — returns dict[int, float] mapping year to cumulative score
trend = temporal_trend(assertions, "FEP_UNIVERSALITY", papers)
for year, cumulative_score in trend.items():
    print(f"{year}: {cumulative_score:+.3f}")
```

> **Note:** Hypotheses can be customized via the `hypothesis_definitions` section in `manuscript/config.yaml`. If no config is provided, the 8 standard hypotheses are used as defaults.
>
> **How to Add a Custom Hypothesis:**
> You do NOT need to edit Python source code to introduce a novel hypothesis into the Knowledge Graph pipeline. Simply open `manuscript/config.yaml` and append an entry matching the following schema:
>
> ```yaml
> project_config:
>   hypothesis_definitions:
>     H9:
>       name: "An explicit theory"
>       description: "A highly specific, refutable string that the LLM will grade the paper against."
>       scope: "theoretical"
> ```
>
> Restart `03_build_knowledge_graph.py` with `--clear-assertions` to force a complete re-evaluation. Note that the H1–H8→code-identifier aliases in `src/manuscript/variables.py` are order-dependent; adding H9 requires extending that alias mapping and updating the manuscript's hypothesis tables.

---

## LLM Prompt Design

Each paper is assessed against all eight hypotheses in a single LLM call. The prompt consists of:

1. **System prompt** — defines the role ("scientific literature analyst"), the three-layer output contract (source claim → evidence supply → hypothesis triage), and valid field values (`direction`: `supports` | `contradicts` | `neutral` | `irrelevant`; `evidence_status`: `explicit_claim` | `mentions` | `no_evidence`; `evidence_type`: `theoretical` | `empirical` | `none`)
2. **User prompt** — contains the paper title, abstract, and a list of hypothesis IDs with descriptions

The expected output is a JSON array with one object per assessed hypothesis:

```json
[
  {
    "hypothesis_id": "FEP_UNIVERSALITY",
    "direction": "supports",
    "confidence": 0.85,
    "reasoning": "The paper provides formal proofs extending FEP...",
    "source_claim_text": "The paper claims...",
    "evidence_quote": "verbatim sentence from the abstract",
    "evidence_status": "explicit_claim",
    "evidence_type": "theoretical"
  }
]
```

The system prompt explicitly requests **no markdown fences** and **no commentary** to simplify parsing. The parser still handles fenced code blocks as a fallback.

---

## Confidence Calibration

Confidence values from the LLM undergo several processing steps:

1. **Clamping** — raw values are clamped to `[0.0, 1.0]`
2. **Irrelevant filtering** — assessments with `direction="irrelevant"` are discarded before scoring
3. **Citation weighting** — the scoring formula applies `log(1 + citations) × confidence`, so highly-cited papers exert proportionally larger influence
4. **Temperature setting** — the default `temperature=0.1` produces near-deterministic outputs, improving reproducibility across runs

These steps ensure that confidence scores behave as calibrated weights rather than raw probabilities.

---

## Failure Modes and Mitigations

| Failure Mode | Description | Mitigation |
| --- | --- | --- |
| Empty abstract | Paper has no abstract text | Skipped with debug log |
| Malformed JSON | LLM returns non-parseable output | Retry up to `max_retries` (default: 3) with exponential backoff |
| Hallucinated hypothesis ID | LLM invents a hypothesis ID | Validated against the known set; unknown IDs skipped |
| Invalid direction | LLM returns a direction not in the valid set | Skipped with debug log |
| Timeout | LLM does not respond within `timeout_seconds` | Retry with backoff; skip on exhaustion |
| Semantic drift | LLM conflates hypothesis meanings | Mitigated by explicit descriptions in the prompt and low temperature |
| Checkpoint corruption | Process killed during checkpoint write | Atomic write (`.tmp` + `rename`) prevents partial files |
