# `gz_tz_system.ko` — source search and candidate classification

**Result: `EXACT_SOURCE` (with one proven revision delta — see §5)**

## 1. Search order

The pinned MediaTek/Nothing MT6878 `device_modules` revision was searched
first, exactly as instructed:

```
NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878
@ 957dac185efe46cbf6336b0fff9516d84c8cd78f
  drivers/misc/mediatek/geniezone/
```

This is the same pinned revision that already produced the closed `ffa_v10.ko`
and `tmem_ffa.ko`.

## 2. The exact build target (proven, not assumed)

`drivers/misc/mediatek/geniezone/Makefile` at that revision contains four
`obj-$(...)` rules. Only one produces a module named `gz_tz_system`:

```make
obj-$(CONFIG_MTK_GZ_MAIN)          += gz_main_mod.o     # NOT this module
gz_main_mod-objs += gz_main.o mtee_ut/gz_ut.o mtee_ut/gz_chmem_ut.o \
                    mtee_ut/gz_shmem_ut.o mtee_ut/gz_vreg_ut.o gz_ffa.o

obj-$(CONFIG_MTK_GZ_TZ_SYSTEM)     += gz_tz_system.o    # <-- THIS MODULE
gz_tz_system-objs += tz_system.o mtee-kree/tz_mmap.o mtee-kree/kree_mem.o

obj-$(CONFIG_MTK_ENABLE_GENIEZONE) += gz-trusty/        # providers, not this
```

So the module is built from **exactly three** translation units. The first
obvious directory entry (`gz_main.c`, the largest file) belongs to a
*different* module — this was checked rather than assumed, as required.

Kconfig symbol, verbatim from `geniezone/Kconfig`:

```
config MTK_GZ_TZ_SYSTEM
	tristate "GenieZone tz_system support"
	help
	  GenieZone TZ_SYSTEM driver
	  supports some APIs for IPC, and
	  session-related functions.
	  This module must be enabled.
```

`tristate` + stock shipping as a `.ko` ⇒ `CONFIG_MTK_GZ_TZ_SYSTEM=m`.

## 3. Identifier coverage against the stock ELF

Every stock identifier recovered in Phase 2 was searched in the three source
files:

| check | result |
|---|---|
| 61 stock functions found in source | **59/61**, the 2 absent being `init_module` / `cleanup_module`, which are the compiler-generated aliases of `module_init`/`module_exit` — i.e. **61/61 accounted** |
| 27 stock exports found in source | **27/27** |
| `MODULE_LICENSE` | `MODULE_LICENSE("GPL v2")` — matches stock `license=GPL v2` |
| `MODULE_DESCRIPTION` | **absent in source** — matches stock (no description field) |
| `MODULE_AUTHOR` | **absent in source** — matches stock (no author field) |
| `MODULE_DEVICE_TABLE(of, tz_system_of_match)` | matches both stock `alias=of:N*T*Cmediatek,trusty-tz*` entries |
| `.compatible = "mediatek,trusty-tz"` | matches stock alias string exactly |
| service-name strings | `com.mediatek.geniezone.srv.sys`, `nebula.com.mediatek.geniezone.srv.sys` present in both |

The absence of `MODULE_DESCRIPTION`/`MODULE_AUTHOR` in *both* the stock
`.modinfo` and the candidate source is a strong positive identity signal: a
wrong-tree candidate would almost certainly carry one.

## 4. External header set (same revision)

`tz_system.c` / `kree_mem.c` / `tz_mmap.c` include, via the vendor Makefile
`-I` paths:

| header | origin at the same pinned revision |
|---|---|
| `kree/mem.h`, `kree/system.h`, `kree/tz_mod.h`, `kree/sdsp_m4u_mva.h` | `geniezone/public/kree/` |
| `tz_cross/trustzone.h`, `ta_system.h`, `ta_mem.h`, `ta_fbc.h`, `ta_test.h`, `gz_version.h` | `geniezone/public/tz_cross/` |
| `gz-trusty/trusty.h`, `trusty_ipc.h`, `smcall.h`, `sm_err.h`, … | `geniezone/public/gz-trusty/` |
| `tee_client_api.h` | `drivers/tee/teei/510/common/include/` (pulled in only when `CONFIG_TEE`) |
| `include/unittest.h` | `geniezone/include/` |

All are byte-identical copies from the pinned revision. `kree/`, `tz_cross/`
and `gz-trusty/` are the *same files* already vetted during the `tmem_ffa`
closure.

One include is referenced but does **not** exist at the pinned revision:
`tz_cross/tz_error_strings.h`. It sits behind `#if debugFg` with
`#define debugFg 0`, so it is never reached — and correspondingly the stock
module does **not** export `TZ_GetErrorString`, which that block would have
exported. This is a positive config confirmation, not a gap.

## 5. Candidate classification

| candidate | classification |
|---|---|
| `device_modules@957dac18 : drivers/misc/mediatek/geniezone/` (`tz_system.c`, `mtee-kree/tz_mmap.c`, `mtee-kree/kree_mem.c`) | **`EXACT_SOURCE`** for `tz_mmap.c` and `kree_mem.c`; **`EXACT_SOURCE_DIFFERENT_REVISION`** for the 45-line `CONFIG_TEE` weak-stub block in `tz_system.c` |

Everything outside that one block is byte-exact: RED-B (§RED report) rebuilt
54/56 shared functions byte-identically and regenerated **27/27 export CRCs
naturally** straight from the unmodified pinned source.

### The single revision delta

At the pinned revision the five `CONFIG_TEE` fallback stubs are named in
snake_case and typed against `struct teec_context` / `teec_session` /
`teec_uuid` / `teec_operation` — **types that are defined nowhere in that
tree**. The donor therefore does not compile at all with `CONFIG_TEE=y`
(RED-A: 9 × `-Wvisibility -Werror`). The stock module instead carries five
WEAK symbols under the GlobalPlatform CamelCase names. See the delta ledger
and RED report for the kCFI proof that pins their exact prototypes.

## 6. Search termination

Per instruction, once exact local lineage was proven the search stopped. One
confirmatory public check was made to establish that the CamelCase weak-stub
revision is not published in any reachable MediaTek tree (all public copies
carry the same snake_case block as the pinned revision); no further broad web
searching was performed.

## 7. Not-used trees

| tree | why rejected |
|---|---|
| `MiCode-MTK-kernel-device-modules-chagall-2.0.31` (local) | no `geniezone/tz_system.c` |
| `MiCode-bsp-klee-w-oss`, `MiCode-dash-w-oss` (local) | no `geniezone/tz_system.c` |
| upstream Linux `drivers/virt/geniezone` (gzvm) | different driver entirely — the type-1 hypervisor driver, not the KREE client |
