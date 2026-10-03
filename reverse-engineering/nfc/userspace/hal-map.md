# Android NFC userspace map

All paths are inside the stock partitions
(`workspace/gq5012bf1/stock/partitions/...`).

## Stack

```
android.nfc framework (AOSP, com.android.nfcservices APEX)
   |  NfcService / NfcAdapter / HostApduService
   |  system_ext/priv-app/Nfc_st  (ST-customised Nfc app, replaces AOSP NfcNci)
   |  system_ext/framework/com.st.android.nfc_extensions.jar
   v
libnfc_nci_jni.so  (APEX + system_ext/lib64 copy)
libstnfc-nci.so    (system_ext/lib64, ST fork of libnfc-nci: NFA/NCI/RW layers)
   |  AIDL android.hardware.nfc INfc/default  (V1)
   v
/vendor/bin/hw/android.hardware.nfc-service-st
   |  dlopen "nfc_nci.st21nfc" (hw_module)
   v
/vendor/lib64/nfc_nci.st21nfc.st.so        (ST NCI HAL: I2C transport + FW download)
   |  open/read/write/ioctl
   v
/dev/st21nfc  ->  st21nfc.ko  ->  I2C6 @0x08  ->  ST21NFC CLF
```

## Services and VINTF

| item | value |
|---|---|
| HAL interface | **AIDL** `android.hardware.nfc`, `INfc/default` (`vendor/etc/vintf/manifest/nfc-service-st.xml`, no version attribute → V1) |
| service | `service nfc_hal_service /vendor/bin/hw/android.hardware.nfc-service-st`, `class hal`, `user nfc`, `group nfc` (`vendor/etc/init/nfc-service-st.rc`) |
| second service | `service stflashtool /vendor/bin/STFlashTool`, `class late_start`, `user nfc`, `group nfc`, `oneshot` (`vendor/etc/init/hw/init.stnfc.rc`) |
| SELinux | `hal_nfc_default_exec` for the HAL binary, `st21nfc_device` for `/dev/st21nfc`, `nfc_socket_file` for `/data/nfc_socket`, `vendor_nfc_socket_file` for `/data/vendor/nfc_socket` |
| device node perms | `/dev/st21nfc 0660 nfc radio` (`vendor/etc/ueventd.rc`) |

Note: the AIDL V1 service is older than the Mainline NFC module it talks to.
That version skew is the proven cause of the T4T/NDEF-NFCEE feature being
dropped (`StNfc_hal_getConfig()` never reports `t4tNfceeEnable`) — see the
runtime analysis carried in
`../../../Reverse Engineer - PARTIAL/ST21NFC/notes/st21nfc-current-findings.md`.

## Binaries and libraries

| object | size | sha256 |
|---|---:|---|
| `vendor/bin/hw/android.hardware.nfc-service-st` | 37904 | `f5c620cecf32962f31631219a28b5262f9a946b212f012d327aaf706728ac82d` |
| `vendor/lib64/nfc_nci.st21nfc.st.so` | 162040 | `7dc795b36ac30139a631ace654cf13beacbfb74487b0b2166a886b3e62196eb0` |
| `vendor/bin/STFlashTool` | 717224 | `513b63a33250bc1e12cd0d0ecd33c27c353a83b586c6ae60a5b22b55901b442b` |
| `system_ext/lib64/libstnfc-nci.so` | 1889600 | `ff6be1dd81f12b8bd03e9a2b36d32070777b141448b7503aa25d6623af3f1f2e` |
| `system_ext/lib64/libstnfc_nci_jni.so` | 2370288 | `85c5280e7bdd649667333c68b50f48fcb667dc05df64fa106d7bb169c8db08de` |
| `system_ext/framework/com.st.android.nfc_extensions.jar` | — | ST NFC extensions framework library |
| `system_ext/priv-app/Nfc_st/Nfc_st.apk` | — | ST-customised NFC app |

### ELF dependencies

`android.hardware.nfc-service-st` → `libbase`, `liblog`, `libutils`,
`libbinder_ndk`, `android.hardware.nfc-V1-ndk.so`, **`nfc_nci.st21nfc.st.so`**,
`libc++`, `libc`, `libm`, `libdl`.

`nfc_nci.st21nfc.st.so` → `libbase`, `libcutils`, `libhardware`,
`libhardware_legacy`, `libhidlbase`, `liblog`, `libutils`, `libc++`, `libc`,
`libm`, `libdl`. It opens `/dev/st21nfc` directly; no further vendor library.

## Declared platform features

| feature file | meaning |
|---|---|
| `android.hardware.nfc.xml` | NFC present |
| `android.hardware.nfc.hce.xml` | host card emulation (ISO-DEP) |
| `android.hardware.nfc.hcef.xml` | host card emulation NFC-F |
| `android.hardware.nfc.uicc.xml` | UICC-backed off-host CE |
| `android.hardware.se.omapi.prebuilt.xml` | declares **only** `android.hardware.se.omapi.uicc` |

There is **no** `android.hardware.se.omapi.ese` feature — see
[`../secure-element/topology.md`](../secure-element/topology.md).

## Persistent storage

`NFA_STORAGE="/data/nfc"`, `PRESERVE_STORAGE=1` (HAL conf) / `0x01` (NCI conf).
Stock ships `/data/nfc` owned `nfc:nfc 0770` but labelled
`u:object_r:system_data_file:s0`, while the NFC domain is `u:r:nfc:s0` and the
policy only grants it `nfc_data_file`. The missing file-context rule is a proven
stock bug (AVC denial on `nfaStorage.bin1`, `nfa_nv_co_write: fail to open,
error = 13`). A replacement ROM needs:

```
/data/nfc(/.*)?    u:object_r:nfc_data_file:s0
```

plus a `restorecon` of existing content.
