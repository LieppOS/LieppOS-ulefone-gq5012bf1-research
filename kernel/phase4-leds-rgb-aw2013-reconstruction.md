# Phase 4 — `leds_rgb_aw2013.ko` reconstruction (Ulefone Armor 29 Pro Thermal / GQ5012BF1)

Target: MediaTek MT6878 / MT6878T, GKI `ab/12901745`,
`common` @ `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.

---

## Final classification

```
SOURCE_DELTA_RECONSTRUCTION_EXACT
```

The reconstruction is a source-delta of the frozen exact-GKI donor
`common/drivers/leds/leds-aw2013.c`, and it rebuilds **byte-identically to the
stock module in every content-bearing ELF section**:

| section | stock | recon | result |
| --- | --- | --- | --- |
| `.text` | 3048 | 3048 | **byte-identical** |
| `.init.text` | 48 | 48 | **byte-identical** |
| `.exit.text` | 40 | 40 | **byte-identical** |
| `.rodata` | 728 | 728 | **byte-identical** |
| `.rodata.str1.1` | 1175 | 1175 | **byte-identical** |
| `.data` | 280 | 280 | **byte-identical** |
| `.init.data` | 8 | 8 | **byte-identical** |
| `.exit.data` | 8 | 8 | **byte-identical** |
| `__versions` | 1728 | 1728 | **byte-identical** (all 27 CRCs) |
| `.gnu.linkonce.this_module` | 1088 | 1088 | **byte-identical** |
| `.init.eh_frame` | 448 | 448 | **byte-identical** |
| `.note.Linux` | 48 | 48 | **byte-identical** |
| `.bss` | 13 (NOBITS) | 13 (NOBITS) | identical size + identical symbol offsets |
| `.modinfo` | 273 | 271 | differs **only** in `vermagic` |

8 / 8 functions byte-identical at identical offsets with identical KCFI type IDs.
170 / 170 relocations identical as a (type, target, addend) multiset.
26 / 26 imports, 27 / 27 MODVERSION CRCs, 0 / 0 exports.

The single residual is the `vermagic` SCM stamp, which is a property of *who
built it*, not of the source (details in **Residual differences**).

---

## Stock oracle

Full detail: `phase4-leds-rgb-aw2013-stock-oracle.txt`.

| field | value |
| --- | --- |
| path | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/leds-rgb-aw2013.ko` |
| copies | **1** (content hash searched across 735 `.ko` paths in the stock tree and the vendor blob tree — no duplicate) |
| size | 24856 bytes |
| SHA-256 | `97c86e3b3dd038c4fc90b73315aac966087a852d604f103fc166076bd28f7549` |
| build-id | `6470ceb27010efd6bd0f20ff10eb1144a74516ab` |
| ELF | ET_REL, EM_AARCH64, 38 sections, 102 symbols, PAC feature note |
| compiler | `.comment` is **empty**; toolchain identity proven structurally — rebuilds byte-identically with `clang-r487747c` (Android clang 17.0.2) from the exact GKI tree |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| name | `leds_rgb_aw2013` |
| author | `Nikita Travkin <nikitos.tr@gmail.com>` |
| description | `AW2013 LED driver` |
| license | `GPL v2` |
| aliases | `of:N*T*Cawinic,rgb,aw2013`, `of:N*T*Cawinic,rgb,aw2013C*` |
| depends | *(empty)* |
| parameters | none |
| srcversion | absent |

Placement: `modules.load` line 179/184, `modules.load.recovery` line 183,
`modules.dep` line 188 (`/lib/modules/leds-rgb-aw2013.ko:` — empty dep list),
`modules.alias` lines 1289–1290.  This module lives in the **vendor_boot
platform ramdisk**, not `vendor_dlkm`.

Live read-only evidence (`snapshots/live-stock-adb-20260831-115649/buses.txt`):
bound at `/sys/bus/i2c/devices/11-0045` to driver `leds-rgb-aw2013`, modalias
`of:Naw2013T(null)Cawinic,rgb,aw2013`.

---

## Source provenance

The decisive fact is **not** the chip name — it is the module author.

```
author=Nikita Travkin <nikitos.tr@gmail.com>
description=AW2013 LED driver
license=GPL v2
```

That is the **upstream mainline Linux** driver `drivers/leds/leds-aw2013.c`
(added by `59ea3c9faf32 leds: add aw2013 driver`), not an Awinic vendor driver.
For comparison, the Awinic vendor drivers on this same phone carry
`author=Alec <like@awinic.com>` (`aw36515`, `aw36518`).

Donor chosen: `gki-12901745-workspace/common/drivers/leds/leds-aw2013.c`
sha256 `8458f2aac83ccb6d996f88895b5e9ce953d3475019405ad869bde06a3c361b17`
at GKI `6b18f0b574ab` (identical to `kernel-research/android-common-gq5012bf1`;
the `nothing-mt6878` copy is an older revision, `e8c8d857c4fe…`).

`CONFIG_LEDS_AW2013` is **not** in `gki_defconfig`, so the stock module is an
out-of-tree/vendor-fragment build of that file — consistent with it shipping in
the vendor_boot ramdisk rather than in GKI.

Searches across every local kernel tree for `awinic,rgb,aw2013`, `led_aw2103`,
`led-fixed-brightness`, `aw2013-pwd-gpio` returned **zero** hits: the Ulefone/YFT
delta itself has no public source and had to be recovered from the binary.

---

## RED baseline

Full detail: `phase4-leds-rgb-aw2013-RED.md`.

The untouched donor was frozen at
`lieppos/aw2013-recon/donor-pristine/leds-aw2013.c`, given **build glue only**
(`obj-m += leds-aw2013.o` plus a `kernel_module()` rule — no `ccflags`, no `-D`,
no header shim, no source edit) and built against the exact GKI:

```
$ tools/bazel build //lieppos/aw2013-recon/donor-build:leds_aw2013_donor
BUILD_RC=0   warnings=0   modpost warnings=0   unresolved=0
leds-aw2013.ko  19928 B  sha256 735c71718dee68b97d8748b72040b9fc8540d7b0a428eb5c8293a7454ff56ffa
```

Donor vs stock, **before any reconstruction edit**:

| item | result |
| --- | --- |
| `aw2013_regmap_config` (328 B) | **byte-identical** |
| `struct i2c_driver` `.data` (280 B) | **byte-identical** |
| `aw2013_match_table` size | identical (400 B); `.rodata` differs by exactly 10 bytes, all inside the compatible string |
| `aw2013_blink_set` | **same size, 492 B**; differs in 7 words only: 2 position-relative `bl` and 5 `chip->regmap` offsets (0x568 → 0x578) |
| `init_module` / `cleanup_module` | same sizes (44 / 36) |
| author / description / license | identical `.modinfo` triple |
| imports | donor 19, stock 26, 16 shared; donor-only = the 3 regulator symbols |

RED classification: **`DIRECT_SOURCE_VARIANT`** — same file, same kernel
revision, bounded vendor delta.  Not `DIRECT_SOURCE_MATCH` (the delta is real),
and strictly stronger than `PARTIAL_PUBLIC_SOURCE_MATCH` /
`SAME_VENDOR_DIFFERENT_REVISION`.

---

## Source delta ledger

Machine-readable: `phase4-leds-rgb-aw2013-delta-ledger.tsv`.
Full patch: `phase4-leds-rgb-aw2013-donor-to-recon.diff` (189 added / 58 removed
lines against the frozen donor).
Final source: `phase4-leds-rgb-aw2013-reconstructed-source.c`
(sha256 `667e417b3cc4a45c62a8ab9b1228815a9f129f12c3409444c3b18a2b27efb8c2`, 565 lines).

19 deltas in 5 categories. Summary:

**Identity (D01–D03)** — source file `leds-aw2013.c` → `leds-rgb-aw2013.c`
(module `leds_rgb_aw2013`); `.driver.name` → `"leds-rgb-aw2013"`; compatible
`awinic,aw2013` → `awinic,rgb,aw2013`.

**Power path (D04–D08)** — `struct regulator *vcc_regulator` removed from
`struct aw2013` (proven by `leds[0]` moving `0x40`→`0x38` and `chip->regmap`
`0x568`→`0x578`); all three `regulator_*` imports gone; replaced by
`yft_aw2013_parse_dts()` which requests **GPIO 188** (`aw2013-pwd-gpio`) and
drives it output-high.  `aw2013_chip_enable()`/`aw2013_chip_disable()` lose their
regulator steps.

**Brightness (D09–D11)** — `u32 fixed_brightness` added to `struct aw2013_led`
at offset `0x1b8` (stride `0x1b8`→`0x1c0`), populated from the new DT property
`led-fixed-brightness` (default `LED_FULL`), and `aw2013_brightness_set()`
substitutes it for any non-zero requested brightness.

**New Ulefone code (D12–D16)** —
`unsigned int led_aw2103_get_boot_mode(void)` (MediaTek `/chosen` `atag,boot`
parser, including the verbatim MTK `log_store` `KERN_NOTICE` strings),
`int led_aw2103_control(void)` (power-off-charging battery indicator),
the globals `gftk_leds` and `aw2013_pwd_gpio`, and the `led_aw2103_control()`
call at the end of probe.

**Teardown (D17–D18)** — `mutex_destroy()` removed from `aw2013_remove()`; the
probe error paths no longer `mutex_unlock`/`mutex_destroy` and return directly.

Two non-obvious facts had to be recovered from the binary and are worth calling
out, because a "reasonable" reconstruction gets them wrong:

1. **`led_aw2103_get_boot_mode()` returns `unsigned int`, not `int`.**
   Its KCFI prologue word is `0x837de525`.  Computing Clang's KCFI type id
   (`(u32) xxHash64(mangled_type_name)`) gives
   `xxHash64("_ZTSFivE") & 0xffffffff = 0x36b1c5a6` for `int(void)` but
   `xxHash64("_ZTSFjvE") & 0xffffffff = 0x837de525` for `unsigned int(void)`.
   The `int(void)` value `0x36b1c5a6` is independently confirmed by
   `init_module` and by `led_aw2103_control` itself.  This 4-byte word was the
   last difference in `.text`.
2. **The GPIO number is cached in a local across the `-1`/`-2` log blocks.**
   Reading the global twice per block (the naive form) costs 2 extra
   instructions; the stock code reads it once per block into a callee-saved
   register.

---

## Hardware contract

Full detail: `phase4-leds-rgb-aw2013-hardware-contract.md`.

| item | value |
| --- | --- |
| chip | Awinic AW2013, 3-channel constant-current RGB LED driver |
| bus / address | I2C bus **11** (`i2c@11d71000`, `mediatek,mt6989-i2c`), **0x45** |
| regmap | 8-bit reg / 8-bit val, `max_register = 0x77` |
| enable | **GPIO 188** (`aw2013-pwd-gpio`, mt6878 pinctrl), driven output-high in probe and never released |
| regulator | **none** — the upstream `vcc` rail is not used on this board |
| channels | 3 — `reg` 0 = **red**, 1 = **green**, 2 = **blue** |
| per-channel current | `led-max-microamp = 5000` → `imax = 1` → **5 mA** full scale on all three |
| brightness | clamped to `led-fixed-brightness`: red 64, green 64, blue 128 |
| blink | hardware blink, 130 ms step, on 130 ms…16.64 s, off 130 ms…4.16 s |
| breathing ramps | **not programmed** — `LCFG.FI/FO`, `LEDT0.T1`, `LEDT1.T3`, `LEDT2` are never written |
| reset | single `RSTR(0x00) = 0x55` software reset in `aw2013_probe_dt` |
| chip ID | `RSTR` must read `0x33`, else `-ENODEV` |
| IRQ / timer / workqueue | **none** |
| PM (suspend/resume/shutdown) | **none** — `.pm` and `.shutdown` are NULL in `aw2013_driver` |
| custom sysfs | **none** — every node comes from the LED class core |
| exports | **none** — no `__ksymtab` section |

### What physical light this is

**The front notification / charging indicator RGB LED.**  Established from four
independent directions, not from the chip name:

1. Its LED class devices are `red`, `green`, `blue`, and the MediaTek Lights HAL
   binary opens exactly those three paths and implements
   `blink_red/blink_green/blink_blue(level,onMS,offMS)` — the Android
   notification/battery/attention light path.
2. `led_aw2103_control()` runs at the end of probe and, **only** in MediaTek boot
   modes 8 (`KERNEL_POWER_OFF_CHARGING_BOOT`) and 9
   (`LOW_POWER_OFF_CHARGING_BOOT`), reads `POWER_SUPPLY_PROP_CAPACITY` from the
   `3rd-gauge` power supply and lights **green ≥ 90 %**, **red ≤ 15 %**, **blue
   16–89 %**.  `3rd-gauge` is confirmed live at
   `/sys/devices/platform/soc/11c24000.i2c/i2c-9/9-0055/power_supply/3rd-gauge`
   (`POWER_SUPPLY_TYPE=Battery`, `POWER_SUPPLY_CAPACITY=79`).
3. It is **not** the decorative/rear light: Ulefone's marquee/"dgled" lights are
   AW22xxx (`aw22xxx_led`, sepolicy `yft_marquee_file` / `yft_dgled_device`), and
   **no AW22xxx device is bound and no AW22xxx module ships** on this build —
   those sepolicy rules are carry-over from other Ulefone models.
4. It is **not** camera-related: camera flash is `aw36515`/`aw36518`/
   `aw36518_v2` on I2C bus 6 @0x63 behind `flashlight.ko`; the camping light is
   `soc:gftk_camplight`; night-vision is `flashlight_core`.  All separate.

`red`/`green`/`blue` LED class devices exist **only** here — the only other LED
providers are `mtk-leds` (`lcd-backlight` only), `leds-ln2403.ko`,
`leds-mtk*.ko` and `aw_vibrator`.

---

## DT contract

Full detail: `phase4-leds-rgb-aw2013-dt-contract.md`.

```dts
i2c@11d71000 {                                  /* bus 11 */
    aw2013@0x45 {
        compatible      = "awinic,rgb,aw2013";
        reg             = <0x45>;
        aw2013-pwd-gpio = <&pinctrl 188 0>;
        status          = "okay";

        aw@0 { label="red";   reg=<0>; led-max-microamp=<5000>; led-fixed-brightness=<0x40>; default-state="off"; };
        aw@1 { label="green"; reg=<1>; led-max-microamp=<5000>; led-fixed-brightness=<0x40>; default-state="off"; };
        aw@2 { label="blue";  reg=<2>; led-max-microamp=<5000>; led-fixed-brightness=<0x80>; default-state="off"; };
    };
};
```

Confirmed twice: in the offline merged DTB and in the live
`/sys/firmware/devicetree/base/soc/i2c@11d71000/aw2013@0x45/...` capture.
Child-count is validated by the driver as `1 <= count <= 3`; a child whose `reg`
is missing or `>= 3` is skipped with `dev_err("Couldn't read LED address: %d")`
and decrements the count.

---

## Userspace / Lights HAL contract

Full detail: `phase4-leds-rgb-aw2013-userspace-contract.md`.

* LED class names **`red` / `green` / `blue`** are hard ABI, derived from the DT
  `label` properties via `init_data.fwnode`.
* `/vendor/bin/hw/android.hardware.lights-service.mediatek` (AIDL
  `android.hardware.light` V2, `ILights/default`, started as
  `vendor.light-default`) opens
  `/sys/class/leds/{red,green,blue}/{brightness,trigger,delay_on,delay_off}`
  and writes `trigger=timer` + `delay_on`/`delay_off` for blinking.  It logs
  `"RED_DELAY_OFF_FILE doesn't exist or cannot write!!"` if the node is missing —
  so **`blink_set` must be implemented**, and it is.
* `init.mt6878.rc` (lines 108–110, 804–806) and the Ulefone-specific
  `init.yft.rc` (lines 28–33, `chmod 0666`) chown/chmod those nodes;
  `ueventd.rc` grants `delay_on`/`delay_off`.
* Direct sysfs consumers: `/system/app/FactoryMode/FactoryMode.apk`,
  `vendor/bin/factory`, `vendor/bin/meta_tst`.
* `system_server`'s `LightsService` reaches the LEDs only through the HAL.
* The `tr1/tr2/tf1/tf2/ton/toff`, `grpfreq`, `grppwm`, `blink` and
  `/sys/devices/platform/leds-mt65xx/` rules in `ueventd.rc` / `init.rc` are dead
  legacy MediaTek entries — those nodes do not exist with this driver and are
  **not** a requirement.
* SELinux pins nothing here: there is no `vendor_file_contexts` rule for the
  `11-0045` path; access is DAC-governed.

---

## Register map

Machine-readable: `phase4-leds-rgb-aw2013-register-map.tsv` (15 proven
operations, each with address / access / mask / value / caller / condition /
delay / retry / binary evidence).

| reg | name | operation |
| --- | --- | --- |
| `0x00` | `RSTR` | read — chip ID, must be `0x33` |
| `0x00` | `RSTR` | write `0x55` — software reset (once, in `aw2013_probe_dt`) |
| `0x01` | `GCR` | write `0x01` — enable; write `0x00` — disable |
| `0x30` | `LCTR` | update_bits mask `BIT(n)` value `0xFF` / `0x00` — channel enable/disable |
| `0x31+n` | `LCFG(n)` | update_bits mask `0x03` value `imax` — per-channel current |
| `0x31+n` | `LCFG(n)` | update_bits mask `0x10` (`MD`) value `0xFF` / `0x00` — blink mode on/off |
| `0x34+n` | `PWM(n)` | write brightness (`0` or `fixed_brightness`) |
| `0x37+3n` | `LEDT0(n)` | write `T2 = on` (blink on-time exponent) |
| `0x38+3n` | `LEDT1(n)` | write `T4 = off` (blink off-time exponent) |
| `0x77` | — | regmap `max_register` only |

**No delays, no retries, no polling and no error-recovery loops exist anywhere
in this driver** — every register access is a single unconditional
`regmap_write` / `regmap_read` / `regmap_update_bits_base` whose return value is
checked and propagated.

Register *names* are taken from the public upstream header block in
`leds-aw2013.c`, which the binary confirms exactly (addresses, masks and the
`0x55`/`0x33` magic values all match).  No name was invented: `LEDT0.T1`,
`LEDT1.T3`, `LEDT2`, `LCFG.FI` and `LCFG.FO` are defined upstream but **never
written** by this driver, and are documented as unused rather than guessed at.

---

## RGB / brightness / timing contract

| behaviour | exact rule |
| --- | --- |
| brightness set (non-zero) | `PWM(n) = led->fixed_brightness`; `LCTR[n] = 1` |
| brightness set (zero) | `PWM(n) = 0`; `LCTR[n] = 0`; `LCFG(n).MD = 0` |
| chip power-up | first non-zero brightness on any channel → `GCR = 1`, then `LCFG(n)[1:0] = imax` for every channel |
| chip power-down | last channel reaching brightness 0 → `GCR = 0` |
| fixed brightness values | red 64, green 64, blue 128 (from DT); default `0xff` if the property is absent |
| current | `imax = min(microamp/5000, 3)` → 1 → 5 mA per channel |
| blink defaults | both delays 0 → 500 ms / 500 ms |
| blink quantisation | `on = min(7, ilog2((delay_on-1)/130)+1)`, `off = min(5, ilog2((delay_off-1)/130)+1)`; both delays are written back as `BIT(x) * 130` |
| blink never-on | `delay_on == 0` → `brightness = LED_OFF`, `brightness_set(0)` |
| blink never-off | `delay_off == 0` → `LCFG(n).MD = 0` (steady) |
| blink from dark | `cdev.brightness == 0` → forced to `LED_FULL` then `brightness_set` first |
| charging indicator | KPOC/LPOC boot only: capacity ≥ 90 → green, ≤ 15 → red, else blue; `cdev.brightness = 6` then `brightness_set(cdev, 6)` (the 6 is only "non-zero"; the actual PWM is the fixed brightness) |

---

## ABI

Machine-readable: `phase4-leds-rgb-aw2013-provider-boundary.tsv`,
`phase4-leds-rgb-aw2013-consumer-boundary.tsv`,
`phase4-leds-rgb-aw2013-modversions.tsv`, `phase4-leds-rgb-aw2013-imports.tsv`.

* **26 imports**, **27 `__versions` records** (26 + `module_layout`).
* **Every one of the 27 CRCs matches the stock module *and* the exact-GKI
  `bazel-bin/common/kernel_aarch64/Module.symvers`.**
* **Provider is `vmlinux` for all 27** — there is no vendor provider, which is
  exactly why `.modinfo depends` is empty and `modules.dep` line 188 has an empty
  dependency list.
* Export breakdown: 11 `EXPORT_SYMBOL`, 16 `EXPORT_SYMBOL_GPL`.  The module is
  `GPL v2`, so the GPL imports are legitimate.

```
missing imports : 0
extra imports   : 0
CRC mismatches  : 0
```

* **0 exports** — the stock module has no `__ksymtab`/`__ksymtab_gpl` section at
  all, so the consumer boundary is empty.  No stock module lists
  `leds_rgb_aw2013` in its `depends`.  `led_aw2103_get_boot_mode` and
  `led_aw2103_control` are non-static (GLOBAL `FUNC`) but **not** exported —
  reproduced exactly.
* `Module.symvers` was never edited; no CRC was faked or overridden.

---

## Exact-GKI build

```
workspace : /home/armol/kernel-work/gki-12901745-workspace
kernel    : //common:kernel_aarch64  (GKI ab/12901745)
common    : 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
toolchain : prebuilts/clang/host/linux-x86/clang-r487747c (Android clang 17.0.2)

RED baseline:
$ tools/bazel build //lieppos/aw2013-recon/donor-build:leds_aw2013_donor
  BUILD_RC=0   compiler warnings=0   modpost warnings=0   unresolved symbols=0

Reconstruction:
$ tools/bazel build //lieppos/aw2013-recon/recon:leds_rgb_aw2013_recon
  BUILD_RC=0   compiler warnings=0   modpost warnings=0   unresolved symbols=0
  -> bazel-bin/lieppos/aw2013-recon/recon/leds_rgb_aw2013_recon/leds-rgb-aw2013.ko
     24720 bytes, sha256 73e0eb219c70905d67c5b652fb87959cfd73b2dfd10910b6e08445600193850e
```

Sources:

```
lieppos/aw2013-recon/
├── donor-pristine/leds-aw2013.c        (frozen, sha256 8458f2aac83c…, untouched)
├── donor-build/{leds-aw2013.c,Makefile,BUILD.bazel}   (RED, build glue only)
└── recon/{leds-rgb-aw2013.c,Makefile,BUILD.bazel}     (reconstruction)
```

No `ccflags`, no `-D` overrides, no header shim, no `KBUILD_MODPOST_WARN`, no
`KBUILD_EXTRA_SYMBOLS`.  The reconstruction needs nothing beyond plain GKI.

---

## Structural verification

Raw transcript: `phase4-leds-rgb-aw2013-verify-recon-vs-stock.txt`.

### Functions — `phase4-leds-rgb-aw2013-functions.tsv`

| function | section | offset | stock | recon | donor | KCFI (stock = recon) | byte-identical |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `led_aw2103_get_boot_mode` | `.text` | `0x004` | 160 | 160 | absent | `0x837de525` | **yes** |
| `led_aw2103_control` | `.text` | `0x0a8` | 296 | 296 | absent | `0x36b1c5a6` | **yes** |
| `aw2013_brightness_set` | `.text` | `0x1d4` | 740 | 740 | 856 | `0x140dd685` | **yes** |
| `aw2013_remove` | `.text` | `0x4bc` | 64 | 64 | 104 | `0x8effdd6d` | **yes** |
| `aw2013_probe` | `.text` | `0x500` | 1272 | 1272 | 908 | `0xcc836375` | **yes** |
| `aw2013_blink_set` | `.text` | `0x9fc` | 492 | 492 | 492 | `0x6286520f` | **yes** |
| `init_module` | `.init.text` | `0x004` | 44 | 44 | 44 | `0x36b1c5a6` | **yes** |
| `cleanup_module` | `.exit.text` | `0x004` | 36 | 36 | 36 | `0xa540670c` | **yes** |

```
stock functions   : 8      rebuilt functions : 8
missing           : 0      extra             : 0
size-identical    : 8/8    byte-identical    : 8/8
KCFI IDs matching : 8/8
```

Six additional functions are inlined in both stock and reconstruction and
therefore carry no symbol: `aw2013_chip_init`, `aw2013_chip_enable`,
`aw2013_chip_disable`, `aw2013_chip_in_use`, `aw2013_probe_dt`,
`yft_aw2013_parse_dts`.  Their presence is proven by the `__func__` strings and
the inlined call sites, and their behaviour is byte-verified as part of the
enclosing functions.

### Relocation / call / string / data reference multisets

170 relocation records in each file; the `(type, target section/symbol, addend)`
multiset is **identical**.  Because `.text`, `.rodata` and `.rodata.str1.1` are
additionally byte-identical, every call target, every string reference and every
data reference is identical by construction.

### Objects — `phase4-leds-rgb-aw2013-objects.tsv`

21 named objects, 21 present in both, **20 byte-identical**; the single exception
is `__UNIQUE_ID_vermagic333` (87 B vs 85 B).

* `aw2013_driver` (`struct i2c_driver`, 280 B) — byte-identical, including
  `.probe_new` → `aw2013_probe`, `.remove` → `aw2013_remove`,
  `.driver.name` → `"leds-rgb-aw2013"`, `.driver.of_match_table` →
  `aw2013_match_table`, and NULL `.pm` / `.shutdown` / `.alert` / `.command`.
* `aw2013_match_table` + `__mod_of__aw2013_match_table_device_table` (400 B) —
  byte-identical, one entry `awinic,rgb,aw2013` + sentinel.
* `aw2013_regmap_config` (328 B) — byte-identical
  (`reg_bits=8`, `val_bits=8`, `max_register=0x77`).
* `.bss` layout identical: `gftk_leds` @0, `aw2013_pwd_gpio` @8,
  `aw2013_probe.__key` @0xc, total 13 bytes.
* No brightness/timing lookup tables exist in either binary — the blink
  conversion is computed arithmetically, not tabulated.
* No sysfs attribute structures exist in either binary.

### ABI

26/26 imports, 27/27 CRCs, 0/0 exports, `.modinfo depends` empty in both.

### Strings

39 strings, `.rodata.str1.1` byte-identical (1175 B) — same content, same order,
same offsets.

---

## Behavioural verification

Because `.text` is byte-identical, behavioural equivalence is not an argument —
it is a consequence.  The table below records what that behaviour *is*, verified
by disassembly before the rebuild existed.

| path | verified behaviour |
| --- | --- |
| **module init** | `i2c_register_driver(THIS_MODULE, &aw2013_driver)` — `.init.text` byte-identical |
| **module exit** | `i2c_del_driver(&aw2013_driver)` — `.exit.text` byte-identical |
| **probe** | `devm_kzalloc(0x588)` → `yft_aw2013_parse_dts` (GPIO 188 high) → `-1`/`-2` log rounds → `mutex_init`/`mutex_lock` → `i2c_set_clientdata` → `devm_regmap_init_i2c` → chip-ID `0x33` → `aw2013_probe_dt` → `mutex_unlock` → `gftk_leds = chip` → `led_aw2103_control()` |
| **initialization** | reset `RSTR = 0x55` once, in `aw2013_probe_dt`, after the child-count check and before child registration; nothing else is written at probe time (chip left disabled, matching `default-state = "off"`) |
| **DT parsing** | `reg` (reject `>=3`), `led-max-microamp` (→ `imax`, default 1 + `dev_info`), `led-fixed-brightness` (default `0xff`), `label` via `init_data.fwnode` |
| **LED class registration** | `devm_led_classdev_register_ext(&client->dev, &led->cdev, &init_data)` per child; `brightness_set_blocking` and `blink_set` installed |
| **RGB brightness** | see the RGB/brightness/timing contract table — clamp to `fixed_brightness`, `LCTR` bit, `LCFG.MD` clear on off |
| **enable/disable** | reference-counted on `cdev.brightness` across all channels via the inlined `aw2013_chip_in_use()` |
| **blinking/breathing** | upstream 130 ms `ilog2` quantisation, `LEDT0`/`LEDT1`, `LCFG.MD`, `LCTR`; no ramp registers touched |
| **charging indicator** | `/chosen` → `atag,boot` → boot mode ∈ {8,9} → `3rd-gauge` `CAPACITY` → green/red/blue |
| **suspend/resume** | none exists — `.pm` is NULL in both |
| **remove** | `i2c_get_clientdata` → inlined `aw2013_chip_disable` (`GCR = 0` if enabled); **no** `mutex_destroy`, **no** `gpio_free` |
| **error unwinding** | `-ENOMEM` (alloc), `-ENODEV` (GPIO failure, wrong chip ID), `-EINVAL` (bad child count), propagated `regmap`/`classdev` errors; probe error paths return **without** unlocking the mutex — a stock quirk, reproduced exactly |

---

## Residual differences

**One**, and it is not a source difference:

| # | item | stock | reconstruction | why |
| --- | --- | --- | --- | --- |
| 1 | `.modinfo` `vermagic` | `6.1.115-android14-11-g945dff7bc1bf …` | `6.1.115-android14-11-maybe-dirty …` | `vermagic` embeds the *builder's* SCM revision. `g945dff7bc1bf` is Ulefone's own kernel-tree HEAD; a local Kleaf build of GKI `6b18f0b574ab` stamps `-maybe-dirty`. The 2-byte size delta (87 → 85) is the whole `.modinfo` difference and the whole 136-byte `.ko` size difference (24856 → 24720, the rest being section padding). |

This field is set at integration time (`setlocalversion` / `--config=stamp` /
`KBUILD_BUILD_VERSION`) and must be pinned to
`6.1.115-android14-11-g945dff7bc1bf` for the module to load into the stock
kernel.  It was **not** faked here: no binary patching, no `Module.symvers`
edit, no CRC override.

**No hardware-affecting residual exists.**  Not one register address, mask,
value, current setting, timing constant, channel mapping, GPIO number, LED class
name, DT property, ABI symbol or CRC differs.

---

## Safety statement

This entire phase was performed **offline**.

* The phone was **not** used to write LED brightness, run blink/breathing tests,
  write I²C registers, toggle GPIO, bind/unbind, `insmod`/`rmmod`, change
  DT/DTBO, flash partitions or switch slots.
* No new runtime evidence was collected. The only device-derived data used is the
  **pre-existing read-only snapshot** `live-stock-adb-20260831-115649`
  (`buses.txt`, `thermal-power.txt`, `devicetree.tar`, `dmesg.txt`), captured in
  an earlier phase, plus the statically extracted stock partition images.
* Static analysis was sufficient throughout; no ambiguity required a runtime
  probe. The one genuinely uncertain item — the return type of
  `led_aw2103_get_boot_mode()` — was resolved **statically** by computing the
  Clang KCFI type id, not by experiment.

---

## Runtime-validation status

```
NOT RUNTIME-VALIDATED — BY DESIGN (offline phase)
```

The reconstruction has never been loaded on hardware. Its correctness rests on
byte-identity of `.text`, `.rodata`, `.rodata.str1.1`, `.data`, `.init.data`,
`.exit.data`, `.init.text`, `.exit.text`, `__versions`,
`.gnu.linkonce.this_module`, `.init.eh_frame` and `.note.Linux` against the
stock module, which is a strictly stronger guarantee than any functional test.

Before deployment the following non-offline steps remain:

1. Build with `vermagic` pinned to `6.1.115-android14-11-g945dff7bc1bf`.
2. Place at `/lib/modules/leds-rgb-aw2013.ko` in the vendor_boot platform
   ramdisk, keeping `modules.load` line 179, the empty `modules.dep` entry and
   the two `modules.alias` lines.
3. Confirm binding at `/sys/bus/i2c/devices/11-0045` and the appearance of
   `/sys/class/leds/{red,green,blue}` with `brightness`, `trigger`, and (after
   `trigger=timer`) `delay_on`/`delay_off`.

---

## Evidence index

| artefact | contents |
| --- | --- |
| `phase4-leds-rgb-aw2013-stock-oracle.txt` | frozen oracle: path, hashes, build-id, ELF/modinfo inventory, load placement, live binding |
| `phase4-leds-rgb-aw2013-RED.md` | donor selection, freeze, RED build, donor-vs-stock delta, classification |
| `phase4-leds-rgb-aw2013-hardware-contract.md` | chip, bus, GPIO enable path, channel/current map, brightness clamp, blink, reset, physical LED role, absent resources |
| `phase4-leds-rgb-aw2013-dt-contract.md` | exact DT node, property-by-property proof against the binary, derived hardware numbers |
| `phase4-leds-rgb-aw2013-userspace-contract.md` | LED class names, sysfs surface, Lights HAL, init/ueventd, direct consumers, dead legacy rules, SELinux |
| `phase4-leds-rgb-aw2013-register-map.tsv` | 15 register operations with address/access/mask/value/caller/condition/delay/retry/evidence |
| `phase4-leds-rgb-aw2013-delta-ledger.tsv` | 19 donor→stock deltas with binary evidence and hardware effect |
| `phase4-leds-rgb-aw2013-donor-to-recon.diff` | complete patch from the frozen donor to the reconstruction |
| `phase4-leds-rgb-aw2013-reconstructed-source.c` | final reconstructed source |
| `phase4-leds-rgb-aw2013-functions.tsv` | per-function offsets, sizes (stock/recon/donor), KCFI IDs, byte-identity |
| `phase4-leds-rgb-aw2013-objects.tsv` | 21 named objects with sizes and byte-identity |
| `phase4-leds-rgb-aw2013-imports.tsv` | 26 imports |
| `phase4-leds-rgb-aw2013-modversions.tsv` | 27 CRCs, stock vs recon vs exact GKI |
| `phase4-leds-rgb-aw2013-provider-boundary.tsv` | every import resolved to its provider (`vmlinux` ×27) with export type |
| `phase4-leds-rgb-aw2013-consumer-boundary.tsv` | empty by construction — 0 exports, 0 dependents |
| `phase4-leds-rgb-aw2013-verify-recon-vs-stock.txt` | raw section/function/object/relocation/ABI comparison transcript |

Working tree (not committed): `/home/armol/kernel-work/aw2013-analysis/`
(stock/donor/recon `.ko`, disassembly, extracted sections),
`/home/armol/kernel-work/gki-12901745-workspace/lieppos/aw2013-recon/`.

---

## Final verdict

`leds_rgb_aw2013.ko` is **solved**.

The stock module is the upstream mainline `drivers/leds/leds-aw2013.c` as
carried by the exact GKI tree, plus a bounded 19-item Ulefone/YFT delta that
swaps the `vcc` regulator for a chip-enable GPIO, clamps every channel to a
DT-supplied fixed brightness, and adds a MediaTek power-off-charging battery
indicator.  All 19 deltas were recovered from the binary, are documented with
evidence, and are the complete difference.

The reconstruction builds cleanly against exact GKI `ab/12901745` with zero
warnings, zero modpost warnings and zero unresolved symbols, and is
**byte-identical to the stock module in every content-bearing section**, with
8/8 functions byte-identical, 170/170 relocations identical, 27/27 MODVERSION
CRCs identical and 0 exports on both sides.  The only difference in the entire
file is the `vermagic` SCM stamp.

```
SOURCE_DELTA_RECONSTRUCTION_EXACT
```
