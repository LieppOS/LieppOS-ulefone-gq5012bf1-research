# SH366003 stock-versus-reconstruction structural comparison

## Inputs

- stock: `workspace/phase4-sh366003/oracle/sh366003_fg.stock.ko`
  - SHA256 `527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7`
- rebuilt: `workspace/phase4-sh366003/recon/sh366003_fg.recon.ko`
- comparison uses `llvm-readelf`, `llvm-nm`, `modprobe --show-modversions`, and relocation-aware `llvm-objdump -dr` output preserved beside both ELFs.

## Summary

| Metric | Stock | Rebuilt |
|---|---:|---:|
| ELF bytes | 85,968 | 42,912 |
| named functions | 39 | 39 |
| named functions shared | 39 | 39 |
| `.text` | 16,172 | 8,144 |
| `.init.text` | 160 | 72 |
| `.exit.text` | 96 | 40 |
| `.rodata` | 2,728 | 2,728 |
| `.data` | 712 | 704 |
| `.bss` | 452 | 544 |
| `.rodata.str1.1` | 9,396 | 396 |
| `__versions` | 2,304 | 2,304 |
| defined objects | 43 | 38 |
| relocations | 1,513 | 450 |
| printable strings | 494 | 328 |
| undefined/import symbols | 35 | 35 |
| MODVERSION entries | 36 | 36 |
| global-function KCFI entries | 8 | 8 |

## Functions

- stock functions: **39**
- reconstructed functions: **39**
- shared names: **39**
- stock-only: **0**
- reconstruction-only: **0**
- size-identical: **3** — `chipid_store`, `sh_fg_remove`, `show_fw_version`
- byte-identical: **2** — `sh_fg_remove`, `show_fw_version`

The low byte-identity result is expected for a C reconstruction without the proprietary source's exact lexical structure, inlining decisions, and complete diagnostic strings. It is not presented as instruction-level identity.

## ABI and KCFI

- undefined/import symbol sets are exact (35/35)
- complete `__versions` maps are exact (36/36), including `module_layout`
- the eight defined global-function KCFI type-ID words are exact:
  - `init_module`: `0x36b1c5a6`
  - `cleanup_module`: `0xa540670c`
  - `sh_fg_get_soc`, `sh_fg_get_vbat`, `sh_fg_get_ibat`, `sh_fg_get_tbat`: `0x36b1c5a6`
  - `file_decode_process`: `0xd73ac971`
  - `hal_fg_init`: `0x0bcd4ce1`

## Hardware-significant data

- `.rodata` size is exact.
- the 2,142-byte `sinofs_afi_data` image is embedded exactly once and is byte-identical (SHA256 `4888c5bc4b847ec6c118cd7bd334cbcffbf52c5fa2bf8f8660c3ac65e03359e1`).
- power-supply property order, OF/I2C tables, register constants, MAC commands, AFI record counts, update gates, timing constants, scaling formulas, and stock YFT CRCs are enforced by `kernel/scripts/phase4_sh366003_verify_recon.py`.

## Structural residuals

The reconstruction intentionally does not claim exact section, relocation, object, complete string-table, function-size, or instruction-byte identity. The principal causes are reconstructed control flow and omission of non-semantic proprietary debug strings. Hardware-significant constants and state transitions are separately fail-closed verified.
