# SH366003 pack fuel gauge ("3rd-gauge"): PARTIAL

## Status

Protocol, register map, AFI interpreter, power_supply contract and consumers
are statically closed. **Exact source parity is not**: the current
reconstruction (`kernel_device_modules-6.1/drivers/power/supply/sh366003/`,
from `lieppos/sh366003-recon`) is behaviour-equivalent but matches only
**2/39 functions and 18/30 data objects**. The ABI matches on imports
(35/35), modinfo and vermagic. Modversions and section sizes differ.

The remaining gap is labour, not a hardware or data blocker:

- the stock module is about 16 KB of code built from SinoWealth's
  "2022.10.17" Linux template plus YFT glue;
- every log line is `__LINE__`-locked (190 … 2490), so an exact rebuild
  must reproduce the original line layout;
- no public donor of this template was found. The closest public relative,
  OnePlus `oplus_sh366002.c`, is a different architecture: bq27541
  glue and a DT-sourced AFI.

The functions with decoded control flow are listed below, so the rewrite
is mechanical.

| item | value |
|---|---|
| stock module | `vendor-ramdisks/platform-extracted/lib/modules/sh366003_fg.ko` (load order 134, before `pd_dbg_info`/tcpc) |
| depends | `yft_devinfo` (`yft_fuelgauge_device_add`, `yft_set_fuelgauge_device_used`, `fuelgauge_fw_version`) |
| bus | `/soc/i2c@11c24000` = **i2c-9**, `sh366003@55`, 400 kHz, **no IRQ** (polling only) |
| identity | SBS control 0x0001 (`regs[15] = 0x04000001`) must read **0x0603**; manufacturer name block MAC 0x004c; `fw_version` string `Vno:0x%02x-%s(%02d%02d)` |
| psy | **`3rd-gauge`** (also the class name `/sys/class/3rd-gauge/`) |
| logging | `fg_sh366003_log` lives in `.data` and is **initialised to 1**, so all `[sh366003]` notices are on in stock |

### Why "3rd-gauge"

The `battery` psy (mt6375-battery) and `mtk-gauge` (the MT6375 PMIC coulomb
counter) already exist. The SinoWealth pack gauge is the third gauge-type
supply on the board, and YFT made it authoritative: every SOC, current and
voltage that the framework, PE/PD/PE5 and the `battery` psy report is
proxied from it (see `../yft-power-deltas.md` #1, 9, 14, 15, 19). The name
is stock-literal; its meaning is inferred from the board topology.

## power_supply contract (exact jump table)

| prop | value |
|---|---|
| STATUS (0) | charger online (`adapter_status` 1/2) → `FULL` if soc == 100, else `CHARGING`; otherwise `DISCHARGING` |
| HEALTH (2), PRESENT (3) | constant 1 |
| TECHNOLOGY (6) | 2 (LION) |
| CYCLE_COUNT (7) | SBS 0x2a |
| VOLTAGE_NOW (12) | SBS 0x08, **pack mV** (mt6375-battery multiplies by 1000) |
| CURRENT_NOW (17) | \|SBS 0x0c\| × 1000, **unsigned µA** (direction is lost) |
| CHARGE_FULL_DESIGN (22) | **learned FCC** (SBS 0x12, mAh), not the design capacity |
| CAPACITY (47) | SBS 0x2c RSOC |
| TEMP (52) | SBS 0x06 − 2731 (0.1 °C) |
| any other | `-EINVAL` |

Supplied-from: 3 names. `external_power_changed` re-queues the monitor
work immediately.

## Data path to Android

```
SH366003 (i2c-9@0x55, SBS/MAC)
  → sh366003_fg monitor work (every 1250 jiffies = 5 s, HZ = 250)
  → psy "3rd-gauge"
     → mt6375-battery "battery" psy (CAPACITY, CURRENT, VOLTAGE, CYCLE, CHARGE_FULL_DESIGN)
       → Android BatteryService / health HAL
     → mt6375-battery daemon: every SET/GET SOC overridden
     → mtk_charger_framework get_uisoc
     → mtk_pep / mtk_pd_charging / mtk_pep50 start/stop SOC windows
```

## New static findings (this pass)

1. **Fallback snapshot bug (`fg_update_workfunc`).** Before an AFI program
   it sets `fallback_soc = fallback_voltage = fallback_current = soc` and
   `fallback_temp = temp`. During an update, `sh_fg_get_vbat()` and
   `sh_fg_get_ibat()` therefore return the SOC number.
2. **Probe "maybe upgrade failed" fake values.** When an update is needed
   and both SOC and voltage read 0, probe sets `soc = 4`, `voltage = 3600`,
   `temp = 256` and uses them as the fallback quartet with
   `use_fallback = 1`. The system boots seeing 4 %, 3.6 V and 25.6 °C until
   the update work clears `use_fallback`.
3. **SOH sysfs side effect (`soh_show`).**
   - Under 400 cycles: `soh = display_soh − cycles/40`.
   - At 400 cycles or more: `soh = display_soh − (cycles − 400)/60 − 10`.
   - In both cases the result is written back into `display_soh`, which is
     initialised to 100.
   - Every read of `/sys/class/3rd-gauge/soh` therefore lowers the reported
     SOH further.
4. **`fg_read_sbs_word` control branch.** After writing the subcommand to
   0x00, the 10 ms `mdelay` runs **only when the write failed**. The success
   path reads 0x00 immediately. The MAC branch always sleeps 3 ms.
5. **Update gate.** The update is refused when:
   - `adapter_status == 2`, i.e. on the charger; or
   - soc < 11; or
   - boot mode is 8 or 9 (KPOC).

   Trigger = `max(force_upgrade, 0) | auto`. A trigger of 0 means "Check
   version ok", with no I2C writes. A trigger of −1 runs only the run-state
   recovery: up to 5 retries; MAC 0x0041 reset when the stock V/I/termVolt
   test fails; MAC 0x0021 if OEMFlag bit 14 is clear; MAC 0x0067 if bit 15
   is clear; block 0x00c5; seal 0x0030; `hal_fg_init`.
6. **Auto trigger.** The update runs automatically when MAC 0x004d differs
   from **0x5a93** or FCC ≤ **3499**. When both reads of 0x0046 and 0x004d
   stay 0 after 5 tries, the auto trigger is set to −1.

## Gauge/profile/calibration boundary

| class | content | where |
|---|---|---|
| OPEN / reconstructed | SBS/MAC protocol, unseal keys `5678 1234 cdef 90ab` → MAC 0x0054 bits 0x0300, block-read checksum `~(cmd + data) & 0xff` and len = data + 4, AFI interpreter (op 1/2/3/4), state machine, sysfs | this repo, `kernel/phase4-sh366003-*.md` |
| DEVICE-SPECIFIC (not copied) | embedded AFI/profile program `sinofs_afi_data` | stock `.rodata+0x35`, **2142 B, SHA-256 `4888c5bc4b847ec6c118cd7bd334cbcffbf52c5fa2bf8f8660c3ac65e03359e1`**; 209 records (104 writes, 104 waits, 1 compare), all to 8-bit address 0xaa (7-bit 0x55); data-flash 0x4000–0x47b8 through 0x3e and embedded checksums through 0x60; final compare expects AFI **0x8cd3** |
| DEVICE-SPECIFIC (in-gauge) | learned FCC, cycle data, calibration (CADC), lifetime data | in the gauge's own flash; the driver never reads, writes or backs it up |

The private build tree keeps the AFI as `sinofs_afi_data.inc`, used only to
reproduce the stock binary. It is not copied into this public RE directory.
AFI programming in the reconstruction is fail-closed unless it is built with
`SH366003_ALLOW_AFI_PROGRAMMING=1`.

## Remaining to reach DONE

The only remaining step is a byte-exact rewrite of `sh366003_fg.c` with the
stock `__LINE__` layout. Line anchors already extracted:

| function | line(s) |
|---|---|
| `__fg_read_word` | 190 |
| `__fg_write_word` | 204 |
| `__fg_write_buffer` | 384 |
| `sh_fg_get_batt_info` | 480 / 501 / 507 |
| `fg_decode_iic_write` | 560 / 576 |
| SOC | 619 |
| VCHG | 641 |
| ICHG | 663 |
| BatteryStatus | 685 |
| Voltage | 714 |
| Current | 743 |
| ExtTemp | 768 |
| IntTemp | 796 |
| soh | 815 |
| cycnt | 834 |
| rc | 853 |
| fcc | 871 |
| device id | 912 / 916 |
| `fg_init` | 926 |
| unseal | 962–969 |
| seal | 987 |
| manufacturer name | 1016 / 1020 |
| serial | 1037 / 1041 |
| maxvoltage | 1057 / 1065 |
| `IntManufacturedate` | 1080 / 1086 |
| date write | 1101–1133 |
| runstate | 1456 / 1498 |
| `Check_Chip_Version` | 1511–1568 |
| `file_decode_process` | 1597–1797 |
| `fg_check_charge_type` | 1841 |
| monitor | 1878 / 1881 |
| `ext_power_changed` | 1968 |
| psy init | 1985 |
| `hal_fg_init` | 2000 / 2007 |
| date store | 2057–2066 |
| boot mode | 2151–2168 |
| update | 2185–2236 |
| probe | 2294–2403 |
| shutdown | 2429 |
| init | 2463–2476 |
| exit | 2488 / 2490 |

No runtime access is required.
