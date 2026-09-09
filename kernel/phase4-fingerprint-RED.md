# `fingerprint.ko` mandatory RED baseline

## Donor outcome

`NO_PUBLIC_DONOR_FOUND`

No plausible donor source exists locally or in the public candidates reviewed.
Consequently there is no honest unchanged-donor build to present. The RED
baseline is the empty-source state measured against the frozen stock oracle;
all implementation work must be justified directly by stock evidence.

## Stock target that RED must reach

| property | stock oracle | initial source state / delta |
|---|---|---|
| defined functions | 16 | 0; missing 16 |
| kernel imports / MODVERSIONs | 18 / 18 | 0; missing all 18 |
| exports | 10 | 0; missing all 10 |
| export CRCs | ten exact CRCs in `phase4-fingerprint-exports.tsv` | none |
| OF compatible | `mediatek,yft_finger` | absent |
| pinctrl object set | 15 pointers: controller plus 14 states | absent |
| pinctrl state names | reset high/low; IRQ pull down/up/disable; SPI CLK/CS/MI/MO in GPIO and SPI functions | absent |
| DT GPIO handling | `int-gpio`, `reset-gpio`; IRQ mapping from matching node | absent |
| DT parsing | global compatible-node lookup and state publication | absent |
| IRQ behavior | pinctrl pull-state selector; no Linux IRQ mask API | absent |
| reset behavior | reset-high/reset-low pinctrl selector | absent |
| SPI-mode behavior | four-pin pinmux transition, not SPI CPOL/CPHA | absent |
| wait/completion behavior | global wait queue plus ready flag and bounded timeout loop | absent |
| PM | no PM callbacks | absent |
| lifecycle | platform-driver register/unregister; probe delegates parser; remove is no-op | absent |
| globals/layout | wait queue, ready flag, pinctrl and 14 state pointers, OF/platform tables | absent |

## Initial ABI delta

All stock exports were missing before reconstruction:

- `yft_finger_probe_isok`
- `yft_finger_set_power`
- `yft_finger_power_deinit`
- `yft_finger_set_reset`
- `yft_finger_set_irq`
- `yft_finger_get_irqnum`
- `yft_finger_get_irq_gpio`
- `yft_finger_get_reset_gpio`
- `yft_finger_set_spi_mode`
- `yft_waite_for_finger_dts_paser`

The typo in `yft_waite_for_finger_dts_paser` is part of the target ABI and is
not corrected.

## RED acceptance rule

A later build is GREEN only if it is produced naturally from source against
the pinned exact GKI, has zero build/modpost warnings and unresolved symbols,
and reproduces every stock-consumer CRC edge without fake symvers, CRC
patching, or ELF editing. Behavioral comparison remains mandatory even if the
export CRCs match.
