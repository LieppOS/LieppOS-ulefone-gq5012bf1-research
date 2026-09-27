# Existing kernel compatibility

Current runtime kernel: `6.1.115-android14-11`.

## What Android 17 source expects

- **PROVEN:** a device launching at Android 17 / FCM `202604` has the new
  Android-C kernel baseline under `kernel/configs/c/android-6.18`.
- **PROVEN:** framework compatibility still retains Android-U FCM level 8 and
  `kernel/configs/u/android-6.1`; an upgrade/vendor stack is not forced onto the
  new-launch 6.18 baseline merely because system is Android 17.
- **PROVEN:** `PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS=true` for the GSI
  configuration.

## Exact 6.1 config comparison

The repository's exact-stock GKI reconstruction config has 6002 entries.
Against Lineage 24's retained U/Android-6.1 requirements:

```text
unconditional requirements: 263
semantic mismatches:          0
active conditional rules:    19
semantic mismatches:          0
```

The only textual base differences were two obsolete negative symbols absent
from modern Kconfig; absent is semantically `n`. The 22.2→24.0 conditional file
removed only a 32-bit ARM `CPU_SW_DOMAIN_PAN` rule, irrelevant to arm64.

Selected exact config evidence:

| Facility | Current config |
|---|---|
| binder IPC / binderfs | `y` / `y` |
| BPF syscall/JIT/JIT-always-on | `y/y/y` |
| EROFS | `y` |
| F2FS | `y` |
| fscrypt | `y` |
| dm-verity / dm-crypt | `y/y` |
| SELinux | `y` |
| arm64 MTE | `y` |
| userfaultfd | `y` |

The current chain also already boots EROFS, F2FS userdata, fscrypt metadata
protection, AVB/dm-verity and separate vendor/system DLKM partitions.

## GKI/KMI conclusion

- **PROVEN:** current kernel meets the frozen U/6.1 config contract represented
  in Android 17 source. Existing vendor modules have extensive KMI/CRC evidence
  in `kernel/` and are not being replaced here.
- **INFERRED:** binder, BPF and filesystem primitives are sufficient for an
  initial API-37 userspace boot. A currently running Android 16 GSI on this same
  kernel/vendor is strong one-generation-up evidence.
- **UNKNOWN:** API-37 module BPF program loading, ART/uprobes behavior, new
  optional eBPF helpers, graphics synchronization and all hardware runtime
  paths until booted.
- **KNOWN RISK:** 6.1.115 is old and not a production-security endpoint for a
  2026 Android 17 ROM. Passing initial boot does not make it a final kernel.
- **TEST TO CONFIRM:** run Android-17 `checkvintf` with the assembled matrices,
  then capture dmesg/BPF loader/module/SELinux failures from an isolated boot.

`CURRENT_KERNEL_INITIAL_BOOT_PLAUSIBLE=1` means plausible, not proven or
certifiable.
