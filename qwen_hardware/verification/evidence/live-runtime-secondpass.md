# Second-pass live-snapshot evidence (read-only, frozen capture 2026-08-31 11:56)

Source: `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/` (the capture taken under the
LieppOS GSI - see `../findings/00-snapshot-provenance-correction.md`; vendor/kernel/DT content was
untouched by the GSI, so kernel- and bus-level facts are stock facts).

No ADB device was attached during this verification pass (`adb devices` empty), so **no new live
query was executed**; everything below is a deeper re-read of the frozen capture.

---

## L21 - `buses.txt` parsed with correct `readlink -f` semantics (decisive population table)

`buses.txt` was produced per device block as `readlink -f <dev>/driver`, `readlink -f <dev>/driver/module`,
the bound driver name and the `of_node` name/compatible. `readlink -f` prints the canonical path
**even when the final component does not exist**, so a block whose second line still ends in
`/driver` means **no driver symlink exists -> the client is NOT bound**, while a block that resolves to
`/sys/bus/<bus>/drivers/<name>` **is bound**. Pass 1 read these blocks as "driver name present" and
therefore over-counted bound clients; the corrected parse of all 53 blocks is the table below.

### Bound (populated and driven)

| device | driver | `/sys/module` | of_node / compatible | reading |
|---|---|---|---|---|
| `i2c 0-0015` | `hyn_ts` | `hynitron` | `hynitron,hyn_ts` | rear sub-display digitizer |
| `i2c 11-0029` | `wl2864c` | **`custom_ldo_wl2868`** | `will,wl2864c_pmu` | bound WL2864C/WL2868C-family camera LDO PMIC; module name and DT's dual ID table do **not** reveal which die revision is fitted |
| `i2c 11-0045` | `leds-rgb-aw2013` | `leds_rgb_aw2013` | `awinic,rgb,aw2013` | Awinic AW2013 RGB notification/warning LED |
| `i2c 11-0066` | `sc8571` | `sc8571_charger` | `sc,sc8571-master` | SC8571 primary charge pump |
| `i2c 12-0063` | `aw36518_v2` | `aw36518_v2` | `mediatek,aw36518_v2` | Awinic AW36518 flash/IR LED driver #2 |
| `i2c 2-000d` | `main4_vcm` | `main4_vcm` | `camera-af-main-four` | AF VCM 4 |
| `i2c 2-0010` | `imgsensor` | `imgsensor` | `sensor2` | camera sensor 2 |
| `i2c 2-0050` | `mediatek,camera_eeprom` | `camera_eeprom_v4l2` | `camera-eeprom2` | OTP EEPROM 2 |
| `i2c 4-000b` | `main2_vcm` | `main2_vcm` | `camera-af-main-two` | AF VCM 2 |
| **`i2c 4-000e`** | **`dw9781c`** | **`dw9781c`** | `camera-ois-main` | **OIS actuator driver bound** |
| `i2c 4-0010` / `4-0020` | `imgsensor` | `imgsensor` | `sensor1` / `sensor4` | camera sensors 1 and 4 (same bus as the OIS actuator) |
| `i2c 4-0050` / `4-0051` | `mediatek,camera_eeprom` | `camera_eeprom_v4l2` | eeprom1 / eeprom4 | OTP EEPROMs |
| `i2c 5-0034` | `mt6375` | `mt6375` | `mediatek,mt6375` | MT6375 charger/PMIC |
| `i2c 6-0008` | `st21nfc` | `st21nfc` | `st,st21nfc` | NFC front end |
| `i2c 6-0034` | `speaker_amp` | `mtk_sp_spk_amp` | `mediatek,speaker_amp` | smart-amp receiver speaker |
| `i2c 6-003e` | `I2C_LCD_BIAS` | `mediatek_drm_gateic` | `mediatek,i2c_lcd_bias` (`lcd_ocp2131`) | Orient-Chip OCP2131 panel bias |
| `i2c 6-0063` | `aw36515` | `aw36515` | `mediatek,aw36515` | Awinic AW36515 dual flash LED driver |
| `i2c 6-0067` | `sc8571` | `sc8571_charger` | `sc,sc8571-slave` | SC8571 secondary charge pump |
| `i2c 6-0069` | `sc851x` | `sc851x_charger` | `sc,sc8510` | SC8510 reverse-path pump |
| `i2c 7-000a` | `main_vcm` | `main_vcm` | `camera-af-main` | AF VCM 1 (main module bus) |
| `i2c 7-0020` | `imgsensor` | `imgsensor` | `sensor0` | main camera sensor |
| `i2c 7-0051` | `mediatek,camera_eeprom` | `camera_eeprom_v4l2` | `camera-eeprom0` | OTP EEPROM 0 |
| `i2c 8-003c` | `tiny2c_usb-sensor` | `yft_tiny2c_usb` | `mediatek,tiny2c_usb` (`fm78100`) | thermal-module power/ID endpoint (see U6) |
| `i2c 8-0063` | `aw36518` | `aw36518` | `mediatek,aw36518` | Awinic AW36518 flash/IR LED driver #1 |
| `i2c 9-0055` | `sh366003` | `sh366003_fg` | `sh,sh366003` | SinhMicro SH366003 pack fuel gauge |
| `spi0.0` | `spi_tiny_lcd_co5300` | `spi_tiny_co5300_lcd` | - | rear 1.04" AMOLED DDIC |
| `spi1.0` | `madev` | `microarray_fp_tee` | - | Microarray fingerprint (SPI, TEE) |
| `spi3.0` | `fts_ts` | `focaltech_touch_spi_ft3680` | - | main-panel touch controller |

### Present in DT but NOT bound (no driver symlink)

`0-0041` `tchip,ilitek` - `0-0048` `chipone-tddi` - `5-0018` `richtek,rt5133` -
`5-0075` + `6-0075` `richtek,rt6160[-vbb]`.

### Bound to the MediaTek placeholder driver `dummy` (reserved addresses, not components)

`5-001a`, `5-003f`, `5-004a`, `5-004e`, `5-0064`.

---

## L22 - MTK CameraProvider runtime enumeration (`camera-media.txt` lines 31-45)

```
== Camera Provider HAL android.hardware.camera.provider.ICameraProvider/internal/0-0 (v2.0, remote) static info: 4 devices: ==
  Physical Devices: # 4
    [03] -> orientation(wanted/setup)=(270/90 ) BACK  hasFlashUnit:1 SENSOR_DRVNAME_OV64B_MIPI_RAW
    [02] -> orientation(wanted/setup)=(270/90 ) BACK  hasFlashUnit:1 SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW
    [01] -> orientation(wanted/setup)=(270/270) FRONT hasFlashUnit:0 SENSOR_DRVNAME_S5KJN1_MIPI_RAW
    [00] -> orientation(wanted/setup)=( 90/90 ) BACK  hasFlashUnit:1 SENSOR_DRVNAME_IMX989_MIPI_RAW
```

The `SENSOR_DRVNAME_*` string is the driver name the probe matched **on this individual handset**, i.e.
the strongest available local evidence for the fitted main die (see `../findings/camera-main-identity.md`).

Per-camera static metadata actually published by the vendor HAL (tag value taken from the line
immediately following each tag inside each `Camera HAL device .../internal/N static information` block):

| HAL id | runtime DRVNAME | facing | `sensor.info.pixelArraySize` | `sensor.info.physicalSize` (mm) | implied pitch | `lens.info.availableOpticalStabilization` |
|---:|---|---|---|---|---|---|
| 0 | IMX989 | BACK | 4096 x 3072 | 13.107 x 9.830 (diagonal 16.4 mm = 1-inch class) | 3.20 um (= IMX989 0.8 um, 4-in-1 binned) | `[0]` = OFF only |
| 1 | S5KJN1 | FRONT | 8160 x 6144 | 4.640 x 3.490 (diagonal 5.81 mm = 1/2.74", JN1 die) | 0.57 um | `[0]` |
| 2 | S5KJN1MAIN2 | BACK | 8160 x 6144 | **13.107 x 9.830** (same 1-inch-class die geometry as cam 0) | 1.60 um | `[0]` |
| 3 | OV64B | BACK | 4624 x 3472 | 6.500 x 4.890 (diagonal 8.14 mm) | 2.81 um (= OV64B 0.7 um, 4-in-1 binned) | `[0]` |

Second-pass reading:

* `LENS_INFO_AVAILABLE_OPTICAL_STABILIZATION = [OFF]` on **all four** logical cameras - the stock HAL
  never advertises OIS, corroborating `../findings/ois-vcm-lens-mapping.md`.
* Camera 2 publishes a **JN1 instance name with a 50 MP, 16 mm-diagonal die geometry**, and camera 1
  publishes a 32 MP-class die with a 50 MP array. `android.lens.aperture` and `android.lens.focalLength`
  are **absent from every block**. These vendor static-metadata blocks are therefore internally
  inconsistent and must not be used as silicon proof for the secondary modules - only the DRVNAME and
  the cam-0 die geometry are self-consistent.

## L23 - input subsystem (`displays.txt`, `dmesg.txt`)

```
Input Reader State (Nums of device: 6):
  Device 6: hyn_ts    SysfsRootPath /sys/devices/platform/soc/11c20000.i2c/i2c-0/0-0015
                      raw X 0..340, Y 0..340  -> RawToDisplay SCALE X 3.1672 / Y 7.0381 -> 1080 x 2400
  Device 4: madev     (fingerprint sensor registered as an input device)
  Device 3: yft-gpio-keys , Device 2: mtk-pmic-keys , Device 5: mt6878-mt6369 Headset Jack
EventHub: 3: fts_ts  classes KEYBOARD|TOUCH|TOUCH_MT  path /sys/devices/platform/soc/11013000.spi3/spi_master/spi3/spi3.0
dmesg: [FTS_TS/I]fts_check_fw_normal:TP Ready,Read ID=0x56
```

Main display = one and only one SurfaceFlinger display (`DisplayDeviceInfo{"Built-in Screen": ... 1080 x 2400,
modeId 3, renderFrameRate 60.0}`, density 480, xDpi 397.6 / yDpi 393.3, `pnpId=MTK`, name `MTKDEV`);
the rear CO5300 panel never appears as a display, only as its own digitizer `hyn_ts` (native 340 x 340)
plus vendor sysfs. The FocalTech SPI controller is alive and reports firmware ID `0x56`.

## L24 - thermal / cooling devices actually exposed (`thermal-power.txt`)

```
CoolingDevice{mValue=0, mType=3, mName=devfreq-13000000.mali}
CoolingDevice{mValue=0, mType=6, mName=charger-cooler}
CoolingDevice{mValue=0, mType=6, mName=flashlight_cooler}
CoolingDevice{mValue=0, mType=6, mName=lcd-backlight}
CoolingDevice{mValue=0, mType=6, mName=wifi-cooler}
```

No fan / TEC / BLDC / tachometer node anywhere: `dmesg.txt` has zero matches for
`fan|tec|motor|pwm-fan|nide|bldc`, and the live DT contains only `backlight-cooler`, the three LED
drivers' `#cooling-cells`, and `mali@13000000` as cooling providers. Corroborates
`../findings/cooling.md` (passive + electrical throttling only).

## L25 - telephony / eSIM runtime state (`telephony.txt`)

```
Euicc enabled=false
SubscriptionInfoInternal: id=1 iccId=8937... simSlotIndex=0 portIndex=0 isEmbedded=0 isRemovableEmbedded=0 ...
```

Independent runtime corroboration of `../findings/esim-euicc.md` (no eUICC).

## L26 - IR path and HAL surface (`services-processes.txt`, `packages.txt`, DT)

DT ships an enabled `/irtx-pwm` node (`mediatek,irtx-pwm`, `pwm-ch = <0>`, supply `mt6369_vio28`,
symbol `irtx_pwm`) and a pinctrl group `ln2403_pwm`. The captured binder service is the AOSP
`android.hardware.ir-service.example` wrapper, but later stock-ELF/property closure proves that it loads
shipped MediaTek backend `consumerir.common.so` via `ro.hardware.consumerir=common`; see
`../findings/ir-blaster.md`. NFC is served by `android.hardware.nfc-service-st`, lights by
`android.hardware.lights-service.mediatek`, vibrator by `android.hardware.vibrator-service.mediatek`, and
face unlock by the unrelated AOSP example `android.hardware.biometrics.face-service.example`.

## L27 - fingerprint device nodes (`fingerprint.txt`)

```
Can't find service: fingerprint
crw-rw-rw- 1 system system u:object_r:mafinger_device:s0     498,  0 /dev/madev0
crw-rw---- 1 root   system u:object_r:tkcore_client_device:s0 10,113 /dev/tkcore_fp
```

## L28 - sensor HAL physical inventory (`sensors.txt`, 22 sensors, 5 physical)

| sensor | vendor string | part |
|---|---|---|
| `icm4n607_acc`, `icm4n607_gyro` | `iven_sense` | TDK InvenSense **ICM-4x607** family 6-axis |
| `mmc5603` | `memsic` | MEMSIC **MMC5603** 3-axis magnetometer |
| `stk3a5x_als`, `stk3a5x_ps` | `sensortek` | Sensortek **STK3A5x** light + proximity |
| `spl07` | `goer` | Goertek **SPL07** barometer |

Remaining 17 entries are MTK virtual/fused sensors (`orientation`, `gravity`, `linear_acc`, `rot_vec`,
`game_rotvec`, `uncali_*`, `significant`, `tilt`, `wake`, `dev_orient`, `step_*`). No hall-effect,
no RGB-light and no sub-display gesture sensor is exposed through the HAL.
