# Kernel ABI parity and implementation ownership

Complete ledger `evidence/acceptance/abi-parity.tsv`: all 103 import CRCs, 40 export slots,
12 absolute KCFI IDs and every modinfo record match stock. All exports are GPL-only.
`import-providers.tsv` resolves 91 imports against the hash-pinned public GKI 12901745
core symvers and 12 against rebuilt pinctrl-mtk-v2 in the same modpost invocation.
No unresolved symbol or extra provider input remains.

| Module | GKI imports | pinctrl-mtk-v2 imports | Exports | KCFI IDs |
|---|---:|---:|---:|---:|
| pinctrl-mt6363 | 4 | 1 | 0 | 0 |
| pinctrl-mt6878 | 2 | 6 | 0 | 5 |
| pinctrl-mtk-common-v2_debug | 25 | 5 | 2 | 3 |
| pinctrl-mtk-v2 | 60 | 0 | 38 | 4 |

* MT6363: `mt63xx_pinctrl_probe` 0x6952d696.
* MT6878: `mtk_paris_pinctrl_probe` 0xf6aec8a7, `mtk_paris_pinctrl_pm_ops` 0x717440da,
  `mtk_pinconf_bias_set_combo` 0xa6facbf8, `mtk_pinconf_bias_get_combo` 0x0028780d,
  `mtk_pinconf_adv_drive_set` 0x78aaf14e, `mtk_pinconf_adv_drive_get` 0x5823900c.
* Debug: `mtk_hw_get_value`, `mtk_hw_set_value`, `mt63xx_hw_set_value`,
  `mtk_pctrl_show_one_pin`, `mtk_is_virt_gpio` (exact CRCs in the provider ledger).
* Debug exports: `gpio_dump_regs` 0x7ec58d17 and `gpio_dump_regs_range` 0x5d37f189.
  The latter matches the already-certified STORAGE `mtk-mmc` consumer exactly.
  Other shipped consumers are recorded in `evidence/inventory/DEPENDENCY-EDGES.tsv`;
  their implementations are not certified by this package.

There are **38**, not 37, v2 exports: `mtk_paris_pinctrl_pm_ops` is exported data.
Counting exported functions alone loses this mandatory ABI slot. The verifier reads
`__crc_*` addresses and asserts complete coverage of both kcrctab buckets.

## Actual compiled implementation

`FUNCTION-PARITY.tsv` identifies every compiled function; helpers may be inlined and do not
necessarily exist as separate ELF symbols. The following ownership is source-supported and
backed by full ELF acceptance, not extrapolated from other MediaTek SoCs.

| Layer | Code / responsibilities |
|---|---|
| MT6878 platform | one registration function; `mt6878_data`, pin/mux/field/pull/EH tables; probe and noirq PM delegated to v2 |
| MT6363 platform | module init/exit, probe wrapper, regmap unlock/lock callback; pin1–9 field tables + dummy descriptor |
| v2 `mtk-eint.c` | DT instance matrix, IRQ domain/chained parent, type/polarity/edge handling, mask/unmask/ack/software IRQs, debounce, wake/current masks, noirq suspend/resume, debug attributes |
| v2 common | binary-search field calculation, bank/bit/offset checks, masked RMW/race-free writes, GPIO↔EINT translation, pull/drive/advanced controls (only SoC-populated callbacks enabled) |
| v2 Paris | platform probe, pinctrl registration/enable, single-pin groups, mux validity, DT maps/configs, GPIO callbacks, generic pin ownership interfaces; MT63xx regmap backend |
| debug | GPIO/register dump exports, tristate helper (changes pulls temporarily), `/proc/mtk_gpio` read/show and pin-control write handler (nodes mode0444; never invoked here) |

Raw KCFI preambles are inside the byte-identical code sections; absolute type IDs match.
All operation table bytes and their call-target relocations match. Metadata `depends=` is
empty for v2 and `pinctrl-mtk-v2` for the other three; vermagic identical. Stock/rebuild
contain no srcversion/signature. No broad generic feature claim is inferred merely from an
export: MT6878's reachable callbacks are precisely those populated by `mt6878_data`.
