# Stale-claim corrections — GPU-AI-AUX-KERNEL-INTERFACES

Corrections produced by the measured reconstruction. The preparation material is otherwise
preserved as-is; these entries supersede it where they conflict.

## 1. Donor choice: `957dac` is wrong for `vcp.ko`

`source-candidates.tsv` listed the NothingOSS `957dac185efe…` tree first for all three
modules. Measured against the ALPS release `5e415e059253…` that actually reproduces stock,
the two trees differ in exactly **one** file across both source directories:

| directory | differing files |
|---|---|
| `drivers/gpu/mediatek/gpueb/` | none — identical |
| `drivers/misc/mediatek/vcp/` | `rv/vcp_excep.c` only |

Consequences: `gpueb.ko` and `vcp_status.ko` would build identically from either donor;
`vcp.ko` would **not**, because `vcp_excep.o` is one of its nine objects. `957dac` remains
required for the vendor `Kconfig` and `mgk_64_k61_defconfig`, not as source. The patched
worktree `ca8b550b75e8` was not used.

## 2. "0 modules have existing published function/data evidence" — superseded

`STATUS.md`, `stock-modules.tsv` and `parity-gaps.tsv` carried
`UNKNOWN / no measured target rebuild parity located` for all three modules. Replaced by a
measured result: all three rebuild byte-identically except their GNU build IDs, with
complete function/data/section/relocation/ABI ledgers and clean-checkout B1/B2 determinism.

## 3. Counting conventions in `stock-modules.tsv`

Re-measured and matching exactly: functions (59 / 107 / 17), data symbols (69 / 136 / 17),
imports (68 / 134 / 1), relocations (1 820 / 5 889 / 158), `kcfi_abs_ids` (6 / 7 / 0).

Export counts differ by convention only: the preparation recorded 14 / 23 / 15
(positional `__ksymtab` pairing); the authoritative count read through `__crc_<name>`
inside `__kcrctab`/`__kcrctab_gpl` is **14 / 27 / 19**, and the ledger is asserted complete
against each module's total `__kcrctab*` size. The extra entries are exported *data*
objects (`vcp_ipidev`, `vcp_mboxdev`, `feature_table`, `vcp_ao`, `pwclkcnt`,
`mmup_enable_count`, `driver_init_done`, `is_suspending`), which positional pairing misses.

## 4. "MTK-TINYSYS-IPI DONE proves the transport, not these clients" — confirmed

Correct and unchanged. The reconstruction consumed `mtk_tinysys_ipi` and `mtk-mbox` purely
as providers: 8 of the 16 external CRCs come from them, regenerated from public source and
equal to stock. Neither module was rebuilt, re-owned or modified.

## 5. "GPUEB … 11 channels, one 160-slot mailbox" and "VCP … 28 configured channel IDs" — refined

Both confirmed from the merged DTB, with detail the preparation did not record: GPUEB's
`mbox-size = 160` slots are **4 bytes each** on mailbox 0, with per-channel slot counts
4/8/3/6/9/4/6/6/1/4/3 and two shared-memory regions (`MEM_ID_GPUFREQ` 16 KiB,
`MEM_ID_LOG` 1.5 MiB); VCP has **5** mailboxes and **7** interrupts (`wdt` SPI 200 plus
`mbox0..4` SPI 202–206), 256 KiB SRAM, an 8 MiB DRAM window and a 2 MiB secure dump
region. See [hardware-contract.md](hardware-contract.md).

## 6. The two VCP modules are a deliberate boot-order split, not a packaging artifact

`vcp_status.ko` ships in the **vendor ramdisk** (`modules.load` line 166) with an
intentionally empty `depends=`, while `vcp.ko` ships in **vendor_dlkm** (line 77) with ten
dependencies. Early consumers (`mmqos-common`, `mtk-mmdvfs-v3`, `mtk-cmdq-drv-ext`,
`mediatek-drm`, `mtk-mminfra-debug`, `mtk_imgsys_cmdq`) link only against the `_ex`
symbols of `vcp_status`; `vcp.ko` injects itself at probe through `vcp_set_fp`,
`vcp_set_ipidev` and `vcp_set_mminfra_cb`. Any future split/merge of these modules would
break that ordering.

## 7. Capability names that are **not** instantiated here

Confirmed against the merged DTB and the shipped build, and worth keeping explicit:
the GPUEB logger is disabled (`gpueb-logger-support = 0`); `/dev/vcp` has no file
operations (`CONFIG_MTK_TINYSYS_VCP_DEBUG_SUPPORT` unset); the
`mediatek,vcp-io-ube-lat` / `vcp-io-ube-core` match entries have **no DT node** on this
board; GPUEB `IPI_TEST` is compiled out. Presence in source is not capability on this
device.

## 8. No firmware claim is attached to this component

Neither module calls `request_firmware`. `gpueb.img` and `vcp.img` are retained,
unmodified and unanalysed. See [firmware-boundary.md](firmware-boundary.md).
