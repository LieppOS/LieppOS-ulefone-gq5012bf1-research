# Final missing-coverage verdict

Final snapshot: **2026-10-08**, source HEAD `3abc5643e539b3f2c8565d8197091d3bb50856ff`; workspace directories are authoritative. This report is reproducible from committed metadata, not a claim that later concurrent closures never occur.

## CONFIRMED MISSING: MALI-GPU-KERNEL

**One** genuinely missing registered ownership scope. Its ADD is recommended but **not applied**.

- **Owns:** `mali_kbase_mt6878_r44.ko`, `mali_mgm_mt6878_r44.ko`, `mali_prot_alloc_mt6878_r44.ko`; enabled `arm,mali-valhall`, `mediatek,mali`, `mediatek,g3d_brisket`; normal-world GPU kernel/platform ABI and the kernel-facing GPU/gpuserv services.
- **Not owned by:** TMEM-FFA's secure-memory transport or VENDOR-BLOB-HAL-INVENTORY's userspace/CSF payload inventory.
- **Boundary:** proprietary userspace/CSF firmware stays retained; source availability and matched r44/MT6878 build are not assumed.
- **Initial proposed status:** PARTIAL/A, HARD. Exact closure plan is in [NEXT-RE.md](NEXT-RE.md).

All **10** normalized E rows converge on that one scope:

- `kernel-module` `mali_kbase_mt6878_r44.ko` — depends=ged.ko,mtk_gpu_qos.ko,mtk_qos.ko,sspm_v3.ko,mtk_gpufreq_wrapper.ko,gpueb.ko,mtk_sec_heap.ko,tmem_ffa.ko,gz_tz_system.ko,gz_ipc_mod.ko,gz_trusty_mod.ko,mtk_pbm.ko,mtk_mdpm.ko,mtk_dynamic_loading_throttling.ko,mtk_low_battery_throttling.ko,mtk_tinysys_ipi.ko,mtk_rpmsg_mbox.ko,mtk-mbox.ko,mtk_gpu_hal.ko; load_order=43
- `kernel-module` `mali_mgm_mt6878_r44.ko` — depends=; load_order=42
- `kernel-module` `mali_prot_alloc_mt6878_r44.ko` — depends=; load_order=41
- `dt-compatible` `arm,mali-valhall` — sample=/soc/mali@13000000; drivers=
- `dt-compatible` `mediatek,g3d_brisket` — sample=/soc/g3d-brisket@13fb0000; drivers=
- `dt-compatible` `mediatek,mali` — sample=/soc/mali@13000000; drivers=
- `vintf-interface` `vendor.mediatek.hardware.gpu` — GPU HAL has no current component; proposed MALI-GPU-KERNEL scope
- `vintf-interface` `vendor.mediatek.hardware.gpuserv` — GPU service has no current component; proposed MALI-GPU-KERNEL scope
- `init-service` `vendor.gpuserv-default` — GPU service has no current component; proposed MALI-GPU-KERNEL scope
- `init-service` `vendor.mali_platform-mediatek` — Mali platform service has no current GPU component

## CAMERA-ISP-KERNEL — covered mixed scope, proposed SPLIT

ISP kernel modules/source donors and near-exact imgsensor reconstruction already belong to CAMERA-HAL-ISP. This is **not a second coverage hole**. Accept the split recommendation to isolate kernel parity from HAL/3A/tuning/CCU, with an explicit transfer ledger and no duplicate primary owners.

## POSSIBLE MISSING

None is supported by unexplained artifacts. Generic MTK/APUSYS/media infrastructure, SCP-owned sensor register drivers, modem/RIL/IMS, TEE TAs, DSP/CSF firmware and per-unit calibration have explicit generic or proprietary boundaries; do not invent source-actionable components for them.

## Not missing / negative findings

Physical sensors belong to SENSOR-HUB/SCP firmware plus their registered sensor scopes; transport is SENSOR-HUB-KERNEL. Camera sensors/VCM/OIS/EEPROM have named child owners. Thermal-camera USB/power, command/viewer and radiometry are separate scopes. eSIM/eUICC and wireless charging are preserved not-fitted findings. RT5133 is a declared, unbound reference client, not a new active camera-LDO gap; see [correction](notes/RT5133-CORRECTION.md).

Generic/dead artifacts stay enumerated in the TSVs with per-row evidence. Coverage is not source openness.
