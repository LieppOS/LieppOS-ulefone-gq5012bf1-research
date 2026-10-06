# RT5133 — hardware / DT topology on GQ5012BF1

## Verdict

```text
RT5133_ROLE_ON_GQ5012BF1   = NONE (inactive MTK platform capability)
DT_NODE                    = present, inherited verbatim from MTK base mt6878.dts
DRIVER_LOADED              = YES  (rt5133-regulator.ko, first stage, vendor_boot modules.load #123)
DRIVER_BOUND               = NO   (probe aborts at the first I2C transaction)
REGULATORS_REGISTERED      = 0 / 9   (BASE + LDO1..LDO8 never registered)
GPIO_CHIP_REGISTERED       = NO   (rt5133-gpio1/2/3 fixed regulators stay "deferred probe pending")
DT_CONSUMERS               = 0    (only RT5133's own GPO fixed-regulators reference its rails)
CAMERA_LDO_ON_THIS_BOARD   = WL2864C/WL2868C at 11-0029 (bound, custom-ldo-wl2868.ko)
```

The older component claim "live `buses.txt`: 5-0018 → driver `rt5133` (bound)"
was a misreading of the capture format and is **withdrawn** (see §3).

## 1. DT node (stock, live FDT)

Path `/soc/i2c@11280000/rt5133@18`; alias `i2c5 = "/soc/i2c@11280000"`, so the
client is `5-0018`. Full node: [`stock-live-dt-rt5133-node.dts`](stock-live-dt-rt5133-node.dts).

| property | stock value | meaning |
|---|---|---|
| `compatible` | `"richtek,rt5133"` | matched by `rt5133_ofid_tbls` |
| `reg` | `0x18` | 7-bit I2C address |
| `interrupts-extended` | `<&pio 19 IRQ_TYPE_EDGE_FALLING>` | EINT19, falling edge |
| `enable-gpio` | `<&pio 1 0>` | **GPIO1**, active-high HWEN |
| `gpio-supply` | `<&rt5133_ldo1>` | GPO block supplied by own LDO1 (unused by driver) |
| `gpio-controller`, `#gpio-cells = <2>` | | 3 GPO lines |
| `wakeup-source` | | inert: the driver never calls `device_init_wakeup()`/`enable_irq_wake()` |
| `regulators/BASE` | `oc-shutdown-all = 0`, `pgb-shutdown-all = 0` | |
| `regulators/LDO1` | 2.80 V fixed | `vout_type1` |
| `regulators/LDO2` | 1.80 – 3.20 V | `vout_type1` |
| `regulators/LDO3..LDO6` | 1.70 – 3.00 V | `vout_type2` |
| `regulators/LDO7` | 0.90 – 1.20 V | `vout_type3` |
| `regulators/LDO8` | 0.855 – 1.20 V | 0.855 V exists only in `vout_type4` → reference DT targets the **RT5133A** die |
| every LDO | `regulator-active-discharge`, `oc-ptsel = 1`, `pgb-ptsel = 1`, `soft-start-time-sel = 1` | `regulator-active-discharge` is valueless; GKI 6.1 parses it as u32 → ignored even on a populated board |

Plus three `/rt5133-gpio{1,2,3}` `regulator-fixed` nodes (2.80 V, `vin-supply = <&rt5133_ldo1>`,
`gpio = <&rt5133 {0,1,2} 0>`, active-high) and an empty `/rt5133-eint` node.

### Provenance of the node

* It is in the **SoC base DTB** (`model = "MT6878"`, vendor_boot), **not** in the
  GQ5012BF1 board DTBO (0 occurrences of `rt5133`).
* Property-by-property comparison against ALPS
  `arch/arm64/boot/dts/mediatek/mt6878.dts @ 5e415e059253` (lines 12217ff and
  11895ff): **68/68 equal** — [`dt-source-vs-live.tsv`](dt-source-vs-live.tsv).
* `rt5133.dtsi` (the generic include, GPOs at 1.8 V, EINT 187/HWEN 188) is
  **not** what ships; the inline `mt6878.dts` node is.

## 2. Consumers

Exhaustive scan of every `*-supply`, `gpio`, `gpios`, `*-gpios` property in
two independent dumps (offline merged FDT `phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`
and live `/proc/device-tree` `usmart-audit/dt/live-merged.dts`) for all 13
RT5133 phandles (`0x14c` device, `0xea`/`0x24b`–`0x251` LDO1–8,
`0x2b9`–`0x2bb` GPO regulators, `0x2b8` eint):

| referrer | property | target |
|---|---|---|
| `rt5133@18` | `gpio-supply` | LDO1 (self) |
| `rt5133-gpio1/2/3` | `vin-supply` | LDO1 |
| `rt5133-gpio1/2/3` | `gpio` | `rt5133@18` GPO 0/1/2 |

Nothing else. No stock `.ko` contains the string `rt5133` other than
`rt5133-regulator.ko` itself, so there is no by-name `regulator_get()` either.
Camera sensors draw from `/odm/camera-common-*` and the WL2864C (`11-0029`).
The MTK *reference* camera DT (`cust_mt6878_camera_v4l2.dtsi`, wiring
sensors to RT5133 LDO1/2/3/6/7 and GPO2/3) is not part of the stock image.

Per-rail table: [`consumer-map.tsv`](consumer-map.tsv).

## 3. Runtime binding — corrected

`workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt`
records, per I2C device: resolved `driver` link, resolved `driver/module`
link, client `name`, `modalias`. For bound clients line 1 is
`/sys/bus/i2c/drivers/<drv>`; when no driver is bound, `readlink -f` returns
the literal `…/<dev>/driver` path.

```text
11-0029  /sys/bus/i2c/drivers/wl2864c                       <- bound
5-0018   /sys/devices/platform/soc/11280000.i2c/i2c-5/5-0018/driver   <- NOT bound
         rt5133                                              <- client *name*, not driver
5-0075   /sys/devices/.../i2c-5/5-0075/driver  rt6160        <- same shape, documented unbound
```

18 records have the unbound shape: `0-0041`, `0-0048`, `5-0018`, `5-0075`,
`6-0075` and the 13 bare adapters. Bus 5 itself is live (`5-0034` → `mt6375` bound).

Independent corroboration (stock kernel + stock vendor_boot, GSI system):
`evidence/boot-hang-2026-08-29/pstore/ulefone-pstore-v9-validated-baseline/console-ramoops-0`

```text
[14.820258] platform rt5133-gpio3: deferred probe pending
[14.820265] platform rt5133-gpio1: deferred probe pending
[14.820268] platform rt5133-gpio2: deferred probe pending
```

— the GPO fixed regulators never obtain their GPIO because the RT5133
`gpio_chip` is only registered at the end of a successful probe.

## 4. Why the probe fails (static proof)

`rt5133_probe()` (exact stock code, see [`../power-sequence.md`](../power-sequence.md))
performs **no I2C traffic** until `rt5133_validate_vendor_info()` reads
`CHIP_INFO` (0x00) through the CRC-8 regmap bus. Any of NACK, short read or
CRC mismatch returns an error and the probe aborts with
`Failed to check vendor info [%d]`. A *responding* chip with an unknown vendor
nibble would instead leave `priv->cdata == NULL` (the `IS_ERR()` test can never
fire) and oops in `devm_regulator_register()` — the stock device boots cleanly,
so that branch is excluded. Therefore:

> **No RT5133/RT5133A answers a CRC-valid read of register 0x00 at 5-0018 on
> the stock GQ5012BF1 boot.**

Whether the footprint is unpopulated or the part is unpowered cannot be
separated statically; the GPIO1 reassignment below makes "not populated
(substituted by WL2864C)" the only coherent board design.

## 5. GPIO1 is shared with the WL2864C camera LDO — functional coupling

| | GPIO1 use |
|---|---|
| MTK base DT | `rt5133@18` `enable-gpio = <&pio 1 0>` (HWEN) |
| GQ5012BF1 board DT | `pmu@wl2864c` (`11-0029`) `reset-gpios = <&pio 1 0>` |

Sequence on every stock boot:

1. first stage, `rt5133-regulator.ko` (vendor_boot `modules.load` #123):
   `devm_gpiod_get_optional(dev, "enable", GPIOD_OUT_HIGH)` → **GPIO1 driven high**;
   CHIP_INFO read fails; devres releases the descriptor; the pin keeps its
   last level (output, high).
2. second stage, `custom-ldo-wl2868.ko` (vendor_dlkm `modules.load` #102):
   `devm_gpiod_get(dev, "reset", …)` succeeds because RT5133 no longer owns it.

Consequence for LieppOS: **the RT5133 probe failure is load-bearing.** If the
RT5133 driver ever bound (wrong DT, a stub responding at 0x18), it would keep
GPIO1 and `custom-ldo-wl2868` would fail with `-EBUSY`, taking down every
camera rail. Removing the module is harmless; making it succeed is not.
