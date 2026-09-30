# Live /proc/device-tree extracts (primary evidence)

Source archive: `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar` (10,504 nodes/properties, captured 2026-08-31). This is the **running, post-DTBO device tree of the real phone**, so it reflects fitted board configuration, not a build-time source file.

## Identity

```
/model                 = "MT8873"
/model-external-name   = "MT6878V/TZA"
/model-part-name       = "MT6878V/TZA"
/memory@40000000/reg   = <0x0 0x40000000 0x4 0x0>      # base 0x40000000, size 0x4_0000_0000 = 16 GiB
```

## /chosen/bootargs (bootloader-detected memory + storage + panel)

```
... ufshcd_core.poll_queues=0 ... bootopt=64S3,32N2,64N2
lpddr_used_name=MT512GBCAV8U31 flash_type=12 lpddr_used_index=0
PreEOLInfo = 0x1 LifeTimeEstA = 0x1 LifeTimeEstB = 0x1
lcmname=yft_vtdr6115_fhdp_dsi_cmd_hx_dphy_667_ky_lcm_drv
charger_boot_switch=0 ...
```

`/chosen/atag,videolfb` = `yft_vtdr6115_fhdp_dsi_cmd_hx_dphy_667_ky_lcm_drv`.

## connfem (Wi-Fi/BT front-end selection)

```
compatible = "mediatek,mt6878-connfem";
epa-elna-mtk { hwid { gpio = <0x89 0x83 0x0  0x89 0x84 0x0  0x89 0x5c 0x0>; };   # pinctrl GPIO 131,132,92
               parts = <96 bytes = 12 phandle pairs>; }
pinctrl-names = "wlan7207h-wlan7207c | qm42195-qm45197 | sky85320-sky85720 |
                 mxd7751s-mxd7751s | nofem-sky85732 | nofem-qm45197 | rtc7620-nofem";
```

Decoded `parts` table (index -> 2.4 GHz part + 5/6 GHz part):

```
0: nofem   + nofem       4: sky85320 + sky85720    8: nofem    + sky85732
1: nofem   + nofem       5: sky85320 + sky85720    9: nofem    + sky85732
2: nofem   + nofem       6: qm42195  + qm45197    10: nofem    + qm45197
3: mxd7751s+ mxd7751s    7: wlan7207h+ wlan7207c  11: rtc7620  + nofem
```

Three HWID GPIOs address indices 0-7 only; indices 8-11 are unreachable reference entries.

## Charging / battery topology

```
/charger:  algorithm-name="Basic"; battery-cv=4450000 uV; max-charger-voltage=12500000 uV;
           ac-charger-current=2100000 uA; vbus-sw-ovp-voltage=22000000 uV; JEITA t0..t4 tables
/hvbp   :  vbat-cv=8900 mV; vbat-threshold=8200; start-vbat 7100..8750; ita-level 2500..2000 mA;
           vta-cap-max=11000 mV; support-ta = "pca_ta_pps","pd_adapter"
/pe5p   :  vbat-cv=8900; ita-level=<5000 4500 3750 3000> mA; vta-cap 14000..20000 mV
/pe5    :  ita-level-dual=<6000 4500 3400 2000> mA; vta-cap 13600..20000 mV     -> 6 A x 20 V = 120 W
/pd-adapter: adapter-name="pd_adapter"; nr-port=1
mt6375@34/chg : cv=4450 mV; ichg=2000; aicr=500; ieoc=400; mivr=4400; vbus-ov=14500 mV
mt6375@34/mtk-gauge : battery0-profile-t1 max cell voltage 4448.4 mV (100x4 OCV table),
                      battery1 alternate profile max 4322.0 mV, bat_type=0
```

**No wireless-charging node exists anywhere in the tree** (verified by full-tree byte scan for
`wireless|wlc|mt5786|nu16|cps4|stwlc|idtp|rx1619|ufcs`; only false positives in `met/mcupm-rts-header`).

## PMIC / power tree (SPMI)

```
soc/spmi@1cc04000/pmic@4        compatible "mediatek,mt6363"   (main PMIC, auxadc, pinctrl, keys)
soc/spmi@1cc04000/second_pmic@5 compatible "mediatek,mt6369"   (regulators, accdet, mt6369codec)
soc/spmi@1cc04000/mt6319@6      compatible "mediatek,mt6319"   (external buck)
soc/spmi@1cc04000/mt6685_mfd    compatible "mediatek,mt6685"   (clkbuf, consys, RTC)
thermal-ntc1/2/3/6              compatible "mediatek,mt6685-tia-ntc"   (4 board NTC channels)
```

## Haptics

```
/regulator-vibrator: compatible="regulator-vibrator"; label="vibrator";
                     min-volt=2200000 uV; max-volt=3500000 uV;
                     vib-supply -> second_pmic@5/regulators/vibr  (mt6369_vibr, 1.2-3.5 V,
                     regulator-enable-ramp-delay = 680 us)
```

No dedicated haptic driver IC node exists on any bus.

## Audio jack / FM

```
second_pmic@5/accdet: compatible="mediatek,mt6369-accdet"; status="okay";
                      headset-three-key-threshold=<0 80 220 400>;
                      headset-four-key-threshold=<0 58 121 192 400>;
                      gpio-accdet-fm-switch = <137 195 0>
/fm      : compatible="mediatek,fm"; family-id=0x6983; host-id=0x6878; conn-id=0x205
/fmradio : compatible="mediatek,fmradio"; fm_lna_gpio=<0x89 0x48 0x0>; status="okay"
/irtx-pwm: compatible="mediatek,irtx-pwm"; pwm-supply="mt6369_vio28"
```

## Cameras

```
i2c@11e02000 (i2c-7): sensor0@0x20  sensor-names = imx989_mipi_raw, s5kgm2sp_mipi_raw,
                                                   imx989cts_mipi_raw, s5kgn1sp_mipi_raw
                      pinctrl adds oisvdd_off/oisvdd_on
                      camera-eeprom0@0x51, camera-af-main@0x0a (mediatek,main_vcm)
i2c@11c23000 (i2c-4): sensor1@0x10  sensor-names = s5kjn1_mipi_raw, ov32b40_mipi_raw, s5kjn1cts_mipi_raw
                      sensor4@0x20  sensor-names = ov64b_mipi_raw  (pinctrl adds oisen_off/oisen_on)
                      camera-eeprom1@0x50, camera-eeprom4@0x51,
                      camera-af-main-two@0x0b (main2_vcm), camera-ois-main@0x0e (mediatek,dw9781c)
i2c@11c22000 (i2c-2): sensor2@0x10  sensor-names = s5kjn1main2_mipi_raw
                      camera-eeprom2@0x50, camera-af-main-four@0x0d (main4_vcm)
```

## Touch / displays

```
spi3@11013000/focaltech@39   "focaltech,fts"   display-coords=<0 0 1080 2400>, 10 touch, 6 MHz
spi0@11010000/tiny_lcd       "hxytech, spi_tiny_lcd"  60 MHz, dc/reset/te/1v8/2v8 GPIO + tiny_lcd_adc
i2c@11c20000/hynitron@15     "hynitron,hyn_ts" display-coords=<340 340>, max-touch-number=<1>
i2c@11c20000/ilitek@41       "tchip,ilitek"    irq-gpio 7 / reset-gpio 6  (SAME pins as focaltech@39)
i2c@11c20000/chipone_tddi@48 "chipone-tddi"    irq-gpio 7 / reset-gpio 6, x-res 1080, y-res 2460
spi1@11011000/fingerprint@0  "mediatek,madev_finger" 8 MHz, vfp-supply
/fingerprint                 "mediatek,goodix-fp"   (no reg/bus - vestigial)
/ft_fingerprint              "focaltech,fp"         (no reg/bus - vestigial)
```

## Other vendor nodes

```
/yft_camplight    leds-red-gpio, leds-blue-gpio, leds-power-gpio,
                  ln2403-en-gpio, ln2403-power-gpio; pinctrl "ln2403_pwmon/pwmoff_high/pwmoff_low"
/yft_tiny2c_usb   tiny2c_usb_vdd_1v8, tiny2c_usb_vdd_3v3, tiny2c_usb_vddio_3v3
/yft_finger       16 pinctrl states incl. SPI-pin-to-GPIO muxing, int-gpio 3, reset-gpio 30
```
