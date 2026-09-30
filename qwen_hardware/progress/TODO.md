# Follow-up verification TODO

**Revised 2026-09-08.** Items closed by the verification pass have been removed; what remains is genuinely open. Full reasoning and the exact evidence each item needs are in `../verification/final/VERIFICATION-REPORT.md`.

## 1. Read-only capture on the untouched stock system (highest value)

- [ ] Full property, `dumpsys` and package capture on **stock** - the previous capture was a GSI, so no "stock uses" statement is currently evidenced.
- [ ] `/sys/class/regulator/*/{name,microvolts}` for programmed rail values (U16b).
- [ ] UFS `model` / `rev` / `manufacturer` / `ufs_version` / `current_gear` (U2b) and the MediaTek DRAM debugfs node (U1b).
- [ ] Enable Bluetooth; capture `dumpsys bluetooth_manager` plus an HCI snoop log with `LE Read Local Supported Features` and `Read Local Supported Commands` (U18).
- [ ] Open-sky `GnssStatus` / `GnssMeasurement` logging, or the bundled `YGPS` app, to demonstrate real L5/E5a/B2a tracking.
- [ ] `cat /sys/bus/i2c/drivers/tiny2c_usb-sensor/*/sensor_id` for the thermal module ID byte.
- [ ] NFC logcat during initialisation for the `HwVersion` byte.
- [ ] Camera EEPROM read at i2c `7-0051` for the main module and sensor ID (closes U3 and U4).
- [ ] `cat /sys/kernel/debug/gpio` for the ConnFem HWID levels (cosmetic - the conclusion will not change).

## 2. Instrumented bench tests

- [ ] Certified 20 V / 6 A PPS source with inline power logging and thermal monitoring, to measure real charging power and derating (U10b).
- [ ] Full metered charge/discharge cycle to settle the 8594 mAh versus 10600 mAh gap (U9b).
- [ ] Camera high-rate mode tests with temperature and current logging.
- [ ] Controlled OIS actuation to confirm which optical path moves - stay within actuator limits (U4).

## 3. Physical evidence

- [ ] FCC internal photographs, a teardown or repair documentation for the antenna and filter inventory (U8), cooling material stack (U21), fingerprint die (U15) and remaining passives (U24b). None was published at the time of the verification pass.
- [ ] Package markings for the main camera module, the LN2403 light driver and the ST21NFC part.
- [ ] IP and MIL test reports from Ulefone or the certifying laboratory (U22).

## Before any of the above

- [ ] Back up stock images, modem NV and calibration, camera EEPROMs, fingerprint/TEE data, and **`/mnt/vendor/nvcfg/infiray`** (the thermal module's per-unit calibration).
- [ ] Note that opening the phone voids the IP68/IP69K sealing.

## Closed by the verification pass

DRAM/UFS identity and health, main-camera identity, thermal detector, FM78100 role, ConnFem selection, battery topology, charging protocols, wireless charging (absent), haptics topology, Ilitek population, rear display, power-IC identities, ST21NFC family, GNSS configuration, camera stream configurations, eSIM (absent) and the hidden support-IC catalogue.
