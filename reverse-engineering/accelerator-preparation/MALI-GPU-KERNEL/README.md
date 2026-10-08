# MALI-GPU-KERNEL — closure (2026-10-08, static)

Status: DONE

- **Subsystem:** Accelerators / Mali GPU (Valhall CSF, DDK r44p1) + MediaTek GED, GPU HAL, GPU QoS, gpufreq v2
- **Stock artifact:** the 8 vendor_dlkm modules `mali_kbase_mt6878_r44`, `mali_mgm_mt6878_r44`,
  `mali_prot_alloc_mt6878_r44`, `ged`, `mtk_gpu_hal`, `mtk_gpu_qos`,
  `mtk_gpufreq_wrapper`, `mtk_gpufreq_mt6878` (unsigned; sha256 in `stock-baseline.tsv`)
- **Result:** every module is rebuilt from pinned public source. Two genuinely clean builds
  are bit-identical (B1 == B2). Against stock, each stripped module is the same size with
  the same section layout:

| module | functions identical | data objects identical | sections identical | imports / exports / KCFI | residue |
|---|---|---|---|---|---|
| mtk_gpu_hal | 46/46 | 52/52 | 34/35 | 10/10 · 44/44 · 0/0 | build-id |
| mtk_gpu_qos | 12/12 | 22/22 | 43/44 | 32/32 · 4/4 · 4/4 | build-id |
| mtk_gpufreq_wrapper | 93/93 | 70/70 | 59/60 | 69/69 · 40/40 · 5/5 | build-id |
| mtk_gpufreq_mt6878 | 39/39 | 49/49 | 41/42 | 31/31 · 0/0 · 0/0 | build-id |
| ged | 666/666 | 756/756 | 58/59 | 230/230 · 100/100 · 9/9 | build-id |
| mali_mgm_mt6878_r44 | 58/58 | 34/34 | 44/45 | 43/43 · 0/0 · 3/3 | build-id |
| mali_prot_alloc_mt6878_r44 | 8/8 | 17/17 | 38/39 | 16/16 · 0/0 · 0/0 | build-id |
| mali_kbase_mt6878_r44 | 1826/1826 | 672/673 (`srcversion` string) | 68/70 | 443/443 · 145/145 · 98/98 | build-id + `srcversion` |

Function counts are STT_FUNC symbol-table entries, with same-named statics counted
separately. All relocations (semantic and raw) are identical.

**Residue, both mechanically explained provenance:**
* the 20-byte GNU build-id, which hashes build-host DWARF paths;
* kbase `srcversion`, an MD4 of source text. Every compiled byte is identical; the stock
  text (MTK rc-V10.29) is unpublished and differs only in text this configuration does not
  compile.

## Where things are

In the workspace pack, top-level research files are under `notes/`.

| topic | file |
|---|---|
| donors, revisions, how they were found | `source-lineage.md` |
| toolchain, flags, one-command B1/B2 | `build-reproduction.md`, `scripts/build_b1_b2.sh` |
| machine-readable ledgers | `stock-baseline.tsv`, `function-parity.tsv`, `data-parity.tsv`, `parity/acceptance/{section,abi,relocation}-parity.tsv`, `residue.tsv`, `consumer-edges.txt` |
| ABI / KMI / KCFI, natural provider CRCs | `abi-kmi-parity.md`, `parity/external-provider-natural-crc.tsv` |
| relocations / sections / modinfo | `relocation-parity.md` |
| DT, IRQ, supplies, OPP, binding evidence | `dt-hardware-contract.md` |
| power, DVFS, GPUEB IPI, thermal | `gpu-power-management.md` |
| `/dev/mali0` ioctls, `/proc/ged` bridge, sysfs | `userspace-kernel-abi.md`, `abi/kbase-ioctls.tsv` |
| CSF and GPUEB firmware | `firmware-boundary.md` |
| OEM/board deltas (none in code) | `board-specific-deltas.md` |
| corrected preparation claims | `stale-claims.md` |
| source patches (git format-patch over pristine archives) | `patches/kdm/`, `patches/gpu/`, `parity/source-manifest.tsv` |
| srcversion tooling and search | `scripts/srcversion.py`, `tools/sv/`, `scripts/sv_search*.py`, `parity/srcversion-search.txt` |
| full report | `FINAL-REPORT.md` |

**Outside this component** (retained, with explicit boundaries):
* the Mali userspace blobs, `mali_csffw.bin`, GPUEB firmware and the `gpueb.ko` host
  (GPU-AI-AUX-KERNEL-INTERFACES);
* secure memory (TMEM-FFA / TKCORE-DRV / GZ);
* `mtk_gpu_power_throttling` (THERMAL-POWER-HAL);
* runtime validation on hardware.

The preparation-pass files (`CLAUDE-HANDOFF.md`, `RE-PLAN.md`, `functions.tsv`,
`imports.tsv`, …) are retained as history. `stale-claims.md` lists what they got wrong.
