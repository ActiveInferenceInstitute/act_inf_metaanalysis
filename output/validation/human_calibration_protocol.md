# Human calibration protocol

Schema version: `1.0`; deterministic queue seed: `42`.

Annotators independently label stance (`supports`, `contradicts`, `neutral`), evidence status, evidence type, source claim, and verbatim evidence quote from the supplied abstract. Do not use the pipeline label as a cue. Adjudicate disagreements before computing agreement, precision, recall, F1, quote fidelity, and uncertainty. Empty queues mean human annotation has not yet been supplied.
