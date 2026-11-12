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
| `doc` | `doc` | Documentation hub (architecture, data formats, citation metadata, API reference, scripts, testing). |
| `CHANGELOG.md` | `doc` | Changelog. |

## Portable tasks

| Task | Command | Working directory | Description |
| --- | --- | --- | --- |
| `test` | `./run.sh test-full` | `.` | Run the coverage gate through the repository's single gate entry point. |

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
