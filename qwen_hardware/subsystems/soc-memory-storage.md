> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Memory and storage are one **Micron uMCP `MT512GBCAV8U31`** (512 GB UFS + 16 GiB DRAM), with UFS health PreEOL Normal / 0-10 % life used. See `dram.md` and `ufs.md`.

# Memory and storage

## Hardware found

* Product configuration: **512 GB ROM** and 12/16 GB physical RAM claims, with up to 50 GB extended/virtual RAM (OEM spec). Exact DRAM and UFS package markings were not captured.
* MT6878/Dimensity 7400 platform capability: LPDDR5-3200, 4×16-bit interface / 25.6 Gb/s class, UFS 3.1; these are SoC ceilings, not a proof of the fitted speed grade.
* Android snapshot exposes the normal vendor/boot/system/product partitions and camera high/low-RAM buffer policies. No removable storage slot was proven in the captured software inventory.

## Board configuration / stock usage

* Stock build is Android 15 and uses vendor partitioned UFS storage. Exact UFS device ID, health/lifetime counters, negotiated gear, capacity after overprovisioning and filesystem layout should be read from `/sys/class/block`, `/sys/devices/platform/.../ufshcd*` and `lshal` on a rooted system.
* Camera properties have separate `high_ram` and `low_ram` pipeline buffer minima, showing RAM-tier policy is active.
* Extended RAM is software-backed/zram or reserved storage, not extra physical DRAM; amount and policy depend on SKU/build.

## Capability gap

The physical package vendor, UFS gear (2.1/3.1), DRAM die/channels and actual 12-vs-16-GB SKU are UNKNOWN. Do not infer LPDDR5/UFS 3.1 from the marketing name alone.

## Hidden / unused

* SoC LPDDR5/UFS 3.1 headroom may be unused if the BOM uses a lower speed grade.
* Storage-backed extended RAM trades latency and flash wear for capacity.

## Verification

Read UFS descriptor/device health and DRAM memory map as root; capture `MemTotal`, `/proc/partitions`, UFS gear/lane mode and package IDs; compare with the exact retail SKU label.

Sources: S04, S06/S07; live snapshot identity/properties; `hardware/MASTER-HARDWARE-INVENTORY.md` memory section.
