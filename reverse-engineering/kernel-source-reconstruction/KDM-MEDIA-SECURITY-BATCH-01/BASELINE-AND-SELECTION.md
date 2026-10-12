# Baseline and selection

| | |
|---|---|
| Baseline | canonical `ee1803b7` (PERFORMANCE-INTEGRATION-01 applied): A375 B1 C10 D18 E0 F0 G54 = 376/458; validator PASS; inventory 458/471 PASS |
| Branch / worktree | `claude/kdm-media-security-batch-01` / `ulefone-gq5012bf1-research-claude-kdm-media` |
| Concurrent work | Codex G-SOURCE-RECOVERY-BATCH-01 (branch @ 59ee0113). It froze 23 Category G identities; none is selected here |

## Frozen manifest: 11 identities

`BATCH-MANIFEST.tsv`, SHA256 `063a19ed6e8dc0d7254e47609dce081deec8b83e3e03ea9e2843a012e8c06e83`.

All 11 are canonical D with a candidate-only owner. All are vendor_dlkm and loaded in the stock capture.
`mtk-mmdvfs-v3-start` has two byte-identical occurrences (vendor_boot + vendor_dlkm). None of the 11 has `.BTF`
or a signature. Each has exactly one standalone `obj-m` in pinned ALPS `5e415e05`, and its Kconfig option is `=m`
in the vendor config (`b826d842`).

| Family | Module | ALPS unit | Stock `depends=` (class) |
|---|---|---|---|
| FLASHLIGHT | flashlight | `drivers/misc/mediatek/flashlight` (`CONFIG_MTK_FLASHLIGHT`) | mtk_pbm, mtk_peak_power_budget, mtk_low_battery_throttling, mtk_bp_thl (all A) |
| FLASHLIGHT | mtk-composite | `drivers/misc/mediatek/flashlight` (`CONFIG_MTK_V4L2_FLASHLIGHT`) | — |
| MEDIA | mtk_jpeg | `drivers/media/platform/mtk-jpeg` | mtk-icc-core, mtk-mmdvfs-v3 (A) |
| MEDIA | mtk-mmdvfs-v3-start | `drivers/misc/mediatek/mmdvfs` | mtk-mmdvfs-debug, mtk-mmdvfs-v3 (A) |
| DMA-HEAP | mtk_sec_heap | `drivers/dma-buf/heaps` (`CONFIG_MTK_TRUSTED_MEMORY_SUBSYSTEM`) | tmem_ffa (**G, Codex target**), system_heap (A) |
| DMA-HEAP | mtk_heap_debug | `drivers/dma-buf/heaps` (`CONFIG_DMABUF_HEAPS_DEBUG`) | mtk_sec_heap (batch), system_heap, mrdump, monitor_hang (A) |
| SECURITY | widevine_driver | `drivers/misc/mediatek/widevine_drm` | mtk_sec_heap (batch) |
| SECURITY | tui-common | `drivers/input/touchscreen` (unconditional `obj-m`) | — |
| SECURITY | sapu | `drivers/misc/mediatek/apusys/sapu` | mtk_sec_heap (batch), gz_trusty_mod, gz_tz_system (**G, Codex targets**) |
| PLATFORM-IO | mtk_irtx_pwm | `drivers/misc/mediatek/irtx` (`CONFIG_MTK_IRTX_PWM_SUPPORT`) | mtk-pwm (**G**, not a Codex target) |
| PLATFORM-IO | nvmem-mt635x-efuse | `drivers/nvmem` (`CONFIG_MT635X_EFUSE`) | — |

## Corrections to the assignment's descriptive names

- **"MediaTek USB composite" does not exist as a D target.** The stock `mtk-composite.ko` is built only by
  `drivers/misc/mediatek/flashlight/Makefile` (`CONFIG_MTK_V4L2_FLASHLIGHT`); it is the V4L2 flashlight composite.
  ALPS has a second `mtk-composite.c` at `lens/vcm/v4l2/media/`, but it is linked into `camera_af_media`, which is
  Codex's G target. That second file is not touched here.
- **"Infrared transmitter"** is `mtk_irtx_pwm`.
- **"NVMEM efuse"** is `nvmem-mt635x-efuse` (PMIC MT635x efuse).

## Provider boundaries with Codex's G scope

`tmem_ffa`, `gz_trusty_mod` and `gz_tz_system` are among Codex's 23 frozen G targets; `mtk-pwm` is Category G but
unselected. They are used here **only** as compile-only ABI witnesses:

- the exporting objects are compiled from pinned ALPS in this batch's own workspace to verify import CRC, licence,
  namespace and KCFI;
- nothing is linked, owned or certified, and no Codex repository, workspace or audit row is touched;
- their audit rows stay G.

The same rule applied earlier to `mtk_fpsgo` (LOW-POWER-BATCH-01).

## Ownership check

- **Maintained repositories:** none owns any of the 11. The `secure_transport` and Codex G mentions of
  `mtk_sec_heap` are `provider_dependencies` or witness references only.
- **Research packages:** no reconstruction exists. Mentions are audit baselines, candidate queues and
  dependency columns.
- **kernel-work:** no workspace builds these modules.

## Remaining D not selected

- `reboot-mode` and `syscon-reboot-mode`: in-tree GKI-tree pair, native stage.
- `fpsgo`, `hbt`, `msync2_frd`, `scheduler_ext`: Nothing `kernel_modules`; two of them link `_shipped` objects.
- `mali_dmabuf_test_mt6878_r44`: Mali r44 tree.

They were left out because they use different source roots and build stages, not because of quota.
