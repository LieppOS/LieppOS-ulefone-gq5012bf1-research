> **Pass-2 pointer (2026-09-08).** First-pass working material. Where anything here conflicts with `../final/` or `../verification/findings/`, the verification pass wins. Two blanket corrections apply: the 2026-08-31 capture ran a **LieppOS GSI**, so its framework-level observations are not stock Ulefone behaviour; and `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this board's bill of materials.

# Component candidates vs physically installed — GQ5012BF1

Statuses: `ACTUALLY INSTALLED` · `ALTERNATE FACTORY VARIANT` · `SUPPORTED BY SOFTWARE ONLY` ·
`FALLBACK DRIVER` · `DEAD/UNUSED SUPPORT` · `UNKNOWN`.

Software support ≠ presence. Driver/DT/firmware/HAL existence alone never promotes a candidate to
`ACTUALLY INSTALLED`.

| # | Subsystem | Candidate (origin of evidence) | Installed? | Status | Deciding evidence |
|---:|---|---|---|---|---|
| 1 | Main SoC | MediaTek MT6878(T) / Dimensity 7400 | YES | ACTUALLY INSTALLED | props, connsys chipid 0x6878, ISP DB, official spec |
| 2 | GPU | Arm Mali-G615 MC2 | YES | ACTUALLY INSTALLED | `ro.hardware.vulkan=mali`, `vendor.mali_platform=mediatek`, SoC spec |
| 3 | NPU | MediaTek APU/NPU 655 + VDSP + TPU | YES | ACTUALLY INSTALLED | thermal zones `npu`, `tpu`, `sys-therm*`, vendor APU HAL |
| 4 | Modem | MTK integrated NR17 (MOLY) | YES | ACTUALLY INSTALLED | baseband string, telephony/RIL, NV partitions |
| 5 | Connex | MT6637 (A-die `ADIE6637`, D-die `connsys_d_die_cfg_mt6878`) | YES | ACTUALLY INSTALLED | dmesg chip-ID logs, `connsys_wifi`/`connsys_bt` services |
| 6 | Main panel | YFT/YuFeiTong VTDR6115 AMOLED DDIC | YES | ACTUALLY INSTALLED | live DT `yft-lcm-vtdr6115-drv`, DSI link contract, 45-write init |
| 7 | Main panel bias | Wuxin OCP2131 LCD bias (`lcd_ocp2131`) | YES | ACTUALLY INSTALLED | bound `mediatek_drm_gateic` @`6-003e` |
| 8 | Main panel gate IC | `chipone-tddi` (`chipone-tddi`) @`0-0048` | PROBES | ACTUALLY INSTALLED (gate/TDDI I2C control path) | live I2C binding via `mediatek_drm_gateic` |
| 9 | Main touch | FocalTech FT3680 (SPI, in-module FW) | YES | ACTUALLY INSTALLED | `spi3.0` → `fts_ts`, 3-record `module_list` with only record 0 populated |
| 10 | Touch alt | Ilitek (`tchip,ilitek`) @`0-0041` | PROBES | UNKNOWN (alt/second panel touch or unpopulated variant) | live I2C binding; no userspace consumer found yet |
| 11 | Rear mini panel | CO5300 (`spi_tiny_lcd_co5300`) @`spi0.0` | YES | ACTUALLY INSTALLED | live SPI binding, `tinylcd_hal` service, YftMiniScreen.apk |
| 12 | Rear mini touch | Hynitron `hyn_ts` @`0-0015` | YES | ACTUALLY INSTALLED | live I2C binding, `tinydisplay_touch_daemon` |
| 13 | CAM0 rear main | Sony IMX989 (`SENSOR_DRVNAME_IMX989_MIPI_RAW`) | YES | ACTUALLY INSTALLED (this unit) | HAL driver name + 13.107×9.830 mm array + 4096×3072 binned mode |
| 14 | CAM0 alt | Samsung S5KGN1 (marketing sheet) | NOT on this unit | ALTERNATE FACTORY VARIANT / mislabel | official spec sheet conflicts with HAL — see contradictions.md#C1 |
| 15 | CAM1 front | Samsung S5KJN1 | YES | ACTUALLY INSTALLED | HAL driver name + aperture + 8160×6144 |
| 16 | CAM2 ultra-wide | Samsung S5KJN1 (MAIN2 tuning entry) | YES | ACTUALLY INSTALLED | HAL driver `S5KJN1MAIN2`, f/2.2, 117.3° |
| 17 | CAM3 night vision | OmniVision OV64B | YES | ACTUALLY INSTALLED | HAL driver + 9216×6912 max + 1/2″ array |
| 18 | Camera AF | DW9718/DW9828-class VCMs (`main_vcm`, `main2_vcm`, `main4_vcm`) | YES (3×) | ACTUALLY INSTALLED | I2C `7-000a`, `4-000b`, `2-000d` |
| 19 | Camera OIS | Dahua/Dongwoon DW9781C @`4-000e` | YES | ACTUALLY INSTALLED, STOCK-DISABLED | probe + HAL `availableOpticalStabilization=[0]` on all 4 sensors |
| 20 | Camera EEPROM | 4× `mediatek,camera_eeprom` (`7-0051`,`4-0050`,`2-0050`,`4-0051`) | YES (4) | ACTUALLY INSTALLED | live I2C binding, `camera_eeprom_v4l2` |
| 21 | Thermal imager | ThermoVue T2 module over USB (`yft_tiny2c_usb`) + `fm78100` I2C endpoint | YES | ACTUALLY INSTALLED | official spec + APK + driver + I2C node |
| 22 | Flash/torch | Awinic AW36515 (dual-channel) @`6-0063` | YES | ACTUALLY INSTALLED | probe, DT `flash-externel` = GPIO 116 |
| 23 | IR/aux light | Awinic AW36518 (single channel) @`8-0063` | YES | ACTUALLY INSTALLED | probe |
| 24 | Warning light | Awinic AW36518_V2 @`12-0063` | YES | ACTUALLY INSTALLED | probe + `YftRedBlueLight` app |
| 25 | Notification LED | Awinic AW2013 RGB @`11-0045` | YES | ACTUALLY INSTALLED | chip-ID `0x33`, GPIO 188 enable, `/sys/class/leds/{red,green,blue}` |
| 26 | Smart PA | Awinic AW88394 (chip-ID `0x2049`) @`6-0034` | YES | ACTUALLY INSTALLED | ACF `dev_name=aw88394`, multi-bin `chip_type` |
| 27 | Smart PA alt | AW88390/2066 & 2183 ID tables in the same module | NO evidence | SUPPORTED BY SOFTWARE ONLY | driver accepts `0x2066`, `0x2183`; runtime ID is `0x2049` |
| 28 | Fuel gauge 1 | MediaTek MT6375 @`5-0034` (gauge + TCPC role) | YES | ACTUALLY INSTALLED | `mtk-gauge` binding; separate `tcpc_mt6375.ko` |
| 29 | Fuel gauge 2 | Sinhmicro SH366003 @`9-0055` (`3rd-gauge`) | YES | ACTUALLY INSTALLED | probe + power_supply dump |
| 30 | Charge pump | Scrcotech/SGMicro SC8571 master @`11-0066`, slave @`6-0067` | YES (2) | ACTUALLY INSTALLED | `sc,sc8571-master` / `sc,sc8571-slave` |
| 31 | Charger/adapter mux | SC851x (`sc,sc8510`) @`6-0069` | YES | ACTUALLY INSTALLED | `sc851x_charger` probe |
| 32 | PMIC (rail) | Crichtek RT5133 @`5-0018`; RT6160 @`5-0075` (VBB) and `6-0075` | YES (3) | ACTUALLY INSTALLED | live I2C bindings with richtek compatibles |
| 33 | Camera/LDO PMIC | WillSemi WL2864C (`will,wl2864c_pmu`) @`11-0029` | YES | ACTUALLY INSTALLED | `custom_ldo_wl2868` probe |
| 34 | Audio codec | MT6369-class on-chip/PMIC audio (ALSA card `mt6878-mt6369`) | YES | ACTUALLY INSTALLED (integration path TBD) | ALSA card + jack device |
| 35 | NFC | STMicro ST21NFC @`6-0008` (+ `st21nfc_fw.bin`, `_fw7.bin`) | YES | ACTUALLY INSTALLED | probe + firmware + HAL |
| 36 | Fingerprint | Madev capacitive SPI die via `microarray_fp_tee` (`/dev/madev0`, `/dev/tkcore_fp`) | YES | ACTUALLY INSTALLED | SPI1 binding + TEE nodes + official spec |
| 37 | IMU | IvenSense ICM-4N607 | YES | ACTUALLY INSTALLED | sensor HAL vendor `iven_sense`, 12.5–400 Hz |
| 38 | Magnetometer | Memsic MMC5603 | YES | ACTUALLY INSTALLED | sensor HAL + FIFO sizes |
| 39 | ALS/PS | Sensortek STK3A5X | YES | ACTUALLY INSTALLED | two sensor entries from one part |
| 40 | Barometer | Goermicro SPL07 | YES | ACTUALLY INSTALLED | sensor HAL vendor `goer` |
| 41 | Hall / SAR / humidity / UV / RGB-with-IR alt | not present in any dump | NO | NOT PRESENT (no evidence) | absent from 22-sensor list |
| 42 | RF FEM (Wi-Fi/BT) | catalog: `wlan7207h/c`, `qm42195`, `qm45197`, `sky85320`, `sky85720`, `sky85732`, `mxd7751s`, `rtc7620` | HWID-selects | UNKNOWN (10-entry catalog; runtime HWID unrecovered) | DTBO frag 39 `parts[24]`, HWID GPIOs 131/132/92 |
| 43 | NFC eSE | SIM1/SIM2 UICC as selectable SE | YES (routing) | ACTUALLY INSTALLED (route-capable) | `mtk_secure_element_hal_service`, SWI/SIM selection |
| 44 | Wireless charging | none | NO | NOT PRESENT | `onWirelessCharger=false`, no WPC driver/firmware anywhere |
| 45 | Active cooling | fan/pump | NO | NOT PRESENT | no fan service/cooling device besides `charger-cooler`, `LCD-backlight`, `wlan`, `flashlight` |
