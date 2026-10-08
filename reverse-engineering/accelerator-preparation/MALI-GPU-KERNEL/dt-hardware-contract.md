# DT / hardware contract — MALI-GPU-KERNEL

**Sources:**
* the stock merged DTB, `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb`
  (decoded rows in `dt-nodes.tsv` and `dt-providers.tsv`);
* the reconstructed driver sources (byte-identical to stock);
* the read-only runtime capture `slot-b-investigation/02-android-topology.txt` and
  `04-focused-android.txt`.

No device interaction took place.

## Binding (DT compatible → driver → runtime evidence)

| DT node | compatible | consumer (match table / lookup) | runtime capture |
|---|---|---|---|
| `/soc/mali@13000000` reg 0x13000000+0x480000 | `mediatek,mali`, `arm,mali-valhall` | kbase `kbase_dt_ids` = `arm,mali-valhall` (platform driver `mali`). `mediatek,mali` is looked up by `of_find_compatible_node` in ged (`ged_main.c`) and by `__gpufreq_of_ioremap("mediatek,mali")` in gpufreq_mt6878. | `sys/bus/platform/drivers/mali/13000000.mali`; `/dev/mali0` (`…/13000000.mali/misc/mali0`); `sys/class/devfreq/13000000.mali`; IRQs 437/438/439 `13000000.mali` |
| `/mgm` | `arm,physical-memory-group-manager` | MGM `memory_group_manager_dt_ids` (driver `physical-memory-group-manager`) | `sys/devices/platform/mgm/driver` |
| `/soc/protected-memory-allocator@13c3f000` reg-name `gpueb_base`, `gpr-offset=0xd1c`, `gpr-id=6`, `gmpu-table-size=0x400000`, `protected-reserve-size=0x200000` | `arm,protected-memory-allocator` | prot_alloc `protected_memory_allocator_dt_ids` | `…/13c3f000.protected-memory-allocator/driver` |
| `/soc/ged` (`gpufreq-supply` → gpufreq) | `mediatek,ged` | ged `g_ged_of_match` | `sys/devices/platform/soc/soc:ged/driver`; devlink `soc:ged → 13000000.mali` (`ged-supply`) |
| `/gpufreq-wrapper` `gpueb-support=1 dual-buck=0 gpufreq-bringup=0 gpufreq-version=2` | `mediatek,gpufreq_wrapper` | mtk_gpufreq_wrapper `g_gpufreq_wrapper_of_match` | `sys/bus/platform/drivers/gpufreq_wrapper/gpufreq-wrapper` |
| `/soc/gpufreq@13fbf000` (15 reg ranges: mfg_top_config, mfg_pll, mfgsc_pll, mfg_rpc, sleep, topckgen, nth_emicfg(_ao_mem), ifrcfg_ao, infra_ao(1)_debug_ctrl, nth_emi_ao_debug_ctrl, nemi_mi32/33_smi_sub, sysram_mfg_history) | `mediatek,gpufreq` | mtk_gpufreq_mt6878 `g_gpufreq_of_match` | `sys/bus/platform/drivers/gpufreq/13fbf000.gpufreq`; devlinks to regulator.7/.27, `1cc04000.spmi` |
| `/soc/gpu-qos@112000` `qos-sysram-support=1` | `mediatek,gpu_qos` | looked up by mtk_gpu_qos (`gpu_bm.c`) and ged (`ged_gpu_bm.c`); no driver binds | device present, no driver (by design) |
| `/gpu-fdvfs@112000` `gpu-freq-notify-support=1 fdvfs-policy-support=0` | `mediatek,gpu_fdvfs` | looked up by ged (`ged_main.c`, `ged_eb.c` ioremap); no driver binds | `sys/devices/platform/112000.gpu-fdvfs`, no driver |
| `/soc/g3d-brisket@13fb0000/1000/2000` | `mediatek,g3d_brisket` | **no stock module references this compatible** (byte scan of all vendor_dlkm and vendor_boot modules) | devices present, no `driver` link. Not a Linux-driven block in this image; it is outside the kernel scope. |

* **Interrupts.** The DT declares JOB (0x10f), MMU (0x10e), GPU (0x10d), EVENT (0x110) and
  PWR (0x111), all SPI and level-high.
* The CSF kbase requests only JOB/MMU/GPU, which matches the 3 IRQs (437–439) in the
  capture.

**Supplies:**
* `vgpu` is mt6319@6 `vbuck2`; `vsram` is pmic@4 `vsram-cpum`.
* `gpufreq_mt6878` gets both with `regulator_get_optional` and declares no clocks; PLLs are
  programmed through `mfg_pll`/`mfgsc_pll`.
* There are no `clocks`, `power-domains` or `iommus` properties on mali.
* GPU MMU translation is kbase's own (`mmu/mali_kbase_mmu.c`). There is no SMMU on MT6878:
  `gpu_iommu` is mt6989-only and not shipped.

**OPP table** (`operating-points-v2` of mali, consumed by kbase devfreq): 46 OPPs, from
1300 MHz @ 875.0 mV down to 265 MHz @ 600.0 mV (`dt-nodes.tsv`). The effective DVFS goes
through gpufreq/GPUEB (`gpu-power-management.md`).

**Cooling:** `#cooling-cells=2` registers kbase devfreq cooling
(`CONFIG_MALI_MTK_DEVFREQ_THERMAL`). `thermal_interface` and `mtk_gpu_power_throttling`
reach GPU limits through the gpufreq_wrapper exports `gpufreq_get_freq_by_idx` and
`gpufreq_set_limit`.

**Runtime-only facts** (not in any static artifact or capture): GPU_ID, product revision and
shader-core mask. kbase reads them from `GPU_ID`/`SHADER_PRESENT` at probe. The driver code
that handles them is identical to stock, so they do not affect parity.

## Stock-specific vs public donor

All 8 modules are compiled unchanged from public MediaTek MT6878 sources (NothingOSS and
ALPS). No stock module contains an OEM, YFT or board string. The board-specific contract
lives entirely in the stock DT, i.e. the node data above. See `board-specific-deltas.md`.
