# NFC hardware topology (GQ5012BF1)

Evidence classes: **PROVEN** (direct artifact/live capture), **STRONGLY SUPPORTED**
(multiple independent artifacts, no contradiction), **INFERRED**, **UNKNOWN**.

## Fitted controller

| item | value | class | evidence |
|---|---|---|---|
| vendor | STMicroelectronics | PROVEN | `author=STMicroelectronics` in stock `st21nfc.ko`; `nfc_nci.st21nfc.st.so` |
| family | ST21NFC contactless front end (CLF), controller-only | PROVEN | DT `compatible = "st,st21nfc"`; HAL selects `NCI_HAL_MODULE="nfc_nci.st21nfc"`, `STNFC_FW_BIN_NAME="st21nfc_fw7.bin"`; the ST54 (CLF+eSE combo) paths in the same HAL are unused |
| die/marketing part (ST21NFCD vs other suffix) | ST21NFCD class | STRONGLY SUPPORTED | `/* For ST21NFCD usage only */` recovery path in the driver; HAL ST54J/ST54K/ST54L branches not selected |
| controller HW version | `HwVersion = 0x04`, `HwRevision = 0x04` | PROVEN (live) | NFC init capture in `../../../Reverse Engineer - PARTIAL/ST21NFC/notes/st21nfc-current-findings.md` |
| running FW patch | `FwVersion = 0x01209280` | PROVEN (live) | same capture; matches the shipped `st21nfc_fw7.bin` |
| loader version | `0x020201` | PROVEN (live) | same capture |
| customer config version | `0x4646` | PROVEN (live) | matches `REM CONFIG CRC IS 4646` in `/vendor/etc/st21nfc_conf.txt` |
| exact orderable P/N and package | — | UNKNOWN | teardown required |

## Board connection

All values from the merged live device tree
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`,
node `/soc/i2c@11e01000/st21nfc@8`, alias `st21nfc`) unless stated otherwise.

```dts
st21nfc@8 {
        compatible   = "st,st21nfc";
        reg          = <0x08>;                 /* I2C slave 0x08 */
        interrupt-parent = <&pinctrl>;         /* phandle 0x89 */
        interrupts   = <0x02 0x00>;            /* EINT on GPIO 2 */
        reset-gpios  = <&pinctrl 0x28 0x00>;   /* GPIO 40, active high */
        irq-gpios    = <&pinctrl 0x02 0x00>;   /* GPIO 2 */
        clkreq-gpios = <&pinctrl 0x97 0x00>;   /* GPIO 151 */
        status       = "okay";
};
```

| item | value | class |
|---|---|---|
| bus type | I²C | PROVEN |
| controller | `/soc/i2c@11e01000`, `compatible = "mediatek,mt6989-i2c"`, alias **i2c6** | PROVEN |
| slave address | **0x08** | PROVEN (DT `reg`, live `/sys/bus/i2c/devices/6-0008`) |
| IRQ GPIO | **GPIO 2**, MediaTek EINT 2, level-triggered, Linux IRQ 47 | PROVEN (DT + live `/proc/interrupts`: `47: ... mtk-eint 2 Level st21nfc`) |
| RESET GPIO | **GPIO 40** (`reset-gpios`) | PROVEN (DT) |
| CLK_REQ GPIO | **GPIO 151** (`clkreq-gpios`) — read by the DT but not requested by the shipped driver build | PROVEN (DT) |
| power-idle GPIO (`pidle-gpios`) | **absent** | PROVEN — no `pidle-gpios` property; the driver's `gpiod_pidle` therefore stays an `ERR_PTR` and the whole power-stats/idle path is inert on this board |
| regulators | **none in DT** — the CLF is not switched by a Linux regulator | PROVEN (no `*-supply` in the node) |
| pinctrl states | **none in the node** — no `pinctrl-0/-names` | PROVEN |
| clock source | PMIC/SRCLKEN-RC buffered XO: `srclken-rc@1c00d000 { nfc { xo-buf = "BBCK4"; sub-id = <0x0b>; } }` | PROVEN (DT) |
| wake source | `st21nfc` registered as a wakeup source; `enable_irq_wake()` on suspend | PROVEN (driver `st21nfc_suspend`, live suspend log) |

Derived topology:

```
MT6878 I2C6 (@0x11e01000) ── 0x08 ── ST21NFC CLF
                                  ├─ IRQ   : GPIO 2  → EINT 2 (level) → Linux IRQ 47
                                  ├─ RESET : GPIO 40
                                  ├─ CLKREQ: GPIO 151
                                  └─ CLK   : SRCLKEN-RC "nfc" sub-id 0x0b, XO buffer BBCK4
                          (no pidle GPIO, no DT regulator, no pinctrl state)
```

## Linux binding

| item | value | class |
|---|---|---|
| DT compatible | `st,st21nfc` (module aliases `of:N*T*Cst,st21nfc`, `of:N*T*Cst,st21nfcC*`) | PROVEN |
| kernel module | `st21nfc.ko`, version `2.2.0.19`, **vendor ramdisk** (`platform.cpio`, `modules.load` line 181) — *not* vendor_dlkm | PROVEN |
| device node | `/dev/st21nfc` (misc char device, `MISC_DYNAMIC_MINOR`, name `st21nfc`) | PROVEN |
| node ownership | `ueventd.rc`: `/dev/st21nfc 0660 nfc radio` | PROVEN |
| SELinux label | `u:object_r:st21nfc_device:s0` (`vendor_file_contexts`) | PROVEN |
| userspace consumer | `/vendor/bin/hw/android.hardware.nfc-service-st` → `nfc_nci.st21nfc.st.so` | PROVEN |
| second consumer | `/vendor/bin/STFlashTool` (firmware/config updater, `init.stnfc.rc`, class `late_start`, oneshot) | PROVEN |

## Not present

| item | result | class |
|---|---|---|
| ST54 SPI secure-element driver (`st54spi.ko`) | **not shipped** — `CONFIG_NFC_ST54_SPI=m` exists in the vendor defconfig but no `st54spi.ko` is in any partition or ramdisk | PROVEN |
| SPI-attached eSE | no SPI SE device in DT, no `st54spi` node, no SE SPI node | PROVEN |
| NXP/other NFC controller | none | PROVEN |
