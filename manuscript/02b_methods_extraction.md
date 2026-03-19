# LLM-Based Assertion Extraction: Prompt Design, Error Taxonomy, and Validation \label{sec:extraction_pipeline}

_This supplementary section documents the implementation specifics of the LLM-based assertion extraction pipeline._

## Relationship to Prior Approaches

The closest prior effort is the systematic literature analysis of Knight, Cordes, and Friedman \citep{knight2022fep}, which used human annotators to manually code structural, visual, and mathematical features of FEP and Active Inference publications. Their work operated at the scale of hundreds of annotated papers and employed terms from the Active Inference Institute's Active Inference Ontology for automated text analysis. Our pipeline replaces the manual coding step with LLM-based assertion extraction, enabling scalable processing of the full corpus ($N = {{CORPUS_SIZE}}$ papers) at the cost of exchanging human-verified precision for machine-generated assessments that require post-hoc validation. This trade-off is characteristic of the broader LLM-based scientific extraction landscape: recent benchmarking confirms that even state-of-the-art modular extraction architectures fall short of production-level precision---particularly on tasks requiring exhaustive retrieval and aggregation of multiple values from long documents---validating our design choice to retain human review pathways alongside automated extraction.

| Dimension | Knight et al. (2022) | This work |
|-----------|---------------------|-----------|
| **Scale** | Hundreds of papers | {{CORPUS_SIZE}} papers |
| **Annotation** | Manual (structural/visual/math features) | Automated (LLM hypothesis assessment) |
| **Ontology** | Active Inference Ontology terms | 8 standard hypotheses |
| **Output** | Annotated features + term frequencies | Nanopublications + knowledge graph |
| **Reproducibility** | Annotator-dependent | Deterministic (given model + seed) |
| **Precision** | High (human-verified) | Medium (requires validation) |

### Positioning in the LLM-Based Review Landscape

Our pipeline operates within a rapidly maturing ecosystem of LLM-powered literature analysis tools. Multi-agent architectures such as LitLLM decompose the review process into specialized sub-agents (planner, identifier, extractor, compiler), while ensemble approaches aggregate outputs from multiple LLMs via weighted voting to improve reliability. Our work differs from these tools in three respects: (1) we target _hypothesis-level evidence scoring_ rather than inclusion/exclusion screening; (2) we produce structured nanopublications rather than narrative summaries; and (3) we operate on abstracts rather than full texts—a deliberate trade-off that enables corpus-scale processing ($N = {{CORPUS_SIZE}}$) at the cost of missing fine-grained claims embedded in method sections or discussion paragraphs. Full-text processing could improve extraction recall, particularly for hypotheses with small evidence bases (H6 Clinical Utility, H7 Morphogenesis).

## Prompt Engineering and Schema Design

The structured prompt is designed to minimize parsing failures and maximize assessment quality:

1. **Explicit JSON schema.** The prompt specifies the exact output schema—field names, allowed direction values, and the numeric confidence range—reducing the LLM's tendency to generate free-form text or ad hoc structures.

2. **Hypothesis definitions in-context.** All eight definitions are included verbatim, ensuring the LLM assesses relevance from the provided context rather than relying on parametric knowledge that may be stale.

3. **Reasoning field.** Each assessment includes a natural-language reasoning string, providing an audit trail for human reviewers and enabling systematic analysis of error patterns.

4. **Irrelevant filtering.** An explicit "irrelevant" direction allows the LLM to mark hypotheses that a paper does not address, avoiding forced spurious assessments.

### Prompt Template

The extraction prompt follows a two-part structure (system + user):

```text
SYSTEM: You are a scientific literature analyst specializing in the
Free Energy Principle and Active Inference. Assess the relevance of
the given paper to each hypothesis. Return a JSON array.

USER:
Paper: {title}
Abstract: {abstract}

Hypotheses:
H1: FEP Universality — {description}
H2: AIF Optimality — {description}
...
H8: Language AIF — {description}

For each hypothesis, return:
{
  "hypothesis_id": "H1",
  "direction": "supports|contradicts|neutral|irrelevant",
  "confidence": 0.0-1.0,
  "reasoning": "..."
}
```

The extraction module (`src/knowledge_graph/llm_extraction.py`) includes configurable retry logic with exponential backoff, JSON parsing with handling of markdown code fences and extraneous text, confidence clamping, and validation against the hypothesis ID set. The default model is `gemma3:4b` on a local Ollama instance, configurable via `--llm-model` and `--llm-url` flags.

## Failure Modes and Error Recovery

The primary failure modes are documented below.

### Over-Extraction Bias

Approximately 15--20\% of assessments in preliminary experiments exhibit over-extraction: the LLM attributes claims to a paper that merely mentions a hypothesis without taking a position. This is the most common error mode and produces false supporting evidence. Over-extraction disproportionately affects broad-scope hypotheses (H1 FEP Universality, H2 AIF Optimality) where most papers in the corpus contain relevant terminology without explicitly endorsing the claim. Narrower hypotheses tied to specific domains (H7 Morphogenesis, H8 Language AIF) show lower over-extraction rates because their vocabulary is more distinctive. This systematic bias inflates support counts for broad hypotheses, and we caution against interpreting absolute scores for H1 and H2 without accounting for this effect.

### Direction Misclassification

The LLM misclassifies a contradicting claim as supporting, or vice versa. Rarer but more consequential, as it directly inverts the evidence signal. Most common for papers that discuss limitations while ultimately endorsing a hypothesis.

### Confidence Calibration Constraints

The model occasionally assigns high confidence to assessments where the underlying evidence is ambiguous. Reliable confidence calibration remains an open problem for zero-shot LLM applications, motivating the multi-tiered validation protocols described below.

### Progressive JSON Parsing Recovery

To mitigate formatting inconsistencies, the module implements a progressive parsing pipeline to recover malformed LLM outputs:

1. **Direct parse**: Attempt `json.loads()` on the raw response.
2. **Strip code fences**: Remove Markdown `` ```json ... ``` `` wrappers and retry.
3. **Extract JSON array**: Scan for the first `[...]` substring in the response text.
4. **Individual recovery**: If a valid array contains malformed elements, parse each element independently.

Papers that fail all parsing stages are logged and skipped; their count is reported at pipeline completion.

## Validation Methodology

Validation of LLM-extracted assertions follows a three-tier protocol:

1. **Spot-check validation.** A random sample of 50 papers has been reviewed by a domain expert, comparing LLM assessments against human judgments for direction accuracy and confidence appropriateness. In this sample, direction agreement (supports/contradicts/neutral) between LLM and human annotator exceeds 80\%, with the majority of disagreements arising from the over-extraction bias described above rather than direction inversion.

2. **Boundary-case audit.** Papers known to make contested claims (e.g., critiques of FEP universality, Markov blanket realism debates) are specifically checked for correct direction assignment.

3. **Aggregate consistency.** Hypothesis scores are compared against qualitative expectations from the literature: hypotheses known to be well-supported (e.g., H4 Predictive Coding) should score positively; those known to be contested (e.g., H3 Markov Blanket Realism) should show lower or mixed scores.

Preliminary experiments on a sampled subset of Active Inference papers—evaluated across GPT-4 and Claude-family models—suggest that this automated approach reduces human annotation time by approximately 60--70\% compared to purely manual extraction. Both over-extraction biases and direction inversion errors are intercepted by human review at acceptable rates. We note that recent benchmarking of LLMs on structured scientific claim extraction reports "extremely low" exact-match accuracy \citep{liang2024survey}, underscoring that our multi-tier validation protocol—rather than raw LLM output—is the operative quality control mechanism. The pipeline supports model upgrades without code changes: swapping the underlying model requires only adjusting the `--llm-model` flag.

## From Assertions to Nanopublications

Each validated assertion is wrapped in a **nanopublication** \citep{groth2010anatomy, kuhn2016decentralized}—a self-contained, machine-readable knowledge unit packaging the assertion with explicit provenance metadata. The wrapping process assigns:

- A **unique identifier** (`nanopub:<uuid12>`) for graph-level deduplication.
- An **attribution string** recording the pipeline name and LLM model version.
- A **UTC timestamp** in ISO 8601 format, establishing temporal provenance.

Nanopublications are persisted **incrementally** during extraction. Every 50 papers (configurable via `--checkpoint-interval`), the pipeline atomically appends newly extracted nanopublications to `nanopublications.jsonl` using a temporary-file-plus-rename strategy that prevents corruption on interruption. Deduplication operates on the composite key $(paper\_id, hypothesis\_id)$: when a paper is re-processed with an improved model, the newer assertion overwrites the stale entry. This merge-on-add design enables iterative model refinement without costly full-corpus re-extraction.

After extraction completes, the full nanopublication set is additionally serialized to **RDF/TriG** format per the nanopublication standard, producing four named graphs per nanopublication (Head, Assertion, Provenance, Publication Info). The TriG output is suitable for publication to the decentralized nanopublication network and archival on data repositories such as Zenodo. The complete RDF schema is specified in the \hyperref[sec:methods_kg]{knowledge graph methodology} and \hyperref[sec:appendix_rdf]{Appendix~A.5}.
