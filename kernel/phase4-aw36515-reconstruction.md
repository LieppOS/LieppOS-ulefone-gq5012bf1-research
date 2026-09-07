# Phase 4 — `aw36515.ko` reconstruction (Ulefone GQ5012BF1)

Primary-camera dual-channel flash driver of the Ulefone Armor 29 Pro Thermal
(`GQ5012BF1`, MediaTek MT6878/MT6878T).  This is a **full reverse-engineering
pass with its own mandatory RED**, not a family rename of AW36518: the two
drivers share an ancestor but differ in channel count, register addressing,
current scales, timeout encoding, cooling ladder, power-throttling path,
GPIO usage, PM surface and function inventory.

## Final classification

```
SOURCE_DELTA_RECONSTRUCTION_EXACT
```

Justification:

* a real public structural donor exists and was proved to be the same source
  lineage (mandatory RED, `phase4-aw36515-RED.md`);
* every delta from that donor to the stock module is enumerated with
  binary evidence (31 rows, `phase4-aw36515-delta-ledger.tsv`);
* the rebuilt module reproduces the stock oracle with **23/23 functions,
  23/23 size-identical, 22/23 byte-identical**, 20/20 KCFI type ids,
  46/46 imports, **47/47 identical MODVERSION CRCs**, 24/24 identical strings
  and **all 13 initialised data objects byte-identical**;
* the single non-byte-identical function (`reg_show`) differs by exactly two
  transposed `mov` instructions — an instruction-scheduling artifact with no
  semantic content.

It is not `DIRECT_SOURCE_MATCH` (the vendor's own revision is not public) and
whole-module byte equality is **not** claimed (`.modinfo` vermagic differs, as
for every local build).

## Stock oracle

```
path        workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/aw36515.ko
copies      1 (only copy in the image; 471 module paths / 458 unique hashes scanned)
size        34768 bytes
SHA-256     85e5a860bc0ebae9c26e401ae333928ab8da9569b3892040da4f858cf6f643e8
build-id    994488f3714386a04ed4c2daedc0330953d96642
ELF         ET_REL, EM_AARCH64, 41 sections, 174 symbols
compiler    Android (10087095, +pgo, +bolt, +lto, -mlgo, based on r487747c) clang 17.0.2
vermagic    6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
name        aw36515        author  Alec <like@awinic.com>
description Awinic AW36515 LED flash driver        license GPL
depends     flashlight
aliases     i2c:aw36515, of:N*T*Cmediatek,aw36515, of:N*T*Cmediatek,aw36515C*
parameters  none           srcversion absent
inventory   23 text symbols / 46 imports / 47 __versions / 0 exports /
            24 strings / 31 named data objects
```

Load order: `… aw36515.ko, aw36518.ko, aw36518_v2.ko, flashlight.ko …`.
`modules.dep` lists `flashlight.ko` plus five transitive power modules.
Live: `aw36515 24576 0 - Live`, `flashlight 65536 4 aw36518_v2,aw36518,aw36515,imgsensor`,
`/sys/bus/i2c/devices/6-0063` bound to driver `aw36515`.
Full record: `phase4-aw36515-stock-oracle.txt`.

## Source provenance

| | |
|---|---|
| vendor source | **not public** for this revision |
| structural donor | `MotorolaMobilityLLC/kernel-mtk` @ `ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de`, `drivers/misc/mediatek/flashlight/v4l2/aw36515.c`, 995 lines, SHA-256 `22603b6de9ab378ead54ed6ab4457b2ffa557a0386b14139d0575be354c5f024` |
| donor relationship | `PARTIAL_PUBLIC_SOURCE_MATCH` |
| rule applied | where donor and stock agree, the donor form is kept verbatim; where they disagree the **stock binary wins** |

Note this is the *same repository and the same commit* that supplied the
AW36518 donor, but a **different file** — the two drivers are siblings in the
MediaTek tree, not copies of each other.

## RED baseline

Frozen and built untouched **before** any reconstruction edit
(`phase4-aw36515-RED.md`):

```
//lieppos/aw36515-recon/donor-build:aw36515_donor   BUILD_RC=0, 38504 bytes
donor 26 text symbols vs stock 23; 21 shared names; 10 size-identical
donor 42 imports vs stock 46; donor 38 objects vs stock 31
```

Ten functions already matched in size — including both per-channel
`get_ctrl` bodies, which proves the register-`0x0A` fault decode is inherited
rather than invented.

## Source delta ledger (donor → stock)

Full table with per-row proof: `phase4-aw36515-delta-ledger.tsv` (31 rows).
Summary:

**Electrical (8)** — flash max 2000000 → **2000560 µA**; torch max 500000 →
**500780 µA**; flash/torch writes change from “`brt/2` into mask `0x7f` on both
LEDs” to “`brt` into mask `0xff` on one LED”; timeout encoding changes from the
`(t/600)-1` staircase with mask `0x1f` to **`t/40` with mask `0x0f`**; the V4L2
timeout step changes 600 → **40 ms**; the cooling ladder changes
`{100000,80000,60000,40000,20000}` → **`{200000,150000,100000,50000,25000} µA`**;
the `FLASH_IOC_SET_ONOFF` torch point changes 25000 → **80000 µA**.

**Behaviour (13)** — per-channel addressing (the donor's own `#if 0` branch is
what stock ships); strobe-source values `0x0C`/`0x20` instead of `0x00`/`0x24`;
the whole `flash-externel` GPIO path (request, init-low, uninit-low,
strobe-high); the probe software reset and chip-ID read; the `reg` debug sysfs;
cooling state 0 restoring the **torch maximum constant** instead of
`ori_current`; `ori_current` seeded to the torch maximum in probe; no
`state < 0` clamp; no thermal-registration error log.

**Structure (6)** — no `dev_pm_ops`, no `suspend`/`resume`; 6.1 `void remove()`;
no `media_entity_cleanup`; virtually all logging removed (stock has no
`___ratelimit` import and only 24 strings); the `snprintf` failure check added;
ten donor functions inlined so the symbol inventory is exactly 23.

**Cosmetic (4)** — Awinic author/description metadata; `reg_store` uses one
2-element array rather than two scalars (recovered from the stack-addressing
form, and it also closed the same residual in AW36518/AW36518_V2); absolute
line numbering restored so the two probe log records print lines 1047/1049 as
stock does.

## Hardware contract

Full document: `phase4-aw36515-hardware-contract.md`.  Key facts, all proved
from AW36515's own binary and DT:

* Awinic AW36515, I²C address **0x63** on **`/soc/i2c@11e01000` (alias `i2c6`,
  live adapter 6 → `6-0063`)**, compatible `mediatek,aw36515`.
* regmap 8/8 with `max_register = 0xFF`; **no** regulator, clock or interrupt
  is requested — faults are polled from register `0x0A`.
* One chip-wide GPIO: `flash-externel = <&pio 116 0>`, requested as
  `GPIOF_OUT_INIT_LOW` under the name `flash_externel`, driven low by
  `aw36515_init()`/`aw36515_uninit()` and **driven high by
  `V4L2_CID_FLASH_STROBE` unconditionally** — including when power throttling
  suppressed the LED enable.  `STROBE_STOP` never lowers it (vendor
  asymmetry, reproduced as-is).
* Runtime PM is enabled and used by the sub-device `open`/`close`, but the
  driver has **no** system-sleep or runtime callbacks at all.
* Struct layout `sizeof = 0x568`, with `ctrls_led[2] @ +0x50` (stride 224),
  `subdev_led[2] @ +0x210` (stride 328), `dnode[2] @ +0x4a0`, a **24-byte
  never-accessed reserved gap at `+0x4b0`**, `flash_dev_id[2] @ +0x4c8`
  (stride 52), `cdev @ +0x530`, cooling fields at `+0x538…+0x558`, GPIO at
  `+0x560`.  The gap is the same vendor-struct feature already proved for
  AW36518/V2 and is reproduced as `void *vendor_reserved[3]`, never as
  invented fields.
* Platform-data defaults allocated by probe: timeout 1600 ms, flash max
  2000560 µA per channel, torch max 500780 µA per channel.

## DT / media-graph contract

Full document: `phase4-aw36515-dt-contract.md`.

* `aw36515@63` has `#cooling-cells = <2>` and two children, emitted in the DTB
  as `flash@1 {type 0, ct 1, part 0, reg 1}` then `flash@0 {type 0, ct 0,
  part 0, reg 0}`, each with an endpoint to `mtk-composite-v4l2-1` ports 1/0.
* Because both `reg` values match a `led_no`, the AW36515 sub-devices **do**
  get firmware nodes and **do** participate in the media graph — unlike
  AW36518/V2 whose single child (`reg = 2`/`3`) never matches.
* The driver indexes the two children **twice with different rules**:
  `subdev_init()` binds by `reg`, while the flashlight registration loop
  assigns `channel` and the `aw36515-ledN` name by **DT order**.  With this
  DTB the result crosses over:

  | flashlight id (`type`,`ct`,`part`) | channel | name | media link |
  |---|---|---|---|
  | (0, **1**, 0) | 0 | `aw36515-led0` | port 1 via `subdev_led[1]`… |
  | (0, **0**, 0) | 1 | `aw36515-led1` | …and port 0 via `subdev_led[0]` |

  This is stock behaviour and is reproduced exactly.
* `part = 0` with both colour temperatures, the only external-strobe GPIO and
  the only real media links on the board identify AW36515 as the **primary
  camera flash pair**.

## Register / electrical contract

Full documents: `phase4-aw36515-register-map.tsv` and
`phase4-aw36515-electrical-contract.md`.  Nothing here was copied from the
AW36518 phase.

```
0x00  chip id            read once in probe, discarded, not logged, no gate
0x01  enable/mode        bit0 LED0, bit1 LED1, [3:2] mode (0x00/0x08/0x0C),
                         strobe source programmed with mask 0x2C: 0x0C sw / 0x20 hw
0x03  LED0 flash         mask 0xFF, code = (uA - 3910) / 7830   [max 2000560 uA]
0x04  LED1 flash         mask 0xFF, same conversion
0x05  LED0 torch         mask 0xFF, code = (uA -  980) / 1960   [max  500780 uA]
0x06  LED1 torch         mask 0xFF, same conversion
0x07  software reset     probe: read, msleep(10), set bit7, write back
0x08  timeout            mask 0x0F, code = ms / 40; init programs 0x0A = 400 ms
0x0A  fault/flag         bit0 -> TIMEOUT, bit2 -> OVER_TEMPERATURE,
                         bit4 (LED1) / bit5 (LED0) -> SHORT_CIRCUIT
```

Fixed operating points: `FLASH_IOC_SET_ONOFF` on → **80000 µA torch** on the
addressed channel; `flashlight_strobe_store` → **`level × 25000` µA torch**
for `arg.dur` ms; every other ioctl → `-ENOTTY`.  Cooling: `flashlight_cooler`,
`max_state = 5`, ladder `{200000,150000,100000,50000,25000} µA` applied to
**both** channels, state 0 restoring 500780 µA.

Units are stated per quantity in the electrical contract; nothing is left as
an unlabelled "vendor unit".

## Dual-channel architecture (the critical delta)

| question | answer | proof |
|---|---|---|
| may both channels run simultaneously? | **yes** — nothing serialises them | independent enable bits (`0x01`/`0x02`), independent current registers, no interlock anywhere in the module |
| how do the enable bits interact? | not at all; each write is a masked RMW of one bit | every enable path selects the mask from `led_no` |
| how is torch/flash mode chosen per channel? | it is **not** per channel — mode bits `0x01[3:2]` are shared | no mode write depends on `led_no` |
| is the timeout shared or per channel? | **shared** (`0x08`) | timeout case ignores `led_no` |
| are the current registers independent? | **yes** (`0x03`/`0x05` vs `0x04`/`0x06`) | disassembly of both brightness paths |
| how do V4L2 controls map to LEDs? | one `v4l2_ctrl_handler`, one `v4l2_subdev` and one `v4l2_ctrl_ops` entry per channel; `led0_*`/`led1_*` thunks call the shared `get_ctrl`/`set_ctrl` with a constant `led_no` | `aw36515_led_ctrl_ops[2]` at `.rodata+0x388`, stride 32; `led0/led1_set_ctrl` are 32-byte tail calls to `aw36515_set_ctrl` |
| how does external strobe affect each channel? | the strobe **source** bit is chip-wide; the GPIO is chip-wide; only the enable bit is per channel | `mask 0x2C` writes carry no `led_no` |
| channel-specific protection? | **none** beyond the shared fault register bits | exhaustive register-write audit |

`aw36515_led0_get_ctrl` (208 B) and `aw36515_led1_get_ctrl` (212 B) are
separate full bodies differing only in the container offset — both are
byte-identical to stock in the rebuild.

## Power-throttling contract

AW36515 is the **only** module of the family that imports
`flashlight_pt_is_low`.

* `aw36515_enable_ctrl(flash, led_no, on)` calls `flashlight_kicker_pbm(on)`
  and then returns **0 without touching the enable register** when
  `flashlight_pt_is_low()` is true.
* Consequently a low battery suppresses only the LED **enable**; the current,
  mode, timeout and strobe-source writes still happen, and the external
  strobe GPIO is still raised by `V4L2_CID_FLASH_STROBE`.
* Call sites (all through `aw36515_enable_ctrl`, inlined): `LED_MODE`
  (`NONE`/`TORCH`), `STROBE_SOURCE = EXTERNAL`, `STROBE`, `STROBE_STOP`,
  `INTENSITY`/`TORCH_INTENSITY` below the control minimum,
  `aw36515_torch_brt_ctrl` below the torch minimum, `aw36515_ioctl`, and
  `aw36515_strobe_store`.  **Both channels are checked** — the check is
  per call, and each call addresses one channel.
* `flashlight_kicker_pbm(on)` is always called *before* the check, so the
  MediaTek peak-power budget is notified even when the enable is suppressed.
* The stock `flashlight.ko` core contains an Ulefone-specific name-match
  bypass in `fl_enable()` for `"aw36518-led0"` (12) and `"aw36518_v2-led0"`
  (15) **only** — the string `aw36515` does not appear in `flashlight.ko` at
  all.  AW36515 therefore also remains subject to the core's own low-battery
  handling, unlike its siblings.

Complete flashlight operation set (`aw36515_flash_ops`, `.data+0x150`):
`flash_open`, `flash_release`, `ioctl`, `strobe_store`, `set_driver` — all
five reproduced byte-identically, together with the `use_count` protocol
(`set_driver(1)` runs `aw36515_init()` on the 0→1 transition; `set_driver(0)`
runs `aw36515_uninit()` on the 1→0 transition and floors `use_count` at 0).

## ABI: providers and consumers

* 46 imports: 43 from GKI `vmlinux`, plus **three** from `flashlight.ko` —
  `flashlight_dev_register_by_device_id` (`0xe8fd8896`),
  `flashlight_kicker_pbm` (`0x8287fd03`) and `flashlight_pt_is_low`
  (`0xe39abd31`).
* All three vendor CRCs come from the really-built provider
  `//lieppos/aw36518-recon/providers/flashlight:flashlight_provider`.  That
  target was rebuilt for this phase with `CONFIG_MTK_FLASHLIGHT_PT=1` (plus
  the two throttling surfaces stock's own `flashlight.ko` imports) so that it
  genuinely exports `flashlight_pt_is_low`; the two previously used CRCs are
  **unchanged**, so the AW36518/AW36518_V2 results are unaffected.
* No `Module.symvers` was hand-written or patched at any point.
* 46/46 rows `MATCH` across stock CRC / exact-GKI CRC / reconstructed-provider
  CRC / rebuilt-consumer CRC: `phase4-aw36515-provider-boundary.tsv`.
* Exports: 0.  No stock module imports an `aw36515` symbol; live
  `/proc/modules` shows refcount 0:
  `phase4-aw36515-consumer-boundary.tsv`.

```
missing imports         = 0
extra imports           = 0
CRC mismatches          = 0
unresolved providers    = 0
hand-written CRCs       = 0
```

## Exact-GKI build

```
kernel      android14-6.1-2024-12_r4, common commit 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09, CI ab/12901745
target      //common:kernel_aarch64
module      //lieppos/aw36515-recon/recon:aw36515_recon
source      $GKI_WS/lieppos/aw36515-recon/recon/aw36515.c   (1097 lines)
BUILD_RC              0
compiler warnings     0
modpost warnings      0
unresolved symbols    0
KBUILD_MODPOST_WARN   not used for this module
output      aw36515.ko, 34616 bytes,
            SHA-256 a6fc1a405d733a4d163e92285e4a07ff41cce51e3b70c4fff3de309eb5144629
```

(The `flashlight.ko` provider is still built with `KBUILD_MODPOST_WARN=1` for
its own tertiary `mtk_pbm`/`mtk_peak_power_budget` symbols; that relaxation
never applies to `aw36515.ko`.)

## Structural verification

| metric | result |
|---|---|
| Functions | stock 23 / rebuilt 23 / shared 23 / stock-only 0 / rebuilt-only 0 |
| Size-identical | **23 / 23** |
| Byte-identical | **22 / 23** — everything except `reg_show` |
| KCFI type ids | 20 present, 20/20 identical |
| Call/string/data reference multisets | 22/23 identical (only `probe`, and only because two byte-identical `.data` objects landed at different offsets) |
| Imports | 46 / 46, 0 missing, 0 extra |
| Exports | 0 / 0 |
| MODVERSIONS | 47 / 47 common, **47 CRC-identical**, 0 mismatch |
| Data objects | 31/31 names; all 13 initialised `.data`/`.rodata` objects byte-identical (`i2c_driver`, `flash_ops`, `cooling_ops`, `dev_attr_reg`, `ops`, `int_ops`, `led_ctrl_ops`, `regmap`, `id_table`, `of_table`, both device tables, and the 5-entry thermal ladder) |
| Strings | 24 / 24 identical |
| `.modinfo` | author, description, license, name, **depends=`flashlight`**, all 3 aliases identical; parameters 0/0; only `vermagic` differs |

Raw output: `phase4-aw36515-verify-recon-vs-stock.txt`.

## Behavioural verification

Each stock behaviour below was recovered from the disassembly and is
reproduced by a byte-identical function unless noted:

| behaviour | status |
|---|---|
| probe: alloc `0x568`, regmap, pdata defaults, mutex, global pointer, GPIO request, two `subdev_init`s, `pm_runtime_enable`, DT parse + flashlight registration, `i2c_set_clientdata`, `device_create_file`, cooling registration, chip-ID read, software reset | byte-identical |
| `subdev_init`: `v4l2_i2c_subdev_init` sequence, name `snprintf` + failure log, `strscpy` of `aw36515-ledN`, `reg == led_no` fwnode binding, 8 controls, `media_entity_pads_init(…, 0, NULL)`, `MEDIA_ENT_F_FLASH`, async register | byte-identical |
| channel 0 / channel 1 control paths (`led0_*`, `led1_*`, `set_ctrl`) | byte-identical |
| torch (`aw36515_torch_brt_ctrl`) incl. thermal clamp and `ori_current` capture | byte-identical |
| flash brightness (inlined in `set_ctrl`) incl. `need_cooler == 1` clamp | byte-identical (inside `set_ctrl`) |
| external strobe: source select, GPIO high on `STROBE`, no GPIO on `STROBE_STOP` | byte-identical |
| timeout programming (`t/40`, init 400 ms) | byte-identical (inside `set_ctrl` / `set_driver`) |
| thermal clamp (`cooling_get_max_state`/`get_cur_state`/`set_cur_state`) | byte-identical |
| power-throttling path (`flashlight_kicker_pbm` + `flashlight_pt_is_low`) | byte-identical |
| faults (`get_ctrl` decode of `0x0A`) | byte-identical |
| ioctl (`FLASH_IOC_SET_ONOFF` 80000 µA, `-ENOTTY` otherwise) | byte-identical |
| `strobe_store` (`level × 25000` µA, `msleep(dur)`, `set_driver` bracket) | byte-identical |
| `set_driver` / `use_count` protocol, `init`/`uninit` inlining | byte-identical |
| remove: cooling unregister, per-LED subdev/handler teardown, runtime-PM disable + set-suspended, **no** `media_entity_cleanup` | byte-identical |
| `reg` sysfs read/write debug hatch | `reg_store` byte-identical; `reg_show` semantically identical (see residuals) |

## Residual differences

Exactly one function is not byte-identical, plus the usual build-identity
fields:

1. **`reg_show`** — size-identical (212 bytes); the only difference is two
   transposed instructions at `+0x24`/`+0x28` (`mov x22, xzr` and
   `mov w20, wzr` are emitted in the opposite order).  Same registers, same
   calls, same constants, same relocation sequence.  Pure instruction
   scheduling under the vendor's `+pgo/+bolt/+lto` flags, which Kleaf does not
   reproduce.  **No hardware effect.**
2. **`.data` object placement** — `aw36515_flash_ops` and `dev_attr_reg` land
   at different offsets inside `.data`; their *contents* are byte-identical.
   This is the only cause of the one differing reference multiset (`probe`).
   **No hardware effect.**
3. **`vermagic`** — `…-g945dff7bc1bf` (Ulefone) vs `…-maybe-dirty` (local
   Kleaf build of the same `6.1.115-android14-11` tree).
4. **Module size** — 34616 vs 34768 bytes, entirely accounted for by the
   `.modinfo`/`vermagic` and section-padding differences above.

No residual touches a register address, a mask, a current, a timing value, a
channel assignment, a device identity, an ABI symbol or a CRC.  There are
**no hardware-affecting residuals**.

## Safety deviations

None.  Offline only.  During this phase no torch was enabled, no camera flash
was fired, no duty or current was changed, no I²C register was written, no
external-strobe GPIO was toggled, no driver was bound or unbound, no module
was inserted or removed, no DT/DTBO was modified, no partition was flashed and
no slot was switched.  The only runtime data used are read-only snapshots
already committed to this repository.

The reconstruction adds no flash/torch gate, no current clamp and no safety
interlock — it is behaviourally identical to stock, including the debug `reg`
sysfs write path, which must remain root-only in LieppOS policy.

## Runtime-validation status

```
STATIC RECONSTRUCTION      DONE   (relocation-aware disassembly of all 23 stock functions)
MANDATORY RED              DONE   (public donor frozen and built untouched first)
BUILD VERIFICATION         DONE   (exact GKI ab/12901745, BUILD_RC=0, 0 warnings, 0 unresolved)
ABI VERIFICATION           DONE   (46/46 imports, 47/47 CRCs, 0 exports, real provider symvers)
PASSIVE RUNTIME EVIDENCE   DONE   (pre-existing read-only /proc/modules, sysfs and DT snapshots)
LIVE HARDWARE VALIDATION   NOT DONE - intentionally, belongs to Slot-B integration
```

## Evidence index

| artifact | content |
|---|---|
| `phase4-aw36515-stock-oracle.txt` | frozen oracle identity |
| `phase4-aw36515-RED.md` | mandatory RED: donor search, freeze, build, diff |
| `phase4-aw36515-delta-ledger.tsv` | 31 donor→stock deltas with per-row binary proof |
| `phase4-aw36515-register-map.tsv` | register/bit/unit map with instruction-level proof |
| `phase4-aw36515-electrical-contract.md` | currents, timings, cooling, operating points, units |
| `phase4-aw36515-hardware-contract.md` | bus, GPIO, struct layout, dual-channel semantics |
| `phase4-aw36515-dt-contract.md` | DT node, children, media graph, the two indexing rules |
| `phase4-aw36515-functions.tsv` / `-objects.tsv` / `-imports.tsv` / `-modversions.tsv` | stock symbol tables (sizes, KCFI ids, CRCs) |
| `phase4-aw36515-provider-boundary.tsv` / `-consumer-boundary.tsv` | ABI boundary |
| `phase4-aw36515-verify-recon-vs-stock.txt` | structural verification output |
| `phase4-aw36515-donor-to-recon.diff` | donor → reconstruction source diff |
| `phase4-aw36518-family-comparison.md` | family evidence (AW36518 / AW36518_V2 / AW36515) |
| `$GKI_WS/lieppos/aw36515-recon/recon/` | reconstruction source + Kleaf target |
| `$GKI_WS/lieppos/aw36515-recon/donor-build/` | verbatim RED donor + build glue |
| `$GKI_WS/lieppos/aw36518-recon/providers/flashlight/` | real provider used for CRC generation |
| `workspace/phase4-aw36515/` (gitignored) | disassembly, section blobs, rebuilt module |

## Final verdict

`aw36515.ko` is **frozen and ready for integration**.  The stock module is
fully characterised: a public MediaTek ancestor plus 31 evidenced vendor
deltas; the reconstruction builds clean against exact GKI `ab/12901745` with
real provider CRCs and is ABI-identical and 22/23 byte-identical to the stock
oracle, with a single scheduling-only residual.  The dual-channel semantics,
the external-strobe GPIO behaviour, the power-throttling path and the crossed
DT indexing are documented rather than normalised.  Live Slot-B validation
remains, deliberately, out of scope.
