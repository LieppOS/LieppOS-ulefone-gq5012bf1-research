# NFC RE status

Scope: ST21NFC CLF kernel driver, its userspace contract, and the HAL /
firmware / secure-element / RF-configuration boundaries around it.

## Phase audit

| component | prior state | gap at start | donor | offline-solvable | result |
|---|---|---|---|---|---|
| fitted hardware identity | "ST21 family, variant unknown" | exact part, bus, GPIOs, clock | DT + live captures | yes | **closed**: ST21NFC controller-only CLF, I²C6@0x08, GPIO 2/40/151, BBCK4 clock, HwVersion 0x04 |
| `st21nfc.ko` source | frozen reconstruction, 20/24 byte-exact (`RECONSTRUCTED_2.2.0.19_FROZEN`) | 4 functions, string table, vermagic | NothingOSS 957dac1 | yes | **improved to 22/24 byte-exact**, 24/24 semantically equivalent, strings and modinfo exact |
| kernel/userspace protocol | partially documented | ioctl semantics, read/poll/IRQ contract | reconstructed source | yes | **closed** (`protocol/kernel-userspace.md`) |
| recovery behaviour | "mentioned" | trigger, GPIO sequence, timings, who can start it | reconstructed source + stock binaries | yes | **closed** (`protocol/recovery.md`) |
| firmware boundary | unknown | class, loader, update trigger | stock binaries/strings | yes | **closed**: flash-resident patch FW, userspace-only download, no write in steady state |
| Android HAL path | partially mapped | AIDL version, service, libs, deps | stock partitions | yes | **closed** (`userspace/hal-map.md`) |
| NFC technologies | partially known | capability vs enablement | configuration files | yes | **closed** (`configuration/analysis.md`) |
| secure element | contradictory notes | eSE real or config-only | runtime NFCEE capture + partitions | yes | **closed**: UICC 0x81 + eSE 0x82 exist; **no OMAPI eSE**, no ST54-SPI driver |
| RF/antenna configuration | unknown | what is board-specific, is anything per-unit | `st21nfc_conf.txt` | yes | **closed**: design-level tuning, no per-unit calibration |
| ST FW images, ST HAL, STFlashTool | proprietary | — | none | no | **PARTIAL boundary**, mapped only |

## Exact kernel closure

[`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) is authoritative;
the full report is [`kernel/parity/st21nfc.parity.txt`](kernel/parity/st21nfc.parity.txt).

A = shipped vendor-ramdisk `st21nfc.ko` (sha256 `5c594545…`).
B = rebuild from `reconstruction/source/` at KDM commit `a8ec14c`, exact GKI
`6.1.115-android14-11-g945dff7bc1bf`.

- **22/24 functions byte-identical**, 23/24 size-identical, 24/24 present.
- 54/54 import modversion CRCs exact; 0/0 exports; `.modinfo` identical
  including `vermagic` and `version=2.2.0.19`.
- `.rodata` and `.data` byte-exact; `.rodata.str1.1` identical size and string
  multiset.
- 33/33 data objects present; the two that differ are `srcversion` (expected:
  the source text differs from ST's original) and `__versions` **ordering**
  (same 54 names, same 54 CRCs).

### Residual, with named operands

1. `st21nfc_dev_ioctl` (A size 1440 = B size 1440): the **instruction multiset
   and the relocation/call/string multiset are identical**; two `BL`
   displacement fields differ because `st21nfc_disable_irq` and
   `st21nfc_loc_set_polaritymode` land at different `.text` offsets. Clang's
   emission order for this translation unit is not source-definition order
   (verified by moving definitions: the order did not change), so the ordering
   is not reachable by source edits found so far.
2. `st21nfc_ping` (A 644, B 656): identical calls and arguments; stock merges
   the "Could not read payload" error tail into the shared `_printk` epilogue
   (it keeps `read_ret` in `w2`), the rebuild emits three extra instructions.
   Also a loop-counter form difference (stock counts `-4 → 0` with
   `adds/b.lo`, the rebuild counts down with `subs/b.ne`) with no size effect;
   six loop spellings were tried, all canonicalise to the down-counter.

Both are compiler-layout artefacts of an otherwise identical program. No
semantic difference was found on any axis (calls, arguments, strings,
relocations, control flow).

## Boundaries

### Reconstructable (done)

- `st21nfc.ko` v2.2.0.19 in full, including the probe-time ping/recovery loop,
  the double-pulse reset, the ST21NFCD recovery GPIO sequence, the ioctl
  surface, IRQ/poll arbitration, suspend/resume wake behaviour and sysfs.
- The device-tree contract and the `/dev/st21nfc` ABI.

### Proprietary, mapped but not source-closed

- `st21nfc_fw7.bin` / `st21nfc_fw.bin` (signed ST flash patch images).
- `nfc_nci.st21nfc.st.so` (ST NCI HAL incl. the FW-download state machine).
- `STFlashTool`, `libstnfc-nci.so`, `libstnfc_nci_jni.so`, `Nfc_st.apk`,
  `com.st.android.nfc_extensions.jar`.
- The opaque NCI proprietary payloads inside `st21nfc_conf.txt`.
- The MediaTek UICC secure-element HAL (`MtkUiccSEHal`) behind
  `ISecureElement/SIM1|SIM2`.

### Physical/runtime only

- Antenna geometry and placement (the matching record in `st21nfc_conf.txt`
  describes a differential antenna with an EMI filter, but not its location).
- Field strength, interoperability and range measurements.
- Whether the eSE at NFCEE 0x82 holds any provisioned applet (not reachable
  from Android on this build).

## Known stock defects carried for LieppOS

1. `/data/nfc` is labelled `system_data_file` with no `nfc_data_file`
   file-context rule → NFA persistent storage fails under enforcing SELinux.
   Fix: `/data/nfc(/.*)?  u:object_r:nfc_data_file:s0` + restorecon.
2. The AIDL NFC HAL is V1 while the Mainline NFC module expects the newer
   `getConfig` layout → `t4tNfceeEnable` is always 0, so the controller-resident
   Type-4 NDEF NFCEE (0x10) is discarded even when `NDEF_NFCEE_ENABLE=1`.

## Scope state

**Kernel/device scope: closed** (`ST21NFC`). The NFC *ecosystem* remains
PARTIAL because the ST firmware images, the ST NCI HAL, `STFlashTool` and the
secure-element HAL are proprietary and material to full functionality — that
part is tracked by the `NFC-SECURE-ELEMENT` component.
