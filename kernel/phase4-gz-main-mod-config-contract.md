# gz_main_mod — stock configuration contract

Every entry below is derived from the frozen stock ELF, never from a vendor
defconfig guess. The rule applied throughout: enable only what stock evidence
demands, and leave everything else off.

## 1. Proven ON

| CONFIG | state | stock evidence |
|---|---|---|
| `CONFIG_MTK_GZ_MAIN` | MODULE | stock is a loadable `gz_main_mod.ko` in `vendor_dlkm`; vendor Kconfig declares it `tristate`. Passed as `-DCONFIG_MTK_GZ_MAIN_MODULE=1`. |
| `CONFIG_MTK_ENABLE_GENIEZONE` | ON | `kree/mem.h` and `kree/system.h` gate their entire body on `CONFIG_MTK_IN_HOUSE_TEE_SUPPORT \|\| CONFIG_MTK_ENABLE_GENIEZONE`. Stock imports 15 `KREE_*`/`tz_system_dev` symbols with the exact stock CRCs, which is only possible when the real prototypes are visible. |
| `CONFIG_MTK_GZ_KREE` | ON | GenieZone KREE user-space API module; consistent with the whole KREE surface and with the sibling `gz_tz_system` contract. |
| `CONFIG_MTK_PROT_MEM_SUPPORT` | ON | `gz_chmem_ut.c` compiles `gz_test_chm_main(SSMR_FEAT_PROT_REGION, MTEE_MCHUNKS_PROT)` only under this config; the `#else` branch would emit the literal string `CONFIG_MTK_PROT_MEM_SUPPORT disabled`. Stock **contains a call to `gz_test_chm_main`** and **does not contain that string**. |
| `CONFIG_ARM_FFA_TRANSPORT` | reachable | `gz_ffa.c` includes `<linux/arm_ffa.h>`; stock imports `ffa_driver_register` with CRC `0x0d53cde9` and defines `gz_ffa_driver_probe`/`gz_get_ffa_dev`. Behind `!IS_REACHABLE()` the prototypes degrade to stubs and neither the import nor that CRC could appear. |
| `CONFIG_COMPAT` | ON | stock defines `gz_compat_ioctl` (36 bytes) and installs it in `fops.compat_ioctl`; both live inside `#if IS_ENABLED(CONFIG_COMPAT)`. |
| `CONFIG_64BIT` | ON | AArch64 GKI baseline. |

## 2. Proven OFF / deliberately not defined

| CONFIG | state | stock evidence |
|---|---|---|
| `CONFIG_MTK_GZ_SUPPORT_SDSP` | OFF | the `MTEE_CMD_FOD_TEE_SHM_ON/OFF` ioctl cases live in an `#ifndef CONFIG_MTK_GZ_SUPPORT_SDSP` block. Stock contains both strings `====> MTEE_CMD_FOD_TEE_SHM_ON ====` and `====> MTEE_CMD_FOD_TEE_SHM_OFF ====`, and the compiled `_gz_ioctl` switch contains the `0x5410`/`0x5411` comparands. The branch is therefore compiled in, so the symbol is undefined. |
| `enable_code` | 0 | source-level `#define enable_code 0`; the DEVAPC violation-callback block is excluded. Stock has no `register_devapc_vio_callback` import. |
| `CONFIG_DEVICE_MODULES_MTK_DEVAPC` | irrelevant/OFF | only reachable inside `#if enable_code`, which is 0. |
| `CONFIG_GZ_VPU_WITH_M4U` | OFF | would add `gz_do_m4u_map`/`gz_do_m4u_umap` prototypes; stock references neither. |
| `CONFIG_MT_GZ_TRUSTY_DEBUGFS` | OFF | would add `mtee_create_debugfs`; stock references it nowhere. |
| `CONFIG_TEE` | not defined | in the vendor Makefile this only selects extra `-I` search paths for Trustonic/Microtrust trees. `gz_main_mod` includes no TEEC header, and the build resolves cleanly without it. |
| `CONFIG_TRUSTONIC_TEE_SUPPORT`, `CONFIG_MICROTRUST_TEE_SUPPORT` | OFF | same Makefile branch; no `TEEC_*` or `teei` symbol appears anywhere in stock. |

## 3. Compiler / codegen flags

| flag | evidence |
|---|---|
| `-faddrsig` | stock carries a `.llvm_addrsig` section. |
| clang 17.0.2 (Android 10087095, `+pgo +bolt +lto`) | stock `.comment`. Supplied by the exact GKI ab/12901745 toolchain. |
| KCFI | 42/42 stock functions carry `__kcfi_typeid`-consistent prologues; reproduced exactly by the GKI build. |
| MODVERSIONS | stock `vermagic` contains `modversions`; 77 `__versions` records present. |

## 4. What was deliberately NOT enabled

The GenieZone Kconfig menu offers several further switches
(`MTK_GZ_LOG`, `MTK_GZ_VIRTIO`, `MTK_GZ_VIRTIO_IPC`, `MTK_GZ_IRQ`,
`GZ_SEC_STORAGE_UT`). None of them affects the `gz_main_mod` object list, and
no stock evidence calls for them, so none was defined. In particular
`gz_sec_storage_ut.o` is **not** in the vendor `gz_main_mod-objs` list and no
secure-storage UT function exists in stock.

## 5. Verification

Building with exactly this config set produced a module whose 42 functions are
byte-identical to stock and whose 2817 relocations and 77 MODVERSION records
match exactly. Any error in this contract would have shown up as a function
size, relocation or CRC difference.
