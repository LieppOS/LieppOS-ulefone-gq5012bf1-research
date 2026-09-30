# U17 - exact ST21NFC silicon variant and secure-element topology

**Current claim:** "ST21 family, firmware/SE images" - exact B/D variant and antenna match unknown.

**Previous confidence:** UNKNOWN.

**New evidence**
* **The HAL supports four ST controller families and the board selects one of them.** `vendor/lib64/nfc_nci.st21nfc.st.so` contains code paths and file names for `st21nfc_fw.bin` / `st21nfc_fw7.bin` / `st21nfc_conf.txt`, `st54j_fw.bin` / `st54j_conf.txt`, `st54l_fw.bin` / `st54l_conf.txt`, plus log strings `CLF version : ST54J`, `CLF version : ST54K` and `HAL_FD_ST54L_STATE_SEND_RAW_APDU`.
* **The board is configured for the ST21NFC path**: `libnfc-hal-st.conf` sets `NCI_HAL_MODULE = "nfc_nci.st21nfc"`, `STNFC_FW_BIN_NAME = "st21nfc_fw7.bin"`, `STNFC_FW_CONF_NAME = "st21nfc_conf.txt"`. The ST54 paths are unused.
* **The ST54 family is specifically the "NFC controller **plus** integrated eSE" product line**, whereas ST21NFC is a controller-only CLF. Since the ST54 configuration is not selected, the fitted part is a controller without an on-die secure element.
* **The declared platform features corroborate that**: the stock images declare `android.hardware.nfc`, `android.hardware.nfc.hce`, `android.hardware.nfc.hcef`, `android.hardware.nfc.uicc` and, for OMAPI, **only** `android.hardware.se.omapi.uicc`. There is **no `android.hardware.se.omapi.ese`**. The `OFFHOST_ROUTE_ESE={82}` / `OFF_HOST_ESE_PIPE_ID=0x5E` lines in the ST configuration are ST reference defaults that no declared feature backs.
* **Antenna tuning is present and board-specific**: `st21nfc_conf.txt` carries `CustomA` and `CustomB` RF parameter blobs, a `DPC` (dynamic power control) table, an `ANTENNA CONFIG` command, UICC/SE/IOT/NFCC configuration blocks and a configuration CRC of `4646`, all applied over NCI proprietary commands at boot. It also uses `HW_RESET_I2C` and `NCI_CORE_RESET/INIT`.
* Bus binding: i2c `6-0008`, driver `st21nfc`, module `st21nfc`, `compatible = "st,st21nfc"`; a live wake-source entry `st21nfc` appears in the suspend log, so the controller is active.
* One runtime error is visible: `st21nfc_dev_write : i2c_master_send returned -6` (ENXIO) during a screen-on transition - a transient write while the CLF was powered down, not a fault indication.

**Contradicting evidence:** none, beyond the misleading presence of unused ST54/eSE strings in the shared HAL.

**Internet sources:** VI21 (ST21NFCD: single NFC controller IC for mobile devices, active load modulation), VI22 (ST product structure: ST21NFC = controller; ST54 = controller + eSE).

**Local evidence:** VL20, VL21.

**Read-only live evidence:** i2c binding and wake-source entry from the frozen capture.

**Final conclusion**
The NFC controller is an **ST21NFC-family contactless front end (ST21NFCD class), running the `st21nfc_fw7` firmware image, with board-specific CustomA/CustomB RF tuning, a DPC table and an explicit antenna configuration**. It is a **controller-only part: there is no integrated or discrete embedded secure element on this device**. Off-host card emulation is available through the **UICC (SIM)** only, alongside host card emulation (HCE and HCE-F).

**Final confidence:** family + firmware image + RF-tuning presence + "no eSE" = **PROVEN**. Narrowing to ST21NFCD specifically = **STRONGLY_SUPPORTED**. The exact orderable ST part number and package = **TEARDOWN_REQUIRED**.

**Remaining uncertainty:** the HAL prints `HwVersion = 0x%02X` at runtime; capturing that byte from an NFC logcat on stock software would pin the silicon revision without any write access.

**Impact on final inventory:** YES - the NFC row gains the firmware image, the RF-tuning evidence and, importantly, the corrected secure-element picture (UICC only, no eSE).

**Answers:** (1) ST21NFC-family CLF with fw7 and board RF tuning, no eSE; (2) the `HwVersion` byte / package marking; (3) yes; (4) yes - read `HwVersion` from NFC logs; (5) yes; (6) for the exact P/N; (7) ST21NFCD-class ST21NFC controller; (8) STRONGLY_SUPPORTED; (9) yes; (10) yes; (11) no.
