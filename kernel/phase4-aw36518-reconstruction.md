# Phase 4 — `aw36518.ko` reconstruction (Ulefone GQ5012BF1)

Awinic AW36518 flash-LED driver of the Ulefone Armor 29 Pro Thermal
(`GQ5012BF1`, MediaTek MT6878), reconstructed from the stock `vendor_dlkm`
module and rebuilt against the exact Google GKI the device runs.

## Final classification

```
STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION
```

Justification (all measured, see `phase4-aw36518-verify-recon-vs-stock.txt`):

* every stock function, import, `__versions` record and static data object is
  accounted for and reproduced;
* imports 46/46 with **47/47 identical MODVERSION CRCs**, no extra and no
  missing symbol, no manually written CRC;
* all 14 relocatable data objects (driver struct, ops tables, OF/I²C tables,
  regmap config, PM ops, sysfs attribute, thermal current table) are
  **byte-identical**;
* the string table is **63/63 identical**, including the vendor log prefix and
  the version banner;
* per-function call/string/data reference multisets are identical for 21/23
  functions, the remaining two differ only in the `.data` offset at which the
  *same* byte-identical objects landed;
* 13 functions are byte-identical and 19/23 are size-identical; the residue is
  instruction scheduling/register allocation, not semantics.

> **Updated after the AW36518_V2 phase** (`phase4-aw36518-v2-reconstruction.md`):
> that phase found a 24-byte reserved gap in the vendor `struct aw36518_flash`
> (between `dnode[]` and `flash_dev_id[]`, never accessed by any stock
> instruction, proved by `sizeof(*flash) = 0x308` and the field offsets
> `dnode[0] @ +0x278`, `flash_dev_id[0] @ +0x298`, `cdev @ +0x2d0`).
> Reproducing it raised byte-identical functions from 6 to 12 here as well.
>
> **Updated again after the AW36515 phase** (`phase4-aw36515-reconstruction.md`):
> that phase recovered the vendor's `reg_store()` local-variable form (one
> 2-element `u32` array rather than two scalars, proved by the `orr xN, sp, #0x4`
> addressing stock uses for the second `sscanf` output).  Applying it here made
> `reg_store` byte-identical too, giving 13/23 byte-identical and 19/23
> size-identical.  The numbers in this report are the post-fix ones.

It is not `DIRECT_SOURCE_MATCH` (no vendor source exists publicly) and not a
whole-module byte match (LTO/PGO-scheduling differences remain), so the
strongest honest label is the consumer-ABI-exact one.

## Stock oracle

```
path      workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/aw36518.ko
size      43128 bytes
SHA-256   7dcf64a7d25c657d1a0795cc89ad519c954561c6c757949c247d623f16976247
build-id  da6b5af2f8a1168d78b60ddb13e22aa1b1da70ac
compiler  Android (11349228, based on r487747c) clang 17.0.2
vermagic  6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
name/author/description  aw36518 / Alec <like@awinic.com> / Awinic AW36518 LED flash driver
license/depends          GPL / yft_devinfo,flashlight
aliases   i2c:aw36518, of:N*T*Cmediatek,aw36518, of:N*T*Cmediatek,aw36518C*
params    none
```

Single copy in the stock image (471 module paths / 458 unique modules scanned).
Details: `phase4-aw36518-stock-oracle.txt`, `phase4-aw36518-stock-inventory.md`.

## Source provenance

| Candidate | Verdict |
|---|---|
| MotorolaMobilityLLC/kernel-mtk `drivers/misc/mediatek/flashlight/v4l2/aw36518.c` @ `ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de` (Linux 5.10 MTK vendor tree) | **accepted as structural donor** — same file, same function names, same framework wiring; 20/23 stock function names shared, 37 CRC-identical modversion entries in the RED build |
| Same file at `a543eaa6`, `1f94e13e`, `c9711bca`, `f10286b9` and the parent revision | inspected, no closer variant (all archived in the workspace `public-source/`) |
| NothingOSS mt6878 `flashlight/v4l2/lm3644.c` | structural reference only (same framework, different chip) |
| Awinic public AW36518 Android release | not required once the MTK V4L2 variant was found |
| any `aw36518_v2.c` / `aw36515.c` | **not found publicly** |

Classification of the public evidence: `PARTIAL_PUBLIC_SOURCE_MATCH` (the file
is the same MediaTek V4L2 AW36518 driver, but a different vendor's revision; it
is never used as an electrical oracle where the stock binary differs).
Full record: `phase4-aw36518-source-candidates.md`.

Mandatory RED (donor built untouched against the exact GKI before any edit):
`phase4-aw36518-RED.md`.  Donor→reconstruction delta:
`phase4-aw36518-donor-to-recon.diff`.

## Hardware contract

Fitted part AW36518, I²C `8-0063` (`i2c@11e03000`, `mediatek,aw36518`), regmap
8/8 with `max_register 0xFF`, one LED channel (`aw36518-led0`), optional
`flash-externel` GPIO (absent in this board's node), no IRQ, no regulator, no
clock, runtime PM + system-sleep PM, thermal cooling device `flashlight_cooler`.
Chip register `0x00` is read and logged but never validated; probe ends with a
`0x07 |= 0x80` software reset after a 10 ms delay.
Details: `phase4-aw36518-hardware-contract.md`, `phase4-aw36518-dt-contract.md`.

## Userspace / camera contract

No stock userspace file names the module.  The camera HAL
(`libcam.hal3a.v3.strobe.so`) drives `/dev/flashlight` and addresses the device
by the DT triple `type=0, ct=0, part=1` registered as `aw36518-led0`; the
Ulefone `init.yft.rc` torch sysfs nodes belong to `flashlight.ko`.  Crucially,
`fl_enable()` inside the stock `flashlight.ko` string-matches
`"aw36518-led0"`/`"aw36518_v2-led0"` to bypass the low-battery cut-off, so the
sub-device name is ABI.  Details:
`phase4-aw36518-userspace-camera-contract.md`.

## Register / electrical contract

* Flash current: `0x03[7:0] = (µA − 2940)/5870`, range 2940 … 1 499 790 µA.
* Torch current: `0x05[7:0] = (µA − 750)/1510`, range 750 … 385 800 µA.
* Timeout: `0x08[3:0] = ms/40`; `aw36518_init()` always programs 400 ms.
* Mode/enable: `0x01` mask `0x03` (on/off), `0x0C` (`{NONE,FLASH,TORCH} =
  {0x00,0x0C,0x08}`), `0x2C` (`0x0C` software / `0x20` external strobe).
* Faults: `0x0A` read on demand → bit0 TIMEOUT, bit2 OVER_TEMPERATURE,
  bit4|bit5 SHORT_CIRCUIT; no IRQ, no polling, no auto-clear.
* Thermal limits `{150000, 100000, 50000, 25000} µA`, max_state 4, clamp can
  only lower current.
* Fixed operating points: 250 000 µA (`FLASH_IOC_SET_ONOFF`), `level×25 000 µA`
  (`flashlight_strobe_store`).

Per-instruction evidence: `phase4-aw36518-register-map.tsv`; unit proof and
protection behaviour: `phase4-aw36518-electrical-contract.md`.

## Kernel framework contract

MediaTek flashlight core (`flashlight_operations` = open/release/ioctl/
strobe_store/set_driver, `FLASH_IOC_SET_ONOFF` = `0x80045373`, everything else
`-ENOTTY`) **and** a V4L2 flash sub-device (8 controls, volatile fault control).
`aw36518_parse_dt()` calls `is_yft_cts_board()` before registering each DT child
and skips flashlight registration on CTS boards.  Details:
`phase4-aw36518-framework-contract.md`.

## ABI: providers and consumers

> Provider note (added by the AW36515 phase): the shared
> `//lieppos/aw36518-recon/providers/flashlight` target is now built with
> `CONFIG_MTK_FLASHLIGHT_PT=1` (plus the two throttling surfaces stock's own
> `flashlight.ko` imports) so that it really exports `flashlight_pt_is_low`
> for AW36515.  The two CRCs consumed here, `0xe8fd8896` and `0x8287fd03`,
> are **unchanged**, so nothing in this report is affected.

* Imports: 46 — 43 from GKI `vmlinux`, plus
  `flashlight_dev_register_by_device_id` (`0xe8fd8896`) and
  `flashlight_kicker_pbm` (`0x8287fd03`) from `flashlight.ko`, and
  `is_yft_cts_board` (`0xad70697b`) from `yft_devinfo.ko`.
* All three vendor-provider CRCs are satisfied by **really built** provider
  modules, never by a hand-written `Module.symvers`:
  * `//lieppos/aw36518-recon/providers/flashlight:flashlight_provider` —
    MediaTek `flashlight-core.c` + `flashlight-device.c` built against the exact
    GKI, emits `0xe8fd8896` / `0x8287fd03`;
  * `//lieppos/yft-devinfo-recon:yft_devinfo_gki` — the existing LieppOS
    `yft_devinfo` reconstruction, emits `0xad70697b`.
* Exports: 0.  An exhaustive scan of all 471 stock module paths finds no
  consumer of any `aw36518` symbol (`phase4-aw36518-consumer-boundary.tsv`).
* Per-symbol table with stock CRC, provider, exact-GKI CRC, reconstructed
  provider CRC and rebuilt-consumer CRC (46/46 `MATCH`):
  `phase4-aw36518-provider-boundary.tsv`.

## Exact-GKI build

```
kernel      android14-6.1-2024-12_r4, common commit 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09, CI ab/12901745
target      //common:kernel_aarch64
module      //lieppos/aw36518-recon/recon:aw36518_recon
source      $GKI_WS/lieppos/aw36518-recon/recon/aw36518.c   (1018 lines)
BUILD_RC              0
compiler warnings     0
modpost warnings      0
unresolved symbols    0
KBUILD_MODPOST_WARN   not used
output      aw36518.ko, 42976 bytes,
            SHA-256 6d7cf0274b84e99b597683427b26feaac38e0fbf3b1b4299db492e073cf47429
```

The provider module `flashlight.ko` is built with `KBUILD_MODPOST_WARN=1` for
its own *tertiary* dependencies (`kicker_pbm_by_flash`,
`kicker_ppb_request_power` live in `mtk_pbm.ko`/`mtk_peak_power_budget.ko`,
which are outside this phase).  That relaxation applies only to the provider
used for CRC generation, never to `aw36518.ko` itself.

## Structural verification (stock vs rebuild)

| Metric | Result |
|---|---|
| Functions | stock 23 / rebuilt 23 / shared 23 / stock-only 0 / rebuilt-only 0 |
| Size-identical functions | 19 / 23 |
| Byte-identical functions | 13 (`init_module`, `cleanup_module`, `aw36518_open`, `aw36518_close`, `aw36518_flash_open`, `aw36518_flash_release`, `aw36518_ioctl`, `aw36518_parse_dt`, `aw36518_remove`, `aw36518_torch_brt_ctrl`, `aw36518_cooling_get_cur_state`, `aw36518_cooling_get_max_state`, `reg_store`) |
| KCFI type ids | 20 present in stock, 20/20 identical |
| Imports | 46 / 46, 0 missing, 0 extra |
| Exports | 0 / 0 |
| MODVERSIONS | 47 / 47 common, **47 CRC-identical**, 0 mismatch |
| Data objects | 32 / 32 names; all 14 initialised `.data`/`.rodata` objects byte-identical |
| Strings | 63 / 63 identical |
| Per-function reference multisets | 21 / 23 identical |
| Module identity | name, author, description, license, depends, both OF aliases and the I²C alias identical; 0 parameters both sides |

Raw output: `phase4-aw36518-verify-recon-vs-stock.txt`.

### Behavioural checklist

| Path | Status |
|---|---|
| probe (regmap, GPIO, subdev+controls, PM, parse_dt, sysfs, thermal, chip-id read, software reset) | reproduced, same order |
| `aw36518_init` sequencing (GPIO low → 400 ms timeout → mode NONE → clear `0x05`/`0x03` bit7 → fault read) | reproduced, same order and same early-return conditions |
| torch / flash brightness incl. thermal clamp and `ori_current` bookkeeping | reproduced |
| enable/disable incl. `flashlight_kicker_pbm()` ordering and `led_no` gate | reproduced |
| timeout programming | reproduced (`ms/40`, not the donor staircase) |
| fault decode | reproduced incl. the bit4-or-bit5 short-circuit mapping |
| `FLASH_IOC_SET_ONOFF`, `strobe_store`, `set_driver` reference counting | reproduced |
| cooling device (max_state 4, table, restore path) | reproduced |
| suspend (GPIO low, no I²C) / resume (`aw36518_init`) | reproduced |
| remove (no `media_entity_cleanup`, no `.shutdown`) | reproduced |
| CTS-board flashlight-registration skip | reproduced |

### Residual differences (all explained, none hardware-affecting)

1. **Instruction scheduling / partial inlining.** 11 of 23 functions differ in
   byte layout; 4 also in size (`probe`, `led0_get_ctrl`,
   `strobe_store`, `set_driver`).  The stock compiler partially inlined
   `aw36518_torch_brt_ctrl` into the `state == 0` arm of
   `aw36518_cooling_set_cur_state`; the rebuild calls it out of line there.
   Same calls, same constants, same order.
2. **`.data` layout.** `aw36518_flash_ops` and `dev_attr_reg` land at different
   offsets inside `.data` (contents byte-identical); this is the only cause of
   the 2 non-identical reference multisets.
3. **`vermagic`.** `…-g945dff7bc1bf` (Ulefone build) vs
   `…-maybe-dirty` (local Kleaf build of the same 6.1.115-android14-11 tree).
   Cosmetic build-provenance string; it is 87 vs 85 bytes in `.modinfo`.
4. **`__LINE__` values** inside four log strings (`probe`, suspend, resume) come
   from the vendor file's line numbering (932/986/991/993/1023/1033) and differ
   in the reconstruction, whose format strings and argument lists are otherwise
   identical.
5. **`aw36518_parse_dt` early return** when the device has no `of_node`: stock
   falls through to the epilogue leaving a stale value in `w0`; the
   reconstruction returns 0.  Unreachable for an I²C-of device and ignored by
   `probe`.

No difference touches a register write, a current value, a timing value, an
ABI symbol, a CRC or a device identity.

## Safety deviations

None.  No build-time flash/torch gate was added (`AW36518_ALLOW_FLASH` /
`AW36518_ALLOW_TORCH` were considered and rejected: any gate would either be a
no-op at the stock default or would change stock behaviour on a driver that
loads on every boot).  The vendor debug sysfs `reg` attribute is reproduced
because it is stock ABI — it is a raw I²C register write path and must remain
root-only in LieppOS policy.

## Runtime-validation status

```
STATIC RECONSTRUCTION      DONE   (relocation-aware disassembly of the stock oracle)
BUILD VERIFICATION         DONE   (exact GKI ab/12901745, BUILD_RC=0, 0 warnings, 0 unresolved)
ABI VERIFICATION           DONE   (46/46 imports, 47/47 CRCs, 0 exports, real provider symvers)
LIVE HARDWARE VALIDATION   NOT DONE - intentionally
```

No torch/flash was fired, no I²C register was written, no GPIO was driven, no
module was inserted or removed, and no partition or DT was modified during this
phase.  Live validation belongs to Slot-B bring-up.

## Evidence index

| Artifact | Content |
|---|---|
| `phase4-aw36518-stock-oracle.txt` | frozen oracle identity |
| `phase4-aw36518-stock-inventory.md` | Phase 0/1 ELF inventory |
| `phase4-aw36518-functions.tsv` / `-objects.tsv` / `-imports.tsv` / `-modversions.tsv` | stock symbol tables (with KCFI ids and CRCs) |
| `phase4-aw36518-hardware-contract.md` | Phase 2 fitted-part contract |
| `phase4-aw36518-dt-contract.md` | Phase 3 device-tree contract |
| `phase4-aw36518-userspace-camera-contract.md` | Phase 4 userspace/HAL contract |
| `phase4-aw36518-source-candidates.md` | Phase 5 donor search |
| `phase4-aw36518-provider-boundary.tsv` / `-consumer-boundary.tsv` | Phase 6 ABI boundary |
| `phase4-aw36518-framework-contract.md` | Phase 7 + 9 framework and fault contract |
| `phase4-aw36518-register-map.tsv` | Phase 8 per-instruction register map |
| `phase4-aw36518-electrical-contract.md` | Phase 8 current/timeout/protection contract |
| `phase4-aw36518-RED.md` | Phase 10 mandatory RED |
| `phase4-aw36518-donor-to-recon.diff` | Phase 11 donor → reconstruction delta |
| `phase4-aw36518-verify-recon-vs-stock.txt` | Phase 14 verification output |
| `phase4-aw36518-family-comparison.md` | Phase 15 AW36518_V2 / AW36515 comparison |
| `phase4-aw36518-v2-reconstruction.md` | sibling phase: AW36518 → AW36518_V2 delta reconstruction |
| `$GKI_WS/lieppos/aw36518-recon/recon/` | reconstruction source + Kleaf target |
| `$GKI_WS/lieppos/aw36518-recon/providers/flashlight/` | real provider used for CRC generation |
| `workspace/phase4-aw36518/` (gitignored) | disassembly, section blobs, sibling inventories, public donor copies, extractor/comparator tooling |

## Final verdict

`aw36518.ko` is **frozen and ready for integration**: the LieppOS source builds
clean against the exact GKI `ab/12901745`, links against really built providers,
and is ABI-identical to the stock module (imports, CRCs, exports, module
identity) with a fully explained, hardware-neutral residue.  The remaining step
is live validation on Slot B, which is deliberately out of scope for this phase.
Reconstructing `aw36518_v2.ko` from this source is a rename plus removal of one
call; `aw36515.ko` needs its own pass (dual channel).
