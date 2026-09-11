# LN2403 → MTK PWM provider ABI

The only intermodule imports are genuine `mtk-pwm.ko` exports:

| symbol | stock CRC | prototype | LN2403 use | result |
|---|---|---|---|---|
| `mt_pwm_disable` | `0xd602ce35` | `void mt_pwm_disable(u32 pwm_no, u8 pmic_pad)` | `(3, 0)`; return is void | source-built CRC exact; 160-byte provider function byte-identical |
| `pwm_set_spec_config` | `0xa54c8591` | `s32 pwm_set_spec_config(struct pwm_spec_config *conf)` | address of 56-byte legacy config; return ignored | source-built CRC exact; 744-byte provider function byte-identical |

Source: local Nothing MT6878 device-modules commit
`957dac185efe46cbf6336b0fff9516d84c8cd78f`, files
`drivers/misc/mediatek/pwm/mtk_pwm.c` (SHA256
`9981b3c73185d0391076b52ebe0a1cba1ec75935973f768461312f94e789dfbc`),
`pwm_v2/mtk_pwm_hal.c` (SHA256
`eeeefe673c279ff65998d67865bc9f121964530315b34a38faa45d12be8db496`),
and `include/mt-plat/mtk_pwm.h` (SHA256
`fe2017c363b459aee1b874f0d8cf43aac61b671a006ab5b5a06be5b83fa87c59`).

The complete real provider was built as
`//lieppos/mtk-pwm-provider:mtk_pwm_provider`. Its `Module.symvers` emits the two
stock CRCs naturally—no fake symvers, CRC patches, ELF edits, or warning mode.
The reconstructed consumer depends on that target.

`pwm_set_spec_config` validates the channel/mode/source/divider, powers the PWM
block, writes OLD-mode register fields and clock selection, executes a memory
barrier, and enables the channel. `mt_pwm_disable` disables channel 3, waits 1
ms in its internal path, and powers it off. Both reconstructed provider entry
points match stock bytes, sizes and direct prototypes, closing call/KCFI ABI.
