# MT6375-CHARGER — closure (2026-10-07, static)

Workspace component: `Reverse Engineer - PARTIAL/MT6375-CHARGER` → **DONE**.

## Selection log

SELECTED TARGET: `MT6375-CHARGER`. VERIFIED: present in `Reverse Engineer - PARTIAL/`
and listed as PARTIAL in the status index.

WHY: the remaining blocker is listed as "full charger source parity". The
power-charging pass of 2026-10-03 had already measured `mt6375-charger` 78/78
and `mt6375-battery` 332/332. The PMIC core modules (`mt6375` MFD,
`mt6375-adc`, `mt6375-auxadc`) belong to no other component and had never been
parity-built. All of them have public MTK ALPS sources.

CURRENT BLOCKERS (as recorded):
1. "Full charger source parity". Its own `source/` held only a build-only
   `yft_usb_flag` ABI witness.
2. "Live charging-protocol validation".

## Scope

The MT6375 sub-PMIC on `i2c-5` at 0x34 (`mt6375@34`; EINT15 level-low; MFD
with an internal IRQ controller). It covers five charger-side modules:

| module | role |
|---|---|
| `mt6375` | MFD core, IRQ domain, sub-address dummies `5-001a`/`5-003f` |
| `mt6375-adc` | charger ADC (IIO) |
| `mt6375-auxadc` | PMIC AUXADC (IIO) |
| `mt6375-charger` | `primary_chg` psy, BC1.2, OTG VBUS regulator, charger_class device |
| `mt6375-battery` | MTK gauge + battery algorithm, `battery` psy |

Neighbours (already DONE, referenced only):
* TCPC (`tcpc_mt6375`: TCPC-MT6375);
* the class/framework/PE modules (`reverse-engineering/power-charging`);
* SC8571/SC8510 pumps and the SH366003 gauge.

## Result

| module | stock (stripped rebuild compared) | result |
|---|---|---|
| mt6375 | 26 424 B | 18/18 functions, 22/22 data, 39/39 versions; **differs only in build-id** |
| mt6375-adc | 21 736 B | 6/6, 20/20, 27/27; **build-id only** |
| mt6375-auxadc | 52 592 B | 23/23, 40/40, 68/68; **build-id only** |
| mt6375-charger | 117 904 B | 78/78, 56/56, 80/80, `yft_usb_flag` export CRC; **build-id only** |
| mt6375-battery | 607 152 B | 330/330, 115/115, 136/136; **build-id only** |

In all five, section headers and the ordered symbol table are identical
(`parity/mt6375-parity.txt`, per-symbol `parity/*-parity.tsv`). The two clean
builds match (B1 == B2) for every `.ko` (`parity/b1-b2-build.txt`).
Integration checks pass 19/19 (`evidence/integration-checks.txt`).

Two new pieces of work closed the gap:
1. **`mt6375.ko` YFT/ODM delta, reconstructed here.** The stock IRQ thread
   collects non-empty event bytes into a bitmap with atomic `set_bit`; that
   atomic is what produces the extra `alt_cb_patch_nops` import. It then acks
   only the range `ffs..fls` with one `regmap_bulk_write` and returns
   `IRQ_NONE` when every event is masked. The handler loop is still the old
   forward one that skips GM30.
   * This is a hybrid: the bitmap ack is later-ALPS code (seen in the Volla
     mt6878 tree), but the old handler loop is kept. No public version is
     exact.
   * The VOLLA/Xiaomi variants (reverse loop, `IRQ_HANDLED`, coverity clamps,
     `max_raw_*`) are **not** stock.
2. **`mt6375-battery` line layout.** The earlier "332/332 exact" claim was
   function-level only: three `WARN_ON` `__bug_table` line numbers still
   differed. Stock has 189 more lines before `force_get_tbat_internal`'s WARN
   and 2 fewer before `battery_update_routine`'s. This is reproduced with
   non-code lines; their text cannot be recovered and is declared as such.
   No public mtk_battery.c (106 kdm, 37 volla and 42 Nothing revisions
   scanned) has stock's 1343/3544/3557 WARN lines.

`mt6375-adc` and `mt6375-auxadc` are unmodified ALPS 5e415e059253. The
auxadc build also needs the matching ALPS `dt-bindings` headers.

Source: KDM workspace commits `9f4d03b`, `6863ff1` and `6d18b45` on pristine
ALPS bases. The delta is in `source/gq5012bf1-over-alps-5e415e059253.patch`,
and the per-module map is in `source/SOURCES.tsv`.

## Behaviour summary (GQ5012BF1 deltas that matter for a port)

* **Charger:**
  * The charger registers a TCPC PD notifier on `type_c_port0`. When PD
    reaches PE_READY_SNK* it sets `pd_status`, and while `pd_status` is set,
    a BC1.2 result is reported as **CDP** (USB type and psy type).
  * When `yft_usb_flag == 1` (internal thermal-camera USB session),
    `set_usbsw` returns early and PD-ready re-queues BC1.2.
  * `yft_usb_flag` is an `EXPORT_SYMBOL_GPL` int consumed by
    `yft_tiny2c_usb` and `extcon-mtk-usb`.
  * psy `CURRENT_MAX` returns the **SH366003 `3rd-gauge` CURRENT_NOW**, and
    `VOLTAGE_MAX` is fixed at 5 V.
  * Status `NOT_CHARGING` is reported as `CHARGING`.
  * New charger op `is_otg_enabled` (reads `F_FORCE_VBUS_SINK`, 3 retries).
  * Init sets TMR bit1 (IEOC deglitch).
  * The power-ready delayed work waits 4 s instead of 2 s.
* **Battery:**
  * The daemon's SOC, UI-SOC, RTC-UI-SOC and CON0 SOC, and the battery psy
    capacity, all come from `3rd-gauge`; the MT6375 coulomb counter is not
    authoritative.
  * Adds a BAT_TEMP sysfs field.
  * `SHUTDOWN_GAUGE1_XMINS` = 0.
  * Defines `BAT_LOW_TEMP_PROTECT_ENABLE` in `mtk_charger.h`.
* **Live stock:**
  * `5-0034` is bound to `mt6375`.
  * `battery` and `primary_chg` psys live under it.
  * `mt6375-chg` dumps CC/AICR/MIVR/IEOC/CV every 10 s (example: CC 500 mA,
    CV 4450 mV).

## Boundaries (external, not blocking)

* Live charging-protocol traces, delivered power and thermal derating are
  runtime/physical. They are integration work, as the DONE definition allows.
* PD/PPS policy lives in `tcpc_class`/`rt_pd_manager` and the PE modules
  (DONE elsewhere). UFCS is refuted for this board; see
  PD-PPS-UFCS/USB-CHARGER-INTEGRATION.
* Intermodule import CRCs are 9/9 and equal to the stock providers'. Those
  providers (`charger_class`, `tcpc_class`, `industrialio-triggered-buffer`,
  `aee_aed`, `pmic_lbat_service`) are linked through stock-harvested symvers,
  as in the power-charging pass. `charger_class` and `tcpc_class` are
  themselves source-built in DONE packs.

## Files

* `source/`: delta patch and `SOURCES.tsv`. The full trees are the KDM
  workspace commits listed above.
* `scripts/`:
  * `build_b1_b2.sh`;
  * `ko_parity.py`, `elfmini.py`, `fdis.py`;
  * `mt6375_integration.py`.
* `parity/`: `b1-b2-build.txt`, `mt6375-parity.txt`, `<module>-parity.tsv`.
* `evidence/integration-checks.txt`.
* `stale-claims.md`, `STATUS.md`.
