# DRAFT: TrustKernel normal-world driver source request (NOT SENT — requires user approval)

To: TrustKernel (Shanghai Pingbo Information Technology), or Ulefone forwarding it. The driver is a GPL Linux
kernel component shipped by Ulefone.

**Subject:** Source of TrustKernel TKCore normal-world Linux driver 6:1.1-k6.6 (tkcore.ko, tkcore_drv.ko) as
shipped on Ulefone GQ5012BF1

## Identification

| Module | modinfo | sha256 (as shipped, vendor_boot) |
|---|---|---|
| `tkcore.ko` | `license=GPL`, `author=TrustKernel`, `description=TrustKernel TKCore TEEC v1.0`, `version=6:1.1-k6.6` | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` |
| `tkcore_drv.ko` | `license=GPL`, `author=TrustKernel`, `description=TrustKernel TKCore TZ driver`, `version=1.0` | `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d` |

Kernel `6.1.115-android14-11-g945dff7bc1bf`, MediaTek MT6878T, firmware `GQ5012BF1_EEA_V15`.

## Requested

`drivers/tee/tkcore/` (`core/`, `armtz/`, `include/`, Kconfig, Makefile, `tkcore_version.h`) exactly at version
**6:1.1-k6.6**, plus the Kconfig values used (`TRUSTKERNEL_TEE_SUPPORT=m`, `RPMB_SUPPORT=y`, `FP_SUPPORT=y` as
observed). Only the GPL normal-world Linux driver is requested. Trusted OS, TAs, keys and firmware are not.

## Public releases already compared (insufficient)

| Release | Location | Why insufficient |
|---|---|---|
| 3.2p3 | ZTE public kernel | struct layout differs (`tee` 0x158, `tee_context` 0xc8 vs stock 0x138/0xd0) |
| 3.2p8.4.14p2 | Vivo Y21s / V23 5G kernels | same old struct blocks |
| 4.0p0.4.19p0 | anvil-kernel branch 4.19 `492dbcf3` | `struct tee` has `miscdev`, not `udevs`; `tee_ops` 104 B vs stock 88 B; `tee_cmd` 0xe8 vs 0x100 |
| 7:2.2 | anvil-kernel `8e1a0f39478f` | the closest: declarations reproduce stock export CRCs once `shm_name` is removed from `struct tee_shm` |

## What is still missing

The implementation differs in 19 of 122 `tkcore.ko` functions, all absent from 7:2.2:

- **Platform:** `plat_cpu_is_big`, `plat_tee_init`, and the stock-only `large_cluster_id`.
- **Procfs logger:** `logd`, `tee_init_procfs`, `tee_version_read`, …
- **Shared-memory allocator:** `tkcore_alloc_shm` (408 B in 6:1.1 vs 104 B), with none of 7:2.2's user-page
  pinning.
- **Others:** `tee_internal_ioctl` and `tee_supp_write`.

Also missing is the armtz `tee_tz_drv.c` as shipped in `tkcore_drv.ko`.

## Licence evidence

Both modules declare `license=GPL`. The public TrustKernel files carry GPL-2.0 headers ("Copyright (c) 2015-2018
TrustKernel Incorporated … GNU General Public License version 2").
