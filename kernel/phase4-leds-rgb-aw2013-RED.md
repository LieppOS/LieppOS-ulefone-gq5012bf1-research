# Phase 4 — RED (Reverse-Engineering Donor) for `leds_rgb_aw2013.ko`

**Rule observed:** no reconstruction edit was made before this document existed.
The donor was frozen untouched, built with build glue only, and compared to the
stock oracle first.

## 0. Starting hypothesis (given)

The exact-source audit proposed `kernel/drivers/leds/leds-aw2013.c` as the first
donor candidate, on the strength of the chip name and the
`awinic,rgb,aw2013` compatible.  The instruction was explicit: *do not* assume
the public file is the exact stock source merely because the chip matches.

## 1. The decisive evidence is not the chip name

The stock `.modinfo` is:

```
author=Nikita Travkin <nikitos.tr@gmail.com>
description=AW2013 LED driver
license=GPL v2
```

Nikita Travkin is the author of the **mainline Linux** driver
`drivers/leds/leds-aw2013.c` (added by commit `59ea3c9faf32 leds: add aw2013
driver`).  Awinic vendor drivers on this same device carry
`author=Alec <like@awinic.com>` (see `phase4-aw36515-stock-oracle.txt`) or
`<awinic>`-style tags.

So the stock module is **not** an Awinic vendor driver at all — it is the
upstream community driver, which Ulefone/YFT picked up and modified.  The
`.rodata.str1.1` string set then confirms it directly: every upstream diagnostic
string is present verbatim.

| upstream string | present in stock |
| --- | --- |
| `Failed to read chip ID: %d\n` | yes, at 0x000 |
| `Chip reported wrong ID: %x\n` | yes, at 0x448 |
| `Failed to enable the chip: %d\n` | yes, at 0x23e |
| `Failed to set maximum current for led %d: %d\n` | yes, at 0x0f9 |
| `Couldn't read LED address: %d\n` | yes, at 0x172 |
| `DT property led-max-microamp is missing\n` | yes, at 0x3f3 |
| `Failed to allocate register map: %d\n` | yes, at 0x3ce |
| `&chip->mutex` | yes, at 0x43b |
| `reg`, `led-max-microamp` | yes |

## 2. Donor selection — which copy of `leds-aw2013.c`

Three local copies were examined:

| tree | sha256 of `drivers/leds/leds-aw2013.c` |
| --- | --- |
| `gki-12901745-workspace/common` (exact GKI, `6b18f0b574ab`) | `8458f2aac83ccb6d996f88895b5e9ce953d3475019405ad869bde06a3c361b17` |
| `kernel-research/android-common-gq5012bf1` | `8458f2aac83c…` (identical) |
| `kernel-research/nothing-mt6878/kernel` | `e8c8d857c4fe909458ec7189b4cc7268db9e34602416db19f68cb27ace291953` (older revision) |

The **exact-GKI copy** was chosen as donor.  Its git history in `common` is:

```
d1f384e4c201 leds: aw2013: Unlock mutex before destroying it
ed5c2f5fd10d i2c: Make remove callback return void
c49d6cab0d7f leds: parse linux,default-trigger DT property in LED core
2c6775625434 leds: various: fix OF node leaks
99a013c840a0 leds: various: use only available OF children
8853c95e997e leds: various: use dev_of_node(dev) instead of dev->of_node
59ea3c9faf32 leds: add aw2013 driver
```

Note `CONFIG_LEDS_AW2013` is **not** in `arch/arm64/configs/gki_defconfig` — the
stock module is therefore an out-of-tree/vendor-fragment build of this file, not
a GKI module.  Consistent with it living in the vendor_boot ramdisk.

Local git/tree searches for `awinic,rgb,aw2013`, `led_aw2103`,
`led-fixed-brightness` and `aw2013-pwd-gpio` across all research kernel trees
returned **zero** hits — the Ulefone delta itself has no public source.

## 3. Frozen donor

```
lieppos/aw2013-recon/donor-pristine/leds-aw2013.c
  sha256 8458f2aac83ccb6d996f88895b5e9ce953d3475019405ad869bde06a3c361b17
  (byte-for-byte common/drivers/leds/leds-aw2013.c @ 6b18f0b574ab)

lieppos/aw2013-recon/donor-build/
  leds-aw2013.c  <- same bytes
  Makefile       <- build glue only:  obj-m += leds-aw2013.o
  BUILD.bazel    <- kernel_module(kernel_build = "//common:kernel_aarch64")
```

No `ccflags`, no `-D`, no header shims, no source edit of any kind.

## 4. RED baseline build (untouched donor, exact GKI)

```
$ tools/bazel build //lieppos/aw2013-recon/donor-build:leds_aw2013_donor
BUILD_RC=0    compiler warnings=0    modpost warnings=0    unresolved=0
-> leds-aw2013.ko  19928 bytes
   sha256 735c71718dee68b97d8748b72040b9fc8540d7b0a428eb5c8293a7454ff56ffa
```

## 5. Donor vs stock — the honest delta

### 5.1 What already matches with zero edits

| item | donor | stock | verdict |
| --- | --- | --- | --- |
| `.rodata` size | 728 | 728 | identical size |
| `aw2013_match_table` size | 400 | 400 | identical (of_device_id[2]) |
| `aw2013_regmap_config` size / content | 328 | 328 | **byte-identical** (`reg_bits=8 val_bits=8 max_register=0x77`) |
| `.data` (`struct i2c_driver`) | 280 | 280 | **byte-identical** |
| `aw2013_blink_set` | 492 B | 492 B | **same size**; differs only in 7 words: 2 `bl` (position-relative call to `brightness_set`) and 5 `ldr x0,[x8,#imm]` (`chip->regmap` at 0x568 vs 0x578) |
| `init_module` / `cleanup_module` | 44 / 36 | 44 / 36 | same |
| `.rodata` diff | — | — | exactly 10 bytes, all inside the compatible string (`awinic,aw2013` vs `awinic,rgb,aw2013`) |
| author / description / license | same | same | identical `.modinfo` triple |

`aw2013_blink_set` being size-identical and semantically identical between an
untouched upstream build and the stock binary — including the `ilog2`/130 ms
magic-multiply sequence and the `min(5,…)`/`min(7,…)` saturations — is by itself
conclusive lineage proof.

### 5.2 What differs (the Ulefone/YFT delta)

**Imports** — donor 19, stock 26, 16 in common.

| donor-only (3) | stock-only (10) |
| --- | --- |
| `devm_regulator_get` | `of_find_node_opts_by_path` |
| `regulator_enable` | `of_get_property` |
| `regulator_disable` | `power_supply_get_by_name` |
| | `power_supply_get_property` |
| | `of_get_named_gpio_flags` |
| | `gpio_to_desc` |
| | `gpio_request` |
| | `gpiod_direction_output_raw` |
| | `gpiod_get_raw_value` |
| | `_printk` |

**Structural deltas recovered from the binary**

1. **`struct regulator *vcc_regulator` removed.**  Donor `chip->regmap` sits at
   offset `0x568`, stock at `0x578`; donor `leds[0]` at `0x40`, stock at `0x38`.
   The 8-byte shift before `leds[]` is exactly one removed pointer.  All
   `regulator_*` calls are gone from the stock binary.
2. **Power rail replaced by a chip-enable GPIO** (`aw2013-pwd-gpio`), driven via
   the legacy gpiolib wrappers, plus a global `int aw2013_pwd_gpio` in `.bss`.
3. **`u32 fixed_brightness` added to `struct aw2013_led`** (offset `0x1b8`,
   stride grows `0x1b8`→`0x1c0`), fed from a new DT property
   `led-fixed-brightness`, defaulting to `LED_FULL`.
4. **`aw2013_brightness_set` overrides the requested brightness** with
   `led->fixed_brightness` whenever brightness is non-zero.
5. **Two new global functions** with no upstream counterpart:
   `led_aw2103_get_boot_mode()` (MediaTek `/chosen` `atag,boot` parser, byte-for-byte
   the MTK `log_store` idiom including the `KERN_NOTICE "log_store: …"` strings)
   and `led_aw2103_control()` (power-off-charging battery indicator).
6. **`static struct aw2013 *gftk_leds`** global, published at end of probe.
7. **`mutex_destroy()` removed** from both `aw2013_remove` and the probe error
   path; the probe error paths also no longer `mutex_unlock`.
8. **Driver identity renamed**: `.driver.name` `leds-aw2013` → `leds-rgb-aw2013`,
   compatible `awinic,aw2013` → `awinic,rgb,aw2013`, source file
   `leds-aw2013.c` → `leds-rgb-aw2013.c` (module name `leds_rgb_aw2013`).

### 5.3 What is *not* different

No register address, mask, value, timing constant, channel formula, chip-ID
check, regmap configuration, blink math or LED-class wiring differs from
upstream.  The Ulefone delta is entirely about *power sequencing*, *brightness
clamping*, *identity* and an *added charging-indicator behaviour*.

## 6. Classification

```
DIRECT_SOURCE_VARIANT
```

The stock module is the exact-GKI in-tree upstream `drivers/leds/leds-aw2013.c`
(same author, same licence, same description, same strings, same structures,
same register semantics, one size-identical function) carrying a bounded,
fully enumerated Ulefone/YFT vendor delta.

It is **not** `DIRECT_SOURCE_MATCH` (the delta is real and non-empty) and it is
strictly stronger than `PARTIAL_PUBLIC_SOURCE_MATCH` or
`SAME_VENDOR_DIFFERENT_REVISION` — the donor is not merely the same vendor or
the same family, it is the same file at the same kernel revision.

## 7. Consequence for the reconstruction

Reconstruction proceeds as a **source-delta reconstruction from the frozen
donor**: start from `donor-pristine/leds-aw2013.c`, apply exactly the eight
deltas above, change nothing else.  The delta ledger in
`phase4-leds-rgb-aw2013-donor-to-recon.diff` is the complete record.
