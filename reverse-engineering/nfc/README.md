# NFC (GQ5012BF1 / Ulefone Armor 29 Pro Thermal)

Named scope for the STMicroelectronics ST21NFC contactless front end: the Linux
driver, its kernel/userspace contract, the Android NFC HAL path, the firmware
and secure-element boundaries, and the board RF configuration.

| document | content |
|---|---|
| [`STATUS.md`](STATUS.md) | phase audit, closure, boundaries |
| [`hardware/topology.md`](hardware/topology.md) | fitted part, bus, GPIOs, clock, DT contract |
| [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) | stock NFC modules |
| [`kernel/source-map.tsv`](kernel/source-map.tsv) | object → source → donor revision |
| [`kernel/parity/st21nfc.parity.txt`](kernel/parity/st21nfc.parity.txt) | full stock-vs-rebuild parity report |
| [`protocol/kernel-userspace.md`](protocol/kernel-userspace.md) | `/dev/st21nfc` ABI, ioctls, IRQ/poll/PM |
| [`protocol/recovery.md`](protocol/recovery.md) | reset/recovery/firmware-download paths |
| [`firmware/boundary.md`](firmware/boundary.md), [`firmware/inventory.tsv`](firmware/inventory.tsv) | firmware class, who writes it, when |
| [`userspace/hal-map.md`](userspace/hal-map.md), [`userspace/dependency-map.tsv`](userspace/dependency-map.tsv) | framework → HAL → kernel chain |
| [`secure-element/topology.md`](secure-element/topology.md) | UICC / eSE / NDEF-NFCEE result |
| [`configuration/analysis.md`](configuration/analysis.md), [`configuration/inventory.tsv`](configuration/inventory.tsv) | NCI/HAL/RF configuration, enabled technologies |
| [`yft-nfc-deltas.md`](yft-nfc-deltas.md) | every confirmed Ulefone/board delta |
| [`reconstruction/`](reconstruction/) | reconstructed source + patch |

## Hardware in one paragraph

A single STMicroelectronics **ST21NFC-family controller-only CLF** (no on-die
secure element product option selected) sits on **MT6878 I²C6 at slave 0x08**,
with **IRQ on GPIO 2** (MediaTek EINT 2, level-triggered, Linux IRQ 47),
**RESET on GPIO 40**, **CLK_REQ on GPIO 151**, and its reference clock from the
SRCLKEN-RC `nfc` consumer (XO buffer `BBCK4`, sub-id 0x0b). There is no
power-idle GPIO, no Linux regulator and no pinctrl state for it. Linux binds it
through `compatible = "st,st21nfc"` with `st21nfc.ko` v2.2.0.19 loaded from the
**vendor ramdisk**, exposing `/dev/st21nfc` (`0660 nfc radio`,
`u:object_r:st21nfc_device:s0`).

```
Android NFC (Nfc_st app) → libstnfc_nci_jni → libstnfc-nci
   → AIDL android.hardware.nfc INfc/default (V1)
   → android.hardware.nfc-service-st → nfc_nci.st21nfc.st.so
   → /dev/st21nfc → st21nfc.ko → I2C6@0x08 → ST21NFC CLF
                                               ├─ NFCEE 0x81  UICC (slot-independent)
                                               ├─ NFCEE 0x82  eSE (not exposed via OMAPI)
                                               └─ NFCEE 0x10  Type-4 NDEF (disabled in stock)
```

## Kernel closure

A = shipped `st21nfc.ko` from the stock vendor ramdisk
(`workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/st21nfc.ko`,
sha256 `5c5945457f8e3f37744c95a98075278134a328590d27e00d38dd8de8261078e8`).
B = rebuild of the reconstructed source at `kernel_device_modules-6.1` commit
`a8ec14c`, exact GKI `6.1.115-android14-11-g945dff7bc1bf`.

| axis | result |
|---|---|
| functions | 24/24 present, 23/24 size-identical, **22/24 byte-identical** |
| `st21nfc_dev_ioctl` | identical instruction multiset and identical relocation/call/string multiset; **only two BL displacement fields differ** (callees sit at different `.text` offsets) |
| `st21nfc_ping` | +12 bytes: one error-path `printk` tail that stock merges into the shared epilogue; identical calls and arguments |
| data objects | 33/33 present, 31/33 byte-identical (`srcversion`, and `__versions` entry ordering) |
| imports | **54/54** names and modversion CRCs exact |
| exports | 0/0 |
| `.modinfo` | identical: `name`, `license`, `author`, `description`, `version=2.2.0.19`, both `alias=` lines, `vermagic`, `depends=` |
| `.rodata`, `.data` | byte-exact |
| `.rodata.str1.1` | identical size (3214) and identical string multiset; order differs |
| KCFI | not applicable — the module contains no `__cfi` symbols |

Donor: NothingOSS MT6878 `device_modules` `957dac1`, which alone yields only
7/24 byte-exact functions. The five recovered source deltas are listed in
[`yft-nfc-deltas.md`](yft-nfc-deltas.md).
