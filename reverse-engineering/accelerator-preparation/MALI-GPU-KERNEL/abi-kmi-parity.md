# ABI / KMI parity — MALI-GPU-KERNEL (measured)

**Comparison:** stock vs clean build B1, stripped. **Ledger:** `parity/acceptance/abi-parity.tsv`
(one row per symbol, CRC, KCFI ID or modinfo key). **Script:** `scripts/mali_acceptance.py`.

| module | imports (name+CRC) | exports (name+bucket+CRC) | KCFI `__kcfi_typeid_*` | `.modinfo` keys |
|---|---|---|---|---|
| mtk_gpu_hal | 10/10 | 44/44 | 0/0 | 6/6 |
| mtk_gpu_qos | 32/32 | 4/4 | 4/4 | 6/6 |
| mtk_gpufreq_wrapper | 69/69 | 40/40 | 5/5 | 6/6 |
| mtk_gpufreq_mt6878 | 31/31 | 0/0 | 0/0 | 6/6 |
| ged | 230/230 | 100/100 | 9/9 | 9/9 |
| mali_mgm_mt6878_r44 | 43/43 | 0/0 | 3/3 | 8/8 |
| mali_prot_alloc_mt6878_r44 | 16/16 | 0/0 | 0/0 | 8/8 |
| mali_kbase_mt6878_r44 | 443/443 | 145/145 | 98/98 | 10/11 (`srcversion`, see source-lineage.md) |

**Totals:** 874 imports, 333 exports and 119 KCFI type IDs, all identical. The `__versions`
sections are byte-identical, which covers CRC, name and order. `vermagic`, `name`,
`depends`, `license`, `author`, `description`, `version`, `import_ns=DMA_BUF`, aliases and
`parm*` are all identical.

## The CRCs are natural, not copied

* **GKI imports.** CRCs come from the vendor kout `Module.symvers`, i.e. genksyms over GKI
  `6b18f0b574ab` with the stock vendor config.
* **Imports between owned modules.** CRCs come from the natural kdm build
  (`B1/kdm.Module.symvers`).
* **The 30 external-provider imports** (aee_aed, emi, irq-dbg, mrdump, mtk_sec_heap,
  tmem_ffa, tinysys-scmi, gpueb, mtk_tinysys_ipi, sspm_v3, system_heap, mediatek-drm,
  mtk_qos, mtk_pbm, device-apc-common):
  * `scripts/derive_provider_crcs.sh` compiles the whole public ALPS 5e41 device-module tree
    and reads genksyms' `#SYMVER` records.
  * **30/30 equal the CRCs the stock providers publish in their `__kcrctab`**
    (`parity/external-provider-natural-crc.tsv`).
  * The B1/B2 build uses these natural CRCs (`symvers/natural-external-provider.symvers`).
    The stock-extracted record is kept only as a cross-check; the two files are
    byte-identical.

**Consumer side:** I scanned all 457 stock modules (vendor_dlkm, vendor_boot ramdisks and
system_dlkm). Every stock consumer of an owned export imports it with a CRC equal to the
reconstruction's natural export CRC; there are 0 mismatches
(`parity/acceptance/consumer-edges.txt`). External consumers are:
* met_gpu_api and met_gpu_adv_api (mtk_gpu_hal);
* mtk_fpsgo and mtk_mbraink (ged, gpufreq_wrapper);
* mtk-swpm-dbg-common-v1;
* mtk_cg_peak_power_throttling;
* mtk_gpu_power_throttling (`gpufreq_set_limit`);
* thermal_interface (`gpufreq_get_freq_by_idx`);
* mtk_perf_common and trace_mmstat.

## KCFI

* **Indirect-call type hashes.** On arm64 KCFI places the callee type hash in the 4 bytes
  before each function and the check constants inline in callers. Both live in `.text*`,
  which is byte-identical for all modules (`parity/acceptance/section-parity.tsv`).
* **Address-taken external hashes.** The `__kcfi_typeid_*` absolute symbols match: 119/119.

## Kernel structure layout

* The modules are compiled against the GKI 6.1 headers and the stock vendor config.
* Any layout difference in an accessed structure would change displacements in `.text`.
  None exists: every function is byte-identical.
* The modversion CRCs, which encode the type layout of every imported symbol, are identical.

## Device-node and userspace ABI

See `userspace-kernel-abi.md`.
* The ioctl numbers are derived by compiling the reconstructed uapi headers.
* The dispatchers are byte-identical, so the ioctl table, argument sizes and copy lengths
  equal stock.
