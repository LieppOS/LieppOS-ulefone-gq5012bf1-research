# Ulefone Armor 29 Pro Thermal (GQ5012BF1) — research

Reverse-engineering evidence, bring-up history and audit tooling for the
**Ulefone Armor 29 Pro Thermal**, Android product `GQ5012BF1`, MediaTek MT6878.

This material used to live inside the LineageOS device tree. It is kept here so
the device tree itself stays a normal, lean LineageOS tree.

| Repository | Contents |
|---|---|
| [`android_device_ulefone_gq5012bf1`](https://github.com/LieppOS/android_device_ulefone_gq5012bf1) | the LineageOS 22.2 device tree |
| [`OrangeFox-Ulefone-GQ5012BF1`](https://github.com/LieppOS/OrangeFox-Ulefone-GQ5012BF1) | OrangeFox recovery overlay, packaging and releases |
| [`LieppOS-ulefone-gq5012bf1-research`](https://github.com/LieppOS/LieppOS-ulefone-gq5012bf1-research) | this one: evidence, analysis and audit tooling |

## Layout

```text
docs/                     per-subsystem hardware and evidence notes
reports/                  bring-up history, audits and remediation reports
tools/                    offline inventory and audit tooling
aosp-replaced-files.txt   stock paths owned by AOSP/ROM modules (audit input)
workspace/                local analysis workspace (gitignored, not published)
```

`workspace/` holds extracted stock partitions, live snapshots and generated
reports. It is large, contains vendor binaries, and is never committed.

## Tooling

See [`tools/README.md`](tools/README.md). The tools operate on a device tree
from the outside:

```bash
export DEVICE_TREE=~/android/lineage-22.2/device/ulefone/gq5012bf1

python3 tools/audit_device_tree.py \
  --device $DEVICE_TREE \
  --inventory workspace/gq5012bf1/reports/inventory \
  --stock-partitions workspace/gq5012bf1/stock/partitions \
  --out workspace/gq5012bf1/reports/device-tree-audit.md
```

Recovery-only invariants are audited only when the OrangeFox overlay is applied
to the device tree, or with `--recovery-tree <overlay checkout>`.

## Evidence hierarchy

Used consistently throughout `docs/` and `reports/`:

```text
Hardware topology:          live snapshots > stock firmware > DTB/inference
Android identity/version:   stock firmware > stock images/manifests > live properties
Security/product identity:  verified TrustKernel experiments > stock firmware > live properties
```

The live snapshots were captured on a KernelSU-patched device with a property
spoofing module active; `tools/snapshot_trust.py` classifies what each snapshot
may still be trusted for. Identity, version and attestation properties from
those snapshots are **not** authoritative.

## Status labels

```text
IDENTIFIED · CONFIGURED · BUILD-VALIDATED · RUNTIME-VALIDATED · UNKNOWN
```

Nothing in this repository upgrades a subsystem to RUNTIME-VALIDATED. Only an
observed test on hardware does.

## Open validation item

Auditing the Android 15 stock payload against an Android 14 recovery source
checkout leaves **27 unresolved required ELF dependencies**. All 27 are Android
15 AOSP `system/lib64` libraries that exist in the stock image but are not Soong
modules in an Android 14 checkout. This predates the device-tree restructuring
and must be re-evaluated against a real LineageOS 22.2 / Android 15 tree. Do not
"fix" it by inventing blobs.
