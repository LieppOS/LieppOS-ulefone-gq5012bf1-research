# GQ5012BF1 reverse-engineering coverage audit

Audit date: 2026-10-07

This directory is the reproducible coverage database behind [`../index.md`](../index.md).

## Verdict

**NEAR-COMPLETE:** one confirmed ownership gap (`MALI-GPU-KERNEL`), no unresolved possible gap meeting the component threshold.

## Reports

- [SUMMARY.md](SUMMARY.md) — measured verdict and explicit answers
- [PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md) — all 45 PARTIAL components, A–F
- [MISSING-COVERAGE.md](MISSING-COVERAGE.md) — confirmed/possible/not-missing/generic
- [PORT-READINESS.md](PORT-READINESS.md) — seven target readiness views
- [PROPOSED-CHANGES.md](PROPOSED-CHANGES.md) — reviewable taxonomy migration plan
- [notes/MANIFEST-HYGIENE.md](notes/MANIFEST-HYGIENE.md) — separate pack/manifest drift result

## Machine-readable tables

- `components.tsv` — 133 canonical components
- `artifact-map.tsv` — 2952 normalized artifacts across axes 1–10
- `kernel-modules.tsv` — 457 modules
- `device-tree.tsv` — 580 compatibles / 930 nodes
- `hardware.tsv` — 44 physical/absence/reference rows
- `hals-services.tsv` — 272 VINTF/legacy-HAL rows
- `vendor-services.tsv` — 253 init service/trigger-exec rows
- `firmware.tsv` — 80 metadata-only payload rows
- `secure-world.tsv` — 13 security boundaries
- `boot-storage.tsv` — 61 partition families
- `android-integration.tsv` — 654 stock/current integration files
- `userspace-libraries.tsv` — 538 significant library basenames

## Coverage classes

A dedicated component; B broader component; C generic/no dedicated RE; D dead/reference; E unmapped.

## Rebuild order

```sh
python3 scripts/harvest-pack-identity.py
python3 scripts/harvest-pack-module-claims.py
python3 scripts/harvest-pack-dt-claims.py
python3 scripts/harvest-pack-artifact-claims.py
python3 scripts/harvest-stock-artifacts.py
python3 scripts/harvest-integration.py
python3 scripts/build-kernel-modules.py
python3 scripts/build-devicetree.py
python3 scripts/build-hardware.py
python3 scripts/build-services.py
python3 scripts/build-integration.py
python3 scripts/build-components.py
python3 scripts/build-reports.py
python3 scripts/check-audit.py
```

`check-audit.py` is the fail-closed quality gate: it re-derives every universe total, coverage tally, orphan-class count, component-set equality with the canonical workspace folders, per-component research path existence and every relative link in the generated Markdown, and exits non-zero on any drift.

Harvesters read private/local stock and workspace trees; committed evidence contains metadata/textual claims only. No proprietary firmware/library payload is copied here.
