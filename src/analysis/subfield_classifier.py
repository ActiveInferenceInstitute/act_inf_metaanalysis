"""Keyword-based classification into Active Inference domains.

Maps papers to one of 8 domains organised in three tiers:
  A – Core Theory (A1 formal theory, A2 qualitative philosophy)
  B – Tools & Translation Methods
  C – Domains of Application (C1–C5)
based on keyword occurrence in title and abstract text.

The keyword definitions can be loaded from ``config.yaml``'s
``subfield_keywords`` section via :func:`load_subfields_from_config`,
making the classification fully config-driven.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from literature.models import Paper

logger = logging.getLogger(__name__)

# ── Default fallback (used when no config is supplied) ────────────────
# Classification priority:
#   1. Specific application domains (C1-C5) — checked first
#   2. Tools domain (B) — intermediate specificity
#   3. Formal theory (A1) — any paper with mathematical formalism
#   4. Qualitative philosophy (A2) — default for prose-based FEP/AIF papers
#
# A1 is deliberately broad: any paper with equations, theorems, proofs, or
# mathematical notation should be classified here. A2 is the catch-all for
# papers that discuss FEP/AIF conceptually without formal mathematical
# treatment. On arXiv, most papers will have some formalism, so A1 should
# dominate over A2 in practice.

DEFAULT_SUBFIELDS: dict[str, dict] = {
    "A1_formal": {
        "keywords": [
            # Mathematical structures and methods
            "category theory",
            "information geometry",
            "bayesian mechanics",
            "markov blanket",
            "stochastic",
            "langevin",
            "gauge theory",
            "path integral",
            "differential equation",
            "dynamical system",
            "fixed point",
            "convergence",
            "ergodic",
            "measure theory",
            "manifold",
            "lie group",
            # Formal reasoning indicators
            "theorem",
            "proof",
            "lemma",
            "corollary",
            "proposition",
            "derivation",
            "formalism",
            "formulation",
            "analytical",
            # Variational and optimization formalism
            "variational inference",
            "variational bound",
            "kl divergence",
            "kullback-leibler",
            "elbo",
            "evidence lower bound",
            "laplace approximation",
            "mean field",
            "message passing",
            "belief propagation",
            "expectation propagation",
            # Statistical mechanics and physics formalism
            "partition function",
            "hamiltonian",
            "lagrangian",
            "entropy production",
            "fluctuation theorem",
            "ito",
            "fokker-planck",
            "helmholtz",
            # Probability and inference formalism
            "posterior",
            "prior",
            "likelihood",
            "marginal",
            "conjugate",
            "sufficient statistic",
            "exponential family",
            "dirichlet",
            "state space model",
            # Mathematical notation indicators
            "equation",
            "matrix",
            "eigenvalue",
            "jacobian",
            "hessian",
            "gradient descent",
            "optimization",
            "objective function",
            "loss function",
        ],
        "description": "A1: Quantitative and formal mathematical theory",
        "priority": 3,  # Lower priority than C/B (checked after specific domains)
    },
    "A2_philosophy": {
        "keywords": [
            # Genuinely philosophical and qualitative terms
            "phenomenology",
            "epistemology",
            "ontology",
            "enactivism",
            "4e cognition",
            "embodied cognition",
            "extended mind",
            "predictive processing",
            "bayesian brain",
            "ecological psychology",
            "affordance",
            "niche construction",
            "autopoiesis",
            "sense-making",
            "consciousness",
            "qualia",
            "intentionality",
            "teleology",
            "reductionism",
            "emergence",
            "self-organization",
            "autonomy",
            "agency",
            "normativity",
            "naturalism",
            # General FEP/AIF terms (catch-all when no specific domain matches)
            "free energy principle",
            "active inference",
            "generative model",
        ],
        "description": "A2: Qualitative philosophy and general FEP theory",
        "priority": 4,  # Lowest priority — catch-all
    },
    "B_tools": {
        "keywords": [
            "planning",
            "reinforcement learning",
            "deep active inference",
            "neural network",
            "amortized",
            "scalable",
            "monte carlo",
            "tree search",
            "benchmark",
            "implementation",
            "library",
            "software",
            "framework",
            "toolkit",
            "open source",
            "api",
            "algorithm",
            "gymnasium",
            "environment",
        ],
        "description": "B: Tools and translation methods development",
        "priority": 2,
    },
    "C1_neuroscience": {
        "keywords": [
            "neural",
            "cortical",
            "hippocampal",
            "eeg",
            "fmri",
            "neuroimaging",
            "synaptic",
            "dopamine",
            "spiking",
            "prefrontal",
            "basal ganglia",
            "cerebellum",
            "thalamus",
            "electrophysiology",
            "meg",
            "bold",
            "brain imaging",
            "neuron",
            "dendrit",
        ],
        "description": "C1: Computational and systems neuroscience",
        "priority": 1,
    },
    "C2_robotics": {
        "keywords": [
            "robot",
            "sensorimotor",
            "motor control",
            "embodied",
            "navigation",
            "manipulation",
            "actuator",
            "simulator",
            "gazebo",
            "ros ",
            "control loop",
            "pid",
            "end effector",
            "gripper",
        ],
        "description": "C2: Robotics and embodied agents",
        "priority": 1,
    },
    "C3_language": {
        "keywords": [
            "language",
            "linguistic",
            "speech",
            "semantic",
            "reading",
            "communication",
            "natural language",
            "syntax",
            "morphology",
            "phonology",
            "discourse",
            "pragmatics",
            "transformer",
            "large language model",
            "llm",
            "tokeniz",
        ],
        "description": "C3: Language processing and communication",
        "priority": 1,
    },
    "C4_psychiatry": {
        "keywords": [
            "psychiatric",
            "schizophrenia",
            "depression",
            "autism",
            "anxiety",
            "psychosis",
            "computational psychiatry",
            "clinical",
            "disorder",
            "diagnosis",
            "symptom",
            "patient",
            "therapy",
            "treatment",
            "mental health",
            "ptsd",
            "ocd",
            "bipolar",
            "addiction",
        ],
        "description": "C4: Computational psychiatry and clinical applications",
        "priority": 1,
    },
    "C5_biology": {
        "keywords": [
            "morphogenesis",
            "cell",
            "organism",
            "evolution",
            "life",
            "autopoiesis",
            "biological",
            "developmental",
            "gene",
            "protein",
            "metabolism",
            "homeostasis",
            "ecological",
            "phenotype",
            "genotype",
            "fitness",
            "adaptation",
            "species",
        ],
        "description": "C5: Biology and morphogenesis",
        "priority": 1,
    },
}

# Module-level active subfields (overridden by configure_subfields)
SUBFIELDS: dict[str, dict] = dict(DEFAULT_SUBFIELDS)


def load_subfields_from_config(config_path: Path) -> dict[str, dict]:
    """Load subfield keyword definitions from a YAML config file.

    Reads the ``subfield_keywords`` section of the config and constructs
    a SUBFIELDS-compatible dict. Falls back to ``DEFAULT_SUBFIELDS`` if
    the section is missing or the file cannot be read.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        Dictionary mapping subfield name to keyword/description dict.
    """
    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML not available; using default subfields")
        return dict(DEFAULT_SUBFIELDS)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as exc:
        logger.warning("Cannot read config %s: %s; using defaults", config_path, exc)
        return dict(DEFAULT_SUBFIELDS)

    subfield_kw = data.get("subfield_keywords")
    if not subfield_kw or not isinstance(subfield_kw, dict):
        logger.info("No subfield_keywords in config; using defaults")
        return dict(DEFAULT_SUBFIELDS)

    result: dict[str, dict] = {}
    # Default priority assignment based on field name prefix
    _priority_map = {
        "C": 1,  # Application domains — most specific
        "B": 2,  # Tools — intermediate
        "A1": 3, # Formal theory
        "A2": 4, # Philosophy catch-all
    }
    for name, keywords in subfield_kw.items():
        if isinstance(keywords, list):
            # Determine priority from field name prefix
            priority = 4  # default catch-all
            for prefix, prio in _priority_map.items():
                if name.startswith(prefix):
                    priority = prio
                    break
            result[name] = {
                "keywords": keywords,
                "description": name.replace("_", " ").title(),
                "priority": priority,
            }
        else:
            logger.warning("Skipping non-list subfield entry: %s", name)

    if not result:
        logger.warning("Config subfield_keywords was empty; using defaults")
        return dict(DEFAULT_SUBFIELDS)

    logger.info(
        "Loaded %d subfield definitions from config: %s",
        len(result),
        list(result.keys()),
    )
    return result


def configure_subfields(config_path: Optional[Path] = None) -> dict[str, dict]:
    """Set the module-level SUBFIELDS from config or defaults.

    Call this before classification to ensure the correct keyword set
    is active. If *config_path* is provided, keywords are loaded from
    the YAML file; otherwise ``DEFAULT_SUBFIELDS`` is used.

    Args:
        config_path: Optional path to the YAML config file.

    Returns:
        The active SUBFIELDS dict.
    """
    global SUBFIELDS
    if config_path is not None:
        SUBFIELDS = load_subfields_from_config(config_path)
    else:
        SUBFIELDS = dict(DEFAULT_SUBFIELDS)
    return SUBFIELDS


def _get_default_field() -> str:
    """Return the default field name for unclassified papers.

    Uses the first field whose key starts with 'A' that contains
    philosophy-related keywords, or simply the first field.
    """
    # Find the philosophy/general theory field (the catch-all)
    for name, info in SUBFIELDS.items():
        kws = [k.lower() for k in info.get("keywords", [])]
        if "free energy principle" in kws or "active inference" in kws:
            return name
    # Fallback: first field
    return next(iter(SUBFIELDS))


def classify_paper(paper: Paper) -> str:
    """Classify a paper into a domain by priority-aware keyword matching.

    Uses a two-pass strategy:
      1. Score all fields by keyword match count.
      2. Among fields with matches, prefer those with higher specificity
         (lower priority number). Within the same priority tier, the
         field with the most keyword matches wins.

    This ensures that specific application domains (C1-C5, priority 1)
    are preferred over tools (B, priority 2), which is preferred over
    formal theory (A1, priority 3), which is preferred over the
    qualitative philosophy catch-all (A2, priority 4).

    If no keywords match at all, returns the default field (A2).

    Args:
        paper: Paper object to classify.

    Returns:
        Domain name string (e.g. ``"A1_formal"``, ``"C2_robotics"``).
    """
    text = (paper.title + " " + paper.abstract).lower()

    default_field = _get_default_field()

    # Score every field
    scores: list[tuple[int, int, str]] = []  # (priority, -count, name)
    for field_name, field_info in SUBFIELDS.items():
        count = 0
        for keyword in field_info["keywords"]:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                count += 1
        if count > 0:
            priority = field_info.get("priority", 4)
            scores.append((priority, -count, field_name))

    if not scores:
        return default_field

    # Sort by (priority ASC, -count ASC i.e. highest count first)
    scores.sort()
    return scores[0][2]


def classify_corpus(
    papers: list[Paper],
    config_path: Optional[Path] = None,
) -> dict[str, list[Paper]]:
    """Classify all papers in a corpus into domains.

    If *config_path* is provided, subfield keywords are loaded from
    the config file before classification.

    Args:
        papers: List of Paper objects to classify.
        config_path: Optional path to YAML config with
            ``subfield_keywords`` section.

    Returns:
        Dictionary mapping domain name to list of papers
        assigned to that domain.
    """
    if config_path is not None:
        configure_subfields(config_path)

    result: dict[str, list[Paper]] = {name: [] for name in SUBFIELDS}

    for paper in papers:
        field = classify_paper(paper)
        result[field].append(paper)

    return result
