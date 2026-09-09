# GQ5012BF1 `fingerprint.ko` source candidates

## Result

`NO_PUBLIC_DONOR_FOUND`

No exact or plausible source donor containing the YFT provider API was found.
Reconstruction is therefore stock-oracle-led.

## Search scope

Local searches covered `/home/armol/androido_dalykai` and
`/home/armol/kernel-work`, excluding generated build outputs and binary stock
artifacts. Public searches covered indexed GitHub/Gitee/web results and queries
for NothingOSS, MediaTek BSP, Motorola, MiCode, OnePlus, OPPO, realme,
Transsion, Sony, Ulefone/YFT, generic MediaTek fingerprint pinctrl code, and
MicroArray `madev` drivers.

Exact identifiers searched:

- `mediatek,yft_finger`
- `yft_finger_set_irq`
- `yft_finger_set_reset`
- `yft_finger_set_spi_mode`
- `yft_waite_for_finger_dts_paser`
- `yft_finger_get_gpio_info`
- `yft_finger_probe_isok`
- `yft_finger_spi0_mi_as_spi0_mi`
- `finger_dts_paser`
- `madev_finger`

Broader semantic queries included `microarray fingerprint`, `MicroArray
fingerprint`, `fingerprint pinctrl mediatek`, `mediatek fingerprint gpio`,
`mediatek fingerprint reset irq spi mode`, and `madev0`.

## Candidate classification

| candidate family | classification | reason |
|---|---|---|
| Local GQ5012BF1 research/evidence references | `NO_USEFUL_SOURCE` | ABI tables, DT snapshots, and prior notes only; no C source |
| Public exact-identifier results | `NO_USEFUL_SOURCE` | zero relevant indexed source hits for all exact YFT identifiers |
| Public generic MicroArray/`madev0` sensor drivers | `SAME_FRAMEWORK_DIFFERENT_BOARD` | describe the sensor/character-device layer, not this YFT board-glue provider; out of reconstruction scope |
| Public generic MediaTek fingerprint GPIO/pinctrl glue | `STRUCTURAL_DONOR_ONLY` | similar concepts but different identifiers, pinctrl state sets, DT semantics, and exported ABI |
| Mainline Linux fingerprint/USB/libfprint material | `NO_USEFUL_SOURCE` | userspace or unrelated hardware; no stock provider semantics |
| Generic x509/netfilter/string “fingerprint” hits | `NO_USEFUL_SOURCE` | lexical false positives |

## Exact-source and strong-match status

- `EXACT_SOURCE`: none
- `STRONG_SOURCE_MATCH`: none
- `SAME_FRAMEWORK_DIFFERENT_BOARD`: generic MicroArray sensor-layer sources only
- `STRUCTURAL_DONOR_ONLY`: generic MediaTek pinctrl/GPIO examples only
- `NO_USEFUL_SOURCE`: all remaining results

No source was frozen as a donor because no candidate crossed the threshold for
an unchanged RED build. Stock disassembly, stock DT, stock metadata, and the
stock MicroArray consumer remain the authoritative inputs.
