# Phase 4 — AW36515 mandatory RED (Reverse-Engineering Diff)

Performed **before any reconstruction edit**: the closest credible public
source was located, frozen verbatim, built against the exact target GKI, and
diffed against the stock oracle.  Only then was a single byte of
reconstruction source written.

## Search scope

Searched for `aw36515`, `AW36515`, `mediatek,aw36515`, `flashlight-aw36515`,
`aw36515_set_ctrl`, `aw36515_led0`, `aw36515_led1` across:

* this research repository and all of its git refs;
* the GQ5012BF1 stock extraction (`workspace/gq5012bf1/`), including every
  partition, `vendor_dlkm`, `vendor`, `system`, `product` and the DTB/DTBO set;
* the exact-GKI workspace `~/kernel-work/gki-12901745-workspace/`;
* the local vendor-reference trees under `~/kernel-work/`;
* the AW36518 phase's frozen public-source set;
* public sources, starting from the repository that supplied the AW36518
  structural donor.

Result: **no local tree contains AW36515 source**, and no vendor (Ulefone /
Awinic) release of the GQ5012BF1 revision is public.  A MediaTek V4L2 +
flashlight-core AW36515 driver *is* public and is an extremely close
structural ancestor.

## Accepted donor

| field | value |
|---|---|
| repository | `https://github.com/MotorolaMobilityLLC/kernel-mtk` |
| commit | `ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de` |
| path | `drivers/misc/mediatek/flashlight/v4l2/aw36515.c` |
| lines | 995 |
| SHA-256 | `22603b6de9ab378ead54ed6ab4457b2ffa557a0386b14139d0575be354c5f024` |
| frozen at | `workspace/phase4-aw36515/public-source/` (gitignored) and `$GKI_WS/lieppos/aw36515-recon/donor-build/aw36515.c` |
| role | structural donor and RED baseline; **not** an electrical oracle |

The file was copied byte-for-byte.  Only build glue was added: a `Makefile`,
a `BUILD.bazel`, and the three MediaTek flashlight headers already frozen for
the AW36518 phase.  No line of the donor `.c` was edited for the RED build.

## RED build

```
target      //lieppos/aw36515-recon/donor-build:aw36515_donor
kernel      //common:kernel_aarch64, android14-6.1-2024-12_r4,
            common 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09, CI ab/12901745
BUILD_RC    0
output      aw36515.ko, 38504 bytes
warnings    2 (donor is a 5.10-era file: a printk format warning and the
              i2c_driver.remove int-vs-void prototype change in 6.1)
modpost     3 undefined vendor symbols (flashlight_*), expected for the
            bare donor build with no provider linked
```

## RED result — donor vs stock

| metric | donor | stock | verdict |
|---|---|---|---|
| text symbols | 26 | 23 | different inventory |
| shared function names | — | 21 | |
| size-identical shared functions | — | 10 | |
| imports | 42 | 46 | |
| `__versions` | 40 | 47 | |
| exports | 0 | 0 | equal |
| named data objects | 38 | 31 | |

**Donor-only functions** (5): `aw36515_enable_ctrl`, `aw36515_init`,
`aw36515_parse_dt`, `aw36515_suspend`, `aw36515_resume`.
**Stock-only functions** (2): `reg_show`, `reg_store`.

**Donor-only imports** (3): `___ratelimit`, `pm_runtime_force_suspend`,
`pm_runtime_force_resume`.
**Stock-only imports** (7): `device_create_file`, `devm_gpio_request_one`,
`gpio_to_desc`, `gpiod_set_raw_value`, `of_get_named_gpio_flags`,
`regmap_write`, `sscanf`.

**Donor-only objects**: `aw36515_pm_ops` and seven `*._rs` rate-limit states.
**Stock-only object**: `dev_attr_reg`.

### Functions that already matched exactly in size

`aw36515_led0_get_ctrl` (208), `aw36515_led1_get_ctrl` (212),
`aw36515_led0_set_ctrl` (32), `aw36515_led1_set_ctrl` (32),
`aw36515_cooling_get_max_state` (20), `aw36515_cooling_get_cur_state` (20),
`aw36515_flash_open` (8), `aw36515_flash_release` (8), `init_module` (44),
`cleanup_module` (36).

That the two per-channel `get_ctrl` bodies are size-identical between donor
and stock is direct evidence that the **fault decode of register 0x0A is
unchanged from the donor** — the reconstruction inherits it rather than
inventing it.

## Classification of the donor relationship

```
PARTIAL_PUBLIC_SOURCE_MATCH
```

The donor establishes, and the stock binary confirms:

* dual-channel AW36515 register interface (`0x01`, `0x03`, `0x04`, `0x05`,
  `0x06`, `0x08`, `0x0A`);
* the 3910 µA + 7830 µA/LSB flash and 980 µA + 1960 µA/LSB torch conversions;
* two V4L2 flash sub-devices with per-LED `v4l2_ctrl_ops`;
* the MediaTek `flashlight_operations` bridge, ioctl, strobe_store, set_driver
  and `use_count` protocol;
* the thermal cooling device with a 5-entry current ladder;
* probe/remove/subdev/DT-parse structure and the `Awinic`/GPL metadata family.

It is **not** the stock revision.  The stock module additionally has the
external-strobe GPIO, the software reset, the chip-ID read, the `reg` debug
sysfs, single-LED register addressing, a different timeout encoding, different
current maxima, a different cooling ladder, a different ioctl operating point,
no runtime-PM sleep ops and almost no logging.  All of those deltas are
enumerated with per-row binary proof in
`phase4-aw36515-delta-ledger.tsv` (31 rows).

## Rule applied for the rest of the phase

Where the donor and the stock binary agree, the donor's source form is kept
verbatim.  Where they disagree, **the stock binary wins** and the donor value
is discarded; no electrical quantity, register meaning, current limit, timing
or chip identifier was taken from the donor without binary confirmation.
