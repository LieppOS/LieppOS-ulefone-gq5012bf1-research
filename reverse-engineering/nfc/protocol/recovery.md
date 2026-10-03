# ST21NFC recovery and reset paths

Static analysis only. **No recovery sequence was triggered on hardware for this
document**; everything below is read from the reconstructed driver source and
the stock userspace binaries.

There are three distinct "reset-ish" paths. They must not be confused.

## 1. Double-pulse reset — `ST21NFC_PULSE_RESET` (`_IO(0xEA,2)`)

Purpose: force the CLF out of Quick Boot / resynchronise NCI.

```
if (!IS_ERR_OR_NULL(gpiod_reset)) {
        st54spi_cb(ST54SPI_CB_RESET_START)
        RESET = 0;  msleep(20);
        RESET = 1;  usleep_range(10000, 11000);
        RESET = 0;  msleep(20);
        RESET = 1;
        st54spi_cb(ST54SPI_CB_RESET_END)
}
r_state_current = ST21NFC_HEADER;
```

Timing: 20 ms low, ~10 ms high, 20 ms low, then released. No IRQ detach, no GPIO
direction change. This is the normal HAL "hardware reset" used before
`CORE_RESET_CMD` and by `st21nfc_conf.txt`'s `HW_RESET_I2C` step.

## 2. ST21NFCD recovery — `ST21NFC_RECOVERY` (`_IO(0xEA,8)`)

Driver comment: `/* For ST21NFCD usage only */`. Serialised by `irq_dir_mutex`.

```
 1. if (irq_is_attached) devm_free_irq();          irq_is_attached = false
 2. RESET = 0;                      usleep_range(10000, 11000)
 3. gpiod_direction_output(IRQ_GPIO, 1)            <- the IRQ line is driven by the AP
       on failure: pr_err "gpiod_direction_output failed", unlock, return -ENODEV
 4. IRQ_GPIO = 1;                   usleep_range(10000, 11000)
 5. RESET = 1                                      ("done Pulse Request")
 6. msleep(20); IRQ_GPIO = 0
 7. msleep(20); IRQ_GPIO = 1
 8. msleep(20); IRQ_GPIO = 0
 9. msleep(20)                                     ("Recovery procedure finished")
10. gpiod_direction_input(IRQ_GPIO)
       on failure: pr_err "gpiod_direction_input failed"
11. irq_enabled = true
12. devm_request_irq(client->irq, st21nfc_dev_irq_handler, polarity_mode, ...)
       on failure: pr_err "devm_request_irq failed", unlock, return -ENODEV
13. irq_is_attached = true; st21nfc_disable_irq()
14. unlock; return 0
```

What it is: the CLF is held in reset while the **IRQ pin is driven as an output**
and toggled 1→0→1→0 with 20 ms spacing after the reset is released. On
ST21NFCD-class parts this pin pattern sampled around the reset edge selects the
controller's alternate boot/recovery entry, i.e. it is the documented way to get
a bricked/mis-flashed CLF back into **loader mode** so that a firmware image can
be re-downloaded over I²C.

Critical properties:

- It does **not** itself transfer any firmware. It only changes the boot state.
- It leaves the IRQ line back as an input with the handler re-attached and
  masked, so the node stays usable afterwards.
- Timing is entirely GPIO/msleep based; total ~130 ms.
- Total control is in userspace: only `/dev/st21nfc` ioctl 0xEA08 can start it.

## 3. Probe-time recovery loop (automatic, every boot)

`st21nfc_probe()` validates the controller before exposing the device:

```
for (recovery = 0; recovery < 3; recovery++) {
        ret = st21nfc_ping(dev);              /* expects CORE_RESET_NTF */
        if (!ret) break;
        pr_err("Did not get CORE_RESET_NTF (%d), try recovery");
        st21nfc_recovery(dev, /*restore_irq=*/false);
}
if (ret && recovery == 3) ret = st21nfc_ping(dev);
if (ret) { pr_err("Did not get CORE_RESET_NTF, hardware issue? (%d)"); goto err_pidle_workqueue; }
```

`st21nfc_recovery(dev, false)` is the same GPIO sequence as path 2 but skips the
IRQ detach/attach (the IRQ is not requested yet at that point in probe).

`st21nfc_ping()` is the kernel-side NCI probe:

1. refuse if the node is already open (`-EBUSY`);
2. one throw-away 1-byte `i2c_master_recv` (forces the CLF out of Quick Boot);
3. the same double-pulse reset as path 1;
4. `msleep(10)`, then up to **4** attempts:
   - if the IRQ GPIO is low → break (nothing to read);
   - read a 3-byte NCI header; handle the `7E` filler cases
     (`7E 7E 7E` → `"Read 7E7E7E... header, IRQ always high ? Stop"`, otherwise
     shift and read the missing header bytes);
   - read `buffer[2]` payload bytes;
   - log `"Read message (%d bytes): %02x %02x %02x %02x ..."`;
   - **success condition: `buffer[0] == 0x60 && buffer[1] == 0x00`**, i.e. an NCI
     notification with GID 0 / OID 0 = `CORE_RESET_NTF` → `status = 0`;
   - `msleep(5)` and retry.

So a normal boot performs: ping → (if no `CORE_RESET_NTF`) recovery → ping, up to
three times, plus one final ping. Probe aborts with the recorded error if the
controller never answers.

## 4. Firmware download — userspace only

The kernel driver contains **no** firmware download logic, no `request_firmware`
and no loader-mode state machine. Downloading is entirely a userspace NCI/APDU
conversation over `/dev/st21nfc`, implemented twice:

- `nfc_nci.st21nfc.st.so` — `mFwUpdateTask`, `mHalFDState` state machine
  (`HAL_FD_STATE_AUTHENTICATE`, `HAL_FD_STATE_ERASE_FLASH`,
  `HAL_FD_STATE_ERASE_FLASH4`, `HAL_FD_STATE_SEND_RAW_APDU`,
  `HAL_FD_STATE_EXIT_APDU`), with retry/timeout handling
  (`"Timer for FW update procedure timeout, retry"`,
  `"Reached maximum nb of retries, FW update failed, exiting"`).
- `/vendor/bin/STFlashTool` — standalone tool, started at every boot from
  `init.stnfc.rc` as `service stflashtool ... class late_start ... oneshot`,
  running as `user nfc group nfc`.

Observable protocol markers inside those binaries:

```
-> Loader Mode NCI_CORE_RESET_NTF received after HW Reset
-> Loader V3 Mode NCI_CORE_RESET_NTF received after HW Reset
NCI_PROP_NFC_FW_RSP : loader mode
send NCI_PROP_NFC_FW_UPDATE_CMD and use 100 ms timer for each cmd from here
send APDU_ACTIVATE_LOADER
send APDU_ERASE_FLASH_LOADER (area 1 / area 2 / area 4)
Error exiting loader mode, i.e. a problem occured during FW update
Reset to factory loader / BackToFactoryLoaderIfPossible
```

Decision inputs it prints: `HwVersion = 0x%02X`, `LoaderVersion = 0x%06X`,
`CustomerVersion = 0x%04X`, `"%s integrates patch NFC FW version 0x%08X"`,
`"FW patch needs to be applied."`, `"Loader update available, do this first."`,
`"Loader mode and no applicable FW patch available."`,
`"integrates unknown patch NFC FW -- rejected"`.

### Does a normal boot write firmware?

**Yes, conditionally.** `stflashtool` runs on every boot and the HAL also owns a
FW-update task. Both compare the running patch version against the version
embedded in `/vendor/firmware/st21nfc_fw7.bin` and the config CRC against
`st21nfc_conf.txt`'s `REM CONFIG CRC IS 4646`; they only enter loader mode and
erase/program when a mismatch is found. On the captured device the running
`FwVersion = 0x01209280` and `CustomerVersion = 0x4646` already match the shipped
files, so the steady-state boot performs **no** flash write.

Consequence for a replacement ROM: shipping a different `st21nfc_fw*.bin` or a
different `st21nfc_conf.txt` **will cause a real flash write on the next boot**.
Keep both files, their names and the `STNFC_FW_*` keys in
`libnfc-hal-st.conf` byte-identical to stock unless a deliberate, verified
firmware change is intended.

## 5. Error states

| condition | driver behaviour |
|---|---|
| CLF never sends `CORE_RESET_NTF` | probe fails after 3 recovery attempts + 4 pings; no `/dev/st21nfc` is created |
| `gpiod_direction_output/input` fails during recovery | `-ENODEV`, mutex released, IRQ left detached |
| `devm_request_irq` fails during recovery | `-ENODEV`, **node left without an IRQ** until another polarity/recovery ioctl succeeds |
| I²C read/write error | errno propagated to userspace; HAL retries or restarts the stack |
| IRQ stuck high with `7E 7E 7E` | ping aborts early with `"IRQ always high ? Stop"` |
