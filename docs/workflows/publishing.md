# Publishing — act_inf_metaanalysis

The [Publishing group contract](https://github.com/ActiveInferenceInstitute/ActiveInferenceJournal/blob/d8ec888a8f3051a66bed9af047ee4b206050bdce/docs/workflows/publishing.md)
is canonical. This member does not redefine its identity grammar or mirror its
schema prose. The vendored [schema](record-identity.schema.json) and
[checker](../../scripts/gate/identity.py) are unchanged copies from that lead
revision. Upgrades replace the canonical bytes and their recorded digests together.

## Member integration

The portable commands live in [`../../.aii/config.yaml`](../../.aii/config.yaml)
under `tasks:`, matching the arms of [`../../run.sh`](../../run.sh). The docs task
names the [documentation index](../documentation-index.md), the render task names
the manuscript command and output root, and the GNN task names the
[parser pin](../../.github/gnn-pin.json).

The existing member gates already implement command dispatch, link and index
checks, measurements, and pinned GNN conformance. They remain in place under the
contract's instruction to retain existing proofs rather than duplicate them.
The docs arm additionally runs the canonical offline checker for every artifact
pinned below; no journal corpus or publication data is fabricated for this check.

## Pinned artifacts

```text
record-identity.schema.json  84f6c4df6efc3f15f0d8a9a05c8aabd0cbdc08b0f4feac5fcc8ae860a81e306b
identity.py  847328ff163fa90c869495164869caf4e83313748e8a444dbab8d4e459b11074
gnn-pin.json  eb83f7f1b73eb31e116bd05b1f457dd07e6874a2a4ba0e9e95e5bc91f094cd55
```

`./run.sh docs` invokes these checks from the member root:

```bash
python3 scripts/gate/identity.py --verify-copy docs/workflows/record-identity.schema.json
python3 scripts/gate/identity.py --verify-copy scripts/gate/identity.py
python3 scripts/gate/identity.py --verify-copy .github/gnn-pin.json
```

The member test arms are `./run.sh test-fast` and `./run.sh test-full`.
GitHub Actions is billing-locked; local runs are the gate.
