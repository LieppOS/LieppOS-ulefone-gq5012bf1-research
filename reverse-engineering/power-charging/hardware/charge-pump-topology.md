# GQ5012BF1 charging hardware topology (static evidence)

Sources:
- the merged DT `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`;
- the stock-exact rebuilt modules (charger framework, PE5, sc8571, sc851x);
- the live-sysfs snapshots already in this repo (`kernel/phase4-sc8571-*`, `kernel/phase4-sc851x-*`).

The material comes from static analysis plus earlier read-only sysfs
snapshots. Nothing was triggered on the device.

## Power-path ICs

| IC | role | DT node (Linux bus) | addr | IRQ | Linux names | driver |
|---|---|---|---|---|---|---|
| MT6375 | 1S switching charger, BC1.2, TCPC, OTG boost, PMIC gauge | `/soc/i2c@11280000/mt6375@34` (i2c-5) | 0x34 | subpmic eint | `primary_chg`, psy `mtk-gauge`, regulator `usb-otg-vbus` | mt6375*, tcpc_mt6375 (exact) |
| SC8571 **master** | 2S 2:1 switched-cap direct charger | `/soc/i2c@11d71000/sc8571@66` (**i2c-11**) | **0x66** | GPIO **4**, falling (`<&pio 4 2>`), thread `sc8571-master-irq` | charger_class **`primary_dvchg`**, psy `sc-cp-master` | sc8571_charger (34/34 exact) |
| SC8571 **slave** | same, parallel | `/soc/i2c@11e01000/sc8571@67` (**i2c-6**) | **0x67** | GPIO **18**, falling, `sc8571-slave-irq` | **`secondary_dvchg`**, psy `sc-cp-slave` | same module |
| SC8510 | 2S↔1S bidirectional 2:1/1:2 switched-cap converter + load switch | `/soc/i2c@11e01000/sc851x-charger@6f` (i2c-6), `reg=<0x69>` | **0x69** (`@6f` suffix is stale) | GPIO **12**, falling, `sc851x-irq` | none (no charger/psy/regulator) | sc851x_charger (11/11 exact) |
| SH366003 | 2S pack fuel gauge | `/soc/i2c@11c24000/sh366003@55` (i2c-9, 400 kHz) | 0x55 | none | psy **`3rd-gauge`** | sh366003_fg (PARTIAL) |

Bus numbers come from DT `aliases` (`i2c6 = /soc/i2c@11e01000`,
`i2c9 = /soc/i2c@11c24000`, `i2c11 = /soc/i2c@11d71000`). They agree with the
live device names in the earlier snapshots (`11-0066`, `6-0067`, `6-0069`,
`9-0055`).

Exactly **two** SC8571 instances exist. The single driver binds three
compatibles (`sc,sc8571-standalone|master|slave`, with mode data 0/1/2), and
the board instantiates master and slave only. The master and the slave sit
on **different** I2C controllers. The slave shares i2c-6 with SC8510.

## Master / slave identification (proof chain)

1. **DT:** `compatible = "sc,sc8571-master"`, `charger_name = "primary_dvchg"` at
   i2c-11@0x66. `compatible = "sc,sc8571-slave"`, `charger_name = "secondary_dvchg"`
   at i2c-6@0x67.
2. **sc8571_charger (exact):** `charger_device_register(sc->chg_dev_name, …)`.
   The psy name is `sc8571_psy_name[mode]`. The slave additionally writes
   `VBUS_IN_RANGE_DIS=1` in `init_device`.
3. **mtk_pe5_hal.c (exact):** `mtk_chgdev_desc_tbl[] = { primary_chg, primary_dvchg,
   secondary_dvchg }` maps to `CHG1`, `DVCHG1` and `DVCHG2`.
4. **mtk_pe5.c (exact):** `pe50_dump_charging_info()` stores
   `pca_master_ibus = ibus[PE50_DVCHG_MASTER]`, which is read from `DVCHG1`,
   and `pca_slave_ibus = ibus[PE50_DVCHG_SLAVE]`, which is read from `DVCHG2`.

Therefore:

- **`pca_master` = SC8571 @ i2c-11/0x66.**
- **`pca_slave` = SC8571 @ i2c-6/0x67.**
- `pca_voltage` = the VBUS ADC read through `pe50_get_adc(VBUS)`, which uses
  DVCHG1 (the master).

These sysfs nodes are on the `pe5` platform device.

## Electrical architecture (inferred from DT units plus silicon class)

```
USB-C VBUS ──┬── MT6375 buck (1S domain, AICR/ICHG, CV 4.45 V "cell-equivalent")
             │        │
             │        └── 1S system rail (VSYS-equivalent) ──┐
             │                                               │ SC8510 V1X side
             │                                       SC8510 2:1 / 1:2 (autonomous)
             │                                               │ SC8510 V2X side
             ├── SC8571 master 2:1 ──────────────────────────┼── 2S battery pack (~7.0–8.8 V)
             └── SC8571 slave  2:1 ──────────────────────────┘        │
                                                              SH366003 pack gauge (i2c-9)
```

Each statement below is backed by the evidence named after it:

- **SC8571 output is the 2S pack.** `VBAT_OVP=90` decodes to 8.8 V. PE5
  `vbat-cv=8750 mV`, `start-vbat-max=8600`, `force-ta-cv-vbat=9000`. The
  gauge reports about 8.4 V at full.
- **SC8571 input is a high-voltage PPS VBUS (2:1).** PE5 `vta-cap-min=13600`,
  `vta-cap-max=20000 mV`. VBUS_OVP is 20.4 V on the master and 17.8 V on the
  slave. IBUS_OCP is 7250 mA. The PE5 dual-charger ITA levels are
  6000/4500/3400/2000 mA at the TA. That is up to about 120 W TA-side, which
  matches the device's 120 W marketing. The marketing claim is used only as a
  cross-check.
- **The MT6375 / MTK charger framework runs in 1S "cell-equivalent" units.**
  `mtk_charger battery-cv = 4450000 µV`. The JEITA CVs are 4.25–4.35 V.
  `min-charger-voltage = 4.5 V`. The framework passes its 1S CV to PE5
  through `set_current_limit`. **PE5 stores `cv*2` (the YFT delta), which
  converts the 1S limit into the 2S pack domain used by the SC8571 VBAT
  ADC.** This is the direct software proof that the dvchg side sees the pack
  voltage while the switching charger sees a cell-equivalent voltage.
- **SC8510 sits between the 2S pack (V2X) and the 1S domain (V1X).** Its DT
  fields name `v2x-ovp/uvlo`, `v1x-ovp/scp`, `fwd-ocp` (2S→1S, discharge)
  and `rvs-ocp` (1S→2S, charge). The driver writes no
  mode/direction/enable/OTG field, so the direction follows the source side
  in hardware. See `../sc8510/README.md`.

Physical wiring is not proven: no schematic is available. The diagram is
the minimum topology consistent with every DT unit and driver behaviour;
alternatives are discussed in `battery-topology.md`.
