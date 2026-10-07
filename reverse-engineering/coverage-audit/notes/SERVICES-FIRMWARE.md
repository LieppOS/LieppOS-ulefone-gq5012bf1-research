# Axes 4–8: HAL, init, firmware, secure-world and boot/storage coverage

Audit date: 2026-10-07

## Evidence and reproducibility

The generated tables are built by `scripts/build-services.py` from metadata-only stock harvests under `audit-evidence/`:

- `raw-vintf.tsv`: every AIDL/HIDL/native interface declaration in the extracted manifests and compatibility matrices;
- `raw-legacy-hw.tsv`: every legacy `*/lib*/hw/android.hardware.*` backend library;
- `raw-init-services.tsv`: every parsed init service plus every executable launched by an `on` trigger;
- `raw-firmware.tsv`: firmware/calibration file metadata and firmware-bearing scatter payload metadata (path, byte count and SHA-256 only);
- `raw-partitions.tsv`: MTK scatter/ABOTA partition metadata;
- `pack-identity.tsv`: canonical component and status lookup.

No proprietary payload is copied into this repository. Coverage assignment is an ordered, curated exact/family mapping. Unknowns remain `E`; there is no generic fallback that silently hides an orphan.

## Measured inventory

| Axis | Rows | A | B | C | D | E |
|---|---:|---:|---:|---:|---:|---:|
| VINTF families + legacy HAL libraries | 272 | 69 | 126 | 74 | 1 | 2 |
| Init services + trigger executables | 253 | 10 | 120 | 118 | 3 | 2 |
| Firmware/calibration payloads | 80 | 45 | 30 | 4 | 1 | 0 |
| Secure-world surfaces | 13 | 5 | 1 | 5 | 2 | 0 |
| Scatter/ABOTA partition families | 61 | 20 | 40 | 1 | 0 | 0 |

The four `E` rows are not four independent gaps. They are two VINTF interfaces and two init services for the same uncovered active Mali GPU ownership scope:

- `vendor.mediatek.hardware.gpu`
- `vendor.mediatek.hardware.gpuserv`
- `vendor.gpuserv-default`
- `vendor.mali_platform-mediatek`

They converge with the three uncovered Mali modules and three uncovered GPU DT compatibles on one proposed component, `MALI-GPU-KERNEL`. The proprietary userspace and CSF firmware remain a vendor-blob boundary; the missing scope is ownership and reconstruction of the active kernel/DT platform contract.

## Important boundaries

- Compatibility-matrix-only declarations are framework requirements, not proof that the device provides an implementation. `hals-services.tsv` records manifest counts separately.
- AOSP/example services are retained as `C` or `D`, rather than being mistaken for phone-specific implementations.
- SCP, modem, connectivity, camera tuning, GPU firmware and secure-world images are represented but are not claimed source-reconstructable.
- Trigger-time init `exec` parsing resolves the first absolute executable path after optional uid/gid/seclabel arguments. This avoids fake artifacts named `-` or `--`.
- `secure-world.tsv` deliberately separates normal-world transport closure from signed TA/hypervisor source availability.
- `boot-storage.tsv` groups A/B slot pairs and does not create one RE component per partition.

## Reference-board / example findings

- `vendor.face-default` is the AOSP face example service with no matching face hardware (`D`).
- Camera P1 self-test and virtual-camera services remain diagnostic/reference baggage (`D`).
- The DOOGEE-named Morpho EIS calibration payload is carried-over reference-board tuning data (`D`), not evidence of an additional fitted camera.

## Rebuild

```sh
cd reverse-engineering/coverage-audit
python3 scripts/harvest-stock-artifacts.py
python3 scripts/build-services.py
```

The harvest script reads the local extracted stock tree; the builder itself is deterministic over the committed TSV evidence.
