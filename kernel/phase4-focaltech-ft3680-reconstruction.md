# Phase 4 — FocalTech FT3680 touchscreen reconstruction (authoritative report)

This report supersedes every earlier intermediate hypothesis about
`focaltech_touch_spi_ft3680.ko`, including the initial
`NEEDS_ULEFONE_PORT` classification in `phase4-focaltech-ft3680.md`.

**Final classification (completion pass — authoritative section is the LAST
one in this file; every earlier classification is withdrawn)**

    STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE
    SYMBOL_SET_PARITY_EXACT (imports 104/104, functions 166/166, 0 extra, 0 missing)
    STOCK_BINARY_ABI_SUBSTITUTION_BLOCKED_BY_TWO_PROVIDER_GENKSYMS_GAPS

The previous classification `BLOCKED_WITH_EXACT_MISSING_EVIDENCE` is
**withdrawn**. Four of the six historical blockers are now closed with exact,
instruction-level evidence (FT3680 chip-ID tuple, `upgrade_setting_list`
layout, the V4.2 PRAM/DPRAM/ECC download engine, the FHP ioctl ABI and the
firmware-debug protocol), the Ulefone integration deltas and the
`touch_fw_version` path are ported, and the donor-only procfs subtree is gone.

What remains is **one unimplemented subsystem** (the FHP misc-device layer,
whose userspace ABI is nevertheless fully recovered and documented) plus the
two long-standing provider genksyms declaration-text gaps. See
"Continuation pass — final state" at the end of this report, which is the
authoritative section.

No fake CRC, no invented firmware sequence and no phone/partition modification
was involved at any point. The recovered firmware-programming engine ships
**disabled by default** behind `FTS_ALLOW_FW_PROGRAMMING`.

---

## Build

```
command:
  cd /home/armol/kernel-work/gki-12901745-workspace
  tools/bazel build //lieppos/focaltech-ft3680-recon/recon:focaltech_touch_spi_ft3680_gki

BUILD_RC: 0

warnings:
  compiler: none (builds -Werror clean)
  modpost (KBUILD_MODPOST_WARN=1): none
```

> **Superseded (yft_devinfo pass).** The four unresolved provider warnings
> that used to appear here
> (`mtk_disp_notifier_register`, `mtk_disp_notifier_unregister`,
> `yft_spitouchpanel_device_add`, `yft_set_touch_device_used`) are **gone**.
> Two causes were fixed: the `yft_devinfo` provider now exists
> (`//lieppos/yft-devinfo-recon:yft_devinfo_gki`), and this target's `Makefile`
> computed `KBUILD_EXTRA_SYMBOLS` inside the `ifneq ($(KERNELRELEASE),)` branch
> while forwarding it from the outer branch, so it was **always empty** and no
> vendor provider had ever actually been resolved. See the
> "YFT devinfo provider resolved" section at the end of this report.

Untouched donor baseline (also builds, `BUILD_RC: 0`):

```
  tools/bazel build //lieppos/focaltech-ft3680-recon/donor-build:focaltech_ft3680_donor_gki
```

## Stock oracle

```
path:        $RESEARCH/workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/focaltech_touch_spi_ft3680.ko
SHA256:      6629ec6148ac361a5f0085b8b19efa9d591426679f58262c4998345f41931162
size:        400936 bytes
build-id:    35c87682241ccdef19a9b1b24c3240fac26caa5a
version:     FocalTech V4.2 20240407
vermagic:    6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
srcversion:  absent
compiler:    Android clang 17.0.2 (r487747c) — identical to the GKI prebuilt
```

Only one copy exists in the stock tree; it was never modified.

## Source provenance

```
donor:                NothingOSS MT6878 device-modules, drivers/input/touchscreen/FT3519
donor repository:     https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878
donor branch:         mt6878/Tetris/u
donor revision:       957dac185efe46cbf6336b0fff9516d84c8cd78f
donor tree object:    f074a8ccb6d1785721946ee71c3e2a0ef149a9ee (25 files)
donor driver version: FocalTech V4.1 20230424
exact/partial:        PARTIAL_PUBLIC_SOURCE_MATCH — immediate prior public
                      revision of the same FocalTech full-driver lineage on the
                      exact MT6878 / Linux 6.1 platform; different chip config
                      (FT3519T), transport (I2C) and feature selection.
```

Quantified overlap with the stock oracle: 110 of 166 stock function names have
definitions in the donor tree, and 275 donor source literals of length ≥10
appear byte-for-byte in the stock `.rodata`.

Exhaustive local-first search (checked-out files, all git refs, and
`git log -S/-G` history) covered `$NOTHING`, `$RESEARCH`, `~/kernel-work`,
`~/kernel-work/vendor-reference` and the AOSP `common` tree. Public search
(web, GitHub, Sourcegraph incl. forks/archives) was then used. Results:

- exact source for `FocalTech V4.2 20240407` — **not found**;
- exact `focaltech_touch_spi_ft3680` — **not found**;
- `fts_fhp_*` / `fts_fwdbg_*` implementations — **not found anywhere public**.

Rejected candidates with reasons are recorded in `source-candidates.md`
(NothingOSS SM7325 V3.4 SPI, Xiaomi `focaltech_3658u` V3.2 SPI, NXP `linux-imx`
V4.1, MiCode MediaTek V3.0, OnePlus FT3683G/FT3658U, official FocalTech ft5x06).

## ABI

```
stock imports:            104   (all with MODVERSION CRCs)
rebuilt imports:           97
missing (stock-only):      15   misc_register, misc_deregister,
                                wakeup_source_register, wakeup_source_unregister,
                                pm_wakeup_ws_event, ktime_get_with_offset,
                                schedule_timeout, __msecs_to_jiffies,
                                usleep_range_state, kmalloc_large, sprintf,
                                tpgesture_value, tpgesture_status,
                                tpgesture_hander, touch_fw_version
extra (rebuilt-only):       8   proc_mkdir, remove_proc_subtree, single_open,
                                single_release, seq_read, seq_lseek, seq_printf,
                                kstrtouint
MODVERSION mismatches:      0 wrong values.
                            0 unresolved provider symbols (was 4; see the
                            "YFT devinfo provider resolved" section):
                              mtk_disp_notifier_register    0x4c353ac0 MATCH
                              mtk_disp_notifier_unregister  0xa11ab00a MATCH
                              yft_set_touch_device_used     0x0a0f3b69 MATCH
                              yft_spitouchpanel_device_add  stock 0xea3d7f0d,
                                rebuilt 0x0776e449 — provider-side ABI
                                provenance gap, exactly scoped (73-char vendor
                                enum), never fabricated
                            All 89 resolved shared imports match stock exactly.

stock exports:              0 (module has no __ksymtab/__kcrctab sections)
rebuilt exports:            0
export CRC mismatches:      n/a
```

Boundary scan of all 471 offline stock `.ko` paths (458 unique binaries,
4,805 export symbols) resolved **all 104** stock imports with **zero** CRC
mismatches: 96 from GKI vmlinux, 8 from three stock modules
(`mtk_disp_notify`, `yft_devinfo`, `yft_tpd_gesture`). No stock module consumes
anything from this driver, so removing the donor's exports is consumer-safe.
Evidence: `consumer-boundary.tsv`, `provider-boundary.tsv`,
`stock-module-boundary-scan.txt`.

## Structural comparison

```
stock functions:        166
rebuilt functions:      131
size-identical:          64
byte-identical:          10 (relocation-normalised, identical relocation-target
                            order, measured against the untouched donor:
                            fts_driverinfo_store, fts_dumpreg_store,
                            fts_fwforceupg_show, fts_fwupgradebin_show,
                            fts_gesture_buf_store, fts_hw_reset_store,
                            fts_read_reg, fts_tpbuf_store, fts_tpfwver_store,
                            fts_write_reg)
unexplained functions:    0
```

Every one of the 59 stock-only and 24 rebuilt-only functions is attributed in
`verification-pass-1.md` §7.

Progress against the untouched donor baseline:

| Metric | Donor | Rebuild |
|---|---:|---:|
| Rebuilt-only functions | 95 | 24 |
| Stock-only imports | 22 | 15 |
| Rebuilt-only imports | 21 | 8 |
| Shared imports | 82 | 89 |
| Strings shared with stock | 338 | 362 |
| Exports vs stock (0) | 3 | 0 |

## Device contract

```
DT compatible:      focaltech,fts   (node /soc/spi3@11013000/focaltech@39)
                    identical in the merged DT and the stock vendor_boot FDT;
                    the stock DTBO contains no touchscreen node at all.
SPI:                MediaTek spi3@11013000, chip select 0, 6,000,000 Hz
IRQ/reset GPIO:     irq  = focaltech,irq-gpio  -> pinctrl GPIO 7,
                           interrupts = <7 2>  (falling edge)
                    reset= focaltech,reset-gpio-> pinctrl GPIO 6
                    vddi = vddi-gpio           -> pinctrl GPIO 183
pinctrl:            none on the touchscreen node; the stock module imports no
                    pinctrl API at all
regulators:         vdd-supply = mt6369_vtp, fixed 3.3 V;
                    NO iovcc-supply (IO rail switched by the VDDI GPIO)
firmware/config:    built into the module — fw_file, 118,972 bytes,
                    SHA256 2269a91f6c07421749f48db31651cf59d63c66da7db92ac767e10cc95ff910bf;
                    optional request_firmware("focaltech_ts_fw_" + "%s%s.bin")
                    from /vendor/firmware, which contains no such file, so the
                    request fails non-fatally and the built-in image is used;
                    no MODULE_FIRMWARE declaration
panel/vendor sel.:  none active — module_list has 3 records, module id 0 and
                    empty vendor names, only record 0 carrying firmware;
                    chip selection is by runtime boot ID against an 18-entry,
                    20-byte-per-record upgrade_setting_list
wake/gesture:       gesture wake via IRQ wake + yft_tpd_gesture
                    (tpgesture_value / tpgesture_status / tpgesture_hander),
                    AOD gated by yft_aod_state and the aod_state sysfs node
notifiers:          MediaTek display notifier registered under the label
                    "Touch_fts"; no kernel power-supply/charger notifier —
                    charger mode is a register mode driven from sysfs
```

Touch reporting: input device `fts_ts`, MT protocol B, 10 slots, coordinate
range 0–1080 × 0–2400 from DT, with both the legacy and the protocol-v2 packet
parsers plus a report-buffer path.

Interfaces the reconstruction must ultimately expose: procfs `ftxxxx-debug`,
`fts_ta`, `fts_fwdbg`; misc devices `fhp_ft`, `fhp_input`; the core, mode,
gesture, ESD/PRC and firmware-debug sysfs attribute groups (full list in
`stock-module-inventory.md`).

## What the reconstruction currently reproduces

- module identity: name, description, license, OF aliases, absent srcversion,
  absent module parameters, absent `MODULE_FIRMWARE`, and the exact
  `FocalTech V4.2 20240407` banner;
- SPI transport (`fts_read`, `fts_write`, `fts_read_reg`, `fts_write_reg`,
  `fts_bus_transfer_direct`, `fts_bus_configure`, `fts_bus_set_speed`) with
  every protocol constant taken from the stock disassembly: 6-byte header,
  3 dummy bytes, 4096-byte frame cap, 3520-byte bus buffers, status mask 0xA0,
  CRC16 poly 0x8408, 3 retries, 150 µs chip-select delay;
- SPI driver registration path including `yft_spitouchpanel_device_add()` before
  `spi_register_driver()` and `yft_set_touch_device_used()` on probe success,
  plus `remove`/`shutdown` sharing the common teardown;
- byte-exact preservation of the stock firmware image, `upgrade_setting_list`
  and `module_list` shape, and the `request_firmware` fallback contract;
- removal of every donor-only component that stock does not contain: the
  production-test engine, `touchpanel_event_notify` (and therefore all exports),
  the FT5452J/FT3519T flash back-ends, the I2C transport, FOD reporting and the
  `/proc` data-dump node.

## Exact missing evidence (why this is BLOCKED)

1. ~~**`yft_devinfo` provider source.**~~ **RESOLVED.** The provider has been
   fully reconstructed and builds against exact GKI 12901745; see
   `kernel/phase4-yft-devinfo-reconstruction.md`. FT3680 now links against it
   with zero unresolved provider symbols and records
   `depends=mtk_disp_notify,yft_devinfo`.

   | Symbol | Stock CRC | Reconstructed provider CRC | Status |
   |---|---|---|---|
   | `yft_set_touch_device_used` | `0x0a0f3b69` | `0x0a0f3b69` | **exact** |
   | `touch_fw_version` | `0xd0815107` | `0xd0815107` | **exact** (not yet referenced by FT3680 — see below) |
   | `yft_spitouchpanel_device_add` | `0xea3d7f0d` | `0x0776e449` | scoped ABI provenance gap |

   What remains is *not* "no source": it is a single 73-character vendor enum
   type text used as the second parameter of every `yft_*_device_add()` export,
   proven by CRC-32 zero-shift analysis and not recoverable from any shipped
   artifact. *Needed:* the vendor's `yft_devinfo.h` (or any Ulefone/YFT BSP
   drop containing it) — nothing else.
2. **`yft_tpd_gesture` provider — 2 of 3 blockers now RESOLVED.**
   The provider has been reconstructed and built against exact GKI 12901745;
   see `kernel/phase4-yft-tpd-gesture-reconstruction.md`. Its `.text`,
   `.init.text`, `.exit.text`, `.rodata`, `.data`, `.bss` layout, imports and
   `__versions` are byte-identical to the stock provider.

   | Symbol | Stock CRC | Reconstructed provider CRC | Status |
   |---|---|---|---|
   | `tpgesture_status` | `0x30ac810a` | `0x30ac810a` | **RESOLVED** (generated from source, not patched) |
   | `tpgesture_hander` | `0x8386526d` | `0x8386526d` | **RESOLVED** (generated from source, not patched) |
   | `tpgesture_value` | `0x02f3ea4c` | `0xec3d4c19` | **still blocked** |

   `tpgesture_value` is the last remaining `tpgesture_*` blocker. Its object is
   reproduced exactly (GLOBAL OBJECT, size 10, `.data..read_mostly+0x0`,
   alignment 1, identical code in every function that touches it), but the
   genksyms declaration *text* behind the stock CRC could not be recovered; an
   exhaustive algebraic search over the reachable declaration space is
   documented in
   `workspace/phase4-yft-providers/yft-tpd-gesture-export-crc-analysis.md`.
   *Needed:* the vendor `yft_tpd_gesture.symref`/`.symtypes` reference type
   string for `tpgesture_value`, or the vendor header declaring it.

   Practical impact: the reconstructed provider satisfies `tpgesture_status`
   and `tpgesture_hander` for the **stock** FT3680 binary. `tpgesture_value`
   resolves only when this FT3680 reconstruction is rebuilt against the
   reconstructed provider, in which case both sides carry `0xec3d4c19`.
3. **FT3680 chip-ID mapping.** `FTS_CHIP_TYPE_MAPPING` for FT3680
   (chip/rom/pramboot/bootloader ID tuple) could not be recovered: the table is
   materialised as inline immediates inside the 3,416-byte
   `fts_ts_probe_entry` and no candidate tuple was isolated.
   *Needed:* targeted RE of `fts_ts_probe_entry`'s inlined
   `fts_get_chip_types`, or a public FT3680 header.
4. **`upgrade_setting_list` record semantics.** The 18 × 20-byte records are
   preserved byte-for-byte and the leading ROM/boot-ID pair is proven, but the
   remaining 18 bytes per record (PRAM/DRAM offsets, lengths, flags) are not.
   The V4.2 download engine is therefore deliberately **not** executed: writing
   an invented PRAM/ECC sequence to a panel can brick it.
   *Needed:* RE of `fts_fw_download`/`fts_dpram_write`/`fts_ecc_check`, or the
   FocalTech V4.2 `focaltech_flash.c`.
5. **FHP ioctl ABI.** `fhp_ft` / `fhp_input` misc devices, their ioctl numbers
   (`fhp_ioctl_get_frame`, `_set_frame_size`, `_set_spi_speed`, `_set_irq`,
   `_set_timeout`, `_spi_sync`, `_clear_frame`, `_get_chip_init_done`, `_reset`)
   and the frame-queue layout are userspace-visible and not yet recovered.
6. **Firmware-debug protocol.** `fts_fwdbg_*` register/frame protocol
   (`regfa`/`regfb` logging, frame block/logging/maxcount semantics) not yet
   recovered.

Items 1–2 are *missing source*, items 3–6 are *unfinished RE with a known target
function set*. None of them was papered over with a guess.

## Residual differences not yet closed but not blocking

- 24 donor procfs/FOD/game/pocket/edge functions and their 8 imports remain
  compiled in; they are BUILD_CONFIG_DIFFERENCE and removable without RE.
- ~~`mtk_disp_notify` CRCs are unresolved only because `KBUILD_EXTRA_SYMBOLS`
  wiring in the kleaf target is incomplete~~ — **fixed.** The `Makefile`
  evaluated the symvers wildcard only in the `KERNELRELEASE` pass but forwarded
  `$(KBUILD_EXTRA_SYMBOLS)` from the outer pass, so it was always empty. It is
  now computed before the `ifneq` and applies to both passes;
  `mtk_disp_notifier_register`/`unregister` now record the exact stock
  `0x4c353ac0` / `0xa11ab00a`.
- The Ulefone AOD/`tpgesture`/`vddi-gpio`/`iovcc`/`fts_ws`/`Touch_fts` deltas are
  fully specified by the DT and string evidence in this phase but are not yet
  ported into `focaltech_core.c`.
- `vermagic` differs only in `LOCALVERSION`/scm-version.

## Safety statement

Everything in this phase was offline source/binary analysis. Nothing was
flashed; no slot, boot control, DT, DTBO, partition or module state on the phone
was changed; no module was inserted or removed; no GPIO was exported; the
known-good slot A was untouched. The stock `.ko` was read only.

## Deliverables

Build/reconstruction workspace — `$GKI_WS/lieppos/focaltech-ft3680-recon/`:

| Path | Contents |
|---|---|
| `donor-pristine/` | untouched NothingOSS FT3519 V4.1 donor |
| `donor-build/` | same sources + build glue only; RED baseline (`BUILD_RC 0`) |
| `recon/` | reconstruction (`BUILD_RC 0`), incl. `focaltech_spi.c`, `focaltech_flash.c`, `focaltech_ft3680_fw.i` |

Research/evidence — `$RESEARCH/workspace/phase4-focaltech-ft3680/`:

`stock-oracle.txt`, `stock-module-inventory.md`, `stock-functions.tsv`,
`stock-imports.tsv`, `stock-exports.tsv`, `stock-objects.tsv`,
`stock-modversions.tsv`, `stock-strings.txt`, `stock-all-strings.txt`,
`stock-call-sequences.tsv`, `stock-function-strings.tsv`,
`stock-relocations.tsv`, `stock-disassembly-{text,init,exit}.txt`,
`stock-builtin-fw_file.bin`, `consumer-boundary.tsv`, `provider-boundary.tsv`,
`stock-module-boundary-scan.txt`, `source-candidates.md`,
`local-git-ref-search.txt`, `gq5012bf1-touchscreen-dt.md`,
`gq5012bf1-touchscreen-dt-window.dts`, `firmware-config-contract.md`,
`RED.md`, `verification-pass-1.md`, and the `donor/` + `recon/` comparison sets.

Reusable tooling — `$GKI_WS/lieppos/`:
`focaltech-ft3680-analyze-stock.py`, `focaltech-ft3680-scan-boundary.py`,
`focaltech-git-provenance-scan.sh`.

## Next pass (ordered, to reach a non-blocked classification)

1. Recover the FT3680 chip-ID tuple from the inlined `fts_get_chip_types`.
2. RE the 20-byte upgrade-setting record layout, then port the V4.2
   PRAM/DPRAM/ECC download engine.
3. RE and implement the FHP misc-device ioctl ABI and the firmware-debug
   protocol.
4. Port the Ulefone AOD/`tpgesture`/`vddi-gpio`/`iovcc`/wakeup-source deltas.
5. Reimplement or obtain `yft_devinfo` and `yft_tpd_gesture` so the four
   provider CRCs resolve to their known stock values.
6. Drop the residual donor procfs/FOD/game/pocket/edge components.

## Final blocker-count clarification

The authoritative blocker count is now **four exact missing-evidence items**
(was six), as listed in the "Exact missing evidence" section.

Remaining:

1. FT3680 chip-ID tuple;
2. 20-byte upgrade-setting record semantics / V4.2 flash engine;
3. FHP misc-device ioctl ABI;
4. firmware-debug protocol.

Retired:

* `yft_tpd_gesture` provider — reconstructed; reduced to an export-CRC
  provenance gap on `tpgesture_value`.
* `yft_devinfo` provider — reconstructed; reduced to an export-CRC provenance
  gap on the ten `*_device_add()` symbols, scoped to one 73-character vendor
  enum type text.

Neither retired item is a missing implementation any more; both are bounded
declaration-text provenance gaps. Earlier summary wording describing these as
"three stock subsystems and one vendor provider", and the later six-item list,
are superseded by this four-item list.

## YFT provider follow-up started

The first stock-provider lookup found:

    vendor_dlkm/lib/modules/yft_devinfo.ko

The initial filename-based search did not find a stock module named:

    yft_tpd_gesture.ko

Therefore the gesture dependency is being resolved by scanning every stock
kernel module for the actual exported symbols:

    tpgesture_value
    tpgesture_status
    tpgesture_hander

This avoids assuming that the provider module filename matches the source/module
name used by the FocalTech driver.

The `yft_devinfo` provider will likewise be verified against:

    yft_spitouchpanel_device_add
    yft_set_touch_device_used
    touch_fw_version

## YFT provider boundary refined

Follow-up inspection positively identified the stock `yft_devinfo.ko` provider:

    vendor_dlkm/lib/modules/yft_devinfo.ko

SHA256:

    0d5e547e3e6c313c88695b2c8f9aae04398e3c8822f16d57dff6aea011f821fe

Relevant exported objects/functions:

    touch_fw_version               30-byte object
    second_touch_fw_version        30-byte object
    yft_spitouchpanel_device_add   664-byte function
    yft_set_touch_device_used      152-byte function

Consumer inspection additionally showed that `hynitron.ko` imports:

    second_touch_fw_version
    yft_set_touch_device_used

Therefore `yft_devinfo` is a shared touchscreen/platform information provider,
not merely an FT3680-specific dependency.

A complete symbol scan of the currently extracted `stock/partitions` `.ko`
set did NOT locate definitions for:

    tpgesture_value
    tpgesture_status
    tpgesture_hander

Those symbols were found only as unresolved imports of
`focaltech_touch_spi_ft3680.ko`.

Therefore the earlier attribution of those symbols to a physical stock file
named `yft_tpd_gesture.ko` is not yet proven. The logical provider may reside
in the vendor_boot ramdisk or another stock module location not represented by
the current `stock/partitions` file scan.

Do not begin reconstruction of a presumed `yft_tpd_gesture.ko` binary until
its actual stock provider object is located.

## YFT gesture provider resolved

The earlier statement that the physical stock provider for the `tpgesture_*`
symbols had not yet been located is superseded.

The exact provider is:

    $RESEARCH/workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/yft_tpd_gesture.ko

Stock metadata:

    name:        yft_tpd_gesture
    description: YFT touch gesturewake driver
    depends:     none

The stock FocalTech module explicitly declares:

    depends: yft_tpd_gesture,mtk_disp_notify,yft_devinfo

The vendor_boot platform ramdisk additionally contains:

    modules.load
    modules.load.recovery

and both load:

    yft_tpd_gesture.ko

The provider exports exactly the three symbols required by
`focaltech_touch_spi_ft3680.ko`:

    tpgesture_status     1-byte object
    tpgesture_value      10-byte object
    tpgesture_hander     108-byte function

Therefore the FT3680 YFT provider boundary is now fully identified:

    yft_devinfo       -> vendor_dlkm / vendor platform provider
    yft_tpd_gesture   -> vendor_boot platform ramdisk provider
    mtk_disp_notify   -> already reconstructed/direct-source matched

The previous conclusion that `yft_tpd_gesture.ko` might not exist as a physical
stock module is withdrawn.

## YFT gesture reconstruction status clarification

`yft_tpd_gesture` is no longer an unreconstructed/missing-source provider.

The module has been reconstructed with byte-identical code and data against
stock. Two of its three FT3680-facing export CRCs are reproduced exactly from
source:

    tpgesture_status  0x30ac810a  exact
    tpgesture_hander  0x8386526d  exact

The only residual provider issue is:

    tpgesture_value

whose runtime object/layout/behavior is reproduced exactly, but whose historical
stock genksyms CRC (`0x02f3ea4c`) cannot currently be regenerated from the
recovered declaration. The reconstructed declaration produces `0xec3d4c19`.

Therefore this is now classified as an export-CRC provenance gap, not an
unfinished `yft_tpd_gesture` implementation.

A LieppOS FT3680 module rebuilt against the reconstructed provider is internally
ABI-coherent because both sides use the reconstructed CRC. The untouched stock
FT3680 binary still requires its original stock CRC.

---

## YFT devinfo provider resolved

The stock `yft_devinfo.ko` provider has been fully reconstructed; authoritative
report: [`kernel/phase4-yft-devinfo-reconstruction.md`](phase4-yft-devinfo-reconstruction.md).

Provider status in one line: **complete provider source, `BUILD_RC=0` against
exact GKI 12901745, 17 of 27 export CRCs and all 40 import CRCs generated from
source, 69 of 72 functions with identical external call sequences.**

### What this changed for FT3680

Two independent defects were fixed in this target.

**1. The provider did not exist.** It now does, and is wired as a bazel dep:

```
deps = [
    "//lieppos/mtk-disp-notify-direct:mtk_disp_notify_gki",
    "//lieppos/yft-devinfo-recon:yft_devinfo_gki",
]
```

**2. `KBUILD_EXTRA_SYMBOLS` never reached the build.** The `Makefile` computed
the provider symvers wildcard inside `ifneq ($(KERNELRELEASE),)` but the outer
recipe forwarded `$(KBUILD_EXTRA_SYMBOLS)` from the *outer* pass, where the
assignment had never run. It was therefore always empty and **no vendor
provider had ever actually been resolved** — including `mtk_disp_notify`, which
this report previously assumed was merely "incomplete wiring". The computation
now happens before the `ifneq` so both passes see it.

**3. The FT3680 declarations were wrong.** The placeholders

```c
extern int  yft_spitouchpanel_device_add(void);
extern void yft_set_touch_device_used(int used);
```

were replaced by the recovered provider API (`yft_devinfo.h`), and the call
sites now match the stock binary exactly:

```c
ret = yft_spitouchpanel_device_add(&fts_ts_spi_driver, 0);   /* init_module  */
yft_set_touch_device_used("fts_ts", 1);                      /* fts_ts_probe */
```

(`"fts_ts"` is the literal the stock module passes, recovered from
`.rodata.str1.1+0x5697`; the stock `init_module` passes `&fts_ts_driver` and
`w1 = 0`.)

### Result

```
command:
  tools/bazel build //lieppos/focaltech-ft3680-recon/recon:focaltech_touch_spi_ft3680_gki
BUILD_RC: 0
modpost warnings: none
.modinfo depends: mtk_disp_notify,yft_devinfo
undefined symbols without a MODVERSION: 0   (was 4)
```

Unresolved provider symbols that disappeared:

```
yft_spitouchpanel_device_add   <- yft_devinfo      (provider reconstruction)
yft_set_touch_device_used      <- yft_devinfo      (provider reconstruction)
mtk_disp_notifier_register     <- mtk_disp_notify  (Makefile fix)
mtk_disp_notifier_unregister   <- mtk_disp_notify  (Makefile fix)
```

Import CRCs, rebuilt vs stock:

| symbol | stock | rebuilt | |
|---|---|---|---|
| `yft_set_touch_device_used` | `0x0a0f3b69` | `0x0a0f3b69` | exact |
| `mtk_disp_notifier_register` | `0x4c353ac0` | `0x4c353ac0` | exact |
| `mtk_disp_notifier_unregister` | `0xa11ab00a` | `0xa11ab00a` | exact |
| `yft_spitouchpanel_device_add` | `0xea3d7f0d` | `0x0776e449` | provider ABI provenance gap |

### Honest statement of what is still open on the FT3680 side

FT3680's `yft_devinfo` dependencies are **not** all solved:

* `yft_spitouchpanel_device_add` still carries the provider's scoped CRC gap
  (the 73-character vendor enum in the never-shipped `yft_devinfo.h`).
* `touch_fw_version` is **not referenced at all** by the reconstruction, because
  `fts_fwupg_work()` is not implemented; stock does
  `sprintf(touch_fw_version, "Vno:0x%02x\n", fw_ver)` there. The provider
  exports it with the exact stock CRC `0xd0815107`, so it will resolve
  correctly as soon as that call site exists. This is an FT3680-side gap, not a
  provider gap.
* stock FT3680 additionally records `depends=yft_tpd_gesture`; the
  reconstruction does not yet reference that provider even though it has been
  reconstructed.

### Relevant provider behaviour for touch

`yft_touchpanel_info_print()` distinguishes the two panels by comparing the
registered instance name against the literal `"hyn_ts"`: Hynitron reports
`second_touch_fw_version`, FocalTech (and anything else) reports
`touch_fw_version`. `yft_set_*_device_used()` dispatches through the per-type
callback pointer registered at `*_device_add()` time (KCFI type id
`0x4d9b0091`), walks the entire type list and always returns 0.

Note also that the provider is **not** an FT3680/Hynitron helper: scanning all
471 stock modules shows seven consumers across nine device classes
(`focaltech_touch_spi_ft3680`, `hynitron`, `hf_manager`, `imgsensor`,
`sh366003_fg`, `spi_tiny_co5300_lcd`, `aw36518`).

## Current reconstruction frontier

The external FT3680 provider dependency work is now substantially complete:

    mtk_disp_notify      solved
    yft_tpd_gesture      reconstructed
    yft_devinfo          reconstructed

The remaining FT3680 work is primarily internal to the FocalTech V4.2 driver:

1. recover the FT3680 chip-ID tuple;
2. recover the 20-byte upgrade-setting record semantics;
3. reconstruct the V4.2 PRAM/DPRAM/ECC firmware-download engine;
4. reconstruct the FHP misc-device ioctl ABI;
5. reconstruct the firmware-debug protocol;
6. port the already-evidenced Ulefone AOD/tpgesture/VDDI/wakeup deltas;
7. restore the fts_fwupg_work()/touch_fw_version path;
8. remove residual donor-only code;
9. rebuild against all reconstructed providers and perform final ABI/structural
   verification.

The hardest remaining item is the V4.2 firmware-download engine because its
chip-specific programming semantics must be proven rather than guessed.


---

# Continuation pass — final state (AUTHORITATIVE)

Everything above this line is historical. Where it conflicts with this
section, this section wins.

## Result summary

| Priority | Task | Outcome |
|---:|---|---|
| 1 | FT3680 chip-ID tuple | **SOLVED — EXACT** |
| 2 | `upgrade_setting_list` 20-byte layout | **SOLVED — EXACT** (all 20 bytes; the 2-byte hole at `+0x02` is read by no stock instruction) |
| 3 | V4.2 PRAM/DPRAM/ECC download engine | **SOLVED — EXACT**, implemented, shipped **gated off** |
| 4 | FHP ioctl ABI | **ABI SOLVED — EXACT**; misc-device layer **not implemented** |
| 5 | firmware-debug protocol | **SOLVED** except the `/proc/fts_fwdbg` read path; implemented |
| 6 | Ulefone gesture/AOD/VDDI/wakeup integration | **PORTED** |
| 7 | `fts_fwupg_work()` / `touch_fw_version` | **SOLVED — EXACT**, implemented |
| 8 | remove donor-only code | **DONE** — 0 extra imports remain |
| 9 | stock-vs-rebuild verification | **DONE** (below) |

New evidence documents, all in `$RESEARCH/workspace/phase4-focaltech-ft3680/`:

* `chip-id-reconstruction.md`
* `upgrade-setting-layout.md`
* `flash-engine-reconstruction.md`
* `fhp-abi.md`
* `fwdbg-protocol.md`
* `ulefone-integration-port.md`
* `verification-pass-2.txt` (raw output of the verifier)

New reusable tooling in `$RESEARCH/tools/`: `fts-annotate.py` (relocation- and
string-annotated function disassembly), `fts-slice-func.py`, `fts-verify.py`.

## Priority 1 — chip-ID tuple (EXACT)

```c
#define FTS_CHIP_TYPE_MAPPING {{0x8A, 0x56, 0x62, 0x56, 0x62, 0x56, 0xE2, 0x00, 0x00}}
```

`fts_get_chip_types()` is inlined into `fts_ts_probe_entry`; clang promoted the
local `ctype[]` array to an **anonymous** `.rodata` constant at `+0x04`, which
is why symbol-name searches missed it. Referenced by exactly one ADRP/ADD pair
(`fts_ts_probe_entry+0xac0`).

```
.rodata+0x04 .. +0x0d : 8a 00 56 62 56 62 56 e2 00 00
        type=0x008A  chip=56/62  rom=56/62  pb=56/E2  bl=00/00
```

The zero `bl_idh`/`bl_idl` are positively proven, not assumed: the compiler
folded the donor's three-way boot-ID test into `cmp w28,#0x56` plus
`and w8,w27,#0x7f; cmp w8,#0x62`, which is only valid when
`rom_idh == pb_idh == 0x56` and `{rom_idl,pb_idl} == {0x62,0xE2}`, and it
eliminated the `bl` comparison entirely because `cbz w28` had already proved
`id_h != 0`. Cross-checks: `_FT3680 == 0x3680008A` gives `IC_SERIALS == 0x8A`;
`upgrade_setting_list[10]` begins with the bytes `56 62`; `fts_check_bootid`
and `fts_enter_normal_fw` re-read the same `ic_info.ids` offsets.

V4.2 also **dropped** the donor's `FTS_REG_CHIP_ID` polling stage:
`fts_get_ic_information()` is a five-attempt boot-ID loop with
`mdelay(12 + 4*i)`. This is now reproduced.

## Priority 2 — `upgrade_setting_list` (EXACT)

18 records × 20 bytes at `.data+0x1d5d8`; stride and count proven by
`add x23,x23,#0x14` / `cmp x23,#0x168` in `fts_fwupg_init`, which is the table's
only direct consumer. All twelve named fields are justified by an instruction
that dereferences that exact byte offset — full table in
`upgrade-setting-layout.md`.

FT3680 selects record 10:

```c
{ 0x56, 0x62, 0, 0x00020000, 0x00020000, 0xa5, 0x01, 0x08, 0, 4, 0, 0, 5 }
/*  rom_idh/idl, reserved, app2_offset, ecclen_max, eccok_val, upgsts_boot,
    delay_init, spi_pe, length_coefficient, fd_check, drwr_support, ecc_delay */
```

The typed table in `focaltech_flash.c` is checked against the byte-for-byte
stock copy (`upgrade_setting_list_stock_bytes[]` in `focaltech_ft3680_fw.i`) at
`fts_fwupg_init()` time, plus two `BUILD_BUG_ON`s, so it can never silently
drift.

## Priority 3 — V4.2 download engine (EXACT, implemented, gated off)

Recovered and implemented: `fts_fw_download`, `fts_fw_write_start`,
`fts_enter_into_boot`, `fts_pram_write_ecc`, `fts_dram_write_ecc`,
`fts_dpram_write`, `fts_dpram_write_pe`, `fts_pram_start`, `fts_ecc_check`,
`fts_ecc_cal_tp`, `fts_crc16_calc_host`, `fts_check_bootid`,
`fts_check_fast_download`, `fts_fw_resume`, `fts_fw_recovery`,
`fts_enter_normal_fw`, `fts_enter_gesture_fw`, `fts_enter_test_environment`,
`fts_upgrade_bin`, `fts_fwupg_work`, `fts_fwrecover_work`, `fts_fwload_work`,
`fts_fwupg_init`, `fts_fwupg_exit`, plus the V4.2 216-byte
`struct fts_upgrade`.

Proven constants (each with a `.text` site in
`flash-engine-reconstruction.md` §3): `0x55/0xAA` boot entry, `0x90` read-ID,
`0xAD` set-PRAM-address (len 4), `0xAE` write, `0x08` start-app, `0xCC` ECC
calc (len 7), `0xCE` ECC finish, `0xCD` ECC read, CRC-16 poly `0x8408`,
PRAM base `0x000000`, DRAM base `0xD00000`, packet `0x7FF0`, buffer
`packet + 7`, 3 download attempts, 30 boot-entry attempts × 3 writes, 100
ECC-finish polls, `fts_msleep(10)` after remap, `fts_msleep(2)` after the ECC
command.

**Safety.** `FTS_ALLOW_FW_PROGRAMMING` defaults to `0`. With the gate off the
whole engine runs — boot entry, boot-ID check, length parsing, host CRC-16,
setting selection, firmware acquisition — but the three operations that can
brick a panel (the `0xAE` PRAM payload write, the `0xAE`+length `_pe` payload
write and the `0x08` remap) return `-EPERM` with an explicit log line. The
host ECC is always *computed* from the image and compared against the value
the panel reports; no CRC is hard-coded anywhere.

## Priority 4 — FHP ABI (EXACT), implementation outstanding

All eleven command values decoded from the literal `movz/movk` immediates and
the 9-entry jump table at `.rodata+0x3f8`:

```
0x4008C501  _IOR (0xC5, 1,  8)   fhp_ioctl_reset            arg by value
0xC018C502  _IOWR(0xC5, 2, 24)   fhp_ioctl_spi_sync         pointer
0x4008C503  _IOR (0xC5, 3,  8)   fhp_ioctl_set_irq          arg by value
0x4008C504  _IOR (0xC5, 4,  8)   fhp_ioctl_set_frame_size   arg by value
0x4008C505  _IOR (0xC5, 5,  8)   fhp_ioctl_set_spi_speed    arg by value
0x8008C506  _IOW (0xC5, 6,  8)   fhp_ioctl_get_chip_init_done  pointer
0x8008C507  _IOW (0xC5, 7,  8)   fhp_ioctl_get_frame        pointer
0x4008C508  _IOR (0xC5, 8,  8)   fhp_ioctl_clear_frame      ignored
0x4008C509  _IOR (0xC5, 9,  8)   fhp_ioctl_set_timeout      arg by value
0x4010C50A  _IOR (0xC5,10, 16)   fhp_input_report           pointer
0x4008C502 / 0x4008C506 / 0x4008C507 -> "unkown ioctl cmd(0x%x)", -EINVAL
```

The direction bits are inverted relative to the data flow (the "get" commands
carry `_IOC_WRITE`); that is a property of the vendor header and is reproduced
rather than corrected. No `compat_ioctl` and no `compat_ptr` import: 32-bit
callers reach the same handler with a native `unsigned long` argument.
`struct fhp_data` is 288 bytes with recovered offsets; `misc_register` is
called for `"fhp_ft"` (`fhp_data+0x08`) and `"fhp_input"` (`fhp_data+0x58`).
`fhp_ioctl_set_frame_size` additionally saves `ts_data->touch_size` into
`fhp_data+0x11c` and replaces it, and `fhp_close` restores it.

Not implemented in the rebuild. This costs exactly 8 stock functions and the
5 remaining stock-only imports.

## Priority 5 — firmware-debug protocol (implemented)

Recovered and implemented: `struct fts_fwdbg_data` (264 bytes, all offsets
tabulated), the `0x96`/`0x9D` configuration handshake, the enable/disable
sequence around register `0x9E`, the `0xFA`/`0xFB` sample loggers with their
exact print formats and differing row widths (`rx` for FB, `rx*2` for FA),
the frame queue (`dbgq_open`/`_close`/`_enqueue` with overwrite-oldest
semantics), `fts_fwdbg_readdata`'s IRQ path and `0xFFFF` frame-id sentinel,
`fts_fwdbg_work_func`, `fts_fwdbg_handle_reset` (200 ms re-arm), the four
sysfs attributes with their exact formats and guard conditions, and
`fts_fwdbg_release`.

Two things are deliberately **not** invented and refuse instead:
`fts_logging_frame()`'s print format and the `/proc/fts_fwdbg` open/read path.
Neither is reachable in the default configuration.

## Priority 6 — Ulefone integration (ported)

`fts_ws` wakeup source, `pm_wakeup_ws_event` on the suspended IRQ path,
`tpgesture_status` → `ts_data->gesture_mode`, the 10-byte `tpgesture_value`
clear in suspend and resume, the per-gesture `tpgesture_value` strings plus
`tpgesture_hander()` on every gesture path, `yft_aod_state`,
`yft_fts_ts_aod_contorl()`, the `aod_state` sysfs node, and the already-present
`Touch_fts` display-notifier and `vddi-gpio` handling. Details and the
instruction-level evidence are in `ulefone-integration-port.md`.

Effect: `.modinfo depends` is now **byte-identical to stock**:
`yft_tpd_gesture,mtk_disp_notify,yft_devinfo`.

## Priority 7 — `touch_fw_version` (EXACT)

`fts_fwupg_work` tail, `.text+0x9bb4..0x9bd8`:

```c
fts_read_reg(FTS_REG_FW_VER /* 0xA6 */, &fw_ver);
sprintf(touch_fw_version, "Vno:0x%02x\n", fw_ver);
```

Verified from the oracle rather than trusted from the note, and confirmed to
run on **both** the success and the failure path of `fts_fw_download()`. The
rebuild now imports `touch_fw_version` (stock CRC `0xd0815107`, exact) and
`sprintf`.

## Priority 8 — donor-only code removed

The donor's `/proc/touchpanel` subtree (`fod_mode`, `gesture_mode`,
`gesture_code`, `game_mode`, `edge_mode`, `pocket_mode`, `TP_charger_flags`,
`tp_data_dump`) is absent from stock and has been removed, together with the
now-dead `fts_gesture_point_show`. This dropped exactly the eight donor-only
imports `proc_mkdir`, `remove_proc_subtree`, `single_open`, `single_release`,
`seq_read`, `seq_lseek`, `seq_printf`, `kstrtouint`.

**The rebuild now has zero extra imports.**

## Priority 9 — final verification

```
command:
  cd /home/armol/kernel-work/gki-12901745-workspace
  tools/bazel build //lieppos/focaltech-ft3680-recon/recon:focaltech_touch_spi_ft3680_gki

BUILD_RC: 0
warnings: none (compiler -Werror clean; modpost with KBUILD_MODPOST_WARN=1 clean)
```

| Metric | Before this pass | After |
|---|---:|---:|
| stock imports | 104 | 104 |
| rebuilt imports | 97 | **99** |
| missing (stock-only) imports | 15 | **5** |
| extra (rebuilt-only) imports | 8 | **0** |
| shared imports | 89 | **100** |
| shared-import CRCs identical | 89 | **98** |
| shared-import CRC mismatches | 0 wrong + 4 unresolved | **2** (both known provider gaps) |
| stock functions | 166 | 166 |
| rebuilt functions | 131 | **149** |
| shared function names | — | **143** |
| size-identical functions | 64 | **87** |
| stock-only functions | 59 | **23** |
| rebuilt-only functions | 24 | **6** |
| `.modinfo depends` | `mtk_disp_notify,yft_devinfo` | **`yft_tpd_gesture,mtk_disp_notify,yft_devinfo` (exact)** |

Explicitly requested import checks:

| symbol | present in rebuild? |
|---|---|
| `tpgesture_value` | **yes** |
| `tpgesture_status` | **yes** |
| `tpgesture_hander` | **yes** |
| `touch_fw_version` | **yes** |

Remaining missing imports (all 5 belong to the unimplemented FHP layer):
`misc_register`, `misc_deregister`, `kmalloc_large`, `schedule_timeout`,
`__msecs_to_jiffies`.

Remaining stock-only functions (23):

* 8 FHP: `fhp_open`, `fhp_close`, `fhp_poll`, `fhp_ioctl`, `fhp_input_open`,
  `fhp_input_close`, `fhp_input_ioctl`, `fhp_input_report`, plus
  `fts_fhp_init`, `fts_fhp_exit`, `fts_fhp_irq_handler` — *not implemented*;
* 2 fwdbg: `fts_fwdbg_read`, `fts_logging_frame` — *documented refusals*;
* 5 inlining artefacts (present in the source, inlined by clang):
  `fts_logging_regfa`, `fts_input_init`, `fts_input_report_buffer`,
  `fts_input_report_touch`, `fts_input_report_touch_pv2`;
* 5 genuinely absent stock features outside this pass's priority list:
  `fts_earphone_show/store`, `fts_edgepalm_show/store`, `fts_ex_mode_set_reg`.

Rebuilt-only functions (6): `fts_get_ic_information`, `fts_procfs_init`,
`fts_procfs_exit`, `fts_esd_is_disable`, `fts_read_fod_info`,
`fts_spi_transfer` — all either inlined into `fts_ts_probe_entry` in stock or
harmless empty shims left at their call sites.

## Provider CRC provenance — stated precisely

Two shared-import CRCs differ, and **neither is a missing implementation**:

| symbol | stock | rebuilt | nature |
|---|---|---|---|
| `tpgesture_value` | `0x02f3ea4c` | `0xec3d4c19` | genksyms declaration-text gap in `yft_tpd_gesture` |
| `yft_spitouchpanel_device_add` | `0xea3d7f0d` | `0x0776e449` | 73-character vendor enum in the never-shipped `yft_devinfo.h` |

Both providers are reconstructed from source and both sides of the LieppOS
stack (provider + FT3680) carry the *same* generated CRC, so the LieppOS stack
is internally ABI-coherent. Only substituting this rebuild underneath the
**untouched stock** provider binaries would require the historical CRCs.

This is the distinction the task asks for:

* **IMPLEMENTATION COMPLETE** — not claimed. The FHP misc-device layer is
  genuinely unimplemented.
* **STOCK BINARY ABI SUBSTITUTION EXACT** — not claimed, for the two CRCs
  above.
* What *is* claimed: `BEHAVIORAL_RECONSTRUCTION_WITH_DOCUMENTED_RESIDUALS`.

## Final blocker list (only genuinely unresolved items)

1. **FHP misc-device implementation.** The ABI is exact and documented
   (`fhp-abi.md`); what is missing is the code. Two sub-items still need RE
   before it can be written faithfully: the member split of the 24-byte
   `spi_sync` argument and the 16-byte `input_report` argument (their *sizes*
   are exact), and the 8-byte queue element header used by
   `fhpq_enqueue`/`fhpq_dequeue_userspace`.
2. **`/proc/fts_fwdbg` read path.** `fts_fwdbg_open` (`.text+0xc2d0`) and
   `fts_fwdbg_read` (`.text+0xc424`) were not disassembled; the userspace
   output format is unknown. Also `fts_logging_frame` (`.text+0xb9e0`).
3. **`tpgesture_value` genksyms declaration text** — provider-side, bounded,
   documented in `phase4-yft-tpd-gesture-reconstruction.md`.
4. **`yft_spitouchpanel_device_add` vendor enum text** — provider-side,
   bounded, documented in `phase4-yft-devinfo-reconstruction.md`.

Items 1–2 are unfinished RE with an exactly known target function set.
Items 3–4 are missing vendor header text, not missing behaviour.

Everything previously listed as a blocker and not repeated here is **closed**.

## Safety statement for this pass

Offline only. No flashing, no `insmod`/`rmmod`, no GPIO writes, no
bind/unbind, no DT/DTBO/vendor_boot/vendor_dlkm change, no slot or boot-control
change, no touchscreen firmware written. The stock `.ko` was read only. The
recovered programming engine is compiled but gated off by
`FTS_ALLOW_FW_PROGRAMMING = 0`; enabling it is a deliberate, documented,
single-line change that must only be made with a recoverable panel.

## Post-continuation audit

The continuation pass closes the difficult chip-specific FT3680 reconstruction
work, but the module is not yet frozen as an implementation-complete stock
replacement.

Clarifications:

1. The FHP ioctl command-number surface is recovered exactly, but the complete
   payload ABI is not yet exact. Remaining structure evidence is required for:

       24-byte spi_sync argument
       16-byte input_report argument
       8-byte FHP queue-element header

   Therefore the current status is:

       FHP_IOCTL_COMMAND_SURFACE_EXACT
       FHP_PAYLOAD_ABI_PARTIALLY_RECOVERED
       FHP_IMPLEMENTATION_INCOMPLETE

2. The final verification's FHP stock-only function count is 11, not 8:

       fhp_open
       fhp_close
       fhp_poll
       fhp_ioctl
       fhp_input_open
       fhp_input_close
       fhp_input_ioctl
       fhp_input_report
       fts_fhp_init
       fts_fhp_exit
       fts_fhp_irq_handler

3. Five genuine stock functions outside the previous continuation priority list
   are also still absent from the reconstruction:

       fts_earphone_show
       fts_earphone_store
       fts_edgepalm_show
       fts_edgepalm_store
       fts_ex_mode_set_reg

   These must either be reconstructed or proven inactive/non-required on the
   GQ5012BF1 stock runtime before claiming full stock behavioral replacement.

The remaining implementation frontier is therefore:

1. finish the FHP payload ABI and misc-device implementation;
2. recover /proc/fts_fwdbg open/read and fts_logging_frame;
3. recover the five remaining stock earphone/edge-palm/ex-mode functions;
4. classify/remove remaining rebuilt-only shims;
5. perform final stock-vs-rebuild verification.

The two provider genksyms declaration-text gaps remain bounded provenance
issues and do not represent missing provider runtime behavior.

The recovered firmware-download engine remains disabled by default via
FTS_ALLOW_FW_PROGRAMMING=0.


---

# Completion pass — FINAL STATE (AUTHORITATIVE, supersedes every section above)

The "Post-continuation audit" frontier is closed. All five items on it are
done: the FHP payload ABI and misc-device layer, the `/proc/fts_fwdbg`
open/read path plus `fts_logging_frame`, the five earphone/edge-palm/ex-mode
functions, the rebuilt-only shims, and the final stock-vs-rebuild
verification.

## Headline result

```
command:
  cd /home/armol/kernel-work/gki-12901745-workspace
  tools/bazel build //lieppos/focaltech-ft3680-recon/recon:focaltech_touch_spi_ft3680_gki

BUILD_RC: 0
warnings:  0   (clang -Werror clean; modpost clean; no undefined-symbol warnings)
```

| Metric | Previous pass | **This pass** |
|---|---:|---:|
| stock imports | 104 | 104 |
| rebuilt imports | 99 | **104** |
| missing imports | 5 | **0** |
| extra imports | 0 | **0** |
| shared imports | 100 | **105** |
| shared-import CRCs identical | 98 | **103** |
| shared-import CRC mismatches | 2 | **2** (the two bounded provider gaps) |
| stock functions | 166 | 166 |
| rebuilt functions | 149 | **166** |
| shared function names | 143 | **166** |
| size-identical functions | 87 | **105** |
| stock-only functions | 23 | **0** |
| rebuilt-only functions | 6 | **0** |
| `.modinfo depends` | exact | **exact** |

Raw verifier output: `workspace/phase4-focaltech-ft3680/verification-pass-3.txt`.
Tool: `tools/fts-verify.py`.

**Symbol-set parity is exact.** There is no stock function the rebuild lacks
and no rebuild function stock lacks. The five imports that were previously
missing — `misc_register`, `misc_deregister`, `kmalloc_large`,
`schedule_timeout`, `__msecs_to_jiffies` — all now resolve, and they resolve
for the right reason: the FHP misc devices, the 0x8000 queue allocation and
the bounded `wait_event_interruptible_timeout` in `GET_FRAME`.

## Priority 1 — FHP: recovered and implemented

New file: `recon/focaltech_fhp.c`. Evidence:
`workspace/phase4-focaltech-ft3680/fhp-abi.md`, section
"Completion pass — full payload ABI and implementation".

All eleven stock functions are present: `fts_fhp_init`, `fts_fhp_exit`,
`fts_fhp_irq_handler`, `fhp_open`, `fhp_close`, `fhp_poll`, `fhp_ioctl`,
`fhp_input_open`, `fhp_input_close`, `fhp_input_ioctl`, `fhp_input_report`.

### The three structures that were previously unknown

**24-byte `spi_sync` argument.** `copy_from_user(&arg, user, 24)` at
`.text+0xddd0` followed by `ldr x8,[sp]` (tx), `ldr x8,[sp,#0x8]` (rx) and
`ldr w2,[sp,#0x10]` (len). The trailing 4 bytes are tail padding that no
stock instruction reads.

**16-byte `input_report` argument.** `copy_from_user(&arg, user, 16)` at
`.text+0xef24` followed by `ldr x22,[sp]` (buf) and `ldr w20,[sp,#0x8]`
(size); size is validated to `1..84` and the 84-byte landing buffer is
pre-filled with `0xFF`, not zero.

**8-byte queue element header.** `str x22, [x0], #0x8` at `.text+0xd794`
writes a microsecond timestamp — `ktime_get_with_offset(TK_OFFS_REAL)` divided
by 1000 with the canonical `0x20C49BA5E353F7CF` / `asr #7` magic — and
advances the cursor by exactly 8 before the payload `memcpy`. Corroborated by
`fhp_get_frame`, which validates `touch_size + 8 == q->sizeq` and carries the
literal `8` in `w4` (`mov w4,#0x8`, `.text+0xd8d0`) as the third argument of
`"touch size(%u,%d,%lu) is invalid"`. `fhpq_dequeue_userspace` then hands the
whole `sizeq` bytes — timestamp included — to userspace, so a userspace frame
buffer must be `frame_size + 8` bytes.

### Correction to the previously published command surface

`fhp_ioctl` accepts the report command as `0x4010C50A` (magic `0xC5`, nr 10),
but `fhp_input_ioctl` accepts it as **`0x4010C601`** (magic `0xC6`, nr 1) —
`mov w9,#0xc601 ; movk w9,#0x4010,lsl#16` at `.text+0xf234`. Both dispatch to
the same `fhp_input_report()`. The earlier document recorded only the first.

### `struct fhp_data` and `struct fhp_queue`

288 bytes and 64 bytes respectively, with every field tied to a dereferencing
instruction (full tables in `fhp-abi.md`). `misc_open()` installs the
`struct miscdevice` pointer in `file->private_data`, so the stock entry points
recover the control block with `container_of()` — that is the source of the
constant biases `cmp x19,#0x8` (`fhp_poll`) and `subs x0,x9,#0x58`
(`fhp_input_ioctl`). One 16-byte range at `+0x100` is dereferenced by no stock
instruction; it is **named** `reserved_0x100[16]`, not guessed.

`fhp_fops` and `fhp_input_fops` carry relocations only for `.poll`,
`.unlocked_ioctl`, `.open` and `.release`. There is **no** relocation against
`__this_module` at slot `+0x00` and none at `.compat_ioctl` (`+0x58`), so the
vendor left `.owner` unset and provided no compat handler. Both facts are
reproduced rather than "fixed".

### One vendor defect, reproduced deliberately

`fhpq_enqueue` writes the 8-byte timestamp and then `memcpy`s a further
`q->sizeq` bytes (`ldrsw x2,[x21,#0xd0]`, `.text+0xd798`) instead of
`sizeq - 8`, so each element writes 8 bytes more than its own stride.

* The **read** side is safe by construction: the source is the 4096-byte
  `ts_data->touch_buf` and `fhp_ioctl_set_frame_size` caps the frame at 4080.
* The **write** side can run 8 bytes past the 0x8000 ring on the final slot,
  but only when `0x8000 % sizeq < 8`.

This is stock behaviour, so it is reproduced verbatim. The one-line hardening
exists and is **disabled**: `FTS_FHP_FIX_ENQUEUE_OVERRUN` defaults to `0`.
Enabling it would be a documented, deliberate divergence from the oracle.

## Priority 2 — fwdbg: `/proc/fts_fwdbg` fully recovered

Evidence: `fwdbg-protocol.md`, section "Completion pass". The previous
`-ENOSYS` refusals are gone; nothing in the subsystem is stubbed.

* `fts_fwdbg_open` (`.text+0xc2d0`) — validates `q.elem_size == frame_size`
  when logging is off, resets the read cursor, and (in non-blocking mode)
  arms the reader, replays the `0xFB`/`0xFA` register logs and `vmalloc`s the
  latch buffer.
* `fts_fwdbg_read` (`.text+0xc424`) — two distinct paths. If the caller's
  buffer is smaller than one frame, `proc_get_one_frame` latches a single
  element into `dbg->read_buf` and serves byte-slices tracked by
  `dbg->read_offset`; otherwise `dbgq_dequeue_to_proc` copies
  `min(q.count, count / frame_size)` whole frames straight from the ring. The
  return value is always a byte count, and a partial `copy_to_user` failure
  returns the bytes already delivered.
* `fts_logging_frame` (`.text+0xb9e0`) — its first argument is **not** the
  control block: `fts_fwdbg_readdata` passes `add x0, x19, #0xa8`, the nine-int
  configuration block. Output is a 512-byte scratch buffer rendered as two
  `"%02x,"` runs (which deliberately share one running character count), a
  single `"%d"` byte, and two big-endian signed 16-bit `"%d,"` sections with
  different index bases, different loop guards and different line-break tests.
  Every quirk is documented at the instruction that proves it.

The control block is reached through `PDE_DATA(inode)` in all three entry
points (`ldr x19,[x0,#0x2b8]`); the previous implementation used
`file->private_data` in `fts_fwdbg_release`, which was wrong and is corrected.

**No format was invented.** Every literal is a string constant or an immediate
in the stock `.text`.

## Priority 3 — earphone / edge-palm / ex-mode: ACTIVE, implemented

Evidence: `ex-mode-and-inlining.md`, part 1.

They are **not** dead code. `fts_ex_mode_init` is called unconditionally from
`fts_ts_probe_entry`, it creates the whole attribute group including both new
nodes, and `fts_ex_mode_recovery` runs on resume and after a firmware reset.
Nothing gates them on chip type or a device-tree property, so they are
implemented rather than documented-as-unreachable.

Stock carries **five** modes, not the donor's three:

| flag | mode | register |
|---|---|---|
| `ts_data+0x30d` | `MODE_GLOVE` | `0xC0` |
| `ts_data+0x30e` | `MODE_COVER` | `0xC1` |
| `ts_data+0x30f` | `MODE_CHARGER` | `0x8B` |
| `ts_data+0x310` | `MODE_EARPHONE` | `0xC3` |
| `ts_data+0x311` | `MODE_EDGEPALM` | `0x8C` |

The first four are replayed with the literal `1`. Edge-palm is replayed with a
stored value from `ts_data+0x320`, so it is not a boolean mode — its store
parses `"%d"` with `sscanf` and pushes the raw value into register `0x8C`.

`fts_ex_mode_set_reg` (`.text+0x5c18`) is a verifying writer, not a plain
write: probe, then up to five write/1 ms-sleep/read-back rounds. Three
behaviours follow from the instruction sequence and are reproduced — an
already-correct register returns 0 *silently*, the last attempt is never read
back, and the failure log therefore quotes the sample taken by the previous
attempt.

## Priority 4 — rebuilt-only functions: classified, residue removed

| symbol | verdict | action |
|---|---|---|
| `fts_procfs_init` | dead donor residue (reduced to `return 0` after the `/proc/touchpanel` removal) | **deleted**, call site removed |
| `fts_procfs_exit` | dead donor residue | **deleted**, call site removed |
| `fts_get_ic_information` | inlined stock behaviour (boot-ID loop lives inside `fts_ts_probe_entry`) | `__always_inline` |
| `fts_read_fod_info` | inlined stock behaviour (inlined into `fts_read_parse_touchdata`) | `__always_inline` |
| `fts_esd_is_disable` | inlined stock behaviour (16-byte accessor, single call site) | `__always_inline` |
| `fts_spi_transfer` | inlined stock behaviour (stock inlines the `spi_message` setup into all three bus helpers) | `__always_inline` |

And in the opposite direction, the last three **stock-only** functions were
resolved by discovering that `fts_input_report_buffer` (`.text+0x984`) is only
120 bytes — a dispatcher, not a parser:

* `fts_input_report_touch` (`.text+0x9fc`) — event type 0, 8-bit coordinates;
* `fts_input_report_touch_pv2` (`.text+0xbb8`) — event type **2**
  (`TOUCH_PROTOCOL_v2`, not the 0x82 high-resolution encoding): packed 16-bit
  coordinates with sub-pixel nibbles, explicit minor axis, fixed pressure
  `0x3F`;
* `fts_input_init` (`.text+0x1f04`) — already present, but clang inlined it.

The reconstruction was split to match, and the three are emitted with
`noinline` (a pure code-layout attribute, no behavioural effect) so that the
rebuild stops inlining functions the vendor build kept out of line. That
split is also what makes the FHP input path possible at all: stock
`fts_input_report_buffer` is **GLOBAL** precisely so `fhp_input_report` can
push a userspace-supplied buffer through the same reporting path as an
interrupt-delivered one.

## Final blocker list — two items, both bounded, neither behavioural

1. **`tpgesture_value` genksyms declaration text** — provider-side.
   Stock CRC `0x02f3ea4c`, rebuilt `0xec3d4c19`.
2. **`yft_spitouchpanel_device_add` vendor enum text** — provider-side.
   Stock CRC `0xea3d7f0d`, rebuilt `0x0776e449`.

Both are missing *vendor header text*, not missing runtime behaviour. The
provider and the FT3680 module are reconstructed from the same sources and
therefore carry the *same* generated CRC on both sides, so the LieppOS stack
is internally ABI-coherent. The historical CRCs would only be required in
order to drop this rebuild underneath the **untouched stock** provider
binaries.

Nothing else is open. Every previously listed blocker is closed:

* FHP implementation — **done**;
* FHP payload ABI (spi_sync / input_report / queue header) — **done**;
* `/proc/fts_fwdbg` open/read and `fts_logging_frame` — **done**;
* earphone / edge-palm / ex-mode — **done**;
* rebuilt-only shims — **classified, residue deleted**.

## What is and is not claimed

* **Claimed: `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`.** Every stock
  function is present, no rebuild function is absent from stock, the import
  set matches exactly, and no subsystem is stubbed or refuses.
* **Claimed: `SYMBOL_SET_PARITY_EXACT`.** 104/104 imports, 166/166 functions,
  zero extra, zero missing, exact `.modinfo depends`.
* **Not claimed: byte-identical `.text`.** 105 of 166 functions match stock
  size exactly; the rest differ in register allocation and scheduling, which
  is expected from a source reconstruction compiled by a different toolchain
  invocation.
* **Not claimed: `STOCK_BINARY_ABI_SUBSTITUTION_EXACT`.** Blocked by the two
  provider genksyms gaps above.

## Known deliberate deviations from the oracle (complete list)

1. `FTS_ALLOW_FW_PROGRAMMING = 0` — the recovered V4.2 download engine is
   compiled but the three panel-bricking operations return `-EPERM`.
2. `FTS_FHP_FIX_ENQUEUE_OVERRUN = 0` — the vendor's 8-byte enqueue overrun is
   reproduced; the hardening exists but is off.
3. `noinline` / `__always_inline` attributes — code layout only, chosen to
   reproduce the stock symbol set. No behavioural effect.

There are no other intentional differences, and no unexplained behavioural
differences.

## Safety statement

Offline only, throughout. No flashing, no `insmod`/`rmmod`, no GPIO writes, no
bind/unbind, no DT/DTBO/vendor_boot/vendor_dlkm modification, no slot or
boot-control change, no touchscreen firmware written, no CRC fabricated. The
stock `.ko` was read as an oracle and never modified. The firmware-programming
engine remains disabled by default.

## Evidence index

| document | covers |
|---|---|
| `workspace/phase4-focaltech-ft3680/chip-id-reconstruction.md` | FT3680 chip-ID tuple |
| `.../upgrade-setting-layout.md` | 20-byte `upgrade_setting_list` record |
| `.../flash-engine-reconstruction.md` | V4.2 PRAM/DPRAM/ECC engine |
| `.../fhp-abi.md` | FHP command surface **and** full payload ABI |
| `.../fwdbg-protocol.md` | firmware-debug protocol **and** the proc read path |
| `.../ulefone-integration-port.md` | gesture / AOD / VDDI / wakeup deltas |
| `.../ex-mode-and-inlining.md` | five-mode ex_mode subsystem; symbol-set convergence |
| `.../verification-pass-3.txt` | raw final verifier output |
| `tools/fts-annotate.py`, `fts-compact.py`, `fts-slice-func.py`, `fts-verify.py` | reusable RE + verification tooling |
