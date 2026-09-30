# ST21 NFC runtime binary inventory

## Evidence status and limitation

The phone is not currently connected (`adb devices` returned no device), so fresh `/proc/<pid>/maps` capture was impossible during this completion pass. Historical captures establish:

- `com.android.nfc` PID 3315/8390 (`analysis/mfc-phone-precheck.txt`, `analysis/t4t-pre-reboot-process-namespace.txt`).
- `android.hardware.nfc-service-st` PID 3316/6198.
- NFC process mapped `/apex/com.android.nfcservices/lib64/libnfc_nci_jni.so`.
- The HAL executable is `/vendor/bin/hw/android.hardware.nfc-service-st`; its ELF `DT_NEEDED` entries require `nfc_nci.st21nfc.st.so` and `android.hardware.nfc-V1-ndk.so`.

The pre-reboot capture was made during a T4T bind-mount experiment: the process-visible APEX JNI hash was `1012cd...`, while the immutable/original APEX file was `b11bde...`. The audit below analyzes the pulled original `b11bde...` build. This distinction was missing from the first draft.

Exact current local metadata is preserved in `evidence/runtime-blob-metadata.tsv`.

## Runtime-path artifacts

| Artifact | Size | SHA-256 | Evidence/status |
|---|---:|---|---|
| `android.hardware.nfc-service-st` | 37,904 | `f5c620cecf32962f31631219a28b5262f9a946b212f012d327aaf706728ac82d` | HAL process executable; **PROVEN RUNTIME** by process name/capture |
| `nfc_nci.st21nfc.st.so` | 162,040 | `7dc795b36ac30139a631ace654cf13beacbfb74487b0b2166a886b3e62196eb0` | HAL `DT_NEEDED`; **STATIC IMPLEMENTATION**, necessarily loaded when service starts successfully |
| `android.hardware.nfc-V1-ndk.so` | 76,416 | `7ba4f4d3eec397583bef33524275a9bb168f31bb113cc2f15a4f67b63f03b3a3` | HAL `DT_NEEDED`; exact pull metadata |
| `libnfc_nci_jni.so` | 2,570,616 | `b11bdea0ac537778f437810d43133f1f5b9240383c639d308e551a71b921cd8e` | Immutable/original APEX JNI; historical process map proves path |
| `st21nfc_fw7.bin` | 215,568 | `458b6b586a14d10e646ce6787c20a3b165fb586b526bb565484d898f5d889d34` | Configured by `STNFC_FW_BIN_NAME`; pulled firmware |
| `st21nfc_fw.bin` | 215,568 | `35572928584a9fb090179bd66b528d26cb9cde326be34fe91bd902c1c3aeeb64` | Alternate firmware image present/pulled |

Corrected errors from the initial Gemini inventory: the AIDL library is 76,416 bytes with hash `7ba4...`, not 26,456 bytes/hash `1d18...`.

## Alternative stock `/system_ext` ST stack

These are useful for static comparison and contain ST extension APIs, but the available process-map evidence does **not** show them mapped in the active mainline NFC process:

| Artifact | Size | SHA-256 | Classification |
|---|---:|---|---|
| `libstnfc-nci.so` | 1,889,600 | `ff6be1dd81f12b8bd03e9a2b36d32070777b141448b7503aa25d6623af3f1f2e` | Alternative stack; not proven runtime-loaded |
| `libstnfc_nci_jni.so` | 2,370,288 | `85c5280e7bdd649667333c68b50f48fcb667dc05df64fa106d7bb169c8db08de` | Alternative JNI; not proven runtime-loaded |
| `com.st.android.nfc_extensions.jar` | 89,286 | `7e99f4743477360ac53782cc74b5bea2b808b30c0c0c5ae558e51ea59c0e87be` | Android APK/JAR with classes.dex; not proven runtime-loaded |

The prior sizes/hashes for all three were wrong and are superseded by `evidence/runtime-blob-metadata.tsv`.

## Important optional library

`nfc_nci.st21nfc.st.so` calls:

```text
dlopen("libstnfc-auth.so", RTLD_NOW)
dlsym: AuthLogVersionImpl
dlsym: AuthCheckCoreResetNtfImpl
dlsym: AuthHandlerImpl
dlsym: AuthCheckConfigCommandImpl
```

However, the library was not present on the tested device. Multiple runtime logs, including `analysis/mifare-090-listen-map-test.txt:329`, report:

```text
AuthCheckCoreResetNtf: libstnfc-auth.so not loaded: dlopen failed: library "libstnfc-auth.so" not found
```

Therefore it was **PROVEN RUNTIME ABSENT/NOT LOADED** in those boots. This corrects the earlier inventory, which mentioned the string but did not trace or classify the optional authentication module.

## Dynamic dependency summary

`android.hardware.nfc-service-st` depends on the AIDL NFC NDK interface and `nfc_nci.st21nfc.st.so`. The ST HAL library supplies transport, config-script handling, firmware loader logic, and optional authentication hooks. The mainline APEX JNI contains AOSP NFA/NFC stack logic and reader-side MIFARE functions.

The alternative `/system_ext` ST stack exports additional ST APIs such as raw vendor commands and `setForceSAK`, but those cannot be treated as reachable in the observed active process without a different package/library loading configuration.
