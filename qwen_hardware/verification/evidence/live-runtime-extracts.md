# Live runtime extracts (primary evidence)

All from `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/`. **Read-only**; no phone was attached during this verification pass.

## ConnFem resolution (dmesg.txt)

```
[  216.645949] [btmtk_info] [InternalCmd] btmtk_intcmd_send_connfem_cmd
[  216.645958] [connfem][API]connfem_is_available: FEM is not available
[  216.645961] [connfem][API]connfem_epaelna_get_fem_info, Not support
[  216.645971] [connfem][API]connfem_epaelna_get_pin_info, Not support
[  216.645981] [connfem][API]connfem_epaelna_get_flags, Not support
[  216.646008] [btmtk_info] CONNFEM BTvid/pid == 0, ignore
```

Driver semantics (`connfem_dt_parser.c:340-342`, `connfem_cfg.c:419-420` in the matching MT6878 ConnFem source): `available = true` only when the resolved `fem_info.id != 0`. `nofem` carries empty `vid`/`pid`, so `id == 0`. `vendor/firmware/connfem.cfg` is **0 bytes**, so the config-file path cannot override the DT result.

## Pack gauge (dmesg.txt, SH366003 at i2c 9-0055)

```
[sh366003] fg_monitor_workfunc: RSOC=,79, Volt=,8397, Curr=,194, Temp=,375,
           SoH:94, cycnt:26, Rc:6713, FCC:8594, Vchg:8900, Ichg=9500, BatS:0x0080
[sh366003] sh_fg_get_batt_info: SafetyAlert=0x0000, SafetyStatus=0x0000, PFAlert=0x0000,
           PF=0x0000, Operation=0x0386, Charging=0x0410
[mt6375-chg] mt6375_dump_registers CC = 500mA, AICR = 500mA, MIVR = 4500mV, IEOC = 400mA, CV = 4450mV
```

## power_supply class (thermal-power.txt)

Complete list of supplies present: `3rd-gauge`, `battery`, `mtk-gauge`, `mtk-master-charger`, `mtk-mst-div-chg`, `mtk-mst-hvdiv-chg`, `mtk-slave-charger`, `mtk-slv-div-chg`, `mtk-slv-hvdiv-chg`, `primary_chg`, `sc-cp-master`, `sc-cp-slave`. **There is no `wireless` supply.**

```
battery:   VOLTAGE_NOW=8397000 uV   CONSTANT_CHARGE_VOLTAGE=4450 mV
           CHARGE_FULL_DESIGN=8594000 uAh   CHARGE_FULL=2946000   CHARGE_COUNTER=2327340
           CAPACITY=79  CYCLE_COUNT=26  TEMP=370  TECHNOLOGY=Li-ion
3rd-gauge: /sys/.../i2c-9/9-0055/power_supply/3rd-gauge  VOLTAGE_NOW=8397 CHARGE_FULL_DESIGN=8594
mtk-master-charger: USB_TYPE=[Unknown] SDP DCP CDP PD PD_PPS
sc-cp-master: /sys/.../i2c-11/11-0066/     sc-cp-slave: /sys/.../i2c-6/6-0067/
```

## Bus/driver bindings (buses.txt) - which driver actually claimed each device

```
0-0015  /sys/bus/i2c/drivers/hyn_ts        /sys/module/hynitron            BOUND
0-0041  <unresolved driver link>           "ilitek"                        NOT BOUND
0-0048  <unresolved driver link>           "chipone-tddi"                  NOT BOUND
6-0069  /sys/bus/i2c/drivers/sc851x        /sys/module/sc851x_charger      name "sc8510"
8-003c  /sys/bus/i2c/drivers/tiny2c_usb-sensor  /sys/module/yft_tiny2c_usb  node name "fm78100"
9-0055  /sys/bus/i2c/drivers/sh366003      /sys/module/sh366003_fg
11-0029 /sys/bus/i2c/drivers/wl2864c       /sys/module/custom_ldo_wl2868
spi0.0  /sys/bus/spi/drivers/spi_tiny_lcd_co5300  /sys/module/spi_tiny_co5300_lcd
spi1.0  /sys/bus/spi/drivers/madev         /sys/module/microarray_fp_tee
spi3.0  /sys/bus/spi/drivers/fts_ts        /sys/module/focaltech_touch_spi_ft3680
```

`vendor_dlkm/lib/modules/` ships `hynitron.ko`, `focaltech_touch_spi_ft3680.ko`, `spi_tiny_co5300_lcd.ko`, `dw9781c.ko`, `main_vcm.ko`, `main2_vcm.ko`, `main3_vcm.ko`, `main4_vcm.ko`, `sub_vcm.ko`, `yft_tiny2c_usb.ko`, `connfem.ko`, `custom-ldo-wl2868.ko`, `aw36515.ko`, `aw36518.ko`, `aw36518_v2.ko`, `aw883xx_driver.ko` — **and no Ilitek or ChipOne-TDDI module at all**.

## Camera static metadata (camera-media.txt)

```
[00] BACK  hasFlashUnit:1  SENSOR_DRVNAME_IMX989_MIPI_RAW
[01] FRONT hasFlashUnit:0  SENSOR_DRVNAME_S5KJN1_MIPI_RAW
[02] BACK  hasFlashUnit:1  SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW
[03] BACK  hasFlashUnit:1  SENSOR_DRVNAME_OV64B_MIPI_RAW
```

| cam | physicalSize (mm) | pixelArraySize | aperture | focal | OIS | RAW16 size | max JPEG/YUV |
|---|---|---|---|---|---|---|---|
| 0 IMX989 back main | 13.107 x 9.830 | 4096 x 3072 | f/1.9 | 23 mm | `[0]` | **4096 x 3072** | 8192 x 6144 (incl. 7680x4320) |
| 1 S5KJN1 front | 4.640 x 3.490 | 8160 x 6144 | f/2.45 | 25 mm | `[0]` | **4080 x 3072** | 8192 x 6144 |
| 2 S5KJN1MAIN2 back UW | 13.107 x 9.830 (copied) | 8160 x 6144 | f/2.2 | 16 mm | `[0]` | **4080 x 3072** | 8192 x 6144 |
| 3 OV64B back night | 6.500 x 4.890 | 4624 x 3472 | f/1.79 | 26 mm | `[0]` | **4624 x 3472** | 9216 x 6912 |

`availableStreamConfigurations`: 215/215/211/211 rows respectively, over formats RAW16(0x20), BLOB(0x21), IMPLEMENTATION_DEFINED(0x22), YUV_420_888(0x23), 0x36, 0x32315659 ("YV12"), plus 42-43 HEIC sizes each. `availableMaxDigitalZoom = 4.0` (cam0). `availableVideoStabilizationModes = [0,1,2]` for cam0/cam1, `[0]` for cam2/cam3.

## GNSS vendor configuration (vendor/etc/MNL_Config.xml)

```
GnssMode      setting=10   -> "GP+GL+GA+BD+NI"  (GPS + GLONASS + Galileo + BeiDou + NavIC)
L1Only        setting=0    -> multi-band enabled
L5Test        setting=1    -> use GPS L5 regardless of health flag
DisableSignal setting=0    -> B1C, GPS L1C, QZSS L1C, E5B, B2B all enabled
DCB           Chip=6637 -> L5_DCB_GPS/QZSS/CNSS/GALILEO = -8.16,-8.34,-10.82,-9.17 (calibrated)
              Chip=6686 -> alternate calibration set
CAIC          L1 = 1 560 000 000 Hz ; L5 = 1 170 000 000 Hz
GNSSPower     singlebandTracking 51.9 / multibandTracking 100.2 mW
OSNMA         setting=1    -> Galileo OSNMA authentication enabled
```

## NFC configuration (vendor/etc/libnfc-hal-st.conf, st21nfc_conf.txt)

```
NCI_HAL_MODULE="nfc_nci.st21nfc";  STNFC_FW_BIN_NAME="st21nfc_fw7.bin"
OFFHOST_ROUTE_UICC={81,83}   OFFHOST_ROUTE_ESE={82}   OFF_HOST_ESE_PIPE_ID=0x5E
st21nfc_conf.txt: CustomA + CustomB RF parameter blobs, DPC table, ANTENNA CONFIG,
                  UICC CONFIG, SE CONFIG, IOT CONFIG, NFCC CONFIG, config CRC 4646
```

`vendor/lib64/nfc_nci.st21nfc.st.so` contains handlers for ST21NFC (`st21nfc_fw*.bin`), ST54J (`st54j_fw.bin`), ST54K and ST54L; only the ST21NFC path is configured for this board.

Declared platform features: `android.hardware.nfc`, `.nfc.hce`, `.nfc.hcef`, `.nfc.uicc`, and `android.hardware.se.omapi.uicc` **only** — no `se.omapi.ese`, no `android.hardware.telephony.euicc`.

## Thermal-imaging stack (stock system partition)

```
system/app/M170infisens/M170infisens.apk      arm64 libs:
system/app/M170infDlp/M170infDlp.apk            libAC020sdk.so, libadvirtempac020.so, libircmd020.so,
                                                libomniircamera020.so, libdualuvccamera020.so,
                                                libusbuvccamera020.so, libircam.so, libirutilssdk.so,
                                                libdualcalibration.so, libcolormapping.so, libMNN*.so
string evidence: "infiray", "mini640", "tiny2c", "tiny1c", "MINI225 MINI238 MINI264 MINI640", "ASIC"
vendor/etc/init/hw/init.yft.rc:  mkdir /mnt/vendor/nvcfg/infiray   ("# YFT.liuyang InfiRay")
                                 mkdir /mnt/vendor/nvcfg/FLIR      (other project variant)
                                 /sys/bus/spi/drivers/spidev/tiny1c_power_enable ("# add InfiSense")
                                 /sys/bus/i2c/drivers/fm78100-sensor/{chip_power,chip_enable,
                                     chip_exist,mems_temp,ntc_temp,objs_temp}
vendor_dlkm yft_tiny2c_usb.ko strings: "gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d",
                                 "read sensor-id fail", dev_attr_sensor_id, dev_attr_tiny2c_usb_mode
```

## Snapshot provenance (identity.txt / packages.txt)

```
[ro.build.fingerprint]     Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274:user/release-keys
[ro.build.display.id]      BP4A.251205.006 release-keys
[ro.lineage.display.version]  LieppOS-23-20260830-VANILLA-EROFS-GSI
identity.txt line 1        uid=0(root) ... context=u:r:ksu:s0        (KernelSU root)
packages.txt               org.lineageos.setupwizard, LineageSettingsProvider, ...
                           zero Ulefone/YFT/thermal packages
```
