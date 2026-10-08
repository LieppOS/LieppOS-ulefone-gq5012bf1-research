# HAL, init, firmware, secure-world and boot/storage coverage

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

Built from committed metadata-only raw TSVs and current curated ownership; no payload copied. Source availability, DT enablement and interface declaration are not runtime or parity proof.

## Measured inventory

| Axis | Rows | A | B | C | D | E |
|---|---:|---:|---:|---:|---:|---:|
| VINTF families + legacy HAL libraries | 272 | 69 | 128 | 74 | 1 | 0 |
| Init services + trigger executables | 253 | 10 | 105 | 114 | 24 | 0 |
| Firmware/calibration payloads | 80 | 45 | 32 | 2 | 1 | 0 |
| Secure-world surfaces | 13 | 5 | 1 | 5 | 2 | 0 |
| Scatter/ABOTA partition families | 61 | 20 | 40 | 1 | 0 | 0 |

GPU interface/service ownership is now MALI-GPU-KERNEL PARTIAL, not an E gap. CSF/APU/GPUEB/VCP binary algorithms are excluded; CCU algorithms remain camera HAL, with a separate ISP host owner. Firmware owner denotes the interface/retention boundary, never reconstructed remote internals. Loading claims are per-payload evidence to reconcile, not proof of a universal Linux loader.

Matrix declarations are framework requirements, not implementation proof. Twenty-two missing-executable non-trigger service groups remain reference baggage; virtual camera, face example and alternative fingerprint templates are not additional fitted hardware. DOOGEE-named EIS calibration remains reference tuning. A/B partition pairs are grouped, not new components. Secure-world/boot ownership is separate from accelerator host ABI.

Reproduce: `python3 scripts/build-services.py` then `python3 scripts/build-reports.py` from the coverage-audit directory. Raw stock harvests are preserved; no repeated hardware discovery required.
