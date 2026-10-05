# YFT / Ulefone deltas — TinySys messaging (mtk_rpmsg_mbox, mtk_tinysys_ipi)

## Verdict: **DIRECT_SOURCE_MATCH — no Ulefone/YFT delta**

| item | donor (MTK ALPS mt6878 `5e415e059253` / NothingOSS) | GQ5012BF1 stock | evidence | delta | confidence |
|---|---|---|---|---|---|
| `mtk_rpmsg_mbox.c` | blob `82ec9c50d3` | identical | rebuilt `.ko` = stock byte-for-byte except build-id; `__bug_table` line numbers exclude the later `a8a808eb63` | none | proven |
| `mtk_tinysys_ipi.c` | blob `1acca98c7c` | identical | same; later/earlier variants rejected (`kernel/parity/lineage-and-whole-file.txt`) | none | proven |
| headers (`mtk_rpmsg.h`, `mtk_tinysys_ipi.h`, `mtk-mbox.h`) | blobs `2e21c19cb1`, `2205ab98d8`, `80ade10970` | identical as far as visible in the binary (struct offsets, sizes, enums used) | byte-identical code and data | none | proven |
| build config | in-tree KDM `CONFIG_RPMSG_MTK=m`, `CONFIG_MTK_IPI=m` | `-faddrsig`, `__FILE__` prefix `../kernel_device_modules-6.1/` | `.llvm_addrsig` and `.rodata.str1.1` exact | none (standard MTK build) | proven |
| `vermagic` / `depends` / `license` / `description` | — | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`, `depends=mtk-mbox` / `mtk_rpmsg_mbox,mtk-mbox` | `.modinfo` byte-exact | none | proven |
| board IPI configuration (DT `send-table`/`recv-table`, SCP/VCP/GPUEB) | reference `arch/arm64/boot/dts/mediatek/mt6878.dts` in the same KDM tree | **identical, same entries in the same order** (SCP 20+19, VCP 14+17, GPUEB 11+11) | `scripts/dtcmp.py` | none | proven |
| MCUPM legacy 8-mailbox mode (no `mbox-extend`) | absent in reference DTS | absent in live DT | `dtcmp`/live DT | none | proven |
| SAP / ADSP not instantiated | no `mediatek,sap` or ADSP node in reference mt6878.dts (SAP nodes exist only in mt6897/mt6989 DTS) | none in live DT | grep of reference DTS + live DT | none: platform-level, not YFT | proven |
| `IPI_ID_PLATFORM` missing from GPUEB name table | reference DTS name table identical to live | gpueb plat service + mobile log inert | DT + `gpueb_plat_service.c`/`gpueb_logger.c` guard on −1 | none (MTK platform config) | high |
| SCP ids used by kernel code but absent from the table (CHRE 47/48, `READY_0` 9, MPOOL 12/25, `DEBUG_CMD` 41, `AUDIO_FW` 49) | reference table identical (MPOOL lines are commented out in the reference DTS itself) | `IPI_UNAVAILABLE` at runtime | DT + call-site census | none (MTK platform config) | high |

The only YFT changes in the surrounding TinySys area are recorded elsewhere and are **outside** these two modules:

- `scp.ko`: DT-driven `awake-timeout` (`scp_awake_timeout`) and a separate `SCP_WFI_WAIT_TIMEOUT`. See `../sensors/notes/yft-deltas.md`. This is already present in the `5e415e059253` tree, so it is MTK/ODM-shared rather than a GQ5012BF1 patch on that base.
- `sensorhub.ko`: display-blank notifier and `yft_devinfo` hooks (`../sensors/`).
