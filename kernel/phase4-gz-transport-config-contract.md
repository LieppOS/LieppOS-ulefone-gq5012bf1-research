# GQ5012BF1 GenieZone transport config contract

## Exact build contract

| Symbol / flag | Stock state | Applies to | Evidence |
|---|---:|---|---|
| `CONFIG_MTK_ENABLE_GENIEZONE` | `m` | `gz_trusty_mod` | vendor Kbuild output selector; module exists; exact object set |
| `CONFIG_MTK_GZ_VIRTIO_IPC` | `m` | `gz_ipc_mod` | vendor Kbuild output selector; module exists; `trusty-ipc.o` exact |
| `CONFIG_MT_GZ_TRUSTY_DEBUGFS` | **OFF** | Trusty | no `trusty-debugfs.o` functions/imports/objects; stock has `Not MT_GZ_TRUSTY_DEBUGFS` branch |
| `CONFIG_MTK_AEE_IPANIC` | **OFF** | Trusty | no AEE/IPANIC imports or ramconsole branch bytes |
| `CONFIG_ARM64` | **ON** | Trusty | AArch64 exact GKI; inline SMC path and stock function bytes |
| `CONFIG_64BIT` | **ON** | Trusty | `trusty_fast_call64` present, size 164, KCFI `0x75b39c8b` |
| `CONFIG_COMPAT` | **ON** | IPC | `tipc_compat_ioctl_entry` and `.compat_ioctl` present |
| `DYNAMIC_SET_PRIORITY` | **undefined/OFF** | Trusty | `trusty_nop_set_switch_pri` compiles to stock no-op branch; scheduler-call imports absent |
| `ENABLE_GZ_TRACE_DUMP` | hard-disabled | Trusty | source macro is `(IS_ENABLED(CONFIG_FTRACE) & 0)`; stock `trusty_dump_systrace` is 8 bytes |
| `CONFIG_MTK_NEBULA_VM_SUPPORT` | not a predicate here | both | source unconditionally registers Trusty and Nebula drivers; stock DT contains both |
| `CONFIG_MTK_GZ_KREE` | not consumed | neither | belongs to `gz_tz_system`, not these object lists |
| `CONFIG_TEE` | not consumed | neither | no conditional in these sources |
| `CONFIG_PM_SLEEP` | not consumed | neither | no conditional in these sources |
| FF-A/shared-memory config | not consumed | neither | no FF-A object or predicate in the transport providers |
| `-faddrsig` | **ON** | both | stock and rebuild carry `.llvm_addrsig`; required for section-set parity |

## Selection discipline

Only the predicates above that affect these translation units are made visible in the wrapper. No broad GenieZone config set is enabled. In particular, Trusty debugfs and AEE/IPANIC remain off.

Final object lists are exactly:

```text
gz_trusty_mod = trusty.o + smcnr-table.o
gz_ipc_mod    = trusty-ipc.o
```

The final build target emits both modules together against `//common:kernel_aarch64`. `CONFIG_COMPAT`, `CONFIG_ARM64`, and `CONFIG_64BIT` come from the exact GKI configuration; the wrapper exposes only the two MediaTek module selectors and `-faddrsig` needed by these sources.

## Multi-TEE behavior

Multi-TEE support is not guessed from a Kconfig name. It is directly stock-proven by:

- `trusty_driver` and `nebula_driver` objects;
- DT compatibles `android,trusty-smc-v1` and `android,nebula-smc-v1`;
- stock root nodes `trusty` (`tee-id = 0`) and `nebula` (`tee-id = 1`);
- TIPC virtio tables for both Trusty and Nebula;
- `enum tee_id_t { TRUSTY=0, NEBULA=1, END }` and byte-identical branch logic.
