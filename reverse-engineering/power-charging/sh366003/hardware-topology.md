# SH366003 hardware topology (GQ5012BF1)

| item | value | evidence | confidence |
|---|---|---|---|
| device | Sino Wealth **SH366003** SBS-style pack fuel gauge | compatible `sh,sh366003`; probe requires control subcommand 0x0001 == **0x0603** (`chipid`) | PROVEN |
| bus | **i2c-9**, `/soc/i2c@11c24000` (`mediatek,mt6989-i2c`, SCL gpio-id 0x8f / SDA 0x90) | base DTB in vendor_boot, alias `i2c9`, live `9-0055` | PROVEN |
| address | 7-bit **0x55** (AFI records use 8-bit 0xAA, driver shifts `>>1`) | DT `reg`, `IIC_ADDR_OF_2_KERNEL` | PROVEN |
| bus speed | **100 kHz** default: the adapter node has no `clock-frequency`; the child's `clock-frequency = <400000>` is not consumed by anyone | i2c-mt65xx.c `mtk_i2c_parse_dt` reads the adapter node | STRONGLY SUPPORTED (corrects earlier "400 kHz") |
| IRQ | **none**; polling (monitor every 5 s, first at 10 s) | no `request_irq`/`devm_request_threaded_irq` import; DT has no `interrupts` | PROVEN |
| GPIOs / supplies / reset pin | none | no gpiod/regulator imports, no DT properties | PROVEN |
| battery connection | pack-side gauge on the **2S** pack: SBS 0x08 = pack voltage (~8.4 V), MAC 0x0071 / 0x0060 give two cell voltages (~4.2 V each) | `battery-topology.md` (power-charging/hardware) + stock driver formulas | PROVEN |
| temperature | SBS 0x06 = pack NTC (0.1 K); SBS 0x28 = die (read, discarded) | stock code | PROVEN |
| module | `sh366003_fg.ko`, vendor_boot first stage (`modules.load` line 134, recovery line 132; resolved insertion 146 after `yft_devinfo` 145) | module-loading/resolved-load-order.tsv | PROVEN |

## Place in the charging architecture

```
 USB-C ─ MT6375 (TCPC/charger/buck, "primary_chg", PMIC gauge "mtk-gauge")
        │        └ 1S-equivalent domain (CV 4.45 V)
        ├ SC8510 (2:1 bridge, V1X 1S rail ↔ V2X 2S pack)
        └ SC8571 master/slave (2:1 charge pumps, VBAT = pack, PE5/PD direct charge)
                                  │
                           2S battery pack ── SH366003 @ i2c-9 0x55 ("3rd-gauge")
```

SH366003's only electrical relationships are the pack (cells, NTC, sense resistor inside the
pack/gauge circuit) and i2c-9. Its only software relationships:

| peer | direction | interface |
|---|---|---|
| MT6375 charger psy `primary_chg` | gauge **reads** ONLINE | `power_supply_get_by_name("primary_chg")` → `adapter_status` 0/2 (STATUS, AFI-update gate) |
| mt6375-battery (`battery` psy), mtk_charger_framework, mtk_pep, mtk_pd_charging, mtk_pep50 | they **read** `3rd-gauge` | power_supply properties (see `charging-boundary.md`) |
| SC8571 / SC8510 | none | no symbol, psy or DT link |
| PMIC MT6363/MT6375 gauge | none | the MT6375 coulomb counter is a separate psy (`mtk-gauge`) overridden by YFT |
| yft_devinfo | gauge **calls** | `yft_fuelgauge_device_add`, `yft_set_fuelgauge_device_used`, `fuelgauge_fw_version` |

Protection FETs/balancing are not visible to software (unchanged unknown from `battery-topology.md`;
the gauge reports Safety/PF words, which the driver only logs).
