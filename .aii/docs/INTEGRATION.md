# InstituteOS integration — act_inf_metaanalysis

## Identity

| Field | Value |
| --- | --- |
| Repository | `ActiveInferenceInstitute/act_inf_metaanalysis` |
| Affiliation | `institute` |
| Category | `publication` |
| Status | `active` |
| Maturity | `released` |
| Steward | Active Inference Institute |
| Default branch | `main` |
| Current release | — |
| License | `CC-BY-4.0` |
| Citation | Active Inference Institute — act_inf_metaanalysis. |

## Federation

| Setting | Value |
| --- | --- |
| Dashboard mode | `repos` |
| Analytics | `true` |
| Dashboard | `true` |
| Sync policy | `pull` |
| Registries | — |
| Tags | meta-analysis, computational, active-inference, tex |

## Ecosystem relations

| Repository | Relation | Note |
| --- | --- | --- |
| `ActiveInferenceInstitute/InstituteOS` | `referenced-by` | Federated via the InstituteOS .aii manifest. |
| `ActiveInferenceInstitute/Active_Inference_Ontology` | `references` | Uses Active Inference Ontology terms. |
| `ActiveInferenceInstitute/ActiveInferenceJournal` | `referenced-by` | Featured in Institute materials. |

## Key artifacts

| Path | Kind | Description |
| --- | --- | --- |
| `README.md` | `doc` | Repository overview. |
| `src` | `code` | Source tree. |
| `pyproject.toml` | `code` | Python package config. |
| `gnn` | `doc` | Illustrative GNN structural sketches for hypotheses H1, H4, and H8; documentation only, not evidence and not a pipeline input. |
| `act_inf_metaanalysis_v2.0.6_2026-07-26.pdf` | `publication` | Date-stamped validated PDF release artifact. |
| `output` | `publication-data` | Versioned data, figures, hydrated manuscript, reports, validation records, release packages, snapshots, and HTML/PDF build outputs. |
| `AGENTS.md` | `doc` | Agent guidance. |
| `LICENSE` | `doc` | License. |
| `CITATION.cff` | `citation` | Machine-readable citation metadata. |
| `tests` | `test` | Test suite. |
| `manuscript` | `publication` | Manuscript sources and artifacts. |
| `docs` | `doc` | Documentation hub (README, documentation index, generated gate receipt). |
| `doc` | `doc` | Long-form guides (architecture, data formats, citation metadata, API reference, scripts, testing). |
| `CHANGELOG.md` | `doc` | Changelog. |

## Portable tasks

| Task | Command | Working directory | Description |
| --- | --- | --- | --- |
| `lint` | `./run.sh lint` | `.` | Run the repository lint arm. |
| `types` | `./run.sh types` | `.` | Run the source type-checking arm. |
| `test-fast` | `./run.sh test-fast` | `.` | Run tests excluding the slow figure-generation selection. |
| `test-full` | `./run.sh test-full` | `.` | Run the full suite with the repository coverage gate. |
| `docs` | `./run.sh docs` | `.` | Check links, docs/documentation-index.md coverage, and Publishing artifact digests. |
| `gnn` | `./run.sh gnn` | `.` | Check illustrative sketches using the parser pinned in .github/gnn-pin.json. |
| `render` | `./run.sh render` | `.` | Render the manuscript via uv run python scripts/15_render_publication.py --output-root .render-check. |
| `all` | `./run.sh all` | `.` | Run the repository's blocking gate sequence. |
| `bench` | `./run.sh bench` | `.` | Measure the gate arms and regenerate docs/_generated/gate_arms.md. |

## Validation

```bash
python -m aii_platform.aii_sidecar.validate <repo> --completeness
python -m aii_platform.aii_sidecar docs <repo> --overwrite
python -m aii_platform.aii_sidecar.run <repo> --list
```

The sidecar is valid when `validate` prints `OK` and reports no missing artifact,
manifest, link, or declared-doc path. Completeness is a curation target, not a
runtime requirement.

## Data boundary

This sidecar carries metadata only. It does not grant execution permission, does not
replace the repository's own documentation, and must not be used to move private
content into a public repository. Task execution is limited to trusted checkouts.
