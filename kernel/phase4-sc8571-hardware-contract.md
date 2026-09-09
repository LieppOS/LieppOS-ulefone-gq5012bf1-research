# GQ5012BF1 SC8571 hardware and framework contract

## Safety and evidence boundary

This contract is recovered only from the frozen stock ELF, the committed DT
snapshot, exact-GKI headers, the stock `charger_class.ko`, and public SC8571
register-map donors. No module was loaded, no driver was rebound, and no phone
register/GPIO/charging/PD operation was performed.

## Board topology

| role | compatible | parent / Linux bus | I2C address | charger-class name | power-supply name | IRQ GPIO | stock IRQ thread |
|---|---|---:|---:|---|---|---|---|
| master | `sc,sc8571-master` | `i2c@11d71000` / 11 | `0x66` | `primary_dvchg` | `sc-cp-master` | controller phandle 137, line 4, flags 2 | `irq/49-sc8571-master-irq` |
| slave | `sc,sc8571-slave` | `i2c@11e01000` / 6 | `0x67` | `secondary_dvchg` | `sc-cp-slave` | controller phandle 137, line 18, flags 2 | `irq/63-sc8571-slave-irq` |

The single I2C driver also accepts `sc,sc8571-standalone`. Its OF match data
selects role integers 0/1/2 for standalone/master/slave. The board has no
standalone node. The I2C core supplies the addresses; the module hard-codes
neither `0x66` nor `0x67`.

All roles must report device ID `0x41` from register `0x22`; otherwise probe
returns `-EINVAL`. The stock module has no OF alias and is explicitly loaded
(normal zero-based index 147, recovery index 145).

## Probe and initialization

Probe performs, in order:

1. allocate an 872-byte zeroed private object;
2. initialize 8-bit/8-bit regmap with maximum register `0x42`;
3. allocate all 58 regmap fields;
4. read and validate device ID `0x41`, and publish lowercase hex `41` through
   the global `chipid` class attribute;
5. create device sysfs `registers` (mode 0660; return ignored);
6. resolve standalone/master/slave from OF match data;
7. require all 40 scalar DT properties, require `sc8571,intr_gpio`, and read
   optional `charger_name` (fallback `charger`);
8. assert register reset (`0x0f[7]=1`), sleep 10 ms, then write all 40 DT raw
   encodings;
9. for slave only, force `VBUS_IN_RANGE_DIS` (`0x05[2]`) to 1 after the DT
   write;
10. register a `POWER_SUPPLY_TYPE_MAINS` device;
11. request a falling-edge, oneshot threaded IRQ and call
    `irq_set_irq_wake(irq, 1)`;
12. register the DT-selected `charger_device` with `sc8571_chg_ops` and alias
    `sc8571_chg`;
13. create per-probe classes `fastcharge_0`, `fastcharge_1`, ... with read-only
    `chipid`.

The initialization loop logs individual field-write errors but continues,
including after a failed reset write. Its return is the last write status (or
the slave override status), matching stock.

Stock error-path quirks are preserved: a missing OF match reaches cleanup with
the prior zero status; a NULL (rather than ERR_PTR) charger registration can
likewise produce zero through `PTR_ERR_OR_ZERO`; charger-registration failure
does not explicitly unregister the already-created power supply, while IRQ
registration failure does; remove explicitly unregisters the devm power supply
and frees devm state. The sysfs/class creations are not unwound on later probe
failure. These are oracle facts, not recommended new-driver patterns.

The full raw property/field ledger is in:

- `phase4-sc8571-dt-contract.tsv`
- `phase4-sc8571-register-fields.tsv`

DT values are raw register encodings, not physical units.

## Register model

The stock table has exactly 58 `struct reg_field` entries (1,160 bytes), over
registers `0x00..0x23` and vendor extension registers `0x40..0x42`. Key groups:

- `0x00..0x08`: VBAT/IBAT/VBUS/IBUS protection and alarm thresholds;
- `0x0a..0x0d`: thermal disable/threshold fields;
- `0x0e`: VAC1/VAC2 OVP and pull-down control;
- `0x0f`: reset, OTG, charge enable, conversion mode and ACDRV status;
- `0x10..0x12`: switching frequency, watchdog, sense resistor, soft-start,
  UCP debounce and VOUT OVP;
- `0x17`: charge-pump switching and VBUS high/low error status;
- `0x22`: device ID;
- `0x23`: ADC enable;
- `0x40..0x42`: ACDRV manual controls, VBUS/PMID2OUT disables/thresholds and
  PMID2OUT flags.

The public OPLUS SC8571 source agrees on coordinates and physical scales and is
used only as a register-map naming/scale donor. It is not behaviorally or
framework-equivalent to stock.

### Board protection encodings

| protection | master raw / physical | slave raw / physical | enabled? |
|---|---|---|---|
| VBAT OVP | 90 / 8.80 V | 90 / 8.80 V | yes |
| VBAT OVP alarm | 70 / 8.40 V | 70 / 8.40 V | no (`alarm-dis=1`) |
| IBAT OCP | 81 / 8.10 A | 81 / 8.10 A | yes |
| IBAT OCP alarm | 80 / 8.00 A | 80 / 8.00 A | no (`alarm-dis=1`) |
| VBUS OVP | 64 / 20.40 V | 38 / 17.80 V | yes |
| VBUS OVP alarm | 64 / 20.40 V | 34 / 17.40 V | no (`alarm-dis=1`) |
| IBUS OCP | 25 / 7.25 A | 25 / 7.25 A | yes |
| VAC1/VAC2 OVP | 7 / 24.0 V | 7 / 24.0 V | yes |
| TDIE alarm | 200 (saturating raw byte) | 200 | configured; `TDIE_ALM_DIS` is allocated but untouched |
| VOUT OVP | code 3 / 10.0 V | code 3 / 10.0 V | disabled (`vout-ovp-dis=1`) |

Both roles disable TSBUS/TSBAT fault comparators and thermal shutdown through
DT (`*_dis=1`). Both program TSBUS/TSBAT raw threshold 21. Exact thermistor
conversion is not claimed because stock exposes no conversion and no board
thermistor transfer function is available.

Both roles select FSW code 4 (500 kHz), soft-start code 7 (13 s), UCP-fall
debounce code 1 (5 ms), and VBUS/VAC pull-down fields 0. Master selects 5 mΩ
IBAT sense (`ibat-sns-r=1`); slave selects 2 mΩ (`0`).

## Charger-class ABI and behavior

The sole intermodule import is:

```text
charger_device_register  CRC=0x36325d38  provider=charger_class
prototype = struct charger_device *charger_device_register(
              const char *name, struct device *parent, void *devdata,
              const struct charger_ops *ops,
              const struct charger_properties *props)
```

`sc8571_chg_ops` is exactly 648 bytes (81 pointer slots). Fourteen slots are
non-NULL: 4, 5, 39..48, 63 and 64. They are respectively `enable`,
`is_enabled`, six protection setters, two alarm-reset stubs,
`is_vbuslowerr`, `init_chip`, `get_adc`, and `get_adc_accuracy`.

Threshold callbacks accept micro-units, truncate to milli-units, clamp and
encode as follows:

| callback | encoding |
|---|---|
| `set_ibusocp` | clamp 1,000..8,000 mA; `(mA-1000)/250`, codes 0..28 |
| `set_vbusovp` | clamp 14,000..26,700 mV; `(mV-14000)/100`, codes 0..127 |
| `set_ibatocp` | clamp 0..12,700 mA; `mA/100`, codes 0..127 |
| `set_vbatovp` | clamp 7,000..9,540 mV; `(mV-7000)/20`, codes 0..127 |
| `set_vbatovp_alarm` | same VBAT encoding |
| `set_vbusovp_alarm` | same VBUS encoding |

`enable` writes `CHG_EN` (`0x0f[4]`) and then dumps every register
`0x00..0x42`. `is_enabled` intentionally reads `CP_SWITCHING_STAT`
(`0x17[6]`), not the command bit. `is_vbuslowerr` reads `0x17[3]`.
Both alarm-reset callbacks only log and return 0; they perform no clear write.
`init_chip` reruns reset plus all DT programming.

## ADC contract

Every conversion enables ADC (`0x23[7]`), waits 50 ms, bulk-reads two bytes
from `0x25 + 2*channel`, converts, then disables ADC. Only the bulk-read error
is propagated by the internal helper; ADC gate-write failures are logged.

| internal ch | signal | register | scale per raw LSB |
|---:|---|---|---:|
| 0 | IBUS | `0x25..0x26` | 2.5 mA |
| 1 | VBUS | `0x27..0x28` | 6.25 mV |
| 2 | VAC1 | `0x29..0x2a` | 6.25 mV |
| 3 | VAC2 | `0x2b..0x2c` | 6.25 mV |
| 4 | VOUT | `0x2d..0x2e` | 2.5 mV |
| 5 | VBAT | `0x2f..0x30` | 2.5 mV |
| 6 | IBAT | `0x31..0x32` | 3.125 mA |
| 7 | TSBUS | `0x33..0x34` | 0.09766 raw ratio unit |
| 8 | TSBAT | `0x35..0x36` | 0.09766 raw ratio unit |
| 9 | TDIE | `0x37..0x38` | 0.5 °C |

Charger-class mapping supports only VBUS, VBAT, IBUS, IBAT, TEMP_JC and VOUT.
Electrical channels are multiplied by 1000 for µV/µA; TDIE is not. The callback
sets min=max and always returns 0, even when the internal read fails. Reported
accuracies are 35 mV VBUS, 20 mV VBAT/VOUT, 150 mA IBUS, 200 mA IBAT and 4 °C
TDIE. Calling `get_adc_accuracy` for an unsupported channel reaches the stock
BUG/trap path.

The power-supply interface lists ONLINE, PRESENT, VOLTAGE_NOW, CURRENT_NOW,
CONSTANT_CHARGE_CURRENT, CONSTANT_CHARGE_VOLTAGE and TEMP. PRESENT is listed
but not implemented and returns `-EINVAL`. Successful ADC values are cached;
a failed read returns the prior cache. These power-supply ADC values remain in
mV/mA/°C, unlike charger-class electrical values. ONLINE set controls CHG_EN,
but `property_is_writeable` always returns 0.

## IRQ and fault handling

IRQ is falling-edge + oneshot and wake is enabled. The threaded handler logs
`INT OCCURED`, reads and logs every register from `0x00` through `0x42`, calls
`power_supply_changed()`, and returns `IRQ_HANDLED`.

There is no decoded fault state machine, no selective status/flag mask logic,
no explicit write-to-clear, no charger-device notifier, no retry/recovery, and
no automatic charge disable. Protection is silicon-register configuration;
fault visibility is raw dump plus power-supply notification.

## Watchdog, PM and shutdown

- `WD_TIMEOUT=0` selects 0.65 s, but `WD_TIMEOUT_DIS=1`; watchdog is disabled.
- `charger_ops.kick_wdt` and `kick_direct_charging_wdt` are NULL.
- suspend logs, optionally sets wake=1 when `device_may_wakeup`, then disables
  the IRQ;
- resume logs, optionally sets wake=0, then enables the IRQ;
- shutdown disables ADC only and prints the stock (misleading)
  `sc8571_enable_adc` message; it does not clear CHG_EN or reprogram watchdog.

## PD/PPS boundary

SC8571 is a charge-pump actuator/telemetry leaf. The module imports no adapter,
TCPM/TCPC, USB-PD, PPS, charger-algorithm or policy symbols. It does not request
PDO/APDO voltage/current and does not negotiate PD. Upstream MediaTek charging
policy reaches it only through the two named `charger_device` instances and
the 14 callbacks above. Therefore PD/PPS negotiation belongs outside this
module (stock load order places adapter/charger algorithm/PD manager/framework
modules before SC8571).

## Bounded unknowns

Static evidence does not prove board net names or analog tolerances beyond the
public register scale, whether every configured protection was exercised on
hardware, or higher-level PD policy decisions. Those require schematics or
prohibited live electrical testing and are not claimed.
