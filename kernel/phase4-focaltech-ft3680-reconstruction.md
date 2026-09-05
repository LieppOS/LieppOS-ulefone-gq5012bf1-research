# Phase 4 — FocalTech FT3680 touchscreen reconstruction (authoritative report)

This report supersedes every earlier intermediate hypothesis about
`focaltech_touch_spi_ft3680.ko`, including the initial
`NEEDS_ULEFONE_PORT` classification in `phase4-focaltech-ft3680.md`.

**Final classification**

    BLOCKED_WITH_EXACT_MISSING_EVIDENCE

The reconstruction is source-backed, builds against exact GKI 12901745, and
reproduces the stock module identity, device contract and firmware data
exactly. It is *not* complete: three stock subsystems and one vendor provider
remain blocked on precisely identified missing evidence, listed in
"Exact missing evidence" below. No fake CRC, no invented firmware sequence and
no phone/partition modification was involved at any point.

---

## Build

```
command:
  cd /home/armol/kernel-work/gki-12901745-workspace
  tools/bazel build //lieppos/focaltech-ft3680-recon/recon:focaltech_touch_spi_ft3680_gki

BUILD_RC: 0

warnings:
  compiler: none (builds -Werror clean)
  modpost (KBUILD_MODPOST_WARN=1) — unresolved vendor providers only:
    mtk_disp_notifier_register, mtk_disp_notifier_unregister,
    yft_spitouchpanel_device_add, yft_set_touch_device_used
```

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
                            4 unresolved provider symbols (recorded as MISSING,
                            never fabricated):
                              mtk_disp_notifier_register    stock 0x4c353ac0
                              mtk_disp_notifier_unregister  stock 0xa11ab00a
                              yft_spitouchpanel_device_add  stock 0xea3d7f0d
                              yft_set_touch_device_used     stock 0x0a0f3b69
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

1. **`yft_devinfo` provider source.** `yft_spitouchpanel_device_add` and
   `yft_set_touch_device_used` (and `touch_fw_version`) are exported only by the
   stock `yft_devinfo.ko`. Their stock CRCs are known
   (`0xea3d7f0d`, `0x0a0f3b69`, `0xd0815107`) but no source exists locally or
   publicly, so the rebuilt module cannot record them without fabricating CRCs.
   *Needed:* `yft_devinfo` source, or a LieppOS reimplementation of that module.
2. **`yft_tpd_gesture` provider source**, for `tpgesture_value`,
   `tpgesture_status`, `tpgesture_hander` (stock CRCs `0x02f3ea4c`,
   `0x30ac810a`, `0x8386526d`). Same situation.
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
- `mtk_disp_notify` CRCs are unresolved only because `KBUILD_EXTRA_SYMBOLS`
  wiring in the kleaf target is incomplete; the in-tree `mtk_disp_notify` build
  already emits exactly the stock `0x4c353ac0` / `0xa11ab00a`.
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

The authoritative blocker count is **six exact missing-evidence items**, as
listed in the "Exact missing evidence" section.

They comprise:

1. `yft_devinfo` provider source/reimplementation;
2. `yft_tpd_gesture` provider source/reimplementation;
3. FT3680 chip-ID tuple;
4. 20-byte upgrade-setting record semantics / V4.2 flash engine;
5. FHP misc-device ioctl ABI;
6. firmware-debug protocol.

Earlier summary wording describing these as "three stock subsystems and one
vendor provider" is imprecise and is superseded by this six-item list.
