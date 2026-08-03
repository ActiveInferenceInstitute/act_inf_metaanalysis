# Security Policy

## Reporting a vulnerability

This is a public research repository for the Active Inference Institute. If you
discover a security issue (for example: credential leakage, unsafe handling of
API keys, or a supply-chain concern in the tooling registry), please report it
privately via **GitHub's private vulnerability reporting**:

<https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis/security/advisories/new>

Please include:

- the affected file(s) and version,
- a minimal description of the issue,
- any suggested mitigation, and
- whether the issue is already public.

Do **not** open a public issue for an active vulnerability.

## What this repository does not contain

- No production credentials. API keys are read from environment variables
  (`SEMANTIC_SCHOLAR_API_KEY`); never commit secrets to this repository.
- No deployed services. This is a batch data pipeline; there is no live
  server, database, or user-facing endpoint to protect.

## Supported versions

Security fixes land on `main` and are released with the next versioned
snapshot. The `output/` tree is a generated publication artifact: treat
`src/` and `scripts/` as the source of truth for code review.
