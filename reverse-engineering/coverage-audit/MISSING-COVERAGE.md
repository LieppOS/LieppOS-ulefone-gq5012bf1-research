# Missing coverage

Audit date: 2026-10-07

## CONFIRMED MISSING

### MALI-GPU-KERNEL

1. **Proposed name:** `MALI-GPU-KERNEL`
2. **Subsystem:** Graphics / GPU
3. **Evidence:** active modules and enabled DT nodes plus vendor GPU services have no canonical component.
4. **Owns:** `mali_kbase_mt6878_r44.ko`, `mali_mgm_mt6878_r44.ko`, `mali_prot_alloc_mt6878_r44.ko`; `arm,mali-valhall`, `mediatek,mali`, `mediatek,g3d_brisket`; the kernel-facing ABI of the GPU/gpuserv/mali-platform services.
5. **Why not covered elsewhere:** `TMEM-FFA` owns secure-memory transport and `VENDOR-BLOB-HAL-INVENTORY` owns proprietary userspace/CSF payloads; neither owns KMD source/DT parity.
6. **Suggested initial status:** PARTIAL, class A.
7. **Estimated difficulty:** HARD.
8. **Expected boundary:** reconstruct kernel/DT/platform ABI; retain proprietary Mali userspace and CSF firmware.

The unified map has 10 E rows, all converging on this single scope:

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

## POSSIBLE MISSING

None currently meets the threshold for a new component. APUSYS/NPU, codec/media, generic MTK performance services and platform remote processors are represented as generic/platform infrastructure or retained vendor-blob boundaries; there is no GQ5012BF1-specific orphan evidence that justifies a new ownership scope.

## NOT MISSING / COVERED ELSEWHERE

- ICM4N607, MMC5603, STK3A5X and SPL07 register drivers are SCP-firmware-owned; Linux transport is `SENSOR-HUB-KERNEL`, while firmware/HAL behavior is `SENSOR-HUB` plus the physical-sensor scopes.
- Modem, RIL and IMS are deliberately split into Linux transport, signed modem firmware and proprietary userspace scopes.
- Camera sensors/VCM/OIS/EEPROM are closed child scopes; proprietary HAL/3A/tuning are represented by `CAMERA-HAL-ISP`.
- Secure TAs are represented by TrustKernel/KeyMint/fingerprint boundaries; lack of TA source is not an ordinary missing kernel component.
- Thermal-camera UVC/power, command/application and radiometry/calibration layers are separately owned.
- eSIM/eUICC and wireless charging are proven absent, not missing implementation scopes.

## GENERIC / NO DEDICATED RE NEEDED

- 207 shipped kernel modules are generic/upstream/platform infrastructure.
- 314 active DT compatible rows are generic infrastructure.
- AOSP interface libraries, framework services, filesystems, schedulers, standard USB classes and generic MTK platform helpers are `COVERED-GENERIC`/`GENERIC-PLATFORM-INFRASTRUCTURE`.
- Generic classification is evidence-backed per row; it is not a default fallback for unknowns.
