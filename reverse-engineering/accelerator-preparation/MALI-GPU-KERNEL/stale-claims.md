# MALI-GPU-KERNEL — stale claims (2026-10-08)

| # | claim (preparation pack) | verdict | correction |
|---|---|---|---|
| 1 | mali r44p1 donor = NothingOSS `kernel_modules@5f75a3b` | **WRONG** | 5f75a3b gives kbase 1122/1819 and MGM 26/58 identical functions. The stock lineage is `580d08eac018` plus 4 files from `c3d070e9f373` (source-lineage.md). |
| 2 | ged / gpufreq donor = NothingOSS `device_modules@957dac` (first-listed candidate) | **WRONG for ged, gpufreq** | 957dac lacks 6 exports and has a CRC-mismatched import. ALPS 5e41 is exact. 957dac is exact for hal and gpu_bm. |
| 3 | "0 modules have existing published function/data evidence"; "no measured target source build exists" | **SUPERSEDED** | 8/8 modules rebuilt. 2748/2748 function symbols are byte-identical, as are all data, relocations and ABI. B1==B2. |
| 4 | "Exact GPU_ID/revision/core count is UNKNOWN" | **STANDS (runtime-only)** | It is not in the DT or any read-only capture. It is read from GPU registers at probe by code identical to stock, so it is not a parity gap. |
| 5 | `g3d-brisket@13fb0000` named as GPU hardware identity | **REFINED** | No stock module references `mediatek,g3d_brisket`. The 3 nodes are present in the runtime capture without drivers, so they are not Linux-driven. |
| 6 | "copied stock symvers is an oracle, not source/type proof" (dependencies.md) | **RESOLVED** | All 30 external-provider CRCs are regenerated naturally from public ALPS 5e41 and equal stock. The deterministic build uses only natural CRCs. |
| 7 | "`/dev/mali0` is the expected Kbase ABI, not a newly observed" node | **CONFIRMED by existing capture** | `13000000.mali/misc/mali0`, the `mali` driver binding and 3 IRQs are all in the read-only `02-android-topology.txt`. |
| 8 | (implicit) module signatures are a parity axis | **N/A** | The stock vendor_dlkm GPU modules are unsigned. |
