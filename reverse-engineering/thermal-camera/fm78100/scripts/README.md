# scripts

All paths assume the pinned GKI workspace `G=/home/armol/kernel-work/gki-12901745-workspace`
(common@6b18f0b574ab, configured output `lieppos/camera-isp/kout`, clang r487747c) and the
isolated work dir `$G/lieppos/thermal-fm78100` (`src/` = `../source`, `stock/` = stock oracle,
`provider.symvers` = `0x398e9c8b yft_usb_flag … EXPORT_SYMBOL_GPL`).

| script | purpose |
|---|---|
| `build.sh <tag>` | isolated `M=` build → `par/yft_tiny2c_usb-<tag>.ko` (stripped) |
| `fast_fn_compile.py` | single-TU compile with the exact kbuild flags (`cc.flags` from `.yft_tiny2c_usb.o.cmd`) and per-function disassembly diff against stock |
| `i2c_read_order_search.py` | hill-climb over `i2c_msg` field-assignment order; found `.addr,.flags,.buf,.len` (0 diff) |
| `probe_unwind_loop_trials.py` | 4 batches of `tiny2c_usb_init_sysfs` loop shapes (all keep the 4-byte probe residual) |

Parity: `python3 reverse-engineering/display-input/rear-display-input/scripts/ko-parity-tsv.py stock.ko par/yft_tiny2c_usb-F1.ko par/F1`.
