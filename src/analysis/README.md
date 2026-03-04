# Analysis Module

Bibliometric, temporal, and text-analytics pipeline for the Active Inference Meta-Analysis.

## Components

- **Topic Modeling (`topic_modeling.py`)**: NMF-based topic discovery from TF-IDF matrices.
- **Text Processing (`text_processing.py`)**: Tokenization, stopword removal, and vectorization.
- **Temporal Analysis (`temporal_analysis.py`)**: Calculates CAGR, doubling times, and growth trends over the corpus timespan.
- **Citation Network (`citation_network.py`)**: Constructs and analyzes networkx `DiGraph` relationships, computing PageRank and identifying communities.
- **Subfield Classifier (`subfield_classifier.py`)**: Keyword-based classification routing papers into the standard 8-category A/B/C taxonomy.

See [AGENTS.md](AGENTS.md) for technical specifics.
