# Corrected assumptions and retained boundaries

| Earlier candidate/assumption | Measured correction |
|---|---|
| Four audit D rows, public source candidates only | Independent maintained clean B1/B2 plus full stock ELF proof now permits four A rows; original owners unchanged. |
| 957dac is the exact source for every pinctrl file | MT6878/MT6363/common/Paris byte blobs match; debug differs. 5e41 debug reproduces stock; 957dac changes tristate function820→824 bytes and fails normalized acceptance. |
| pinctrl-mtk-v2 exports37 symbols | 37 exported functions plus exported data mtk_paris_pinctrl_pm_ops =38 CRC slots. Data export is counted and matched. |
| MT6878 exposes196 GPIO/EINT descriptors, all interrupt capable | 196 physical +20 virtual descriptors. Only117 physical support EINT; DT configures137 entries across4 instances of216 domain IDs. |
| GPIO number equals EINT register bit/index | E.g. GPIO28 → EINT0/local15, GPIO55 →0/local31, GPIO14 →2/local1; bank/register fields have independent calculations. |
| GPIO152 or thermal149/191/192 could be interrupt inputs | These descriptors have NO_EINT_SUPPORT; their proven software use is GPIO output control. |
| MT6878 uses a separate mt6878-eint module/binding | EINT is compiled into v2; board matrix node compatible is mediatek,mt6983-eint. |
| All MT6375 child interrupt cells are SoC EINT IDs | Parent PMIC has its own #interrupt-cells domain. Generator follows IRQ parent resolution, excluding child charger/TCPC/ADC IRQ numbers. |
| GPIO DT offsets are Linux global GPIOs | SoC chip base is dynamic; legacy consumers translate through of_get_named_gpio. Global base was not captured; use controller-relative identities. |
| MT6363 npins10 means ten usable physical pins | Pins1–9 plus dummy0xffffffff; FLAG_GPIO_START_IDX_1 registers9 physical pins. No DT GPIO client to it found. |
| drive-strength3 means3 mA | MT6878 FLAG_DRIVE_SET_RAW passes raw register code; physical current not proven. |
| MT6878 slew-rate accesses separate SR circuitry | SR table aliases DIR; stock Paris slew handler writes that same field. Do not normalize away this stock behavior. |
| DT okay/default guarantees selected pins or binding | Declared configurations, empty defaults, alternative variants and late-only runtime logs do not establish selected state or successful EINT init. |
| fingerprint state name spi0 means SoC SPI0 function | Pins60–63 mode2 are SPI1_* in the stock table; retain original names but use decoded function identity. |
| pinctrl suspend selects a board sleep pad configuration | No referenced literal sleep/idle states found; SoC noirq PM programs EINT wake/current masks, not full pad save/restore. |
| UFS_MPHY functions on192/193 prove UFS pad use | UFS has no host pinctrl state; mode4 is only supported alternate functionality. GPIO192 is a separate thermal control path. |
| Every declared FEM/audio/touch/camera state runs simultaneously | Multi-variant DT tables are not PCB wiring or runtime selection proof; potential overlaps are documented, not claimed active conflicts. |

These are scoped corrections, not edits to existing completed consumer evidence or component
taxonomy. Unobserved GPIO bases, electrical readings, physical netlists, selected alternative
states and controlled replacement runtime remain UNKNOWN/deferred—not compile blockers.
