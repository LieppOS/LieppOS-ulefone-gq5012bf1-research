# CONNFEM (connfem.ko)

**Status: CONNFEM = DONE** (kernel driver + DT contract + board selection). Physical antenna and
RF layout are BLOCKED on teardown (`../hardware/rf-front-end.md`).

| item | result |
|---|---|
| module | `connfem.ko` (206,304 B, sha256 in `../kernel/module-inventory.tsv`), `depends=` (none) |
| source | NothingOSS kernel_modules **2115d27** (alps-mp-u0.mp1-V9.9) `connectivity/connfem` |
| parity | **94/94 functions, 45/45 data**, imports 64/64, exports 8/8, modversions 65/65, **export CRCs 8/8**, modinfo 7/7, vermagic, sections 23/23 |
| Ulefone delta in driver | none |

## What changed vs. the earlier PARTIAL reconstruction

The Phase-4 reconstruction (`Reverse Engineer - DONE/CONNFEM/notes/phase4-connfem-reconstruction.md`)
only had the NothingOSS 5f75a3b snapshot (Tetris U2.6). The 38 SKU/truth-table functions
(`cfm_sku_*`, `connfem_sku_data`, `connfem_sku_flag_u8`, 21,472-byte SKU context) were
rebuilt from disassembly as behavioural equivalents, with one unmatched export CRC. The newly
fetched NothingOSS history contains MediaTek's own V9.9 connfem (`git diff 5f75a3b 2115d27 --
connectivity/connfem`: 17 files, +3257/−244). That source contains the SKU subsystem and
rebuilds byte-exact unmodified, so the hand reconstruction is superseded.

## DT contract and board result

* `connfem` node: `compatible = "mediatek,mt6878-connfem"`, 7 pinctrl states (FEM pairs),
  `epa-elna-mtk { hwid { gpio = <&pio 131 0>, <&pio 132 0>, <&pio 92 0>; } parts = <24 phandles>
  ... }`, BT/Wi-Fi flags per HWID.
* HWID = **2** (inferred from the SKU-6637 cross-check in `../hardware/mt6637.md`) → `nofem` +
  `nofem`. Runtime: `connfem_is_available: FEM is not available`.
* Consumers: `bt_drv_6878` (`connfem_epaelna_get_fem_info/get_flags/get_pin_info`) and
  `wlan_drv_gen4m_6878` (`connfem_is_available` + epaelna API).
* Userspace: `libconnfem.so`, `/dev/connfem` (`CONNFEM_DRIVER_NAME`), `vendor/firmware/connfem.cfg`
  (0 bytes, so the DT data is used).
