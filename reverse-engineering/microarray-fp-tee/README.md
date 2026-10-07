# MICROARRAY-FP-TEE — closure (2026-10-07, static)

Workspace component: `Reverse Engineer - PARTIAL/MICROARRAY-FP-TEE` → **DONE**.

## Selection log

SELECTED TARGET: `MICROARRAY-FP-TEE`. VERIFIED: present in `Reverse Engineer - PARTIAL/`,
and `REVERSE-ENGINEERING-STATUS.md` lists it as PARTIAL.

WHY: a single leaf module (27 functions). The 2026-10-07 TKCORE-DRV closure had
just pinned the public TrustKernel donor, and its notes say that donor's `core/`
reproduces the stock `tee_spi_transfer` CRC. That was the one recorded blocker.

CURRENT BLOCKERS (as recorded): (1) "one tkcore runtime-provider witness"
(`tee_spi_transfer` CRC taken from the stock `tkcore.ko`); (2) "device
validation". Implicit: "EMPTY-SOURCE RED / NO_USEFUL_SOURCE"; the old
clean-room rebuild was only behavioural (69 688 B vs stock 69 296 B; 14/27
functions byte-identical when re-measured today).

## Scope

The stock `microarray_fp_tee.ko`: the MicroArray SPI fingerprint driver in
vendor_ramdisk first stage. It covers the DT binding, the provider edges to
`fingerprint.ko` / `spi-mt65xx.ko` / `tkcore.ko`, probe-time chip
identification through the TrustKernel SPI proxy, the `/dev/madev0`
char-device ABI (read/write/ioctl/mmap), IRQ/input/sysfs, and its
userspace/SELinux consumers.

Outside scope:
* The secure world: TrustKernel SPI proxy TA `966d3f7c-…` and MicroArray TA
  `edcf9395-…`, i.e. what `smt_conf` and the opcodes mean inside the TEE.
* `tkcore.ko` itself (`TRUSTKERNEL-TEE`, BLOCKED).
* `fingerprint.ko` glue and the SPI controller (their own components).

## Result

| item | result |
|---|---|
| lineage | **DIRECT FAMILY DONOR + ODM DELTA, BYTE-IDENTICAL**. MicroArray driver **v4.0.06** (`MA_DRV_VERSION 0x4006`), two TUs `mtk-settings.c` + `madev.c`. Public donor: HelloVolla `UT-kernel-volla-mt6768` 981578e37858 `drivers/input/fingerprint/microarray_fp/` (`donor/`, sha256 in `donor/donor-files.sha256`). ODM delta reconstructed in `source/`. |
| B1 == B2 | `.ko`, stripped `.ko`, `mtk-settings.o`, `madev.o` byte-identical (`parity/b1-b2-build.txt`) |
| stock (`8e1449ce…`, 69 296 B) vs rebuild (stripped) | same size; **20 differing bytes, all `.note.gnu.build-id`** (`parity/mafp-parity.txt`) |
| functions | 27/27 identical (bytes, symbolic relocations, KCFI type ids) |
| data | 47/47 objects identical (incl. 80-byte `init_connect.smt_conf`, `sfops`, `sdrv`, OF table) |
| ABI | `__versions` 66/66 (order + CRC), `.modinfo` identical incl. `vermagic=6.1.115-android14-11-g945dff7bc1bf …`, `depends=fingerprint,spi-mt65xx,tkcore`, aliases; no srcversion on either side; 0 exports |
| layout | 42 section headers identical, ordered symtab 519/519, `.rodata.str1.1`/`.rodata` identical |
| providers | **all natural**: `fingerprint` and `spi-mt65xx` from their source builds; `tkcore` from the **pristine public TrustKernel `core/`** (anvil-kernel 8e1a0f39478f, tree 6b94428f, config TEE=m RPMB=y FP=y). Its `tee_spi_transfer` CRC `0x184ce7da` equals both the stock `tkcore.ko` `__kcrctab` and the stock microarray import (`evidence/tkcore-provider-crc.txt`; 11/25 stock tkcore exports reproduced, incl. all 4 FP/SPI exports). No stock witness is used. |

## ODM delta vs donor v4.0.06 (what `source/` changes)

* **Power/GPIO:** the donor pinctrl/`vfp_regulator_ctl` path is replaced by
  `regulator_get(dev,"vfp")` (2.8 V) plus the YFT glue
  `yft_finger_set_reset/spi_mode/irq(1)`. `mas_switch_power` toggles the
  regulator. Log text still says "mt6377_ldo" (stale ODM label).
* **Platform/SPI:** no platform driver or board info. One `spi_driver` (`madev`,
  OF `mediatek,madev_finger`). `mas_select_transfer`/`ma_spi_change` are empty.
  `max_speed_hz` is 6 MHz. `spi_setup` is called directly.
* **Chip ID:** v4.0.06 `TEE_ID_COMPATIBLE_TRUSTKERNEL` path, extended to three
  sequences (`8C FF FF FF` reset; `00 FF FF FF` → `0x41/0x45`; `70…`,
  `90 08…` → `0x20/0x1A`; `90 0B…` → `0x4A`) through `tee_spi_transfer(&smt_conf, 80, …)`.
  `smt_conf` is the **legacy MediaTek `struct mt_chip_conf`** (20×u32):
  * setup/hold/high/low/cs_idle = 10. The donor comment maps `high_time 10`
    to 6 MHz, which matches `max_speed_hz`.
  * MSB first both ways.
  * FIFO mode, finish interrupt enabled.
  * `chip_id` is exposed in sysfs `chip_id`. The probe ignores the result.
* **Removed:** the fb notifier (`init_notifier_call` only sets
  `is_screen_on = 1`), the clock ioctls (`0x4d04/05` are no-ops, so
  `mas_enable/disable_spi_clock` are dead), double-tap/long-tap/nav keys and
  the INT-status ioctl.
* **Changed:** one key code (249) plus KEY_POWER. Read/write are clamped to
  48 KiB (`kmalloc`), and the write path zero-fills instead of 0xFF. The mmap
  buffer is 68 KiB. `WAIT_SCREEN_STATUS_CHANGE` returns `is_screen_on`
  without waiting. `SYNC` (`0x4d2d`) = power off → 5 ms → power on.
  `MA_DRV_VERSION` is a `.data` object.
* **Kept from the donor:**
  * freezable waits (`TASK_FREEZABLE`) and plain `wake_up`;
  * the `MAFP_ … debug/warning/error log!` macro family (commented-out in the donor);
  * the ioctl numbering, `mas_compat_ioctl`, the `init_*`/`deinit_*` structure,
    `mas_set_input`, `mas_work`/`mas_interrupt`.

## Interface (stock, GQ5012BF1)

* DT: `spi1@11011000` (`mediatek,mt6989-spi`, **`tee-only`**, cs GPIO61) →
  `fingerprint@0` `mediatek,madev_finger`, `spi-max-frequency` 8 MHz (driver
  uses 6 MHz), `vfp-supply` → `mt6369_vfp`. IRQ from node `yft_finger`:
  EINT3 rising, `int-gpio` GPIO3, `reset-gpio` GPIO30, 16 pinctrl states
  owned by `fingerprint.ko`.
* Char device `/dev/madev0` (class `madev`, dynamic major; 498 in capture).
  Runtime `read`/`write` go through normal-world `spi_sync` (TEE only at probe).
  ioctl set as in `source/ioctl_cmd.h` (23 accepted commands).
* Load: first-stage `modules.load` after `tkcore`, `fingerprint`, `spi-mt65xx`.
* Userspace: `init.fingerprint.rc` sets `/dev/madev0` to 0666 system
  (later 777). SELinux type `mafinger_device`: `hal_fingerprint_default`
  gets `ioctl read write map open`, `factory` gets `ioctl read write open`.
  Consumers are `microarray.fingerprint.default.so` and `libfprint-x64.so`.

## GQ5012BF1 behaviour

**ACTIVE.** `spi1.0` is bound to driver `madev` (module `microarray_fp_tee`),
and `/dev/madev0` exists (`evidence/integration-checks.txt`, 14/14 PASS). Which
of the three ID sequences matched is runtime-only; the probe succeeds either
way.

## Stock defects (reproduced byte-for-byte; LieppOS decision)

1. **Unbounded `mmap`.** `mas_mmap` remaps `vm_end - vm_start` bytes starting
   at a 68 KiB `kmalloc` buffer. There is no size check, so a mapping larger
   than 68 KiB exposes adjacent physical memory to userspace, uncached and
   writable. Containment in stock is only SELinux `map` (fingerprint HAL
   only). Hardening: reject `size > 0x11000`.
2. The probe ignores `init_connect()`, `init_file_node` failures leave a
   half-registered device, and `mas_remove` leaks class/device/chrdev/input.
3. Global `ret` is shared between unrelated paths (log values are
   unreliable).

## Boundaries (external)

* Secure world: SPI proxy TA and MicroArray TA semantics, opcode meaning.
* `tkcore.ko` (`TRUSTKERNEL-TEE`, BLOCKED). Only its four FP/SPI export CRCs
  are used here, and they reproduce from public source.
* Device validation (enrol/match) is runtime-only and does not affect the
  module contract.

## LieppOS contract

Build with `scripts/build_b1_b2.sh`. It needs no stock symvers and produces a
drop-in replacement for stock (build-id aside). Keep the providers
`fingerprint`, `spi-mt65xx` and `tkcore` (stock or the public TrustKernel
`core/`), the DT nodes `spi1/fingerprint@0` + `yft_finger`, and the SELinux
`mafinger_device` rules. Consider defect 1 for any build that does not need
byte parity.

## Files

* `source/`: the reconstruction (`madev.c`, `mtk-settings.c`, `madev.h`,
  `mtk-settings.h`, `ioctl_cmd.h`, `Makefile`).
* `donor/`: public v4.0.06 files with hashes.
* `scripts/`: `build_b1_b2.sh`, `build_tkcore_core_natural.sh`,
  `mafp_parity.py`, `mafp_integration.py`, `elfmini.py`, `fdis.py`.
* `parity/`: `b1-b2-build.txt`, `mafp-parity.{txt,tsv}`.
* `evidence/`: `tkcore-provider-crc.txt`, `tkcore-core-donor-files.sha256`,
  `integration-checks.txt`.
* `stale-claims.md`.
