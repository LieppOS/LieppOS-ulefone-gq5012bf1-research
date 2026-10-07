# SH366003 source lineage

**Classification: BINARY RECONSTRUCTION** (binary-equivalent source; literal source not recovered).

| layer | origin | evidence |
|---|---|---|
| driver body | Sino Wealth Linux gauge template, version string **"2022.10.17"** (probe/remove logs), Chinese developer comments in AFI log strings (`OPERATE_COMPARE 重试…`) | stock `.rodata.str1.1` (194 strings, all reproduced) |
| AFI interpreter (`file_decode_process`, `fg_decode_iic_read/write`, OPERATE_READ/WRITE/COMPARE/WAIT = 1/2/3/4, COMPARE_RETRY_CNT 2 / 50 ms, TEMPER_OFFSET 2731, `fg_read_block`, SBS/MAC word reader) | shared Sino Wealth code family | closest public relative: OnePlus `oplus_sh366002.c` — LineageOS `android_kernel_oneplus_sm8550-modules` branch `lineage-22.2`, path `oplus/kernel/charger/gauge_ic/oplus_sh366002.c`, last commit **959d4ed89cf6d1d26ca74f51c0dfa6d2f8d21835** (2025-09-11, "Import rather minimal set of drivers from OOS 15.0.0.850(EX01)"), file sha256 `f197fe2d…0aa4` |
| differences from that relative (not a donor) | different template generation | sh366002: bq27541 glue (`struct chip_bq27541`), AFI from DT `battery_params`, unseal key 0x19861115/0xFFFFFFFF, CMDMASK_CNTL_R = 0x08000000; SH366003 stock: own `struct sh_fg_chip`, AFI compiled in, keys 0x12345678/0x90ABCDEF, ALTMAC=bit27/CNTL=bit26, frame-restart (`i_bak`, `retry2` ≤ 10) in COMPARE, run-state check (OEMFlag 0x00C1), `Check_Chip_Version` on MAC 0x0046/0x004D |
| YFT/Ulefone glue | YFT | `yft_devinfo` calls, psy/class name `3rd-gauge`, `primary_chg` charger probe, `/chosen atag,boot` boot-mode gate (copied MTK `log_store` helper — log text still says `log_store:`), date sysfs, synthetic `soh` | see `yft-sh366003-deltas.md` |
| build | GKI android14-6.1 KMI, `kernel_device_modules-6.1` external module, Android clang 17.0.2 (r487747c, `.comment` identical) | vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |

Searched without a match for the exact template: MediaTek ALPS / `kernel_device_modules-6.1`,
NothingOSS mt6878 trees (`nt6878`, `nkm`, `volla6878`, `kdm`), Lineage tree, local
`kernel-research/`, web searches for unique strings (`fg_gauge_runstate_check`, `QEN_FLAG`,
`sh366003_GaugeLog`, `i_bak` + `retry2`, `sinofs_afi_data`). No public SH366003 driver exists.

## Reconstruction

- `source/sh366003_fg.src.c` — readable source; each log call carries `/*@NNNN*/`, the stock
  `__LINE__` (124 anchors, lines 190 … 2490).
- `scripts/pad_lines.py` expands it to `source/sh366003_fg.c` (2499 lines), which is what is
  compiled; private tree `kernel_device_modules-6.1/drivers/power/supply/sh366003/`.
- `sinofs_afi_data.inc` stays in the private tree / `kernel/phase4-sh366003-recon/` (not duplicated).
- Build: `scripts/build_sh366003.sh`; no `KBUILD_MODPOST_WARN`, no ELF editing, CRCs from
  `source/stock-yft-devinfo.symvers` via `KBUILD_EXTRA_SYMBOLS`.

Supersedes the September behaviour-equivalent reconstruction (`kernel/phase4-sh366003-recon/sh366003_fg.c`,
private commit 68e8898, 2/39 functions exact).
